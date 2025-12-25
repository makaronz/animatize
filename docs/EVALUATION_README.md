# Video Generation Evaluation System

## 🎯 Overview

A comprehensive evaluation harness and regression testing system for video generation models. This system provides automated quality assessment, performance benchmarking, and CI/CD integration for video generation pipelines.

## ✨ Key Features

### 📋 25+ Test Scenarios
- **Character Movement**: Walking, running, gestures, facial expressions, head turns, body rotation
- **Camera Movement**: Pan, tilt, zoom, dolly, orbit, subject tracking
- **Environment Effects**: Wind, water, particles, weather transitions, vegetation
- **Lighting Changes**: Day/night, shadows, intensity, color temperature
- **Multi-Scene Continuity**: Character and lighting consistency across scenes

### 📊 6 Quality Metrics
1. **Temporal Consistency** - Frame-to-frame coherence using SSIM
2. **Optical Flow Consistency** - Motion vector stability analysis
3. **SSIM** - Structural similarity (temporal or reference-based)
4. **Perceptual Quality** - Sharpness, contrast, and brightness analysis
5. **Instruction Following** - Semantic alignment (CLIP-based, placeholder)
6. **CLIP Similarity** - Cross-modal similarity (placeholder)

### 🏆 Golden Set Management
- SHA-256 video hashing for exact comparison
- Frame-level hash sampling
- Metadata tracking (fps, resolution, duration)
- Expert approval workflow
- Version control for references

### 🔄 Regression Testing
- Automated baseline comparison
- Metric delta tracking
- Degradation detection
- Pass/Fail/Degraded status classification
- Multi-scenario test suites

### ⚡ Performance Benchmarking
- Latency measurement (avg, median, p95, p99)
- Throughput tracking (FPS)
- Resource monitoring (CPU, memory)
- Statistical analysis across multiple runs
- Performance comparison reports

### 🔧 CI/CD Integration
- GitHub Actions workflow
- Automated test execution
- Badge generation
- PR comment integration
- Configurable pass/fail criteria

### 📈 Automated Reports
- HTML reports (styled, interactive)
- Markdown reports (GitHub-friendly)
- JSON reports (machine-readable)
- Model comparison reports (A vs B)
- Version progression reports (N vs N+1)

## 🚀 Quick Start

### Installation

```bash
# Install core dependencies
pip install -r requirements.txt

# Install computer vision dependencies
pip install -r requirements-cv.txt

# Optional: For CLIP metrics (requires PyTorch)
# pip install torch transformers clip-by-openai
```

### Basic Usage

```python
from src.evaluation import EvaluationHarness

# Initialize
harness = EvaluationHarness()

# Evaluate a video
result = harness.evaluate_video(
    video_path="my_video.mp4",
    scenario_id="TS_CHAR_001",
    model_version="v1.0.0"
)

print(f"Passed: {result['all_metrics_passed']}")
```

## 📚 Documentation

- [Full Guide](evaluation_system_guide.md) - Comprehensive documentation
- [Examples](../examples/evaluation_examples.py) - 9 detailed examples
- [API Reference](api_reference.md) - Complete API documentation

## 🧪 Test Scenarios

### Character Movement (6 scenarios)

| ID | Name | Difficulty | Frames | Key Thresholds |
|----|------|------------|--------|----------------|
| TS_CHAR_001 | Natural Walking | Basic | 60 | Temporal: 0.88 |
| TS_CHAR_002 | Sprint Running | Intermediate | 48 | Temporal: 0.85 |
| TS_CHAR_003 | Hand Gestures | Intermediate | 72 | Quality: 0.85 |
| TS_CHAR_004 | Facial Expression | Advanced | 36 | Temporal: 0.92 |
| TS_CHAR_005 | Head Turn | Advanced | 48 | Following: 0.92 |
| TS_CHAR_006 | Body Rotation | Expert | 96 | Temporal: 0.88 |

