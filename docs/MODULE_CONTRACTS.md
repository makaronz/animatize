# ANIMAtiZE Module Contracts Specification

**Version**: 1.0.0  
**Date**: 2025-01-28  
**Purpose**: Formal interface contracts for all core modules

---

## 📋 Contract Overview

This document specifies the formal contracts (interfaces, inputs, outputs, side effects, error handling) for all core modules in the ANIMAtiZE framework.

---

## 1. SceneAnalyzer Module

### Module Information
- **File**: `src/analyzers/scene_analyzer.py`
- **Lines**: 435 total
- **Dependencies**: OpenCV, PIL, NumPy
- **State**: Stateful (has cache)

### Class: `SceneAnalyzer`

#### Constructor Contract

```python
def __init__(self, config_path: Optional[str] = None) -> None:
    """
    Initialize the scene analyzer with optional configuration.
    
    Args:
        config_path: Path to JSON config file (optional)
                    If None, uses default config
                    If provided but not found, logs warning and uses defaults
    
    Side Effects:
        - Creates self.analysis_cache = {} (in-memory dict)
        - Loads configuration from file or uses defaults
        - Initializes logger
    
    Raises:
        None (no exceptions, uses defaults on failure)
    """
```

**Default Configuration**:
```json
{
  "confidence_threshold": 0.5,
  "max_objects": 20,
  "composition_weights": {
    "rule_of_thirds": 0.3,
    "symmetry": 0.3,
    "depth": 0.4
  },
  "scene_thresholds": {
    "sky_ratio": 0.3,
    "green_ratio": 0.2,
    "building_ratio": 0.3,
    "water_ratio": 0.1
  }
}
```

#### Main Analysis Method

```python
def analyze_image(self, image_path: str) -> Dict[str, Any]:
    """
    Perform comprehensive image analysis using computer vision.
    
    Args:
        image_path: Absolute or relative path to image file
                   Supported formats: JPEG, PNG, BMP, TIFF, WEBP
    
    Returns:
        On success:
        {
            "timestamp": "ISO-8601 datetime string",
            "image_path": "str - input path",
            "image_info": {
                "width": int,
                "height": int,
                "mode": str (e.g., "RGB"),
                "format": str (e.g., "JPEG"),
                "aspect_ratio": float (3 decimals),
                "mean_brightness": float,
                "std_dev": float
            },
            "objects": [
                {
                    "class": str (e.g., "sky", "vegetation", "building"),
                    "confidence": float [0.0-1.0] (2 decimals),
                    "bbox": [x: int, y: int, w: int, h: int],
                    "center": [cx: int, cy: int],
                    "area": int (pixels)
                },
                ... (up to max_objects from config)
            ],
            "depth": {
                "method": "gradient_depth",
                "min_depth": float,
                "max_depth": float,
                "mean_depth": float,
                "depth_variance": float,
                "depth_complexity": float
            },
            "composition": {
                "rule_of_thirds": {
                    "grid": [[x1, x2, x3], [y1, y2, y3]],
                    "key_points": [[x1, y1], [x2, y1], [x1, y2], [x2, y2]]
                },
                "symmetry": {
                    "horizontal_symmetry": float [0.0-1.0] (3 decimals),
                    "vertical_symmetry": float [0.0-1.0] (3 decimals)
                },
                "complexity": {
                    "edge_density": float [0.0-1.0] (3 decimals),
                    "texture_complexity": float (3 decimals)
                }
            },
            "scene_type": {
                "type": str (e.g., "landscape", "urban", "nature"),
                "confidence": float [0.0-1.0] (2 decimals),
                "color_ratios": {
                    "sky": float (3 decimals),
                    "vegetation": float (3 decimals),
                    "building": float (3 decimals),
                    "water": float (3 decimals)
                }
            },
            "aesthetics": {
                "overall_score": float [0.0-1.0] (3 decimals),
                "composition_score": float [0.0-1.0] (3 decimals),
                "depth_score": float [0.0-1.0] (3 decimals),
                "color_score": float [0.0-1.0] (3 decimals),
                "breakdown": {
                    "symmetry": float (3 decimals),
                    "depth_variance": float (3 decimals),
                    "edge_density": float (3 decimals)
                }
            }
        }
        
        On error:
        {
            "error": True,
            "error_message": str,
            "timestamp": "ISO-8601 datetime string"
        }
    
    Side Effects:
        - Reads image file from disk
        - Stores result in self.analysis_cache[image_path]
        - Logs errors to logger
    
    Performance:
        - Latency: 50-200ms for 1080p images
        - Memory: ~30MB peak (for 1080p)
        - Deterministic: Yes (same image → same result)
    
    Caching:
        - Cache key: image_path (string)
        - Cache location: self.analysis_cache (in-memory dict)
        - Cache eviction: None (unbounded growth ⚠️)
        - Cache invalidation: None (stale until restart ⚠️)
    
    Error Handling:
        - FileNotFoundError → ValueError → error dict
        - cv2.imread() returns None → ValueError → error dict
        - Any exception → logged + error dict returned
    
    Thread Safety:
        - ❌ NOT thread-safe (shared cache without locks)
    """
```

