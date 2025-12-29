# ANIMAtiZE Framework - TODO Plan

> **Generated**: Based on comprehensive codebase analysis  
> **Total Estimated Effort**: 50-65 hours (6-8 days)  
> **Target**: Production-Ready Deployment

---

## 📋 Overview

This TODO plan is organized into 4 sprints with prioritized tasks based on:
- **Impact**: How much it improves the system
- **Effort**: Time required to implement
- **Risk**: What happens if not addressed

---

## 🔴 Sprint 1: Critical Fixes (Week 1)
**Priority**: P0 - Must Fix Before Production  
**Effort**: 15-20 hours

### 1.1 Fix Unbounded Cache Memory Leak
- **File**: `src/analyzers/scene_analyzer.py`
- **Line**: 27-29
- **Issue**: `self.analysis_cache = {}` grows indefinitely
- **Risk**: OOM crash in production

**Tasks**:
- [ ] Import `OrderedDict` from collections
- [ ] Add `max_cache_size` parameter (default: 100)
- [ ] Implement LRU eviction when cache exceeds limit
- [ ] Add cache size to `get_cache_stats()` method
- [ ] Write unit test for cache eviction

**Estimated Time**: 2-3 hours

---

### 1.2 Add API Retry Logic to ImageGenerator
- **File**: `src/core/image_generator.py`
- **Line**: 82-117
- **Issue**: No retry on transient API failures
- **Risk**: 5% failure rate, lost API costs

**Tasks**:
- [ ] Install `tenacity` library for retry logic
- [ ] Add `@retry` decorator with exponential backoff
- [ ] Implement API fallback chain (Flux → Imagen → DALL-E)
- [ ] Add retry metrics logging
- [ ] Write integration test for retry behavior

**Estimated Time**: 4-6 hours

---

### 1.3 Add Observability/Telemetry
- **Files**: All core modules
- **Issue**: Zero production monitoring capability
- **Risk**: Cannot debug production issues

**Tasks**:
- [ ] Install OpenTelemetry SDK
- [ ] Create `src/core/telemetry.py` module
- [ ] Add timing metrics to SceneAnalyzer
- [ ] Add timing metrics to MovementPredictor
- [ ] Add timing metrics to PromptExpander
- [ ] Add timing metrics to ImageGenerator
- [ ] Add cache hit/miss counters
- [ ] Add error counters by type
- [ ] Create Prometheus metrics endpoint
- [ ] Write basic Grafana dashboard config

**Estimated Time**: 2-3 days (16-24 hours)

---

## 🟠 Sprint 2: Performance Optimization (Week 2)
**Priority**: P1 - Should Fix  
**Effort**: 20-25 hours

### 2.1 Parallelize CV Analysis in SceneAnalyzer
- **File**: `src/analyzers/scene_analyzer.py`
- **Line**: 79-84
- **Issue**: 4 independent analyses run sequentially
- **Expected Improvement**: 2-3x speedup (50ms → 20ms)

**Tasks**:
- [ ] Import `ThreadPoolExecutor` from concurrent.futures
- [ ] Create async version `analyze_image_async()`
- [ ] Run `_detect_objects_fallback` in parallel
- [ ] Run `_estimate_depth_fallback` in parallel
- [ ] Run `_analyze_composition` in parallel
- [ ] Run `_classify_scene` in parallel
- [ ] Add thread pool configuration to constructor
- [ ] Benchmark before/after performance
- [ ] Update unit tests

**Estimated Time**: 4-6 hours

---

### 2.2 Implement OpenAI Batch API for PromptExpander
- **File**: `src/core/prompt_expander.py`
- **Issue**: Sequential API calls, no batching
- **Expected Improvement**: 50% cost reduction, 2x throughput

**Tasks**:
- [ ] Research OpenAI Batch API documentation
- [ ] Add `expand_prompts_batch()` method
- [ ] Implement batch file creation
- [ ] Add batch status polling
- [ ] Add webhook support for batch completion
- [ ] Update cache strategy for batch results
- [ ] Write integration tests with mock API

