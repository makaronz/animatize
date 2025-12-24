# Consistency Engine - Quick Start

## Installation

No additional dependencies required beyond project requirements.

## Quick Usage

### 1. Basic Setup

```python
from src.wedge_features.consistency_integration import ConsistencyOrchestrator

# Initialize orchestrator
orchestrator = ConsistencyOrchestrator(
    storage_path="data/reference_library",
    enable_scene_analyzer=True
)
```

### 2. Create References

```python
# Create style anchor
style = orchestrator.create_style_anchor_from_image(
    image_path="reference.jpg",
    anchor_id="fantasy_01",
    name="Fantasy Style",
    description="Epic fantasy aesthetic"
)

# Create character reference
character = orchestrator.create_character_reference(
    character_id="hero_001",
    name="Hero",
    description="Main protagonist",
    reference_image="hero_ref.jpg",
    facial_features={"eye_color": "blue", "hair": "brown"}
)

# Create world reference
world = orchestrator.create_world_reference(
    world_id="castle_01",
    name="Castle",
    description="Grand medieval castle",
    reference_image="castle_ref.jpg",
    time_of_day="midday",
    weather="clear"
)
```

### 3. Process Frames

```python
# Process a shot frame
frame = orchestrator.process_shot_image(
    image_path="shot_001_frame_000.jpg",
    shot_id="shot_001",
    timestamp=0.0
)
```

### 4. Validate Consistency

```python
# Validate single shot
validation = orchestrator.validate_shot_consistency("shot_001")

print(f"Overall score: {validation['scores']['overall']:.3f}")
print(f"Violations: {len(validation['violations'])}")

# Validate across shots
result = orchestrator.validate_sequence_consistency(
    shot_ids=["shot_001", "shot_002", "shot_003"]
)

print(f"Consistency: {result['report']['summary']['consistency_score']:.3f}")
```

### 5. Check Character Consistency

```python
# Validate specific character
char_result = orchestrator.validate_character_across_shots(
    character_id="hero_001",
    shot_ids=["shot_001", "shot_002"]
)

print(f"Mean similarity: {char_result['mean_similarity']:.3f}")
```

### 6. Style Consistency

```python
# Check style consistency
style_report = orchestrator.get_style_consistency_report(
    style_anchor_id="fantasy_01",
    shot_ids=["shot_001", "shot_002"]
)

print(f"Style match: {style_report['mean_similarity']:.3f}")
```

## Using Middleware

```python
from src.wedge_features.consistency_integration import ConsistencyMiddleware

# Setup middleware
middleware = ConsistencyMiddleware(orchestrator, auto_validate=True)

# Start shot
middleware.before_shot("shot_001")

# Process frames (auto-validates)
for frame_path in frames:
    result = middleware.after_frame_generated(frame_path, timestamp=i*0.5)
    
    if result and result.get('violations'):
        print(f"⚠️ {len(result['violations'])} violations detected")

# Complete shot
final = middleware.after_shot()
```

## Configuration

Edit `configs/consistency_engine.json`:

```json
{
  "thresholds": {
    "character_identity": 0.95,
    "lighting": 0.85,
    "color_grading": 0.90
  },
  "continuity_rules": {
    "color_consistency": {
      "enabled": true,
      "threshold": 0.1
    }
  }
}
```

## Key Classes

### ConsistencyOrchestrator
- Main interface for all operations
- Manages references and validation
- Integrates with scene analyzer

### ConsistencyMiddleware
- Pipeline integration
- Auto-validation support
- Shot lifecycle management

### ConsistencyEngine (Core)
- Reference frame creation
- Consistency checking
- Violation detection

### ReferenceLibrary
- Storage and retrieval
- Similarity search
- Export/import

## Common Patterns

### Pattern 1: Reference-Based Generation

```python
# Create references first
style = orchestrator.create_style_anchor_from_image(...)
character = orchestrator.create_character_reference(...)

# Then generate and validate
for shot in shots:
    frames = generate_frames(shot, style_anchor=style)
    validation = orchestrator.validate_shot_consistency(shot.id)
```

### Pattern 2: Continuous Validation

```python
middleware = ConsistencyMiddleware(orchestrator, auto_validate=True)

for shot in video.shots:
    middleware.before_shot(shot.id)
    
    for frame in shot.frames:
        # Generate frame
        image = generate_frame(frame.prompt)
        
        # Auto-validate
        middleware.after_frame_generated(image, frame.timestamp)
    
    middleware.after_shot()
```

### Pattern 3: Post-Production Analysis

```python
# Process all frames first
for shot in shots:
    for frame in shot.frames:
        orchestrator.process_shot_image(frame.path, shot.id, frame.time)

# Then analyze
report = orchestrator.validate_sequence_consistency(shot_ids)

# Review violations
for violation in report['report']['violations']:
    if violation['severity'] > 0.5:
        print(f"FIX REQUIRED: {violation['description']}")
        print(f"  Suggestion: {violation['suggested_fix']}")
```

## Troubleshooting

### Low Scores
- Verify reference image quality
- Check style anchor matches target
- Adjust thresholds in config

### High Violations
- Review prompts for consistency
- Use same style keywords
- Check lighting descriptions

### Missing Data
- Ensure frames are processed
- Verify reference library has data
- Check file paths

## Testing

Run examples:
```bash
python examples/consistency_engine_usage.py
```

Run tests:
```bash
python tests/test_consistency_engine.py
```

## Next Steps

1. Read full guide: `docs/consistency_engine_guide.md`
2. Review implementation: `docs/CONSISTENCY_ENGINE_IMPLEMENTATION.md`
3. Study examples: `examples/consistency_engine_usage.py`
4. Check configuration: `configs/consistency_engine.json`

## Support

- GitHub Issues: [project repository]
- Documentation: `docs/` directory
- Examples: `examples/` directory