#### Helper Methods (Internal)

```python
def _get_image_info(self, image: Image.Image) -> Dict[str, Any]:
    """Extract basic image metadata using PIL."""

def _detect_objects_fallback(self, image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Detect objects using color segmentation.
    
    Algorithm:
        1. Convert BGR → HSV
        2. Apply predefined color thresholds
        3. Find contours in each color mask
        4. Filter by area (> 1% of image)
        5. Sort by confidence, limit to max_objects
    
    Limitations:
        - No ML model (heuristic-based)
        - Fixed color ranges (not adaptive)
        - Limited to 5 object classes
    """

def _estimate_depth_fallback(self, image: np.ndarray) -> Dict[str, Any]:
    """
    Estimate depth using gradient magnitude.
    
    Algorithm:
        1. Convert to grayscale
        2. Calculate Sobel gradients (x and y)
        3. Compute gradient magnitude
        4. Normalize to [0, 1]
        5. Invert (high gradient = near)
    
    Limitations:
        - Not true depth (heuristic proxy)
        - No multi-scale analysis
        - No occlusion handling
    """

def _analyze_composition(self, image: np.ndarray) -> Dict[str, Any]:
    """
    Analyze compositional elements.
    
    Includes:
        - Rule of thirds grid calculation
        - Horizontal/vertical symmetry analysis
        - Edge density (complexity metric)
        - Texture complexity (local std dev)
    """

def _classify_scene(self, image: np.ndarray) -> Dict[str, Any]:
    """
    Classify scene type based on color ratios.
    
    Scene Types:
        - "landscape": sky + vegetation
        - "urban": building ratio high
        - "water_scene": water ratio high
        - "nature": vegetation high
        - "sky": sky dominant
        - "mixed": default fallback
    """

def _calculate_aesthetics_score(self, analysis: Dict) -> Dict[str, Any]:
    """
    Calculate overall aesthetics score.
    
    Formula:
        overall = (composition_score + depth_score + color_score) / 3
        
    Weights (from config):
        - rule_of_thirds: 0.3
        - symmetry: 0.3
        - depth: 0.4
    """
```

#### Batch Processing

```python
def batch_analyze(self, image_dir: str, output_dir: str) -> Dict[str, Any]:
    """
    Analyze all images in a directory.
    
    Args:
        image_dir: Path to input directory
        output_dir: Path to output directory (created if not exists)
    
    Returns:
        {
            "total_images": int,
            "successful_analyses": int,
            "failed_analyses": int,
            "analyses": {
                "path/to/image1.jpg": {...analysis...},
                "path/to/image2.jpg": {...analysis...}
            }
        }
    
    Side Effects:
        - Creates output_dir if not exists
        - Writes {filename}_analysis.json for each image
        - Processes images sequentially (no parallelization ⚠️)
    """
```

#### I/O Methods