**Estimated Time**: 1-2 days (8-16 hours)

---

### 2.3 Add Determinism Controls
- **File**: `src/core/prompt_expander.py`
- **Line**: 251 (ExpansionRequest dataclass)
- **Issue**: GPT temperature=0.7 causes non-reproducible results

**Tasks**:
- [ ] Change default temperature from 0.7 to 0.0
- [ ] Add `seed` parameter to `ExpansionRequest`
- [ ] Pass seed to OpenAI API call
- [ ] Add determinism flag to configuration
- [ ] Document determinism behavior in docstrings
- [ ] Add test for reproducibility

**Estimated Time**: 1-2 hours

---

### 2.4 Implement Semantic Caching for ImageGenerator
- **File**: `src/core/image_generator.py`
- **Issue**: Exact-match cache misses similar prompts
- **Expected Improvement**: 30-50% cache hit increase

**Tasks**:
- [ ] Install sentence-transformers library
- [ ] Add embedding model initialization
- [ ] Create `_check_semantic_cache()` method
- [ ] Store embeddings alongside cached images
- [ ] Add similarity threshold configuration
- [ ] Benchmark cache hit rate improvement
- [ ] Write tests for semantic matching

**Estimated Time**: 1-2 days (8-16 hours)

---

## 🟡 Sprint 3: Robustness & Quality (Week 3)
**Priority**: P2 - Nice to Have  
**Effort**: 15-20 hours

### 3.1 Add Input Validation with Pydantic
- **Files**: All core modules
- **Issue**: No schema validation, cryptic errors

**Tasks**:
- [ ] Create `src/models/requests.py` with Pydantic models
- [ ] Add `ImageAnalysisRequest` model
- [ ] Add `MovementPredictionRequest` model
- [ ] Add `PromptExpansionRequest` model (extend existing)
- [ ] Add `ImageGenerationRequest` model (extend existing)
- [ ] Add file size validation
- [ ] Add image format validation
- [ ] Add path existence validation
- [ ] Integrate validators into each module
- [ ] Write validation error tests

**Estimated Time**: 4-6 hours

---

### 3.2 Fix Filesystem Cache Accumulation
- **File**: `src/core/image_generator.py`
- **Line**: 79-80
- **Issue**: Cache grows indefinitely on disk

**Tasks**:
- [ ] Add `cache_ttl_days` parameter (default: 7)
- [ ] Add `max_cache_size_gb` parameter (default: 10)
- [ ] Create `_cleanup_cache()` method
- [ ] Implement TTL-based eviction
- [ ] Implement size-based eviction (LRU)
- [ ] Add periodic cleanup task (asyncio)
- [ ] Add cache cleanup metrics
- [ ] Write cleanup tests

**Estimated Time**: 3-4 hours

---

### 3.3 Consolidate Caching Strategies
- **Files**: Multiple modules
- **Issue**: 3 different cache implementations

**Tasks**:
- [ ] Create unified `src/core/cache_manager.py`
- [ ] Implement `CacheManager` class with:
  - [ ] In-memory LRU cache
  - [ ] Filesystem cache with TTL
  - [ ] Optional Redis backend
- [ ] Migrate SceneAnalyzer to CacheManager
- [ ] Migrate PromptExpander to CacheManager
- [ ] Migrate ImageGenerator to CacheManager
- [ ] Add unified cache statistics
- [ ] Write comprehensive cache tests

**Estimated Time**: 4-6 hours

---

### 3.4 Remove/Integrate Orphaned MotionDetector
- **File**: `src/analyzers/motion_detector.py`
- **Issue**: Module exists but not used in pipeline

**Tasks**:
- [ ] Evaluate if motion_detector adds value
- [ ] Option A: Integrate into main pipeline for video support
- [ ] Option B: Remove from codebase and document reason
- [ ] Update imports and __init__.py files
- [ ] Update tests accordingly
- [ ] Update documentation

