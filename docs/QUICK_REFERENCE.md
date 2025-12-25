# Test Plan Quick Reference

## File Locations

### Documentation
- `docs/TEST_PLAN_SPECIFICATION.md` - Complete test plan (1200+ lines)
- `docs/GOLDEN_SET_USAGE_GUIDE.md` - Usage guide (500+ lines)
- `docs/TEST_PLAN_IMPLEMENTATION_SUMMARY.md` - Implementation summary
- `docs/QUICK_REFERENCE.md` - This file

### Code
- `src/evaluation/test_scenarios.py` - 25+ test scenarios
- `src/evaluation/golden_set.py` - Golden set management
- `src/evaluation/regression_system.py` - Regression testing
- `src/evaluation/metrics.py` - Metrics computation
- `src/evaluation/ci_integration.py` - CI/CD integration

### Tests
- `tests/fixtures/video_generation_fixtures.py` - Pytest fixtures
- `tests/test_golden_set_integration.py` - Integration tests
- `tests/conftest.py` - Pytest configuration
- `pytest.ini` - Pytest settings

### Scripts
- `scripts/add_golden_reference.py` - Add golden reference
- `scripts/validate_golden_reference.py` - Validate reference
- `scripts/export_golden_summary.py` - Export summary

### Data
- `data/golden_prompts/prompt_library.json` - Golden prompts
- `data/golden_set/` - Golden reference videos and metadata

## Test Scenarios (12+ Core Scenes)

### Portrait (2)
- `TS_CHAR_004` - Subtle facial expression (Advanced, 36 frames)
- `TS_CHAR_005` - Head turn with eye tracking (Advanced, 48 frames)

### Landscape (2)
- `TS_CAM_001` - Slow horizontal pan (Basic, 72 frames)
- `TS_LIGHT_001` - Day to night transition (Advanced, 120 frames)

### Multi-Character (2)
- `TS_CHAR_001` - Character walking forward (Basic, 60 frames)
- `TS_CHAR_002` - Sprint running lateral (Intermediate, 48 frames)

### Dynamic Motion (2)
- `TS_CHAR_006` - Full body rotation 360° (Expert, 96 frames)
- `TS_CAM_006` - Dynamic subject tracking (Advanced, 90 frames)

### Lighting Change (2)
- `TS_LIGHT_003` - Light intensity change (Intermediate, 60 frames)
- `TS_LIGHT_004` - Color temperature shift (Advanced, 72 frames)

### Multi-Shot (2)
- `TS_MULTI_001` - Character continuity (Expert, 3 scenes)
- `TS_MULTI_002` - Lighting continuity (Expert, 2 scenes)

### Edge Cases (3)
- `TS_ENV_002` - Flowing water surface (Advanced, 84 frames)
- `TS_ENV_003` - Particle simulation (Advanced, 60 frames)
- `TS_ENV_004` - Weather transition (Expert, 96 frames)

## Acceptance Criteria Thresholds

| Metric | Threshold | Critical |
|--------|-----------|----------|
| Temporal Consistency | ≥ 0.85 | ≥ 0.75 |
| CLIP Score | ≥ 0.80 | ≥ 0.70 |
| SSIM | ≥ 0.75 | ≥ 0.65 |
| Perceptual Quality | ≥ 0.80 | ≥ 0.70 |
| Instruction Following | ≥ 0.90 | ≥ 0.80 |
| Optical Flow | ≥ 0.80 | ≥ 0.70 |
| Latency | ≤ 5000ms | ≤ 8000ms |
| Throughput | ≥ 1.0 FPS | ≥ 0.5 FPS |

## Common Commands

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run integration tests
pytest tests/test_golden_set_integration.py -v

# Run with coverage
pytest tests/ --cov=src.evaluation --cov-report=html

# Run specific markers
pytest tests/ -m regression -v
pytest tests/ -m "not slow" -v
```

### Golden Set Management
```bash
# Add reference
python scripts/add_golden_reference.py \
  --scenario TS_CHAR_001 \
  --video video.mp4 \
  --model-version v1.0.0 \
  --approver email@example.com \
  --compute-metrics

# Validate reference
python scripts/validate_golden_reference.py \
  --reference-id REF_TS_CHAR_001_v1.0.0_20240115 \
  --approver email@example.com \
  --recompute-metrics

# Export summary
python scripts/export_golden_summary.py \
  --output reports/summary.json \
  --format json
```

### CI Integration
```bash
# Run CI tests
python -m src.evaluation.ci_integration \
  --test-videos manifest.json \
  --test-version v1.1.0 \
  --baseline-version v1.0.0 \
  --output-dir ci_reports
```

## Python API Quick Start

### Load Test Scenarios
```python
from src.evaluation import TestScenarioLibrary

library = TestScenarioLibrary()
scenario = library.get_scenario("TS_CHAR_001")
print(f"Prompt: {scenario.prompt}")
print(f"Duration: {scenario.duration_frames} frames")
```

### Compute Metrics
```python
from src.evaluation import MetricsEngine

