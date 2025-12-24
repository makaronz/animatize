# Video Prompting Research Documentation

## Overview

This document provides comprehensive research on AI video prompting techniques, cataloging prompt structures per model, documenting controllability parameters, and compiling best practices for temporal consistency and multi-scene coherence.

## Source Analysis

Based on analysis of `ai-video-prompting-guide_PL-EN.md` and integration with ANIMAtiZE's existing 47+ cinematic rules in `movement_prediction_rules.json`.

## Supported Models

### Model Catalog Summary

| Model | Provider | Max Duration | Resolution | Specialization |
|-------|----------|--------------|------------|----------------|
| Kling | Kwai | 5-10s | 1080p | Realistic cinematic scenes |
| WAN | WAN AI | 2-8s | 4K | Dynamic scenes with audio sync |
| Runway | Runway | 4-16s | 4K | Creative experimentation |
| LTX | Lightricks | 4-10s | 1080p | Realistic temporal control |
| LTX 2 | Lightricks | 5-15s | 4K | Enhanced movements |
| Sora 2 | OpenAI | 60s | 4K | Complex narratives |
| Veo 3 | Google | 60s | 1080p | Audio-visual integration |
| Veo 3.1 | Google | 60s | 4K | Enhanced effects |
| Higgsfield | Higgsfield | 5-10s | 1080p | Dynamic animations |
| Luma | Luma Labs | 5-12s | 1080p | Professional camera control |
| Pika | Pika Labs | 3-8s | 1080p | Expressive animations |
| Stable Video Diffusion | Stability AI | 4-10s | 1024p | Fine-tunable diffusion |

## Prompt Structures by Model

### Universal Template

```
[SUBJECT_DESCRIPTION] [ACTION/MOVEMENT] [ENVIRONMENT] [LIGHTING] [ATMOSPHERE] [CAMERA_MOVEMENT] [VISUAL_STYLE]
```

### Model-Specific Structures

#### Kling
**Format:** `[SUBJECT_DESCRIPTION] [SUBJECT_MOVEMENT] [ENVIRONMENT] [LIGHTING] [ATMOSPHERE] [CAMERA_MOVEMENT] [STYLE]`

**Patterns:**
- **CAMS (Character-Action-Movement-Setting):** For character-focused scenes
- **CINE (Camera-Intent-Narrative-Emotion):** For cinematic storytelling

**Example:**
```
A young woman in a red dress dances on a rainy city square, raindrops reflecting off neon advertisements. The camera circles around her, capturing the grace of her movement. Cinematic, realistic.
```

#### WAN
**Format:** `[SUBJECT] [SCENE] [MOTION] [CAMERA_LANGUAGE] [ATMOSPHERE] [STYLING] [AUDIO_SYNCHRONIZATION]`

**Patterns:**
- **SPARK (Subject-Purpose-Action-Result-Key):** For creative artistic scenes

**Example:**
```
Golden retriever: Grassy meadow -> chasing ball with joy -> water splashing. Camera follows alongside. Realistic, natural.
```

#### Sora 2
**Format:** `[NARRATIVE] [SCENE] [CHARACTER] [ACTION] [TIME_PERIOD] [VISUAL_STYLE] [NARRATIVE_CONTROLS]`

**Patterns:**
- **NARRATIVE:** Multi-scene storytelling with scene-by-scene breakdown

**Example:**
```
Scene 1: Small robot discovers a hidden garden on a deserted planet. 
Scene 2: Robot explores with wonder and curiosity.
Scene 3: Robot finds beauty in unexpected places.
Camera follows discovery, showing emotion. Animation, family-friendly.
```

#### Luma
**Format:** `[SCENE] [CHARACTER] [ACTION] [CAMERA_COMPOSITION] [CAMERA_MOVEMENT] [CINEMATIC_STYLE]`

**Patterns:**
- **CINEMATIC:** Professional cinematography with technical camera specs

**Example:**
```
Close-up shot: Luxury car on mountain road at sunset with golden lighting, creating aspirational mood.
Camera: Steadicam tracking shot, 50mm focal length, f/2.8 aperture.
Style: Commercial, cinematic.
```

## Controllability Parameters

### Critical Parameters for Temporal Consistency

#### Universal Parameters

1. **seed**
   - Type: Integer (0-2147483647)
   - Impact: Critical for reproducibility
   - Recommendation: Use fixed seed for consistent results
   - Models: All except audio-focused models

