# Video Generation Test Plan and Golden Set Specification

## Overview

This document defines the comprehensive test plan for video generation systems, including 12+ test scenes across diverse scenarios, acceptance criteria, golden prompt library, regression test automation, and storage specifications.

---

## 1. Test Scene Definitions (12 Core Scenes)

### 1.1 Portrait Scene Tests

#### Scene 1: Single Character Portrait - Subtle Facial Expression
- **Scenario ID**: `TS_CHAR_004`
- **Type**: Portrait, Close-up
- **Description**: Micro-expressions and subtle facial movements in portrait framing
- **Input Prompt**: "Subtle smile forming with slight eye movement and eyebrow raise"
- **Duration**: 36 frames (1.2 seconds @ 30fps)
- **Difficulty**: Advanced
- **Key Features**:
  - Facial micro-expressions
  - Eye movement coordination
  - Natural emotion progression
  - High-detail skin texture preservation

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.92
- CLIP Score: ≥ 0.85
- Perceptual Quality: ≥ 0.88
- SSIM (frame-to-frame): ≥ 0.85
- No visible artifacts: Face morphing, eye discontinuities, skin texture degradation
- Latency: ≤ 3800ms

#### Scene 2: Head Turn with Eye Tracking
- **Scenario ID**: `TS_CHAR_005`
- **Type**: Portrait, Dynamic Head Movement
- **Description**: Character turns head 90 degrees while eyes track a moving object
- **Input Prompt**: "Head turns 90 degrees from profile to camera while eyes track movement"
- **Duration**: 48 frames (1.6 seconds @ 30fps)
- **Difficulty**: Advanced
- **Key Features**:
  - Complex head rotation
  - Eye tracking coordination
  - Perspective consistency
  - Facial feature preservation

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.90
- Instruction Following: ≥ 0.92
- CLIP Score: ≥ 0.83
- No visible artifacts: Facial distortion, eye misalignment, perspective breaks
- Latency: ≤ 4100ms

---

### 1.2 Landscape Scene Tests

#### Scene 3: Slow Horizontal Pan
- **Scenario ID**: `TS_CAM_001`
- **Type**: Landscape, Camera Movement
- **Description**: Smooth horizontal pan revealing scenic vista details
- **Input Prompt**: "Slow, steady pan from left to right revealing scenic vista"
- **Duration**: 72 frames (2.4 seconds @ 30fps)
- **Difficulty**: Basic
- **Key Features**:
  - Smooth camera motion
  - Parallax effects
  - Detail preservation during movement
  - Motion blur consistency

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.90
- SSIM: ≥ 0.82
- Optical Flow Consistency: ≥ 0.85
- No visible artifacts: Warping, jitter, blur inconsistency
- Latency: ≤ 3500ms

#### Scene 4: Day to Night Transition
- **Scenario ID**: `TS_LIGHT_001`
- **Type**: Landscape, Lighting Change
- **Description**: Natural lighting transition from day to dusk
- **Input Prompt**: "Scene transitions from bright day to dusk with natural color grading"
- **Duration**: 120 frames (4.0 seconds @ 30fps)
- **Difficulty**: Advanced
- **Key Features**:
  - Smooth lighting transition
  - Color temperature shift
  - Shadow movement
  - Exposure consistency

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.86
- Instruction Following: ≥ 0.90
- Perceptual Quality: ≥ 0.87
- No visible artifacts: Harsh lighting jumps, color banding, exposure spikes
- Latency: ≤ 4900ms

---

### 1.3 Multi-Character Scene Tests

#### Scene 5: Character Walking - Forward Motion
- **Scenario ID**: `TS_CHAR_001`
- **Type**: Multi-character capable, Basic locomotion
- **Description**: Character walks naturally towards camera with realistic gait
- **Input Prompt**: "Person walks naturally forward with steady, confident gait"
- **Duration**: 60 frames (2.0 seconds @ 30fps)
- **Difficulty**: Basic
- **Key Features**:
  - Natural gait cycle
  - Body coordination
  - Perspective consistency
  - Ground contact realism

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.88
- SSIM: ≥ 0.80
- Perceptual Quality: ≥ 0.82
- No visible artifacts: Limb detachment, foot sliding, gait irregularity
- Latency: ≤ 4000ms

