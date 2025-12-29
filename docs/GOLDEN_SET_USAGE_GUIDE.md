# Golden Set Usage Guide

## Quick Start

### 1. Running Tests

```bash
# Run all regression tests
pytest tests/test_golden_set_integration.py -v

# Run specific scenario tests
pytest tests/scenarios/test_portrait_scenes.py -v

# Run with coverage
pytest tests/ --cov=src.evaluation --cov-report=html

# Run only fast tests (exclude slow tests)
pytest tests/ -m "not slow"
```

### 2. Adding Golden References

```bash
# Add a new golden reference video
python scripts/add_golden_reference.py \
  --scenario TS_CHAR_001 \
  --video path/to/video.mp4 \
  --model-version v1.0.0 \
  --approver your.email@example.com \
  --compute-metrics

# Validate existing reference
python scripts/validate_golden_reference.py \
  --reference-id REF_TS_CHAR_001_v1.0.0_20240115 \
  --approver your.email@example.com \
  --recompute-metrics
```

### 3. Running CI Tests

```bash
# Run CI test suite
python -m src.evaluation.ci_integration \
  --test-videos test_videos_manifest.json \
  --test-version v1.1.0 \
  --baseline-version v1.0.0 \
  --output-dir ci_reports
```

### 4. Exporting Reports

```bash
# Export golden set summary as JSON
python scripts/export_golden_summary.py \
  --output reports/golden_set_summary.json \
  --format json

# Export as Markdown
python scripts/export_golden_summary.py \
  --output reports/golden_set_summary.md \
  --format markdown
```

## Test Scenarios

### Available Scenarios

The system includes 25+ test scenarios organized into categories:

#### Portrait Scenes (2)
- `TS_CHAR_004` - Subtle facial expression
- `TS_CHAR_005` - Head turn with eye tracking

#### Landscape Scenes (2)
- `TS_CAM_001` - Slow horizontal pan
- `TS_LIGHT_001` - Day to night transition

#### Multi-Character Scenes (2)
- `TS_CHAR_001` - Character walking forward
- `TS_CHAR_002` - Sprint running lateral

#### Dynamic Motion (2)
- `TS_CHAR_006` - Full body rotation (360°)
- `TS_CAM_006` - Dynamic subject tracking

#### Lighting Changes (2)
- `TS_LIGHT_003` - Light intensity change
- `TS_LIGHT_004` - Color temperature shift

#### Multi-Shot Sequences (2)
- `TS_MULTI_001` - Character continuity (indoor to outdoor)
- `TS_MULTI_002` - Lighting continuity (time progression)

#### Edge Cases (3)
- `TS_ENV_002` - Flowing water surface
- `TS_ENV_003` - Particle simulation (dust)
- `TS_ENV_004` - Weather transition (rain)

### Using Scenarios in Tests

```python
from src.evaluation import TestScenarioLibrary

library = TestScenarioLibrary()

# Get specific scenario
scenario = library.get_scenario("TS_CHAR_001")
print(f"Prompt: {scenario.prompt}")
print(f"Min Temporal Consistency: {scenario.min_temporal_consistency}")

# Filter by type
from src.evaluation.test_scenarios import MovementType
portrait_scenes = library.get_scenarios_by_type(MovementType.CHARACTER_FACIAL)

# Filter by difficulty
from src.evaluation.test_scenarios import DifficultyLevel
expert_scenes = library.get_scenarios_by_difficulty(DifficultyLevel.EXPERT)
```

## Pytest Fixtures

### Session-Scoped Fixtures

These are created once and shared across all tests:

- `golden_set_manager` - Golden set manager instance
- `scenario_library` - Test scenario library
- `metrics_engine` - Metrics computation engine
- `regression_suite` - Regression testing suite

### Function-Scoped Fixtures

These are created fresh for each test:

- `sample_test_video` - Generates a test video (640x480, 60 frames)
- `sample_test_video_high_quality` - 1080p test video
- `temp_dir` - Temporary directory for test artifacts

### Parametrized Fixtures

These run tests multiple times with different inputs:

```python
# Test will run once for each scenario
def test_scenario(scenario_id):
    # scenario_id will be: TS_CHAR_001, TS_CHAR_004, TS_CAM_001, etc.
    pass

# Test will run for each difficulty level
def test_difficulty(difficulty_level):
    # difficulty_level will be: BASIC, INTERMEDIATE, ADVANCED, EXPERT
    pass
```

## Metrics and Thresholds

### Available Metrics

1. **Temporal Consistency** - Frame-to-frame similarity
2. **Optical Flow Consistency** - Motion vector coherence
3. **SSIM** - Structural similarity
4. **Perceptual Quality** - Sharpness, contrast, brightness
5. **CLIP Similarity** - Text-video semantic alignment
6. **Instruction Following** - Prompt adherence

### Configuring Thresholds

```python
from src.evaluation import MetricsEngine

engine = MetricsEngine()

# Update global thresholds
engine.update_thresholds({
    "temporal_consistency": 0.90,
    "ssim": 0.85,
    "perceptual_quality": 0.85
})

# Compute metrics with custom thresholds
results = engine.compute_all(
    video_path="video.mp4",
    reference_data={"prompt": "Person walks forward"}
)
```

