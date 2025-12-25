# Video Generation Evaluation System Guide

## Overview

Comprehensive evaluation harness for video generation models with automated regression testing, performance benchmarking, and CI/CD integration.

## Features

### 1. Test Scenarios (25+ scenarios)

#### Coverage Areas:
- **Character Movement** (6 scenarios)
  - Walking, running, gestures, facial expressions, head turns, body rotation
- **Camera Movement** (6 scenarios)
  - Pan, tilt, zoom, dolly, orbit, tracking
- **Environment Effects** (5 scenarios)
  - Wind, water, particles, weather, vegetation
- **Lighting Changes** (4 scenarios)
  - Day/night transitions, shadows, intensity, color temperature
- **Multi-Scene Continuity** (2+ scenarios)
  - Character consistency, lighting continuity across scenes

### 2. Quality Metrics

#### Implemented Metrics:
1. **Temporal Consistency** (0-1)
   - Measures frame-to-frame coherence using SSIM
   - Higher scores = smoother, more consistent motion

2. **Optical Flow Consistency** (0-1)
   - Analyzes motion vector stability
   - Detects jittery or inconsistent movement

3. **SSIM (Structural Similarity)** (0-1)
   - Compares structural similarity between frames or against reference
   - Can be temporal or reference-based

4. **Perceptual Quality** (0-1)
   - Combined metric of sharpness, contrast, and brightness
   - Measures overall visual quality

5. **Instruction Following** (placeholder)
   - Requires CLIP model integration
   - Measures semantic alignment with text prompt

6. **CLIP Similarity** (placeholder)
   - Requires transformers/CLIP
   - Cross-modal text-image similarity

### 3. Golden Set Management

Reference video management system with:
- SHA-256 hashing for exact matching
- Frame-level hash sampling
- Metadata extraction (fps, resolution, duration)
- Expert approval workflow
- Version tracking

### 4. Regression Testing

Automated comparison system:
- Baseline vs. test comparison
- Metric delta tracking
- Degradation detection
- Status classification (PASS/FAIL/DEGRADED/IMPROVED)
- Multi-scenario suite execution

### 5. Performance Benchmarking

System performance measurement:
- Latency tracking (avg, median, p95, p99)
- Throughput measurement (FPS)
- Resource monitoring (CPU, memory)
- Multi-run statistical analysis
- Performance comparison reports

### 6. CI/CD Integration

Continuous integration support:
- GitHub Actions workflow
- Automated test execution
- Badge generation
- PR comments with results
- Configurable pass/fail thresholds

### 7. Report Generation

Multiple report formats:
- HTML (styled, interactive)
- Markdown (GitHub-friendly)
- JSON (machine-readable)
- CI badges
- GitHub Actions summaries

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-cv.txt
```

### Basic Usage

```python
from src.evaluation import EvaluationHarness

# Initialize harness
harness = EvaluationHarness(
    golden_set_path="data/golden_set",
    output_dir="evaluation_results"
)

# Evaluate a single video
result = harness.evaluate_video(
    video_path="test_video.mp4",
    scenario_id="TS_CHAR_001",
    model_version="v1.0.0"
)

print(f"All metrics passed: {result['all_metrics_passed']}")
```

### Running Regression Tests

```python
# Prepare test videos
test_videos = {
    "TS_CHAR_001": "path/to/walking_video.mp4",
    "TS_CAM_001": "path/to/pan_video.mp4"
}

# Run regression tests
results = harness.run_regression_tests(
    test_videos=test_videos,
    test_version="v2.0.0",
    baseline_version="v1.0.0",
    generate_report=True
)
```

### Comparing Two Models

```python
# Compare model outputs
comparison = harness.compare_models(
    model_a_videos={"TS_CHAR_001": "modelA_video.mp4"},
    model_b_videos={"TS_CHAR_001": "modelB_video.mp4"},
    model_a_name="ModelA",
    model_b_name="ModelB",
    generate_report=True
)

print(f"Winner: {comparison['summary']['overall_winner']}")
```

### Performance Benchmarking

```python
def my_inference_fn(prompt, duration_frames):
    # Your inference code here
    return {
        "video_path": "output.mp4",
        "frames_generated": duration_frames,
        "processing_time": 2.5
    }