#### Scene 6: Sprint Running - Lateral Motion
- **Scenario ID**: `TS_CHAR_002`
- **Type**: Multi-character capable, High-speed motion
- **Description**: Character sprints laterally with dynamic, powerful motion
- **Input Prompt**: "Athlete sprints left to right with powerful, dynamic running motion"
- **Duration**: 48 frames (1.6 seconds @ 30fps)
- **Difficulty**: Intermediate
- **Key Features**:
  - High-speed motion handling
  - Motion blur realism
  - Body dynamics
  - Edge retention

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.85
- Instruction Following: ≥ 0.88
- Optical Flow Consistency: ≥ 0.82
- No visible artifacts: Motion blur artifacts, body distortion, background smearing
- Latency: ≤ 4500ms

---

### 1.4 Dynamic Motion Tests

#### Scene 7: Full Body Rotation
- **Scenario ID**: `TS_CHAR_006`
- **Type**: Complex rotation, 360-degree
- **Description**: Character performs smooth 360-degree rotation
- **Input Prompt**: "Person rotates smoothly 360 degrees showing all sides"
- **Duration**: 96 frames (3.2 seconds @ 30fps)
- **Difficulty**: Expert
- **Key Features**:
  - Complete rotation cycle
  - Identity preservation through rotation
  - Occlusion handling
  - Perspective consistency

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.88
- SSIM: ≥ 0.78
- Perceptual Quality: ≥ 0.85
- No visible artifacts: Morphing during rotation, feature loss, perspective breaks
- Latency: ≤ 5000ms

#### Scene 8: Dynamic Subject Tracking
- **Scenario ID**: `TS_CAM_006`
- **Type**: Camera tracking, Moving subject
- **Description**: Camera follows running subject maintaining composition
- **Input Prompt**: "Camera tracks running subject keeping them centered in frame"
- **Duration**: 90 frames (3.0 seconds @ 30fps)
- **Difficulty**: Advanced
- **Key Features**:
  - Tracking smoothness
  - Subject centering
  - Background motion consistency
  - Focus maintenance

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.87
- CLIP Score: ≥ 0.83
- Optical Flow Consistency: ≥ 0.84
- No visible artifacts: Jerky tracking, subject drift, focus loss
- Latency: ≤ 4600ms

---

### 1.5 Lighting Change Tests

#### Scene 9: Light Intensity Change
- **Scenario ID**: `TS_LIGHT_003`
- **Type**: Lighting, Exposure adjustment
- **Description**: Scene lighting gradually brightens revealing details
- **Input Prompt**: "Scene lighting gradually brightens revealing more details"
- **Duration**: 60 frames (2.0 seconds @ 30fps)
- **Difficulty**: Intermediate
- **Key Features**:
  - Smooth exposure transition
  - Detail emergence
  - No over/underexposure
  - Highlight preservation

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.88
- Perceptual Quality: ≥ 0.85
- SSIM: ≥ 0.80
- No visible artifacts: Blown highlights, crushed shadows, exposure jumps
- Latency: ≤ 4100ms

#### Scene 10: Color Temperature Shift
- **Scenario ID**: `TS_LIGHT_004`
- **Type**: Lighting, Color grading
- **Description**: Lighting shifts from warm sunset to cool blue evening
- **Input Prompt**: "Lighting shifts from warm sunset tones to cool blue evening"
- **Duration**: 72 frames (2.4 seconds @ 30fps)
- **Difficulty**: Advanced
- **Key Features**:
  - Color temperature transition
  - White balance consistency
  - Tone preservation
  - Natural color grading

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.85
- Instruction Following: ≥ 0.89
- CLIP Score: ≥ 0.81
- No visible artifacts: Color banding, unnatural tints, saturation spikes
- Latency: ≤ 4500ms

---

### 1.6 Multi-Shot Sequence Tests

#### Scene 11: Character Continuity - Indoor to Outdoor
- **Scenario ID**: `TS_MULTI_001`
- **Type**: Multi-shot sequence, 3 scenes
- **Description**: Character maintains identity across three connected scenes
- **Scenes**:
  1. Indoor hallway walk (60 frames)
  2. Doorway transition (48 frames)
  3. Outdoor continuation (60 frames)
- **Difficulty**: Expert
- **Key Features**:
  - Character identity consistency
  - Clothing/appearance preservation
  - Lighting adaptation
  - Spatial continuity

