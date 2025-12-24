# Prompt Compiler & Control Map System

## Overview

The Prompt Compiler is a sophisticated system that transforms high-level Director Intent into model-specific prompts with comprehensive control parameters. It bridges the gap between creative vision and technical execution across multiple video generation platforms.

## Key Features

### 🎬 Director Intent → Model Prompts
- Compile high-level creative specifications into platform-specific prompts
- Support for Runway Gen-3, Pika, Sora, Veo, and Flux
- Automatic parameter translation and optimization

### 📹 Camera Motion Control
- 19 camera motion types (pan, tilt, dolly, crane, zoom, etc.)
- Configurable strength, speed, and easing
- Temporal range control (start/end times)

### 👤 Character Consistency
- Maintain appearance across shots and scenes
- Feature-specific weighting (face, body, clothing, hair)
- Reference frame linking
- Expression range control

### 🗺️ Control Maps
- Depth maps for spatial guidance
- Pose maps for character animation
- Edge detection for composition
- Semantic segmentation
- Support for multiple preprocessors

### 🎯 Deterministic Generation
- Seed management for reproducibility
- Per-shot and global seed control
- Seed manifest export/import
- Multiple reproducibility levels

### 🎞️ Multi-Scene Production
- Scene-based organization
- Shot list compilation
- Transition specifications
- Storyboard integration

### 📊 Control Vocabulary
- Standardized control parameters
- Validation and type checking
- Cross-platform compatibility
- Extensible design

## Quick Start

### Basic Usage

```python
from core.prompt_expander import (
    PromptExpander,
    DirectorIntent,
    Scene,
    Shot,
    CameraMotion,
    CameraMotionType,
    MotionStrength
)

# Initialize compiler
expander = PromptExpander()

# Define a shot
shot = Shot(
    shot_id="shot_001",
    scene_id="scene_001",
    prompt="Wide establishing shot of futuristic city at sunset",
    camera_motion=CameraMotion(
        motion_type=CameraMotionType.DOLLY_IN,
        strength=MotionStrength.MODERATE,
        speed=0.8
    ),
    fps=24,
    duration=8.0
)

# Create a scene
scene = Scene(
    scene_id="scene_001",
    description="Opening establishing sequence",
    shots=[shot]
)

# Define director intent
intent = DirectorIntent(
    intent_id="my_film",
    narrative_description="A sci-fi epic about humanity's future",
    visual_theme="neo-noir cyberpunk",
    target_providers=["runway", "pika", "sora"],
    scenes=[scene]
)

# Compile!
result = expander.compile_director_intent(intent)

# Access model-specific prompts
for prompt in result.model_prompts:
    print(f"{prompt.provider}: {prompt.compiled_prompt}")
    print(f"Controls: {prompt.control_parameters}")
```

## Control Vocabulary

### Camera Motion Types

| Type | Description |
|------|-------------|
| `STATIC` | No camera movement |
| `PAN_LEFT` / `PAN_RIGHT` | Horizontal rotation |
| `TILT_UP` / `TILT_DOWN` | Vertical rotation |
| `DOLLY_IN` / `DOLLY_OUT` | Move camera closer/farther |
| `TRACK_LEFT` / `TRACK_RIGHT` | Move camera laterally |
| `CRANE_UP` / `CRANE_DOWN` | Vertical movement |
| `ZOOM_IN` / `ZOOM_OUT` | Optical zoom |
| `ORBIT_CLOCKWISE` / `ORBIT_COUNTER_CLOCKWISE` | Circular movement |
| `HANDHELD` | Handheld camera style |
| `STEADICAM` | Smooth tracking shot |
| `PUSH_IN` / `PULL_OUT` | Forward/backward movement |

### Motion Strength Levels

| Level | Description | Runway | Pika |
|-------|-------------|--------|------|
| `NONE` | Static/minimal | 0 | 0.0 |
| `SUBTLE` | Barely noticeable | 3 | 0.25 |
| `MODERATE` | Natural motion | 5 | 0.5 |
| `STRONG` | Prominent motion | 8 | 0.75 |
| `EXTREME` | Maximum motion | 10 | 1.0 |