```python
def save_analysis(self, analysis: Dict, output_path: str) -> None:
    """
    Save analysis results to JSON file.
    
    Args:
        analysis: Analysis dict from analyze_image()
        output_path: Path to output JSON file
    
    Side Effects:
        - Writes JSON file to disk
        - Logs success/failure
    
    Error Handling:
        - Catches all exceptions, logs errors
    """
```

---

## 2. MovementPredictor Module

### Module Information
- **File**: `src/analyzers/movement_predictor.py`
- **Lines**: 339 total
- **Dependencies**: OpenCV, NumPy, PIL
- **State**: Stateless (loads rules from config)

### Class: `MovementPredictor`

#### Constructor Contract

```python
def __init__(self, config_path: str = None) -> None:
    """
    Initialize movement predictor with cinematic rules.
    
    Args:
        config_path: Path to movement rules JSON
                    Default: "configs/movement_prediction_rules.json"
    
    Side Effects:
        - Loads rules from JSON file
        - Initializes logger
        - Stores rules in self.rules (dict)
    
    Raises:
        - Logs error if file not found (does not raise)
        - Sets self.rules = {} on failure
    """
```

**Rules Configuration Structure**:
```json
{
  "version": "1.0.0",
  "must_do_rules": {...},
  "movement_categories": {
    "character_action": {
      "priority": 1.0,
      "must_analyze": ["body_language", "facial_expression", ...]
    },
    "camera_movement": {...},
    "environment_animation": {...}
  },
  "movement_prediction_rules": [
    {
      "id": "movement_001",
      "category": "character_action",
      "rule_name": "Pose-to-Action Continuation",
      "priority": 1.0,
      "must_do": true,
      "description": "...",
      "analysis_points": [...],
      "prompt_template": "...",
      "examples": [...]
    },
    ... (47 total rules)
  ]
}
```

#### Main Analysis Method

```python
def analyze_image(self, image_path: str) -> Dict[str, Any]:
    """
    Analyze static image and generate justified movement predictions.
    
    Args:
        image_path: Path to image file
    
    Returns:
        On success:
        {
            "image_path": str,
            "image_size": (width: int, height: int),
            "movement_predictions": {
                "character_actions": [
                    {
                        "pose_type": str,
                        "predicted_action": str,
                        "justification": str,
                        "confidence": float [0.0-1.0],
                        "movement_category": "character_action"
                    },
                    ...
                ],
                "camera_movements": [
                    {
                        "type": str (e.g., "tracking_shot", "pan", "slow_push"),
                        "direction": str (e.g., "horizontal", "forward", "diagonal"),
                        "justification": str,
                        "confidence": float [0.0-1.0]
                    },
                    ...
                ],
                "environment_animations": [
                    {
                        "element": str (e.g., "shadows", "vegetation", "fabric"),
                        "motion": str,
                        "justification": str,
                        "confidence": float [0.0-1.0]
                    },
                    ...
                ]
            },
            "justifications": Dict (currently empty),
            "generated_prompts": [
                str (combined prompt),
                str (character prompt),
                str (camera prompt),
                str (environment prompt),
                ...
            ]
        }
        
        On error:
        {
            "error": str
        }
    
    Algorithm:
        1. Load image with PIL and OpenCV
        2. Analyze character movement (contour-based)
        3. Analyze camera movement (Hough lines)
        4. Analyze environmental motion (HSV color)
        5. Generate movement prompts
    
    Performance:
        - Latency: 100-300ms for 1080p
        - Memory: ~15MB peak
        - Deterministic: Yes
    
    Limitations:
        - Heuristic-based (no ML)
        - Fixed confidence scores
        - Single-frame analysis (no temporal context)
    """
```

#### Internal Analysis Methods