**Acceptance Criteria (per scene)**:
- Temporal Consistency: ≥ 0.90
- Character Consistency (cross-scene): ≥ 0.95
- Lighting Consistency (cross-scene): ≥ 0.82
- Style Consistency: ≥ 0.92
- Transition Smoothness: ≥ 0.88
- No visible artifacts: Identity shift, clothing changes, discontinuities

#### Scene 12: Lighting Continuity - Time Progression
- **Scenario ID**: `TS_MULTI_002`
- **Type**: Multi-shot sequence, 2 scenes
- **Description**: Location maintains spatial consistency across lighting changes
- **Scenes**:
  1. Morning light (72 frames)
  2. Midday light (72 frames)
- **Difficulty**: Expert
- **Key Features**:
  - Spatial consistency
  - Natural lighting progression
  - Shadow movement
  - Environment preservation

**Acceptance Criteria (per scene)**:
- Temporal Consistency: ≥ 0.88
- Lighting Consistency: ≥ 0.88
- Style Consistency: ≥ 0.93
- Transition Smoothness: ≥ 0.85
- No visible artifacts: Location changes, unnatural lighting, shadow discontinuities

---

### 1.7 Edge Case Tests

#### Edge Case 1: Particle Simulation - Dust
- **Scenario ID**: `TS_ENV_003`
- **Type**: Environment, Particle physics
- **Description**: Dust particles floating with realistic physics
- **Input Prompt**: "Dust particles float and drift through air with natural motion"
- **Duration**: 60 frames (2.0 seconds @ 30fps)
- **Difficulty**: Advanced
- **Key Features**:
  - Particle simulation accuracy
  - Physics realism
  - Depth consistency
  - Motion coherence

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.83
- Perceptual Quality: ≥ 0.83
- Optical Flow Consistency: ≥ 0.80
- No visible artifacts: Particle popping, unnatural movement, depth conflicts
- Latency: ≤ 4400ms

#### Edge Case 2: Flowing Water Surface
- **Scenario ID**: `TS_ENV_002`
- **Type**: Environment, Complex surface dynamics
- **Description**: Water surface with realistic waves and reflections
- **Input Prompt**: "Water surface with gentle waves and realistic reflections moving"
- **Duration**: 84 frames (2.8 seconds @ 30fps)
- **Difficulty**: Advanced
- **Key Features**:
  - Fluid dynamics
  - Reflection accuracy
  - Surface deformation
  - Light interaction

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.84
- SSIM: ≥ 0.76
- Perceptual Quality: ≥ 0.84
- No visible artifacts: Reflection breaks, unnatural waves, surface tearing
- Latency: ≤ 4700ms

#### Edge Case 3: Weather Transition - Rain
- **Scenario ID**: `TS_ENV_004`
- **Type**: Environment, Weather simulation
- **Description**: Rain beginning and gradually intensifying
- **Input Prompt**: "Rain begins falling, starting light and gradually intensifying"
- **Duration**: 96 frames (3.2 seconds @ 30fps)
- **Difficulty**: Expert
- **Key Features**:
  - Weather transition realism
  - Particle density variation
  - Atmospheric effects
  - Surface interaction

**Acceptance Criteria**:
- Temporal Consistency: ≥ 0.82
- Instruction Following: ≥ 0.88
- Perceptual Quality: ≥ 0.84
- No visible artifacts: Rain pattern repetition, unnatural accumulation, lighting inconsistency
- Latency: ≤ 5000ms

---

## 2. Acceptance Criteria Framework

### 2.1 Temporal Metrics

| Metric | Threshold | Description |
|--------|-----------|-------------|
| Temporal Consistency | ≥ 0.85 | Frame-to-frame SSIM measuring motion smoothness |
| Optical Flow Consistency | ≥ 0.80 | Motion vector coherence across frames |
| Frame Jitter Detection | < 5% frames | Percentage of frames with abnormal motion |

### 2.2 Semantic Alignment Metrics

| Metric | Threshold | Description |
|--------|-----------|-------------|
| CLIP Score | ≥ 0.80 | Text-video semantic alignment |
| Instruction Following | ≥ 0.90 | Prompt adherence accuracy |
| Object Presence Accuracy | ≥ 0.95 | Requested objects present in scene |

### 2.3 Visual Quality Metrics

