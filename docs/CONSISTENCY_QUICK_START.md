# Consistency Engine - Quick Start Guide

## Installation

No additional dependencies required beyond the existing project requirements:
- numpy
- opencv-python
- Pillow

## 5-Minute Setup

### 1. Initialize the System

```python
from src.wedge_features.consistency_integration import ConsistencyIntegration

# One-line initialization
integration = ConsistencyIntegration()
```

### 2. Create Your First Character Reference

```python
# Define a character from reference images
character = integration.create_character_reference(
    character_id="protagonist",
    name="Sarah Chen",
    description="Young detective, 30s, athletic",
    reference_image_paths=[
        "references/sarah_front.jpg",
        "references/sarah_side.jpg"
    ],
    appearance_attributes={
        'facial_features': {
            'eye_color': 'brown',
            'hair_color': 'black',
            'hair_style': 'ponytail'
        },
        'body_proportions': {
            'height': 1.7,
            'build': 'athletic'
        },
        'clothing': {
            'primary': 'leather jacket',
            'secondary': 'jeans'
        }
    }
)

print(f"✓ Character '{character.name}' created!")
```

### 3. Create a Style Anchor

```python
# Define your visual style
style = integration.create_style_anchor(
    anchor_id="detective_noir",
    name="Detective Noir",
    description="Dark, moody, high-contrast",
    reference_image_paths=[
        "references/noir_style1.jpg",
        "references/noir_style2.jpg"
    ],
    style_attributes={
        'visual_attributes': {
            'contrast': 'high',
            'saturation': 'low',
            'mood': 'dark'
        },
        'composition_rules': [
            "Use dramatic shadows",
            "High contrast lighting",
            "Moody color palette"
        ]
    }
)

print(f"✓ Style '{style.name}' created!")
```

### 4. Process Your Shots

```python
# Process each frame in your sequence
shot_frames = [
    "output/shot_001/frame_0001.jpg",
    "output/shot_001/frame_0002.jpg",
    "output/shot_001/frame_0003.jpg"
]

for i, frame_path in enumerate(shot_frames):
    frame = integration.process_image(
        image_path=frame_path,
        shot_id="shot_001",
        timestamp=i * 0.033,  # 30fps
        character_ids=["protagonist"],
        style_anchor_id="detective_noir"
    )
    print(f"✓ Processed frame {i+1}")
```

### 5. Validate Consistency

```python
# Check consistency for the shot
report = integration.validate_shot("shot_001", detailed=True)

print(f"\nConsistency Report:")
print(f"Score: {report['consistency_score']:.2%}")
print(f"Violations: {report['violations']}")
print(f"Status: {'✓ PASS' if report['passed'] else '✗ FAIL'}")

# Export detailed report
integration.export_report("reports/shot_001_consistency.json")
```

## Common Use Cases

### Use Case 1: Multi-Shot Character Consistency

```python
# Process multiple shots with same character
for shot_num in range(1, 6):
    shot_id = f"shot_{shot_num:03d}"
    
    for frame_num in range(24):  # 24 frames per shot
        frame_path = f"output/{shot_id}/frame_{frame_num:04d}.jpg"
        integration.process_image(
            image_path=frame_path,
            shot_id=shot_id,
            timestamp=frame_num * 0.033,
            character_ids=["protagonist"]
        )

# Validate character consistency across all shots
char_report = integration.validate_character_consistency(
    character_id="protagonist",
    shot_ids=[f"shot_{i:03d}" for i in range(1, 6)]
)

print(f"Character Consistency: {char_report['mean_similarity']:.2%}")
```

### Use Case 2: Scene-to-Scene Transition Validation

```python
# Validate smooth transitions between shots
sequence_report = integration.validate_sequence(
    shot_ids=["shot_001", "shot_002", "shot_003"],
    detailed=True
)

print(f"Sequence Consistency: {sequence_report['consistency_score']:.2%}")

# Check for transition issues
if sequence_report['violations'] > 0:
    print("\nTransition Issues:")
    for violation in sequence_report['violation_details']:
        print(f"  - {violation['type']}: {violation['description']}")
        print(f"    Fix: {violation['suggested_fix']}")
```

### Use Case 3: Style Enforcement

