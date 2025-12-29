"""
Unit tests for VideoGenerationPipeline
"""

import pytest
from unittest.mock import Mock
from src.core.video_pipeline import (
    VideoGenerationPipeline,
    PipelineConfig,
    RetryConfig,
    RetryStrategy,
    FallbackChain,
)
from src.adapters.contracts import (
    UnifiedRequest,
    UnifiedResponse,
    SchemaVersion,
    MediaType,
    ProviderType,
    ErrorCode,
    ErrorDetails,
)


@pytest.fixture
def mock_adapter():
    adapter = Mock()
    adapter.provider_name = "test_provider"
    adapter.health_check.return_value = True
    return adapter


@pytest.fixture
def pipeline():
    config = PipelineConfig(enable_cache=True, enable_metrics=True)
    return VideoGenerationPipeline(config=config)


@pytest.fixture
def sample_request():
    return UnifiedRequest(
        schema_version=SchemaVersion.V2_0,
        request_id="test-123",
        provider=ProviderType.RUNWAY,
        model="gen3",
        prompt="Test video prompt",
        media_type=MediaType.VIDEO,
        parameters={"duration": 4.0},
    )


@pytest.fixture
def success_response():
    return UnifiedResponse(
        schema_version=SchemaVersion.V2_0,
        request_id="test-123",
        provider="test_provider",
        model="test_model",
        status="success",
        result={"video_url": "https://example.com/video.mp4"},
        processing_time_ms=1000.0,
    )


@pytest.fixture
def error_response():
    return UnifiedResponse(
        schema_version=SchemaVersion.V2_0,
        request_id="test-123",
        provider="test_provider",
        model="test_model",
        status="failed",
        error=ErrorDetails(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message="Rate limit exceeded",
            retryable=True,
            provider="test_provider",
            retry_after=5,
        ),
    )


class TestPipelineInitialization:
    def test_default_initialization(self):
        pipeline = VideoGenerationPipeline()
        assert pipeline.config is not None
        assert pipeline.cache is not None
        assert pipeline.metrics is not None
        assert len(pipeline.adapters) == 0

    def test_custom_config_initialization(self):
        config = PipelineConfig(
            enable_cache=False,
            enable_metrics=False,
            default_timeout=900,
        )
        pipeline = VideoGenerationPipeline(config=config)
        assert pipeline.config.default_timeout == 900
        assert pipeline.cache is None


class TestAdapterRegistration:
    def test_register_adapter(self, pipeline, mock_adapter):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        assert ProviderType.RUNWAY in pipeline.adapters
        assert pipeline.adapters[ProviderType.RUNWAY] == mock_adapter

    def test_list_providers(self, pipeline, mock_adapter):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        pipeline.register_adapter(ProviderType.SORA, mock_adapter)
        providers = pipeline.list_providers()
        assert len(providers) == 2
        assert "runway" in providers
        assert "sora" in providers


