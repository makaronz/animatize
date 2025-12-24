# Prompt Compiler & Control Map System Schema

## Overview

The Prompt Compiler system transforms high-level Director Intent into model-specific prompts with control parameters, supporting multi-scene production workflows with deterministic reproducibility.

## Version History

| Version | Release Date | Changes |
|---------|--------------|---------|
| 3.0 | 2024 | Full control map system, multi-scene support, determinism |
| 2.0 | 2024 | Camera motion, character consistency |
| 1.0 | 2024 | Initial release |

## Core Data Structures

### DirectorIntent

High-level creative specification that gets compiled into model-specific prompts.

```json
{
  "intent_id": "unique_identifier",
  "narrative_description": "Overall story or concept description",
  "style_references": ["Blade Runner 2049", "Dune"],
  "mood": "contemplative",
  "pacing": "slow",
  "visual_theme": "neo-noir cyberpunk",
  "target_providers": ["runway", "pika", "sora", "veo"],
  "scenes": [],
  "storyboards": [],
  "global_determinism": {},
  "prompt_version": "2.0",
  "schema_version": "3.0",
  "created_at": "2024-01-01T00:00:00Z",
  "metadata": {}
}
```

### Scene

Container for multiple shots with transitions.

```json
{
  "scene_id": "scene_001",
  "description": "Opening establishing sequence",
  "shots": [],
  "transitions": [],
  "global_characters": [],
  "scene_fps": 24,
  "total_duration": 30.0,
  "metadata": {}
}
```

### Shot

Individual shot specification with full control parameters.

```json
{
  "shot_id": "shot_001",
  "scene_id": "scene_001",
  "prompt": "Wide establishing shot of futuristic city at sunset",
  "camera_motion": {},
  "characters": [],
  "reference_frames": [],
  "control_maps": [],
  "fps": 24,
  "duration": 8.0,
  "motion_strength": "moderate",
  "determinism": {},
  "storyboard_ref": "panel_001",
  "metadata": {}
}
```

## Control Vocabulary

### Camera Motion Types

```
static, pan_left, pan_right, tilt_up, tilt_down,
dolly_in, dolly_out, track_left, track_right,
crane_up, crane_down, zoom_in, zoom_out,
orbit_clockwise, orbit_counter_clockwise,
handheld, steadicam, push_in, pull_out
```

### Camera Motion Structure

```json
{
  "motion_type": "dolly_in",
  "strength": "moderate",
  "speed": 1.0,
  "start_time": 0.0,
  "end_time": 5.0,
  "easing": "ease_in_out",
  "constraints": {}
}
```

**Parameters:**
- `motion_type`: One of the camera motion types
- `strength`: none | subtle | moderate | strong | extreme
- `speed`: 0.1 to 5.0 (multiplier)
- `start_time`: Start time in seconds
- `end_time`: End time in seconds (optional)
- `easing`: linear | ease_in | ease_out | ease_in_out

### Character Consistency

Maintains consistent character appearance across shots.

```json
{
  "character_id": "protagonist_001",
  "reference_frames": [0, 10, 20, 30],
  "feature_weights": {
    "face": 1.0,
    "body": 0.9,
    "clothing": 0.95,
    "hair": 0.85
  },
  "appearance_locked": true,
  "expression_range": ["neutral", "determined"],
  "clothing_consistency": true,
  "pose_reference": "character_poses/pose_001.json"
}
```

**Feature Weights:**
- `face`: 0.0 to 1.0 (facial features)
- `body`: 0.0 to 1.0 (body type/proportions)
- `clothing`: 0.0 to 1.0 (outfit consistency)
- `hair`: 0.0 to 1.0 (hairstyle)

### Reference Frames

Link to specific frames for visual reference.

```json
{
  "frame_id": "ref_001",
  "timestamp": 0.0,
  "image_path": "/path/to/reference.jpg",
  "image_url": "https://example.com/reference.jpg",
  "embeddings": {},
  "weight": 1.0,
  "aspect": "full"
}
```

**Aspect Types:**
- `full`: Full frame reference
- `face`: Face only
- `body`: Body composition
- `detail`: Specific detail element

### Motion Strength

Overall motion intensity level.

```
none, subtle, moderate, strong, extreme
```

**Model Mappings:**

| Strength | Runway (1-10) | Pika (0.0-1.0) | Description |
|----------|---------------|----------------|-------------|
| none | 0 | 0.0 | Static or minimal motion |
| subtle | 3 | 0.25 | Gentle, barely noticeable |
| moderate | 5 | 0.5 | Natural motion |
| strong | 8 | 0.75 | Prominent motion |
| extreme | 10 | 1.0 | Maximum motion |

