# Video Prompt Compiler Documentation

## Overview

The Enhanced Video Prompt Compiler transforms director intent into model-specific video generation prompts with advanced control parameters, versioning, and cinematic rule integration.

## Features

### 1. Video-Specific Control Parameters

Fine-grained control over video generation:

```python
from src.generators.video_prompt_generator import VideoControlParameters, CameraMotion

controls = VideoControlParameters(
    camera_motion=CameraMotion(
        type="dolly",           # static, pan, tilt, zoom, dolly, orbit, crane
        speed="slow",           # slow, medium, fast
        direction="in",         # left, right, up, down, in, out
        focal_length=50         # mm
    ),
    duration_seconds=8.0,       # 0-60 seconds
    fps=24,                     # 24, 25, 30, 60
    shot_type="medium",         # wide, medium, close-up, extreme_close-up, establishing
    transitions="fade",         # fade, cut, dissolve, wipe, cross_dissolve
    motion_strength=0.5         # 0.0-1.0
)
```

### 2. Determinism Controls

Reproducible generation with seed management:

```python
from src.generators.video_prompt_generator import DeterminismConfig

# Strategy 1: Fixed seed
determinism = DeterminismConfig(
    seed=42,
    enable_seed_management=True
)

# Strategy 2: Incremental seeds for multi-scene
determinism = DeterminismConfig(
    seed=1000,
    seed_increment_per_scene=100  # Scene 1: 1000, Scene 2: 1100, Scene 3: 1200
)

# Strategy 3: Hash-based seed from prompt
determinism = DeterminismConfig(
    use_hash_based_seed=True  # Generates consistent seed from prompt text
)
```

### 3. Versioning System

Track prompt versions and schema evolution:

```python
# Automatically included in compiled prompts
{
    "version": {
        "prompt_version": "1.0.0",      # Individual prompt version
        "schema_version": "2.0.0",      # Compiler schema version
        "generator_version": "2.0.0",   # Generator version
        "created_at": "2025-01-28T...", # ISO timestamp
        "model_type": "kling"           # Target model
    }
}
```

### 4. Cinematic Rules Integration

Automatically applies 47+ cinematic rules from `movement_prediction_rules.json`:

- **Character Action Rules**: Pose-to-Action Continuation, Emotional Momentum, Interaction Anticipation
- **Camera Movement Rules**: Composition-Guided Flow, Depth Layer Parallax, Emotional Framing
- **Environment Rules**: Physics-Based Motion, Atmospheric Response

```python
compiled = compiler.compile_video_prompt(request)

print(f"Rules Applied: {compiled.cinematic_rules.total_rules_applied}")
print(f"Rule IDs: {compiled.cinematic_rules.rule_ids}")
print(f"Enhancements: {compiled.cinematic_rules.enhancements}")
```

## Usage

### Basic Compilation

```python
from src.generators.video_prompt_generator import (
    VideoPromptCompiler,
    VideoGenerationRequest,
    ModelType
)

compiler = VideoPromptCompiler()

request = VideoGenerationRequest(
    model_type=ModelType.KLING,
    scene_description="A young woman walks through a misty forest at golden hour",
    duration=8.0,
    style="cinematic",
    temporal_consistency_priority="high"
)

compiled = compiler.compile_video_prompt(request)
print(compiled.prompt_text)
```

### Full Control

```python
from src.generators.video_prompt_generator import (
    VideoPromptCompiler,
    VideoGenerationRequest,
    VideoControlParameters,
    DeterminismConfig,
    CameraMotion,
    ModelType
)

compiler = VideoPromptCompiler()

# Define precise controls
controls = VideoControlParameters(
    camera_motion=CameraMotion(type="dolly", speed="slow", direction="in"),
    duration_seconds=10.0,
    fps=24,
    shot_type="medium",
    motion_strength=0.4
)

determinism = DeterminismConfig(seed=12345)

request = VideoGenerationRequest(
    model_type=ModelType.SORA2,
    scene_description="A warrior stands on a cliff at sunrise",
    control_parameters=controls,
    determinism_config=determinism
)

compiled = compiler.compile_video_prompt(request)
parameters = compiler.compile_model_parameters(compiled)
```

