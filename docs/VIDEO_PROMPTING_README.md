# AI Video Prompting Implementation

## Overview

This implementation provides a comprehensive framework for generating optimized prompts for AI video generation models, with deep integration into ANIMAtiZE's 47+ cinematic movement prediction rules.

## Components

### 1. Video Prompting Catalog
**File:** `configs/video_prompting_catalog.json`

Complete catalog of 12 AI video models with:
- Prompt structure templates per model
- 50+ controllability parameters
- Temporal consistency guidelines
- Multi-scene coherence strategies
- Best practices and failure modes

**Models Covered:**
- Kling (Kwai) - Realistic cinematic scenes
- WAN - Dynamic scenes with audio sync
- Runway - Creative experimentation
- LTX & LTX 2 (Lightricks) - Temporal control
- Sora 2 (OpenAI) - Complex narratives
- Veo 3 & 3.1 (Google) - Audio-visual integration
- Higgsfield - Dynamic animations
- Luma - Professional camera control
- Pika - Expressive animations
- Stable Video Diffusion - Fine-tunable models

### 2. Video Prompt Analyzer
**File:** `src/analyzers/video_prompt_analyzer.py`

Analyzes and validates video prompts with:
- Model information retrieval
- Parameter validation
- Temporal consistency optimization
- Multi-scene coherence planning
- Prompt quality analysis
- Integration with ANIMAtiZE cinematic rules

**Key Classes:**
- `VideoPromptAnalyzer` - Main analyzer class
- `PromptStructure` - Structured prompt components
- `CameraMotion` - Camera movement configuration
- `TemporalConsistencyConfig` - Temporal parameters
- `SceneTransition` - Scene transition handling

### 3. Video Prompt Generator
**File:** `src/generators/video_prompt_generator.py`

Generates optimized prompts with:
- Natural language parsing
- Model-specific prompt formatting
- Automatic parameter optimization
- Multi-scene sequence generation
- Cinematic rule application

**Key Classes:**
- `VideoPromptGenerator` - Main generator class
- `VideoGenerationRequest` - Generation request specification

### 4. Rule Mapping
**File:** `configs/video_prompt_rule_mapping.json`

Maps video prompting parameters to ANIMAtiZE's movement prediction rules:
- 8 core movement rules mapped
- Parameter recommendations per rule
- Model-specific optimal configurations
- Workflow recommendations
- Integration examples

### 5. Documentation
**File:** `docs/video_prompting_research.md`

Complete research documentation covering:
- Model comparison and selection
- Prompt structures and patterns
- Controllability parameters
- Temporal consistency techniques
- Multi-scene coherence strategies
- Implementation examples

### 6. Tests
**File:** `tests/test_video_prompt_analyzer.py`

Comprehensive unit tests for all components.

## Quick Start

### Basic Single Scene Generation

```python
from src.generators.video_prompt_generator import (
    VideoPromptGenerator, 
    VideoGenerationRequest, 
    ModelType
)

generator = VideoPromptGenerator()

request = VideoGenerationRequest(
    model_type=ModelType.KLING,
    scene_description="A warrior stands on a cliff at sunrise, camera slowly dollies in",
    duration=8.0,
    aspect_ratio="16:9",
    style="cinematic",
    temporal_consistency_priority="high"
)

# Generate optimized prompt
prompt = generator.generate_prompt(request)

# Generate model parameters
parameters = generator.generate_model_parameters(request)

print(f"Prompt: {prompt}")
print(f"Parameters: {parameters}")
```

### Multi-Scene Sequence

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

# Access coherence analysis
print(f"Character Consistency: {multi_scene['coherence_analysis']['consistency_checks']['character_consistency']}")

# Iterate through scenes
for scene in multi_scene['scenes']:
    print(f"Scene {scene['scene_number']}: {scene['prompt']}")
```

### Analyzing Existing Prompts

```python
from src.analyzers.video_prompt_analyzer import VideoPromptAnalyzer, ModelType

analyzer = VideoPromptAnalyzer()

prompt = "A young woman in a red dress walks through a misty forest"

# Analyze quality
quality = analyzer.analyze_prompt_quality(prompt, ModelType.KLING)
print(f"Quality Score: {quality['score']}%")
print(f"Suggestions: {quality['suggestions']}")

