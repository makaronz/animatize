from typing import Dict, Any
import requests
from .base import BaseModelAdapter
from .contracts import (
    UnifiedRequest,
    UnifiedResponse,
    ModelCapabilities,
    ErrorCode,
    ErrorDetails,
)


class FluxAdapter(BaseModelAdapter):
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.bfl.ml/v1",
        timeout: int = 300,
        max_retries: int = 3,
    ):
        super().__init__(api_key, api_url, timeout, max_retries)

    def _get_provider_name(self) -> str:
        return "flux"

    def get_capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            max_resolution=(2048, 2048),
            supported_formats=["image/png", "image/jpeg", "image/webp"],
            supports_batch=True,
            max_batch_size=4,
            rate_limit_per_minute=60,
            features={
                "text_to_image": True,
                "image_to_image": True,
                "inpainting": True,
                "controlnet": True,
                "lora": True,
            },
        )

    def _transform_request(self, request: UnifiedRequest) -> Dict[str, Any]:
        transformed = {
            "prompt": request.prompt,
            "width": request.parameters.get("width", 1024),
            "height": request.parameters.get("height", 1024),
            "num_inference_steps": request.parameters.get("steps", 50),
            "guidance_scale": request.parameters.get("guidance_scale", 7.5),
            "seed": request.parameters.get("seed"),
            "output_format": request.parameters.get("output_format", "png"),
        }

        if "negative_prompt" in request.parameters:
            transformed["negative_prompt"] = request.parameters["negative_prompt"]

        if "lora_weights" in request.parameters:
            transformed["lora_weights"] = request.parameters["lora_weights"]

        return transformed

    def _transform_response(
        self, provider_response: Dict[str, Any], request: UnifiedRequest
    ) -> UnifiedResponse:
        if "error" in provider_response:
            error_msg = provider_response["error"]
            return UnifiedResponse(
                schema_version=request.schema_version,
                request_id=request.request_id,
                provider=self.provider_name,
                model=request.model,
                status="failed",
                error=ErrorDetails(
                    code=self._map_error_code(error_msg),
                    message=error_msg,
                    retryable=self._is_error_retryable(error_msg),
                    provider=self.provider_name,
                ),
            )

        return UnifiedResponse(
            schema_version=request.schema_version,
            request_id=request.request_id,
            provider=self.provider_name,
            model=request.model,
            status="success",
            result={
                "output_url": provider_response.get("result", {}).get("sample"),
                "nsfw_detected": provider_response.get("has_nsfw_concepts", [False])[0],
                "seed": provider_response.get("seed"),
            },
            metadata={
                "width": request.parameters.get("width", 1024),
                "height": request.parameters.get("height", 1024),
            },
        )

    def _make_api_call(self, transformed_request: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{self.api_url}/generate",
            json=transformed_request,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _map_error_code(self, error_msg: str) -> ErrorCode:
        error_lower = error_msg.lower()
        if "rate limit" in error_lower:
            return ErrorCode.RATE_LIMIT_EXCEEDED
        elif "authentication" in error_lower or "unauthorized" in error_lower:
            return ErrorCode.AUTHENTICATION_FAILED
        elif "timeout" in error_lower:
            return ErrorCode.TIMEOUT
        elif "content" in error_lower or "nsfw" in error_lower:
            return ErrorCode.CONTENT_POLICY_VIOLATION
        else:
            return ErrorCode.PROVIDER_ERROR

    def _is_error_retryable(self, error_msg: str) -> bool:
        retryable_keywords = ["rate limit", "timeout", "503", "502", "500"]
        error_lower = error_msg.lower()
        return any(keyword in error_lower for keyword in retryable_keywords)
