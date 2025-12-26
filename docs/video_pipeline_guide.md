# Video Generation Pipeline Guide

## Overview

The VideoGenerationPipeline provides a unified interface for generating videos across multiple providers (Flux, VEO, Runway, Sora, Pika) with built-in retry logic, fallback chains, caching, and metrics tracking.

## Features

- **Unified Interface**: Single API for all video generation providers
- **Automatic Retry**: Exponential backoff for transient failures
- **Provider Fallback**: Automatic failover between providers
- **Smart Caching**: Deduplicate requests and optimize costs
- **Metrics Tracking**: Monitor performance and usage patterns
- **Error Handling**: Comprehensive error codes and retryable detection
- **Health Checks**: Monitor provider availability

## Quick Start

```python
from src.core.video_pipeline import VideoGenerationPipeline
from src.adapters.contracts import ProviderType

# Initialize pipeline
pipeline = VideoGenerationPipeline()

# Register providers
pipeline.register_runway_adapter(api_key="your_api_key")
pipeline.register_sora_adapter(api_key="your_api_key")

# Generate video
response = pipeline.generate_video(
    prompt="A sunset over mountains",
    provider=ProviderType.RUNWAY,
    model="gen3",
    parameters={"duration": 4.0}
)

if response.is_success():
    print(f"Video URL: {response.result['video_url']}")
```

## Core Components

### VideoGenerationPipeline

Main orchestrator class that manages providers, caching, retries, and fallbacks.

**Key Methods:**
- `register_adapter()` - Register a provider adapter
- `generate_video()` - Generate a video with specified parameters
- `execute_request()` - Execute a pre-built UnifiedRequest
- `batch_generate()` - Process multiple requests
- `get_metrics()` - Retrieve pipeline statistics
- `health_check()` - Check provider health status

### Configuration Classes

#### PipelineConfig

```python
config = PipelineConfig(
    enable_cache=True,              # Enable response caching
    cache_ttl=3600,                 # Cache TTL in seconds
    cache_max_size=1000,            # Maximum cache entries
    retry_config=RetryConfig(),     # Retry configuration
    fallback_chain=FallbackChain(), # Fallback configuration
    default_timeout=600,            # Default request timeout
    enable_metrics=True,            # Track metrics
    max_concurrent_requests=10      # Concurrency limit
)
```

#### RetryConfig

```python
from src.core.video_pipeline import RetryConfig, RetryStrategy

retry_config = RetryConfig(
    max_attempts=3,                 # Maximum retry attempts
    initial_delay=1.0,              # Initial delay in seconds
    max_delay=60.0,                 # Maximum delay cap
    backoff_multiplier=2.0,         # Exponential multiplier
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    retryable_error_codes=[...]     # Error codes to retry
)
```

**Retry Strategies:**
- `EXPONENTIAL_BACKOFF` - Delay doubles each attempt
- `LINEAR_BACKOFF` - Delay increases linearly
- `FIXED_DELAY` - Same delay for all retries

#### FallbackChain

```python
from src.core.video_pipeline import FallbackChain

fallback_chain = FallbackChain(
    providers=[
        ProviderType.RUNWAY,
        ProviderType.PIKA,
        ProviderType.VEO
    ],
    enable_automatic_fallback=True,
    fallback_on_error_codes=[
        ErrorCode.RATE_LIMIT_EXCEEDED,
        ErrorCode.TIMEOUT,
        ErrorCode.PROVIDER_ERROR
    ]
)
```

## Provider Adapters

### Supported Providers

| Provider | Media Types | Max Duration | Special Features |
|----------|-------------|--------------|------------------|
| Flux | Image | N/A | LoRA, ControlNet, Inpainting |
| VEO | Video | 120s | Camera control, Motion control |
| Runway | Video | 16s | Motion brush, Upscaling |
| Sora | Video | 60s | Style transfer, Prompt enhancement |
| Pika | Video | 10s | Lip sync, Sound effects |

### Registering Adapters