### Supported FPS Values

`12, 15, 24, 25, 30, 48, 50, 60, 120`

### Transition Types

`CUT, FADE, DISSOLVE, WIPE, MATCH_CUT, JUMP_CUT, SMASH_CUT, CROSSFADE`

## Advanced Features

### Character Consistency

```python
from core.prompt_expander import CharacterConsistency, ReferenceFrame

# Define character
character = CharacterConsistency(
    character_id="protagonist",
    reference_frames=[0, 10, 20],
    feature_weights={
        "face": 1.0,
        "body": 0.9,
        "clothing": 0.95,
        "hair": 0.85
    },
    appearance_locked=True,
    expression_range=("neutral", "determined")
)

# Add reference frame
ref_frame = ReferenceFrame(
    frame_id="ref_001",
    timestamp=0.0,
    image_path="/path/to/reference.jpg",
    weight=1.0,
    aspect="full"
)

# Use in shot
shot = Shot(
    shot_id="shot_001",
    scene_id="scene_001",
    prompt="Hero enters the room",
    characters=[character],
    reference_frames=[ref_frame],
    fps=24,
    duration=5.0
)
```

### Control Maps

```python
from core.prompt_expander import ControlMap

# Depth map for spatial control
depth_map = ControlMap(
    map_type="depth",
    map_data="/path/to/depth_map.png",
    strength=0.8,
    start_frame=0,
    end_frame=120,
    preprocessor="depth_midas",
    conditioning_scale=1.0
)

# Pose map for character animation
pose_map = ControlMap(
    map_type="pose",
    map_data="/path/to/pose_sequence.json",
    strength=1.0,
    preprocessor="openpose"
)

shot = Shot(
    shot_id="shot_001",
    scene_id="scene_001",
    prompt="Dancer performs choreography",
    control_maps=[depth_map, pose_map],
    fps=30,
    duration=4.0
)
```

### Deterministic Seeds

```python
from core.prompt_expander import DeterminismConfig

# Global determinism for entire project
determinism = DeterminismConfig(
    use_fixed_seed=True,
    seed=42,
    reproducibility_level="high"
)

intent = DirectorIntent(
    intent_id="reproducible_project",
    narrative_description="Test",
    target_providers=["runway"],
    scenes=[scene],
    global_determinism=determinism
)

result = expander.compile_director_intent(intent)

# Export seed manifest for later reproduction
seed_manifest = result.seed_manifest
# Save: {"scene:scene_001:shot:shot_001": 1234567890, ...}
```

### Multi-Scene with Transitions

```python
from core.prompt_expander import ShotTransition, TransitionType

# Create shots
shot1 = Shot(shot_id="s1_001", scene_id="scene_001", 
             prompt="Opening wide shot", fps=24, duration=5.0)
shot2 = Shot(shot_id="s1_002", scene_id="scene_001",
             prompt="Close-up reaction", fps=24, duration=3.0)

# Define transition
transition = ShotTransition(
    from_shot="s1_001",
    to_shot="s1_002",
    transition_type=TransitionType.DISSOLVE,
    duration=1.0
)

# Create scene with transitions
scene = Scene(
    scene_id="scene_001",
    description="Opening scene",
    shots=[shot1, shot2],
    transitions=[transition]
)
```

### Storyboard Integration

```python
from core.prompt_expander import Storyboard

# Create storyboard panels
storyboard = Storyboard(
    panel_id="panel_001",
    shot_number="1A",
    description="Hero stands on cliff overlooking valley",
    camera_angle="low angle",
    composition="rule of thirds, hero on right",
    duration=3.0,
    reference_image="/path/to/storyboard.jpg"
)

# Reference in shot
shot = Shot(
    shot_id="shot_001",
    scene_id="scene_001",
    prompt="Cliff overlook shot",
    storyboard_ref="panel_001",
    fps=24,
    duration=3.0
)

# Include in intent
intent = DirectorIntent(
    intent_id="with_storyboard",
    narrative_description="Epic adventure",
    target_providers=["runway", "flux"],
    scenes=[scene],
    storyboards=[storyboard]
)
```