### Multi-Scene Compilation

```python
scenes = [
    "A warrior stands on a cliff",
    "The warrior draws their sword",
    "The warrior charges into battle"
]

shared_config = VideoGenerationRequest(
    model_type=ModelType.RUNWAY,
    scene_description="",
    duration=6.0,
    determinism_config=DeterminismConfig(seed=1000, seed_increment_per_scene=100)
)

result = compiler.compile_multi_scene_prompts(scenes, ModelType.RUNWAY, shared_config)

print(f"Total Scenes: {result['total_scenes']}")
print(f"Consistency: {result['consistency_analysis']}")
```

### Export Compiled Prompt

```python
compiled = compiler.compile_video_prompt(request)

# Export to dictionary (can be saved as JSON)
exported = compiled.to_dict()

# Contains:
# - prompt_text
# - model_type
# - control_parameters
# - determinism config
# - version info
# - cinematic_rules applied
# - temporal_config
# - metadata

import json
with open('compiled_prompt.json', 'w') as f:
    json.dump(exported, f, indent=2)
```

## API Reference

### VideoPromptCompiler

Main compiler class for video prompt generation.

#### Methods

**`compile_video_prompt(request, scene_index=0) -> CompiledPrompt`**

Compiles a complete video prompt from director intent.

**Parameters:**
- `request`: `VideoGenerationRequest` - The generation request
- `scene_index`: `int` - Scene index for multi-scene seed management

**Returns:** `CompiledPrompt` with all metadata

---

**`compile_model_parameters(compiled_prompt) -> Dict[str, Any]`**

Generates model-specific parameters from compiled prompt.

**Parameters:**
- `compiled_prompt`: `CompiledPrompt` - The compiled prompt

**Returns:** Dictionary of model parameters

---

**`compile_multi_scene_prompts(scenes, model_type, shared_config) -> Dict[str, Any]`**

Compiles multiple scenes with coherence.

**Parameters:**
- `scenes`: `List[str]` - List of scene descriptions
- `model_type`: `ModelType` - Target model
- `shared_config`: `VideoGenerationRequest` - Shared configuration

**Returns:** Multi-scene compilation result

### VideoControlParameters

Video-specific control parameters.

**Fields:**
- `camera_motion`: `CameraMotion` - Camera movement configuration
- `duration_seconds`: `float` - Video duration (0-60s)
- `fps`: `int` - Frame rate (24, 25, 30, 60)
- `shot_type`: `str` - Shot framing type
- `transitions`: `Optional[str]` - Transition type
- `motion_strength`: `float` - Motion intensity (0.0-1.0)

**Methods:**
- `validate() -> Tuple[bool, List[str]]` - Validate parameters
- `to_dict() -> Dict[str, Any]` - Export to dictionary

### DeterminismConfig

Configuration for reproducible generation.

**Fields:**
- `seed`: `Optional[int]` - Fixed seed value
- `enable_seed_management`: `bool` - Enable seed management
- `seed_increment_per_scene`: `int` - Increment for multi-scene
- `use_hash_based_seed`: `bool` - Generate from prompt hash
- `seed_hash_source`: `Optional[str]` - Custom hash source

**Methods:**
- `generate_seed(scene_index, prompt_text) -> int` - Generate seed

### CompiledPrompt

Fully compiled prompt with all metadata.

**Fields:**
- `prompt_text`: `str` - Final prompt text
- `model_type`: `ModelType` - Target model
- `control_parameters`: `VideoControlParameters` - Controls
- `determinism_config`: `DeterminismConfig` - Determinism settings
- `version`: `PromptVersion` - Version information
- `cinematic_rules`: `CinematicRuleApplication` - Applied rules
- `temporal_config`: `TemporalConsistencyConfig` - Temporal settings
- `metadata`: `Dict[str, Any]` - Additional metadata

