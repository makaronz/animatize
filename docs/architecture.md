# ANIMAtiZE Framework - Complete Architecture Documentation

## Version: 2.0.0
**Last Updated:** 2025-01-28  
**Status:** Production-Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [End-to-End Flow Diagram](#end-to-end-flow-diagram)
3. [Module Contracts & Interfaces](#module-contracts--interfaces)
4. [Storage & Cache Design](#storage--cache-design)
5. [Multi-Model Routing & Fallback Logic](#multi-model-routing--fallback-logic)
6. [Versioning Strategy](#versioning-strategy)
7. [Observability & Logging](#observability--logging)
8. [Deployment Considerations](#deployment-considerations)
9. [Error Handling & Retry Policies](#error-handling--retry-policies)
10. [Security Considerations](#security-considerations)

---

## System Overview

ANIMAtiZE is a production-ready framework that transforms static images into cinematic video prompts through computer vision analysis, AI-powered movement prediction, and multi-model video generation orchestration.

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     ANIMAtiZE Framework                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Analyzers  │  │  Generators  │  │   Adapters   │         │
│  │              │  │              │  │              │         │
│  │  - Movement  │  │  - Prompt    │  │  - Flux      │         │
│  │  - Scene     │  │    Expander  │  │  - VEO       │         │
│  │  - Motion    │  │  - Video     │  │  - Runway    │         │
│  │              │  │    Generator │  │  - Sora      │         │
│  └──────────────┘  └──────────────┘  │  - Pika      │         │
│                                       └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Consistency  │  │  Evaluation  │  │   Feedback   │         │
│  │   Engine     │  │   System     │  │   System     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │          Router & Cache Infrastructure            │          │
│  │  - Multi-level cache (L1/L2)                      │          │
│  │  - Intelligent routing (Priority/RR/Weighted)     │          │
│  │  - Circuit breaker pattern                        │          │
│  │  - Retry with exponential backoff                 │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Language:** Python 3.8+
- **Computer Vision:** OpenCV 4.x, NumPy
- **AI/ML:** OpenAI GPT-4, Google Imagen, Runway Gen-2, Flux, VEO, Sora, Pika
- **Storage:** In-memory (OrderedDict), Redis (optional), File system
- **Observability:** Python logging, Custom metrics
- **Testing:** pytest, 95%+ coverage

---

## End-to-End Flow Diagram

### Request Flow (Text-based Diagram)

```
┌─────────────┐
│   Client    │
│  Request    │
└──────┬──────┘
       │
       │ 1. Image + Config
       ▼
┌─────────────────────────────────────────┐
│        ANIMAtiZE Framework              │
│  ┌────────────────────────────────┐     │
│  │  Request Validation & Schema   │     │
│  │  Version Detection (1.0/1.1/2.0)│    │
│  └─────────────┬──────────────────┘     │
│                │                         │
│       2. Validate & Transform           │
│                ▼                         │
│  ┌────────────────────────────────┐     │
│  │    Image Analysis Pipeline     │     │
│  │                                 │     │
│  │  ┌──────────────────────────┐  │     │
│  │  │ Scene Analyzer           │  │     │
│  │  │ - Composition analysis   │  │     │
│  │  │ - Object detection       │  │     │
│  │  │ - Lighting analysis      │  │     │
│  │  └──────────┬───────────────┘  │     │
│  │             │                   │     │
│  │  ┌──────────▼───────────────┐  │     │
│  │  │ Movement Predictor       │  │     │
│  │  │ - Pose analysis          │  │     │
│  │  │ - Physics-based motion   │  │     │
│  │  │ - Cinematic rules (47+)  │  │     │
│  │  └──────────┬───────────────┘  │     │
│  │             │                   │     │
│  │  ┌──────────▼───────────────┐  │     │
│  │  │ Motion Detector          │  │     │
│  │  │ - Optical flow analysis  │  │     │
│  │  │ - Environmental motion   │  │     │
│  │  └──────────┬───────────────┘  │     │
│  └─────────────┼──────────────────┘     │
│                │                         │
│       3. Analysis Results               │
│                ▼                         │
│  ┌────────────────────────────────┐     │
│  │   Consistency Engine            │     │
│  │   (Optional - Cross-shot)       │     │
│  │  - Identity preservation        │     │
│  │  - Style anchors                │     │
│  │  - Temporal coherence           │     │
│  └─────────────┬──────────────────┘     │
│                │                         │
│       4. Validated Analysis             │
│                ▼                         │
│  ┌────────────────────────────────┐     │
│  │   Prompt Expansion              │     │
│  │  - GPT-4 enhancement            │     │
│  │  - Cinematic language           │     │
│  │  - Model-specific formatting    │     │
│  └─────────────┬──────────────────┘     │
│                │                         │
│       5. Enhanced Prompt                │
│                ▼                         │
│  ┌────────────────────────────────┐     │
│  │    Router Layer                 │     │
│  │  - Cache lookup (L1/L2)         │     │
│  │  - Provider selection           │     │
│  │  - Load balancing               │     │
│  │  - Circuit breaker check        │     │
│  └─────────────┬──────────────────┘     │
│                │                         │
│       6. Route to Provider              │
│                ▼                         │
│  ┌────────────────────────────────┐     │
│  │    Adapter Layer                │     │
│  │  ┌───────┬───────┬───────┬───┐ │     │
│  │  │ Flux  │  VEO  │Runway │etc│ │     │
│  │  └───┬───┴───┬───┴───┬───┴───┘ │     │
│  │      │       │       │          │     │
│  │  7. Transform Request            │     │
│  │      │       │       │          │     │
│  │      ▼       ▼       ▼          │     │
│  │  Provider-specific API calls    │     │
│  └─────────────┬──────────────────┘     │
│                │                         │
└────────────────┼─────────────────────────┘
                 │
       8. API Call to Provider
                 ▼
┌─────────────────────────────────────┐
│    External Video Generation APIs   │
│  ┌───────┬───────┬───────┬───────┐ │
│  │ Flux  │  VEO  │Runway │ Pika  │ │
│  │  API  │  API  │  API  │  API  │ │
│  └───┬───┴───┬───┴───┬───┴───┬───┘ │
│      │       │       │       │     │
│      └───────┴───┬───┴───────┘     │
│                  │                  │
└──────────────────┼──────────────────┘
                   │
       9. Provider Response
                   ▼
┌─────────────────────────────────────────┐
│        ANIMAtiZE Framework              │
│  ┌────────────────────────────────┐     │
│  │  Response Transformation        │     │
│  │  - Normalize format             │     │
│  │  - Extract metadata             │     │
│  │  - Error mapping                │     │
│  └─────────────┬──────────────────┘     │
│                │                         │
│      10. Transform Response             │
│                ▼                         │
│  ┌────────────────────────────────┐     │
│  │   Cache Update                  │     │
│  │  - Store successful results     │     │
│  │  - Update metrics               │     │
│  │  - Record latency               │     │
│  └─────────────┬──────────────────┘     │
│                │                         │
│      11. Cache & Metrics                │
│                ▼                         │
│  ┌────────────────────────────────┐     │
│  │   Evaluation & Feedback         │     │
│  │  - Quality metrics              │     │
│  │  - Performance tracking         │     │
│  │  - Regression testing           │     │
│  └─────────────┬──────────────────┘     │
│                │                         │
└────────────────┼─────────────────────────┘
                 │
      12. Final Response
                 ▼
         ┌─────────────┐
         │   Client    │
         │  Response   │
         └─────────────┘
```

### Data Flow Summary

1. **Input:** Image file + configuration (style, model preferences, parameters)
2. **Analysis:** Computer vision analysis extracts scene features
3. **Prediction:** AI predicts cinematic movements based on 47+ rules
4. **Enhancement:** GPT-4 expands prompts with cinematic language
5. **Routing:** Intelligent router selects optimal provider
6. **Transformation:** Adapter converts unified request to provider format
7. **Execution:** External API generates video/animation
8. **Response:** Unified response format returned to client
9. **Caching:** Successful results cached for reuse
10. **Evaluation:** Quality metrics tracked for continuous improvement

---

## Module Contracts & Interfaces

### 1. Adapter Layer Contracts

#### Base Adapter Interface

```python
# src/adapters/base.py

class BaseModelAdapter(ABC):
    """Abstract base adapter for all AI model providers"""
    
    @abstractmethod
    def _get_provider_name(self) -> str:
        """Return provider identifier (e.g., 'flux', 'veo')"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ModelCapabilities:
        """
        Return provider capabilities
        
        Returns:
            ModelCapabilities: Supported formats, resolutions, features
        """
        pass
    
    @abstractmethod
    def _transform_request(self, request: UnifiedRequest) -> Dict[str, Any]:
        """
        Transform unified request to provider-specific format
        
        Args:
            request: Unified request object
            
        Returns:
            Dict: Provider-specific request payload
        """
        pass
    
    @abstractmethod
    def _transform_response(
        self, 
        provider_response: Dict[str, Any],
        request: UnifiedRequest
    ) -> UnifiedResponse:
        """
        Transform provider response to unified format
        
        Args:
            provider_response: Raw provider API response
            request: Original unified request
            
        Returns:
            UnifiedResponse: Normalized response object
        """
        pass
    
    @abstractmethod
    def _make_api_call(self, transformed_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute provider API call
        
        Args:
            transformed_request: Provider-specific request
            
        Returns:
            Dict: Raw provider response
            
        Raises:
            NetworkError, TimeoutError, AuthenticationError
        """
        pass
    
    def validate_request(self, request: UnifiedRequest) -> Optional[ErrorDetails]:
        """Validate request against provider capabilities"""
        pass
    
    def execute(self, request: UnifiedRequest) -> UnifiedResponse:
        """Main execution method with validation, transformation, error handling"""
        pass
    
    def health_check(self) -> bool:
        """Check provider availability and health"""
        pass
```

#### Unified Request Contract

```python
# src/adapters/contracts.py

@dataclass
class UnifiedRequest:
    """Unified request format across all providers"""
    
    schema_version: SchemaVersion      # "1.0", "1.1", "2.0"
    request_id: str                    # Unique identifier (UUID)
    provider: ProviderType             # Target provider enum
    model: str                         # Model identifier
    prompt: str                        # Generation prompt
    media_type: MediaType              # "image", "video", "audio", "text"
    parameters: Dict[str, Any]         # Provider-specific parameters
    metadata: Dict[str, Any]           # Client metadata
    timestamp: str                     # ISO 8601 timestamp
    timeout: int                       # Request timeout (seconds)
    retry_config: Optional[Dict]       # Retry configuration
    callback_url: Optional[str]        # Async callback URL
```

#### Unified Response Contract

```python
@dataclass
class UnifiedResponse:
    """Unified response format from all providers"""
    
    schema_version: SchemaVersion
    request_id: str                    # Matches request ID
    provider: str                      # Provider name
    model: str                         # Model used
    status: str                        # "success", "failed", "processing"
    result: Optional[Dict[str, Any]]   # Generation results
    error: Optional[ErrorDetails]      # Error details if failed
    metadata: Dict[str, Any]           # Response metadata
    timestamp: str                     # ISO 8601 timestamp
    processing_time_ms: Optional[float]  # Processing latency
    tokens_used: Optional[int]         # Tokens consumed (if applicable)
    cost: Optional[float]              # Cost in USD (if tracked)
    
    def is_success(self) -> bool:
        """Check if request succeeded"""
        return self.status == "success" and self.error is None
    
    def is_retryable(self) -> bool:
        """Check if failed request can be retried"""
        return self.error is not None and self.error.retryable
```

#### Model Capabilities Contract

```python
@dataclass
class ModelCapabilities:
    """Provider model capabilities and limits"""
    
    max_resolution: tuple[int, int]    # Maximum (width, height)
    supported_formats: List[str]       # ["image/png", "video/mp4", ...]
    max_duration: Optional[float]      # Max video duration (seconds)
    supports_batch: bool               # Batch processing support
    supports_streaming: bool           # Streaming response support
    max_batch_size: Optional[int]      # Max items per batch
    rate_limit_per_minute: Optional[int]  # API rate limit
    features: Dict[str, bool]          # Feature flags
        # Example: {
        #   "text_to_image": True,
        #   "image_to_image": True,
        #   "inpainting": False,
        #   "controlnet": True,
        #   "temporal_consistency": True
        # }
```

### 2. Router Layer Interface

```python
# src/adapters/router.py

class AdapterRouter:
    """Intelligent routing layer with load balancing and failover"""
    
    def register_provider(
        self,
        provider_name: str,
        adapter: BaseModelAdapter,
        priority: int = 1,
        weight: float = 1.0,
        enabled: bool = True
    ):
        """
        Register a provider adapter
        
        Args:
            provider_name: Unique provider identifier
            adapter: Provider adapter instance
            priority: Priority for PRIORITY routing (higher = preferred)
            weight: Weight for WEIGHTED routing (higher = more traffic)
            enabled: Enable/disable provider
        """
        pass
    
    def execute(self, request: UnifiedRequest) -> UnifiedResponse:
        """
        Execute request with routing, caching, retry, and fallback
        
        Flow:
            1. Check cache (L1 -> L2)
            2. Select provider based on strategy
            3. Execute with retry and exponential backoff
            4. Fallback to alternate providers on failure
            5. Cache successful results
            6. Return unified response
        
        Args:
            request: Unified request
            
        Returns:
            UnifiedResponse: Processed response
        """
        pass
    
    def get_provider_stats(self) -> Dict[str, Dict]:
        """Get real-time provider statistics"""
        pass
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all registered providers"""
        pass
```

### 3. Cache Layer Interface

```python
# src/adapters/cache.py

class AdapterCache:
    """Multi-level cache with LRU/LFU/TTL eviction"""
    
    def generate_cache_key(
        self,
        provider: str,
        model: str,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Generate deterministic cache key
        
        Format: {provider}:{model}:{prompt_hash}:{params_hash}
        """
        pass
    
    def get(self, cache_key: str) -> Optional[UnifiedResponse]:
        """Retrieve cached response with expiration check"""
        pass
    
    def set(
        self,
        cache_key: str,
        response: UnifiedResponse,
        ttl: Optional[int] = None
    ):
        """Store response with TTL"""
        pass
    
    def invalidate_provider(self, provider: str) -> int:
        """Invalidate all cache entries for a provider"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Return cache statistics
        
        Returns:
            {
                "size": 150,
                "max_size": 1000,
                "hits": 1200,
                "misses": 300,
                "hit_rate": 0.80,
                "evictions": 50,
                "expired": 25
            }
        """
        pass
```

### 4. Analyzer Interface

```python
# src/analyzers/movement_predictor.py

class MovementPredictor:
    """Predict cinematic movements from static images"""
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze image and predict movements
        
        Args:
            image_path: Path to image file
            
        Returns:
            {
                "image_path": str,
                "image_size": (width, height),
                "movement_predictions": {
                    "character_actions": List[Dict],
                    "camera_movements": List[Dict],
                    "environment_animations": List[Dict]
                },
                "justifications": Dict,
                "generated_prompts": List[str]
            }
        """
        pass
    
    def _analyze_character_movement(self, image: np.ndarray) -> List[Dict]:
        """Analyze character poses and predict actions"""
        pass
    
    def _analyze_camera_movement(self, image: np.ndarray) -> List[Dict]:
        """Analyze composition and predict camera movements"""
        pass
    
    def _analyze_environmental_motion(self, image: np.ndarray) -> List[Dict]:
        """Analyze environmental elements and predict motion"""
        pass
```

### 5. Prompt Expander Interface

```python
# src/core/prompt_expander.py

class PromptExpander:
    """Expand prompts with GPT-4 for cinematic language"""
    
    def expand_prompt(
        self,
        base_prompt: str,
        model_target: str,
        cinematic_style: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Expand prompt with cinematic language
        
        Args:
            base_prompt: Basic movement description
            model_target: Target model (flux, veo, etc.)
            cinematic_style: Style enum (neo_noir, documentary, etc.)
            metadata: Additional context
            
        Returns:
            {
                "expanded_prompt": str,
                "model_specific_prompt": str,
                "prompt_version": str,
                "confidence": float,
                "tokens_used": int
            }
        """
        pass
```

### 6. Consistency Engine Interface

```python
# src/wedge_features/consistency_engine.py

class ConsistencyEngine:
    """Cross-shot consistency management"""
    
    def validate_sequence(
        self,
        shots: List[Dict],
        consistency_rules: Dict
    ) -> Dict:
        """
        Validate consistency across shot sequence
        
        Args:
            shots: List of shot definitions
            consistency_rules: Validation rules
            
        Returns:
            {
                "is_consistent": bool,
                "violations": List[Dict],
                "suggestions": List[str],
                "consistency_score": float
            }
        """
        pass
    
    def generate_reference_library(self, images: List[str]) -> Dict:
        """Generate reference library for characters/styles"""
        pass
```

---

## Storage & Cache Design

### Multi-Level Cache Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Cache Hierarchy                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │  L1 Cache (In-Memory / Hot Cache)                │     │
│  │  - Implementation: OrderedDict (Python)           │     │
│  │  - Max Size: 1000 entries (configurable)          │     │
│  │  - TTL: 1 hour (default)                          │     │
│  │  - Eviction: LRU (Least Recently Used)            │     │
│  │  - Use Case: Frequently accessed prompts          │     │
│  │  - Hit Rate Target: >80%                          │     │
│  │  - Access Time: <1ms                              │     │
│  └────────────────┬─────────────────────────────────┘     │
│                   │ Cache Miss                             │
│                   ▼                                         │
│  ┌──────────────────────────────────────────────────┐     │
│  │  L2 Cache (Redis / Warm Cache) - OPTIONAL        │     │
│  │  - Implementation: Redis (if configured)          │     │
│  │  - Max Size: 10000 entries                        │     │
│  │  - TTL: 24 hours                                  │     │
│  │  - Eviction: TTL-based + LRU fallback             │     │
│  │  - Use Case: Shared cache across instances        │     │
│  │  - Hit Rate Target: >60%                          │     │
│  │  - Access Time: <10ms                             │     │
│  └────────────────┬─────────────────────────────────┘     │
│                   │ Cache Miss                             │
│                   ▼                                         │
│  ┌──────────────────────────────────────────────────┐     │
│  │  Provider API Call (Cold Path)                    │     │
│  │  - Full request processing                        │     │
│  │  - Result stored in L1 & L2                       │     │
│  │  - Access Time: 2-30 seconds                      │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Cache Key Structure

```
Format: {provider}:{model}:{prompt_hash}:{params_hash}

Components:
  - provider:      Provider name (flux, veo, runway, etc.)
  - model:         Model identifier (flux-pro, veo-2, etc.)
  - prompt_hash:   SHA256 hash of prompt (first 16 chars)
  - params_hash:   SHA256 hash of sorted parameters JSON (first 16 chars)

Example:
  flux:flux-pro-1.1:a3f5e8b2c1d4f6e9:b7c3d9e1f4a6b8c2

Rationale:
  - Deterministic: Same inputs always generate same key
  - Collision-resistant: SHA256 provides strong uniqueness
  - Readable: Human-inspectable for debugging
  - Compact: ~60 characters total
```

### Cache TTL Strategy

| Cache Level | Default TTL | Use Case | Reasoning |
|-------------|-------------|----------|-----------|
| **L1 (Memory)** | 1 hour | Immediate reuse within session | Balance memory usage vs hit rate |
| **L2 (Redis)** | 24 hours | Cross-session, cross-instance sharing | API results stable for 24h |
| **Image Analysis** | 7 days | Immutable image features | Analysis results don't change |
| **Consistency Data** | 30 days | Character/style references | Long-lived reference data |
| **Error Responses** | 5 minutes | Transient failures | Quick retry without hammering API |

### Eviction Strategies

#### LRU (Least Recently Used)
- **Used for:** L1 cache (default)
- **Logic:** Remove least recently accessed items when full
- **Best for:** Temporal locality (recent items accessed again soon)
- **Implementation:** OrderedDict with `move_to_end()` on access

#### LFU (Least Frequently Used)
- **Used for:** Optional L1 configuration
- **Logic:** Remove least frequently accessed items
- **Best for:** Stable access patterns with "hot" items
- **Implementation:** Track access count per entry

#### TTL (Time-to-Live)
- **Used for:** L2 cache, error responses
- **Logic:** Remove items after expiration timestamp
- **Best for:** Time-sensitive data, API rate limits
- **Implementation:** Timestamp check on access

### Cache Invalidation

```python
# Manual invalidation methods
cache.invalidate(cache_key)                    # Single key
cache.invalidate_pattern("flux:*")             # Pattern match
cache.invalidate_provider("flux")              # All provider entries
cache.invalidate_model("flux", "flux-pro")     # Specific model
cache.clear()                                  # Full cache clear

# Automatic invalidation triggers
- Provider error rate > 50% in 5 minutes
- Provider health check failure
- Schema version upgrade
- Manual admin action
```

### Storage Backends

#### In-Memory Storage (Default)

```python
Implementation: collections.OrderedDict
Capacity: 1000 entries (configurable)
Persistence: None (ephemeral)
Concurrency: threading.RLock
Use Case: Single-instance deployments

Configuration:
  cache = AdapterCache(
      max_size=1000,
      default_ttl=3600,
      strategy=CacheStrategy.LRU
  )
```

#### Redis Storage (Optional)

```python
Implementation: redis-py
Capacity: 10000 entries
Persistence: RDB + AOF
Concurrency: Redis native
Use Case: Multi-instance, distributed deployments

Configuration:
  redis_cache = RedisCache(
      host="localhost",
      port=6379,
      db=0,
      max_size=10000,
      default_ttl=86400
  )
  
  tiered_cache = TieredCache(
      l1_cache=memory_cache,
      l2_cache=redis_cache
  )
```

#### File System Storage (Persistence)

```python
Implementation: Custom file-based cache
Capacity: Unlimited (disk-bound)
Persistence: JSON files
Concurrency: File locking
Use Case: Long-term storage, audit trail

Structure:
  data/
    cache/
      flux/
        {cache_key}.json
      veo/
        {cache_key}.json
```

---

## Multi-Model Routing & Fallback Logic

### Routing Strategies

#### 1. Priority-Based Routing

```python
strategy = RoutingStrategy.PRIORITY

# Configuration
router.register_provider("flux", flux_adapter, priority=10)
router.register_provider("veo", veo_adapter, priority=8)
router.register_provider("runway", runway_adapter, priority=5)

# Behavior: Always tries highest priority first
# Use Case: Preferred provider with fallback chain
# Flow: flux → veo → runway → fail
```

#### 2. Round-Robin Routing

```python
strategy = RoutingStrategy.ROUND_ROBIN

# Behavior: Cycles through providers sequentially
# Use Case: Even load distribution across providers
# Flow: Request 1 → flux, Request 2 → veo, Request 3 → runway, repeat
```

#### 3. Weighted Routing

```python
strategy = RoutingStrategy.WEIGHTED

# Configuration
router.register_provider("flux", flux_adapter, weight=5.0)   # 50% traffic
router.register_provider("veo", veo_adapter, weight=3.0)     # 30% traffic
router.register_provider("runway", runway_adapter, weight=2.0) # 20% traffic

# Behavior: Probabilistic selection based on weights
# Use Case: Gradual rollout, A/B testing, cost optimization
```

#### 4. Least-Loaded Routing

```python
strategy = RoutingStrategy.LEAST_LOADED

# Behavior: Routes to provider with fewest concurrent requests
# Use Case: Dynamic load balancing, avoiding bottlenecks
# Metric: current_concurrent count per provider
```

#### 5. Latency-Based Routing

```python
strategy = RoutingStrategy.LATENCY_BASED

# Behavior: Routes to provider with lowest average latency
# Use Case: Performance optimization, SLA requirements
# Metric: Rolling average of last 100 requests per provider
```

### Fallback Logic

```
┌─────────────────────────────────────────────────────────┐
│             Fallback Decision Tree                      │
└─────────────────────────────────────────────────────────┘

Request received
    │
    ├─> Check cache
    │   ├─> HIT: Return cached response ✓
    │   └─> MISS: Continue to routing
    │
    ├─> Select primary provider (based on strategy)
    │   │
    │   ├─> Check circuit breaker
    │   │   ├─> OPEN: Skip to next provider
    │   │   └─> CLOSED: Continue
    │   │
    │   ├─> Execute request (with retry)
    │   │   │
    │   │   ├─> Attempt 1
    │   │   │   ├─> SUCCESS: Cache & return ✓
    │   │   │   └─> FAIL (retryable): Retry
    │   │   │
    │   │   ├─> Attempt 2 (after 1s delay)
    │   │   │   ├─> SUCCESS: Cache & return ✓
    │   │   │   └─> FAIL (retryable): Retry
    │   │   │
    │   │   ├─> Attempt 3 (after 2s delay)
    │   │   │   ├─> SUCCESS: Cache & return ✓
    │   │   │   └─> FAIL: Mark as failed
    │   │   │
    │   │   └─> All retries exhausted
    │   │       ├─> Error is retryable: Try next provider
    │   │       └─> Error is non-retryable: Return error ✗
    │   │
    │   └─> Record failure
    │       ├─> Increment failure count
    │       └─> If count ≥ threshold: Open circuit breaker
    │
    ├─> Fallback to next provider (if enabled)
    │   └─> Repeat above flow
    │
    └─> All providers failed
        └─> Return aggregated error ✗
```

### Circuit Breaker Pattern

```python
Circuit Breaker States:
  - CLOSED: Normal operation, requests flow through
  - OPEN: Provider failed, requests skip to next provider
  - HALF-OPEN: Testing if provider recovered (not implemented yet)

Configuration:
  circuit_breaker_threshold = 5        # Failures before opening
  circuit_breaker_timeout = 60         # Seconds before retry

Behavior:
  1. Provider succeeds → failure_count = 0
  2. Provider fails → failure_count++
  3. failure_count ≥ threshold → circuit_open = True
  4. time.time() - last_failure_time > timeout → circuit_open = False

Benefits:
  - Prevents cascading failures
  - Fast-fail for degraded providers
  - Automatic recovery after timeout
```

### Retry Policy

```python
Exponential Backoff Configuration:
  max_retries = 3
  retry_delay = 1.0  # Base delay in seconds
  
Delay Calculation:
  attempt 1: delay = 1.0 * 2^0 = 1.0 second
  attempt 2: delay = 1.0 * 2^1 = 2.0 seconds
  attempt 3: delay = 1.0 * 2^2 = 4.0 seconds

Retryable Conditions:
  - Network timeouts
  - HTTP 5xx errors (500, 502, 503)
  - Rate limit errors (429)
  - Temporary provider unavailability

Non-Retryable Conditions:
  - Authentication failures (401, 403)
  - Invalid request format (400)
  - Content policy violations
  - Insufficient credits
```

### Provider Selection Algorithm

```python
def _select_providers(self, request: UnifiedRequest) -> List[str]:
    """
    Select ordered list of providers to try
    
    Returns:
        List of provider names in priority order
    """
    
    # Filter available providers
    available = [
        name for name, config in self.providers.items()
        if config.enabled and not config.circuit_open
    ]
    
    # Check if request specifies provider
    if request.provider in available:
        # Prioritize requested provider, but include fallbacks
        primary = request.provider
        fallbacks = [p for p in available if p != primary]
        return [primary] + fallbacks
    
    # Apply routing strategy
    if strategy == PRIORITY:
        return sorted(available, key=lambda p: providers[p].priority, reverse=True)
    elif strategy == ROUND_ROBIN:
        # Rotate and return
        ...
    elif strategy == WEIGHTED:
        # Weighted random selection
        ...
    elif strategy == LEAST_LOADED:
        return sorted(available, key=lambda p: providers[p].current_concurrent)
    elif strategy == LATENCY_BASED:
        return sorted(available, key=lambda p: avg_latency[p])
```

---

## Versioning Strategy

### Schema Versioning

#### Current Versions

- **v1.0** - Initial unified schema (legacy)
- **v1.1** - Added retry_config, improved error handling
- **v2.0** - Current version, full feature set

#### Version Migration Flow

```
┌────────────────────────────────────────────────────┐
│          Request Version Detection                 │
├────────────────────────────────────────────────────┤
│                                                     │
│  Incoming Request                                  │
│       │                                             │
│       ├─> Parse "schema_version" field             │
│       │                                             │
│       ├─> v1.0 detected                            │
│       │   └─> Migrate v1.0 → v1.1 → v2.0          │
│       │                                             │
│       ├─> v1.1 detected                            │
│       │   └─> Migrate v1.1 → v2.0                  │
│       │                                             │
│       └─> v2.0 detected                            │
│           └─> No migration needed                  │
│                                                     │
│  Unified Processing (always v2.0 internally)       │
│                                                     │
│  Response Generation                               │
│       │                                             │
│       └─> Return response in same version as       │
│           request (backward compatibility)         │
│                                                     │
└────────────────────────────────────────────────────┘
```

#### Migration Transformations

**v1.0 → v1.1:**

```python
# Additions
- Add "metadata" field (empty dict if missing)
- Add "retry_config" with defaults:
    {
        "max_retries": 3,
        "retry_delay": 1.0
    }
- Transform single "output_url" → "urls" array in result

# Backward Compatible: Yes
```

**v1.1 → v2.0:**

```python
# Additions
- Transform "provider" string → "provider_info" object:
    {
        "name": provider,
        "version": "unknown",
        "region": "unknown"
    }
- Enhance "error" object with correlation_id
- Add "generation_config" from parameters:
    {
        "quality": params.get("quality", "standard"),
        "safety_settings": params.get("safety_settings", {}),
        "advanced_options": {...}
    }

# Backward Compatible: No (breaking changes)
```

### Prompt Versioning

```python
class PromptVersion(str, Enum):
    V1_0 = "1.0"  # Basic prompts
    V1_1 = "1.1"  # Added cinematic language
    V2_0 = "2.0"  # Full GPT-4 expansion with control maps

Prompt Template Structure:
  {
      "version": "2.0",
      "base_prompt": str,
      "expanded_prompt": str,
      "model_specific_prompts": {
          "flux": str,
          "veo": str,
          "runway": str
      },
      "control_maps": Dict,
      "metadata": {
          "expansion_timestamp": str,
          "tokens_used": int,
          "model": "gpt-4-turbo"
      }
  }
```

### Model Version Tracking

```python
Provider Model Versioning:
  flux:
    - flux-pro-1.1 (current)
    - flux-pro-1.0 (deprecated)
    - flux-dev (beta)
  
  veo:
    - veo-2 (current)
    - veo-1 (supported)
  
  runway:
    - gen-3-alpha (current)
    - gen-2 (supported)
  
  sora:
    - sora-1.0 (current)
  
  pika:
    - pika-1.5 (current)
    - pika-1.0 (deprecated)

Version Selection Strategy:
  1. Client specifies exact version → Use specified
  2. Client specifies provider only → Use current/recommended version
  3. Version not available → Fallback to latest supported
  4. Log version used in response metadata
```

### API Versioning

```
URL Structure:
  https://api.animatize.dev/v2/analyze
  https://api.animatize.dev/v2/generate
  https://api.animatize.dev/v1/analyze  (legacy, maintained)

Version Negotiation:
  1. URL path version (preferred): /v2/analyze
  2. Header version: X-API-Version: 2.0
  3. Query parameter: ?api_version=2.0
  4. Default: v2 (latest stable)

Deprecation Policy:
  - v1 supported until 2026-01-01
  - 6 months warning before deprecation
  - Migration guide provided
  - Automatic request logging for deprecated versions
```

---

## Observability & Logging

### Logging Architecture

```
┌────────────────────────────────────────────────────┐
│           Logging Hierarchy & Levels               │
├────────────────────────────────────────────────────┤
│                                                     │
│  Application Root Logger                           │
│  Level: INFO (production) / DEBUG (development)    │
│       │                                             │
│       ├─> animatize.adapters                       │
│       │   ├─> animatize.adapters.router           │
│       │   │   Level: INFO                          │
│       │   │   Events: routing decisions, fallbacks │
│       │   │                                         │
│       │   ├─> animatize.adapters.cache             │
│       │   │   Level: INFO                          │
│       │   │   Events: hit/miss, evictions          │
│       │   │                                         │
│       │   └─> animatize.adapters.{provider}        │
│       │       Level: INFO                          │
│       │       Events: API calls, errors            │
│       │                                             │
│       ├─> animatize.analyzers                      │
│       │   Level: INFO                              │
│       │   Events: image analysis, predictions      │
│       │                                             │
│       ├─> animatize.generators                     │
│       │   Level: INFO                              │
│       │   Events: prompt expansion, GPT calls      │
│       │                                             │
│       └─> animatize.consistency                    │
│           Level: INFO                              │
│           Events: validation, consistency checks   │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Log Levels & Use Cases

| Level | Use Case | Examples |
|-------|----------|----------|
| **DEBUG** | Development, troubleshooting | Request/response payloads, parameter dumps, detailed flow |
| **INFO** | Normal operations | Request started, cache hit, provider selected, request completed |
| **WARNING** | Degraded performance, fallbacks | Circuit breaker opened, retry attempted, cache full |
| **ERROR** | Failures, exceptions | API errors, validation failures, unhandled exceptions |
| **CRITICAL** | System failures | All providers down, database unavailable, OOM |

### Structured Logging Format

```python
# JSON structured logs for production
{
    "timestamp": "2025-01-28T10:15:30.123Z",
    "level": "INFO",
    "logger": "animatize.adapters.router",
    "message": "Request routed to provider",
    "context": {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "provider": "flux",
        "model": "flux-pro-1.1",
        "strategy": "priority",
        "cache_hit": false,
        "latency_ms": 2347.5
    },
    "trace_id": "abc123",    # Distributed tracing
    "span_id": "def456",
    "user_id": "user_789",   # If authenticated
    "environment": "production"
}
```

### Key Logging Hooks

#### Pre-Request Hooks

```python
# Before any processing
logger.info(
    "Request received",
    extra={
        "request_id": request.request_id,
        "provider": request.provider,
        "model": request.model,
        "media_type": request.media_type,
        "prompt_length": len(request.prompt),
        "parameters": request.parameters
    }
)
```

#### Cache Operations

```python
# Cache hit
logger.info(
    "Cache hit",
    extra={
        "request_id": request.request_id,
        "cache_key": cache_key,
        "cache_level": "L1",
        "age_seconds": time.time() - entry.timestamp
    }
)

# Cache miss
logger.info(
    "Cache miss",
    extra={
        "request_id": request.request_id,
        "cache_key": cache_key,
        "reason": "not_found"  # or "expired"
    }
)
```

#### Provider Selection

```python
logger.info(
    "Provider selected",
    extra={
        "request_id": request.request_id,
        "provider": selected_provider,
        "strategy": self.strategy,
        "available_providers": available_providers,
        "circuit_breaker_states": {...}
    }
)
```

#### API Calls

```python
# Before API call
logger.debug(
    "Making API call",
    extra={
        "request_id": request.request_id,
        "provider": provider_name,
        "endpoint": api_url,
        "timeout": timeout,
        "payload": transformed_request  # DEBUG only
    }
)

# After API call
logger.info(
    "API call completed",
    extra={
        "request_id": request.request_id,
        "provider": provider_name,
        "status": "success",
        "latency_ms": processing_time_ms,
        "tokens_used": tokens,
        "cost_usd": cost
    }
)
```

#### Errors & Failures

```python
logger.error(
    "Provider API call failed",
    extra={
        "request_id": request.request_id,
        "provider": provider_name,
        "error_code": error.code,
        "error_message": error.message,
        "retryable": error.retryable,
        "attempt": attempt_number,
        "will_retry": will_retry
    },
    exc_info=True  # Include stack trace
)
```

#### Retry & Fallback

```python
logger.warning(
    "Retrying request",
    extra={
        "request_id": request.request_id,
        "provider": provider_name,
        "attempt": attempt_number,
        "max_retries": max_retries,
        "delay_seconds": retry_delay
    }
)

logger.warning(
    "Falling back to alternate provider",
    extra={
        "request_id": request.request_id,
        "failed_provider": failed_provider,
        "fallback_provider": next_provider,
        "reason": "circuit_breaker_open"  # or "all_retries_exhausted"
    }
)
```

#### Circuit Breaker

```python
logger.warning(
    "Circuit breaker opened",
    extra={
        "provider": provider_name,
        "failure_count": config.failure_count,
        "threshold": circuit_breaker_threshold,
        "timeout_seconds": circuit_breaker_timeout
    }
)

logger.info(
    "Circuit breaker closed",
    extra={
        "provider": provider_name,
        "downtime_seconds": time.time() - config.last_failure_time
    }
)
```

### Metrics & Monitoring

#### Key Metrics to Track

```python
# Request Metrics
- Total requests: Counter
- Requests per provider: Counter (labeled by provider)
- Request latency: Histogram (labeled by provider)
- Request status: Counter (labeled by status: success/failed/timeout)

# Cache Metrics
- Cache hit rate: Gauge (hits / total requests)
- Cache size: Gauge (entries count)
- Cache evictions: Counter
- Cache expired: Counter

# Provider Metrics
- Provider success rate: Gauge (per provider)
- Provider average latency: Gauge (per provider)
- Provider concurrent requests: Gauge (per provider)
- Provider circuit breaker state: Gauge (0=closed, 1=open)
- Provider failure count: Counter (per provider)

# Cost Metrics
- Total cost: Counter (USD)
- Cost per provider: Counter (labeled by provider)
- Tokens used: Counter (labeled by provider)

# Business Metrics
- Images analyzed: Counter
- Videos generated: Counter
- Active users: Gauge
- API calls per user: Counter (labeled by user_id)
```

#### Metrics Instrumentation Points

```python
# In router.execute()
metrics.counter("requests.total").inc()
metrics.counter(f"requests.provider.{provider}").inc()

with metrics.histogram("request.latency").time():
    response = adapter.execute(request)

if response.is_success():
    metrics.counter("requests.success").inc()
    metrics.counter(f"costs.total").inc(response.cost or 0)
else:
    metrics.counter("requests.failed").inc()

# In cache operations
if cache_hit:
    metrics.counter("cache.hits").inc()
else:
    metrics.counter("cache.misses").inc()

# In circuit breaker
if config.circuit_open:
    metrics.gauge(f"circuit_breaker.{provider}").set(1)
else:
    metrics.gauge(f"circuit_breaker.{provider}").set(0)
```

### Alerting Rules

```yaml
# High error rate
alert: HighErrorRate
expr: rate(requests.failed[5m]) > 0.1  # 10% error rate
severity: warning
annotations:
  description: "Error rate {{ $value }}% in last 5 minutes"

# Circuit breaker open
alert: CircuitBreakerOpen
expr: circuit_breaker{provider="flux"} == 1
severity: critical
annotations:
  description: "Circuit breaker open for provider {{ $labels.provider }}"

# Low cache hit rate
alert: LowCacheHitRate
expr: cache.hit_rate < 0.5  # 50%
severity: warning
annotations:
  description: "Cache hit rate dropped to {{ $value }}%"

# High latency
alert: HighLatency
expr: histogram_quantile(0.95, request.latency) > 10000  # 10 seconds
severity: warning
annotations:
  description: "P95 latency {{ $value }}ms"
```

---

## Deployment Considerations

### API Rate Limits

#### Provider-Specific Limits

| Provider | Rate Limit | Burst | Cooldown | Notes |
|----------|------------|-------|----------|-------|
| **Flux** | 60 req/min | 10 | None | Per API key |
| **VEO** | 30 req/min | 5 | 1 min | Per project |
| **Runway** | 100 req/hour | 20 | None | Tiered by plan |
| **Sora** | 50 req/min | None | None | Per account |
| **Pika** | 120 req/min | 15 | None | Per API key |
| **OpenAI** | 3500 req/min | 500 | None | GPT-4 Turbo |

#### Rate Limit Handling

```python
Rate Limit Strategy:
  1. Respect provider-reported rate limits
  2. Implement token bucket algorithm
  3. Queue requests when approaching limit
  4. Return HTTP 429 with Retry-After header
  5. Automatic throttling & backoff

Configuration:
  rate_limiter = RateLimiter(
      provider="flux",
      rate=60,           # requests per minute
      burst=10,          # burst allowance
      window=60          # window in seconds
  )

Response Headers:
  X-RateLimit-Limit: 60
  X-RateLimit-Remaining: 23
  X-RateLimit-Reset: 1706443200
  Retry-After: 45  (if rate limited)
```

### Batching Strategy

```python
Batch Processing Configuration:
  
  # Provider support
  flux:
      supports_batch: True
      max_batch_size: 4
      batch_timeout: 30s
  
  veo:
      supports_batch: False
  
  runway:
      supports_batch: True
      max_batch_size: 10
      batch_timeout: 60s

Batching Logic:
  1. Collect requests for same provider+model
  2. Wait up to batch_timeout for batch_size requests
  3. Submit as single batch API call
  4. Distribute responses to individual requests

Benefits:
  - Reduced API calls (cost savings)
  - Better rate limit utilization
  - Improved throughput

Trade-offs:
  - Increased latency for early requests in batch
  - Complexity in error handling
  - Not suitable for real-time applications
```

### Cost Optimization

#### Provider Cost Comparison (Estimated)

| Provider | Cost per Image | Cost per Video (10s) | Model |
|----------|----------------|----------------------|-------|
| **Flux** | $0.04 | $0.10 | flux-pro-1.1 |
| **VEO** | $0.06 | $0.15 | veo-2 |
| **Runway** | $0.05 | $0.12 | gen-3-alpha |
| **Sora** | $0.08 | $0.20 | sora-1.0 |
| **Pika** | $0.03 | $0.08 | pika-1.5 |
| **OpenAI** | $0.01 / 1K tokens | N/A | gpt-4-turbo |

#### Cost Optimization Strategies

```python
1. Aggressive Caching
   - Cache hit rate: 80% target
   - Cost savings: ~80% on repeated prompts
   - ROI: High

2. Weighted Routing by Cost
   - Route 60% to Pika (cheapest)
   - Route 30% to Flux (balance)
   - Route 10% to Sora (quality)
   - Cost savings: ~40%
   - ROI: Medium

3. Resolution Optimization
   - Default to 1024x1024 (not 2048x2048)
   - Cost savings: ~50%
   - ROI: High

4. Batch Processing
   - Combine compatible requests
   - Cost savings: ~30%
   - ROI: Medium

5. Off-Peak Pricing
   - Schedule batch jobs during off-peak hours
   - Cost savings: ~20% (provider-dependent)
   - ROI: Low (requires scheduling infrastructure)

Estimated Total Savings: 70-85% with aggressive optimization
```

### Deployment Architectures

#### Single Instance (Development/Small Scale)

```
┌─────────────────────────────────┐
│     Single Server               │
│                                  │
│  ┌────────────────────────────┐ │
│  │  ANIMAtiZE App             │ │
│  │  - In-memory cache (L1)    │ │
│  │  - All adapters             │ │
│  │  - Sqlite DB (optional)    │ │
│  └────────────────────────────┘ │
│                                  │
│  Pros:                           │
│  - Simple deployment             │
│  - Low cost ($50/mo)             │
│  - Easy debugging                │
│                                  │
│  Cons:                           │
│  - No high availability          │
│  - Limited scalability           │
│  - Cache not shared              │
│                                  │
│  Use Case: <100 req/day          │
└─────────────────────────────────┘
```

#### Multi-Instance with Shared Cache (Production)

```
                 ┌──────────────┐
                 │ Load Balancer│
                 └───────┬──────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
    │Instance1│     │Instance2│     │Instance3│
    │- L1 cache│     │- L1 cache│     │- L1 cache│
    └────┬────┘     └────┬────┘     └────┬────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                    ┌────▼────┐
                    │  Redis  │
                    │L2 Cache │
                    └─────────┘
                         │
                    ┌────▼────┐
                    │PostgreSQL│
                    │Metrics DB│
                    └─────────┘

Pros:
  - High availability (99.9% uptime)
  - Horizontal scalability
  - Shared cache across instances
  - Load balancing

Cons:
  - Higher complexity
  - Higher cost ($300+/mo)
  - Network latency to Redis

Use Case: >1000 req/day, production SLA
```

#### Serverless (Cloud Functions)

```
┌─────────────────────────────────────────┐
│         API Gateway                     │
└───────────────┬─────────────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│Lambda1│  │Lambda2│  │Lambda3│
│Analyze│  │Generate│ │Callback│
└───┬───┘  └───┬───┘  └───┬───┘
    │          │          │
    └──────────┼──────────┘
               │
        ┌──────▼──────┐
        │   Redis     │
        │ElastiCache  │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │  DynamoDB   │
        │  Metrics    │
        └─────────────┘

Pros:
  - Auto-scaling (0 to 1000s)
  - Pay per use
  - Zero maintenance
  - High availability

Cons:
  - Cold start latency
  - Limited execution time (15 min)
  - Stateless (requires external cache)

Use Case: Variable load, cost-sensitive
```

### Environment Configuration

```python
# Development
ENV = "development"
LOG_LEVEL = "DEBUG"
CACHE_ENABLED = True
CACHE_SIZE = 100
CACHE_TTL = 600  # 10 minutes
ENABLE_RETRY = True
MAX_RETRIES = 1
CIRCUIT_BREAKER_ENABLED = False

# Staging
ENV = "staging"
LOG_LEVEL = "INFO"
CACHE_ENABLED = True
CACHE_SIZE = 500
CACHE_TTL = 1800  # 30 minutes
ENABLE_RETRY = True
MAX_RETRIES = 2
CIRCUIT_BREAKER_ENABLED = True
CIRCUIT_BREAKER_THRESHOLD = 3

# Production
ENV = "production"
LOG_LEVEL = "INFO"
CACHE_ENABLED = True
CACHE_SIZE = 1000
CACHE_TTL = 3600  # 1 hour
REDIS_ENABLED = True
REDIS_HOST = "redis.production.internal"
ENABLE_RETRY = True
MAX_RETRIES = 3
CIRCUIT_BREAKER_ENABLED = True
CIRCUIT_BREAKER_THRESHOLD = 5
ENABLE_METRICS = True
METRICS_BACKEND = "prometheus"
```

---

## Error Handling & Retry Policies

### Error Classification

```python
class ErrorCode(str, Enum):
    # Client Errors (4xx) - Non-Retryable
    INVALID_REQUEST = "invalid_request"              # 400
    AUTHENTICATION_FAILED = "authentication_failed"  # 401
    INSUFFICIENT_CREDITS = "insufficient_credits"    # 402
    CONTENT_POLICY_VIOLATION = "content_policy"      # 403
    INVALID_MODEL = "invalid_model"                  # 404
    
    # Rate Limiting (429) - Retryable with delay
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"      # 429
    
    # Server Errors (5xx) - Retryable
    PROVIDER_ERROR = "provider_error"                # 500
    TIMEOUT = "timeout"                              # 504
    NETWORK_ERROR = "network_error"                  # 503
    
    # Unknown
    UNKNOWN_ERROR = "unknown_error"                  # 500

Error Response Structure:
{
    "code": ErrorCode,
    "message": str,             # Human-readable error message
    "retryable": bool,          # Can this error be retried?
    "provider": str,            # Provider that generated error
    "details": Dict[str, Any],  # Additional error context
    "timestamp": str,           # ISO 8601 timestamp
    "retry_after": Optional[int],  # Seconds to wait (for rate limits)
    "correlation_id": str       # Request ID for tracking
}
```

### Retry Decision Matrix

| Error Code | Retryable | Max Retries | Backoff Strategy | Notes |
|------------|-----------|-------------|------------------|-------|
| **INVALID_REQUEST** | ❌ No | 0 | N/A | Client must fix request |
| **AUTHENTICATION_FAILED** | ❌ No | 0 | N/A | Invalid API key |
| **INSUFFICIENT_CREDITS** | ❌ No | 0 | N/A | Billing issue |
| **CONTENT_POLICY_VIOLATION** | ❌ No | 0 | N/A | Content filter triggered |
| **INVALID_MODEL** | ❌ No | 0 | N/A | Model not supported |
| **RATE_LIMIT_EXCEEDED** | ✅ Yes | 3 | Exponential + Jitter | Wait for retry_after |
| **PROVIDER_ERROR** | ✅ Yes | 3 | Exponential | 5xx server errors |
| **TIMEOUT** | ✅ Yes | 2 | Exponential | Network timeout |
| **NETWORK_ERROR** | ✅ Yes | 3 | Exponential | Connection issues |
| **UNKNOWN_ERROR** | ⚠️ Maybe | 1 | Linear | Case-by-case |

### Retry Algorithms

#### Exponential Backoff

```python
def calculate_retry_delay(attempt: int, base_delay: float = 1.0) -> float:
    """
    Calculate retry delay with exponential backoff
    
    Formula: delay = base_delay * (2 ^ attempt)
    
    Args:
        attempt: Retry attempt number (0-indexed)
        base_delay: Base delay in seconds
        
    Returns:
        Delay in seconds
    """
    return base_delay * (2 ** attempt)

Examples:
  Attempt 0: 1.0 * 2^0 = 1.0 second
  Attempt 1: 1.0 * 2^1 = 2.0 seconds
  Attempt 2: 1.0 * 2^2 = 4.0 seconds
  Attempt 3: 1.0 * 2^3 = 8.0 seconds
```

#### Exponential Backoff with Jitter

```python
import random

def calculate_retry_delay_jittered(
    attempt: int,
    base_delay: float = 1.0,
    jitter: float = 0.3
) -> float:
    """
    Calculate retry delay with exponential backoff and jitter
    
    Jitter prevents thundering herd problem when multiple
    requests fail simultaneously
    
    Formula: delay = base_delay * (2 ^ attempt) * (1 ± jitter)
    
    Args:
        attempt: Retry attempt number
        base_delay: Base delay in seconds
        jitter: Jitter factor (0.0-1.0)
        
    Returns:
        Delay in seconds with random jitter
    """
    base = base_delay * (2 ** attempt)
    jitter_amount = base * jitter
    return base + random.uniform(-jitter_amount, jitter_amount)

Examples (jitter=0.3):
  Attempt 0: 1.0 ± 0.3 = 0.7-1.3 seconds
  Attempt 1: 2.0 ± 0.6 = 1.4-2.6 seconds
  Attempt 2: 4.0 ± 1.2 = 2.8-5.2 seconds
```

#### Rate Limit Aware Retry

```python
def calculate_rate_limit_delay(error: ErrorDetails) -> float:
    """
    Calculate retry delay for rate limit errors
    
    Respects provider's retry_after header
    
    Args:
        error: Error details with retry_after
        
    Returns:
        Delay in seconds
    """
    if error.retry_after:
        # Use provider's suggested delay
        return error.retry_after
    else:
        # Default exponential backoff for rate limits
        return 60.0  # Wait 1 minute

Example Response:
  HTTP 429 Too Many Requests
  Retry-After: 45
  → Wait 45 seconds before retry
```

### Error Handling Flow

```python
def execute_with_retry(
    request: UnifiedRequest,
    adapter: BaseModelAdapter
) -> UnifiedResponse:
    """
    Execute request with intelligent retry logic
    """
    attempt = 0
    last_error = None
    
    while attempt < MAX_RETRIES:
        try:
            # Execute request
            response = adapter.execute(request)
            
            # Check if successful
            if response.is_success():
                return response
            
            # Check if retryable
            if not response.is_retryable():
                logger.warning(f"Non-retryable error: {response.error.code}")
                return response
            
            # Calculate retry delay
            if response.error.code == ErrorCode.RATE_LIMIT_EXCEEDED:
                delay = calculate_rate_limit_delay(response.error)
            else:
                delay = calculate_retry_delay_jittered(attempt)
            
            # Log retry
            logger.info(
                f"Retrying request after {delay}s "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )
            
            # Wait before retry
            time.sleep(delay)
            attempt += 1
            last_error = response.error
            
        except Exception as e:
            logger.exception("Unexpected error during execution")
            last_error = ErrorDetails(
                code=ErrorCode.UNKNOWN_ERROR,
                message=str(e),
                retryable=False,
                provider=adapter.provider_name
            )
            break
    
    # All retries exhausted
    return UnifiedResponse(
        schema_version=request.schema_version,
        request_id=request.request_id,
        provider=adapter.provider_name,
        model=request.model,
        status="failed",
        error=last_error
    )
```

### Error Recovery Strategies

#### 1. Graceful Degradation

```python
Strategy: Fallback to simpler operation when complex operation fails

Example:
  1. Try: High-res video generation (2048x2048, 30s)
  2. Fallback: Lower-res video (1024x1024, 10s)
  3. Fallback: Static image generation
  4. Fail: Return error

Implementation:
  def generate_with_degradation(request: UnifiedRequest) -> UnifiedResponse:
      # Try full quality
      response = router.execute(request)
      if response.is_success():
          return response
      
      # Fallback to lower quality
      request.parameters["width"] = 1024
      request.parameters["height"] = 1024
      response = router.execute(request)
      if response.is_success():
          response.metadata["degraded"] = True
          return response
      
      # Final fallback
      return generate_static_image(request)
```

#### 2. Partial Success Handling

```python
Strategy: Return partial results instead of full failure

Example: Batch request with 10 images
  - 8 succeed
  - 2 fail
  → Return 8 results + errors for 2

Implementation:
  {
      "status": "partial_success",
      "results": [
          {"index": 0, "status": "success", "url": "..."},
          {"index": 1, "status": "success", "url": "..."},
          ...
          {"index": 8, "status": "failed", "error": {...}},
          {"index": 9, "status": "failed", "error": {...}}
      ],
      "summary": {
          "total": 10,
          "succeeded": 8,
          "failed": 2,
          "success_rate": 0.8
      }
  }
```

#### 3. Async Retry with Callbacks

```python
Strategy: For long-running operations, retry asynchronously

Flow:
  1. Client submits request with callback_url
  2. Server returns 202 Accepted immediately
  3. Server retries in background
  4. Server calls callback_url when complete

Implementation:
  # Initial request
  POST /generate
  {
      "prompt": "...",
      "callback_url": "https://client.com/webhook"
  }
  
  # Immediate response
  202 Accepted
  {
      "request_id": "...",
      "status": "processing",
      "estimated_time": "30s"
  }
  
  # Background processing with retries
  # ...
  
  # Webhook callback on completion
  POST https://client.com/webhook
  {
      "request_id": "...",
      "status": "success",
      "result": {...}
  }
```

---

## Security Considerations

### API Key Management

```python
Security Best Practices:
  1. Never hardcode API keys in code
  2. Store in environment variables or secrets manager
  3. Rotate keys regularly (quarterly)
  4. Use separate keys for dev/staging/prod
  5. Monitor key usage for anomalies
  6. Revoke compromised keys immediately

Configuration:
  # .env file (never commit to git)
  FLUX_API_KEY=sk-flux-...
  VEO_API_KEY=veo_...
  RUNWAY_API_KEY=rwy_...
  OPENAI_API_KEY=sk-...
  
  # In code
  flux_key = os.getenv("FLUX_API_KEY")
  if not flux_key:
      raise ValueError("FLUX_API_KEY not set")

Secrets Management:
  - Development: .env files (git-ignored)
  - Staging/Production: AWS Secrets Manager, HashiCorp Vault
  - CI/CD: GitHub Secrets, GitLab Variables
```

### Input Validation

```python
Validation Rules:
  1. Prompt length: Max 2000 characters
  2. Image size: Max 10MB
  3. Image format: PNG, JPEG, WebP only
  4. Parameters: Whitelist known parameters
  5. Model: Validate against supported models
  6. Schema version: Validate against known versions

Implementation:
  def validate_request(request: UnifiedRequest) -> Optional[ErrorDetails]:
      # Prompt validation
      if len(request.prompt) > 2000:
          return ErrorDetails(
              code=ErrorCode.INVALID_REQUEST,
              message="Prompt exceeds 2000 characters",
              retryable=False,
              provider="validator"
          )
      
      # Model validation
      if request.model not in SUPPORTED_MODELS:
          return ErrorDetails(
              code=ErrorCode.INVALID_MODEL,
              message=f"Model '{request.model}' not supported",
              retryable=False,
              provider="validator"
          )
      
      # Parameter validation (whitelist)
      allowed_params = {"width", "height", "steps", "guidance_scale"}
      invalid_params = set(request.parameters.keys()) - allowed_params
      if invalid_params:
          return ErrorDetails(
              code=ErrorCode.INVALID_REQUEST,
              message=f"Invalid parameters: {invalid_params}",
              retryable=False,
              provider="validator"
          )
      
      return None  # Valid
```

### Content Safety

```python
Content Policy Enforcement:
  1. OpenAI Moderation API for prompt screening
  2. Provider-specific safety filters
  3. Logging of policy violations
  4. Rate limiting for violating users

Implementation:
  def check_content_safety(prompt: str) -> bool:
      """
      Check prompt against content policy
      
      Returns:
          True if safe, False if policy violation
      """
      # Use OpenAI Moderation API
      response = openai.Moderations.create(input=prompt)
      result = response.results[0]
      
      if result.flagged:
          logger.warning(
              "Content policy violation",
              extra={
                  "categories": result.categories,
                  "scores": result.category_scores
              }
          )
          return False
      
      return True

Violation Response:
  {
      "status": "failed",
      "error": {
          "code": "content_policy_violation",
          "message": "Prompt violates content policy",
          "retryable": False,
          "details": {
              "categories": ["violence", "hate"],
              "action": "Modify prompt and resubmit"
          }
      }
  }
```

### Rate Limiting & DDoS Protection

```python
Multi-Layer Rate Limiting:
  
  1. Per-User Rate Limit
     - 100 requests per minute per user
     - 1000 requests per hour per user
     
  2. Per-IP Rate Limit
     - 200 requests per minute per IP
     - Prevents abuse from single source
  
  3. Global Rate Limit
     - 10,000 requests per minute globally
     - Protects infrastructure
  
  4. Provider Rate Limits
     - Respect individual provider limits
     - See "API Rate Limits" section

Implementation:
  from ratelimit import limits, sleep_and_retry
  
  @sleep_and_retry
  @limits(calls=100, period=60)  # 100 per minute
  def handle_request(user_id: str, request: UnifiedRequest):
      ...

DDoS Protection:
  - Cloudflare / AWS Shield for network layer
  - Application-level rate limiting
  - CAPTCHA for suspicious traffic
  - IP blacklisting for repeat offenders
```

### Data Privacy

```python
Privacy Principles:
  1. Minimize data collection (only what's needed)
  2. Encrypt data in transit (TLS 1.3)
  3. Encrypt data at rest (AES-256)
  4. No permanent storage of user images (optional)
  5. Anonymize logs (remove PII)
  6. GDPR compliance (right to deletion)

Data Retention Policy:
  - Request logs: 30 days
  - Cache entries: 24 hours
  - Analytics: 90 days (anonymized)
  - Backups: 7 days
  - User data: Deleted on account closure

PII Handling:
  - Never log full prompts (only hashes)
  - Redact email addresses in logs
  - No IP address storage (only country)
  - Pseudonymize user IDs in analytics
```

---

## Appendix

### Glossary

- **Adapter:** Provider-specific implementation of the unified interface
- **Circuit Breaker:** Pattern to prevent cascading failures by stopping requests to failing providers
- **Fallback:** Alternative provider to try when primary fails
- **LRU:** Least Recently Used cache eviction strategy
- **Schema Version:** Version of the unified request/response format
- **Routing Strategy:** Algorithm for selecting which provider to use
- **TTL:** Time-to-Live, duration before cache entry expires
- **Unified Request/Response:** Standardized format across all providers

### Related Documentation

- [Module Contracts](./MODULE_CONTRACTS.md)
- [Adapter Architecture](./ADAPTER_ARCHITECTURE.md)
- [Consistency Engine](./consistency_engine.md)
- [Evaluation System](./EVALUATION_README.md)
- [Product Backlog](./PRODUCT_BACKLOG_README.md)

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-01-28 | Complete architecture documentation |
| 1.1.0 | 2025-01-15 | Added consistency engine |
| 1.0.0 | 2025-01-01 | Initial release |

---

**Document Status:** Production-Ready  
**Maintained By:** ANIMAtiZE Core Team  
**Last Review:** 2025-01-28
