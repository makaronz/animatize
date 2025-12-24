# Multi-Model Adapter Architecture

## Overview

This document describes the unified multi-model adapter architecture for integrating various AI model providers (Flux, Veo, Runway, Sora, Pika, etc.) with standardized contracts, routing logic, caching, and versioning.

## Architecture Components

### 1. Unified Contracts (`contracts.py`)

#### Schema Versioning
- **Current Version**: `2.0`
- **Supported Versions**: `1.0`, `1.1`, `2.0`
- **Version Format**: Semantic versioning (MAJOR.MINOR)

#### Request Contract (`UnifiedRequest`)
```python
@dataclass
class UnifiedRequest:
    schema_version: SchemaVersion       # Protocol version
    request_id: str                     # Unique identifier for tracking
    provider: ProviderType              # Target provider (flux, veo, runway, etc.)
    model: str                          # Specific model name
    prompt: str                         # Generation prompt
    media_type: MediaType               # Output type (image, video, audio, text)
    parameters: Dict[str, Any]          # Provider-specific parameters
    metadata: Dict[str, Any]            # Additional context
    timestamp: str                      # ISO 8601 timestamp
    timeout: int                        # Request timeout in seconds
    retry_config: Optional[Dict]        # Retry configuration
    callback_url: Optional[str]         # Async callback endpoint
```

#### Response Contract (`UnifiedResponse`)
```python
@dataclass
class UnifiedResponse:
    schema_version: SchemaVersion       # Protocol version
    request_id: str                     # Matches request identifier
    provider: str                       # Provider that handled request
    model: str                          # Model used
    status: str                         # success, failed, processing
    result: Optional[Dict[str, Any]]    # Generated content/URLs
    error: Optional[ErrorDetails]       # Error information if failed
    metadata: Dict[str, Any]            # Response metadata
    timestamp: str                      # ISO 8601 timestamp
    processing_time_ms: Optional[float] # Execution time
    tokens_used: Optional[int]          # Token consumption
    cost: Optional[float]               # Request cost
```

#### Error Contract (`ErrorDetails`)
```python
@dataclass
class ErrorDetails:
    code: ErrorCode                     # Standardized error code
    message: str                        # Human-readable message
    retryable: bool                     # Can be retried?
    provider: str                       # Provider that errored
    details: Optional[Dict[str, Any]]   # Additional error context
    timestamp: str                      # When error occurred
    retry_after: Optional[int]          # Seconds to wait before retry
```

#### Error Codes
- `INVALID_REQUEST` - Malformed or invalid request parameters
- `AUTHENTICATION_FAILED` - API key or auth issues
- `RATE_LIMIT_EXCEEDED` - Rate limit hit (retryable)
- `PROVIDER_ERROR` - Provider-specific error
- `TIMEOUT` - Request timeout (retryable)
- `INVALID_MODEL` - Model not found or unsupported
- `INSUFFICIENT_CREDITS` - Quota/credits exhausted
- `CONTENT_POLICY_VIOLATION` - Content filtered
- `NETWORK_ERROR` - Network connectivity issues (retryable)
- `UNKNOWN_ERROR` - Unclassified error

### 2. Base Adapter (`base.py`)

All model adapters extend `BaseModelAdapter` and implement core methods for request transformation, API calls, and response handling.

### 3. Provider Adapters

#### FluxAdapter (Image Generation)
- **Max Resolution**: 2048x2048
- **Rate Limit**: 60 req/min
- **Features**: Text-to-image, image-to-image, inpainting, ControlNet, LoRA

#### VeoAdapter (Video Generation)
- **Max Resolution**: 1920x1080
- **Max Duration**: 120 seconds
- **Rate Limit**: 10 req/min

#### RunwayAdapter, SoraAdapter, PikaAdapter
Each with specific capabilities and rate limits.

### 4. Routing Logic (`router.py`)

#### Routing Strategies
1. **Priority-based** - Routes by assigned priority
2. **Round-robin** - Even distribution across providers
3. **Weighted** - Proportional distribution
4. **Least-loaded** - Routes to least busy provider
5. **Latency-based** - Routes to fastest provider

#### Features
- Automatic fallback on provider failure
- Exponential backoff retry logic
- Circuit breaker pattern (auto-disable failing providers)
- Health monitoring

### 5. Cache Layer (`cache.py`)

#### Cache Key Generation
```python
key = f"{provider}:{model}:{hash(prompt)}:{hash(parameters)}"
```

#### Strategies
- **LRU** (Least Recently Used)
- **LFU** (Least Frequently Used)
- **TTL** (Time To Live)

#### Features
- Configurable TTL (default: 3600s)
- Pattern-based invalidation
- Provider/model-specific invalidation
- Statistics tracking (hit rate, evictions, etc.)
- Tiered caching (L1/L2)

### 6. Versioning Strategy (`versioning.py`)

#### Migration System
- Forward migrations: v1.0 → v1.1 → v2.0
- Backward compatibility per migration
- Automatic path finding for multi-hop migrations

#### Supported Migrations
- **v1.0 → v1.1**: Add metadata, retry_config (backward compatible)
- **v1.1 → v2.0**: Restructure provider info, enhance errors (breaking)

## Usage Examples

### Basic Usage
```python
from src.adapters import FluxAdapter, AdapterRouter, UnifiedRequest

flux = FluxAdapter(api_key="key")
router = AdapterRouter()
router.register_provider("flux", flux, priority=1)

request = UnifiedRequest(
    schema_version=SchemaVersion.V2_0,
    request_id=str(uuid.uuid4()),
    provider=ProviderType.FLUX,
    model="flux-pro",
    prompt="Mountain landscape",
    media_type=MediaType.IMAGE,
)

response = router.execute(request)
```

### With Caching
```python
cache = AdapterCache(max_size=1000, strategy=CacheStrategy.LRU)
router = AdapterRouter(cache=cache)
```

## Configuration

Environment variables for API keys, cache settings, and routing strategy can be configured via `.env` file or system environment.

## Security

- Store API keys securely
- Validate all inputs
- Sanitize prompts
- Never log sensitive data

## Future Enhancements

- Webhook support for async callbacks
- Request queueing and prioritization
- Multi-region provider support
- Real-time provider health scoring
- Distributed caching (Redis/Memcached)