2. **temporal_weight / temporal_consistency**
   - Type: Float (0.0-1.0)
   - Impact: Critical for frame-to-frame coherence
   - Recommendation: 0.7-0.9 for most scenes
   - Models: WAN, LTX, LTX2, Sora 2

3. **motion_strength**
   - Type: Float (0.0-1.0)
   - Impact: Critical for stability vs dynamics
   - Recommendation: 0.3-0.6 for stability
   - Models: WAN, Runway, Kling

4. **guidance_scale**
   - Type: Float (1.0-20.0)
   - Impact: Critical for prompt adherence
   - Recommendation: 7.0-9.0 for balance
   - Models: Stable Video Diffusion, similar architectures

5. **frame_interpolation / frame_rate**
   - Type: Integer (24, 30, 60 fps)
   - Impact: High for motion smoothness
   - Recommendation: 24fps for cinematic, 60fps for smooth motion
   - Models: LTX, LTX2, Higgsfield, Pika

### Camera Motion Parameters

#### camera_movement / camera_type
- **Values:** static, pan, tilt, zoom, dolly, orbit, crane, drone, handheld, steadicam, tripod
- **Impact:** High on temporal consistency
- **Usage:**
  - **static:** No movement, emphasizes subject action
  - **pan:** Horizontal rotation, reveals environment
  - **tilt:** Vertical rotation, shows scale
  - **zoom:** Focal length change, increases/decreases intimacy
  - **dolly:** Physical camera movement, creates depth
  - **orbit:** Circular movement, shows all angles
  - **crane:** Vertical sweep, establishes scale

#### focal_length (Luma-specific)
- **Range:** 14mm-200mm
- **Common values:**
  - 14-24mm: Ultra-wide, environmental shots
  - 35-50mm: Natural perspective, general use
  - 85-135mm: Portrait, character close-ups
  - 200mm+: Telephoto, compression effects

### Audio Synchronization Parameters

#### audio_sync (Veo 3, Veo 3.1, WAN)
- **Type:** Boolean
- **Impact:** Critical for audio-visual coherence
- **Use case:** Music videos, dialogue scenes

#### beat_sync (Veo 3, Veo 3.1)
- **Type:** Boolean
- **Impact:** High for rhythmic motion
- **Use case:** Dance scenes, action synchronized to music

#### lip_sync (Veo 3, Veo 3.1)
- **Type:** Boolean
- **Impact:** High for dialogue
- **Use case:** Speaking characters

### Special Effects Parameters

#### particle_effects (Veo 3.1)
- **Type:** Boolean
- **Impact:** Medium on temporal consistency
- **Use case:** Magic, explosions, atmospheric effects

#### physics_simulation (Veo 3.1)
- **Type:** Boolean
- **Impact:** High on realism
- **Use case:** Realistic object interactions

## Best Practices for Temporal Consistency

### Core Principles

1. **Precision and Detail**
   - Use specific, concrete descriptions
   - Avoid vague or ambiguous language
   - Include temporal markers ("gradually", "slowly", "smoothly")

2. **Logical Structure**
   - Organize prompts with clear hierarchy
   - Follow consistent ordering of elements
   - Separate distinct concepts clearly

3. **Contextualization**
   - Provide environmental context
   - Establish spatial relationships
   - Define temporal progression

4. **Iterative Refinement**
   - Test and adjust parameters
   - Document successful configurations
   - Build on working patterns

### Specific Techniques

#### For High Temporal Consistency

1. **Use Fixed Seeds**
   ```json
   {
     "seed": 42,
     "temporal_consistency": 0.85
   }
   ```

2. **Moderate Motion Strength**
   - Keep motion_strength between 0.3-0.6
   - Higher values risk temporal artifacts
   - Lower values may appear static

3. **Specify Gradual Transitions**
   - ❌ "Camera moves to close-up"
   - ✅ "Camera slowly dollies in over 3 seconds to close-up"

4. **Maintain Consistent Lighting**
   - ❌ "Scene changes from day to night"
   - ✅ "Golden hour light gradually dims as sun sets over 8 seconds"

5. **Use Temporal Anchors**
   ```
   Beginning: Character stands still, contemplating
   Middle: Character begins walking forward slowly
   End: Character reaches destination and stops
   ```

#### For Stable Camera Movement

1. **Specify Movement Speed**
   - "slow dolly in" vs "rapid zoom"
   - Slower movements = better stability

2. **Define Movement Path**
   - "Camera pans left following subject"
   - Clear direction improves consistency