```python
def _analyze_character_movement(self, image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Analyze character pose using contour analysis.
    
    Algorithm:
        1. Convert to grayscale
        2. Canny edge detection
        3. Find contours
        4. Get largest contour (assumed to be person)
        5. Calculate bounding box aspect ratio
        6. Classify pose based on aspect ratio:
           - > 1.5: standing/walking
           - < 0.7: sitting/crouching
           - else: standing neutral
    
    Returns:
        List of character movement predictions
    
    Limitations:
        - No actual pose estimation
        - Only analyzes largest contour
        - Simple aspect ratio heuristic
    """

def _analyze_camera_movement(self, image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Determine camera movements from composition.
    
    Algorithm:
        1. Detect leading lines (Hough transform)
        2. Classify lines as horizontal/vertical/diagonal
        3. Suggest camera movements based on lines
        4. Add default movements (slow push, subtle tilt)
    
    Returns:
        List of camera movement predictions (4-6 items)
    
    Note:
        Always returns some movements (has defaults)
    """

def _analyze_environmental_motion(self, image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Predict environmental element animations.
    
    Algorithm:
        1. Analyze brightness → shadow predictions
        2. Detect green pixels → vegetation motion
        3. Calculate texture variance → fabric motion
    
    Returns:
        List of environmental predictions (0-3 items)
    """

def _generate_movement_prompts(self, analysis: Dict) -> List[str]:
    """
    Generate text prompts from analysis.
    
    Format:
        - [0]: Combined cinematic prompt (all movements)
        - [1+]: Individual prompts for each movement
    
    Returns:
        List of prompt strings
    """
```

#### Validation Method

```python
def validate_movement_justification(
    self, 
    movement: Dict[str, Any], 
    image_context: Dict[str, Any]
) -> bool:
    """
    Validate that a movement has proper justification.
    
    Args:
        movement: Movement prediction dict
        image_context: Context from image analysis
    
    Returns:
        True if justified, False otherwise
    
    Validation Rules:
        - Must have 'justification' field
        - Must contain keywords: gravity, natural, composition
    
    Limitations:
        - Simple keyword matching (not semantic)
        - Does not check image_context (unused parameter)
    """
```

#### Output Methods

```python
def get_cinematic_movement_prompt(self, image_path: str) -> str:
    """
    Generate complete cinematic prompt for video generation.
    
    Args:
        image_path: Path to static image
    
    Returns:
        Combined prompt with technical specs:
        "{primary_prompt}. Technical requirements: 24fps, cinematic motion blur, ..."
    
    Error Handling:
        Returns error string on failure
    """

def save_analysis(self, analysis: Dict, output_path: str) -> bool:
    """
    Save analysis to JSON file.
    
    Args:
        analysis: Analysis dict from analyze_image()
        output_path: Output file path
    
    Returns:
        True on success, False on failure
    
    Side Effects:
        - Creates parent directories if needed
        - Writes JSON with ensure_ascii=False (Unicode support)
    """
```

---

## 3. PromptExpander Module

### Module Information
- **File**: `src/core/prompt_expander.py`
- **Lines**: 293 total
- **Dependencies**: OpenAI SDK, functools (lru_cache)
- **State**: Stateful (has cache, API client)

### Data Classes

```python
@dataclass
class ExpansionRequest:
    """
    Request structure for prompt expansion.
    
    Fields:
        base_prompt: str - Original prompt to expand
        rules: List[Dict[str, Any]] - Cinematic rules to apply
        context: Optional[Dict[str, Any]] - Additional context
        max_tokens: int = 500 - Max tokens in response
        temperature: float = 0.7 - GPT temperature (0.0-2.0)
    
    Constraints:
        - base_prompt: non-empty string
        - rules: non-empty list
        - max_tokens: 1-4096
        - temperature: 0.0-2.0
    """

@dataclass
class ExpansionResult:
    """
    Result structure from prompt expansion.
    
    Fields:
        expanded_prompt: str - Expanded cinematic prompt
        used_rules: List[str] - IDs of applied rules
        confidence: float - Quality score [0.0-1.0]
        processing_time: float - Seconds
        metadata: Dict[str, Any] - Additional info
            - "model": str (e.g., "gpt-4-turbo-preview")
            - "tokens_used": int
            - "cached": bool
    """
```

### Class: `PromptExpander`

#### Constructor Contract

