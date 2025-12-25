# Video Generation Evaluation System - Quick Reference

## 🚀 Quick Start (3 lines)

```python
from src.evaluation import EvaluationHarness
harness = EvaluationHarness()
result = harness.evaluate_video("video.mp4", "TS_CHAR_001", "v1.0.0")
```

## 📋 All Test Scenarios

| ID | Name | Type | Difficulty | Frames |
|----|------|------|------------|--------|
| **CHARACTER MOVEMENT** |
| TS_CHAR_001 | Natural Walking | Walk | Basic | 60 |
| TS_CHAR_002 | Sprint Running | Run | Intermediate | 48 |
| TS_CHAR_003 | Hand Gestures | Gesture | Intermediate | 72 |
| TS_CHAR_004 | Facial Expression | Facial | Advanced | 36 |
| TS_CHAR_005 | Head Turn | Head | Advanced | 48 |
| TS_CHAR_006 | Body Rotation | Body | Expert | 96 |
| **CAMERA MOVEMENT** |
| TS_CAM_001 | Horizontal Pan | Pan | Basic | 72 |
| TS_CAM_002 | Vertical Tilt | Tilt | Basic | 60 |
| TS_CAM_003 | Dynamic Zoom | Zoom | Intermediate | 54 |
| TS_CAM_004 | Dolly Push | Dolly | Intermediate | 84 |
| TS_CAM_005 | Circular Orbit | Orbit | Advanced | 96 |
| TS_CAM_006 | Subject Tracking | Track | Advanced | 90 |
| **ENVIRONMENT** |
| TS_ENV_001 | Wind Through Trees | Wind | Intermediate | 72 |
| TS_ENV_002 | Flowing Water | Water | Advanced | 84 |
| TS_ENV_003 | Particle Simulation | Particles | Advanced | 60 |
| TS_ENV_004 | Weather Transition | Weather | Expert | 96 |
| TS_ENV_005 | Vegetation Movement | Vegetation | Intermediate | 78 |
| **LIGHTING** |
| TS_LIGHT_001 | Day to Night | Day/Night | Advanced | 120 |
| TS_LIGHT_002 | Shadow Movement | Shadows | Intermediate | 84 |
| TS_LIGHT_003 | Intensity Change | Intensity | Intermediate | 60 |
| TS_LIGHT_004 | Color Temperature | Color | Advanced | 72 |
| **MULTI-SCENE** |
| TS_MULTI_001 | Character Continuity | Continuity | Expert | 168 |
| TS_MULTI_002 | Lighting Continuity | Continuity | Expert | 144 |

## 📊 All Metrics

| Metric | Range | Default Threshold | Description |
|--------|-------|-------------------|-------------|
| temporal_consistency | 0-1 | 0.85 | Frame-to-frame coherence (SSIM) |
| optical_flow_consistency | 0-1 | 0.80 | Motion vector stability |
| ssim | 0-1 | 0.75 | Structural similarity |
| perceptual_quality | 0-1 | 0.80 | Sharpness + contrast + brightness |
| instruction_following | 0-1 | 0.90 | Prompt adherence (requires CLIP) |
| clip_similarity | 0-1 | 0.80 | Text-image similarity (requires CLIP) |

## 🔧 Common Operations

### Evaluate Single Video
```python
result = harness.evaluate_video(
    video_path="test.mp4",
    scenario_id="TS_CHAR_001",
    model_version="v1.0.0",
    save_to_golden_set=True,  # Save if passed
    expert_approved=True       # Mark as approved
)
print(f"Passed: {result['all_metrics_passed']}")
```

### Run Regression Tests
```python
results = harness.run_regression_tests(
    test_videos={
        "TS_CHAR_001": "v2_walking.mp4",
        "TS_CAM_001": "v2_pan.mp4"
    },
    test_version="v2.0.0",
    baseline_version="v1.0.0",
    generate_report=True
)
```

### Compare Two Models
```python
comparison = harness.compare_models(
    model_a_videos={"TS_CHAR_001": "modelA.mp4"},
    model_b_videos={"TS_CHAR_001": "modelB.mp4"},
    model_a_name="ModelA",
    model_b_name="ModelB",
    generate_report=True
)
print(f"Winner: {comparison['summary']['overall_winner']}")
```

### Benchmark Performance
```python
def inference_fn(prompt, duration_frames):
    video = generate_video(prompt, duration_frames)
    return {"video_path": video, "frames_generated": duration_frames}

result = harness.benchmark_performance(
    inference_fn=inference_fn,
    scenario_id="TS_CHAR_001",
    model_version="v1.0.0",
    num_runs=10
)
print(f"Avg latency: {result['avg_latency_ms']:.0f}ms")
```

### Evaluate Multiple Scenarios
```python
results = harness.evaluate_scenario_suite(
    videos={
        "TS_CHAR_001": "walking.mp4",
        "TS_CHAR_002": "running.mp4",
        "TS_CAM_001": "pan.mp4"
    },
    model_version="v1.0.0",
    save_best_to_golden_set=True
)
print(f"Pass rate: {results['pass_rate']:.1f}%")
```

## 🎯 CI/CD Commands