engine = MetricsEngine()
results = engine.compute_all(
    video_path="video.mp4",
    reference_data={"prompt": "Person walks forward"}
)

for name, result in results.items():
    print(f"{name}: {result.score:.3f} (passed: {result.passed})")
```

### Golden Set Operations
```python
from src.evaluation import GoldenSetManager

manager = GoldenSetManager("data/golden_set")

# Add reference
ref_id = manager.add_reference(
    scenario_id="TS_CHAR_001",
    video_path="video.mp4",
    model_version="v1.0.0",
    metric_results={"temporal_consistency": 0.89},
    expert_approved=True,
    approver="email@example.com"
)

# Get reference
ref = manager.get_reference(ref_id)
print(f"Video: {ref.video_path}")
print(f"Metrics: {ref.metric_results}")
```

### Run Regression Test
```python
from src.evaluation import RegressionTestSuite, GoldenSetManager, MetricsEngine, TestScenarioLibrary

golden_set = GoldenSetManager("data/golden_set")
metrics = MetricsEngine()
scenarios = TestScenarioLibrary()

suite = RegressionTestSuite(golden_set, metrics, scenarios)

result = suite.run_regression_test(
    test_video_path="new_video.mp4",
    scenario_id="TS_CHAR_001",
    test_version="v1.1.0",
    baseline_version="v1.0.0"
)

print(f"Status: {result.status}")
print(f"Pass Rate: {result.metrics_passed}/{result.metrics_passed + result.metrics_failed}")
```

## Pytest Fixtures

### Use in Tests
```python
def test_scenario(scenario_id):
    """Test runs for each parametrized scenario"""
    # scenario_id will be TS_CHAR_001, TS_CHAR_004, etc.
    
def test_with_video(sample_test_video):
    """Test with auto-generated video"""
    # sample_test_video is path to 640x480, 60 frame video
    
def test_with_golden_set(golden_set_manager):
    """Test with golden set manager"""
    # golden_set_manager is shared across all tests
```

## Storage Format

### Video File Naming
```
REF_{scenario_id}_{model_version}_{timestamp}.mp4

Example:
REF_TS_CHAR_001_v1.0.0_20240115_103000.mp4
```

### Directory Structure
```
data/golden_set/
├── metadata.json
├── videos/
│   └── REF_*.mp4
├── frames/
│   └── REF_*/frame_*.png
├── embeddings/
│   └── REF_*.npy
└── metrics/
    └── REF_*.json
```

## Markers

Use with `-m` flag:

- `slow` - Slow tests (skip with `-m "not slow"`)
- `integration` - Integration tests
- `regression` - Regression tests
- `performance` - Performance benchmarks
- `requires_golden` - Needs golden set

Example:
```bash
pytest tests/ -m "regression and not slow" -v
```

## Environment Variables

```bash
# Optional configuration
export GOLDEN_SET_PATH="data/golden_set"
export TEST_OUTPUT_DIR="ci_reports"
export PYTEST_WORKERS="auto"  # For parallel execution
```

## Troubleshooting

### Test Failures
```bash
# Run with verbose output
pytest tests/test_golden_set_integration.py -vv

# Run with debug logging
pytest tests/ --log-cli-level=DEBUG

# Run single test
pytest tests/test_golden_set_integration.py::TestGoldenSetIntegration::test_scenario_library_completeness -v
```

### Missing Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-cv.txt
pip install pytest pytest-cov
```

### Video Issues
```bash
# Check video file
ffprobe video.mp4

# Verify video format
python -c "import cv2; cap = cv2.VideoCapture('video.mp4'); print(f'Frames: {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}, FPS: {cap.get(cv2.CAP_PROP_FPS)}')"
```

## Key Metrics Reference

| Metric Name | Description | Good Range |
|-------------|-------------|------------|
| temporal_consistency | Frame-to-frame SSIM | 0.85-0.95 |
| optical_flow_consistency | Motion coherence | 0.80-0.90 |
| ssim | Structural similarity | 0.75-0.90 |
| perceptual_quality | Sharpness/contrast | 0.80-0.95 |
| clip_similarity | Text-video alignment | 0.80-0.95 |
| instruction_following | Prompt adherence | 0.90-0.98 |

## Golden Prompt Categories

- `characters/locomotion` - 6 prompts
- `characters/facial_expressions` - 3 prompts
- `characters/gestures` - 2 prompts
- `characters/rotations` - 2 prompts
- `camera/pan_tilt` - 2 prompts
- `camera/zoom` - 2 prompts
- `camera/dolly` - 1 prompt
- `camera/tracking` - 2 prompts
- `environment/*` - 4 prompts
- `lighting/*` - 4 prompts

Total: 20+ validated prompts

## Resources

- [Full Specification](TEST_PLAN_SPECIFICATION.md)
- [Usage Guide](GOLDEN_SET_USAGE_GUIDE.md)
- [Implementation Summary](TEST_PLAN_IMPLEMENTATION_SUMMARY.md)
- [Test Scenarios Code](../src/evaluation/test_scenarios.py)
- [Golden Set Code](../src/evaluation/golden_set.py)