```python
def __init__(
    self, 
    api_key: Optional[str] = None, 
    model: str = "gpt-4-turbo-preview"
) -> None:
    """
    Initialize prompt expander with OpenAI API.
    
    Args:
        api_key: OpenAI API key (default: from OPENAI_API_KEY env var)
        model: OpenAI model name (default: gpt-4-turbo-preview)
    
    Raises:
        ValueError: If api_key not provided and not in environment
    
    Side Effects:
        - Creates OpenAI client
        - Loads templates from configs/templates/
        - Initializes cache (dict)
        - Sets cache_ttl = 3600 (1 hour)
    
    Supported Models:
        - gpt-4-turbo-preview (default)
        - gpt-4
        - gpt-3.5-turbo
    """
```

#### Main Expansion Method

```python
def expand_prompt(self, request: ExpansionRequest) -> ExpansionResult:
    """
    Expand prompt using cinematic rules and GPT.
    
    Args:
        request: ExpansionRequest with prompt and rules
    
    Returns:
        ExpansionResult with expanded prompt and metadata
    
    Process:
        1. Generate cache key (MD5 of request)
        2. Check cache (LRU + TTL)
        3. If cache miss:
           a. Build system prompt (from templates)
           b. Build user prompt (prompt + rules + context)
           c. Call OpenAI API (with retry logic)
           d. Calculate confidence (keyword matching)
           e. Cache result
        4. Return result
    
    Performance:
        - Cache hit: ~0ms (memory lookup)
        - Cache miss: 500-3000ms (OpenAI API)
    
    Caching:
        - Key: MD5(base_prompt + rules + context)
        - Eviction: LRU (128 items) + TTL (1 hour)
        - Thread-safe: No ⚠️
    
    Error Handling:
        - openai.RateLimitError: Retry 3x with exponential backoff
        - openai.APIError: Retry 1x
        - Other exceptions: Logged and raised
    
    Determinism:
        - ❌ Non-deterministic (temperature=0.7)
        - Cache provides pseudo-determinism
        - No seed control
    
    Cost:
        - GPT-4-turbo: ~$0.01-0.03 per call
        - GPT-3.5-turbo: ~$0.001-0.002 per call
    """
```

#### Internal Methods

```python
@lru_cache(maxsize=128)
def _get_cache_key(self, request: ExpansionRequest) -> str:
    """
    Generate cache key from request.
    
    Algorithm:
        1. Serialize prompt + rules + context to JSON
        2. Sort keys for consistency
        3. Return JSON string (used as dict key)
    
    Note:
        @lru_cache decorator provides additional caching layer
    """

def _is_cached(self, cache_key: str) -> bool:
    """Check if result is in cache and not expired."""

def _get_cached_result(self, cache_key: str) -> Optional[ExpansionResult]:
    """Retrieve cached result if available and not expired."""

def _cache_result(self, cache_key: str, result: ExpansionResult) -> None:
    """Store result in cache with timestamp."""

def _build_system_prompt(self, request: ExpansionRequest) -> str:
    """
    Build system prompt for GPT.
    
    Sources:
        - Template file: configs/templates/base_expansion.txt
        - Fallback: Hardcoded prompt (lines 157-167)
    
    Returns:
        System prompt instructing GPT to act as cinematographer
    """

def _build_user_prompt(self, request: ExpansionRequest) -> str:
    """
    Build user prompt with rules and context.
    
    Format:
        Base prompt: {request.base_prompt}
        
        Apply these cinematic rules:
        - {rule1.name}: {rule1.snippet} (priority: {rule1.priority})
        - {rule2.name}: ...
        
        Context: {json.dumps(request.context)}
        
        Expand this into a detailed, cinematic prompt...
    """

def _call_openai_with_retry(
    self,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    max_retries: int = 3
) -> Any:
    """
    Call OpenAI API with exponential backoff retry.
    
    Retry Logic:
        - RateLimitError: Wait 2^attempt seconds, retry
        - APIError: Wait 1 second, retry
        - Max retries: 3
    
    Timeout: 30 seconds per request
    
    Returns:
        OpenAI completion response object
    
    Raises:
        openai.RateLimitError: If all retries fail
        openai.APIError: If all retries fail
    """

def _calculate_confidence(
    self, 
    expanded_prompt: str, 
    rules: List[Dict[str, Any]]
) -> float:
    """
    Calculate confidence score for expanded prompt.
    
    Algorithm:
        base = 0.5
        + 0.05 per cinematic keyword (max +0.30)
        + 0.02 per rule applied (max +0.20)
        + 0.03 per descriptive word (max +0.15)
        = max 1.0
    
    Cinematic Keywords:
        camera, shot, angle, lighting, composition, depth, focus,
        movement, tracking, zoom, pan, tilt, dolly, crane
    
    Descriptive Indicators:
        beautiful, dramatic, elegant, smooth, dynamic, cinematic
    
    Limitations:
        - Heuristic-based (not ML)
        - Simple keyword matching
        - No semantic analysis
    """
```

