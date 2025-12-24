"""
Video Prompt Analyzer for AI Video Generation Models

Analyzes and structures prompts for various AI video generation models,
ensuring optimal temporal consistency and multi-scene coherence.
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ModelType(Enum):
    """Supported AI video generation models"""
    KLING = "kling"
    WAN = "wan"
    RUNWAY = "runway"
    LTX = "ltx"
    LTX2 = "ltx2"
    SORA2 = "sora2"
    VEO3 = "veo3"
    VEO3_1 = "veo3_1"
    HIGGSFIELD = "higgsfield"
    LUMA = "luma"
    PIKA = "pika"
    STABLE_VIDEO_DIFFUSION = "stable_video_diffusion"


@dataclass
class TemporalConsistencyConfig:
    """Configuration for temporal consistency parameters"""
    seed: Optional[int] = None
    temporal_weight: float = 0.8
    motion_strength: float = 0.5
    frame_interpolation: int = 24
    guidance_scale: float = 7.5
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate temporal consistency configuration"""
        errors = []
        
        if self.temporal_weight < 0.0 or self.temporal_weight > 1.0:
            errors.append("temporal_weight must be between 0.0 and 1.0")
        
        if self.motion_strength < 0.0 or self.motion_strength > 1.0:
            errors.append("motion_strength must be between 0.0 and 1.0")
        
        if self.frame_interpolation not in [24, 30, 60]:
            errors.append("frame_interpolation must be 24, 30, or 60 fps")
        
        if self.guidance_scale < 1.0 or self.guidance_scale > 20.0:
            errors.append("guidance_scale must be between 1.0 and 20.0")
        
        return len(errors) == 0, errors


@dataclass
class CameraMotion:
    """Camera motion configuration"""
    type: str = "static"  # static, pan, tilt, zoom, dolly, orbit, crane
    speed: str = "medium"  # slow, medium, fast
    direction: Optional[str] = None  # left, right, up, down, in, out
    focal_length: Optional[int] = 50  # mm
    
    def to_prompt_string(self) -> str:
        """Convert camera motion to prompt string"""
        if self.type == "static":
            return "Camera static, no movement"
        
        motion_desc = f"Camera {self.type}"
        
        if self.direction:
            motion_desc += f" {self.direction}"
        
        motion_desc += f" at {self.speed} speed"
        
        if self.focal_length:
            motion_desc += f", {self.focal_length}mm focal length"
        
        return motion_desc


@dataclass
class SceneTransition:
    """Scene transition configuration"""
    type: str = "fade"  # fade, cut, dissolve
    duration: float = 0.5  # seconds
    
    def to_prompt_string(self) -> str:
        """Convert transition to prompt string"""
        return f"Transition: {self.type} over {self.duration}s"


@dataclass
class PromptStructure:
    """Structured prompt components"""
    subject: str
    action: str
    environment: str
    lighting: str
    atmosphere: str
    camera: CameraMotion
    style: str
    temporal_config: TemporalConsistencyConfig = field(default_factory=TemporalConsistencyConfig)
    
    def to_prompt(self, model_type: ModelType) -> str:
        """Convert structure to model-specific prompt"""
        camera_str = self.camera.to_prompt_string()
        
        # Model-specific formatting
        if model_type == ModelType.KLING:
            return f"{self.subject} {self.action} in {self.environment} lit by {self.lighting}, creating {self.atmosphere}. {camera_str}. {self.style}"
        
        elif model_type == ModelType.WAN:
            return f"{self.subject}: {self.environment} -> {self.action} with {self.atmosphere}. {camera_str}. Style: {self.style}"
        
        elif model_type == ModelType.SORA2:
            return f"Scene: {self.subject} {self.action} in {self.environment}. Lighting: {self.lighting}. Atmosphere: {self.atmosphere}. {camera_str}. Visual style: {self.style}"
        
        elif model_type == ModelType.LUMA:
            return f"{camera_str} showing {self.subject} {self.action} in {self.environment}. {self.lighting} creates {self.atmosphere}. Cinematic {self.style}"
        
        else:
            # Generic format
            return f"{self.subject} {self.action} {self.environment} {self.lighting} {self.atmosphere} {camera_str} {self.style}"


