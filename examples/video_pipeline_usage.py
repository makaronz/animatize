"""
Example usage of the VideoGenerationPipeline with unified interface,
retry logic, fallback chains, and caching.
"""

import logging
from src.core.video_pipeline import (
    VideoGenerationPipeline,
    PipelineConfig,
    RetryConfig,
    RetryStrategy,
    FallbackChain,
)
from src.adapters.contracts import ProviderType, ErrorCode

logging.basicConfig(level=logging.INFO)


def basic_usage_example():
    """Basic example: Generate a video with a single provider."""
    pipeline = VideoGenerationPipeline()

    pipeline.register_runway_adapter(api_key="your_runway_api_key")

    response = pipeline.generate_video(
        prompt="A serene sunset over the ocean with waves gently crashing",
        provider=ProviderType.RUNWAY,
        model="gen3",
        parameters={
            "duration": 4.0,
            "resolution": "1280x768",
        },
    )

    if response.is_success():
        print(f"Video generated successfully: {response.result['video_url']}")
    else:
        print(f"Error: {response.error.message}")


def retry_with_exponential_backoff_example():
    """Example: Custom retry configuration with exponential backoff."""
    retry_config = RetryConfig(
        max_attempts=5,
        initial_delay=2.0,
        max_delay=120.0,
        backoff_multiplier=3.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        retryable_error_codes=[
            ErrorCode.RATE_LIMIT_EXCEEDED,
            ErrorCode.TIMEOUT,
            ErrorCode.NETWORK_ERROR,
        ],
    )

    config = PipelineConfig(
        retry_config=retry_config,
        enable_cache=True,
        cache_ttl=7200,
    )

    pipeline = VideoGenerationPipeline(config=config)
    pipeline.register_sora_adapter(api_key="your_sora_api_key")

    response = pipeline.generate_video(
        prompt="A futuristic city with flying cars",
        provider=ProviderType.SORA,
        model="sora-1.0",
        parameters={"duration": 10.0, "quality": "high"},
    )

    print(f"Request completed with {pipeline.metrics.retry_attempts} retry attempts")


def fallback_chain_example():
    """Example: Provider fallback chain with automatic failover."""
    fallback_chain = FallbackChain(
        providers=[
            ProviderType.RUNWAY,
            ProviderType.PIKA,
            ProviderType.VEO,
        ],
        enable_automatic_fallback=True,
        fallback_on_error_codes=[
            ErrorCode.RATE_LIMIT_EXCEEDED,
            ErrorCode.TIMEOUT,
            ErrorCode.INSUFFICIENT_CREDITS,
        ],
    )

    config = PipelineConfig(
        fallback_chain=fallback_chain,
        enable_cache=True,
        enable_metrics=True,
    )

    pipeline = VideoGenerationPipeline(config=config)

    pipeline.register_runway_adapter(api_key="runway_key")
    pipeline.register_pika_adapter(api_key="pika_key")
    pipeline.register_veo_adapter(api_key="veo_key")

    response = pipeline.generate_video(
        prompt="A magical forest with glowing mushrooms",
        provider=ProviderType.RUNWAY,
        model="gen3",
        parameters={"duration": 5.0},
    )

    print(f"Final provider used: {response.provider}")
    print(f"Fallback invocations: {pipeline.metrics.fallback_invocations}")


def multi_provider_with_caching_example():
    """Example: Multiple providers with cache optimization."""
    config = PipelineConfig(
        enable_cache=True,
        cache_ttl=3600,
        cache_max_size=500,
        enable_metrics=True,
    )

    pipeline = VideoGenerationPipeline(config=config)

    pipeline.register_flux_adapter(api_key="flux_key")
    pipeline.register_runway_adapter(api_key="runway_key")
    pipeline.register_sora_adapter(api_key="sora_key")
    pipeline.register_pika_adapter(api_key="pika_key")
    pipeline.register_veo_adapter(api_key="veo_key")

    prompt = "A dragon flying through clouds"

    response1 = pipeline.generate_video(
        prompt=prompt,
        provider=ProviderType.RUNWAY,
        model="gen3",
        parameters={"duration": 4.0},
    )
    print(f"First request - Cache hit: {pipeline.metrics.cache_hits > 0}")

    response2 = pipeline.generate_video(
        prompt=prompt,
        provider=ProviderType.RUNWAY,
        model="gen3",
        parameters={"duration": 4.0},
    )
    print(f"Second request (cached) - Cache hit: {pipeline.metrics.cache_hits > 0}")

    metrics = pipeline.get_metrics()
    print(f"Cache hit rate: {metrics['cache_hit_rate']:.2%}")


