from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class SchemaVersion(str, Enum):
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"


class ErrorCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    AUTHENTICATION_FAILED = "authentication_failed"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    PROVIDER_ERROR = "provider_error"
    TIMEOUT = "timeout"
    INVALID_MODEL = "invalid_model"
    INSUFFICIENT_CREDITS = "insufficient_credits"
    CONTENT_POLICY_VIOLATION = "content_policy_violation"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"


class ProviderType(str, Enum):
    FLUX = "flux"
    VEO = "veo"
    RUNWAY = "runway"
    SORA = "sora"
    PIKA = "pika"
    STABLE_DIFFUSION = "stable_diffusion"
    MIDJOURNEY = "midjourney"


@dataclass
class ErrorDetails:
    code: ErrorCode
    message: str
    retryable: bool
    provider: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    retry_after: Optional[int] = None


@dataclass
class ModelCapabilities:
    max_resolution: tuple[int, int]
    supported_formats: List[str]
    max_duration: Optional[float] = None
    supports_batch: bool = False
    supports_streaming: bool = False
    max_batch_size: Optional[int] = None
    rate_limit_per_minute: Optional[int] = None
    features: Dict[str, bool] = field(default_factory=dict)


@dataclass
class UnifiedRequest:
    schema_version: SchemaVersion
    request_id: str
    provider: ProviderType
    model: str
    prompt: str
    media_type: MediaType
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    timeout: int = 300
    retry_config: Optional[Dict[str, Any]] = None
    callback_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version.value,
            "request_id": self.request_id,
            "provider": self.provider.value,
            "model": self.model,
            "prompt": self.prompt,
            "media_type": self.media_type.value,
            "parameters": self.parameters,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "timeout": self.timeout,
            "retry_config": self.retry_config,
            "callback_url": self.callback_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnifiedRequest":
        return cls(
            schema_version=SchemaVersion(data["schema_version"]),
            request_id=data["request_id"],
            provider=ProviderType(data["provider"]),
            model=data["model"],
            prompt=data["prompt"],
            media_type=MediaType(data["media_type"]),
            parameters=data.get("parameters", {}),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            timeout=data.get("timeout", 300),
            retry_config=data.get("retry_config"),
            callback_url=data.get("callback_url"),
        )


@dataclass
class UnifiedResponse:
    schema_version: SchemaVersion
    request_id: str
    provider: str
    model: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[ErrorDetails] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version.value,
            "request_id": self.request_id,
            "provider": self.provider,
            "model": self.model,
            "status": self.status,
            "result": self.result,
            "error": self.error.__dict__ if self.error else None,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "processing_time_ms": self.processing_time_ms,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnifiedResponse":
        error_data = data.get("error")
        error = None
        if error_data:
            error = ErrorDetails(
                code=ErrorCode(error_data["code"]),
                message=error_data["message"],
                retryable=error_data["retryable"],
                provider=error_data["provider"],
                details=error_data.get("details"),
                timestamp=error_data.get("timestamp", datetime.utcnow().isoformat()),
                retry_after=error_data.get("retry_after"),
            )

        return cls(
            schema_version=SchemaVersion(data["schema_version"]),
            request_id=data["request_id"],
            provider=data["provider"],
            model=data["model"],
            status=data["status"],
            result=data.get("result"),
            error=error,
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            processing_time_ms=data.get("processing_time_ms"),
            tokens_used=data.get("tokens_used"),
            cost=data.get("cost"),
        )

    def is_success(self) -> bool:
        return self.status == "success" and self.error is None

    def is_retryable(self) -> bool:
        return self.error is not None and self.error.retryable


@dataclass
class CacheKey:
    provider: str
    model: str
    prompt: str
    parameters_hash: str

    def to_string(self) -> str:
        return f"{self.provider}:{self.model}:{hash(self.prompt)}:{self.parameters_hash}"


@dataclass
class VersionMigration:
    from_version: SchemaVersion
    to_version: SchemaVersion
    migration_fn: callable
    backward_compatible: bool = True
