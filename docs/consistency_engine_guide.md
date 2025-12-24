# Consistency Engine - Complete Implementation Guide

## Overview

The Consistency Engine is a comprehensive system designed to maintain character, world, and style consistency across video shots. It solves the critical pain point of cross-shot consistency that competitors struggle with.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Consistency Engine                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  Reference     │  │   Style      │  │  Cross-Shot     │ │
│  │  Management    │  │  Extraction  │  │  Validation     │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  Character     │  │  Continuity  │  │  Reference      │ │
│  │  References    │  │  Rules       │  │  Library        │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   Scene Analyzer        │
              │   Integration           │
              └─────────────────────────┘
```

## Data Models

### 1. StyleAnchor

Defines a consistent visual style for the project.

```python
StyleAnchor(
    anchor_id: str              # Unique identifier
    name: str                   # Human-readable name
    description: str            # Style description
    style_embedding: ndarray    # 64-dim style vector
    color_palette: List[RGB]    # Dominant colors
    texture_profile: Dict       # Texture characteristics
    lighting_style: Dict        # Lighting parameters
    composition_rules: List     # Composition guidelines
    reference_images: List      # Reference image paths
)
```

**Example:**
```python
fantasy_style = StyleAnchor(
    anchor_id="fantasy_epic_01",
    name="Epic Fantasy Style",
    description="Vibrant colors with dramatic lighting",
    style_embedding=np.array([...]),
    color_palette=[(135, 206, 235), (34, 139, 34)],
    lighting_style={
        "intensity": "high",
        "color_temperature": 6000,
        "quality": "dramatic"
    }
)
```

### 2. CharacterReference

Maintains character identity across shots.

```python
CharacterReference(
    character_id: str           # Unique identifier
    name: str                   # Character name
    description: str            # Physical description
    appearance_embedding: ndarray  # 64-dim appearance vector
    facial_features: Dict       # Eye color, hair, etc.
    body_proportions: Dict      # Height, build measurements
    clothing: Dict              # Outfit descriptions
    color_scheme: List[RGB]     # Character color palette
    distinctive_marks: List     # Scars, tattoos, etc.
    reference_images: List      # Reference image paths
    expression_variants: Dict   # Different expressions
)
```

**Example:**
```python
hero = CharacterReference(
    character_id="hero_001",
    name="Alex the Brave",
    description="Young warrior with silver armor",
    appearance_embedding=np.array([...]),
    facial_features={
        "eye_color": "blue",
        "hair_color": "brown",
        "hair_style": "short"
    },
    clothing={
        "primary": "silver armor",
        "secondary": "blue cape"
    }
)
```

### 3. WorldReference

Maintains spatial and environmental consistency.

```python
WorldReference(
    world_id: str               # Unique identifier
    name: str                   # Location name
    description: str            # Environment description
    spatial_embedding: ndarray  # 64-dim spatial vector
    location_map: Dict          # 3D positions of landmarks
    lighting_conditions: Dict   # Environment lighting
    time_of_day: str           # Morning, noon, night, etc.
    weather: str               # Weather conditions
    architectural_style: str   # Building/environment style
    scale_references: Dict     # Size measurements
    spatial_relationships: Dict # How objects relate spatially
)
```

**Example:**
```python
castle = WorldReference(
    world_id="castle_exterior_01",
    name="Grand Castle",
    description="Medieval fortress with towers",
    spatial_embedding=np.array([...]),
    location_map={
        "main_gate": (0.5, 0.6, 0.0),
        "north_tower": (0.3, 0.2, 0.8)
    },
    time_of_day="midday",
    weather="clear"
)
```

### 4. ReferenceFrame

Stores extracted features from each frame.

```python
ReferenceFrame(
    frame_id: str               # Unique identifier
    shot_id: str                # Parent shot ID
    timestamp: float            # Time in shot (seconds)
    embeddings: Dict[str, ndarray]  # Feature embeddings
    color_histogram: ndarray    # Color distribution
    lighting_profile: Dict      # Lighting parameters
    character_positions: Dict   # Character locations (x, y)
    object_registry: Dict       # Detected objects
    style_anchor_id: str        # Associated style anchor
    character_ids: Set[str]     # Present characters
    world_id: str              # Associated world
)
```

## Continuity Rules

### ColorConsistencyRule

Maintains consistent color grading across shots.

- **Threshold:** 0.1 (configurable)
- **Metric:** Color histogram distance
- **Evaluation:** Returns 0-1 score, where 1 = perfect match

```python
rule = ColorConsistencyRule(threshold=0.1)
score = rule.evaluate(frame_a, frame_b)
```

### LightingContinuityRule

Ensures consistent lighting across shots.

- **Threshold:** 0.15 (configurable)
- **Metrics:** 
  - Intensity difference
  - Color temperature difference
- **Evaluation:** Combined normalized score

```python
rule = LightingContinuityRule(threshold=0.15)
score = rule.evaluate(frame_a, frame_b)
```

### SpatialCoherenceRule

Maintains spatial relationships between objects.

- **Threshold:** 0.2 (configurable)
- **Metric:** Position distance in normalized space
- **Evaluation:** Average coherence for common objects

```python
rule = SpatialCoherenceRule(threshold=0.2)
score = rule.evaluate(frame_a, frame_b)
```

## Reference Library Storage

The reference library organizes and persists all references:

```
data/reference_library/
├── characters/
│   ├── hero_001.json
│   ├── villain_002.json
│   └── ...
├── styles/
│   ├── fantasy_style_01.json
│   ├── noir_style_02.json
│   └── ...
├── worlds/
│   ├── castle_exterior_01.json
│   ├── forest_interior_01.json
│   └── ...
└── frames/
    ├── frame_001.pkl
    ├── frame_002.pkl
    └── ...