### Command Line
```bash
# Run CI tests
python -m src.evaluation.ci_integration \
  --test-videos test_videos.json \
  --test-version v2.0.0 \
  --baseline-version v1.0.0 \
  --output-dir ci_reports

# Run with specific scenarios
python -m src.evaluation.ci_integration \
  --test-videos test_videos.json \
  --test-version v2.0.0 \
  --scenarios TS_CHAR_001 TS_CAM_001
```

### Python
```python
from src.evaluation import CIIntegration, CITestConfig

ci = CIIntegration()
config = CITestConfig(
    test_version="v2.0.0",
    max_failures=0,
    max_degradations=2,
    min_pass_rate=95.0
)

results = ci.run_ci_tests(test_videos, config)
exit_code = 0 if results['status'] == 'PASS' else 1
```

## 📁 File Structure

```
src/evaluation/
├── __init__.py                 # Main exports
├── evaluation_harness.py       # Orchestrator (USE THIS)
├── test_scenarios.py           # 25+ scenarios
├── metrics.py                  # 6 metrics
├── golden_set.py               # Reference management
├── regression_system.py        # Regression tests
├── performance_benchmarks.py   # Performance tests
├── ci_integration.py           # CI/CD hooks
└── report_generator.py         # Report generation

examples/evaluation_examples.py # 9 examples
scripts/run_evaluation_demo.py  # Interactive demo
tests/test_evaluation_system.py # Unit tests
```

## 🔍 Golden Set Operations

```python
from src.evaluation import GoldenSetManager

manager = GoldenSetManager("data/golden_set")

# Add reference
ref_id = manager.add_reference(
    scenario_id="TS_CHAR_001",
    video_path="reference.mp4",
    model_version="v1.0.0",
    expert_approved=True
)

# Get latest reference
latest = manager.get_latest_reference(
    scenario_id="TS_CHAR_001",
    expert_approved_only=True
)

# Compare videos
comparison = manager.compare_videos(
    "video1.mp4", "video2.mp4",
    comparison_level="hash"  # or "frames"
)
```

## 📊 Report Generation

```python
from src.evaluation import generate_all_reports

reports = generate_all_reports(
    comparison_data=comparison_results,
    title="Model Comparison Report",
    output_dir="reports"
)
# Generates: HTML, Markdown, JSON
```

## 🧪 Custom Metrics

```python
from src.evaluation.metrics import VideoMetric, MetricResult

class MyMetric(VideoMetric):
    def get_name(self):
        return "my_metric"
    
    def compute(self, video_path, reference_data=None):
        score = compute_my_score(video_path)
        return MetricResult(
            metric_name=self.get_name(),
            score=score,
            passed=score >= self.threshold,
            threshold=self.threshold
        )

# Register
harness.metrics_engine.register_metric(MyMetric(threshold=0.85))
```

## ⚙️ Configuration

### Update Thresholds
```python
harness.metrics_engine.update_thresholds({
    "temporal_consistency": 0.90,
    "ssim": 0.85,
    "perceptual_quality": 0.88
})
```

### CI Config (YAML)
```yaml
# configs/ci_config.yaml
test_config:
  thresholds:
    max_failures: 0
    max_degradations: 2
    min_pass_rate: 95.0
```

## 📈 Status Codes

### Regression Status
- `PASS`: All metrics meet thresholds
- `FAIL`: One or more metrics fail
- `DEGRADED`: Significant decline (>5%)
- `IMPROVED`: Better than baseline
- `UNSTABLE`: Inconsistent results
- `ERROR`: Test execution error

### CI Exit Codes
- `0`: Tests passed
- `1`: Tests failed

## 🎓 Examples

```bash
# Run demo (no videos needed)
python scripts/run_evaluation_demo.py

# Run examples
python examples/evaluation_examples.py

# Run tests
pytest tests/test_evaluation_system.py -v

# Run specific example
python -c "from examples.evaluation_examples import example_6_explore_test_scenarios; example_6_explore_test_scenarios()"
```

## 📚 Documentation

- **Full Guide**: `docs/evaluation_system_guide.md`
- **README**: `docs/EVALUATION_README.md`
- **Summary**: `docs/IMPLEMENTATION_SUMMARY.md`
- **This File**: `docs/QUICK_REFERENCE.md`

## 🐛 Troubleshooting

### Import Error
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.evaluation import EvaluationHarness
```

### Missing Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-cv.txt
```

### Video Reading Issues
```python
# Check if OpenCV can read video
import cv2
cap = cv2.VideoCapture("video.mp4")
print(f"Can read: {cap.isOpened()}")
cap.release()
```

## 💡 Tips

1. **Start Simple**: Use `example_6_explore_test_scenarios()` to understand scenarios
2. **Test Coverage**: Run `harness.get_test_coverage_report()` to see status
3. **Custom Scenarios**: Add to `TestScenarioLibrary._initialize_scenarios()`
4. **Golden Set**: Always get expert approval before adding references
5. **CI/CD**: Start with relaxed thresholds, tighten over time
6. **Reports**: HTML for humans, JSON for automation
7. **Performance**: Use `num_runs=3` for quick tests, `10+` for production

## 🔗 Quick Links

- GitHub Actions: `.github/workflows/video_evaluation.yml`
- CI Config: `configs/ci_config.yaml`
- Main Module: `src/evaluation/evaluation_harness.py`
- Examples: `examples/evaluation_examples.py`
- Tests: `tests/test_evaluation_system.py`