| Metric | Threshold | Description |
|--------|-----------|-------------|
| SSIM (Structural Similarity) | ≥ 0.75 | Frame structural quality |
| Perceptual Quality | ≥ 0.80 | Combined sharpness, contrast, brightness |
| Sharpness (Laplacian Variance) | ≥ 100 | Image detail and focus quality |
| Contrast Score | ≥ 30 | Dynamic range utilization |

### 2.4 Artifact Detection

| Artifact Type | Maximum Tolerance |
|---------------|-------------------|
| Face/Body Morphing | 0 occurrences |
| Temporal Flickering | < 2% frames |
| Object Disappearance | 0 occurrences |
| Perspective Breaks | 0 occurrences |
| Color Banding | < 1% image area |
| Motion Blur Artifacts | < 3% frames |
| Background Inconsistencies | < 5% variation |

### 2.5 Performance Metrics

| Metric | Threshold |
|--------|-----------|
| Inference Latency (per frame) | ≤ 150ms |
| Total Generation Time (60 frames) | ≤ 5000ms |
| Memory Usage (peak) | ≤ 16GB |
| Throughput | ≥ 1.0 FPS |

### 2.6 Scene-Specific Criteria

#### Portrait Scenes
- Face Identity Consistency: ≥ 0.95
- Expression Naturalness: ≥ 0.90
- Eye Movement Coordination: No drift

#### Landscape Scenes
- Spatial Consistency: ≥ 0.92
- Parallax Correctness: ≥ 0.88
- Horizon Line Stability: ≤ 2px variance

#### Multi-Character Scenes
- Inter-Character Occlusion: Correct depth ordering
- Character Identity Preservation: ≥ 0.95 per character
- Relative Motion Consistency: ≥ 0.90

#### Lighting Change Scenes
- Exposure Smoothness: ≥ 0.88
- Color Grading Consistency: ≥ 0.85
- Shadow Movement Realism: ≥ 0.87

---

## 3. Golden Prompt Library

### 3.1 Library Organization

The golden prompt library is organized into categories with validated, high-performing prompts:

```
golden_prompts/
├── characters/
│   ├── locomotion.json
│   ├── facial_expressions.json
│   ├── gestures.json
│   └── rotations.json
├── camera/
│   ├── pan_tilt.json
│   ├── zoom.json
│   ├── dolly.json
│   └── tracking.json
├── environment/
│   ├── weather.json
│   ├── particles.json
│   ├── water.json
│   └── vegetation.json
├── lighting/
│   ├── time_of_day.json
│   ├── intensity.json
│   ├── color_temperature.json
│   └── shadows.json
└── multi_scene/
    ├── continuity.json
    └── transitions.json
```

### 3.2 Prompt Template Structure

Each prompt in the library includes:

```json
{
  "prompt_id": "GP_CHAR_WALK_001",
  "category": "characters/locomotion",
  "template": "Person walks {direction} with {gait_style}, {speed} pace",
  "variables": {
    "direction": ["forward", "backward", "sideways"],
    "gait_style": ["confident", "casual", "hurried", "cautious"],
    "speed": ["slow", "moderate", "brisk"]
  },
  "examples": [
    "Person walks forward with confident, moderate pace",
    "Person walks backward with cautious, slow pace"
  ],
  "tested_scenarios": ["TS_CHAR_001"],
  "avg_clip_score": 0.89,
  "avg_temporal_consistency": 0.88,
  "expert_validated": true,
  "validation_date": "2024-01-15",
  "notes": "Works best with full-body character visible"
}
```

### 3.3 Core Golden Prompts

#### Character Motion Prompts
- `GP_CHAR_001`: "Person walks naturally forward with steady, confident gait"
- `GP_CHAR_002`: "Athlete sprints left to right with powerful, dynamic running motion"
- `GP_CHAR_003`: "Person gestures expressively with hands while explaining something"
- `GP_CHAR_004`: "Subtle smile forming with slight eye movement and eyebrow raise"
- `GP_CHAR_005`: "Head turns 90 degrees from profile to camera while eyes track movement"
- `GP_CHAR_006`: "Person rotates smoothly 360 degrees showing all sides"

#### Camera Movement Prompts
- `GP_CAM_001`: "Slow, steady pan from left to right revealing scenic vista"
- `GP_CAM_002`: "Camera tilts upward from building base to top revealing architecture"
- `GP_CAM_003`: "Smooth zoom in from wide shot to close-up maintaining sharp focus"
- `GP_CAM_004`: "Camera dollies forward through corridor with smooth motion parallax"
- `GP_CAM_005`: "Camera orbits 180 degrees around subject maintaining framing"
- `GP_CAM_006`: "Camera tracks running subject keeping them centered in frame"

