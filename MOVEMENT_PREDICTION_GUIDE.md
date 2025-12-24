# ANiMAtiZE Movement Prediction System

## Overview

The Movement Prediction System transforms static images into cinematic movement prompts for AI video generation models (Flux, Imagen, OpenAI). This system analyzes static images and generates justified, physics-based movement descriptions that serve narrative purposes.

## Core Components

### 1. Movement Predictor (`movement_predictor.py`)

**Purpose**: Analyzes static images to generate comprehensive cinematic movement prompts.

**Key Features**:
- Character action prediction based on pose and body language
- Camera movement analysis using compositional principles
- Environmental animation based on physics and atmospheric conditions
- Movement justification validation system
- Export capabilities for AI model integration

**Usage**:
```python
from src.analyzers.movement_predictor import MovementPredictor

predictor = MovementPredictor()
analysis = predictor.analyze_image("path/to/image.jpg")
prompt = predictor.get_cinematic_movement_prompt("path/to/image.jpg")
```

### 2. Movement Rules (`movement_prediction_rules.json`)

**Purpose**: Comprehensive rule system for generating justified movement predictions.

**Must-Do Rules**:
- Every movement must serve the narrative
- Physics must be consistent and realistic
- Emotional beats must be maintained
- Composition must guide viewer attention
- Timing must feel natural and cinematic

**AI Model Requirements**:
- **Flux**: 24fps, cinematic motion blur, smooth keyframes, physics-based movement
- **Imagen**: Temporal coherence, narrative-serving motion, emotional continuity
- **OpenAI**: Cinematic directing language, explicit justification, technical specs

## Movement Categories

### Character Action Prediction
- **Pose-to-Action Continuation**: Natural next movement from current pose
- **Emotional Momentum Analysis**: Movement based on emotional trajectory
- **Interaction Anticipation**: Predicted interactions with environment

### Camera Movement Analysis
- **Composition-Guided Camera Flow**: Movement based on compositional elements
- **Depth Layer Parallax**: Realistic parallax from depth separation
- **Emotional Framing Progression**: Camera movement enhancing emotional narrative

### Environmental Animation
- **Physics-Based Environmental Motion**: Realistic physics application
- **Atmospheric Response System**: Environmental response to conditions

## Integration Workflow

### 1. Image Analysis
```bash
python src/analyzers/movement_predictor.py path/to/image.jpg
```

### 2. Generate Movement Prompt
The system outputs a comprehensive prompt including:
- Character movements with justification
- Camera movements with compositional reasoning
- Environmental animations with physics basis
- Technical specifications for AI models

### 3. AI Model Integration

**For Flux**:
```
Cinematic sequence: [character_action]; [camera_movement]; [environment_response] - all movements must be subtle, justified, and serve the narrative. Technical requirements: 24fps, cinematic motion blur, smooth keyframes, natural timing, physics-based movement, emotional coherence
```

**For Imagen**:
```
Unified movement where [character] [action] synchronized with [camera] [movement] while [environment] [response] enhances [mood]. Maintain temporal coherence and emotional progression.
```

**For OpenAI**:
```
Generate a cinematic sequence based on this static image: [detailed movement description with justification]. Include specific camera movements, character actions, and environmental animations that serve the narrative.
```

## Quality Assurance

### Validation Checks
- ✅ Physics consistency (gravity, momentum, friction)
- ✅ Narrative justification (every movement serves story)
- ✅ Visual coherence (lighting, shadows, continuity)
- ✅ Emotional progression (coherent emotional beats)

### Rejection Criteria
- ❌ Movement contradicts image evidence
- ❌ Physics violations detected
- ❌ Emotional progression makes no sense
- ❌ Visual inconsistencies present
- ❌ No clear justification provided

## Testing

Run the test suite:
```bash
python tests/test_movement_simple.py
```

## Example Output

**Input**: Static image of person standing
**Analysis**: 
- Character: Taking next step forward (upright stance indicates walking motion)
- Camera: Pan horizontal (horizontal lines suggest lateral movement)
- Environment: Shadows gradually shift (bright lighting creates defined shadows)

**Generated Prompt**:
"Cinematic sequence: Character taking next step forward - upright stance indicates walking motion; Camera pan horizontal - horizontal lines suggest lateral movement; Camera slow_push forward - gradual intimacy with subject - all movements must be subtle, justified, and serve the narrative. Technical requirements: 24fps, cinematic motion blur, smooth keyframes, natural timing, physics-based movement, emotional coherence"

## Technical Specifications

### Dependencies
- OpenCV (cv2) for image analysis
- NumPy for numerical operations
- JSON for rule storage
- Pathlib for file handling

### File Structure
```
configs/
├── movement_prediction_rules.json  # Comprehensive movement rules
├── rules/                         # Additional cinematic rules

src/analyzers/
├── movement_predictor.py         # Main prediction engine

tests/
├── test_movement_simple.py       # Basic functionality tests
├── test_movement_predictor.py    # Comprehensive test suite
```

## Future Enhancements

- Advanced pose estimation integration
- Machine learning-based movement prediction
- Multi-frame temporal analysis
- Real-time movement generation
- Cross-model prompt optimization

---

*This system enables the transformation of static images into dynamic, cinematic video prompts while maintaining narrative coherence and visual justification.*