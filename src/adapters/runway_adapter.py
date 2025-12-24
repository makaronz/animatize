from typing import Dict, Any
import requests
import time
from .base import BaseModelAdapter
from .contracts import (
    UnifiedRequest,
    UnifiedResponse,
    ModelCapabilities,
    ErrorCode,
    ErrorDetails,
)


class RunwayAdapter(BaseModelAdapter):
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.runwayml.com/v1",
        timeout: int = 600,
        max_retries: int = 3,
    ):
        super().__init__(api_key, api_url, timeout, max_retries)

    def _get_provider_name(self) -> str:
        return "runway"

    def get_capabilities(self) -> ModelCapabilities:
        return ModelCapabilities(
            max_resolution=(1920, 1080),
            supported_formats=["video/mp4", "image/png", "image/jpeg"],
            max_duration=16.0,
            supports_batch=False,
            supports_streaming=True,
            rate_limit_per_minute=20,
            features={
                "text_to_video": True,
                "image_to_video": True,
                "video_to_video": True,
                "motion_brush": True,
                "frame_interpolation": True,
                "upscaling": True,
            },
        )

    def _transform_request(self, request: UnifiedRequest) -> Dict[str, Any]:
        transformed = {
            "text_prompt": request.prompt,
            "duration": request.parameters.get("duration", 4.0),
            "resolution": request.parameters.get("resolution", "1280x768"),
            "model": request.parameters.get("gen_version", "gen3"),
        }

        if "image_prompt" in request.parameters:
            transformed["image_prompt"] = request.parameters["image_prompt"]

        if "motion_vectors" in request.parameters:
            transformed["motion_vectors"] = request.parameters["motion_vectors"]

        if "seed" in request.parameters:
            transformed["seed"] = request.parameters["seed"]

        if "watermark" in request.parameters:
            transformed["watermark"] = request.parameters["watermark"]

        return transformed

    def _transform_response(
        self, provider_response: Dict[str, Any], request: UnifiedRequest
    ) -> UnifiedResponse:
        if provider_response.get("status") == "failed":
            error_msg = provider_response.get("error", "Unknown error")
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

        artifacts = provider_response.get("artifacts", [])
        output_url = None
        if artifacts:
            output_url = artifacts[0].get("url")

        return UnifiedResponse(
            schema_version=request.schema_version,
            request_id=request.request_id,
            provider=self.provider_name,
            model=request.model,
            status="success" if output_url else "processing",
            result={
                "video_url": output_url,
                "task_id": provider_response.get("id"),
                "progress": provider_response.get("progress", 0),
            },
            metadata={
                "duration": request.parameters.get("duration", 4.0),
                "resolution": request.parameters.get("resolution", "1280x768"),
            },
            cost=provider_response.get("cost"),
        )

    def _make_api_call(self, transformed_request: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06",
        }

        response = requests.post(
            f"{self.api_url}/generations",
            json=transformed_request,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

        result = response.json()
        task_id = result.get("id")

        if task_id:
            result = self._poll_task_status(task_id, headers)

        return result

    def _poll_task_status(
        self, task_id: str, headers: Dict[str, str], max_wait: int = 300
    ) -> Dict[str, Any]:
        start_time = time.time()

        while time.time() - start_time < max_wait:
            response = requests.get(
                f"{self.api_url}/generations/{task_id}",
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()

            status = result.get("status")
            if status in ["succeeded", "failed"]:
                return result

            time.sleep(2)

        return {"status": "timeout", "error": "Task polling timeout exceeded"}

    def _map_error_code(self, error_msg: str) -> ErrorCode:
        error_lower = error_msg.lower()
        if "rate limit" in error_lower or "quota" in error_lower:
            return ErrorCode.RATE_LIMIT_EXCEEDED
        elif "authentication" in error_lower or "api key" in error_lower:
            return ErrorCode.AUTHENTICATION_FAILED
        elif "timeout" in error_lower:
            return ErrorCode.TIMEOUT
        elif "credits" in error_lower or "insufficient" in error_lower:
            return ErrorCode.INSUFFICIENT_CREDITS
        elif "content" in error_lower or "policy" in error_lower:
            return ErrorCode.CONTENT_POLICY_VIOLATION
        else:
            return ErrorCode.PROVIDER_ERROR

    def _is_error_retryable(self, error_msg: str) -> bool:
        retryable_keywords = ["rate limit", "timeout", "503", "502", "500", "busy"]
        error_lower = error_msg.lower()
        return any(keyword in error_lower for keyword in retryable_keywords)
