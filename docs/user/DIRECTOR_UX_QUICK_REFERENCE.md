# Director UX Control Surface - Quick Reference

## Quick Start

### Pro Mode (5 lines)
```python
from src.core.director_ux import DirectorControls, CameraMovementType, ShotType

controls = DirectorControls(mode="pro")
controls.camera.movement_type = CameraMovementType.DOLLY
controls.camera.shot_type = ShotType.CLOSEUP
controls.timing.duration = 7.0
params = controls.to_internal_params()
```

### Auto Mode (3 lines)
```python
from src.core.director_ux import AutoModeAssistant

controls = AutoModeAssistant.suggest_controls("product", "exciting", 5.0)
params = controls.to_internal_params()
```

### Use Preset (2 lines)
```python
from src.core.director_ux import PresetLibrary, StylePreset

controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
```

---

## Camera Movement Types

| Type | Description | Use Case |
|------|-------------|----------|
| `STATIC` | No movement | Stability, focus |
| `PAN` | Horizontal rotation | Follow action, reveal |
| `TILT` | Vertical rotation | Reveal height, scale |
| `DOLLY` | Move toward/away | Intimacy, reveal |
| `TRACK` | Move parallel | Follow subject |
| `CRANE` | Vertical movement | Grand reveals, scope |
| `ZOOM` | Lens zoom | Quick focus change |
| `ORBIT` | Circular around subject | 360° view, showcase |
| `HANDHELD` | Natural shake | Documentary, realism |
| `STEADICAM` | Smooth following | Professional tracking |
| `PUSH` | Forward into scene | Building tension |
| `PULL` | Backward from scene | Reveal context |

---

## Shot Types

| Type | Frame | Use Case |
|------|-------|----------|
| `EXTREME_WIDE` | Full environment | Establish location |
| `WIDE` | Subject in environment | Context, scene setting |
| `FULL` | Full body | Action, movement |
| `MEDIUM` | Waist up | Conversation, interaction |
| `CLOSEUP` | Face/head | Emotion, detail |
| `EXTREME_CLOSEUP` | Eyes/detail | Intense emotion, detail |
| `OVER_SHOULDER` | Behind one subject | Conversation POV |
| `POV` | Character's view | Immersion, perspective |
| `TWO_SHOT` | Two subjects | Relationship, dialogue |

---

## Camera Angles

| Angle | View | Emotional Effect |
|-------|------|------------------|
| `EYE_LEVEL` | Neutral | Equality, naturalism |
| `HIGH_ANGLE` | Looking down | Vulnerability, diminutive |
| `LOW_ANGLE` | Looking up | Power, dominance |
| `BIRDS_EYE` | Directly overhead | Disorientation, overview |
| `DUTCH_ANGLE` | Tilted horizon | Unease, tension |

---

## Motion Strength Levels

| Level | Value | Description |
|-------|-------|-------------|
| `NONE` | 0.0 | Completely static |
| `SUBTLE` | 0.25 | Barely perceptible |
| `MODERATE` | 0.5 | Natural, balanced |
| `STRONG` | 0.75 | Pronounced, dynamic |
| `EXTREME` | 1.0 | Maximum energy |

---

## Transition Types

| Type | Description | Duration |
|------|-------------|----------|
| `CUT` | Instant | 0s |
| `FADE` | Through black/white | 1-2s |
| `DISSOLVE` | Cross-blend | 0.5-1.5s |
| `CROSSFADE` | Audio + visual blend | 1-2s |
| `SMASH_CUT` | Abrupt contrast | 0s |
| `FADE_TO_BLACK` | End scene | 1-2s |

---

## FPS Guidelines

| FPS | Use Case |
|-----|----------|
| 24 | Cinematic standard (film look) |
| 30 | Broadcast standard (smooth) |
| 60 | Slow motion source (2.5x at 24fps) |
| 120 | Extreme slow motion (5x at 24fps) |