#### Environment Prompts
- `GP_ENV_001`: "Gentle wind rustles through tree leaves with natural swaying motion"
- `GP_ENV_002`: "Water surface with gentle waves and realistic reflections moving"
- `GP_ENV_003`: "Dust particles float and drift through air with natural motion"
- `GP_ENV_004`: "Rain begins falling, starting light and gradually intensifying"
- `GP_ENV_005`: "Plants and flowers sway gently in breeze with natural movement"

#### Lighting Prompts
- `GP_LIGHT_001`: "Scene transitions from bright day to dusk with natural color grading"
- `GP_LIGHT_002`: "Shadows sweep across scene as if sun is moving through sky"
- `GP_LIGHT_003`: "Scene lighting gradually brightens revealing more details"
- `GP_LIGHT_004`: "Lighting shifts from warm sunset tones to cool blue evening"

### 3.4 Prompt Performance Tracking

Track performance metrics for each prompt:
- Average CLIP Score across test runs
- Average Temporal Consistency
- Success rate (% of generations meeting criteria)
- Common failure modes
- Best-performing model versions
- Input image requirements

---

## 4. Regression Test Automation

### 4.1 Pytest Fixtures

#### Core Fixtures (`tests/fixtures/video_generation_fixtures.py`)

```python
@pytest.fixture(scope="session")
def golden_set_manager(tmp_path_factory):
    """Provides golden set manager for test session"""
    golden_path = tmp_path_factory.mktemp("golden_set")
    return GoldenSetManager(str(golden_path))

@pytest.fixture(scope="session")
def scenario_library():
    """Provides test scenario library"""
    return TestScenarioLibrary()

@pytest.fixture(scope="session")
def metrics_engine():
    """Provides metrics computation engine"""
    return MetricsEngine()

@pytest.fixture(scope="session")
def regression_suite(golden_set_manager, metrics_engine, scenario_library):
    """Provides regression test suite"""
    return RegressionTestSuite(
        golden_set_manager=golden_set_manager,
        metrics_engine=metrics_engine,
        scenario_library=scenario_library
    )

@pytest.fixture
def sample_test_video(tmp_path):
    """Generates a sample test video"""
    video_path = tmp_path / "test_video.mp4"
    # Generate synthetic video for testing
    create_sample_video(str(video_path), frames=60, fps=30)
    return str(video_path)

@pytest.fixture(params=[
    "TS_CHAR_001", "TS_CHAR_004", "TS_CAM_001", 
    "TS_LIGHT_001", "TS_ENV_002"
])
def scenario_id(request):
    """Parametrized fixture for testing multiple scenarios"""
    return request.param

@pytest.fixture
def test_config():
    """Provides test configuration"""
    return {
        "test_version": "v1.0.0",
        "baseline_version": "v0.9.0",
        "degradation_threshold": 0.05,
        "max_latency_ms": 5000.0
    }
```

#### Video Generation Fixtures

```python
@pytest.fixture
def video_generator_mock():
    """Mock video generator for testing"""
    def generate(prompt: str, **kwargs):
        # Return mock video path
        return "mock_output.mp4"
    return generate

@pytest.fixture
def golden_reference_videos(golden_set_manager, scenario_library):
    """Loads golden reference videos for all scenarios"""
    references = {}
    for scenario_id in scenario_library.scenarios.keys():
        ref = golden_set_manager.get_latest_reference(
            scenario_id=scenario_id,
            expert_approved_only=True
        )
        if ref:
            references[scenario_id] = ref
    return references
```

### 4.2 Test Suite Structure

```
tests/
├── integration/
│   ├── test_regression_suite.py
│   ├── test_golden_set_validation.py
│   └── test_multi_scene_continuity.py
├── metrics/
│   ├── test_temporal_metrics.py
│   ├── test_clip_scoring.py
│   └── test_perceptual_quality.py
├── scenarios/
│   ├── test_portrait_scenes.py
│   ├── test_landscape_scenes.py
│   ├── test_multi_character_scenes.py
│   └── test_edge_cases.py
└── fixtures/
    ├── video_generation_fixtures.py
    └── data_fixtures.py
```

### 4.3 CI Trigger Configuration