**Methods:**
- `to_dict() -> Dict[str, Any]` - Export complete structure

## Cinematic Rules

The compiler integrates 47+ cinematic rules from `movement_prediction_rules.json`:

### Character Action (8 rules)
- movement_001: Pose-to-Action Continuation
- movement_004: Emotional Momentum Analysis
- movement_007: Interaction Anticipation

### Camera Movement (8 rules)
- movement_002: Composition-Guided Camera Flow
- movement_005: Depth Layer Parallax
- movement_008: Emotional Framing Progression

### Environment Animation (8 rules)
- movement_003: Physics-Based Environmental Motion
- movement_006: Atmospheric Response System

Rules are automatically selected based on:
- Camera motion type
- Shot type
- Scene content
- Director intent

## Temporal Consistency

Temporal consistency priority levels:

| Priority | Temporal Weight | Motion Strength | Frame Rate | Guidance Scale |
|----------|----------------|-----------------|------------|----------------|
| low      | 0.5            | 0.7             | 24 fps     | 7.0            |
| medium   | 0.7            | 0.5             | 30 fps     | 7.5            |
| high     | 0.85           | 0.4             | 30 fps     | 8.0            |
| critical | 0.95           | 0.3             | 60 fps     | 9.0            |

## Model Support

Supports 12+ AI video models:
- KLING (Kwai)
- WAN AI
- Runway Gen-3
- LTX / LTX2
- Sora 2 (OpenAI)
- Veo 3 / 3.1 (Google)
- Higgsfield
- Luma Dream Machine
- Pika Labs
- Stable Video Diffusion

Each model receives optimized prompts and parameters.

## Backward Compatibility

Legacy `VideoPromptGenerator` class maintained for backward compatibility:

```python
from src.generators.video_prompt_generator import VideoPromptGenerator

generator = VideoPromptGenerator()

# Legacy methods still work
prompt = generator.generate_prompt(request)
params = generator.generate_model_parameters(request)
multi = generator.generate_multi_scene_prompts(scenes, model_type)
```

## Examples

See `examples/video_prompt_compiler_example.py` for comprehensive examples:

1. Basic compilation with automatic inference
2. Full control with explicit parameters
3. Multi-scene compilation with coherence
4. Determinism strategies
5. Cinematic rules integration
6. Export/import compiled prompts
7. Model-specific compilation

## Testing

Run comprehensive tests:

```bash
python -m pytest tests/test_video_prompt_analyzer.py -v
```

Test coverage includes:
- Video control parameters validation
- Determinism seed generation (fixed, incremental, hash-based)
- Prompt version tracking
- Cinematic rules application
- Multi-scene coherence
- Model-specific compilation
- Backward compatibility

## Best Practices

1. **Use explicit controls for precision**: Define `VideoControlParameters` for critical shots
2. **Enable seed management**: Use `DeterminismConfig` for reproducible results
3. **Multi-scene coherence**: Use shared config with incremental seeds
4. **Export compiled prompts**: Save full metadata for future reference
5. **Monitor rules applied**: Check `cinematic_rules.total_rules_applied` for quality
6. **Validate parameters**: Call `validate()` before compilation
7. **Model-specific optimization**: Let compiler optimize per model

## Architecture

```
Director Intent
      ↓
Parse Intent → Components
      ↓
Infer Controls → Camera, Shot Type, Motion
      ↓
Apply Cinematic Rules → 47+ Rules
      ↓
Generate Temporal Config → Consistency Settings
      ↓
Compile Model Prompt → Model-Specific Format
      ↓
CompiledPrompt (with versioning, metadata)
```

## Future Enhancements

Planned features:
- Custom rule definition API
- ML-based intent parsing
- Real-time preview generation
- Advanced multi-scene transitions
- Audio-visual synchronization
- Interactive parameter tuning