### Control Maps

Spatial/temporal guidance for generation.

```json
{
  "map_type": "depth",
  "map_data": "/path/to/depth_map.png",
  "strength": 0.8,
  "start_frame": 0,
  "end_frame": 120,
  "preprocessor": "depth_midas",
  "conditioning_scale": 1.0
}
```

**Map Types:**
- `depth`: Depth map for spatial control
- `normal`: Surface normal maps
- `edge`: Edge detection maps
- `pose`: Human pose skeleton
- `segmentation`: Semantic segmentation

**Preprocessors:**
- `depth_midas`: Midas depth estimation
- `depth_leres`: LeReS depth estimation
- `openpose`: OpenPose skeleton detection
- `canny`: Canny edge detection
- `hed`: HED edge detection

### Storyboard

Pre-visualization panel reference.

```json
{
  "panel_id": "panel_001",
  "shot_number": "1A",
  "description": "Hero stands on cliff overlooking valley",
  "camera_angle": "low angle",
  "composition": "rule of thirds, hero on right",
  "duration": 3.0,
  "reference_image": "/path/to/storyboard.jpg",
  "motion_notes": "Slow crane up",
  "dialogue": "Optional dialogue text",
  "metadata": {}
}
```

### Shot Transitions

Transitions between shots.

```json
{
  "from_shot": "shot_001",
  "to_shot": "shot_002",
  "transition_type": "dissolve",
  "duration": 1.0,
  "parameters": {}
}
```

**Transition Types:**
```
cut, fade, dissolve, wipe, match_cut,
jump_cut, smash_cut, crossfade
```

### Determinism Configuration

Controls for reproducible generation.

```json
{
  "seed": 42,
  "use_fixed_seed": true,
  "generation_seed": 42,
  "sampler_seed": 42,
  "noise_seed": 42,
  "seed_mode": "auto",
  "reproducibility_level": "high"
}
```

**Reproducibility Levels:**
- `standard`: Basic seed control
- `high`: Fixed seeds + deterministic sampling
- `maximum`: All randomness sources controlled

### FPS (Frames Per Second)

Supported frame rates:
```
12, 15, 24, 25, 30, 48, 50, 60, 120
```

Standard recommendations:
- `24`: Cinematic standard
- `30`: Video standard
- `60`: Smooth motion
- `120`: High-speed/slow-motion capture

## Model-Specific Compilation

### Runway Gen-3

```json
{
  "provider": "runway",
  "model": "gen3",
  "compiled_prompt": "Enhanced prompt with Runway-specific language",
  "control_parameters": {
    "duration": 8.0,
    "fps": 24,
    "motion_amount": 5,
    "camera_motion": {
      "type": "dolly_in",
      "speed": 0.8,
      "strength": "moderate"
    },
    "seed": 42,
    "image_prompt": "/path/to/reference.jpg"
  }
}
```

### Pika 1.5

```json
{
  "provider": "pika",
  "model": "pika-1.5",
  "compiled_prompt": "Enhanced prompt",
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

### OpenAI Sora

```json
{
  "provider": "sora",
  "model": "sora-1.0",
  "compiled_prompt": "Enhanced prompt with character consistency notes",
  "control_parameters": {
    "duration": 8.0,
    "resolution": [1920, 1080],
    "seed": 42
  }
}
```

### Google Veo

```json
{
  "provider": "veo",
  "model": "veo-1",
  "compiled_prompt": "Enhanced prompt with camera motion description",
  "control_parameters": {
    "duration_seconds": 8.0,
    "fps": 24,
    "camera_motion": "dolly_in",
    "seed": 42
  }
}
```

### Flux (Image Generation)

```json
{
  "provider": "flux",
  "model": "flux-1-dev",
  "compiled_prompt": "Enhanced storyboard prompt",
  "control_parameters": {
    "guidance_scale": 7.5,
    "num_inference_steps": 50,
    "seed": 42
  }
}
```

## Best Practices

1. **Versioning**: Always specify prompt_version and schema_version
2. **Seeds**: Use seed manifests for reproducibility in production
3. **Character Consistency**: Define characters at scene level when appearing in multiple shots
4. **Control Maps**: Use appropriate preprocessors for your content type
5. **FPS Selection**: Match FPS to target platform requirements
6. **Motion Strength**: Start with "moderate" and adjust based on results
7. **Transitions**: Consider transition duration in total scene timing
8. **Reference Frames**: Use high-quality references for best consistency