**Estimated Time**: 2-3 hours

---

## 🟢 Sprint 4: Enhancement & Documentation (Week 4)
**Priority**: P3 - Future Improvements  
**Effort**: 10-15 hours

### 4.1 Add Cheaper Model Fallback for PromptExpander
- **File**: `src/core/prompt_expander.py`
- **Issue**: Only uses expensive GPT-4-turbo

**Tasks**:
- [ ] Add `fallback_model` parameter (default: gpt-3.5-turbo)
- [ ] Create model tier selection logic
- [ ] Use fallback for non-critical expansions
- [ ] Add cost estimation per request
- [ ] Track model usage in metrics
- [ ] Document cost optimization

**Estimated Time**: 2-3 hours

---

### 4.2 Improve MovementPredictor Confidence Scoring
- **File**: `src/analyzers/movement_predictor.py`
- **Issue**: Hardcoded confidence scores (0.5-0.8)

**Tasks**:
- [ ] Calculate confidence from CV metrics
- [ ] Factor in edge detection quality
- [ ] Factor in contour clarity
- [ ] Factor in line detection strength
- [ ] Add uncertainty quantification
- [ ] Document confidence calculation

**Estimated Time**: 3-4 hours

---

### 4.3 Create API Documentation
- **Location**: `docs/api/`

**Tasks**:
- [ ] Generate OpenAPI/Swagger spec
- [ ] Document all public methods
- [ ] Add request/response examples
- [ ] Add error code documentation
- [ ] Create Postman collection
- [ ] Add curl examples to README

**Estimated Time**: 3-4 hours

---

### 4.4 Performance Benchmarking Suite
- **Location**: `tests/performance/`

**Tasks**:
- [ ] Create benchmark script for each module
- [ ] Add memory profiling tests
- [ ] Add latency percentile tracking
- [ ] Create CI/CD performance regression check
- [ ] Document baseline metrics
- [ ] Add performance comparison report generator

**Estimated Time**: 2-3 hours

---

## 📊 Summary Table

| Sprint | Focus | Tasks | Effort | Impact |
|--------|-------|-------|--------|--------|
| **Sprint 1** | Critical Fixes | 3 | 15-20 hrs | Prevents crashes, enables monitoring |
| **Sprint 2** | Performance | 4 | 20-25 hrs | 3x faster, 50% cost reduction |
| **Sprint 3** | Robustness | 4 | 15-20 hrs | Better errors, cleaner code |
| **Sprint 4** | Enhancement | 4 | 10-15 hrs | Polish and documentation |
| **Total** | - | **15** | **60-80 hrs** | **Production Ready** |

---

## ✅ Definition of Done

Each task is complete when:
- [ ] Code implemented and passes linting
- [ ] Unit tests written and passing
- [ ] Integration tests updated if needed
- [ ] Documentation updated
- [ ] Code reviewed by peer
- [ ] Merged to main branch

---

## 🎯 Success Metrics

| Metric | Current | Target | Sprint |
|--------|---------|--------|--------|
| Memory Usage | Unbounded | <200MB capped | 1 |
| API Reliability | 95% | 99.9% | 1 |
| Observability | 0% | 100% | 1 |
| Avg Latency | 19.6s | 7.0s | 2 |
| Throughput | 240/hr | 720/hr | 2 |
| Cache Hit Rate | Unknown | 70%+ | 2 |
| Cost per 1000 | $80 | $40 | 2 |
| Test Coverage | ~60% | 90%+ | 3 |
| Production Ready | 60% | 95%+ | 4 |

---

## 📝 Notes

- Priorities may shift based on user feedback
- Sprint 1 is non-negotiable before any production deployment
- Sprint 2 can be parallelized with multiple developers
- Consider feature flags for gradual rollout of changes
- Set up staging environment before Sprint 3

---

**Last Updated**: Based on codebase analysis  
**Owner**: Development Team  
**Status**: Ready for Implementation
