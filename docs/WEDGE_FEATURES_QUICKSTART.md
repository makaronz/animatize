# Wedge Features Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize data directories
mkdir -p data/{film_grammar_db,golden_dataset,reference_library,character_library,projects}
```

## 5-Minute Quick Start

### 1. Film Grammar Engine

```python
from wedge_features import FilmGrammarEngine, Genre

engine = FilmGrammarEngine()

# Get rules for your genre
rules = engine.get_applicable_rules(
    genre=Genre.NEO_NOIR,
    category="camera_movement"
)

# Validate your scene
scene = {
    'type': 'dialogue',
    'tags': ['scene_with_dialogue'],
    'elements': []
}
validation = engine.validate_grammar(scene, ['FG_001'])
print(f"Valid: {validation.is_valid}")
```

### 2. Shot List Compiler

```python
from wedge_features import ShotListCompiler

compiler = ShotListCompiler()

# Parse your script
script = """
INT. OFFICE - NIGHT
Detective sits at desk.
"""
scenes = compiler.parse_script(script)

# Generate coverage
shots = compiler.generate_coverage(scenes[0], 'dialogue')
print(f"Generated {len(shots)} shots")
```

### 3. Consistency Engine

```python
from wedge_features import ConsistencyEngine
import numpy as np

engine = ConsistencyEngine()

# Create reference frames (normally from actual video)
frames = [create_test_frame(i) for i in range(5)]

# Validate consistency
violations = engine.validate_shot_sequence(frames)
print(f"Found {len(violations)} violations")
```

### 4. Quality Assurance

```python
from wedge_features import QualityAssuranceSystem

qa = QualityAssuranceSystem()

video_data = {
    'width': 1920,
    'height': 1080,
    'fps': 24,
    'codec': 'h264',
    'bitrate': 8000
}

report = qa.assess_quality(video_data)
print(f"Quality Score: {report.overall_score:.2f}")
print(f"Status: {'PASSED' if report.passed else 'FAILED'}")
```

### 5. Character Identity

```python
from wedge_features import CharacterIdentityEngine

engine = CharacterIdentityEngine()

# Add character to library
engine.add_character(
    "hero_001",
    "Detective James",
    reference_images=["ref1.jpg", "ref2.jpg"]
)

# Use in prompt
prompt = engine.preserve_identity_in_generation(
    "hero_001",
    "Walking through rain"
)
```

## Run Complete Demo

```bash
python examples/wedge_features_demo.py
```

This demonstrates all 8 wedge features with integrated workflow.

## Run Tests

```bash
pytest tests/test_wedge_features.py -v
```

## Configuration

Edit configurations in `configs/wedge_features/`:

```json
// film_grammar.json
{
  "confidence_threshold": 0.85,
  "validation_settings": {
    "strict_mode": false
  }
}
```

## Next Steps

1. **Read Full Documentation**: `docs/WEDGE_FEATURES.md`
2. **Review Market Analysis**: `docs/market_gap_analysis.md`
3. **Explore Examples**: `examples/wedge_features_demo.py`
4. **Run Benchmarks**: Use Evaluation Harness for quality validation

## Support

- Issues: GitHub Issues
- Documentation: `docs/` directory
- Examples: `examples/` directory

## Key Takeaways

✅ **8 Strategic Features** that create defensible competitive moat  
✅ **Data Moats** through proprietary corpus and feedback loops  
✅ **Workflow Lock-in** by replacing 3-5 separate tools  
✅ **Industry Authority** through benchmark establishment  
✅ **18-24 months** estimated time to replicate

Start with Film Grammar Engine and Quality Assurance for immediate value!