# Benchmark performance
result = harness.benchmark_performance(
    inference_fn=my_inference_fn,
    scenario_id="TS_CHAR_001",
    model_version="v1.0.0",
    num_runs=10,
    prompt="Person walks forward",
    duration_frames=60
)
```

## Test Scenarios Reference

### Character Movement Scenarios

| Scenario ID | Name | Difficulty | Duration | Key Metrics |
|-------------|------|------------|----------|-------------|
| TS_CHAR_001 | Natural Walking | Basic | 60 frames | Temporal: 0.88, SSIM: 0.80 |
| TS_CHAR_002 | Sprint Running | Intermediate | 48 frames | Temporal: 0.85, Following: 0.88 |
| TS_CHAR_003 | Hand Gestures | Intermediate | 72 frames | Temporal: 0.87, Quality: 0.85 |
| TS_CHAR_004 | Facial Expression | Advanced | 36 frames | Temporal: 0.92, Quality: 0.88 |
| TS_CHAR_005 | Head Turn | Advanced | 48 frames | Temporal: 0.90, Following: 0.92 |
| TS_CHAR_006 | Body Rotation | Expert | 96 frames | Temporal: 0.88, SSIM: 0.78 |

### Camera Movement Scenarios

| Scenario ID | Name | Difficulty | Duration | Key Metrics |
|-------------|------|------------|----------|-------------|
| TS_CAM_001 | Horizontal Pan | Basic | 72 frames | Temporal: 0.90, SSIM: 0.82 |
| TS_CAM_002 | Vertical Tilt | Basic | 60 frames | Temporal: 0.89, Following: 0.90 |
| TS_CAM_003 | Dynamic Zoom | Intermediate | 54 frames | Temporal: 0.87, Quality: 0.86 |
| TS_CAM_004 | Dolly Push | Intermediate | 84 frames | Temporal: 0.88, SSIM: 0.79 |
| TS_CAM_005 | Circular Orbit | Advanced | 96 frames | Temporal: 0.86, Following: 0.89 |
| TS_CAM_006 | Subject Tracking | Advanced | 90 frames | Temporal: 0.87, CLIP: 0.83 |

## Metric Thresholds

Default thresholds can be customized per scenario:

```python
scenario = TestScenario(
    scenario_id="CUSTOM_001",
    # ... other params ...
    min_temporal_consistency=0.85,
    min_instruction_following=0.90,
    min_clip_similarity=0.80,
    min_ssim=0.75,
    min_perceptual_quality=0.80,
    max_latency_ms=5000.0,
    min_throughput_fps=1.0
)
```

## Golden Set Best Practices

1. **Expert Approval**: Always have experts review before approval
2. **Version Tracking**: Track model version for each reference
3. **Regular Updates**: Update golden set as quality improves
4. **Diversity**: Ensure coverage across all scenario types
5. **Documentation**: Add notes explaining why references are good

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/video_evaluation.yml
- name: Run evaluation tests
  run: |
    python -m src.evaluation.ci_integration \
      --test-videos test_videos/manifest.json \
      --test-version ${{ github.sha }} \
      --baseline-version latest \
      --output-dir ci_reports
```

### Configuration

```yaml
# configs/ci_config.yaml
test_config:
  thresholds:
    max_failures: 0
    max_degradations: 2
    min_pass_rate: 95.0
```

## Advanced Usage

### Custom Metrics

```python
from src.evaluation.metrics import VideoMetric, MetricResult

class CustomMetric(VideoMetric):
    def get_name(self):
        return "custom_metric"
    
    def compute(self, video_path, reference_data=None):
        # Your metric computation
        score = 0.85
        return MetricResult(
            metric_name=self.get_name(),
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold
        )

# Register custom metric
harness.metrics_engine.register_metric(CustomMetric(threshold=0.80))
```

### Multi-Scene Evaluation

```python
# Get multi-scene scenario
multi_scene = harness.scenario_library.get_multi_scene_scenario("TS_MULTI_001")

# Evaluate each scene
for scene in multi_scene.scenes:
    result = harness.evaluate_video(
        video_path=f"scene_{scene.scenario_id}.mp4",
        scenario_id=scene.scenario_id,
        model_version="v1.0.0"
    )
```

## Troubleshooting

### Common Issues

1. **Missing CLIP/transformers**
   - Instruction following and CLIP metrics require additional dependencies
   - Install: `pip install torch transformers clip-by-openai`

2. **Video codec issues**
   - Ensure OpenCV can read your video format
   - Try converting to MP4 (H.264)

3. **Memory issues with large videos**
   - Use frame sampling in metrics
   - Process videos in batches

## Performance Tips

1. **Parallel Processing**: Process multiple scenarios in parallel
2. **Frame Sampling**: Use `sample_every` parameter in frame hash computation
3. **Caching**: Cache metric results to avoid recomputation
4. **GPU Acceleration**: Use GPU for CLIP/neural metrics when available

## API Reference

See [API Documentation](api_reference.md) for detailed API reference.

## Examples

See `examples/evaluation_examples.py` for 9 comprehensive examples covering:
1. Single video evaluation
2. Scenario suite evaluation
3. Regression testing
4. Model comparison
5. Performance benchmarking
6. Test scenario exploration
7. Golden set management
8. CI/CD integration
9. Test coverage reporting

## Contributing

When adding new test scenarios:
1. Define clear movement type and difficulty
2. Set appropriate metric thresholds
3. Document expected behavior
4. Add to scenario library
5. Create golden references
6. Update documentation

## License

See LICENSE file for details.