---

## Style Presets Cheat Sheet

| Preset | Camera | Motion | FPS | Use For |
|--------|--------|--------|-----|---------|
| **Documentary** | Handheld | Subtle | 24 | Reality, interviews |
| **Commercial** | Dolly | Moderate | 30 | Products, brands |
| **Art House** | Track | Subtle | 24 | Artistic, mood |
| **Action** | Handheld | Extreme | 60 | Sports, energy |
| **Drama** | Push | Subtle | 24 | Emotion, character |
| **Music Video** | Orbit | Strong | 30 | Performance, creative |

---

## Common Workflows

### 1. Quick Generation
```python
controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
controls.timing.duration = 5.0
params = controls.to_internal_params()
# → Generate video
```

### 2. Iterate and Refine
```python
# Start
controls = PresetLibrary.get_preset(StylePreset.DRAMA)

# Lock good parameters
controls.lock_parameter("camera.focal_length", 85, "Perfect bokeh")

# Create variation
workflow = IterationWorkflow(controls)
variation = workflow.create_variation({"camera.speed": 0.5})

# Compare
comparison = GenerationComparison(
    generation_id="gen_001",
    parameters=params,
    rating=4,
    notes="Good but slightly fast"
)
controls.add_comparison(comparison)

# Get best
best = controls.get_best_generation()
```

### 3. Auto to Pro Upgrade
```python
# Start in Auto
controls = AutoModeAssistant.suggest_controls("product", "exciting", 5.0)

# Switch to Pro for fine-tuning
controls.mode = DirectorMode.PRO
controls.camera.speed = 0.8
controls.depth_of_field = 0.3

params = controls.to_internal_params()
```

---

## Parameter Ranges

| Parameter | Min | Max | Default | Unit |
|-----------|-----|-----|---------|------|
| `camera.speed` | 0.1 | 5.0 | 1.0 | multiplier |
| `camera.focal_length` | 12 | 200 | 50 | mm |
| `timing.duration` | 1.0 | 60.0 | 5.0 | seconds |
| `timing.speed_factor` | 0.25 | 4.0 | 1.0 | multiplier |
| `motion.*_motion` | 0.0 | 1.0 | 0.5 | normalized |
| `depth_of_field` | 0.0 | 1.0 | 0.5 | normalized |
| `motion_blur_amount` | 0.0 | 1.0 | 0.5 | normalized |

---

## Common Combinations

### Product Showcase
```python
camera.movement = DOLLY
camera.shot_type = MEDIUM
camera.speed = 0.6
timing.fps = 30
motion.strength = MODERATE
```

### Dramatic Scene
```python
camera.movement = PUSH
camera.shot_type = CLOSEUP
camera.focal_length = 85
timing.fps = 24
motion.strength = SUBTLE
```

### Action Sequence
```python
camera.movement = HANDHELD
camera.shot_type = MEDIUM
camera.speed = 1.8
timing.fps = 60
motion.strength = EXTREME
```

### Artistic/Moody
```python
camera.movement = TRACK
camera.shot_type = WIDE
camera.speed = 0.4
timing.fps = 24
motion.strength = SUBTLE
```

---

## Troubleshooting

### Too Fast/Motion Sickness
```python
controls.camera.speed = 0.5  # Slow down
controls.motion.overall_strength = MotionStrengthLevel.SUBTLE
controls.motion.motion_blur = True  # Add blur for smoothness
```

### Too Static/Boring
```python
controls.camera.speed = 1.2  # Speed up
controls.motion.overall_strength = MotionStrengthLevel.STRONG
controls.camera.movement_type = CameraMovementType.ORBIT  # More dynamic
```

### Too Shaky
```python
controls.camera.movement_type = CameraMovementType.STEADICAM  # Stabilize
controls.motion.camera_motion = 0.3  # Reduce camera motion
```