3. **Use Professional Camera Types**
   - Steadicam for smooth tracking
   - Tripod for stable static shots
   - Drone for aerial movements

## Multi-Scene Coherence

### Planning Multi-Scene Videos

#### Character Consistency

**Critical Elements to Maintain:**
- Exact character description (age, appearance, clothing)
- Character name/identifier
- Character traits and behaviors

**Example:**
```
Scene 1: "Maya, a young woman with long black hair wearing a blue jacket"
Scene 2: "Maya, a young woman with long black hair wearing a blue jacket" (identical)
Scene 3: "Maya, a young woman with long black hair wearing a blue jacket" (identical)
```

#### Environmental Continuity

**Maintain Across Scenes:**
- Location description
- Time of day
- Weather conditions
- Lighting direction

**Example Continuity:**
```
Scene 1: "Forest at golden hour, warm sunlight from the right"
Scene 2: "Same forest at golden hour, warm sunlight from the right, slightly dimmer"
Scene 3: "Same forest as sun sets, warm orange light fading from the right"
```

#### Style Uniformity

**Keep Consistent:**
- Visual style descriptor (cinematic, realistic, artistic)
- Color palette references
- Mood and atmosphere

#### Seed Sequencing

**Strategy for Related Scenes:**
```python
base_seed = 42
scene_1_seed = base_seed + 0  # 42
scene_2_seed = base_seed + 1  # 43
scene_3_seed = base_seed + 2  # 44
```

Sequential seeds provide variation while maintaining coherence.

### Scene Transitions

#### Fade
- **Description:** Gradual opacity change
- **Use case:** Time passage, emotional transitions
- **Temporal impact:** Low
- **Prompt suggestion:** "Scene gradually fades to black, then fades in to..."

#### Cut
- **Description:** Instant scene change
- **Use case:** Action sequences, parallel narratives
- **Temporal impact:** Medium
- **Prompt suggestion:** "Cut to..."

#### Dissolve
- **Description:** Blended transition
- **Use case:** Dreamlike sequences, memory transitions
- **Temporal impact:** High
- **Prompt suggestion:** "Scene dissolves into..."

## Mapping to ANIMAtiZE Cinematic Rules

### Integration with Movement Prediction Rules

The video prompting catalog integrates with ANIMAtiZE's 47+ cinematic rules:

#### Camera Motion → Rule Mapping

1. **Static Camera** (no movement)
   - Applies: `movement_001` - Pose-to-Action Continuation
   - Applies: `movement_004` - Emotional Momentum Analysis
   - Focus: Subject movement and emotional expression

2. **Pan/Tilt/Orbit** (rotational)
   - Applies: `movement_002` - Composition-Guided Camera Flow
   - Applies: `movement_005` - Depth Layer Parallax
   - Focus: Compositional elements and depth

3. **Zoom/Dolly** (distance change)
   - Applies: `movement_008` - Emotional Framing Progression
   - Focus: Emotional intimacy and narrative focus

4. **All Camera Types**
   - Applies: `movement_003` - Physics-Based Environmental Motion
   - Applies: `movement_006` - Atmospheric Response System
   - Focus: Environmental realism and atmosphere

### Core ANIMAtiZE Principles Applied

1. **Every movement must serve the narrative**
   - Video prompts should justify all motion
   - Camera moves support story beats

2. **Physics must be consistent and realistic**
   - Environmental motion follows natural laws
   - Object interactions are believable

3. **Emotional beats must be maintained**
   - Character expressions evolve logically
   - Emotional progression is coherent

4. **Composition must guide viewer attention**
   - Camera movement follows compositional lines
   - Framing emphasizes narrative focus

5. **Timing must feel natural and cinematic**
   - Movement speed matches emotional tone
   - Transitions are smooth and motivated

## Parameter Optimization Guidelines

### By Use Case

#### Product Videos
```json
{
  "model": "luma",
  "camera_type": "steadicam",
  "focal_length": 50,
  "motion_strength": 0.3,
  "temporal_consistency": 0.9,
  "style": "commercial"
}
```

#### Action Sequences
```json
{
  "model": "kling",
  "camera_movement": "dolly",
  "motion_strength": 0.7,
  "temporal_consistency": 0.7,
  "frame_rate": 60,
  "style": "cinematic"
}
```

#### Dialogue Scenes
```json
{
  "model": "veo3",
  "audio_sync": true,
  "lip_sync": true,
  "camera_type": "tripod",
  "temporal_consistency": 0.85,
  "style": "realistic"
}
```

