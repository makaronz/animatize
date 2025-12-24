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


class VeoAdapter(BaseModelAdapter):
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://generativelanguage.googleapis.com/v1",
        timeout: int = 600,
        max_retries: int = 3,
    ):
        super().__init__(api_key, api_url, timeout, max_retries)

    def _get_provider_name(self) -> str:
        return "veo"

    def get_capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            max_resolution=(1920, 1080),
            supported_formats=["video/mp4", "video/webm"],
            max_duration=120.0,
            supports_batch=False,
            supports_streaming=False,
            rate_limit_per_minute=10,
            features={
                "text_to_video": True,
                "image_to_video": True,
                "video_extension": True,
                "camera_control": True,
                "motion_control": True,
            },
        )

    def _transform_request(self, request: UnifiedRequest) -> Dict[str, Any]:
        transformed = {
            "prompt": request.prompt,
            "duration": request.parameters.get("duration", 5.0),
            "aspect_ratio": request.parameters.get("aspect_ratio", "16:9"),
            "fps": request.parameters.get("fps", 24),
            "model": request.model,
        }

        if "reference_image" in request.parameters:
            transformed["reference_image"] = request.parameters["reference_image"]

        if "camera_motion" in request.parameters:
            transformed["camera_motion"] = request.parameters["camera_motion"]

        if "motion_strength" in request.parameters:
            transformed["motion_strength"] = request.parameters["motion_strength"]

        return transformed

    def _transform_response(
        self, provider_response: Dict[str, Any], request: UnifiedRequest
    ) -> UnifiedResponse:
        if "error" in provider_response:
            error_data = provider_response["error"]
            return UnifiedResponse(
                schema_version=request.schema_version,
                request_id=request.request_id,
                provider=self.provider_name,
                model=request.model,
                status="failed",
                error=ErrorDetails(
                    code=self._map_error_code(error_data),
                    message=error_data.get("message", "Unknown error"),
                    retryable=self._is_error_retryable(error_data),
                    provider=self.provider_name,
                    details=error_data,
                ),
            )

        return UnifiedResponse(
            schema_version=request.schema_version,
            request_id=request.request_id,
            provider=self.provider_name,
            model=request.model,
            status="success",
            result={
                "video_url": provider_response.get("video", {}).get("url"),
                "thumbnail_url": provider_response.get("thumbnail_url"),
                "duration": provider_response.get("duration"),
                "resolution": provider_response.get("resolution"),
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
            f"{self.api_url}/models/{transformed_request['model']}:generateVideo",
            json=transformed_request,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _map_error_code(self, error_data: Dict[str, Any]) -> ErrorCode:
        status = error_data.get("status", "")
        code = error_data.get("code", 0)

        if code == 429 or "RESOURCE_EXHAUSTED" in status:
            return ErrorCode.RATE_LIMIT_EXCEEDED
        elif code == 401 or "UNAUTHENTICATED" in status:
            return ErrorCode.AUTHENTICATION_FAILED
        elif code == 400 or "INVALID_ARGUMENT" in status:
            return ErrorCode.INVALID_REQUEST
        elif "DEADLINE_EXCEEDED" in status:
            return ErrorCode.TIMEOUT
        else:
            return ErrorCode.PROVIDER_ERROR

    def _is_error_retryable(self, error_data: Dict[str, Any]) -> bool:
        retryable_statuses = ["RESOURCE_EXHAUSTED", "DEADLINE_EXCEEDED", "UNAVAILABLE"]
        status = error_data.get("status", "")
        return any(s in status for s in retryable_statuses)