#### GitHub Actions Workflow (`.github/workflows/video_regression.yml`)

```yaml
name: Video Generation Regression Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

env:
  TEST_VERSION: ${{ github.sha }}
  BASELINE_VERSION: main
  GOLDEN_SET_PATH: data/golden_set
  OUTPUT_DIR: ci_reports

jobs:
  regression_tests:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-cv.txt
      
      - name: Download Golden Set
        run: |
          # Download from artifact storage or S3
          python scripts/download_golden_set.py
      
      - name: Run Regression Tests
        run: |
          python -m src.evaluation.ci_integration \
            --test-videos test_videos_manifest.json \
            --test-version ${{ github.sha }} \
            --baseline-version $BASELINE_VERSION \
            --output-dir $OUTPUT_DIR
      
      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: regression-reports
          path: ci_reports/
      
      - name: Comment PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const summary = fs.readFileSync('ci_reports/github_summary.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });
      
      - name: Fail on Regression
        run: |
          if [ -f ci_reports/ci_results.json ]; then
            status=$(jq -r '.status' ci_reports/ci_results.json)
            if [ "$status" != "PASS" ]; then
              exit 1
            fi
          fi
```

### 4.4 Comparison Thresholds

#### Global Thresholds
```python
GLOBAL_THRESHOLDS = {
    "temporal_consistency": {
        "min_score": 0.85,
        "degradation_threshold": 0.05,  # 5% drop allowed
        "critical_threshold": 0.75      # Below this = critical failure
    },
    "clip_similarity": {
        "min_score": 0.80,
        "degradation_threshold": 0.05,
        "critical_threshold": 0.70
    },
    "ssim": {
        "min_score": 0.75,
        "degradation_threshold": 0.05,
        "critical_threshold": 0.65
    },
    "perceptual_quality": {
        "min_score": 0.80,
        "degradation_threshold": 0.05,
        "critical_threshold": 0.70
    }
}
```

#### Scenario-Specific Overrides
```python
SCENARIO_THRESHOLDS = {
    "TS_CHAR_004": {  # Subtle facial expression
        "temporal_consistency": 0.92,
        "perceptual_quality": 0.88
    },
    "TS_MULTI_001": {  # Multi-scene continuity
        "character_consistency": 0.95,
        "lighting_consistency": 0.82
    }
}
```

#### Performance Thresholds
```python
PERFORMANCE_THRESHOLDS = {
    "max_latency_ms": 5000.0,
    "latency_regression_threshold": 0.10,  # 10% slowdown allowed
    "min_throughput_fps": 1.0,
    "memory_limit_gb": 16.0
}
```

---

## 5. Storage Format for Golden Outputs

### 5.1 Directory Structure

```
data/golden_set/
├── metadata.json                    # Master metadata file
├── videos/                          # Golden reference videos
│   ├── REF_TS_CHAR_001_v1.0.0_*.mp4
│   ├── REF_TS_CHAR_004_v1.0.0_*.mp4
│   └── ...
├── frames/                          # Extracted key frames
│   ├── REF_TS_CHAR_001_v1.0.0/
│   │   ├── frame_0000.png
│   │   ├── frame_0015.png
│   │   └── ...
│   └── ...
├── embeddings/                      # CLIP and visual embeddings
│   ├── REF_TS_CHAR_001_v1.0.0.npy
│   └── ...
├── hashes/                          # Checksums and frame hashes
│   ├── REF_TS_CHAR_001_v1.0.0.json
│   └── ...
└── metrics/                         # Pre-computed metric results
    ├── REF_TS_CHAR_001_v1.0.0.json
    └── ...
```

### 5.2 Metadata Schema

#### Master Metadata (`metadata.json`)

```json
{
  "version": "1.0.0",
  "updated_at": "2024-01-15T10:30:00Z",
  "total_references": 24,
  "schema_version": "1.0",
  "references": {
    "REF_TS_CHAR_001_v1.0.0_20240115_103000": {
      "reference_id": "REF_TS_CHAR_001_v1.0.0_20240115_103000",
      "scenario_id": "TS_CHAR_001",
      "video_path": "videos/REF_TS_CHAR_001_v1.0.0_20240115_103000.mp4",
      "model_version": "v1.0.0",
      "created_at": "2024-01-15T10:30:00Z",
      "video_hash": "sha256:abc123...",
      "frame_hashes": ["sha256:frame1...", "sha256:frame2..."],
      "duration_frames": 60,
      "resolution": [1920, 1080],
      "fps": 30.0,
      "file_size_bytes": 5242880,
      "expert_approved": true,
      "approval_date": "2024-01-15T12:00:00Z",
      "approver": "senior_engineer@example.com",
      "notes": "Baseline reference for v1.0.0 release"
    }
  }
}
```