def callback_and_metrics_example():
    """Example: Using callbacks and monitoring metrics."""

    def on_video_complete(response):
        if response.is_success():
            print(f"✓ Video ready: {response.result.get('video_url')}")
            print(f"  Processing time: {response.processing_time_ms:.2f}ms")
        else:
            print(f"✗ Failed: {response.error.message}")

    pipeline = VideoGenerationPipeline()
    pipeline.register_runway_adapter(api_key="runway_key")
    pipeline.register_pika_adapter(api_key="pika_key")

    prompts = [
        "A cat playing piano",
        "Northern lights over mountains",
        "Underwater coral reef scene",
    ]

    for prompt in prompts:
        pipeline.generate_video(
            prompt=prompt,
            provider=ProviderType.RUNWAY,
            model="gen3",
            parameters={"duration": 3.0},
            callback=on_video_complete,
        )

    metrics = pipeline.get_metrics()
    print("\n=== Pipeline Metrics ===")
    print(f"Total requests: {metrics['total_requests']}")
    print(f"Success rate: {metrics['success_rate']:.2%}")
    print(f"Average processing time: {metrics['average_processing_time_ms']:.2f}ms")
    print(f"Provider usage: {metrics['provider_usage']}")


def advanced_configuration_example():
    """Example: Advanced configuration with all features."""
    retry_config = RetryConfig(
        max_attempts=4,
        initial_delay=1.5,
        max_delay=90.0,
        backoff_multiplier=2.5,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    )

    fallback_chain = FallbackChain(
        providers=[
            ProviderType.RUNWAY,
            ProviderType.SORA,
            ProviderType.PIKA,
            ProviderType.VEO,
        ],
        enable_automatic_fallback=True,
    )

    config = PipelineConfig(
        enable_cache=True,
        cache_ttl=7200,
        cache_max_size=2000,
        retry_config=retry_config,
        fallback_chain=fallback_chain,
        default_timeout=900,
        enable_metrics=True,
        max_concurrent_requests=20,
    )

    pipeline = VideoGenerationPipeline(config=config)

    pipeline.register_runway_adapter(api_key="runway_key", timeout=600)
    pipeline.register_sora_adapter(api_key="sora_key", timeout=600)
    pipeline.register_pika_adapter(api_key="pika_key", timeout=600)
    pipeline.register_veo_adapter(api_key="veo_key", timeout=600)

    response = pipeline.generate_video(
        prompt="Epic space battle with lasers and starships",
        provider=ProviderType.RUNWAY,
        model="gen3",
        parameters={
            "duration": 8.0,
            "resolution": "1920x1080",
            "motion_strength": 0.8,
        },
        metadata={
            "project_id": "proj_123",
            "user_id": "user_456",
        },
    )

    print(f"Status: {response.status}")
    print(f"Provider: {response.provider}")
    print(f"Processing time: {response.processing_time_ms}ms")

    health_status = pipeline.health_check()
    print("\n=== Provider Health ===")
    for provider, is_healthy in health_status.items():
        print(f"{provider}: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")

    capabilities = pipeline.get_adapter_capabilities(ProviderType.RUNWAY)
    if capabilities:
        print("\n=== Runway Capabilities ===")
        print(f"Max resolution: {capabilities['max_resolution']}")
        print(f"Max duration: {capabilities['max_duration']}s")
        print(f"Features: {list(capabilities['features'].keys())}")


def cache_management_example():
    """Example: Cache management and invalidation."""
    pipeline = VideoGenerationPipeline()
    pipeline.register_runway_adapter(api_key="runway_key")

    pipeline.generate_video(
        prompt="Test video 1",
        provider=ProviderType.RUNWAY,
        model="gen3",
        parameters={"duration": 3.0},
    )

    print(f"Cache size: {pipeline.cache.get_stats()['size']}")

    pipeline.invalidate_cache(provider="runway", model="gen3")
    print(f"Cache size after invalidation: {pipeline.cache.get_stats()['size']}")

    pipeline.generate_video(
        prompt="Test video 2",
        provider=ProviderType.RUNWAY,
        model="gen3",
        parameters={"duration": 3.0},
    )

    pipeline.clear_cache()
    print(f"Cache size after clear: {pipeline.cache.get_stats()['size']}")


if __name__ == "__main__":
    print("=== Basic Usage Example ===")
    basic_usage_example()

    print("\n=== Retry with Exponential Backoff ===")
    retry_with_exponential_backoff_example()

    print("\n=== Fallback Chain Example ===")
    fallback_chain_example()

    print("\n=== Multi-Provider with Caching ===")
    multi_provider_with_caching_example()

    print("\n=== Callback and Metrics ===")
    callback_and_metrics_example()

    print("\n=== Advanced Configuration ===")
    advanced_configuration_example()

    print("\n=== Cache Management ===")
    cache_management_example()
