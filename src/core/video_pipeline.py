import uuid
import logging
import time
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..adapters.contracts import (
    UnifiedRequest,
    UnifiedResponse,
    SchemaVersion,
    MediaType,
    ProviderType,
    ErrorCode,
    ErrorDetails,
)
from ..adapters.cache import AdapterCache
from ..adapters.base import BaseModelAdapter
from ..adapters.flux_adapter import FluxAdapter
from ..adapters.veo_adapter import VeoAdapter
from ..adapters.runway_adapter import RunwayAdapter
from ..adapters.sora_adapter import SoraAdapter
from ..adapters.pika_adapter import PikaAdapter

logger = logging.getLogger(__name__)


class RetryStrategy(str, Enum):
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


@dataclass
class RetryConfig:
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retryable_error_codes: List[ErrorCode] = field(
        default_factory=lambda: [
            ErrorCode.RATE_LIMIT_EXCEEDED,
            ErrorCode.TIMEOUT,
            ErrorCode.NETWORK_ERROR,
            ErrorCode.PROVIDER_ERROR,
        ]
    )

    def should_retry(self, error: ErrorDetails, attempt: int) -> bool:
        if attempt >= self.max_attempts:
            return False
        if not error.retryable:
            return False
        return error.code in self.retryable_error_codes

    def get_delay(self, attempt: int) -> float:
        if self.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.initial_delay * (self.backoff_multiplier**attempt)
        elif self.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.initial_delay * (attempt + 1)
        else:
            delay = self.initial_delay

        return min(delay, self.max_delay)


@dataclass
class FallbackChain:
    providers: List[ProviderType]
    enable_automatic_fallback: bool = True
    fallback_on_error_codes: List[ErrorCode] = field(
        default_factory=lambda: [
            ErrorCode.RATE_LIMIT_EXCEEDED,
            ErrorCode.TIMEOUT,
            ErrorCode.PROVIDER_ERROR,
            ErrorCode.INSUFFICIENT_CREDITS,
        ]
    )

    def should_fallback(self, error: ErrorDetails) -> bool:
        if not self.enable_automatic_fallback:
            return False
        return error.code in self.fallback_on_error_codes

    def get_next_provider(self, current_provider: ProviderType) -> Optional[ProviderType]:
        try:
            current_index = self.providers.index(current_provider)
            if current_index < len(self.providers) - 1:
                return self.providers[current_index + 1]
        except (ValueError, IndexError):
            pass
        return None


@dataclass
class PipelineConfig:
    enable_cache: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    fallback_chain: Optional[FallbackChain] = None
    default_timeout: int = 600
    enable_metrics: bool = True
    max_concurrent_requests: int = 10


@dataclass
class PipelineMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    retry_attempts: int = 0
    fallback_invocations: int = 0
    total_processing_time_ms: float = 0.0
    average_processing_time_ms: float = 0.0
    provider_usage: Dict[str, int] = field(default_factory=dict)
    error_distribution: Dict[ErrorCode, int] = field(default_factory=dict)

    def record_request(self, response: UnifiedResponse, cache_hit: bool = False):
        self.total_requests += 1

        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        if response.is_success():
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if response.error:
                self.error_distribution[response.error.code] = self.error_distribution.get(response.error.code, 0) + 1

        if response.processing_time_ms:
            self.total_processing_time_ms += response.processing_time_ms
            self.average_processing_time_ms = self.total_processing_time_ms / self.total_requests

        self.provider_usage[response.provider] = self.provider_usage.get(response.provider, 0) + 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": (
                self.cache_hits / (self.cache_hits + self.cache_misses)
                if (self.cache_hits + self.cache_misses) > 0
                else 0
            ),
            "retry_attempts": self.retry_attempts,
            "fallback_invocations": self.fallback_invocations,
            "average_processing_time_ms": self.average_processing_time_ms,
            "provider_usage": self.provider_usage,
            "error_distribution": {code.value: count for code, count in self.error_distribution.items()},
        }


