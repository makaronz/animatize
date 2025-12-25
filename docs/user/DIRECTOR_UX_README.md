# Director UX Control Surface

Professional-grade control interface for AI video generation that bridges creative intent and technical parameters.

## Overview

The Director UX Control Surface provides two modes of operation:

- **Pro Mode**: Full professional controls for directors and cinematographers
- **Auto Mode**: Simplified 3-input interface for casual users

## Features

✅ **Professional Controls**
- Camera movement types (dolly, track, crane, orbit, etc.)
- Shot types (wide, medium, closeup, etc.)
- Camera angles (eye level, high, low, dutch, etc.)
- Precise timing (duration, fps, speed factors)
- Motion control (strength, blur, subject/camera/background)
- Transitions (cut, fade, dissolve, etc.)

✅ **Dual Modes**
- Pro mode: 30+ parameters for fine control
- Auto mode: 3 inputs → optimized settings

✅ **Iteration Workflow**
- Parameter locking for refinement
- Generation comparison with ratings
- AI-powered refinement suggestions
- Version history tracking

✅ **Style Presets**
- Documentary (naturalistic, observational)
- Commercial (polished, product showcase)
- Art House (atmospheric, contemplative)
- Action (dynamic, high-energy)
- Drama (intimate, emotional)
- Music Video (stylized, creative)

✅ **Intelligent Mapping**
- Converts UX controls to internal parameters
- Adapts to different model APIs (Runway, Pika, Sora, Veo)

## Quick Start

### Pro Mode
```python
from src.core.director_ux import DirectorControls, CameraMovementType, ShotType

# Create controls
controls = DirectorControls(mode="pro")

# Configure camera
controls.camera.movement_type = CameraMovementType.DOLLY
controls.camera.shot_type = ShotType.CLOSEUP
controls.camera.speed = 0.8

# Set timing
controls.timing.duration = 7.0
controls.timing.fps = 30

# Generate parameters
params = controls.to_internal_params()
```

### Auto Mode
```python
from src.core.director_ux import AutoModeAssistant

# Simple 3-input setup
controls = AutoModeAssistant.suggest_controls(
    content_type="product",
    mood="exciting",
    duration=5.0
)

# Ready to generate
params = controls.to_internal_params()
```

### Use Preset
```python
from src.core.director_ux import PresetLibrary, StylePreset

# Load preset
controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)

# Customize if needed
controls.timing.duration = 7.0

# Generate
params = controls.to_internal_params()
```

## Iteration Workflow

```python
from src.core.director_ux import IterationWorkflow, GenerationComparison

# Lock successful parameters
controls.lock_parameter("camera.movement_type", "dolly", "Perfect motion")
controls.lock_parameter("timing.fps", 30, "30fps looks best")

# Create variation
workflow = IterationWorkflow(controls)
variation = workflow.create_variation({
    "camera.speed": 1.0,
    "motion.overall_strength": "strong"
})

# Track results
comparison = GenerationComparison(
    generation_id="gen_001",
    parameters=params,
    rating=4,
    notes="Good but slightly fast"
)
controls.add_comparison(comparison)

# Get best result
best = controls.get_best_generation()
```

## Documentation

### 📚 Full Documentation
- **[Complete Specification](DIRECTOR_UX_SPECIFICATION.md)** - Comprehensive guide with wireframes
- **[Quick Reference](DIRECTOR_UX_QUICK_REFERENCE.md)** - Cheat sheet and common patterns
- **[JSON Schemas](director_ux_schemas.json)** - Data structure definitions

### 💻 Code Examples
- **[Usage Examples](../../examples/director_ux_examples.py)** - 9 complete examples
- **[Test Suite](../../tests/test_director_ux.py)** - Unit and integration tests

### 🎯 Key Concepts
1. **Control Surface** - Professional parameters (camera, timing, motion)
2. **Operating Modes** - Pro vs Auto for different skill levels
3. **Iteration** - Lock, compare, refine workflow
4. **Presets** - Production-ready style configurations
5. **Mapping** - UX → Internal → Model-specific parameters

## Style Presets

| Preset | Camera | Motion | Best For |
|--------|--------|--------|----------|
| **Documentary** | Handheld | Subtle | Reality, interviews |
| **Commercial** | Dolly | Moderate | Products, brands |
| **Art House** | Track | Subtle | Artistic, mood |
| **Action** | Handheld | Extreme | Sports, energy |
| **Drama** | Push | Subtle | Emotion, character |
| **Music Video** | Orbit | Strong | Performance, creative |

## Camera Movement Types

- **Static** - No movement, stable
- **Pan** - Horizontal rotation
- **Tilt** - Vertical rotation
- **Dolly** - Move toward/away from subject
- **Track** - Move parallel to subject
- **Crane** - Vertical movement
- **Zoom** - Lens zoom in/out
- **Orbit** - Circular movement around subject
- **Handheld** - Natural shake
- **Steadicam** - Smooth following motion
- **Push** - Forward movement
- **Pull** - Backward movement

## Shot Types

- **Extreme Wide** - Full environment
- **Wide** - Subject in environment
- **Full** - Full body
- **Medium** - Waist up
- **Closeup** - Face/head
- **Extreme Closeup** - Eyes/detail
- **Over Shoulder** - Behind one subject
- **POV** - Point of view
- **Two Shot** - Two subjects
- **Group Shot** - Multiple subjects

## Parameter Ranges