#### Cache Management

```python
def clear_cache(self) -> None:
    """
    Clear the expansion cache.
    
    Side Effects:
        - Clears self.cache dict
        - Logs info message
    
    Use Cases:
        - Memory management
        - Force fresh expansions
        - Testing
    """

def get_cache_stats(self) -> Dict[str, int]:
    """
    Get cache statistics.
    
    Returns:
        {
            "cached_items": int,
            "max_cache_size": 128,
            "cache_ttl": 3600
        }
    """
```

---

## 4. ImageGenerator Module

### Module Information
- **File**: `src/core/image_generator.py`
- **Lines**: 408 total
- **Dependencies**: aiohttp, PIL, asyncio
- **State**: Stateful (API keys, cache directory)

### Enums and Data Classes

```python
class ImageAPI(Enum):
    """Supported image generation APIs."""
    FLUX = "flux"
    IMAGEN = "imagen"
    DALLE = "dalle"

@dataclass
class GenerationRequest:
    """
    Request for image generation.
    
    Fields:
        prompt: str - Text prompt for generation
        api: ImageAPI - Which API to use
        width: int = 1024 - Image width (pixels)
        height: int = 1024 - Image height (pixels)
        quality: str = "high" - Quality setting
        style: str = "cinematic" - Style preset
        negative_prompt: Optional[str] = None - Things to avoid
        seed: Optional[int] = None - Random seed (for reproducibility)
        guidance_scale: float = 7.5 - How closely to follow prompt
        num_inference_steps: int = 50 - Generation steps
    
    Constraints:
        - width, height: 512-2048 (API-dependent)
        - quality: "low", "medium", "high", "ultra"
        - style: API-dependent
        - guidance_scale: 0.0-20.0
        - num_inference_steps: 1-150
    """

@dataclass
class GenerationResult:
    """
    Result from image generation.
    
    Fields:
        image_data: bytes - PNG image data
        api_used: ImageAPI - Which API generated it
        generation_time: float - Seconds
        metadata: Dict[str, Any] - API-specific metadata
        quality_score: float - Assessed quality [0.0-1.0]
        prompt_used: str - Actual prompt sent to API
    """
```

### Class: `ImageGenerator`

#### Constructor Contract

```python
def __init__(self) -> None:
    """
    Initialize multi-API image generator.
    
    Side Effects:
        - Loads API keys from environment variables:
          * FLUX_API_KEY
          * IMAGEN_API_KEY
          * OPENAI_API_KEY
        - Creates cache directory: data/cache/images/
        - Initializes logger
    
    API Endpoints:
        - Flux: https://api.flux.ai/v1/generate
        - Imagen: https://imagen.googleapis.com/v1/images:generate
        - DALL-E: https://api.openai.com/v1/images/generations
    
    Quality Thresholds:
        - low: 0.6
        - medium: 0.75
        - high: 0.85
        - ultra: 0.95
    """
```

#### Main Generation Method