# Get temporal critical parameters
critical_params = analyzer.get_temporal_critical_params(ModelType.KLING)
print(f"Critical Parameters: {critical_params}")
```

## Key Features

### 1. Temporal Consistency

The framework prioritizes temporal consistency through:
- **Fixed seeds** for reproducibility
- **Temporal weights** (0.7-0.9 recommended)
- **Motion strength** moderation (0.3-0.6)
- **Frame interpolation** control
- **Guidance scale** optimization

### 2. Multi-Scene Coherence

Maintains coherence across scenes via:
- **Character consistency** - Identical descriptions
- **Environmental continuity** - Consistent settings
- **Style uniformity** - Matching visual style
- **Seed sequencing** - base_seed + scene_index
- **Transition planning** - Fade, cut, dissolve

### 3. ANIMAtiZE Integration

Maps to 47+ cinematic rules:
- **movement_001** - Pose-to-Action Continuation
- **movement_002** - Composition-Guided Camera Flow
- **movement_003** - Physics-Based Environmental Motion
- **movement_004** - Emotional Momentum Analysis
- **movement_005** - Depth Layer Parallax
- **movement_006** - Atmospheric Response System
- **movement_007** - Interaction Anticipation
- **movement_008** - Emotional Framing Progression

### 4. Camera Motion Control

Professional camera movements:
- Static, Pan, Tilt, Zoom, Dolly, Orbit, Crane
- Speed control (slow, medium, fast)
- Direction specification
- Focal length configuration
- Camera type selection (tripod, steadicam, drone, handheld)

### 5. Model-Specific Optimization

Automatic parameter optimization per model:
- Kling: Cinematic camera movement, realistic character action
- WAN: Dynamic scenes, audio sync, stylistic flexibility
- Sora 2: Complex narratives, character consistency, long duration
- Luma: Professional camera control, cinematic composition
- Veo 3/3.1: Audio-visual integration, special effects
- LTX/LTX 2: Enhanced temporal control, object tracking

## Parameter Glossary

### Critical for Temporal Consistency

| Parameter | Type | Range | Impact | Models |
|-----------|------|-------|--------|--------|
| seed | integer | 0-2147483647 | Critical | All |
| temporal_weight/consistency | float | 0.0-1.0 | Critical | WAN, LTX, Sora2 |
| motion_strength | float | 0.0-1.0 | Critical | WAN, Runway, Kling |
| guidance_scale | float | 1.0-20.0 | Critical | Stable Diffusion |
| frame_interpolation | int | 24,30,60 | High | LTX, Higgsfield |

### Camera Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| camera_movement | static, pan, tilt, zoom, dolly, orbit, crane | Movement type |
| camera_type | tripod, steadicam, drone, handheld | Camera rig |
| focal_length | 14-200mm | Lens focal length |
| aperture | f/1.4-f/22 | Aperture setting |

### Audio Parameters

| Parameter | Type | Models | Use Case |
|-----------|------|--------|----------|
| audio_sync | boolean | Veo3, WAN | Music sync |
| beat_sync | boolean | Veo3 | Rhythmic motion |
| lip_sync | boolean | Veo3 | Dialogue |

## Best Practices

### For High Temporal Consistency

1. **Use fixed seeds** - Ensures reproducibility
2. **Moderate motion strength** - 0.3-0.6 for stability
3. **Specify gradual transitions** - "slowly dollies in over 3 seconds"
4. **Maintain consistent lighting** - Avoid sudden changes
5. **Use temporal anchors** - Beginning, middle, end descriptions

### For Multi-Scene Coherence

1. **Identical character descriptions** across all scenes
2. **Sequential seed strategy** - base_seed + scene_index
3. **Consistent style descriptors** - Same visual style throughout
4. **Planned transitions** - Choose appropriate transition types
5. **Environmental continuity** - Maintain location consistency

### For Professional Results

1. **Specify camera movement details** - Type, speed, direction
2. **Define lighting explicitly** - Quality, direction, color
3. **Include atmospheric elements** - Weather, mood, atmosphere
4. **Use cinematic language** - Professional terminology
5. **Test iteratively** - Refine based on results

## Common Failure Modes & Solutions

### Temporal Artifacts (Flickering)
- ✅ Increase temporal_consistency to 0.85-0.95
- ✅ Reduce motion_strength to 0.3-0.5
- ✅ Use fixed seed
- ✅ Add "smooth" and "gradual" keywords

### Character Inconsistency
- ✅ Use identical character descriptions
- ✅ Enable character_consistency (Sora 2)
- ✅ Use object_tracking (LTX 2)
- ✅ Increase temporal_weight

### Motion Instability
- ✅ Increase motion_smoothness
- ✅ Specify movement timing
- ✅ Use appropriate camera_type
- ✅ Add motion blur

### Audio Desynchronization
- ✅ Enable audio_sync parameter
- ✅ Use beat_sync for rhythmic content
- ✅ Enable lip_sync for dialogue
- ✅ Test with shorter durations

## Integration with ANIMAtiZE Rules

The video prompting system automatically maps camera movements to ANIMAtiZE's cinematic rules:

```python
from src.generators.video_prompt_generator import VideoPromptGenerator
from src.analyzers.video_prompt_analyzer import CameraMotion

