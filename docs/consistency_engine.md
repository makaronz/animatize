# Consistency Engine Documentation

## Overview

The Consistency Engine is a comprehensive system for maintaining visual consistency across video generation shots. It provides character identity preservation, style coherence, lighting continuity, and spatial relationship management.

## Features

### 1. Reference Management

#### Character References
- Store and manage character appearance data
- Track facial features, body proportions, clothing
- Maintain appearance embeddings for similarity matching
- Support multiple expression and pose variants

#### Style Anchors
- Define and enforce visual style consistency
- Manage color palettes and composition rules
- Track texture profiles and lighting styles
- Support reference image collections

#### World References
- Maintain spatial consistency for environments
- Track location maps and spatial relationships
- Define lighting conditions and architectural styles
- Store scale references for accurate positioning

### 2. Continuity Rules

The engine enforces various continuity rules across shots:

#### Color Consistency
- Monitors color grading across frames
- Compares color histograms between shots
- Threshold: 0.1 (configurable)
- Weight: 1.0

#### Lighting Continuity
- Tracks lighting intensity and color temperature
- Validates lighting direction and quality
- Threshold: 0.15 (configurable)
- Weight: 1.2

#### Spatial Coherence
- Validates object and character positions
- Maintains spatial relationships between elements
- Threshold: 0.2 (configurable)
- Weight: 1.0

### 3. Style Extraction

Integrates with `scene_analyzer.py` to extract:

- **Color Palette**: Dominant colors from scene analysis
- **Composition Style**: Rule of thirds adherence, symmetry patterns
- **Lighting Style**: Intensity, direction, quality characteristics
- **Texture Profile**: Complexity, smoothness, detail level
- **Scene Atmosphere**: Overall mood and aesthetic

### 4. Embeddings

Multiple embedding types for similarity comparison:

- **Visual Embeddings** (512D): General visual features
- **Style Embeddings** (64D): Style-specific characteristics
- **Character Embeddings** (256D): Character appearance features
- **World Embeddings** (128D): Spatial and environmental features

### 5. Cross-Shot Validation

#### Validation Features
- Sequence consistency checking
- Per-shot validation reports
- Character-specific consistency tracking
- Detailed violation reporting with fix suggestions

#### Validation Metrics
- Overall consistency score (0-1)
- Per-rule compliance scores
- Violation severity ratings
- Confidence levels for each check

## Architecture

### Core Components

```
ConsistencyEngine
├── ReferenceLibrary
│   ├── CharacterReference
│   ├── StyleAnchor
│   └── WorldReference
├── StyleExtractor
│   └── Integration with SceneAnalyzer
├── CrossShotValidator
│   └── ContinuityRule implementations
└── ConsistencyIntegration
    └── Main orchestration layer
```

### Storage Structure

```
data/reference_library/
├── characters/
│   └── {character_id}.json
├── styles/
│   └── {style_id}.json
├── worlds/
│   └── {world_id}.json
└── frames/
    └── {frame_id}.pkl
```

## Usage

### Basic Setup

```python
from src.wedge_features.consistency_engine import (
    ConsistencyEngine,
    ReferenceLibrary
)

# Initialize
library = ReferenceLibrary(storage_path="data/reference_library")
engine = ConsistencyEngine(reference_library=library)
```

### Create Character Reference

```python
from src.wedge_features.consistency_integration import ConsistencyIntegration

integration = ConsistencyIntegration()

character = integration.create_character_reference(
    character_id="hero_01",
    name="Alex Thompson",
    description="Main protagonist",
    reference_image_paths=["ref1.jpg", "ref2.jpg"],
    appearance_attributes={
        'facial_features': {
            'eye_color': 'blue',
            'hair_color': 'brown'
        },
        'body_proportions': {
            'height': 1.8,
            'build': 'athletic'
        }
    }
)
```

### Create Style Anchor

```python
style = integration.create_style_anchor(
    anchor_id="noir_style",
    name="Film Noir",
    description="High contrast noir aesthetic",
    reference_image_paths=["noir1.jpg", "noir2.jpg"],
    style_attributes={
        'visual_attributes': {
            'contrast': 'high',
            'mood': 'dramatic'
        },
        'composition_rules': [
            "Use strong diagonal lines",
            "Emphasize shadows"
        ]
    }
)
```

