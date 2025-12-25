# Director UX Control Surface Specification

## Overview

The Director UX Control Surface provides professional-grade controls for AI video generation, bridging the gap between creative intent and technical parameters. It offers two modes (Pro and Auto) to serve both professional directors and casual users.

## Table of Contents

1. [Control Surface Architecture](#control-surface-architecture)
2. [Professional Controls](#professional-controls)
3. [Operating Modes](#operating-modes)
4. [Iteration Workflow](#iteration-workflow)
5. [Style Presets](#style-presets)
6. [Parameter Mapping](#parameter-mapping)
7. [UI Wireframes](#ui-wireframes)
8. [API Reference](#api-reference)

---

## Control Surface Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Director UX Layer                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌───────────────┐           │
│  │  Auto Mode   │              │   Pro Mode    │           │
│  │  Assistant   │              │   Controls    │           │
│  └──────┬───────┘              └───────┬───────┘           │
│         │                              │                    │
│         └──────────┬───────────────────┘                    │
│                    │                                         │
│            ┌───────▼────────┐                               │
│            │ Director       │                               │
│            │ Controls       │                               │
│            └───────┬────────┘                               │
│                    │                                         │
│        ┌───────────┼───────────┐                           │
│        │           │           │                            │
│   ┌────▼───┐  ┌───▼────┐  ┌──▼─────┐                     │
│   │ Camera │  │ Timing │  │ Motion │                      │
│   │Control │  │Control │  │Control │                      │
│   └────┬───┘  └───┬────┘  └──┬─────┘                     │
│        │          │          │                             │
│        └──────────┼──────────┘                             │
│                   │                                         │
├───────────────────┼─────────────────────────────────────────┤
│                   │  Parameter Mapping Layer                │
├───────────────────┼─────────────────────────────────────────┤
│                   │                                         │
│              ┌────▼─────┐                                   │
│              │ Internal │                                   │
│              │Parameters│                                   │
│              └────┬─────┘                                   │
│                   │                                         │
├───────────────────┼─────────────────────────────────────────┤
│                   │  Model Adapter Layer                    │
├───────────────────┼─────────────────────────────────────────┤
│                   │                                         │
│     ┌─────────────┼─────────────┐                          │
│     │             │             │                           │
│ ┌───▼───┐    ┌───▼───┐    ┌───▼───┐                       │
│ │Runway │    │ Pika  │    │ Sora  │  ... (Model APIs)     │
│ └───────┘    └───────┘    └───────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **DirectorControls**: Main control container
2. **CameraControl**: Professional camera controls
3. **TimingControl**: Temporal parameters
4. **MotionControl**: Motion strength and blur
5. **TransitionControl**: Shot transitions
6. **PresetLibrary**: Professional style presets
7. **IterationWorkflow**: Refinement and comparison
8. **AutoModeAssistant**: Simplified control selection

---

## Professional Controls

### 1. Camera Controls

#### Movement Types
```python
CameraMovementType:
    STATIC          # Fixed camera position
    PAN             # Horizontal rotation
    TILT            # Vertical rotation
    DOLLY           # Move toward/away from subject
    TRACK           # Move parallel to subject
    CRANE           # Vertical movement
    ZOOM            # Lens zoom in/out
    ORBIT           # Circular movement around subject
    HANDHELD        # Natural handheld shake
    STEADICAM       # Smooth following motion
    PUSH            # Forward movement
    PULL            # Backward movement
    WHIP_PAN        # Fast pan transition
```

#### Shot Types
```python
ShotType:
    EXTREME_WIDE    # Establishes full environment
    WIDE            # Shows full subject in environment
    FULL            # Full body shot
    MEDIUM          # Waist up
    CLOSEUP         # Face/head
    EXTREME_CLOSEUP # Eyes/detail
    OVER_SHOULDER   # Behind one subject viewing another
    POV             # Point of view shot
    INSERT          # Detail shot
    CUTAWAY         # Supporting shot
    TWO_SHOT        # Two subjects in frame
    GROUP_SHOT      # Multiple subjects
```

#### Camera Angles
```python
CameraAngle:
    EYE_LEVEL       # Neutral, at subject's eye level
    HIGH_ANGLE      # Looking down (diminutive)
    LOW_ANGLE       # Looking up (powerful)
    BIRDS_EYE       # Directly overhead
    WORMS_EYE       # Directly from ground
    DUTCH_ANGLE     # Tilted horizon (unease)
    OVERHEAD        # High angle view
```

#### Camera Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| movement_type | Enum | - | STATIC | Type of camera movement |
| angle | Enum | - | EYE_LEVEL | Camera angle |
| shot_type | Enum | - | MEDIUM | Framing type |
| focal_length | int | 12-200mm | 50mm | Lens focal length |
| speed | float | 0.1-5.0 | 1.0 | Movement speed multiplier |
| strength | Enum | - | MODERATE | Movement intensity |
| easing | string | - | linear | Motion easing curve |
| start_time | float | 0.0+ | 0.0 | When movement starts (seconds) |
| end_time | float | 0.0+ | null | When movement ends (seconds) |

### 2. Timing Controls

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| duration | float | 1.0-60.0s | 5.0s | Total clip duration |
| fps | int | 12,15,24,25,30,48,60,120 | 24 | Frames per second |
| speed_factor | float | 0.25-4.0 | 1.0 | Playback speed (slow-mo/timelapse) |
| start_offset | float | 0.0+ | 0.0 | Trim from start (seconds) |

**FPS Guidelines:**
- 24 fps: Cinematic standard (film look)
- 30 fps: Broadcast standard (smooth)
- 60 fps: Slow motion source (2.5x slow at 24fps)
- 120 fps: Extreme slow motion (5x slow at 24fps)

### 3. Motion Controls

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| overall_strength | Enum | NONE-EXTREME | MODERATE | Global motion intensity |
| subject_motion | float | 0.0-1.0 | 0.5 | Subject movement amount |
| camera_motion | float | 0.0-1.0 | 0.5 | Camera movement amount |
| background_motion | float | 0.0-1.0 | 0.3 | Background movement amount |
| motion_blur | bool | true/false | true | Enable motion blur |
| motion_blur_amount | float | 0.0-1.0 | 0.5 | Blur strength |

**Motion Strength Levels:**
```
NONE     (0.0) : Completely static
SUBTLE   (0.25): Barely perceptible movement
MODERATE (0.5) : Natural, balanced motion
STRONG   (0.75): Pronounced, dynamic motion
EXTREME  (1.0) : Maximum energy and movement
```

### 4. Transition Controls

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| style | Enum | - | CUT | Transition type |
| duration | float | 0.1-5.0s | 1.0s | Transition length |
| offset | float | 0.0+ | 0.0 | Offset from shot end |
| parameters | dict | - | {} | Style-specific params |

**Transition Types:**
```python
TransitionStyle:
    CUT             # Instant cut (0 duration)
    FADE            # Fade through black/white
    DISSOLVE        # Cross-dissolve blend
    WIPE            # Directional wipe
    MATCH_CUT       # Visual match between shots
    JUMP_CUT        # Jarring temporal jump
    SMASH_CUT       # Abrupt contrast cut
    CROSSFADE       # Audio/visual fade
    FADE_TO_BLACK   # Fade out to black
    FADE_FROM_BLACK # Fade in from black
```

### 5. Style Controls

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| visual_style | string | - | "cinematic" | Overall visual aesthetic |
| mood | string | - | "neutral" | Emotional tone |
| color_grade | string | - | "natural" | Color treatment |
| depth_of_field | float | 0.0-1.0 | 0.5 | Bokeh/focus range |
| lighting_style | string | - | "natural" | Lighting approach |
| composition_rule | string | - | "rule_of_thirds" | Framing guideline |
| aspect_ratio | string | - | "16:9" | Frame dimensions |

---

## Operating Modes

### Pro Mode

**Target Users:** Professional directors, cinematographers, video editors

**Features:**
- Full access to all professional controls
- Fine-grained parameter adjustment
- Advanced camera motion controls
- Custom transition timing
- Parameter locking for iteration
- Generation comparison tools
- Batch processing capabilities

**Workflow:**
```
1. Select base preset (optional)
2. Adjust individual parameters
3. Lock satisfied parameters
4. Generate and compare variations
5. Refine based on results
6. Export final parameters
```

**Example:**
```python
controls = DirectorControls(mode=DirectorMode.PRO)

# Fine-tune camera
controls.camera.movement_type = CameraMovementType.DOLLY
controls.camera.shot_type = ShotType.CLOSEUP
controls.camera.speed = 0.8
controls.camera.easing = "ease_in_out"

# Precise timing
controls.timing.duration = 7.5
controls.timing.fps = 30

# Lock parameters
controls.lock_parameter("camera.movement_type", 
                       CameraMovementType.DOLLY.value,
                       "Perfect dolly movement")
```

### Auto Mode

**Target Users:** Content creators, social media, casual users

**Features:**
- Simplified 3-input interface
- Automatic preset selection
- Smart parameter suggestions
- Mood-based adjustments
- Quick duration presets
- One-click generation

**Interface:**
```
┌─────────────────────────────────────┐
│         Auto Mode Assistant         │
├─────────────────────────────────────┤
│                                     │
│  What type of content?              │
│  ⚪ Product    ⚪ Interview          │
│  ⚪ Artistic   ⚪ Sport              │
│  ⚪ Story      ⚪ Music              │
│                                     │
│  What's the mood?                   │
│  ⚪ Calm       ⚪ Exciting           │
│  ⚪ Dramatic   ⚪ Peaceful           │
│  ⚪ Energetic  ⚪ Mysterious         │
│                                     │
│  How long?                          │
│  ⚪ Short (3s)   ⚪ Medium (5s)      │
│  ⚪ Long (10s)   ⚪ Extended (15s)   │
│                                     │
│         [Generate Video]            │
└─────────────────────────────────────┘
```

**Workflow:**
```
1. Select content type → Auto-selects preset
2. Choose mood → Adjusts motion/speed
3. Pick duration → Sets timing
4. Generate → One-click creation
5. (Optional) Switch to Pro mode for refinement
```

**Example:**
```python
auto_controls = AutoModeAssistant.suggest_controls(
    content_type="product",
    mood="exciting",
    duration=5.0
)
# Returns optimized DirectorControls with:
# - Commercial preset base
# - Increased speed for "exciting"
# - 5 second duration
```

### Mode Comparison

| Feature | Auto Mode | Pro Mode |
|---------|-----------|----------|
| Controls Visible | 3 inputs | 30+ parameters |
| Presets | Auto-applied | Manual selection |
| Parameter Locking | N/A | Full support |
| Iteration Tools | Basic | Advanced |
| Learning Curve | Immediate | Moderate |
| Customization | Limited | Complete |
| Target Audience | Casual users | Professionals |
| Workflow Speed | Very fast | Flexible |

---

## Iteration Workflow

### Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Iteration Cycle                           │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Initial Generate  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Review & Compare  │
                    └─────────┬──────────┘
                              │
                     ┌────────┴─────────┐
                     │                  │
           ┌─────────▼────────┐  ┌─────▼─────────┐
           │ Lock Good Params │  │ Note Changes  │
           └─────────┬────────┘  └─────┬─────────┘
                     │                  │
                     └────────┬─────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Create Variation  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │      Generate      │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │    Add to History  │
                    └─────────┬──────────┘
                              │
                              │
                    ┌─────────▼──────────┐
                    │  Satisfied?        │
                    │  Yes → Export      │
                    │  No → Loop Back    │
                    └────────────────────┘
```

### 1. Parameter Locking

**Purpose:** Preserve successful parameters while experimenting with others

**Features:**
- Lock individual parameters with notes
- Locked parameters persist across variations
- Visual indicators in UI
- Unlock anytime

**Example:**
```python
# Lock successful camera movement
controls.lock_parameter(
    parameter_name="camera.movement_type",
    value=CameraMovementType.DOLLY.value,
    notes="Perfect smooth dolly - don't change"
)

# Lock good timing
controls.lock_parameter(
    parameter_name="timing.fps",
    value=30,
    notes="30fps matches our target platform"
)

# Create variation - locked params preserved
workflow = IterationWorkflow(controls)
variation = workflow.create_variation({
    "camera.speed": 1.2,  # Only unlocked params change
    "motion.overall_strength": "strong"
})
```

### 2. Generation Comparison

**Purpose:** Side-by-side comparison of different parameter sets

**Features:**
- Store multiple generations with metadata
- Rate generations (1-5 stars)
- Add notes and feedback
- Visual thumbnail comparison
- Automatic "best" selection
- Parameter diff view

**Data Structure:**
```python
comparison = GenerationComparison(
    generation_id="gen_abc123",
    parameters={...},
    result_url="https://cdn.../video.mp4",
    thumbnail_url="https://cdn.../thumb.jpg",
    rating=4,
    notes="Good speed but too much blur",
    created_at="2025-01-28T10:30:00Z"
)

controls.add_comparison(comparison)
```

**Comparison View:**
```
┌─────────────────────────────────────────────────────────────┐
│                  Generation Comparison                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Gen 1       │  │  Gen 2 ⭐    │  │  Gen 3       │     │
│  │  [Thumbnail] │  │  [Thumbnail] │  │  [Thumbnail] │     │
│  │  ⭐⭐⭐⭐       │  │  ⭐⭐⭐⭐⭐     │  │  ⭐⭐⭐         │     │
│  │              │  │              │  │              │     │
│  │  Speed: 0.8  │  │  Speed: 1.0  │  │  Speed: 1.2  │     │
│  │  Dolly       │  │  Dolly 🔒    │  │  Track       │     │
│  │  5s          │  │  5s 🔒       │  │  5s 🔒       │     │
│  │              │  │              │  │              │     │
│  │  "Too slow"  │  │  "Perfect!"  │  │  "Too fast"  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  [View Diff] [Export Best] [Create New Variation]          │
└─────────────────────────────────────────────────────────────┘
```

### 3. Refinement Suggestions

**Purpose:** AI-assisted parameter adjustments based on feedback

**Features:**
- Natural language feedback analysis
- Smart parameter suggestions
- Reason explanations
- One-click apply
- Suggestion history

**Example:**
```python
workflow = IterationWorkflow(controls)

suggestions = workflow.suggest_refinements(
    current_controls=controls,
    feedback="Camera moves too fast and feels rushed"
)

# Returns:
[
    {
        "parameter": "camera.speed",
        "current_value": 1.5,
        "suggested_value": 1.05,
        "reason": "Reduce camera speed for smoother motion"
    },
    {
        "parameter": "timing.duration",
        "current_value": 5.0,
        "suggested_value": 7.5,
        "reason": "Increase duration for better pacing"
    }
]
```

### 4. Batch Iteration

**Purpose:** Test multiple parameter combinations efficiently

**Features:**
- Define parameter ranges
- Automatic variation generation
- Parallel processing
- Comparison matrix
- Best parameter discovery

**Example:**
```python
# Define ranges to test
batch_config = {
    "camera.speed": [0.6, 0.8, 1.0, 1.2],
    "motion.overall_strength": ["subtle", "moderate", "strong"]
}

# Generates 4 × 3 = 12 variations
# With locked parameters preserved
```

---

## Style Presets

### Preset Library

#### 1. Documentary
```yaml
name: Documentary
description: Naturalistic, observational style
use_case: Reality content, interviews, behind-the-scenes

camera:
  movement: HANDHELD
  angle: EYE_LEVEL
  shot_type: MEDIUM
  focal_length: 35mm
  speed: 0.8
  strength: SUBTLE

timing:
  duration: 8.0s
  fps: 24

motion:
  strength: SUBTLE
  subject_motion: 0.4
  camera_motion: 0.6

style:
  visual: "naturalistic"
  mood: "observational"
  color_grade: "neutral"
  lighting: "natural"
```

#### 2. Commercial
```yaml
name: Commercial
description: Polished, professional product showcase
use_case: Product showcases, brand content, advertising

camera:
  movement: DOLLY
  angle: EYE_LEVEL
  shot_type: MEDIUM
  focal_length: 50mm
  speed: 0.6
  strength: MODERATE
  easing: ease_in_out

timing:
  duration: 5.0s
  fps: 30

motion:
  strength: MODERATE
  subject_motion: 0.5
  camera_motion: 0.7
  motion_blur: true

transition:
  style: DISSOLVE
  duration: 0.8s

style:
  visual: "polished"
  mood: "aspirational"
  color_grade: "vibrant"
  lighting: "three_point"
  depth_of_field: 0.4
```

#### 3. Art House
```yaml
name: Art House
description: Atmospheric, contemplative cinematic style
use_case: Artistic content, experimental videos, mood pieces

camera:
  movement: TRACK
  angle: LOW_ANGLE
  shot_type: WIDE
  focal_length: 24mm
  speed: 0.4
  strength: SUBTLE
  easing: linear

timing:
  duration: 12.0s
  fps: 24
  speed_factor: 0.8  # Slightly slower

motion:
  strength: SUBTLE
  subject_motion: 0.3
  camera_motion: 0.4

transition:
  style: FADE
  duration: 2.0s

style:
  visual: "atmospheric"
  mood: "contemplative"
  color_grade: "desaturated"
  lighting: "chiaroscuro"
  composition_rule: "symmetry"
  depth_of_field: 0.6
```

#### 4. Action
```yaml
name: Action
description: Dynamic, intense high-energy style
use_case: Action sequences, sports, high-energy content

camera:
  movement: HANDHELD
  angle: EYE_LEVEL
  shot_type: MEDIUM
  focal_length: 35mm
  speed: 1.8
  strength: STRONG

timing:
  duration: 3.0s
  fps: 60  # High frame rate for impact

motion:
  strength: EXTREME
  subject_motion: 0.9
  camera_motion: 0.8
  motion_blur: true
  motion_blur_amount: 0.7

transition:
  style: SMASH_CUT

style:
  visual: "dynamic"
  mood: "intense"
  color_grade: "high_contrast"
  lighting: "dramatic"
  depth_of_field: 0.3
```

#### 5. Drama
```yaml
name: Drama
description: Intimate, emotional character-focused style
use_case: Character moments, emotional scenes, narrative content

camera:
  movement: PUSH
  angle: EYE_LEVEL
  shot_type: CLOSEUP
  focal_length: 85mm
  speed: 0.5
  strength: SUBTLE
  easing: ease_in

timing:
  duration: 6.0s
  fps: 24

motion:
  strength: SUBTLE
  subject_motion: 0.3
  camera_motion: 0.5

transition:
  style: CROSSFADE
  duration: 1.5s

style:
  visual: "intimate"
  mood: "emotional"
  color_grade: "warm"
  lighting: "soft"
  composition_rule: "center_weighted"
  depth_of_field: 0.2  # Shallow for bokeh
```

#### 6. Music Video
```yaml
name: Music Video
description: Stylized, energetic with creative freedom
use_case: Music videos, performance content, creative projects

camera:
  movement: ORBIT
  angle: HIGH_ANGLE
  shot_type: FULL
  focal_length: 35mm
  speed: 1.2
  strength: STRONG
  easing: ease_in_out

timing:
  duration: 4.0s
  fps: 30

motion:
  strength: STRONG
  subject_motion: 0.7
  camera_motion: 0.9
  motion_blur: true

transition:
  style: WIPE
  duration: 0.5s

style:
  visual: "stylized"
  mood: "energetic"
  color_grade: "saturated"
  lighting: "theatrical"
  composition_rule: "balanced"
```

### Preset Usage

```python
# Load preset
controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)

# Customize as needed
controls.timing.duration = 7.0
controls.mood = "luxury"

# Generate
params = controls.to_internal_params()
```

---

## Parameter Mapping

### Control Surface → Internal Parameters

```python
DirectorControls → Internal Parameters Mapping:

camera.movement_type     → camera_motion.type
camera.angle            → camera_angle
camera.shot_type        → shot_type
camera.focal_length     → focal_length
camera.speed           → camera_motion.speed
camera.strength        → camera_motion.strength
camera.easing          → camera_motion.easing

timing.duration        → duration
timing.fps            → fps
timing.speed_factor   → speed_factor

motion.overall_strength    → motion_strength
motion.subject_motion     → subject_motion
motion.camera_motion      → camera_motion_amount
motion.background_motion  → background_motion
motion.motion_blur       → enable_motion_blur
motion.motion_blur_amount → motion_blur_strength

transition.style      → transition_type
transition.duration   → transition_duration

visual_style          → style
mood                 → mood
color_grade          → color_grading
depth_of_field       → dof_strength
lighting_style       → lighting
composition_rule     → composition
aspect_ratio         → aspect_ratio
```

### Model-Specific Mappings

#### Runway Gen-3
```python
Internal → Runway:
  duration          → duration
  fps               → fps
  motion_strength   → motion_amount (0-10 scale)
  camera_motion     → camera_motion dict
  seed              → seed
  image_path        → image_prompt
```

#### Pika
```python
Internal → Pika:
  fps              → fps
  motion_strength  → motion (0.0-1.0)
  camera_motion    → camera dict (pan, tilt, zoom)
  seed             → seed
```

#### Sora
```python
Internal → Sora:
  duration         → duration
  resolution       → resolution tuple
  seed             → seed
  style            → style parameter
```

#### Veo
```python
Internal → Veo:
  duration         → duration_seconds
  fps              → fps
  camera_motion    → camera_motion string
  seed             → seed
```

---

## UI Wireframes

### Pro Mode Interface

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ANIMAtiZE Director                                    ⚫ PRO  ⚪ AUTO  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────┐  ┌──────────────────────────────────────────┐ │
│  │  🎬 CAMERA         │  │                                          │ │
│  ├────────────────────┤  │         PREVIEW WINDOW                   │ │
│  │ Movement           │  │                                          │ │
│  │ [Dolly       ▼]   │  │      [  Generated Video Preview  ]       │ │
│  │                    │  │                                          │ │
│  │ Shot Type          │  │                                          │ │
│  │ [Close-up    ▼]   │  │      1920 × 1080  •  24fps  •  5.0s    │ │
│  │                    │  │                                          │ │
│  │ Angle              │  └──────────────────────────────────────────┘ │
│  │ [Eye Level   ▼]   │                                                │
│  │                    │  ┌──────────────────────────────────────────┐ │
│  │ Focal Length       │  │  🎨 STYLE                               │ │
│  │ [====•=====] 50mm  │  ├──────────────────────────────────────────┤ │
│  │                    │  │  Preset: [Commercial      ▼]            │ │
│  │ Speed 🔒           │  │  Mood:   [Aspirational    ▼]            │ │
│  │ [===•======] 0.8   │  │  Color:  [Vibrant         ▼]            │ │
│  │                    │  └──────────────────────────────────────────┘ │
│  │ Strength           │                                                │
│  │ (●) Subtle         │  ┌──────────────────────────────────────────┐ │
│  │ ( ) Moderate       │  │  📊 ITERATION                           │ │
│  │ ( ) Strong         │  ├──────────────────────────────────────────┤ │
│  └────────────────────┘  │  Generation History: 3                  │ │
│                          │                                          │ │
│  ┌────────────────────┐  │  ⭐⭐⭐⭐⭐  [thumb]  Speed: 0.8  🔒      │ │
│  │  ⏱ TIMING          │  │  ⭐⭐⭐⭐    [thumb]  Speed: 1.0         │ │
│  ├────────────────────┤  │  ⭐⭐⭐     [thumb]  Speed: 1.2         │ │
│  │ Duration 🔒        │  │                                          │ │
│  │ [====•=====] 5.0s  │  │  [Compare] [New Variation] [Export]    │ │
│  │                    │  └──────────────────────────────────────────┘ │
│  │ FPS                │                                                │
│  │ ( ) 24  (●) 30     │  ┌──────────────────────────────────────────┐ │
│  │ ( ) 60  ( ) 120    │  │  🎯 QUICK ACTIONS                       │ │
│  │                    │  ├──────────────────────────────────────────┤ │
│  └────────────────────┘  │  [Lock Selected Params]                 │ │
│                          │  [Apply Suggestions]                     │ │
│  ┌────────────────────┐  │  [Load Preset]                          │ │
│  │  🎭 MOTION         │  │  [Save as Preset]                       │ │
│  ├────────────────────┤  │  [Generate Video]                       │ │
│  │ Overall            │  └──────────────────────────────────────────┘ │
│  │ [====•=====] Mod.  │                                                │
│  │                    │                                                │
│  │ Subject   0.5      │                                                │
│  │ Camera    0.7      │                                                │
│  │ Background 0.3     │                                                │
│  │                    │                                                │
│  │ [✓] Motion Blur    │                                                │
│  │ [====•=====] 0.5   │                                                │
│  └────────────────────┘                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Auto Mode Interface

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ANIMAtiZE Director                                    ⚪ PRO  ⚫ AUTO  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                                                                          │
│                 ┌────────────────────────────────────┐                  │
│                 │                                    │                  │
│                 │       PREVIEW WINDOW               │                  │
│                 │                                    │                  │
│                 │  [  Generated Video Preview  ]     │                  │
│                 │                                    │                  │
│                 │                                    │                  │
│                 │    1920 × 1080  •  30fps  •  5s   │                  │
│                 └────────────────────────────────────┘                  │
│                                                                          │
│                                                                          │
│         ┌──────────────────────────────────────────────────┐           │
│         │  🎬 What type of content are you creating?      │           │
│         ├──────────────────────────────────────────────────┤           │
│         │                                                  │           │
│         │    ┌─────────┐  ┌─────────┐  ┌─────────┐       │           │
│         │    │ Product │  │Interview│  │Artistic │       │           │
│         │    └─────────┘  └─────────┘  └─────────┘       │           │
│         │                                                  │           │
│         │    ┌─────────┐  ┌─────────┐  ┌─────────┐       │           │
│         │    │  Sport  │  │  Story  │  │  Music  │       │           │
│         │    └─────────┘  └─────────┘  └─────────┘       │           │
│         │                                                  │           │
│         └──────────────────────────────────────────────────┘           │
│                                                                          │
│         ┌──────────────────────────────────────────────────┐           │
│         │  🎨 What mood do you want?                       │           │
│         ├──────────────────────────────────────────────────┤           │
│         │                                                  │           │
│         │    ┌─────────┐  ┌─────────┐  ┌─────────┐       │           │
│         │    │  Calm   │  │ Exciting│  │Dramatic │       │           │
│         │    └─────────┘  └─────────┘  └─────────┘       │           │
│         │                                                  │           │
│         │    ┌─────────┐  ┌─────────┐  ┌─────────┐       │           │
│         │    │Peaceful │  │Energetic│  │Mysterious│      │           │
│         │    └─────────┘  └─────────┘  └─────────┘       │           │
│         │                                                  │           │
│         └──────────────────────────────────────────────────┘           │
│                                                                          │
│         ┌──────────────────────────────────────────────────┐           │
│         │  ⏱ How long should it be?                       │           │
│         ├──────────────────────────────────────────────────┤           │
│         │                                                  │           │
│         │    ┌─────────┐  ┌─────────┐  ┌─────────┐       │           │
│         │    │Short 3s │  │Medium 5s│  │ Long 10s│       │           │
│         │    └─────────┘  └─────────┘  └─────────┘       │           │
│         │                                                  │           │
│         │              ┌──────────────┐                   │           │
│         │              │Extended  15s │                   │           │
│         │              └──────────────┘                   │           │
│         │                                                  │           │
│         └──────────────────────────────────────────────────┘           │
│                                                                          │
│                                                                          │
│                     ┌────────────────────────┐                          │
│                     │                        │                          │
│                     │   🎬 Generate Video   │                          │
│                     │                        │                          │
│                     └────────────────────────┘                          │
│                                                                          │
│                  Need more control? Switch to Pro Mode →                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Comparison View

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Generation Comparison                                     [Close ✕]    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐│
│  │   Generation 1     │  │   Generation 2 ⭐  │  │   Generation 3     ││
│  ├────────────────────┤  ├────────────────────┤  ├────────────────────┤│
│  │                    │  │                    │  │                    ││
│  │   [Video Thumb]    │  │   [Video Thumb]    │  │   [Video Thumb]    ││
│  │                    │  │                    │  │                    ││
│  ├────────────────────┤  ├────────────────────┤  ├────────────────────┤│
│  │ ⭐⭐⭐⭐            │  │ ⭐⭐⭐⭐⭐          │  │ ⭐⭐⭐              ││
│  │                    │  │                    │  │                    ││
│  │ Camera             │  │ Camera             │  │ Camera             ││
│  │  Movement: Dolly   │  │  Movement: Dolly🔒 │  │  Movement: Track   ││
│  │  Speed: 0.8        │  │  Speed: 1.0        │  │  Speed: 1.2        ││
│  │  Shot: Closeup 🔒  │  │  Shot: Closeup 🔒  │  │  Shot: Closeup 🔒  ││
│  │                    │  │                    │  │                    ││
│  │ Timing             │  │ Timing             │  │ Timing             ││
│  │  Duration: 5.0s 🔒 │  │  Duration: 5.0s 🔒 │  │  Duration: 5.0s 🔒 ││
│  │  FPS: 30 🔒        │  │  FPS: 30 🔒        │  │  FPS: 30 🔒        ││
│  │                    │  │                    │  │                    ││
│  │ Motion             │  │ Motion             │  │ Motion             ││
│  │  Strength: Subtle  │  │  Strength: Moderate│  │  Strength: Strong  ││
│  │                    │  │                    │  │                    ││
│  │ Notes:             │  │ Notes:             │  │ Notes:             ││
│  │ "Camera too slow,  │  │ "Perfect balance!  │  │ "Too fast, feels   ││
│  │  feels sluggish"   │  │  This is the one"  │  │  rushed and jerky" ││
│  │                    │  │                    │  │                    ││
│  │ [▶ Play]  [📝]    │  │ [▶ Play]  [📝]    │  │ [▶ Play]  [📝]    ││
│  │                    │  │                    │  │                    ││
│  └────────────────────┘  └────────────────────┘  └────────────────────┘│
│                                                                          │
│  Differences from Best (Gen 2):                                         │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │ Gen 1: camera.speed (-0.2), motion.strength (-1 level)            ││
│  │ Gen 3: camera.movement (Track), camera.speed (+0.2),              ││
│  │        motion.strength (+1 level)                                 ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  [Use Gen 2 Params] [Create Variation] [Export All] [Start Over]       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## API Reference

### Core Classes

#### DirectorControls
```python
class DirectorControls:
    """Main control container"""
    
    def __init__(
        self,
        control_id: str = auto,
        mode: DirectorMode = DirectorMode.AUTO,
        camera: CameraControl = CameraControl(),
        timing: TimingControl = TimingControl(),
        motion: MotionControl = MotionControl(),
        transition: Optional[TransitionControl] = None,
        **kwargs
    )
    
    def lock_parameter(
        self,
        parameter_name: str,
        value: Any,
        notes: str = ""
    ) -> None
    
    def unlock_parameter(
        self,
        parameter_name: str
    ) -> None
    
    def add_comparison(
        self,
        comparison: GenerationComparison
    ) -> None
    
    def get_best_generation(
        self
    ) -> Optional[GenerationComparison]
    
    def to_internal_params(
        self
    ) -> Dict[str, Any]
    
    def to_dict(
        self
    ) -> Dict[str, Any]
    
    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ) -> 'DirectorControls'
```

#### PresetLibrary
```python
class PresetLibrary:
    """Professional style presets"""
    
    @staticmethod
    def get_preset(
        preset_type: StylePreset
    ) -> DirectorControls
    
    @staticmethod
    def list_presets() -> List[Dict[str, str]]
```

#### IterationWorkflow
```python
class IterationWorkflow:
    """Iteration and refinement tools"""
    
    def __init__(
        self,
        controls: DirectorControls
    )
    
    def create_variation(
        self,
        parameter_changes: Dict[str, Any],
        preserve_locked: bool = True
    ) -> DirectorControls
    
    def compare_generations(
        self,
        generations: List[GenerationComparison]
    ) -> Dict[str, Any]
    
    def suggest_refinements(
        self,
        current_controls: DirectorControls,
        feedback: str
    ) -> List[Dict[str, Any]]
```

#### AutoModeAssistant
```python
class AutoModeAssistant:
    """Simplified control selection"""
    
    @staticmethod
    def suggest_controls(
        content_type: str,
        mood: str,
        duration: float
    ) -> DirectorControls
    
    @staticmethod
    def get_quick_options() -> Dict[str, List[str]]
```

### Usage Examples

#### Pro Mode Workflow
```python
from src.core.director_ux import (
    DirectorControls, DirectorMode, CameraMovementType,
    ShotType, StylePreset, PresetLibrary, IterationWorkflow
)

# Start with a preset
controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)

# Customize
controls.camera.speed = 0.8
controls.timing.duration = 7.0

# Lock good parameters
controls.lock_parameter("camera.movement_type", 
                       CameraMovementType.DOLLY.value,
                       "Perfect smooth dolly")
controls.lock_parameter("timing.fps", 30, "30fps is ideal")

# Generate
internal_params = controls.to_internal_params()
# ... send to video generator ...

# Iterate
workflow = IterationWorkflow(controls)
variation = workflow.create_variation({
    "camera.speed": 1.0,
    "motion.overall_strength": "strong"
})

# Compare
comparison = GenerationComparison(
    generation_id="gen_001",
    parameters=internal_params,
    rating=4,
    notes="Good but slightly slow"
)
controls.add_comparison(comparison)
```

#### Auto Mode Workflow
```python
from src.core.director_ux import AutoModeAssistant

# Simple 3-input generation
controls = AutoModeAssistant.suggest_controls(
    content_type="product",
    mood="exciting",
    duration=5.0
)

# Generate immediately
internal_params = controls.to_internal_params()
```

#### Refinement Workflow
```python
workflow = IterationWorkflow(controls)

# Get AI suggestions
suggestions = workflow.suggest_refinements(
    current_controls=controls,
    feedback="Camera moves too fast and creates motion sickness"
)

# Apply suggestions
for suggestion in suggestions:
    # Apply to controls...
    pass
```

---

## Integration with ANIMAtiZE Framework

### Connection to Existing Systems

```python
# Director UX → Prompt Expander → Model Adapters

from src.core.director_ux import DirectorControls, PresetLibrary, StylePreset
from src.core.prompt_expander import (
    PromptCompiler, DirectorIntent, Scene, Shot,
    CameraMotion, MotionStrength
)

# 1. Create director controls
controls = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
controls.timing.duration = 7.0

# 2. Convert to internal parameters
internal_params = controls.to_internal_params()

# 3. Create director intent for compilation
camera_motion = CameraMotion(
    motion_type=internal_params['camera_motion']['type'],
    strength=MotionStrength(internal_params['camera_motion']['strength']),
    speed=internal_params['camera_motion']['speed']
)

shot = Shot(
    shot_id="shot_001",
    scene_id="scene_001",
    prompt="Product showcase on elegant display",
    camera_motion=camera_motion,
    fps=internal_params['fps'],
    duration=internal_params['duration'],
    motion_strength=MotionStrength(internal_params['motion_strength'])
)

scene = Scene(
    scene_id="scene_001",
    description="Commercial product showcase",
    shots=[shot],
    scene_fps=internal_params['fps']
)

intent = DirectorIntent(
    intent_id="intent_001",
    narrative_description="Professional product commercial",
    visual_theme=internal_params['visual_style'],
    mood=internal_params['mood'],
    target_providers=['runway', 'pika'],
    scenes=[scene]
)

# 4. Compile to model-specific prompts
compiler = PromptCompiler()
result = compiler.compile(intent)

# 5. Access model-specific prompts
for model_prompt in result.model_prompts:
    print(f"Provider: {model_prompt.provider}")
    print(f"Prompt: {model_prompt.compiled_prompt}")
    print(f"Parameters: {model_prompt.control_parameters}")
```

---

## Summary

The Director UX Control Surface provides:

✅ **Professional Controls**: Full access to camera, timing, motion, and style parameters  
✅ **Dual Modes**: Pro mode for professionals, Auto mode for casual users  
✅ **Iteration Workflow**: Parameter locking, comparison, and refinement tools  
✅ **Style Presets**: 6 production-ready presets for common use cases  
✅ **Intelligent Mapping**: Seamless conversion to internal and model-specific parameters  
✅ **Extensible Design**: Easy to add new presets, controls, and models  

**Next Steps:**
1. Implement UI components based on wireframes
2. Add real-time preview integration
3. Build comparison visualization
4. Create preset customization interface
5. Add export/import for control configurations