#### Individual Reference Metadata

```json
{
  "reference_id": "REF_TS_CHAR_001_v1.0.0_20240115_103000",
  "scenario": {
    "scenario_id": "TS_CHAR_001",
    "name": "Natural Walking - Forward",
    "prompt": "Person walks naturally forward with steady, confident gait",
    "difficulty": "basic",
    "movement_type": "character_walk"
  },
  "video": {
    "path": "videos/REF_TS_CHAR_001_v1.0.0_20240115_103000.mp4",
    "hash": "sha256:abc123...",
    "duration_frames": 60,
    "duration_seconds": 2.0,
    "resolution": [1920, 1080],
    "fps": 30.0,
    "codec": "h264",
    "bitrate_kbps": 5000,
    "file_size_bytes": 5242880
  },
  "frames": {
    "extraction_method": "uniform",
    "sample_rate": 15,
    "total_extracted": 4,
    "frame_hashes": {
      "0": "sha256:frame0...",
      "15": "sha256:frame15...",
      "30": "sha256:frame30...",
      "45": "sha256:frame45..."
    },
    "frame_paths": [
      "frames/REF_TS_CHAR_001_v1.0.0/frame_0000.png",
      "frames/REF_TS_CHAR_001_v1.0.0/frame_0015.png"
    ]
  },
  "embeddings": {
    "clip_embeddings": {
      "path": "embeddings/REF_TS_CHAR_001_v1.0.0_clip.npy",
      "shape": [4, 512],
      "model": "openai/clip-vit-base-patch32"
    },
    "semantic_embedding": {
      "path": "embeddings/REF_TS_CHAR_001_v1.0.0_semantic.npy",
      "shape": [768],
      "model": "sentence-transformers/all-mpnet-base-v2"
    }
  },
  "metrics": {
    "temporal_consistency": {
      "score": 0.89,
      "passed": true,
      "threshold": 0.88,
      "details": {
        "mean": 0.89,
        "std": 0.03,
        "min": 0.84,
        "max": 0.94
      }
    },
    "ssim": {
      "score": 0.82,
      "passed": true,
      "threshold": 0.80
    },
    "perceptual_quality": {
      "score": 0.85,
      "passed": true,
      "threshold": 0.80,
      "details": {
        "sharpness": 234.5,
        "contrast": 45.2
      }
    },
    "clip_similarity": {
      "score": 0.87,
      "passed": true,
      "threshold": 0.80
    }
  },
  "generation": {
    "model_version": "v1.0.0",
    "model_name": "video-gen-model",
    "generation_config": {
      "num_inference_steps": 50,
      "guidance_scale": 7.5,
      "seed": 42
    },
    "latency_ms": 3845,
    "throughput_fps": 15.6
  },
  "validation": {
    "expert_approved": true,
    "approval_date": "2024-01-15T12:00:00Z",
    "approver": "senior_engineer@example.com",
    "validation_criteria_met": [
      "temporal_consistency",
      "ssim",
      "perceptual_quality",
      "clip_similarity"
    ],
    "notes": "Excellent gait animation, natural motion"
  },
  "tags": ["character", "locomotion", "basic", "approved"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### 5.3 Video Storage Specifications

#### Format Requirements
- **Container**: MP4 (H.264 video, AAC audio optional)
- **Resolution**: 1920x1080 (1080p) or 1280x720 (720p)
- **Frame Rate**: 30 FPS
- **Bitrate**: 5000-8000 kbps (constant or variable)
- **Color Space**: sRGB, 8-bit per channel
- **Pixel Format**: YUV420p

#### Naming Convention
```
REF_{scenario_id}_{model_version}_{timestamp}.mp4
```

Example: `REF_TS_CHAR_001_v1.0.0_20240115_103000.mp4`

### 5.4 Frame Extraction Specifications

#### Extraction Strategy
- **Method**: Uniform sampling
- **Sample Rate**: Every 15 frames (0.5s intervals @ 30fps)
- **Format**: PNG (lossless)
- **Resolution**: Match source video
- **Color Space**: RGB

#### Frame Naming Convention
```
frame_{frame_number:04d}.png
```

Example: `frame_0000.png`, `frame_0015.png`, `frame_0030.png`

### 5.5 Embedding Storage

#### CLIP Embeddings
- **Format**: NumPy binary (.npy)
- **Dimensions**: [num_frames, 512] or [num_frames, 768]
- **Model**: OpenAI CLIP or similar
- **Normalization**: L2-normalized

#### Semantic Embeddings
- **Format**: NumPy binary (.npy)
- **Dimensions**: [768] (average pooling across frames)
- **Model**: Sentence-transformers or similar

### 5.6 Hash Storage

#### Video Hash
- **Algorithm**: SHA-256
- **Input**: Raw video bytes
- **Format**: Hexadecimal string (64 characters)

#### Frame Hashes
- **Algorithm**: SHA-256
- **Input**: Raw frame pixels (PNG bytes)
- **Format**: JSON object mapping frame indices to hashes

```json
{
  "algorithm": "sha256",
  "frame_hashes": {
    "0": "abc123...",
    "15": "def456...",
    "30": "ghi789..."
  }
}
```

### 5.7 Backup and Versioning

#### Backup Strategy
- **Frequency**: Daily incremental, weekly full backup
- **Storage**: Cloud object storage (S3, GCS, Azure Blob)
- **Retention**: 90 days for incremental, 1 year for full backups
- **Encryption**: AES-256 at rest

#### Versioning
- Use git-LFS for large files
- Track metadata.json in git
- Store videos and embeddings in versioned object storage
- Maintain version manifest linking git commits to storage versions

---

## 6. Test Execution Workflow

### 6.1 Manual Test Execution

```bash
# Run all regression tests
pytest tests/integration/test_regression_suite.py -v