### Process Frames

```python
# Process an image and create reference frame
frame = integration.process_image(
    image_path="shot_001_frame_001.jpg",
    shot_id="shot_001",
    timestamp=0.0,
    character_ids=["hero_01"],
    style_anchor_id="noir_style",
    world_id="city_01"
)
```

### Validate Consistency

```python
# Validate single shot
shot_report = integration.validate_shot(
    shot_id="shot_001",
    detailed=True
)

# Validate sequence of shots
sequence_report = integration.validate_sequence(
    shot_ids=["shot_001", "shot_002", "shot_003"],
    detailed=True
)

# Validate character consistency
character_report = integration.validate_character_consistency(
    character_id="hero_01",
    shot_ids=["shot_001", "shot_002"]
)
```

### Generate Reports

```python
# Generate comprehensive consistency report
report = engine.generate_consistency_report(frames)

# Export to file
integration.export_report("reports/consistency_report.json")
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
  }
}
```

## Integration with Scene Analyzer

The Consistency Engine integrates seamlessly with the existing `SceneAnalyzer`:

```python
from src.analyzers.scene_analyzer import SceneAnalyzer
from src.wedge_features.consistency_engine import StyleExtractor

# Initialize
scene_analyzer = SceneAnalyzer()
style_extractor = StyleExtractor(scene_analyzer)

# Analyze scene
scene_analysis = scene_analyzer.analyze_image("frame.jpg")

# Extract style features
style_features = style_extractor.extract_style_from_analysis(scene_analysis)

# Create style embedding
style_embedding = style_extractor.create_style_embedding(style_features)
```

## API Reference

### ConsistencyEngine

#### Methods

- `check_character_consistency(frame_a, frame_b, character_name)`: Check character consistency between frames
- `check_lighting_consistency(frame_a, frame_b)`: Validate lighting continuity
- `check_color_consistency(frame_a, frame_b)`: Validate color grading
- `check_spatial_consistency(frame_a, frame_b, object_id)`: Check spatial relationships
- `validate_shot_sequence(frames, check_types)`: Validate entire sequence
- `generate_consistency_report(frames)`: Generate detailed report

### ReferenceLibrary

#### Methods

- `add_character(character)`: Add character reference
- `add_style_anchor(style)`: Add style anchor
- `add_world(world)`: Add world reference
- `add_frame(frame)`: Add reference frame
- `get_character(character_id)`: Retrieve character
- `get_style(anchor_id)`: Retrieve style anchor
- `get_world(world_id)`: Retrieve world reference
- `find_similar_characters(embedding, top_k)`: Find similar characters
- `export_library(export_path)`: Export entire library

### CrossShotValidator

#### Methods

- `validate_shot_sequence(shots, context)`: Validate shot sequence
- `validate_character_consistency(character_id, shots)`: Validate character appearances

### StyleExtractor

#### Methods

- `extract_style_from_analysis(scene_analysis)`: Extract style features
- `create_style_embedding(style_features)`: Create numerical embedding

## Performance Metrics

Target performance benchmarks:

- **Cross-shot consistency**: >85% match
- **Character identity**: >95% F1 score
- **Lighting coherence**: <10% ΔRGB variance
- **Spatial accuracy**: <5% position deviation

## Best Practices

1. **Reference Quality**: Use high-quality reference images for best results
2. **Multiple References**: Provide multiple reference images per character/style
3. **Consistent Tagging**: Use consistent naming conventions for IDs
4. **Regular Validation**: Validate consistency after each shot completion
5. **Iterative Refinement**: Use violation reports to improve generation
6. **Backup Library**: Regularly export reference library backups

## Troubleshooting

### Common Issues

1. **Low Similarity Scores**: Increase reference image count
2. **False Violations**: Adjust thresholds in configuration
3. **Missing Embeddings**: Ensure images are processed correctly
4. **Performance Issues**: Enable caching and parallel validation

## Future Enhancements

- Integration with deep learning feature extractors (ResNet, CLIP)
- Temporal consistency for motion analysis
- Advanced color grading transfer
- Real-time consistency monitoring
- ML-based violation prediction

## License

Copyright (c) 2024 ANIMAtiZE Framework