### Camera Movement (6 scenarios)

| ID | Name | Difficulty | Frames | Key Thresholds |
|----|------|------------|--------|----------------|
| TS_CAM_001 | Horizontal Pan | Basic | 72 | SSIM: 0.82 |
| TS_CAM_002 | Vertical Tilt | Basic | 60 | Following: 0.90 |
| TS_CAM_003 | Dynamic Zoom | Intermediate | 54 | Quality: 0.86 |
| TS_CAM_004 | Dolly Push | Intermediate | 84 | Temporal: 0.88 |
| TS_CAM_005 | Circular Orbit | Advanced | 96 | Following: 0.89 |
| TS_CAM_006 | Subject Tracking | Advanced | 90 | CLIP: 0.83 |

[Full scenario list](evaluation_system_guide.md#test-scenarios-reference)

## 🔬 Usage Examples

### 1. Single Video Evaluation

```python
from src.evaluation import EvaluationHarness

harness = EvaluationHarness()

result = harness.evaluate_video(
    video_path="test_video.mp4",
    scenario_id="TS_CHAR_001",
    model_version="v1.0.0",
    save_to_golden_set=True,
    expert_approved=True
)

# Check results
for metric_name, metric_data in result['metrics'].items():
    print(f"{metric_name}: {metric_data['score']:.3f} ({'✅' if metric_data['passed'] else '❌'})")
```

### 2. Regression Testing

```python
# Test new version against baseline
test_videos = {
    "TS_CHAR_001": "v2_walking.mp4",
    "TS_CAM_001": "v2_pan.mp4"
}

results = harness.run_regression_tests(
    test_videos=test_videos,
    test_version="v2.0.0",
    baseline_version="v1.0.0",
    generate_report=True
)

# Reports saved to: evaluation_results/reports/
```

### 3. Model Comparison

```python
# Compare two different models
comparison = harness.compare_models(
    model_a_videos={"TS_CHAR_001": "modelA.mp4"},
    model_b_videos={"TS_CHAR_001": "modelB.mp4"},
    model_a_name="ModelA",
    model_b_name="ModelB",
    generate_report=True
)

print(f"Winner: {comparison['summary']['overall_winner']}")
```

### 4. Performance Benchmarking

```python
def my_inference_fn(prompt, duration_frames):
    # Your video generation code
    video = generate_video(prompt, duration_frames)
    return {
        "video_path": video,
        "frames_generated": duration_frames,
        "processing_time": 2.5
    }

result = harness.benchmark_performance(
    inference_fn=my_inference_fn,
    scenario_id="TS_CHAR_001",
    model_version="v1.0.0",
    num_runs=10,
    prompt="Person walks forward",
    duration_frames=60
)

print(f"Avg latency: {result['avg_latency_ms']:.0f}ms")
```

### 5. CI/CD Integration

```python
from src.evaluation import CIIntegration, CITestConfig

ci = CIIntegration()

config = CITestConfig(
    test_version="v2.0.0",
    max_failures=0,
    max_degradations=2,
    min_pass_rate=95.0
)

results = ci.run_ci_tests(
    test_videos=test_videos,
    config=config
)

# Exit code 0 = pass, 1 = fail
```

## 📊 Report Examples

### HTML Report Features
- Interactive metric visualizations
- Color-coded pass/fail indicators
- Detailed metric breakdowns
- Side-by-side comparisons
- Responsive design

### Markdown Report (GitHub)
- Tables with metric comparisons
- Status badges
- Collapsible sections
- PR-friendly format

### JSON Report (Machine-Readable)
- Complete metric data
- Structured results
- CI/CD parseable
- Historical tracking

## 🔧 CI/CD Setup

### GitHub Actions

```yaml
# .github/workflows/video_evaluation.yml
name: Video Evaluation

on: [pull_request, push]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-cv.txt
      
      - name: Run evaluation
        run: |
          python -m src.evaluation.ci_integration \
            --test-videos test_videos/manifest.json \
            --test-version ${{ github.sha }} \
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

## 🎓 Advanced Features

### Custom Metrics

```python
from src.evaluation.metrics import VideoMetric, MetricResult

class MyCustomMetric(VideoMetric):
    def get_name(self):
        return "my_metric"
    
    def compute(self, video_path, reference_data=None):
        score = compute_my_metric(video_path)
        return MetricResult(
            metric_name=self.get_name(),
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold
        )

# Register
harness.metrics_engine.register_metric(MyCustomMetric(threshold=0.80))
```

### Multi-Scene Evaluation

```python
# Evaluate multi-scene scenario
multi_scene = harness.scenario_library.get_multi_scene_scenario("TS_MULTI_001")

for scene in multi_scene.scenes:
    result = harness.evaluate_video(
        video_path=f"scene_{scene.scenario_id}.mp4",
        scenario_id=scene.scenario_id,
        model_version="v1.0.0"
    )
```

## 📁 Directory Structure

```
src/evaluation/
├── __init__.py              # Main exports
├── evaluation_harness.py    # Orchestrator
├── test_scenarios.py        # 25+ test scenarios
├── metrics.py               # 6 quality metrics
├── golden_set.py            # Reference management
├── regression_system.py     # Regression testing
├── performance_benchmarks.py # Performance tests
├── ci_integration.py        # CI/CD hooks
└── report_generator.py      # Report generation

examples/
└── evaluation_examples.py   # 9 usage examples

tests/
└── test_evaluation_system.py # Unit tests

docs/
├── evaluation_system_guide.md # Full guide
└── EVALUATION_README.md      # This file

configs/
└── ci_config.yaml           # CI configuration

.github/workflows/
└── video_evaluation.yml     # GitHub Actions
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/test_evaluation_system.py -v

# Run examples
python examples/evaluation_examples.py

# Run specific example
python -c "from examples.evaluation_examples import example_6_explore_test_scenarios; example_6_explore_test_scenarios()"
```

## 📈 Metrics Explained

### Temporal Consistency (0-1)
Measures how consistent frames are over time. Higher = smoother motion.
- **Implementation**: SSIM between consecutive frames
- **Typical range**: 0.80-0.95
- **Use case**: Detect flickering or jittery motion

### Optical Flow Consistency (0-1)
Analyzes motion vector stability. Higher = more coherent movement.
- **Implementation**: Farneback optical flow analysis
- **Typical range**: 0.75-0.90
- **Use case**: Detect motion artifacts

### SSIM (0-1)
Structural similarity between frames or against reference.
- **Implementation**: Scikit-image SSIM
- **Typical range**: 0.70-0.90
- **Use case**: Compare with ground truth

### Perceptual Quality (0-1)
Combined metric of visual quality indicators.
- **Implementation**: Sharpness + contrast + brightness
- **Typical range**: 0.75-0.95
- **Use case**: Overall visual assessment

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Adding new test scenarios
- Implementing custom metrics
- Extending the evaluation system
- Submitting improvements

## 📄 License

See [LICENSE](../LICENSE) file.

## 🙏 Acknowledgments

Built using:
- OpenCV for video processing
- Scikit-image for image metrics
- NumPy for numerical operations
- Matplotlib for visualizations

## 📞 Support

- Documentation: [docs/evaluation_system_guide.md](evaluation_system_guide.md)
- Examples: [examples/evaluation_examples.py](../examples/evaluation_examples.py)
- Issues: File an issue on GitHub

## 🗺️ Roadmap

- [ ] CLIP metric integration
- [ ] GPU-accelerated metrics
- [ ] Real-time evaluation dashboard
- [ ] Extended scenario library (50+ scenarios)
- [ ] Video quality prediction models
- [ ] A/B testing framework
- [ ] Multi-model ensemble evaluation