| Parameter | Range | Default | Unit |
|-----------|-------|---------|------|
| Camera Speed | 0.1 - 5.0 | 1.0 | multiplier |
| Focal Length | 12 - 200 | 50 | mm |
| Duration | 1.0 - 60.0 | 5.0 | seconds |
| FPS | 24, 30, 60, 120 | 24 | frames/sec |
| Motion Strength | 0.0 - 1.0 | 0.5 | normalized |
| Depth of Field | 0.0 - 1.0 | 0.5 | normalized |

## Integration with ANIMAtiZE

```python
from src.core.director_ux import PresetLibrary, StylePreset
from src.core.prompt_expander import PromptCompiler, DirectorIntent, Scene, Shot

# 1. Create director controls
controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
controls.timing.duration = 7.0

# 2. Convert to internal parameters
internal_params = controls.to_internal_params()

# 3. Create shot and scene
shot = Shot(
    shot_id="shot_001",
    scene_id="scene_001",
    prompt="Product showcase",
    fps=internal_params['fps'],
    duration=internal_params['duration']
)

scene = Scene(scene_id="scene_001", shots=[shot])
intent = DirectorIntent(
    intent_id="intent_001",
    target_providers=['runway', 'pika'],
    scenes=[scene]
)

# 4. Compile to model-specific prompts
compiler = PromptCompiler()
result = compiler.compile(intent)

# 5. Ready for generation
for model_prompt in result.model_prompts:
    print(f"Provider: {model_prompt.provider}")
    print(f"Prompt: {model_prompt.compiled_prompt}")
    print(f"Parameters: {model_prompt.control_parameters}")
```

## Common Workflows

### 1. Quick Generation
```python
# One-liner for common use cases
params = PresetLibrary.get_preset(StylePreset.COMMERCIAL).to_internal_params()
```

### 2. Iterate and Refine
```python
# Lock good parameters, vary others
controls.lock_parameter("camera.focal_length", 85)
variation = IterationWorkflow(controls).create_variation({"camera.speed": 0.5})
```

### 3. Auto to Pro Upgrade
```python
# Start simple, upgrade for control
controls = AutoModeAssistant.suggest_controls("product", "calm", 5.0)
controls.mode = "pro"
controls.depth_of_field = 0.3
```

### 4. Batch Comparison
```python
# Test multiple variations
for speed in [0.6, 0.8, 1.0]:
    variation = workflow.create_variation({"camera.speed": speed})
    # Generate and compare...
```

## API Reference

### Core Classes

- **`DirectorControls`** - Main control container
- **`CameraControl`** - Camera parameters
- **`TimingControl`** - Temporal parameters
- **`MotionControl`** - Motion parameters
- **`TransitionControl`** - Transition parameters

### Enums

- **`DirectorMode`** - AUTO, PRO
- **`CameraMovementType`** - STATIC, PAN, DOLLY, etc.
- **`ShotType`** - WIDE, MEDIUM, CLOSEUP, etc.
- **`CameraAngle`** - EYE_LEVEL, HIGH_ANGLE, etc.
- **`MotionStrengthLevel`** - NONE, SUBTLE, MODERATE, STRONG, EXTREME
- **`TransitionStyle`** - CUT, FADE, DISSOLVE, etc.
- **`StylePreset`** - DOCUMENTARY, COMMERCIAL, ACTION, etc.

### Utilities

- **`PresetLibrary`** - Access predefined presets
- **`IterationWorkflow`** - Refinement tools
- **`AutoModeAssistant`** - Simplified control selection
- **`GenerationComparison`** - Track and compare generations

## Best Practices

1. **Start with Presets** - Use presets as baseline, customize from there
2. **Lock Early** - Lock parameters that work before iterating
3. **Small Changes** - Adjust one parameter at a time
4. **Compare Always** - Track what works with ratings and notes
5. **Auto → Pro** - Start in Auto, upgrade to Pro for control
6. **Match FPS** - Choose FPS for your platform (24 film, 30 web, 60 slow-mo)
7. **Motion Matters** - Lower motion for stability, higher for energy

## Troubleshooting

### Too Fast / Motion Sickness
```python
controls.camera.speed = 0.5
controls.motion.overall_strength = MotionStrengthLevel.SUBTLE
controls.motion.motion_blur = True
```

### Too Static / Boring
```python
controls.camera.speed = 1.2
controls.motion.overall_strength = MotionStrengthLevel.STRONG
controls.camera.movement_type = CameraMovementType.ORBIT
```

### Too Shaky
```python
controls.camera.movement_type = CameraMovementType.STEADICAM
controls.motion.camera_motion = 0.3
```

## Testing

Run the test suite:
```bash
pytest tests/test_director_ux.py -v
```

Run examples:
```bash
python examples/director_ux_examples.py
```

## Architecture

```
DirectorControls (UX Layer)
    ↓
Internal Parameters (Unified Format)
    ↓
Model Adapters (Runway, Pika, Sora, Veo)
    ↓
Video Generation APIs
```

## Contributing

When adding new features:

1. Add to appropriate control class (Camera, Timing, Motion)
2. Update `to_internal_params()` method
3. Add to JSON schema
4. Update documentation
5. Add tests
6. Update examples

## License

Part of the ANIMAtiZE Framework. See LICENSE for details.

## Support

- **Full Spec**: [DIRECTOR_UX_SPECIFICATION.md](DIRECTOR_UX_SPECIFICATION.md)
- **Quick Reference**: [DIRECTOR_UX_QUICK_REFERENCE.md](DIRECTOR_UX_QUICK_REFERENCE.md)
- **Examples**: [director_ux_examples.py](../../examples/director_ux_examples.py)
- **Tests**: [test_director_ux.py](../../tests/test_director_ux.py)

---

**Director UX Control Surface** - Professional video generation controls for the ANIMAtiZE Framework