```python
# Method 1: Direct registration
pipeline.register_runway_adapter(api_key="key", timeout=600)

# Method 2: Custom adapter
from src.adapters import RunwayAdapter
adapter = RunwayAdapter(api_key="key", timeout=600)
pipeline.register_adapter(ProviderType.RUNWAY, adapter)
```

## Unified Contracts

### UnifiedRequest

```python
from src.adapters.contracts import UnifiedRequest, SchemaVersion, MediaType

request = UnifiedRequest(
    schema_version=SchemaVersion.V2_0,
    request_id="unique-id",
    provider=ProviderType.RUNWAY,
    model="gen3",
    prompt="A serene beach at sunset",
    media_type=MediaType.VIDEO,
    parameters={
        "duration": 4.0,
        "resolution": "1280x768",
        "fps": 24
    },
    metadata={
        "user_id": "user_123",
        "project_id": "proj_456"
    }
)
```

### UnifiedResponse

```python
response = pipeline.execute_request(request)

# Check status
if response.is_success():
    video_url = response.result['video_url']
    print(f"Generated in {response.processing_time_ms}ms")
    
elif response.is_retryable():
    print(f"Retryable error: {response.error.message}")
    
else:
    print(f"Permanent failure: {response.error.code}")
```

## Caching

### Cache Layer Integration

The pipeline automatically caches successful responses based on:
- Provider name
- Model name
- Prompt text
- Parameters hash

```python
# Enable caching
config = PipelineConfig(
    enable_cache=True,
    cache_ttl=3600,  # 1 hour
    cache_max_size=1000
)

pipeline = VideoGenerationPipeline(config)

# First request - cache miss
response1 = pipeline.generate_video(...)

# Second identical request - cache hit
response2 = pipeline.generate_video(...)
```

### Cache Management

```python
# Get cache statistics
stats = pipeline.get_metrics()
print(f"Cache hit rate: {stats['cache_hit_rate']}")

# Invalidate specific cache entries
pipeline.invalidate_cache(provider="runway", model="gen3")

# Clear entire cache
pipeline.clear_cache()
```

## Error Handling

### Error Codes

```python
from src.adapters.contracts import ErrorCode

ErrorCode.INVALID_REQUEST          # Bad request parameters
ErrorCode.AUTHENTICATION_FAILED    # Invalid API key
ErrorCode.RATE_LIMIT_EXCEEDED      # Rate limit hit
ErrorCode.TIMEOUT                  # Request timeout
ErrorCode.PROVIDER_ERROR           # Provider-side error
ErrorCode.INSUFFICIENT_CREDITS     # Out of credits
ErrorCode.CONTENT_POLICY_VIOLATION # Content filtered
ErrorCode.NETWORK_ERROR            # Network issues
```

### Handling Errors

```python
response = pipeline.generate_video(...)

if not response.is_success():
    error = response.error
    
    if error.code == ErrorCode.RATE_LIMIT_EXCEEDED:
        print(f"Rate limited. Retry after {error.retry_after}s")
    
    elif error.retryable:
        print("Transient error - will retry automatically")
    
    else:
        print(f"Permanent failure: {error.message}")
        print(f"Details: {error.details}")
```

## Metrics and Monitoring

### Pipeline Metrics

```python
metrics = pipeline.get_metrics()

print(f"Total requests: {metrics['total_requests']}")
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Cache hit rate: {metrics['cache_hit_rate']:.2%}")
print(f"Retry attempts: {metrics['retry_attempts']}")
print(f"Fallback invocations: {metrics['fallback_invocations']}")
print(f"Average processing time: {metrics['average_processing_time_ms']}ms")

# Provider usage breakdown
for provider, count in metrics['provider_usage'].items():
    print(f"{provider}: {count} requests")

# Error distribution
for error_code, count in metrics['error_distribution'].items():
    print(f"{error_code}: {count} occurrences")
```

### Health Checks

```python
health = pipeline.health_check()

for provider, is_healthy in health.items():
    status = "✓" if is_healthy else "✗"
    print(f"{status} {provider}")
```