```python
async def generate_image(self, request: GenerationRequest) -> GenerationResult:
    """
    Generate image using specified API.
    
    Args:
        request: GenerationRequest with prompt and parameters
    
    Returns:
        GenerationResult with image data and metadata
    
    Process:
        1. Validate API key availability
        2. Check filesystem cache (MD5-based)
        3. If cache miss:
           a. Call API-specific generation method
           b. Assess image quality
           c. Cache result to file
        4. Return result
    
    Performance:
        - Cache hit: 50-100ms (file I/O)
        - Cache miss:
          * DALL-E: 5-30 seconds
          * Flux: 3-20 seconds
          * Imagen: 4-40 seconds
    
    Caching:
        - Key: MD5(prompt + api + dimensions + quality + seed + guidance)
        - Storage: data/cache/images/{key}.png
        - Eviction: None (manual cleanup needed ⚠️)
        - Persistence: Yes (survives restarts)
    
    Error Handling:
        - ValueError: If API key not found
        - HTTP errors: Raised as exceptions (no retry ⚠️)
    
    Cost (per image):
        - DALL-E 3: $0.04-0.08
        - Flux Pro: $0.05-0.10
        - Imagen 3: $0.02-0.04
    """
```

#### API-Specific Methods

```python
async def _generate_flux(self, request: GenerationRequest) -> GenerationResult:
    """
    Generate image using Flux API.
    
    API Details:
        - Model: flux-pro-1.1
        - Endpoint: POST https://api.flux.ai/v1/generate
        - Auth: Bearer token
    
    Payload:
        {
            "prompt": str,
            "width": int,
            "height": int,
            "num_inference_steps": int,
            "guidance_scale": float,
            "seed": Optional[int],
            "negative_prompt": Optional[str]
        }
    
    Response:
        {
            "images": [base64_string],
            "seed": int
        }
    """

async def _generate_imagen(self, request: GenerationRequest) -> GenerationResult:
    """
    Generate image using Google Imagen API.
    
    API Details:
        - Model: imagen-3.0-generate-001
        - Endpoint: POST https://imagen.googleapis.com/v1/images:generate
        - Auth: Bearer token (Google Cloud)
    
    Payload:
        {
            "instances": [{
                "prompt": str,
                "parameters": {
                    "sampleCount": 1,
                    "sampleImageSize": "1024x1024",
                    "aspectRatio": "1:1",
                    "guidanceScale": float,
                    "seed": Optional[int]
                }
            }]
        }
    """

async def _generate_dalle(self, request: GenerationRequest) -> GenerationResult:
    """
    Generate image using OpenAI DALL-E API.
    
    API Details:
        - Model: dall-e-3
        - Endpoint: POST https://api.openai.com/v1/images/generations
        - Auth: Bearer token
    
    Payload:
        {
            "model": "dall-e-3",
            "prompt": str,
            "n": 1,
            "size": "1024x1024",
            "quality": str,
            "style": str,
            "response_format": "b64_json"
        }
    
    Response:
        {
            "data": [{
                "b64_json": str,
                "revised_prompt": str
            }]
        }
    
    Note:
        DALL-E may revise the prompt for safety/quality.
        The revised prompt is returned in metadata.
    """
```

#### Batch Processing

```python
async def generate_batch(
    self,
    requests: List[GenerationRequest],
    max_concurrent: int = 3
) -> List[GenerationResult]:
    """
    Generate multiple images concurrently.
    
    Args:
        requests: List of generation requests
        max_concurrent: Maximum concurrent API calls
    
    Returns:
        List of generation results (same order as requests)
    
    Concurrency:
        - Uses asyncio.Semaphore(max_concurrent)
        - Limits parallel API calls to prevent rate limiting
        - Uses asyncio.gather() for execution
    
    Performance:
        For N images with max_concurrent=3:
        - Sequential: N × 10s = 10N seconds
        - Batch: ceil(N/3) × 10s = 3.33N seconds
        - Speedup: 3x
    
    Error Handling:
        - Failures are raised (no partial results)
        - Consider using return_exceptions=True in gather()
    """
```

#### Cache Methods

