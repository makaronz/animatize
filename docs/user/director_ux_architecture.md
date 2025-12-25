# Director UX Control Surface - Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE LAYER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────┐              ┌─────────────────────────────┐   │
│  │     AUTO MODE UI      │              │      PRO MODE UI            │   │
│  ├───────────────────────┤              ├─────────────────────────────┤   │
│  │  Content Type [▼]     │              │  Camera Controls            │   │
│  │  Mood [▼]            │              │  ├─ Movement [▼]           │   │
│  │  Duration [▼]        │              │  ├─ Shot Type [▼]          │   │
│  │                       │              │  ├─ Angle [▼]             │   │
│  │  [Generate]           │              │  ├─ Speed [═══●══]        │   │
│  └───────────────────────┘              │  └─ Focal Length [▼]      │   │
│             │                            │                             │   │
│             │                            │  Timing Controls            │   │
│             │                            │  ├─ Duration [═══●══]      │   │
│             │                            │  ├─ FPS (○ 24 ● 30)       │   │
│             │                            │  └─ Speed Factor [▼]      │   │
│             │                            │                             │   │
│             │                            │  Motion Controls            │   │
│             │                            │  ├─ Strength [▼]          │   │
│             │                            │  ├─ Subject [═══●══]      │   │
│             │                            │  └─ Camera [═══●══]       │   │
│             │                            │                             │   │
│             │                            │  [Lock Params] [Generate]   │   │
│             │                            └─────────────────────────────┘   │
│             │                                         │                    │
└─────────────┼─────────────────────────────────────────┼────────────────────┘
              │                                         │
              ▼                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DIRECTOR UX CONTROL LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐                          ┌──────────────────┐        │
│  │ AutoModeAssistant│                          │ DirectorControls │        │
│  ├──────────────────┤                          ├──────────────────┤        │
│  │ suggest_controls │                          │  control_id      │        │
│  │ get_options      │                          │  mode: auto/pro  │        │
│  └────────┬─────────┘                          │                  │        │
│           │                                    │  ┌─────────────┐ │        │
│           └──────────────────┐                 │  │CameraControl│ │        │
│                              │                 │  ├─────────────┤ │        │
│  ┌──────────────────┐        │                 │  │movement_type│ │        │
│  │  PresetLibrary   │        │                 │  │shot_type    │ │        │
│  ├──────────────────┤        │                 │  │angle        │ │        │
│  │ get_preset()     │────────┼────────────────▶│  │speed        │ │        │
│  │ list_presets()   │        │                 │  │focal_length │ │        │
│  │                  │        │                 │  └─────────────┘ │        │
│  │ Presets:         │        │                 │                  │        │
│  │ - Documentary    │        │                 │  ┌─────────────┐ │        │
│  │ - Commercial     │        │                 │  │TimingControl│ │        │
│  │ - Art House      │        │                 │  ├─────────────┤ │        │
│  │ - Action         │        │                 │  │duration     │ │        │
│  │ - Drama          │        │                 │  │fps          │ │        │
│  │ - Music Video    │        │                 │  │speed_factor │ │        │
│  └──────────────────┘        │                 │  └─────────────┘ │        │
│                              │                 │                  │        │
│  ┌──────────────────┐        │                 │  ┌─────────────┐ │        │
│  │IterationWorkflow │        │                 │  │MotionControl│ │        │
│  ├──────────────────┤        │                 │  ├─────────────┤ │        │
│  │create_variation()│◀───────┘                 │  │strength     │ │        │
│  │compare_gens()    │                          │  │subject      │ │        │
│  │suggest_refine()  │                          │  │camera       │ │        │
│  └──────────────────┘                          │  │motion_blur  │ │        │
│                                                 │  └─────────────┘ │        │
│                                                 │                  │        │
│                                                 │  locked_params[] │        │
│                                                 │  gen_history[]   │        │
│                                                 └────────┬─────────┘        │
│                                                          │                  │
└──────────────────────────────────────────────────────────┼──────────────────┘
                                                           │
                                                           │ to_internal_params()
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARAMETER MAPPING LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Internal Parameter Format:                                                │
│  {                                                                          │
│    "camera_motion": {                                                       │
│      "type": "dolly",                                                       │
│      "speed": 0.8,                                                          │
│      "strength": "moderate"                                                 │
│    },                                                                       │
│    "camera_angle": "eye_level",                                             │
│    "shot_type": "closeup",                                                  │
│    "focal_length": 50,                                                      │
│    "duration": 7.0,                                                         │
│    "fps": 30,                                                               │
│    "motion_strength": "moderate",                                           │
│    "visual_style": "cinematic",                                             │
│    "mood": "dramatic",                                                      │
│    ...                                                                      │
│  }                                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MODEL ADAPTER LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌─────────────┐│
│  │Runway Adapter│   │ Pika Adapter │   │ Sora Adapter │   │ Veo Adapter ││
│  ├──────────────┤   ├──────────────┤   ├──────────────┤   ├─────────────┤│
│  │ duration     │   │ fps          │   │ duration     │   │ duration_s  ││
│  │ fps          │   │ motion (0-1) │   │ resolution   │   │ fps         ││
│  │ motion (0-10)│   │ camera{      │   │ seed         │   │ camera      ││
│  │ camera_motion│   │   pan: ±1.0  │   │ style        │   │ seed        ││
│  │ seed         │   │   tilt: ±1.0 │   │              │   │             ││
│  │ image_prompt │   │   zoom: ±1.0 │   │              │   │             ││
│  │              │   │ }            │   │              │   │             ││
│  │              │   │ seed         │   │              │   │             ││
│  └──────────────┘   └──────────────┘   └──────────────┘   └─────────────┘│
│         │                  │                   │                  │        │
└─────────┼──────────────────┼───────────────────┼──────────────────┼────────┘
          │                  │                   │                  │
          ▼                  ▼                   ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VIDEO GENERATION APIs                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    Runway Gen-3          Pika 1.5          OpenAI Sora        Google Veo   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────┐