class VideoGenerationPipeline:
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.adapters: Dict[ProviderType, BaseModelAdapter] = {}
        self.cache: Optional[AdapterCache] = None
        self.metrics = PipelineMetrics()

        if self.config.enable_cache:
            self.cache = AdapterCache(
                max_size=self.config.cache_max_size,
                default_ttl=self.config.cache_ttl,
            )

        logger.info("VideoGenerationPipeline initialized")

    def register_adapter(self, provider: ProviderType, adapter: BaseModelAdapter):
        self.adapters[provider] = adapter
        logger.info(f"Registered adapter for provider: {provider.value}")

    def register_flux_adapter(self, api_key: str, **kwargs):
        adapter = FluxAdapter(api_key=api_key, **kwargs)
        self.register_adapter(ProviderType.FLUX, adapter)

    def register_veo_adapter(self, api_key: str, **kwargs):
        adapter = VeoAdapter(api_key=api_key, **kwargs)
        self.register_adapter(ProviderType.VEO, adapter)

    def register_runway_adapter(self, api_key: str, **kwargs):
        adapter = RunwayAdapter(api_key=api_key, **kwargs)
        self.register_adapter(ProviderType.RUNWAY, adapter)

    def register_sora_adapter(self, api_key: str, **kwargs):
        adapter = SoraAdapter(api_key=api_key, **kwargs)
        self.register_adapter(ProviderType.SORA, adapter)

    def register_pika_adapter(self, api_key: str, **kwargs):
        adapter = PikaAdapter(api_key=api_key, **kwargs)
        self.register_adapter(ProviderType.PIKA, adapter)

    def generate_video(
        self,
        prompt: str,
        provider: ProviderType,
        model: str,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        retry_config: Optional[RetryConfig] = None,
        fallback_chain: Optional[FallbackChain] = None,
        callback: Optional[Callable[[UnifiedResponse], None]] = None,
    ) -> UnifiedResponse:
        request = UnifiedRequest(
            schema_version=SchemaVersion.V2_0,
            request_id=str(uuid.uuid4()),
            provider=provider,
            model=model,
            prompt=prompt,
            media_type=MediaType.VIDEO,
            parameters=parameters or {},
            metadata=metadata or {},
            timeout=self.config.default_timeout,
        )

        return self.execute_request(
            request=request,
            retry_config=retry_config,
            fallback_chain=fallback_chain,
            callback=callback,
        )

    def execute_request(
        self,
        request: UnifiedRequest,
        retry_config: Optional[RetryConfig] = None,
        fallback_chain: Optional[FallbackChain] = None,
        callback: Optional[Callable[[UnifiedResponse], None]] = None,
    ) -> UnifiedResponse:
        retry_config = retry_config or self.config.retry_config
        fallback_chain = fallback_chain or self.config.fallback_chain

        if self.cache:
            cache_key = self.cache.generate_cache_key(
                request.provider.value,
                request.model,
                request.prompt,
                request.parameters,
            )
            cached_response = self.cache.get(cache_key)
            if cached_response:
                logger.info(f"Cache hit for request {request.request_id}")
                if self.config.enable_metrics:
                    self.metrics.record_request(cached_response, cache_hit=True)
                if callback:
                    callback(cached_response)
                return cached_response

        current_provider = request.provider
        providers_to_try = [current_provider]

        if fallback_chain and fallback_chain.enable_automatic_fallback:
            providers_to_try = [p for p in fallback_chain.providers if p in self.adapters]
            if current_provider not in providers_to_try:
                providers_to_try.insert(0, current_provider)

        last_response = None

        for provider_index, provider in enumerate(providers_to_try):
            if provider not in self.adapters:
                logger.warning(f"No adapter registered for provider: {provider.value}")
                continue

            adapter = self.adapters[provider]
            request.provider = provider

            logger.info(
                f"Attempting request {request.request_id} with provider: {provider.value} "
                f"(provider {provider_index + 1}/{len(providers_to_try)})"
            )

            response = self._execute_with_retry(
                request=request,
                adapter=adapter,
                retry_config=retry_config,
            )

            if response.is_success():
                logger.info(f"Request {request.request_id} succeeded with provider: {provider.value}")

                if self.cache:
                    self.cache.set(cache_key, response)

                if self.config.enable_metrics:
                    if provider_index > 0:
                        self.metrics.fallback_invocations += 1
                    self.metrics.record_request(response, cache_hit=False)

                if callback:
                    callback(response)

                return response

            last_response = response

            if fallback_chain and provider_index < len(providers_to_try) - 1:
                if fallback_chain.should_fallback(response.error):
                    logger.warning(
                        f"Request {request.request_id} failed with provider {provider.value}, "
                        f"falling back to next provider"
                    )
                    continue
                else:
                    logger.error(
                        f"Request {request.request_id} failed with non-fallback error: " f"{response.error.code.value}"
                    )
                    break

        if last_response and self.config.enable_metrics:
            self.metrics.record_request(last_response, cache_hit=False)

        if callback and last_response:
            callback(last_response)

        return last_response or UnifiedResponse(
            schema_version=request.schema_version,
            request_id=request.request_id,
            provider=request.provider.value,
            model=request.model,
            status="failed",
            error=ErrorDetails(
                code=ErrorCode.PROVIDER_ERROR,
                message="No available providers to handle request",
                retryable=False,
                provider="pipeline",
            ),
        )

    def _execute_with_retry(
        self,
        request: UnifiedRequest,
        adapter: BaseModelAdapter,
        retry_config: RetryConfig,
    ) -> UnifiedResponse:
        attempt = 0

        while attempt < retry_config.max_attempts:
            try:
                start_time = time.time()
                response = adapter.execute(request)
                processing_time = (time.time() - start_time) * 1000

                if not response.processing_time_ms:
                    response.processing_time_ms = processing_time

                if response.is_success():
                    return response

                if response.error and retry_config.should_retry(response.error, attempt):
                    attempt += 1
                    if self.config.enable_metrics:
                        self.metrics.retry_attempts += 1

                    if attempt < retry_config.max_attempts:
                        delay = retry_config.get_delay(attempt - 1)

                        if response.error.retry_after:
                            delay = max(delay, response.error.retry_after)

                        logger.info(
                            f"Retrying request {request.request_id} after {delay:.2f}s "
                            f"(attempt {attempt + 1}/{retry_config.max_attempts})"
                        )
                        time.sleep(delay)
                        continue

                return response

            except Exception as e:
                logger.exception(
                    f"Unexpected error executing request {request.request_id} " f"on provider {adapter.provider_name}"
                )

                error_response = UnifiedResponse(
                    schema_version=request.schema_version,
                    request_id=request.request_id,
                    provider=adapter.provider_name,
                    model=request.model,
                    status="failed",
                    error=ErrorDetails(
                        code=ErrorCode.UNKNOWN_ERROR,
                        message=str(e),
                        retryable=False,
                        provider=adapter.provider_name,
                        details={"exception_type": type(e).__name__},
                    ),
                )

                attempt += 1
                if attempt < retry_config.max_attempts:
                    delay = retry_config.get_delay(attempt - 1)
                    logger.info(
                        f"Retrying request {request.request_id} after exception "
                        f"(attempt {attempt + 1}/{retry_config.max_attempts})"
                    )
                    time.sleep(delay)
                    continue

                return error_response

        return UnifiedResponse(
            schema_version=request.schema_version,
            request_id=request.request_id,
            provider=adapter.provider_name,
            model=request.model,
            status="failed",
            error=ErrorDetails(
                code=ErrorCode.UNKNOWN_ERROR,
                message=f"Max retries ({retry_config.max_attempts}) exceeded",
                retryable=False,
                provider=adapter.provider_name,
            ),
        )

    def batch_generate(
        self,
        requests: List[UnifiedRequest],
        retry_config: Optional[RetryConfig] = None,
        fallback_chain: Optional[FallbackChain] = None,
    ) -> List[UnifiedResponse]:
        responses = []
        for request in requests:
            response = self.execute_request(
                request=request,
                retry_config=retry_config,
                fallback_chain=fallback_chain,
            )
            responses.append(response)
        return responses

    def get_metrics(self) -> Dict[str, Any]:
        metrics_dict = self.metrics.to_dict()

        if self.cache:
            cache_stats = self.cache.get_stats()
            metrics_dict["cache_stats"] = cache_stats

        return metrics_dict

    def reset_metrics(self):
        self.metrics = PipelineMetrics()
        if self.cache:
            self.cache.reset_stats()
        logger.info("Pipeline metrics reset")

    def clear_cache(self):
        if self.cache:
            self.cache.clear()
            logger.info("Pipeline cache cleared")

    def invalidate_cache(self, provider: Optional[str] = None, model: Optional[str] = None):
        if not self.cache:
            return

        if provider and model:
            count = self.cache.invalidate_model(provider, model)
            logger.info(f"Invalidated {count} cache entries for {provider}:{model}")
        elif provider:
            count = self.cache.invalidate_provider(provider)
            logger.info(f"Invalidated {count} cache entries for provider {provider}")
        else:
            self.cache.clear()
            logger.info("Cleared entire cache")

    def health_check(self) -> Dict[str, bool]:
        results = {}
        for provider, adapter in self.adapters.items():
            results[provider.value] = adapter.health_check()
        return results

    def get_adapter_capabilities(self, provider: ProviderType) -> Optional[Dict[str, Any]]:
        if provider not in self.adapters:
            return None

        adapter = self.adapters[provider]
        capabilities = adapter.get_capabilities()

        return {
            "provider": provider.value,
            "max_resolution": capabilities.max_resolution,
            "supported_formats": capabilities.supported_formats,
            "max_duration": capabilities.max_duration,
            "supports_batch": capabilities.supports_batch,
            "supports_streaming": capabilities.supports_streaming,
            "max_batch_size": capabilities.max_batch_size,
            "rate_limit_per_minute": capabilities.rate_limit_per_minute,
            "features": capabilities.features,
        }

    def list_providers(self) -> List[str]:
        return [provider.value for provider in self.adapters.keys()]
