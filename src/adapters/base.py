from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .contracts import (
    UnifiedRequest,
    UnifiedResponse,
    ModelCapabilities,
    ErrorDetails,
    ErrorCode,
)
import time
import logging

logger = logging.getLogger(__name__)


class BaseModelAdapter(ABC):
    def __init__(
        self,
        api_key: str,
        api_url: Optional[str] = None,
        timeout: int = 300,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.provider_name = self._get_provider_name()

    @abstractmethod
    def _get_provider_name(self) -> str:
        pass

    @abstractmethod
    def get_capabilities(self) -> ModelCapabilities:
        pass

    @abstractmethod
    def _transform_request(self, request: UnifiedRequest) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _transform_response(
        self, provider_response: Dict[str, Any], request: UnifiedRequest
    ) -> UnifiedResponse:
        pass

    @abstractmethod
    def _make_api_call(self, transformed_request: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def validate_request(self, request: UnifiedRequest) -> Optional[ErrorDetails]:
        capabilities = self.get_capabilities()

        if request.media_type.value not in [
            fmt.split("/")[0] for fmt in capabilities.supported_formats
        ]:
            return ErrorDetails(
                code=ErrorCode.INVALID_REQUEST,
                message=f"Media type {request.media_type} not supported by {self.provider_name}",
                retryable=False,
                provider=self.provider_name,
            )

        if "resolution" in request.parameters:
            res = request.parameters["resolution"]
            if isinstance(res, (list, tuple)) and len(res) == 2:
                if (
                    res[0] > capabilities.max_resolution[0]
                    or res[1] > capabilities.max_resolution[1]
                ):
                    return ErrorDetails(
                        code=ErrorCode.INVALID_REQUEST,
                        message=f"Resolution {res} exceeds maximum {capabilities.max_resolution}",
                        retryable=False,
                        provider=self.provider_name,
                    )

        return None

    def execute(self, request: UnifiedRequest) -> UnifiedResponse:
        start_time = time.time()

        validation_error = self.validate_request(request)
        if validation_error:
            return UnifiedResponse(
                schema_version=request.schema_version,
                request_id=request.request_id,
                provider=self.provider_name,
                model=request.model,
                status="failed",
                error=validation_error,
                processing_time_ms=(time.time() - start_time) * 1000,
            )

        try:
            transformed_request = self._transform_request(request)
            provider_response = self._make_api_call(transformed_request)
            response = self._transform_response(provider_response, request)
            response.processing_time_ms = (time.time() - start_time) * 1000
            return response

        except Exception as e:
            logger.exception(f"Error executing request on {self.provider_name}")
            return UnifiedResponse(
                schema_version=request.schema_version,
                request_id=request.request_id,
                provider=self.provider_name,
                model=request.model,
                status="failed",
                error=ErrorDetails(
                    code=ErrorCode.PROVIDER_ERROR,
                    message=str(e),
                    retryable=self._is_retryable_error(e),
                    provider=self.provider_name,
                    details={"exception_type": type(e).__name__},
                ),
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def _is_retryable_error(self, error: Exception) -> bool:
        retryable_errors = [
            "timeout",
            "network",
            "rate limit",
            "503",
            "502",
            "500",
        ]
        error_str = str(error).lower()
        return any(err in error_str for err in retryable_errors)

    def health_check(self) -> bool:
        try:
            return self._health_check_impl()
        except Exception as e:
            logger.error(f"Health check failed for {self.provider_name}: {e}")
            return False

    def _health_check_impl(self) -> bool:
        return True
