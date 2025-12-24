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


class SoraAdapter(BaseModelAdapter):
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.openai.com/v1",
        timeout: int = 600,
        max_retries: int = 3,
    ):
        super().__init__(api_key, api_url, timeout, max_retries)

    def _get_provider_name(self) -> str:
        return "sora"

    def get_capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            max_resolution=(1920, 1080),
            supported_formats=["video/mp4"],
            max_duration=60.0,
            supports_batch=False,
            supports_streaming=False,
            rate_limit_per_minute=5,
            features={
                "text_to_video": True,
                "image_to_video": True,
                "video_extension": True,
                "prompt_enhancement": True,
                "style_transfer": True,
            },
        )

    def _transform_request(self, request: UnifiedRequest) -> Dict[str, Any]:
        transformed = {
            "model": request.model,
            "prompt": request.prompt,
            "size": request.parameters.get("size", "1280x720"),
            "quality": request.parameters.get("quality", "standard"),
            "n": request.parameters.get("n", 1),
        }

        if "duration" in request.parameters:
            transformed["duration"] = request.parameters["duration"]

        if "style" in request.parameters:
            transformed["style"] = request.parameters["style"]

        return transformed

    def _transform_response(
        self, provider_response: Dict[str, Any], request: UnifiedRequest
    ) -> UnifiedResponse:
        if "error" in provider_response:
            error = provider_response["error"]
            return UnifiedResponse(
                schema_version=request.schema_version,
                request_id=request.request_id,
                provider=self.provider_name,
                model=request.model,
                status="failed",
                error=ErrorDetails(
                    code=self._map_error_code(error),
                    message=error.get("message", "Unknown error"),
                    retryable=self._is_error_retryable(error),
                    provider=self.provider_name,
                    details=error,
                ),
            )

        data = provider_response.get("data", [])
        video_url = None
        if data:
            video_url = data[0].get("url")

        return UnifiedResponse(
            schema_version=request.schema_version,
            request_id=request.request_id,
            provider=self.provider_name,
            model=request.model,
            status="success",
            result={
                "video_url": video_url,
                "revised_prompt": data[0].get("revised_prompt") if data else None,
            },
            metadata={
                "size": request.parameters.get("size", "1280x720"),
                "quality": request.parameters.get("quality", "standard"),
            },
        )

    def _make_api_call(self, transformed_request: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{self.api_url}/videos/generations",
            json=transformed_request,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _map_error_code(self, error: Dict[str, Any]) -> ErrorCode:
        error_type = error.get("type", "")
        code = error.get("code", "")

        if "rate_limit" in error_type or code == "rate_limit_exceeded":
            return ErrorCode.RATE_LIMIT_EXCEEDED
        elif "authentication" in error_type or code == "invalid_api_key":
            return ErrorCode.AUTHENTICATION_FAILED
        elif "invalid_request" in error_type:
            return ErrorCode.INVALID_REQUEST
        elif code == "insufficient_quota":
            return ErrorCode.INSUFFICIENT_CREDITS
        elif "content_policy" in error_type:
            return ErrorCode.CONTENT_POLICY_VIOLATION
        else:
            return ErrorCode.PROVIDER_ERROR

    def _is_error_retryable(self, error: Dict[str, Any]) -> bool:
        retryable_types = ["rate_limit_error", "timeout", "server_error"]
        error_type = error.get("type", "")
        return any(t in error_type for t in retryable_types)