│   USER   │
└────┬─────┘
     │
     │ Select Mode / Input Parameters
     ▼
┌─────────────────────────────────────┐
│      Choose Operating Mode          │
│                                     │
│  ┌──────────┐      ┌─────────────┐ │
│  │   AUTO   │  OR  │     PRO     │ │
│  └────┬─────┘      └──────┬──────┘ │
└───────┼────────────────────┼────────┘
        │                    │
        │                    │
        ▼                    ▼
┌───────────────┐    ┌──────────────────┐
│Auto Assistant │    │ Manual Controls  │
│- content_type │    │ - Camera         │
│- mood         │    │ - Timing         │
│- duration     │    │ - Motion         │
│               │    │ - Style          │
│  ↓ suggests   │    │ - Transitions    │
│  preset       │    │                  │
└───────┬───────┘    └────────┬─────────┘
        │                     │
        └──────────┬──────────┘
                   │
                   ▼
           ┌───────────────┐
           │DirectorControls│
           └───────┬───────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
    Camera     Timing     Motion
    Control    Control    Control
        │          │          │
        └──────────┼──────────┘
                   │
                   │ to_internal_params()
                   ▼
         ┌─────────────────┐
         │Internal Params  │
         │ (Unified Format)│
         └────────┬────────┘
                  │
         ┌────────┼────────┐
         │        │        │
         ▼        ▼        ▼
      Runway    Pika    Sora
      Adapter   Adapter Adapter
         │        │        │
         ▼        ▼        ▼
      Runway    Pika    Sora
       API       API     API
         │        │        │
         └────────┼────────┘
                  │
                  ▼
           ┌────────────┐
           │   VIDEO    │
           └────────────┘