generator = VideoPromptGenerator()

# Camera motion automatically maps to rules
camera = CameraMotion(type="dolly", speed="slow", direction="in")

# Get applicable cinematic rules
structure = generator.generate_prompt_structure(request)
enhancements = generator.apply_cinematic_rules(structure)

print(f"Applicable Rules: {enhancements['applicable_rules']}")
```

## File Structure

```
configs/
  ├── video_prompting_catalog.json          # Complete model catalog
  ├── video_prompt_rule_mapping.json        # ANIMAtiZE rule mapping
  └── movement_prediction_rules.json        # Core cinematic rules

src/
  ├── analyzers/
  │   └── video_prompt_analyzer.py          # Prompt analysis
  └── generators/
      └── video_prompt_generator.py         # Prompt generation

docs/
  ├── video_prompting_research.md           # Research documentation
  └── VIDEO_PROMPTING_README.md             # This file

tests/
  └── test_video_prompt_analyzer.py         # Unit tests
```

## Usage Examples

### Example 1: Product Video

```python
request = VideoGenerationRequest(
    model_type=ModelType.LUMA,
    scene_description="Smartphone rotating on black background with dynamic lighting",
    duration=5.0,
    style="commercial",
    temporal_consistency_priority="critical",
    custom_parameters={
        "camera_type": "tripod",
        "focal_length": 85,
        "aperture": "f/2.8"
    }
)
```

### Example 2: Action Sequence

```python
request = VideoGenerationRequest(
    model_type=ModelType.KLING,
    scene_description="Parkour athlete leaping between rooftops, camera tracking",
    duration=10.0,
    style="cinematic",
    temporal_consistency_priority="high",
    custom_parameters={
        "camera_movement": "dolly",
        "motion_strength": 0.7,
        "frame_rate": 60
    }
)
```

### Example 3: Dialogue Scene

```python
request = VideoGenerationRequest(
    model_type=ModelType.VEO3,
    scene_description="Two people conversing in a cafe, intimate lighting",
    duration=15.0,
    style="realistic",
    include_audio=True,
    custom_parameters={
        "lip_sync": True,
        "camera_type": "steadicam"
    }
)
```

## Testing

Run comprehensive unit tests:

```bash
python -m pytest tests/test_video_prompt_analyzer.py -v
```

## Future Enhancements

- [ ] NLP-based scene description parsing
- [ ] Real-time parameter tuning interface
- [ ] Model performance benchmarking
- [ ] Automated A/B testing framework
- [ ] Style transfer between models
- [ ] Batch generation workflows

## References

- Source Document: `ai-video-prompting-guide_PL-EN.md` (2025-10-26)
- ANIMAtiZE Framework: `movement_prediction_rules.json`
- Model Documentation: Individual vendor APIs

## Contributing

When extending this framework:
1. Add new models to `video_prompting_catalog.json`
2. Update parameter mappings in `video_prompt_rule_mapping.json`
3. Extend analyzer/generator classes as needed
4. Add comprehensive tests
5. Update documentation

## License

See main project LICENSE file.