```python
async def _check_cache(self, request: GenerationRequest) -> Optional[GenerationResult]:
    """
    Check filesystem cache for existing image.
    
    Returns:
        GenerationResult if cached, None otherwise
    
    Cache Format:
        - Filename: {cache_key}.png
        - Metadata: Lost (only image data retrieved)
    """

async def _cache_result(
    self, 
    request: GenerationRequest, 
    result: GenerationResult
) -> None:
    """
    Save generated image to cache.
    
    Side Effects:
        - Writes PNG file to data/cache/images/
        - Logs warnings on failure (does not raise)
    """

def _generate_cache_key(self, request: GenerationRequest) -> str:
    """
    Generate MD5 cache key from request.
    
    Includes:
        - prompt
        - api
        - width, height
        - quality
        - style
        - seed
        - guidance_scale
    
    Returns:
        32-character hex string (MD5 hash)
    """
```

#### Quality Assessment

```python
async def _assess_quality(self, image_data: bytes) -> float:
    """
    Assess image quality using heuristics.
    
    Algorithm:
        resolution_score = min(pixels / (1024×1024), 1.0)
        format_score = 1.0 if PNG/JPEG/WEBP else 0.8
        quality = (resolution_score + format_score) / 2
    
    Returns:
        Quality score [0.0-1.0]
    
    Limitations:
        - No perceptual quality analysis
        - No BRISQUE/NIQE metrics
        - No blur/noise detection
    """
```

#### Utility Methods

```python
def get_supported_apis(self) -> List[Dict[str, Any]]:
    """
    Get list of available APIs.
    
    Returns:
        [
            {
                "name": "flux",
                "available": bool (has API key),
                "endpoint": "https://..."
            },
            ...
        ]
    """

def get_cache_stats(self) -> Dict[str, int]:
    """
    Get cache statistics.
    
    Returns:
        {
            "cached_images": int (number of PNG files),
            "cache_size_mb": float (total size)
        }
    """
```

---

## 📊 Contract Compliance Summary

### Type Safety
| Module | Type Hints | Return Types | Error Types |
|--------|-----------|--------------|-------------|
| SceneAnalyzer | ✅ Complete | ✅ Dict | ❌ Generic |
| MovementPredictor | ✅ Complete | ✅ Dict | ❌ Generic |
| PromptExpander | ✅ Complete | ✅ Dataclass | ✅ Specific |
| ImageGenerator | ✅ Complete | ✅ Dataclass | ✅ Specific |

### Error Handling
| Module | Structured Errors | Retry Logic | Fallbacks |
|--------|------------------|-------------|-----------|
| SceneAnalyzer | ❌ Dicts | ❌ None | ❌ None |
| MovementPredictor | ❌ Dicts | ❌ None | ❌ None |
| PromptExpander | ⚠️ Raises | ✅ Yes (3x) | ❌ None |
| ImageGenerator | ⚠️ Raises | ❌ None | ❌ None |

### Caching Strategy
| Module | Cache Type | Eviction | TTL | Thread-safe |
|--------|-----------|----------|-----|-------------|
| SceneAnalyzer | In-memory | ❌ None | ❌ None | ❌ No |
| MovementPredictor | ❌ None | N/A | N/A | ✅ Yes |
| PromptExpander | In-memory | ✅ LRU | ✅ 1hr | ❌ No |
| ImageGenerator | Filesystem | ❌ None | ❌ None | ✅ Yes |

### Documentation Quality
| Module | Docstrings | Type Hints | Examples | Tests |
|--------|-----------|-----------|----------|-------|
| SceneAnalyzer | ✅ Good | ✅ Yes | ⚠️ Basic | ❌ Missing |
| MovementPredictor | ✅ Good | ✅ Yes | ⚠️ Basic | ❌ Missing |
| PromptExpander | ✅ Excellent | ✅ Yes | ✅ Yes | ❌ Missing |
| ImageGenerator | ✅ Excellent | ✅ Yes | ✅ Yes | ❌ Missing |

---

**Module Contracts Complete**
