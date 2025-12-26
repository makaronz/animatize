# Video Prompt Compiler - Quick Reference

## Installation

```bash
# Import required modules
from src.generators.video_prompt_generator import (
    VideoPromptCompiler,
    VideoGenerationRequest,
    VideoControlParameters,
    DeterminismConfig,
    CameraMotion,
    ModelType
)
```

## Quick Start

```python
# 1. Create compiler
compiler = VideoPromptCompiler()

# 2. Create request
request = VideoGenerationRequest(
    model_type=ModelType.KLING,
    scene_description="Your director intent here",
    duration=8.0
)

# 3. Compile
compiled = compiler.compile_video_prompt(request)
print(compiled.prompt_text)
```

## Control Parameters

```python
controls = VideoControlParameters(
    camera_motion=CameraMotion(
        type="dolly",      # static, pan, tilt, zoom, dolly, orbit, crane
        speed="slow",      # slow, medium, fast
        direction="in",    # left, right, up, down, in, out
        focal_length=50
    ),
    duration_seconds=8.0,  # 0-60
    fps=24,                # 24, 25, 30, 60
    shot_type="medium",    # wide, medium, close-up, extreme_close-up
    motion_strength=0.5    # 0.0-1.0
)
```

## Determinism

```python
# Fixed seed
det = DeterminismConfig(seed=42)

# Incremental (multi-scene)
det = DeterminismConfig(seed=1000, seed_increment_per_scene=100)

# Hash-based
det = DeterminismConfig(use_hash_based_seed=True)
```

## Multi-Scene

```python
scenes = ["Scene 1", "Scene 2", "Scene 3"]

result = compiler.compile_multi_scene_prompts(
    scenes,
    ModelType.SORA2,
    shared_config=VideoGenerationRequest(
        model_type=ModelType.SORA2,
        scene_description="",
        duration=6.0,
        determinism_config=DeterminismConfig(seed=1000)
    )
)
```

## Export

```python
compiled = compiler.compile_video_prompt(request)

# Export to dict/JSON
data = compiled.to_dict()

# Access fields
print(data['prompt_text'])
print(data['version'])
print(data['cinematic_rules'])
print(data['control_parameters'])
```

## Models

```python
ModelType.KLING
ModelType.SORA2
ModelType.RUNWAY
ModelType.LUMA
ModelType.VEO3
ModelType.PIKA
# ... and 6 more
```

## Temporal Priority

```python
temporal_consistency_priority="low"      # Relaxed
temporal_consistency_priority="medium"   # Balanced
temporal_consistency_priority="high"     # Strong (default)
temporal_consistency_priority="critical" # Maximum
```

## Common Patterns

### Pattern 1: Basic Scene
```python
compiler = VideoPromptCompiler()
request = VideoGenerationRequest(
    model_type=ModelType.KLING,
    scene_description="A warrior on a cliff",
    duration=5.0
)
compiled = compiler.compile_video_prompt(request)
```

### Pattern 2: Precise Control
```python
controls = VideoControlParameters(
    camera_motion=CameraMotion(type="dolly", speed="slow"),
    fps=24,
    shot_type="wide"
)
request = VideoGenerationRequest(
    model_type=ModelType.SORA2,
    scene_description="Epic battle scene",
    control_parameters=controls,
    determinism_config=DeterminismConfig(seed=12345)
)
compiled = compiler.compile_video_prompt(request)
```

### Pattern 3: Multi-Scene Story
```python
scenes = [
    "Hero enters ancient temple",
    "Discovery of mysterious artifact",
    "Artifact begins to glow"
]
result = compiler.compile_multi_scene_prompts(
    scenes,
    ModelType.RUNWAY,
    shared_config=VideoGenerationRequest(
        model_type=ModelType.RUNWAY,
        scene_description="",
        determinism_config=DeterminismConfig(seed=9999, seed_increment_per_scene=1000)
    )
)
```

## Validation

```python
# Validate controls
controls = VideoControlParameters(...)
is_valid, errors = controls.validate()
if not is_valid:
    print(f"Errors: {errors}")

# Validate temporal config
temporal = TemporalConsistencyConfig(...)
is_valid, errors = temporal.validate()
```

## Accessing Results

```python
compiled = compiler.compile_video_prompt(request)

# Prompt
print(compiled.prompt_text)

# Version
print(compiled.version.schema_version)
print(compiled.version.created_at)

# Rules applied
print(compiled.cinematic_rules.total_rules_applied)
print(compiled.cinematic_rules.rule_names)

# Controls
print(compiled.control_parameters.fps)
print(compiled.control_parameters.shot_type)

# Seed
print(compiled.temporal_config.seed)

# Metadata
print(compiled.metadata)

# Model parameters
params = compiler.compile_model_parameters(compiled)
print(params)
```

## Backward Compatibility

```python
# Old API still works
from src.generators.video_prompt_generator import VideoPromptGenerator

generator = VideoPromptGenerator()
prompt = generator.generate_prompt(request)
params = generator.generate_model_parameters(request)
```

## Camera Types

| Type   | Description              |
|--------|--------------------------|
| static | Fixed camera position    |
| pan    | Horizontal rotation      |
| tilt   | Vertical rotation        |
| zoom   | Focal length change      |
| dolly  | Physical camera movement |
| orbit  | Circular movement        |
| crane  | Vertical movement        |

## Shot Types

| Type              | Description        |
|-------------------|--------------------|
| wide              | Full scene         |
| medium            | Subject + context  |
| close-up          | Subject detail     |
| extreme_close-up  | Intimate detail    |
| establishing      | Scene introduction |

## FPS Options

- **24 fps**: Cinematic standard
- **25 fps**: PAL standard
- **30 fps**: Smooth motion
- **60 fps**: Ultra-smooth (high temporal priority)

## Tips

1. **Start simple**: Use basic compilation first, add controls as needed
2. **Use determinism**: Always set seed for reproducible results
3. **Check rules**: Monitor `cinematic_rules.total_rules_applied`
4. **Export prompts**: Save compiled prompts for reuse
5. **Validate early**: Call `validate()` before compilation
6. **Multi-scene seeds**: Use incremental seeds for consistency
7. **Model-specific**: Let compiler handle model differences

## Examples

See `examples/video_prompt_compiler_example.py` for complete examples.

## Documentation

See `docs/VIDEO_PROMPT_COMPILER.md` for full documentation.

## Tests

```bash
python -m pytest tests/test_video_prompt_analyzer.py -v
```