class VideoPromptAnalyzer:
    """Analyzer for AI video generation prompts"""
    
    def __init__(self, catalog_path: str = "configs/video_prompting_catalog.json"):
        """Initialize analyzer with prompt catalog"""
        with open(catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f)
        
        self.model_catalog = self.catalog["model_catalog"]
        self.best_practices = self.catalog["universal_best_practices"]
        self.parameter_glossary = self.catalog["parameter_glossary"]
    
    def get_model_info(self, model_type: ModelType) -> Dict[str, Any]:
        """Get information about a specific model"""
        return self.model_catalog.get(model_type.value, {})
    
    def get_controllability_parameters(self, model_type: ModelType) -> Dict[str, Any]:
        """Get controllability parameters for a model"""
        model_info = self.get_model_info(model_type)
        return model_info.get("controllability_parameters", {})
    
    def get_temporal_critical_params(self, model_type: ModelType) -> List[str]:
        """Get parameters critical for temporal consistency"""
        params = self.get_controllability_parameters(model_type)
        critical = []
        
        for param_name, param_info in params.items():
            if param_info.get("temporal_consistency_impact") in ["critical", "high"]:
                critical.append(param_name)
        
        return critical
    
    def get_best_practices_for_model(self, model_type: ModelType) -> Dict[str, List[str]]:
        """Get best practices for a specific model"""
        model_info = self.get_model_info(model_type)
        return model_info.get("best_practices", {})
    
    def validate_parameters(self, model_type: ModelType, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate parameters against model specifications"""
        model_params = self.get_controllability_parameters(model_type)
        errors = []
        warnings = []
        
        for param_name, param_value in parameters.items():
            if param_name not in model_params:
                warnings.append(f"Parameter '{param_name}' not recognized for {model_type.value}")
                continue
            
            param_spec = model_params[param_name]
            param_type = param_spec.get("type")
            
            # Type validation
            if param_type == "enum":
                allowed_values = param_spec.get("values", [])
                if param_value not in allowed_values:
                    errors.append(f"Parameter '{param_name}' must be one of {allowed_values}, got '{param_value}'")
            
            elif param_type == "range":
                min_val = param_spec.get("min")
                max_val = param_spec.get("max")
                if not (min_val <= param_value <= max_val):
                    errors.append(f"Parameter '{param_name}' must be between {min_val} and {max_val}, got {param_value}")
            
            elif param_type == "boolean":
                if not isinstance(param_value, bool):
                    errors.append(f"Parameter '{param_name}' must be boolean, got {type(param_value).__name__}")
        
        return len(errors) == 0, errors + warnings
    
    def optimize_for_temporal_consistency(
        self,
        model_type: ModelType,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize parameters for temporal consistency"""
        optimized = parameters.copy()
        critical_params = self.get_temporal_critical_params(model_type)
        
        # Apply recommended values for temporal consistency
        if "seed" in critical_params and "seed" not in optimized:
            optimized["seed"] = 42  # Use fixed seed for reproducibility
        
        if "temporal_consistency" in critical_params:
            if optimized.get("temporal_consistency", 0) < 0.7:
                optimized["temporal_consistency"] = 0.8
        
        if "temporal_weight" in critical_params:
            if optimized.get("temporal_weight", 0) < 0.7:
                optimized["temporal_weight"] = 0.8
        
        if "motion_strength" in critical_params:
            # Moderate motion strength for stability
            if optimized.get("motion_strength", 1.0) > 0.7:
                optimized["motion_strength"] = 0.6
        
        if "guidance_scale" in critical_params:
            # Balanced guidance for consistency
            if "guidance_scale" not in optimized:
                optimized["guidance_scale"] = 7.5
        
        return optimized
    
    def generate_multi_scene_plan(
        self,
        scenes: List[PromptStructure],
        model_type: ModelType,
        transitions: Optional[List[SceneTransition]] = None
    ) -> Dict[str, Any]:
        """Generate multi-scene coherence plan"""
        if transitions is None:
            transitions = [SceneTransition(type="fade") for _ in range(len(scenes) - 1)]
        
        # Analyze consistency requirements
        character_descriptions = [scene.subject for scene in scenes]
        environment_descriptions = [scene.environment for scene in scenes]
        lighting_descriptions = [scene.lighting for scene in scenes]
        styles = [scene.style for scene in scenes]
        
        # Check for consistency
        consistency_report = {
            "total_scenes": len(scenes),
            "transitions": [t.type for t in transitions],
            "consistency_checks": {
                "character_consistency": len(set(character_descriptions)) == 1,
                "environment_continuity": len(set(environment_descriptions)) <= 2,
                "lighting_coherence": len(set(lighting_descriptions)) <= 2,
                "style_uniformity": len(set(styles)) == 1
            },
            "recommendations": []
        }
        
        # Generate recommendations
        if not consistency_report["consistency_checks"]["character_consistency"]:
            consistency_report["recommendations"].append(
                "Character descriptions vary across scenes. Consider using identical character descriptions for consistency."
            )
        
        if not consistency_report["consistency_checks"]["style_uniformity"]:
            consistency_report["recommendations"].append(
                "Visual style varies across scenes. Maintain consistent style descriptors for better coherence."
            )
        
        # Generate temporal consistency config for all scenes
        base_seed = scenes[0].temporal_config.seed or 42
        for i, scene in enumerate(scenes):
            scene.temporal_config.seed = base_seed + i
        
        consistency_report["scene_prompts"] = [
            scene.to_prompt(model_type) for scene in scenes
        ]
        
        return consistency_report
    
    def map_to_cinematic_rules(
        self,
        camera_motion: CameraMotion,
        movement_rules: Dict[str, Any]
    ) -> List[str]:
        """Map camera motion to ANIMAtiZE cinematic rules"""
        applicable_rules = []
        
        # Map camera motion to movement prediction rules
        if camera_motion.type in ["pan", "tilt", "orbit"]:
            applicable_rules.append("movement_002: Composition-Guided Camera Flow")
            applicable_rules.append("movement_005: Depth Layer Parallax")
        
        if camera_motion.type in ["zoom", "dolly"]:
            applicable_rules.append("movement_008: Emotional Framing Progression")
        
        if camera_motion.type == "static":
            # Static camera emphasizes subject movement
            applicable_rules.append("movement_001: Pose-to-Action Continuation")
            applicable_rules.append("movement_004: Emotional Momentum Analysis")
        
        # Always apply physics and environmental rules
        applicable_rules.append("movement_003: Physics-Based Environmental Motion")
        applicable_rules.append("movement_006: Atmospheric Response System")
        
        return applicable_rules
    
    def analyze_prompt_quality(self, prompt: str, model_type: ModelType) -> Dict[str, Any]:
        """Analyze prompt quality and provide suggestions"""
        quality_report = {
            "prompt": prompt,
            "model": model_type.value,
            "completeness": {},
            "suggestions": [],
            "score": 0.0
        }
        
        # Check for essential elements
        essential_elements = [
            "subject", "action", "environment", "lighting", "atmosphere", "camera", "style"
        ]
        
        prompt_lower = prompt.lower()
        for element in essential_elements:
            # Simple keyword detection
            quality_report["completeness"][element] = any(
                keyword in prompt_lower 
                for keyword in [element, element + "s", element + "ing"]
            )
        
        # Calculate completeness score
        present_count = sum(quality_report["completeness"].values())
        quality_report["score"] = (present_count / len(essential_elements)) * 100
        
        # Generate suggestions
        for element, present in quality_report["completeness"].items():
            if not present:
                quality_report["suggestions"].append(
                    f"Consider adding {element} description for better results"
                )
        
        # Check for temporal consistency keywords
        temporal_keywords = ["gradually", "slowly", "smoothly", "continuous", "steady"]
        has_temporal_guidance = any(kw in prompt_lower for kw in temporal_keywords)
        
        if not has_temporal_guidance:
            quality_report["suggestions"].append(
                "Add temporal guidance keywords (gradually, slowly, smoothly) for better consistency"
            )
        
        return quality_report


def create_example_scene(model_type: ModelType) -> PromptStructure:
    """Create an example scene for demonstration"""
    camera = CameraMotion(
        type="dolly",
        speed="slow",
        direction="in",
        focal_length=50
    )
    
    temporal_config = TemporalConsistencyConfig(
        seed=42,
        temporal_weight=0.85,
        motion_strength=0.5,
        frame_interpolation=24,
        guidance_scale=7.5
    )
    
    return PromptStructure(
        subject="A young woman in a flowing red dress",
        action="walking through",
        environment="a misty forest at golden hour",
        lighting="warm sunlight filtering through leaves",
        atmosphere="serene and ethereal",
        camera=camera,
        style="cinematic and dreamlike",
        temporal_config=temporal_config
    )


if __name__ == "__main__":
    # Example usage
    analyzer = VideoPromptAnalyzer()
    
    # Analyze Kling model
    kling_info = analyzer.get_model_info(ModelType.KLING)
    print(f"Kling Model Info:")
    print(f"  Max Duration: {kling_info['max_duration']}")
    print(f"  Resolution: {kling_info['max_resolution']}")
    print(f"  Modes: {kling_info['supported_modes']}")
    
    # Get temporal critical parameters
    critical_params = analyzer.get_temporal_critical_params(ModelType.KLING)
    print(f"\nTemporal Critical Parameters: {critical_params}")
    
    # Create and analyze example scene
    scene = create_example_scene(ModelType.KLING)
    prompt = scene.to_prompt(ModelType.KLING)
    print(f"\nGenerated Prompt:\n{prompt}")
    
    # Analyze prompt quality
    quality = analyzer.analyze_prompt_quality(prompt, ModelType.KLING)
    print(f"\nPrompt Quality Score: {quality['score']:.1f}%")
    print(f"Suggestions: {quality['suggestions']}")
    
    # Multi-scene planning
    scenes = [create_example_scene(ModelType.KLING) for _ in range(3)]
    plan = analyzer.generate_multi_scene_plan(scenes, ModelType.KLING)
    print(f"\nMulti-Scene Consistency Report:")
    print(f"  Total Scenes: {plan['total_scenes']}")
    print(f"  Character Consistency: {plan['consistency_checks']['character_consistency']}")
    print(f"  Style Uniformity: {plan['consistency_checks']['style_uniformity']}")