```python
# Ensure all shots match your style anchor
shots = ["shot_001", "shot_002", "shot_003"]

for shot_id in shots:
    # Process with style anchor
    frames = get_shot_frames(shot_id)  # Your function
    for i, frame_path in enumerate(frames):
        integration.process_image(
            image_path=frame_path,
            shot_id=shot_id,
            timestamp=i * 0.033,
            style_anchor_id="detective_noir"
        )
    
    # Validate style consistency
    report = integration.validate_shot(shot_id)
    if report['consistency_score'] < 0.85:
        print(f"⚠ {shot_id} needs style adjustment")
```

## Configuration

Edit `configs/consistency_engine.json` to adjust thresholds:

```json
{
  "thresholds": {
    "character_identity": 0.95,
    "lighting": 0.85,
    "color_grading": 0.90
  }
}
```

## Command-Line Usage

Create a simple CLI script:

```python
#!/usr/bin/env python3
"""consistency_check.py - Quick consistency checker"""

import sys
from src.wedge_features.consistency_integration import ConsistencyIntegration

def main():
    if len(sys.argv) < 2:
        print("Usage: python consistency_check.py <shot_id>")
        sys.exit(1)
    
    shot_id = sys.argv[1]
    
    integration = ConsistencyIntegration()
    report = integration.validate_shot(shot_id, detailed=True)
    
    print(f"\n{'='*60}")
    print(f"Consistency Report: {shot_id}")
    print(f"{'='*60}")
    print(f"Score: {report['consistency_score']:.2%}")
    print(f"Frames: {report['frame_count']}")
    print(f"Violations: {report['violations']}")
    print(f"Status: {'✓ PASS' if report['passed'] else '✗ FAIL'}")
    
    if report['violations'] > 0:
        print(f"\nIssues Found:")
        for v in report.get('violation_details', []):
            print(f"  • {v['description']}")

if __name__ == "__main__":
    main()
```

Run:
```bash
python consistency_check.py shot_001
```

## Troubleshooting

### Issue: Low Character Similarity

**Solution**: Add more reference images

```python
# Update existing character with more references
library = integration.reference_library
char = library.get_character("protagonist")
char.reference_images.extend([
    "references/sarah_3.jpg",
    "references/sarah_4.jpg"
])
library.add_character(char)  # Updates existing
```

### Issue: Too Many Color Violations

**Solution**: Adjust threshold

```python
# Edit config or override
integration.consistency_engine.thresholds['color_grading'] = 0.80
```

### Issue: False Spatial Violations

**Solution**: Increase spatial tolerance

```python
# Update rule threshold
for rule in integration.validator.rules:
    if rule.rule_id == 'spatial_coherence':
        rule.threshold = 0.3  # More tolerant
```

## Best Practices

### 1. Reference Quality
- Use high-resolution reference images (1920x1080+)
- Provide multiple angles and lighting conditions
- Include close-ups and full-body shots

### 2. Shot Organization
- Process shots in sequence order
- Use consistent naming conventions
- Maintain shot metadata

### 3. Validation Workflow
```
Create References → Process Shots → Validate → Fix Issues → Re-validate
```

### 4. Regular Backups
```python
# Backup your reference library
integration.reference_library.export_library(
    f"backups/library_{datetime.now().isoformat()}.tar.gz"
)
```

### 5. Iterative Refinement
```python
# Start with loose thresholds, tighten as needed
initial_thresholds = {
    'character_identity': 0.85,
    'lighting': 0.75,
    'color_grading': 0.80
}

# After tuning
production_thresholds = {
    'character_identity': 0.95,
    'lighting': 0.85,
    'color_grading': 0.90
}
```

## Performance Tips

### 1. Batch Processing
```python
# Process multiple frames in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for frame_path in frame_paths:
        future = executor.submit(
            integration.process_image,
            image_path=frame_path,
            shot_id=shot_id,
            # ... other params
        )
        futures.append(future)
    
    # Wait for completion
    results = [f.result() for f in futures]
```

### 2. Caching
```python
# Enable embedding caching (already enabled by default)
# Frames are cached in memory for fast access
```

### 3. Selective Validation
```python
# Only validate what you need
report = integration.validate_shot(
    shot_id="shot_001",
    detailed=False  # Faster, less detail
)
```

## Next Steps

1. **Read Full Documentation**: `docs/consistency_engine.md`
2. **Explore Examples**: `examples/consistency_engine_usage.py`
3. **Run Tests**: `pytest tests/test_consistency_engine.py`
4. **Customize Rules**: Create your own `ContinuityRule` subclasses
5. **Integrate with Pipeline**: Add to your video generation workflow

## Support

For issues or questions:
1. Check the full documentation
2. Review test examples
3. Examine the source code
4. Create an issue on the project repository

Happy consistency checking! 🎬
