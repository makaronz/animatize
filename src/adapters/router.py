from typing import Dict, List, Optional
import time
import logging
from .base import BaseModelAdapter
from .contracts import (
    UnifiedRequest,
    UnifiedResponse,
    ErrorCode,
    ErrorDetails,
)
from .cache import AdapterCache

logger = logging.getLogger(__name__)


class ProviderConfig:
    def __init__(
        self,
        adapter: BaseModelAdapter,
        priority: int = 1,
        weight: float = 1.0,
        enabled: bool = True,
        max_concurrent: int = 10,
    ):
        self.adapter = adapter
        self.priority = priority
        self.weight = weight
        self.enabled = enabled
        self.max_concurrent = max_concurrent
        self.current_concurrent = 0
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.circuit_open = False


class RoutingStrategy:
    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_LOADED = "least_loaded"
    LATENCY_BASED = "latency_based"


class AdapterRouter:
    def __init__(
        self,
        cache: Optional[AdapterCache] = None,
        strategy: str = RoutingStrategy.PRIORITY,
        enable_fallback: bool = True,
        enable_retry: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
    ):
        self.providers: Dict[str, ProviderConfig] = {}
        self.cache = cache or AdapterCache()
        self.strategy = strategy
        self.enable_fallback = enable_fallback
        self.enable_retry = enable_retry
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout

        self._round_robin_index = 0
        self._provider_latencies: Dict[str, List[float]] = {}

    def register_provider(
        self,
        provider_name: str,
        adapter: BaseModelAdapter,
        priority: int = 1,
        weight: float = 1.0,
        enabled: bool = True,
    ):
        config = ProviderConfig(
            adapter=adapter,
            priority=priority,
            weight=weight,
            enabled=enabled,
        )
        self.providers[provider_name] = config
        self._provider_latencies[provider_name] = []
        logger.info(f"Registered provider: {provider_name}")

    def unregister_provider(self, provider_name: str):
        if provider_name in self.providers:
            del self.providers[provider_name]
            del self._provider_latencies[provider_name]
            logger.info(f"Unregistered provider: {provider_name}")

    def execute(self, request: UnifiedRequest) -> UnifiedResponse:
        cache_key = self.cache.generate_cache_key(
            request.provider.value,
            request.model,
            request.prompt,
            request.parameters,
        )

        cached_response = self.cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for request {request.request_id}")
            return cached_response

        selected_providers = self._select_providers(request)

        if not selected_providers:
            return UnifiedResponse(
                schema_version=request.schema_version,
                request_id=request.request_id,
                provider=request.provider.value,
                model=request.model,
                status="failed",
                error=ErrorDetails(
                    code=ErrorCode.PROVIDER_ERROR,
                    message="No available providers",
                    retryable=False,
                    provider="router",
                ),
            )

        response = None
        for provider_name in selected_providers:
            config = self.providers[provider_name]

            if config.circuit_open:
                if time.time() - config.last_failure_time > self.circuit_breaker_timeout:
                    config.circuit_open = False
                    config.failure_count = 0
                    logger.info(f"Circuit breaker closed for {provider_name}")
                else:
                    logger.warning(f"Circuit breaker open for {provider_name}, skipping")
                    continue

            response = self._execute_with_retry(request, config)

            if response.is_success():
                self._record_success(provider_name, response.processing_time_ms)
                self.cache.set(cache_key, response)
                return response

            self._record_failure(provider_name)

            if not self.enable_fallback:
                break

        return response or UnifiedResponse(
            schema_version=request.schema_version,
            request_id=request.request_id,
            provider=request.provider.value,
            model=request.model,
            status="failed",
            error=ErrorDetails(
                code=ErrorCode.PROVIDER_ERROR,
                message="All providers failed",
                retryable=False,
                provider="router",
            ),
        )

    def _select_providers(self, request: UnifiedRequest) -> List[str]:
        available_providers = [
            name
            for name, config in self.providers.items()
            if config.enabled and not config.circuit_open
        ]

        if not available_providers:
            return []

        if hasattr(request, "provider") and request.provider.value in available_providers:
            primary = request.provider.value
            others = [p for p in available_providers if p != primary]
            return [primary] + others

        if self.strategy == RoutingStrategy.PRIORITY:
            return sorted(
                available_providers,
                key=lambda p: self.providers[p].priority,
                reverse=True,
            )

        elif self.strategy == RoutingStrategy.ROUND_ROBIN:
            self._round_robin_index = (self._round_robin_index + 1) % len(available_providers)
            selected = available_providers[self._round_robin_index]
            others = [p for p in available_providers if p != selected]
            return [selected] + others

        elif self.strategy == RoutingStrategy.WEIGHTED:
            import random

            total_weight = sum(self.providers[p].weight for p in available_providers)
            rand = random.uniform(0, total_weight)
            cumulative = 0
            for provider in available_providers:
                cumulative += self.providers[provider].weight
                if rand <= cumulative:
                    others = [p for p in available_providers if p != provider]
                    return [provider] + others

        elif self.strategy == RoutingStrategy.LEAST_LOADED:
            return sorted(
                available_providers,
                key=lambda p: self.providers[p].current_concurrent,
            )

        elif self.strategy == RoutingStrategy.LATENCY_BASED:
            return sorted(
                available_providers,
                key=lambda p: self._get_average_latency(p),
            )

        return available_providers

    def _execute_with_retry(
        self,
        request: UnifiedRequest,
        config: ProviderConfig,
    ) -> UnifiedResponse:
        attempt = 0

        while attempt < self.max_retries if self.enable_retry else attempt < 1:
            try:
                config.current_concurrent += 1
                response = config.adapter.execute(request)
                config.current_concurrent -= 1

                if response.is_success() or not response.is_retryable():
                    return response

                attempt += 1
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(
                        f"Retrying request {request.request_id} after {delay}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(delay)

            except Exception as e:
                config.current_concurrent -= 1
                logger.exception(f"Error executing request on {config.adapter.provider_name}")
                return UnifiedResponse(
                    schema_version=request.schema_version,
                    request_id=request.request_id,
                    provider=config.adapter.provider_name,
                    model=request.model,
                    status="failed",
                    error=ErrorDetails(
                        code=ErrorCode.UNKNOWN_ERROR,
                        message=str(e),
                        retryable=False,
                        provider=config.adapter.provider_name,
                    ),
                )

        return response

    def _record_success(self, provider_name: str, latency_ms: Optional[float]):
        config = self.providers[provider_name]
        config.failure_count = 0

        if latency_ms is not None:
            latencies = self._provider_latencies[provider_name]
            latencies.append(latency_ms)
            if len(latencies) > 100:
                latencies.pop(0)

    def _record_failure(self, provider_name: str):
        config = self.providers[provider_name]
        config.failure_count += 1
        config.last_failure_time = time.time()

        if config.failure_count >= self.circuit_breaker_threshold:
            config.circuit_open = True
            logger.warning(
                f"Circuit breaker opened for {provider_name} "
                f"after {config.failure_count} failures"
            )

    def _get_average_latency(self, provider_name: str) -> float:
        latencies = self._provider_latencies.get(provider_name, [])
        if not latencies:
            return float("inf")
        return sum(latencies) / len(latencies)

    def get_provider_stats(self) -> Dict[str, Dict]:
        stats = {}
        for name, config in self.providers.items():
            stats[name] = {
                "enabled": config.enabled,
                "priority": config.priority,
                "weight": config.weight,
                "current_concurrent": config.current_concurrent,
                "failure_count": config.failure_count,
                "circuit_open": config.circuit_open,
                "average_latency_ms": self._get_average_latency(name),
            }
        return stats

    def health_check(self) -> Dict[str, bool]:
        results = {}
        for name, config in self.providers.items():
            results[name] = config.adapter.health_check()
        return results