```

### Operations

```python
library = ReferenceLibrary(storage_path="data/reference_library")

# Add references
library.add_character(character)
library.add_style_anchor(style)
library.add_world(world)
library.add_frame(frame)

# Retrieve references
char = library.get_character("hero_001")
style = library.get_style("fantasy_style_01")
world = library.get_world("castle_exterior_01")

# Find similar items
similar = library.find_similar_characters(query_embedding, top_k=5)
similar = library.find_similar_styles(query_embedding, top_k=5)

# Export entire library
library.export_library("backup.tar.gz")
```

## Scene Analyzer Integration

The consistency engine integrates with `scene_analyzer.py` for automatic style extraction.

### From Scene Analysis

```python
from src.analyzers.scene_analyzer import SceneAnalyzer

analyzer = SceneAnalyzer()
scene_analysis = analyzer.analyze_image("frame.jpg")

# Create reference frame from scene analysis
frame = engine.integrate_scene_analysis(
    frame_id="frame_001",
    scene_analysis=scene_analysis,
    shot_id="shot_001",
    timestamp=0.5
)
```

### Direct from Image

```python
# Create reference frame directly from image
frame = engine.create_reference_from_image(
    frame_id="frame_001",
    image_path="frame.jpg",
    shot_id="shot_001",
    timestamp=0.5
)
```

### Extracted Features

The style extractor analyzes:

1. **Color Palette:** Dominant colors via k-means clustering
2. **Lighting:** Brightness, contrast, intensity distribution
3. **Texture:** Edge density, smoothness, detail level
4. **Composition:** Symmetry, complexity, rule of thirds

## Cross-Shot Consistency Validation

### Validation Process

```python
validator = CrossShotValidator(reference_library)

# Validate sequence of frames
result = validator.validate_shot_sequence(frames, context={})

# Result structure:
{
    "violations": [...],           # List of violations
    "rule_scores": {...},          # Scores per rule
    "overall_consistency": 0.92,   # Overall score
    "total_checks": 10,            # Number of comparisons
    "passed": True                 # Whether it passed thresholds
}
```

### Character Consistency

```python
# Validate specific character across shots
result = validator.validate_character_consistency(
    character_id="hero_001",
    shots=[frame1, frame2, frame3]
)

# Result:
{
    "character_id": "hero_001",
    "character_name": "Alex",
    "appearances": 3,
    "mean_similarity": 0.94,
    "min_similarity": 0.89,
    "violations": [],
    "consistency_rating": "high"
}
```

## Usage Examples

### Basic Usage with Orchestrator

```python
from src.wedge_features.consistency_integration import ConsistencyOrchestrator

orchestrator = ConsistencyOrchestrator(
    storage_path="data/reference_library",
    enable_scene_analyzer=True
)