### Wrong Mood
```python
# Use presets as starting point
controls = PresetLibrary.get_preset(StylePreset.DRAMA)  # For emotion
# or
controls = PresetLibrary.get_preset(StylePreset.ACTION)  # For energy
```

---

## API Cheat Sheet

### Import
```python
from src.core.director_ux import (
    DirectorControls, DirectorMode,
    CameraMovementType, ShotType, CameraAngle,
    MotionStrengthLevel, TransitionStyle,
    StylePreset, PresetLibrary,
    IterationWorkflow, AutoModeAssistant,
    GenerationComparison
)
```

### Create
```python
# From scratch
controls = DirectorControls(mode=DirectorMode.PRO)

# From preset
controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)

# Auto mode
controls = AutoModeAssistant.suggest_controls("product", "calm", 5.0)

# From dict
controls = DirectorControls.from_dict(saved_data)
```

### Modify
```python
controls.camera.movement_type = CameraMovementType.DOLLY
controls.timing.duration = 7.0
controls.motion.overall_strength = MotionStrengthLevel.MODERATE
```

### Lock
```python
controls.lock_parameter("camera.speed", 0.8, "Perfect speed")
controls.unlock_parameter("camera.speed")
```

### Iterate
```python
workflow = IterationWorkflow(controls)
variation = workflow.create_variation({"camera.speed": 1.0})
suggestions = workflow.suggest_refinements(controls, "too fast")
```

### Compare
```python
comp = GenerationComparison(
    generation_id="gen_001",
    parameters={...},
    rating=4,
    notes="Good result"
)
controls.add_comparison(comp)
best = controls.get_best_generation()
```

### Export
```python
# To internal parameters (for video generation)
params = controls.to_internal_params()

# To dict (for storage)
data = controls.to_dict()

# To JSON
import json
json_str = json.dumps(controls.to_dict(), indent=2)
```

---

## One-Liners

```python
# Quick commercial video
params = PresetLibrary.get_preset(StylePreset.COMMERCIAL).to_internal_params()

# Auto mode product video
params = AutoModeAssistant.suggest_controls("product", "exciting", 5.0).to_internal_params()

# List all presets
presets = [p['name'] for p in PresetLibrary.list_presets()]

# Lock all current camera settings
for param in ['movement_type', 'speed', 'shot_type']:
    controls.lock_parameter(f"camera.{param}", getattr(controls.camera, param))

# Create 3 speed variations
variations = [IterationWorkflow(controls).create_variation({"camera.speed": s}) 
              for s in [0.6, 0.8, 1.0]]
```

---

## Best Practices

1. **Start with Presets**: Use `PresetLibrary.get_preset()` as base
2. **Lock Early**: Lock parameters that work before iterating
3. **Small Changes**: Adjust one parameter at a time when refining
4. **Compare Always**: Use `GenerationComparison` to track what works
5. **Auto → Pro**: Start in Auto mode, upgrade to Pro for fine control
6. **Use Suggestions**: Trust `suggest_refinements()` for quick fixes
7. **Test FPS**: Match FPS to your target platform (24 film, 30 web, 60 slow-mo)
8. **Motion Matters**: Lower motion strength for stability, higher for energy

---

## Integration Example

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
    prompt="Elegant product showcase on marble display",
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

# 5. Generate video with first model
model_prompt = result.model_prompts[0]
# → Send to video generation API
```

---

## Resources

- **Full Documentation**: `docs/user/DIRECTOR_UX_SPECIFICATION.md`
- **JSON Schemas**: `docs/user/director_ux_schemas.json`
- **Examples**: `examples/director_ux_examples.py`
- **Source Code**: `src/core/director_ux.py`

---

## Support

For issues or questions:
- Check examples: `python examples/director_ux_examples.py`
- Review schemas: `docs/user/director_ux_schemas.json`
- Read full spec: `docs/user/DIRECTOR_UX_SPECIFICATION.md`