#### Artistic/Experimental
```json
{
  "model": "runway",
  "motion_strength": 0.6,
  "aesthetic": "specific",
  "seed": 42,
  "style": "artistic"
}
```

### Quality Checklist

Before generating, verify:

- [ ] Subject description is clear and specific
- [ ] Action/movement is well-defined
- [ ] Environment provides context
- [ ] Lighting is described
- [ ] Atmosphere/mood is specified
- [ ] Camera movement is justified
- [ ] Visual style is consistent
- [ ] Temporal consistency parameters are set
- [ ] Seed is fixed (if reproducibility needed)
- [ ] Motion strength is appropriate for scene type

## Common Failure Modes and Solutions

### Temporal Artifacts

**Problem:** Flickering, inconsistent frames
**Solutions:**
- Increase temporal_consistency to 0.85-0.95
- Reduce motion_strength to 0.3-0.5
- Use fixed seed
- Add "smooth" and "gradual" to prompt

### Character Inconsistency

**Problem:** Character appearance changes between frames
**Solutions:**
- Use identical character descriptions
- Enable character_consistency parameter (Sora 2)
- Use object_tracking (LTX 2)
- Increase temporal_weight

### Motion Instability

**Problem:** Jerky or unnatural movement
**Solutions:**
- Increase motion_smoothness
- Specify movement timing ("over 3 seconds")
- Use appropriate camera_type (steadicam vs handheld)
- Add motion blur

### Audio Desynchronization

**Problem:** Audio and video don't match
**Solutions:**
- Enable audio_sync parameter
- Use beat_sync for rhythmic content
- Enable lip_sync for dialogue
- Test with shorter durations first

### Style Inconsistency

**Problem:** Visual style changes during video
**Solutions:**
- Use identical style descriptors
- Maintain consistent color palette
- Keep lighting descriptions similar
- Use same seed base for related scenes

## Implementation Examples

### Example 1: Single Cinematic Scene

```python
from src.generators.video_prompt_generator import VideoPromptGenerator, VideoGenerationRequest, ModelType

generator = VideoPromptGenerator()

request = VideoGenerationRequest(
    model_type=ModelType.KLING,
    scene_description="A warrior stands on a cliff at sunrise, wind blowing through their cloak. Camera slowly dollies in to their determined face.",
    duration=8.0,
    aspect_ratio="16:9",
    style="cinematic",
    temporal_consistency_priority="high"
)

prompt = generator.generate_prompt(request)
parameters = generator.generate_model_parameters(request)

print(f"Prompt: {prompt}")
print(f"Parameters: {parameters}")
```

### Example 2: Multi-Scene Sequence

```python
scenes = [
    "Warrior stands on cliff at sunrise, contemplating",
    "Warrior draws sword, determination in eyes",
    "Warrior charges into battle, camera tracking alongside"
]

multi_scene = generator.generate_multi_scene_prompts(
    scenes,
    ModelType.SORA2
)

for scene in multi_scene['scenes']:
    print(f"Scene {scene['scene_number']}: {scene['prompt']}")
```

### Example 3: Audio-Synchronized Video

```python
request = VideoGenerationRequest(
    model_type=ModelType.VEO3,
    scene_description="Musician plays piano in dimly lit jazz club, fingers dancing across keys. Camera circles around, capturing emotion.",
    duration=12.0,
    style="cinematic",
    include_audio=True,
    custom_parameters={
        "music_style": "jazz",
        "audio_sync": True
    }
)

prompt = generator.generate_prompt(request)
```

## Conclusion

This research provides a comprehensive framework for AI video prompting that:

1. **Catalogs** prompt structures for 12 major AI video models
2. **Documents** 50+ controllability parameters with impact analysis
3. **Compiles** best practices for temporal consistency and multi-scene coherence
4. **Maps** to ANIMAtiZE's 47+ cinematic rules for justified movement
5. **Provides** practical implementation examples

By following these guidelines and using the provided tools, users can generate high-quality, temporally consistent AI videos with professional cinematic characteristics.

## References

- Source: `ai-video-prompting-guide_PL-EN.md` (October 26, 2025)
- Integration: `configs/movement_prediction_rules.json` (ANIMAtiZE framework)
- Implementation: `src/analyzers/video_prompt_analyzer.py`
- Generation: `src/generators/video_prompt_generator.py`