class TestCaching:
    def test_cache_hit(self, pipeline, mock_adapter, sample_request, success_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = success_response

        response1 = pipeline.execute_request(sample_request)
        response2 = pipeline.execute_request(sample_request)

        mock_adapter.execute.assert_called_once()
        assert pipeline.metrics.cache_hits == 1
        assert pipeline.metrics.cache_misses == 1

    def test_cache_miss(self, pipeline, mock_adapter, success_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = success_response

        request1 = UnifiedRequest(
            schema_version=SchemaVersion.V2_0,
            request_id="req-1",
            provider=ProviderType.RUNWAY,
            model="gen3",
            prompt="Prompt 1",
            media_type=MediaType.VIDEO,
        )

        request2 = UnifiedRequest(
            schema_version=SchemaVersion.V2_0,
            request_id="req-2",
            provider=ProviderType.RUNWAY,
            model="gen3",
            prompt="Prompt 2",
            media_type=MediaType.VIDEO,
        )

        pipeline.execute_request(request1)
        pipeline.execute_request(request2)

        assert mock_adapter.execute.call_count == 2
        assert pipeline.metrics.cache_misses == 2

    def test_cache_invalidation(self, pipeline, mock_adapter, sample_request, success_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = success_response

        pipeline.execute_request(sample_request)
        pipeline.invalidate_cache(provider="runway", model="gen3")
        pipeline.execute_request(sample_request)

        assert mock_adapter.execute.call_count == 2


class TestRetryLogic:
    def test_retry_on_retryable_error(self, pipeline, mock_adapter, sample_request, error_response, success_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.side_effect = [error_response, success_response]

        retry_config = RetryConfig(
            max_attempts=3,
            initial_delay=0.1,
            strategy=RetryStrategy.FIXED_DELAY,
        )

        response = pipeline.execute_request(sample_request, retry_config=retry_config)

        assert response.is_success()
        assert mock_adapter.execute.call_count == 2
        assert pipeline.metrics.retry_attempts > 0

    def test_exponential_backoff(self, pipeline, mock_adapter, sample_request):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)

        retry_config = RetryConfig(
            max_attempts=3,
            initial_delay=0.1,
            backoff_multiplier=2.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        )

        assert retry_config.get_delay(0) == 0.1
        assert retry_config.get_delay(1) == 0.2
        assert retry_config.get_delay(2) == 0.4

    def test_max_retries_exceeded(self, pipeline, mock_adapter, sample_request, error_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = error_response

        retry_config = RetryConfig(max_attempts=2, initial_delay=0.01)
        response = pipeline.execute_request(sample_request, retry_config=retry_config)

        assert not response.is_success()
        assert mock_adapter.execute.call_count == 2

    def test_no_retry_on_non_retryable_error(self, pipeline, mock_adapter, sample_request):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)

        non_retryable_error = UnifiedResponse(
            schema_version=SchemaVersion.V2_0,
            request_id="test-123",
            provider="test_provider",
            model="test_model",
            status="failed",
            error=ErrorDetails(
                code=ErrorCode.INVALID_REQUEST,
                message="Invalid request",
                retryable=False,
                provider="test_provider",
            ),
        )

        mock_adapter.execute.return_value = non_retryable_error
        response = pipeline.execute_request(sample_request)

        assert not response.is_success()
        assert mock_adapter.execute.call_count == 1


class TestFallbackChain:
    def test_fallback_on_error(self, pipeline, sample_request, error_response, success_response):
        adapter1 = Mock()
        adapter1.provider_name = "provider1"
        adapter1.execute.return_value = error_response

        adapter2 = Mock()
        adapter2.provider_name = "provider2"
        adapter2.execute.return_value = success_response

        pipeline.register_adapter(ProviderType.RUNWAY, adapter1)
        pipeline.register_adapter(ProviderType.PIKA, adapter2)

        fallback_chain = FallbackChain(
            providers=[ProviderType.RUNWAY, ProviderType.PIKA],
            enable_automatic_fallback=True,
        )

        response = pipeline.execute_request(sample_request, fallback_chain=fallback_chain)

        assert response.is_success()
        assert pipeline.metrics.fallback_invocations > 0

    def test_no_fallback_on_non_fallback_error(self, pipeline, sample_request):
        adapter1 = Mock()
        adapter1.provider_name = "provider1"

        non_fallback_error = UnifiedResponse(
            schema_version=SchemaVersion.V2_0,
            request_id="test-123",
            provider="provider1",
            model="test_model",
            status="failed",
            error=ErrorDetails(
                code=ErrorCode.INVALID_REQUEST,
                message="Invalid request",
                retryable=False,
                provider="provider1",
            ),
        )

        adapter1.execute.return_value = non_fallback_error
        pipeline.register_adapter(ProviderType.RUNWAY, adapter1)

        fallback_chain = FallbackChain(
            providers=[ProviderType.RUNWAY, ProviderType.PIKA],
            enable_automatic_fallback=True,
        )

        response = pipeline.execute_request(sample_request, fallback_chain=fallback_chain)

        assert not response.is_success()
        assert adapter1.execute.call_count == 1


class TestMetrics:
    def test_metrics_tracking(self, pipeline, mock_adapter, sample_request, success_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = success_response

        pipeline.execute_request(sample_request)

        metrics = pipeline.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["success_rate"] == 1.0

    def test_error_distribution(self, pipeline, mock_adapter, sample_request, error_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = error_response

        pipeline.execute_request(sample_request)

        metrics = pipeline.get_metrics()
        assert ErrorCode.RATE_LIMIT_EXCEEDED.value in metrics["error_distribution"]

    def test_provider_usage_tracking(self, pipeline, mock_adapter, sample_request, success_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = success_response

        pipeline.execute_request(sample_request)
        pipeline.execute_request(sample_request)

        metrics = pipeline.get_metrics()
        assert "test_provider" in metrics["provider_usage"]
        assert metrics["provider_usage"]["test_provider"] >= 1

    def test_reset_metrics(self, pipeline, mock_adapter, sample_request, success_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = success_response

        pipeline.execute_request(sample_request)
        pipeline.reset_metrics()

        metrics = pipeline.get_metrics()
        assert metrics["total_requests"] == 0


class TestHealthCheck:
    def test_health_check_all_healthy(self, pipeline, mock_adapter):
        mock_adapter.health_check.return_value = True
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)

        health = pipeline.health_check()
        assert health["runway"] is True

    def test_health_check_unhealthy(self, pipeline, mock_adapter):
        mock_adapter.health_check.return_value = False
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)

        health = pipeline.health_check()
        assert health["runway"] is False


class TestBatchGeneration:
    def test_batch_generate(self, pipeline, mock_adapter, success_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = success_response

        requests = [
            UnifiedRequest(
                schema_version=SchemaVersion.V2_0,
                request_id=f"req-{i}",
                provider=ProviderType.RUNWAY,
                model="gen3",
                prompt=f"Prompt {i}",
                media_type=MediaType.VIDEO,
            )
            for i in range(3)
        ]

        responses = pipeline.batch_generate(requests)

        assert len(responses) == 3
        assert all(r.is_success() for r in responses)


class TestCallbacks:
    def test_callback_on_success(self, pipeline, mock_adapter, sample_request, success_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = success_response

        callback = Mock()
        pipeline.execute_request(sample_request, callback=callback)

        callback.assert_called_once()
        assert callback.call_args[0][0].is_success()

    def test_callback_on_error(self, pipeline, mock_adapter, sample_request, error_response):
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)
        mock_adapter.execute.return_value = error_response

        callback = Mock()
        pipeline.execute_request(sample_request, callback=callback)

        callback.assert_called_once()
        assert not callback.call_args[0][0].is_success()


class TestCapabilities:
    def test_get_adapter_capabilities(self, pipeline, mock_adapter):
        mock_capabilities = Mock()
        mock_capabilities.max_resolution = (1920, 1080)
        mock_capabilities.supported_formats = ["video/mp4"]
        mock_capabilities.max_duration = 10.0
        mock_capabilities.supports_batch = False
        mock_capabilities.supports_streaming = True
        mock_capabilities.max_batch_size = None
        mock_capabilities.rate_limit_per_minute = 20
        mock_capabilities.features = {"text_to_video": True}

        mock_adapter.get_capabilities.return_value = mock_capabilities
        pipeline.register_adapter(ProviderType.RUNWAY, mock_adapter)

        caps = pipeline.get_adapter_capabilities(ProviderType.RUNWAY)

        assert caps is not None
        assert caps["max_resolution"] == (1920, 1080)
        assert caps["max_duration"] == 10.0

    def test_get_capabilities_unknown_provider(self, pipeline):
        caps = pipeline.get_adapter_capabilities(ProviderType.RUNWAY)
        assert caps is None