## Advanced Usage

### Callbacks

```python
def on_complete(response):
    if response.is_success():
        print(f"Video ready: {response.result['video_url']}")

pipeline.generate_video(
    prompt="...",
    provider=ProviderType.RUNWAY,
    model="gen3",
    callback=on_complete
)
```

### Batch Processing

```python
requests = [
    UnifiedRequest(...),
    UnifiedRequest(...),
    UnifiedRequest(...)
]

responses = pipeline.batch_generate(
    requests=requests,
    retry_config=custom_retry_config,
    fallback_chain=custom_fallback_chain
)
```

### Provider Capabilities

```python
caps = pipeline.get_adapter_capabilities(ProviderType.RUNWAY)

print(f"Max resolution: {caps['max_resolution']}")
print(f"Max duration: {caps['max_duration']}s")
print(f"Supports batch: {caps['supports_batch']}")
print(f"Rate limit: {caps['rate_limit_per_minute']} req/min")
print(f"Features: {caps['features']}")
```

## Best Practices

1. **Always use fallback chains** for production workloads
2. **Enable caching** to reduce costs and improve latency
3. **Configure appropriate retry settings** based on your SLA
4. **Monitor metrics regularly** to optimize provider selection
5. **Use callbacks** for async processing patterns
6. **Set reasonable timeouts** based on expected video duration
7. **Handle errors gracefully** with proper user feedback

## Example: Production Setup

```python
from src.core.video_pipeline import (
    VideoGenerationPipeline,
    PipelineConfig,
    RetryConfig,
    RetryStrategy,
    FallbackChain,
)
from src.adapters.contracts import ProviderType

# Production configuration
retry_config = RetryConfig(
    max_attempts=4,
    initial_delay=2.0,
    max_delay=120.0,
    backoff_multiplier=2.5,
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
)

fallback_chain = FallbackChain(
    providers=[
        ProviderType.RUNWAY,
        ProviderType.PIKA,
        ProviderType.VEO,
        ProviderType.SORA,
    ],
    enable_automatic_fallback=True,
)

config = PipelineConfig(
    enable_cache=True,
    cache_ttl=7200,
    cache_max_size=5000,
    retry_config=retry_config,
    fallback_chain=fallback_chain,
    enable_metrics=True,
)

# Initialize pipeline
pipeline = VideoGenerationPipeline(config)

# Register all providers
pipeline.register_runway_adapter(api_key=RUNWAY_KEY)
pipeline.register_pika_adapter(api_key=PIKA_KEY)
pipeline.register_veo_adapter(api_key=VEO_KEY)
pipeline.register_sora_adapter(api_key=SORA_KEY)

# Health check on startup
health = pipeline.health_check()
print(f"Healthy providers: {sum(health.values())}/{len(health)}")

# Generate video with full resilience
response = pipeline.generate_video(
    prompt="A beautiful landscape",
    provider=ProviderType.RUNWAY,
    model="gen3",
    parameters={"duration": 5.0},
)
```

## Troubleshooting

### Common Issues

**Cache not working:**
- Verify `enable_cache=True` in PipelineConfig
- Check cache key generation matches exactly (same prompt, params)

**Retries not happening:**
- Ensure error is in `retryable_error_codes` list
- Check `max_attempts` is > 1
- Verify error has `retryable=True` flag

**Fallback not triggering:**
- Confirm error code is in `fallback_on_error_codes`
- Check multiple providers are registered
- Verify `enable_automatic_fallback=True`

**High latency:**
- Enable caching to reduce API calls
- Reduce `max_attempts` if not needed
- Use provider-specific timeouts
- Check network connectivity

## API Reference

See individual module documentation:
- `src/core/video_pipeline.py` - Pipeline orchestrator
- `src/adapters/contracts.py` - Unified contracts
- `src/adapters/cache.py` - Cache layer
- `src/adapters/base.py` - Base adapter class
- Provider adapters: `flux_adapter.py`, `veo_adapter.py`, etc.
