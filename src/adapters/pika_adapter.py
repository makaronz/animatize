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


class PikaAdapter(BaseModelAdapter):
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.pika.art/v1",
        timeout: int = 600,
        max_retries: int = 3,
    ):
        super().__init__(api_key, api_url, timeout, max_retries)

    def _get_provider_name(self) -> str:
        return "pika"

    def get_capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            max_resolution=(1920, 1080),
            supported_formats=["video/mp4", "video/gif"],
            max_duration=10.0,
            supports_batch=False,
            supports_streaming=False,
            rate_limit_per_minute=15,
            features={
                "text_to_video": True,
                "image_to_video": True,
                "lip_sync": True,
                "sound_effects": True,
                "extend_video": True,
                "modify_region": True,
            },
        )

    def _transform_request(self, request: UnifiedRequest) -> Dict[str, Any]:
        transformed = {
            "prompt": request.prompt,
            "fps": request.parameters.get("fps", 24),
            "duration": request.parameters.get("duration", 3.0),
            "aspect_ratio": request.parameters.get("aspect_ratio", "16:9"),
        }

        if "image" in request.parameters:
            transformed["image"] = request.parameters["image"]

        if "negative_prompt" in request.parameters:
            transformed["negative_prompt"] = request.parameters["negative_prompt"]

        if "motion_strength" in request.parameters:
            transformed["motion"] = request.parameters["motion_strength"]

        if "camera_control" in request.parameters:
            transformed["camera"] = request.parameters["camera_control"]

        if "sound_prompt" in request.parameters:
            transformed["sound_prompt"] = request.parameters["sound_prompt"]

        return transformed

    def _transform_response(
        self, provider_response: Dict[str, Any], request: UnifiedRequest
    ) -> UnifiedResponse:
        if provider_response.get("status") == "error":
            error_msg = provider_response.get("message", "Unknown error")
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
                "video_url": provider_response.get("video_url"),
                "thumbnail_url": provider_response.get("thumbnail_url"),
                "duration": provider_response.get("duration"),
                "job_id": provider_response.get("job_id"),
            },
            metadata={
                "fps": request.parameters.get("fps", 24),
                "aspect_ratio": request.parameters.get("aspect_ratio", "16:9"),
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
        elif "invalid" in error_lower:
            return ErrorCode.INVALID_REQUEST
        elif "content" in error_lower or "policy" in error_lower:
            return ErrorCode.CONTENT_POLICY_VIOLATION
        else:
            return ErrorCode.PROVIDER_ERROR

    def _is_error_retryable(self, error_msg: str) -> bool:
        retryable_keywords = ["rate limit", "timeout", "503", "502", "500"]
        error_lower = error_msg.lower()
        return any(keyword in error_lower for keyword in retryable_keywords)