### Threshold Levels

- **Basic Scenes**: Lower thresholds (0.75-0.85)
- **Intermediate**: Moderate thresholds (0.80-0.88)
- **Advanced**: High thresholds (0.85-0.92)
- **Expert**: Strict thresholds (0.88-0.95)

## Golden Prompt Library

### Loading Prompts

```python
import json

with open('data/golden_prompts/prompt_library.json', 'r') as f:
    library = json.load(f)

# Get a specific prompt
prompt_data = library['prompts']['GP_CHAR_001']
canonical_prompt = prompt_data['canonical_prompt']

# Use template with variables
template = prompt_data['template']
# Template: "Person walks {direction} with {gait_style}, {speed} pace"

# Generate variations
variations = []
for direction in prompt_data['variables']['direction']:
    for gait in prompt_data['variables']['gait_style']:
        prompt = template.format(
            direction=direction,
            gait_style=gait,
            speed='moderate'
        )
        variations.append(prompt)
```

### Prompt Performance Tracking

Each prompt includes performance metrics:

```python
performance = prompt_data['performance']
print(f"Average CLIP Score: {performance['avg_clip_score']}")
print(f"Average Temporal Consistency: {performance['avg_temporal_consistency']}")
print(f"Success Rate: {performance['success_rate']}")
```

## CI/CD Integration

### GitHub Actions Workflow

The `.github/workflows/video_regression.yml` workflow:

1. Triggers on push/PR to main/develop branches
2. Downloads golden set from artifact storage
3. Runs regression tests against baseline
4. Uploads test reports as artifacts
5. Comments results on PRs
6. Fails build if regressions detected

### Triggering CI Tests

```bash
# Manually trigger CI tests
python -m src.evaluation.ci_integration \
  --test-videos test_videos_manifest.json \
  --test-version $GITHUB_SHA \
  --baseline-version main \
  --output-dir ci_reports

# Check exit code
if [ $? -eq 0 ]; then
  echo "All tests passed"
else
  echo "Tests failed - regressions detected"
fi
```

### Test Videos Manifest

Create a `test_videos_manifest.json`:

```json
{
  "version": "1.0.0",
  "created_at": "2024-01-15T10:00:00Z",
  "videos": {
    "TS_CHAR_001": "outputs/char_walk_v1.1.0.mp4",
    "TS_CHAR_004": "outputs/facial_expr_v1.1.0.mp4",
    "TS_CAM_001": "outputs/camera_pan_v1.1.0.mp4"
  }
}
```

## Storage and Versioning

### Directory Structure

```
data/golden_set/
├── metadata.json              # Master metadata
├── videos/                    # Reference videos
│   └── REF_TS_CHAR_001_*.mp4
├── frames/                    # Extracted frames
│   └── REF_TS_CHAR_001_*/
├── embeddings/                # CLIP embeddings
│   └── REF_TS_CHAR_001_*.npy
└── metrics/                   # Pre-computed metrics
    └── REF_TS_CHAR_001_*.json
```

### Backup Strategy

1. **Daily incremental backups** to cloud storage (S3/GCS)
2. **Weekly full backups** with 1-year retention
3. **Git-LFS** for large files versioning
4. **Metadata** tracked in git repository

### Accessing Golden Set

```python
from src.evaluation import GoldenSetManager

manager = GoldenSetManager("data/golden_set")

# Get latest approved reference
ref = manager.get_latest_reference(
    scenario_id="TS_CHAR_001",
    expert_approved_only=True
)

print(f"Reference ID: {ref.reference_id}")
print(f"Video Path: {ref.video_path}")
print(f"Metrics: {ref.metric_results}")
```

## Troubleshooting

### Common Issues

**Issue**: "Reference not found"
```bash
# Solution: Verify scenario ID is correct
python -c "from src.evaluation import TestScenarioLibrary; lib = TestScenarioLibrary(); print(list(lib.scenarios.keys()))"
```

**Issue**: "Video file not found"
```bash
# Solution: Check video path exists
ls -lh data/golden_set/videos/
```

**Issue**: "Metrics computation fails"
```bash
# Solution: Verify video file is valid
ffprobe path/to/video.mp4
```

### Debug Mode

```bash
# Run tests with verbose output
pytest tests/ -vv --log-cli-level=DEBUG

# Run single test with debugging
pytest tests/test_golden_set_integration.py::TestGoldenSetIntegration::test_scenario_library_completeness -vv
```

## Best Practices

1. **Always validate** golden references before marking as approved
2. **Compute metrics** when adding new references
3. **Document** any deviations or special cases in notes
4. **Version control** prompt library updates
5. **Run regression tests** before releasing new model versions
6. **Monitor trends** in metric scores over time
7. **Update thresholds** as model quality improves
8. **Archive** old references but keep metadata

## Resources

- Full specification: `docs/TEST_PLAN_SPECIFICATION.md`
- Evaluation system: `src/evaluation/`
- Test scenarios: `src/evaluation/test_scenarios.py`
- Metrics implementation: `src/evaluation/metrics.py`
- CI integration: `src/evaluation/ci_integration.py`
