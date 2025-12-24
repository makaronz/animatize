# 🤝 Contributing to ANIMAtiZE Framework

Thank you for your interest in contributing to ANIMAtiZE! This document provides comprehensive guidelines for contributing to our cinematic AI framework.

## 🎯 Overview

ANIMAtiZE is a production-ready framework that transforms static images into cinematic masterpieces. We welcome contributions from developers, filmmakers, AI researchers, and creative professionals.

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Contribution Types](#-contribution-types)
- [Code Guidelines](#-code-guidelines)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Pull Request Process](#-pull-request-process)
- [Release Process](#-release-process)

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.8 or higher
- **Git**: Latest version
- **Virtual Environment**: venv or conda
- **API Keys**: OpenAI (for testing)

### Fork & Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/animatize-framework.git
cd animatize-framework

# Add upstream remote
git remote add upstream https://github.com/animatize/framework.git
```

## 🔧 Development Setup

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -r requirements-cv.txt
pip install -r requirements-test.txt

# Set up pre-commit hooks
pre-commit install

# Configure environment
cp configs/env/.env.example configs/env/.env.local
# Edit with your test API keys
```

### Development Tools

```bash
# Install additional development tools
pip install black isort flake8 mypy pytest-cov pre-commit

# Set up git hooks
pre-commit install --hook-type pre-push
```

## 🎯 Contribution Types

### 🐛 Bug Reports

Create issues for bugs with:
- **Clear description** of the problem
- **Minimal reproduction steps**
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Screenshots** if applicable

### ✨ Feature Requests

For new features:
- **Use feature request template**
- **Describe the use case**
- **Provide examples**
- **Consider backward compatibility**
- **Discuss implementation approach**

### 📚 Documentation

Improve documentation by:
- **Fixing typos and grammar**
- **Adding examples**
- **Improving clarity**
- **Adding missing documentation**
- **Translating to other languages**

### 🔧 Code Contributions

#### Core Features
- **New cinematic rules**
- **AI model integrations**
- **Performance optimizations**
- **New analysis algorithms**

#### Testing
- **Unit tests for new features**
- **Integration tests**
- **Performance benchmarks**
- **Edge case testing**

## 📝 Code Guidelines

### Python Style Guide

We follow PEP 8 with these additions:

```python
# Use type hints
def analyze_image(image_path: str) -> AnalysisResult:
    """Analyze image and return comprehensive results.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        AnalysisResult: Complete analysis results
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image format is not supported
    """
    pass

# Use descriptive variable names
character_bounding_box: Tuple[int, int, int, int]
is_portrait_orientation: bool

# Use constants for magic numbers
MAX_IMAGE_SIZE: int = 4096
DEFAULT_FPS: int = 24
CONFIDENCE_THRESHOLD: float = 0.8
```

### Code Structure

```
src/
├── analyzers/          # Image analysis modules
├── generators/         # AI model integrations
├── rules/             # Cinematic rules engine
├── core/              # Framework core
├── utils/             # Utility functions
└── web/               # Web interface
```

### Naming Conventions

- **Classes**: PascalCase (`MovementPredictor`)
- **Functions**: snake_case (`analyze_image`)
- **Variables**: snake_case (`camera_movement`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_IMAGE_SIZE`)
- **Modules**: snake_case (`movement_predictor`)

## 🧪 Testing Guidelines

### Test Structure

```python
# tests/test_movement_predictor.py
import pytest
from animatize.analyzers import MovementPredictor

class TestMovementPredictor:
    """Test suite for MovementPredictor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.predictor = MovementPredictor()
    
    def test_analyze_character_motion(self):
        """Test character motion analysis."""
        # Arrange
        image = load_test_image("portrait.jpg")
        
        # Act
        motion = self.predictor.predict_character_motion(image)
        
        # Assert
        assert motion.confidence > 0.8
        assert motion.type in ["walking", "standing", "sitting"]
    
    @pytest.mark.parametrize("image_path,expected_motion", [
        ("portrait.jpg", "subtle"),
        ("landscape.jpg", "panoramic"),
        ("action.jpg", "dynamic")
    ])
    def test_various_image_types(self, image_path, expected_motion):
        """Test different image types."""
        image = load_test_image(image_path)
        result = self.predictor.analyze(image)
        assert result.motion_type == expected_motion
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_movement_predictor.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run performance tests
pytest tests/performance/ -v --benchmark-only
```

## 📚 Documentation Standards

### Docstring Format

Use Google-style docstrings:

```python
def predict_camera_movement(
    image: np.ndarray,
    focal_length: float = 50.0,
    style: str = "cinematic"
) -> CameraMovement:
    """Predict optimal camera movement for given image.
    
    Args:
        image: Input image as numpy array (H, W, 3)
        focal_length: Camera focal length in mm (default: 50.0)
        style: Cinematic style ("cinematic", "documentary", "commercial")
    
    Returns:
        CameraMovement: Predicted camera movement with confidence score
    
    Raises:
        ValueError: If image format is invalid
        ValueError: If style parameter is not recognized
    
    Examples:
        >>> image = load_image("portrait.jpg")
        >>> movement = predict_camera_movement(image, style="cinematic")
        >>> print(f"Movement: {movement.type}, Confidence: {movement.confidence}")
    """
```

### README Updates

When adding new features:
- Update README.md examples
- Add to feature list
- Update performance benchmarks
- Add usage examples

## 🔄 Pull Request Process

### 1. Branch Creation

```bash
# Create feature branch
git checkout -b feature/add-new-cinematic-rule

# Or bug fix branch
git checkout -b fix/movement-prediction-accuracy
```

### 2. Development Workflow

```bash
# Make your changes
git add .
git commit -m "feat: add new cinematic rule for portrait lighting

- Add golden hour lighting movement
- Implement soft focus transitions
- Add comprehensive tests
- Update documentation"

# Push to your fork
git push origin feature/add-new-cinematic-rule
```

### 3. Commit Message Format

Use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 4. Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🚀 Release Process

### Version Numbering

We use semantic versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] GitHub release created
- [ ] PyPI package published

## 🎨 Cinematic Rules Development

### Adding New Rules

1. **Research**: Study professional film techniques
2. **Define**: Create rule definition in JSON
3. **Implement**: Add rule logic in Python
4. **Test**: Comprehensive testing
5. **Document**: Add examples and usage

### Rule Structure

```json
{
  "rule_id": "golden_hour_portrait",
  "name": "Golden Hour Portrait Lighting",
  "description": "Soft, warm lighting movement for portrait photography",
  "conditions": [
    "portrait_orientation",
    "golden_hour_lighting",
    "warm_color_temperature"
  ],
  "actions": [
    "gentle_lighting_sweep",
    "soft_focus_transition",
    "warm_tone_enhancement"
  ],
  "intensity": 0.7,
  "duration": 5.0
}
```

## 🔍 Code Review Guidelines

### Review Checklist

- [ ] **Functionality**: Does it work as intended?
- [ ] **Code Quality**: Clean, readable, maintainable?
- [ ] **Performance**: Efficient algorithms?
- [ ] **Testing**: Adequate test coverage?
- [ ] **Documentation**: Clear and complete?
- [ ] **Security**: No vulnerabilities?

### Review Process

1. **Automated Checks**: CI/CD pipeline
2. **Code Review**: Peer review required
3. **Testing**: Manual testing for complex features
4. **Documentation**: Verify documentation updates
5. **Approval**: At least 2 approvals required

## 🐛 Debugging

### Common Issues

```bash
# Import errors
export PYTHONPATH=src:$PYTHONPATH

# API key issues
echo $OPENAI_API_KEY  # Check if set

# Performance issues
python scripts/profile.py --image test.jpg

# Memory issues
python -m memory_profiler src/main.py
```

### Debug Tools

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Performance profiling
import cProfile
cProfile.run('framework.analyze_image("test.jpg")')
```

## 🌟 Recognition

Contributors are recognized in:
- **README.md**: Special thanks section
- **CHANGELOG.md**: Contributor mentions
- **GitHub**: Contributors page
- **Website**: Hall of fame

## 📞 Contact

- **Discord**: [Join our community](https://discord.gg/animatize)
- **Email**: dev@animatize.dev
- **GitHub**: [Create an issue](https://github.com/animatize/framework/issues)

---

Thank you for contributing to ANIMAtiZE! Together, we're revolutionizing cinematic AI.