# Process a shot image
frame = orchestrator.process_shot_image(
    image_path="shot_001_frame_000.jpg",
    shot_id="shot_001",
    timestamp=0.0
)

# Create style anchor from reference image
style = orchestrator.create_style_anchor_from_image(
    image_path="style_reference.jpg",
    anchor_id="epic_fantasy",
    name="Epic Fantasy Style",
    description="Dramatic fantasy with vibrant colors"
)

# Validate shot consistency
validation = orchestrator.validate_shot_consistency("shot_001")
print(f"Consistency score: {validation['scores']['overall']:.3f}")
```

### Using Middleware

```python
from src.wedge_features.consistency_integration import ConsistencyMiddleware

middleware = ConsistencyMiddleware(orchestrator, auto_validate=True)

# Start shot
middleware.before_shot("shot_001")

# Process frames (auto-validates)
for i, frame_path in enumerate(frame_paths):
    result = middleware.after_frame_generated(
        image_path=frame_path,
        timestamp=i * 0.5
    )
    
    if result and result.get('violations'):
        print(f"Warning: {len(result['violations'])} violations detected")

# Complete shot
final_validation = middleware.after_shot()
```

### Sequence Validation

```python
# Validate consistency across multiple shots
result = orchestrator.validate_sequence_consistency(
    shot_ids=["shot_001", "shot_002", "shot_003"]
)

# Generate comprehensive report
report = result['report']
print(f"Overall consistency: {report['summary']['consistency_score']:.3f}")
print(f"Total violations: {report['summary']['total_violations']}")

for violation in report['violations']:
    print(f"- {violation['type']}: {violation['description']}")
    print(f"  Fix: {violation['suggested_fix']}")
```

### Style Consistency Report

```python
# Check style consistency against anchor
report = orchestrator.get_style_consistency_report(
    style_anchor_id="epic_fantasy",
    shot_ids=["shot_001", "shot_002"]
)

print(f"Mean similarity: {report['mean_similarity']:.3f}")
print(f"Violations: {len(report['violations'])}")
```

## Configuration

Edit `configs/consistency_engine.json`:

```json
{
  "thresholds": {
    "character_identity": 0.95,
    "lighting": 0.85,
    "color_grading": 0.90,
    "spatial_relationship": 0.88
  },
  "continuity_rules": {
    "color_consistency": {
      "enabled": true,
      "threshold": 0.1,
      "weight": 1.0
    }
  },
  "validation": {
    "min_frames_per_shot": 2,
    "cache_embeddings": true
  }
}
```

## Performance Metrics

The Consistency Engine targets:

- **Cross-shot consistency:** >85% match
- **Character identity:** >95% F1 score
- **Lighting coherence:** <10% ΔRGB variance
- **Spatial accuracy:** <5% position deviation

## Best Practices

### 1. Reference Collection

- Create style anchors from hero frames
- Use multiple reference images per character
- Document distinctive features explicitly

### 2. Validation Strategy

- Validate after each shot completion
- Use auto-validation during generation
- Review violations with severity > 0.5

### 3. Consistency Maintenance

- Apply style anchors consistently
- Use reference frames for regeneration
- Track consistency history for learning

### 4. Error Handling

- Handle missing references gracefully
- Log validation failures
- Provide actionable fix suggestions

## Troubleshooting

### Low Consistency Scores

1. Check reference quality
2. Verify style anchor matches intent
3. Review lighting parameters
4. Adjust thresholds if needed

### High False Positive Rate

1. Increase thresholds
2. Disable strict rules
3. Review continuity rule weights
4. Check for noise in embeddings

### Storage Issues

1. Enable compression
2. Limit cache size
3. Regular backup and cleanup
4. Use frame sampling for validation

## API Reference

See inline documentation in:
- `src/wedge_features/consistency_engine.py`
- `src/wedge_features/consistency_integration.py`

## Testing

Run comprehensive tests:

```bash
python tests/test_consistency_engine.py
```

Run examples:

```bash
python examples/consistency_engine_usage.py
```

## Future Enhancements

- Deep learning-based embeddings
- Real-time validation UI
- Automated fix suggestions with image manipulation
- Multi-modal consistency (audio + visual)
- Temporal smoothing algorithms