```

## Iteration Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  START: Initial Controls                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   Generate    │
                 │   Video #1    │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   Review &    │
                 │   Evaluate    │
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
      ┌──────────────┐      ┌─────────────┐
      │ Satisfactory?│      │ Needs Work? │
      │     YES      │      │     NO      │
      └──────┬───────┘      └──────┬──────┘
             │                     │
             │                     ▼
             │              ┌─────────────────┐
             │              │ Lock Good Params│
             │              │ - camera.motion │
             │              │ - timing.fps    │
             │              │ - etc.          │
             │              └────────┬────────┘
             │                       │
             │                       ▼
             │              ┌─────────────────┐
             │              │ Create Variation│
             │              │ - Modify unlocked│
             │              │   parameters    │
             │              │ - Generate new ID│
             │              └────────┬────────┘
             │                       │
             │                       ▼
             │              ┌─────────────────┐
             │              │  Generate #2    │
             │              └────────┬────────┘
             │                       │
             │                       ▼
             │              ┌─────────────────┐
             │              │ Add to Comparison│
             │              │ - Store params  │
             │              │ - Add rating    │
             │              │ - Add notes     │
             │              └────────┬────────┘
             │                       │
             │                       ▼
             │              ┌─────────────────┐
             │              │  Compare All    │
             │              │  Generations    │
             │              └────────┬────────┘
             │                       │
             │                       ▼
             │              ┌─────────────────┐
             │              │ Select Best or  │
             │              │ Create New      │
             │              │ Variation       │
             │              └────────┬────────┘
             │                       │
             │                       │ Loop back
             │              ┌────────┘
             │              │
             ▼              ▼
      ┌─────────────────────────────┐
      │  COMPLETE: Export Best      │
      │  - Best generation params   │
      │  - Locked parameters        │
      │  - Ready for production     │
      └─────────────────────────────┘
```

## Preset Application Flow

```
┌──────────────────────┐
│  User Selects Preset │
│  (e.g., "Commercial")│
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────────────────┐
│      PresetLibrary.get_preset()        │
└────────────────┬───────────────────────┘
                 │
                 ▼
       ┌─────────────────────┐
       │  Load Preset Config │
       │                     │
       │  Camera:            │
       │    movement: dolly  │
       │    shot: medium     │
       │    speed: 0.6       │
       │                     │
       │  Timing:            │
       │    duration: 5.0    │
       │    fps: 30          │
       │                     │
       │  Motion:            │
       │    strength: mod    │
       │    blur: true       │
       │                     │
       │  Style:             │
       │    visual: polished │
       │    mood: aspir...   │
       │    grade: vibrant   │
       └──────────┬──────────┘
                  │
                  ▼
        ┌──────────────────┐
        │Apply to Controls │
        └──────────┬───────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
   ┌─────────┐        ┌───────────┐
   │ As-Is   │   OR   │Customize  │
   │ Usage   │        │Parameters │
   └────┬────┘        └─────┬─────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
         ┌────────────────┐
         │to_internal_    │
         │params()        │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │Ready for Video │
         │Generation      │
         └────────────────┘
```

## Class Hierarchy

```
DirectorControls (Main Container)
│
├── control_id: str
├── mode: DirectorMode (AUTO | PRO)
│
├── camera: CameraControl
│   ├── movement_type: CameraMovementType
│   ├── angle: CameraAngle
│   ├── shot_type: ShotType
│   ├── focal_length: int
│   ├── speed: float
│   ├── strength: MotionStrengthLevel
│   ├── easing: str
│   └── timing: (start_time, end_time)
│
├── timing: TimingControl
│   ├── duration: float
│   ├── fps: int
│   ├── speed_factor: float
│   └── start_offset: float
│
├── motion: MotionControl
│   ├── overall_strength: MotionStrengthLevel
│   ├── subject_motion: float
│   ├── camera_motion: float
│   ├── background_motion: float
│   ├── motion_blur: bool
│   └── motion_blur_amount: float
│
├── transition: TransitionControl (Optional)
│   ├── style: TransitionStyle
│   ├── duration: float
│   ├── offset: float
│   └── parameters: dict
│
├── style_preset: StylePreset (Optional)
│
├── visual_style: str
├── mood: str
├── color_grade: str
├── depth_of_field: float
├── lighting_style: str
├── composition_rule: str
├── aspect_ratio: str
│
├── locked_parameters: dict[str, ParameterLock]
│   └── ParameterLock
│       ├── locked: bool
│       ├── locked_at: datetime
│       ├── locked_value: Any
│       └── notes: str
│
└── generation_history: list[GenerationComparison]
    └── GenerationComparison
        ├── generation_id: str
        ├── parameters: dict
        ├── result_url: str
        ├── thumbnail_url: str
        ├── rating: int (1-5)
        ├── notes: str
        └── created_at: datetime
```