# Run specific scenario
pytest tests/scenarios/test_portrait_scenes.py::test_facial_expression -v

# Run with coverage
pytest tests/ --cov=src.evaluation --cov-report=html

# Run performance benchmarks
pytest tests/integration/test_performance_benchmarks.py -v --benchmark
```

### 6.2 Automated CI Execution

```bash
# Trigger via CLI
python -m src.evaluation.ci_integration \
  --test-videos test_videos_manifest.json \
  --test-version v1.1.0 \
  --baseline-version v1.0.0 \
  --output-dir ci_reports

# With specific scenarios
python -m src.evaluation.ci_integration \
  --test-videos test_videos_manifest.json \
  --test-version v1.1.0 \
  --scenarios TS_CHAR_001 TS_CHAR_004 TS_CAM_001
```

### 6.3 Golden Set Management

```bash
# Add new golden reference
python scripts/add_golden_reference.py \
  --scenario TS_CHAR_001 \
  --video path/to/video.mp4 \
  --model-version v1.0.0 \
  --approver email@example.com

# Validate existing reference
python scripts/validate_golden_reference.py \
  --reference-id REF_TS_CHAR_001_v1.0.0_20240115

# Export golden set summary
python scripts/export_golden_summary.py \
  --output reports/golden_set_summary.json
```

---

## 7. Continuous Improvement

### 7.1 Metrics Evolution
- Track metric trends over time
- Identify scenarios with high variance
- Adjust thresholds based on model capabilities
- Add new metrics as evaluation science advances

### 7.2 Golden Set Maintenance
- Review golden references quarterly
- Update references when new model versions show significant improvement
- Archive outdated references with metadata preservation
- Expand coverage for edge cases and failure modes

### 7.3 Prompt Library Updates
- Incorporate community-contributed prompts
- A/B test prompt variations
- Document prompt engineering best practices
- Version control prompt templates

---

## 8. References and Resources

### 8.1 Related Documentation
- `EVALUATION_SYSTEM_MANIFEST.md` - System architecture
- `src/evaluation/test_scenarios.py` - Scenario implementations
- `src/evaluation/metrics.py` - Metrics computation
- `tests/test_evaluation_system.py` - Test suite

### 8.2 External Standards
- CLIP: Contrastive Language-Image Pre-training
- SSIM: Structural Similarity Index Measure
- FVD: Fréchet Video Distance
- Perceptual Quality Metrics (LPIPS, DISTS)

---

**Document Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Authors**: Video Generation Testing Team  
**Status**: Active