## Model-Specific Output

### Runway Gen-3

```python
{
    "provider": "runway",
    "model": "gen3",
    "compiled_prompt": "Wide establishing shot of...",
    "control_parameters": {
        "duration": 8.0,
        "fps": 24,
        "motion_amount": 5,
        "camera_motion": {
            "type": "dolly_in",
            "speed": 0.8,
            "strength": "moderate"
        },
        "seed": 42
    }
}
```

### Pika 1.5

```python
{
    "provider": "pika",
    "model": "pika-1.5",
    "compiled_prompt": "...",
    "control_parameters": {
        "fps": 24,
        "motion": 0.5,
        "camera": {
            "pan": 0.0,
            "tilt": 0.0,
            "zoom": 1.0
        },
        "seed": 42
    }
}
```

## Seed Management

### Deterministic Seed Generation

Seeds are generated deterministically from context using SHA-256:

```python
from core.prompt_expander import SeedManager

manager = SeedManager(base_seed=42)

# Generate seeds
seed1 = manager.generate_seed("scene_001:shot_001")
seed2 = manager.generate_seed("scene_001:shot_002")

# Export manifest
manifest = manager.export_manifest()

# Later, import to reproduce
new_manager = SeedManager()
new_manager.import_manifest(manifest)
```

### Seed Context Format

```
scene:<scene_id>:shot:<shot_id>
storyboard:<panel_id>
character:<character_id>
```

## Validation

The system validates:
- Shot duration > 0
- FPS in supported list
- Motion strength valid enum
- Camera motion types valid
- Seeds < 2^31
- Feature weights 0.0-1.0
- Control map parameters in range

## Best Practices

1. **Use versioning**: Always specify `prompt_version` and `schema_version`
2. **Seed manifests**: Export and save for production reproducibility
3. **Character scope**: Define characters at scene level for multi-shot consistency
4. **Control map quality**: Use high-quality inputs for best results
5. **FPS matching**: Match target platform requirements
6. **Motion testing**: Start with "moderate" strength and adjust
7. **Transition timing**: Include in total duration calculations
8. **Reference quality**: Use high-resolution references

## Examples

See `examples/prompt_expander_usage.py` for comprehensive examples including:
- Simple prompt compilation
- Multi-scene production
- Character consistency
- Control maps
- Deterministic generation
- Storyboard integration

## API Documentation

Full API reference: [docs/api/prompt_compiler_schema.md](api/prompt_compiler_schema.md)

## Testing

Run tests:
```bash
pytest src/tests/test_prompt_expander.py -v
```

## Integration

The Prompt Compiler integrates with:
- **Model Adapters**: Automatic provider-specific translation
- **Shot List Compiler**: Scene and shot organization
- **Temporal Control**: Keyframe-based animation
- **Identity Preservation**: Character consistency across shots

## Supported Providers

| Provider | Support Level | Features |
|----------|--------------|----------|
| Runway Gen-3 | Full | Camera motion, duration, FPS, motion amount |
| Pika 1.5 | Full | Camera controls, motion strength |
| OpenAI Sora | Partial | Duration, resolution |
| Google Veo | Partial | Duration, FPS, camera motion |
| Flux | Full | Image generation for storyboards |

## Future Enhancements

- Audio synchronization
- Multi-camera setups
- Real-time preview
- Advanced transition effects
- AI-assisted shot suggestions
- Automatic storyboard generation
- Cloud rendering integration

## Contributing

Contributions welcome! Areas for improvement:
- Additional model adapters
- Enhanced validation
- More control map types
- Better error messages
- Performance optimizations

## License

See main project LICENSE file.