## Parameter Mapping Flow

```
DirectorControls (UX Layer)
       │
       │ User-friendly names & ranges
       │
       ▼
┌──────────────────────────────────────┐
│     to_internal_params()             │
│                                      │
│  camera.movement_type                │
│    → camera_motion.type              │
│                                      │
│  camera.speed                        │
│    → camera_motion.speed             │
│                                      │
│  timing.duration                     │
│    → duration                        │
│                                      │
│  motion.overall_strength             │
│    → motion_strength                 │
│                                      │
│  ... (all mappings)                  │
└───────────────┬──────────────────────┘
                │
                ▼
Internal Parameters (Unified Format)
                │
                │ Model-agnostic
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌────────┐  ┌────────┐  ┌────────┐
│Runway  │  │ Pika   │  │ Sora   │
│Adapter │  │Adapter │  │Adapter │
└───┬────┘  └───┬────┘  └───┬────┘
    │           │           │
    │ Model-specific formats│
    │           │           │
    ▼           ▼           ▼
 Runway       Pika       Sora
  API          API        API
```

## State Management

```
┌───────────────────────────────────────────┐
│         DirectorControls State            │
├───────────────────────────────────────────┤
│                                           │
│  Current Configuration                    │
│  ├─ camera: {...}                         │
│  ├─ timing: {...}                         │
│  ├─ motion: {...}                         │
│  └─ style: {...}                          │
│                                           │
│  Lock State                               │
│  └─ locked_parameters: {                  │
│       "camera.speed": {                   │
│         locked: true,                     │
│         value: 0.8,                       │
│         notes: "Perfect"                  │
│       }                                   │
│     }                                     │
│                                           │
│  Iteration History                        │
│  └─ generation_history: [                 │
│       {                                   │
│         id: "gen_001",                    │
│         params: {...},                    │
│         rating: 4,                        │
│         notes: "Good"                     │
│       },                                  │
│       {...}                               │
│     ]                                     │
│                                           │
│  Metadata                                 │
│  ├─ control_id: "ctrl_123"                │
│  ├─ created_at: timestamp                 │
│  ├─ modified_at: timestamp                │
│  └─ version: "1.0"                        │
│                                           │
└───────────────────────────────────────────┘
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────┐
│                   User Actions                          │
└───┬─────────────────────────────────────────────────────┘
    │
    ├─ Select Preset ───────────────▶ PresetLibrary
    │                                      │
    │                                      ▼
    │                                 DirectorControls
    │                                      ▲
    ├─ Adjust Parameters ─────────────────┤
    │                                      │
    ├─ Lock Parameter ────────────────────┤
    │                                      │
    ├─ Create Variation ──────────────▶ IterationWorkflow
    │                                      │
    │                                      ▼
    │                                 New DirectorControls
    │                                      │
    ├─ Add Comparison ────────────────────┤
    │                                      │
    ├─ Get Suggestions ───────────────▶ IterationWorkflow
    │                                      │
    │                                      ▼
    │                                 Refinement Suggestions
    │                                      │
    └─ Generate Video ────────────────────┤
                                           │
                                           ▼
                                    Internal Parameters
                                           │
                                           ▼
                                      Model Adapters
                                           │
                                           ▼
                                      Video Generation
```

---

This architecture enables:

1. **Separation of Concerns**: UI → Controls → Parameters → Adapters
2. **Mode Flexibility**: Auto for simplicity, Pro for control
3. **Iteration Support**: Lock, compare, refine workflow
4. **Model Agnostic**: Unified internal format adapts to any model
5. **State Management**: Complete history and tracking
6. **Extensibility**: Easy to add new controls, presets, or models
