"""
Video Prompt Generator for AI Video Generation Models

Generates optimized prompts for various AI video models based on
temporal consistency requirements and cinematic rules.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from src.analyzers.video_prompt_analyzer import (
    ModelType,
    PromptStructure,
    CameraMotion,
    TemporalConsistencyConfig,
    VideoPromptAnalyzer
)


@dataclass
class VideoGenerationRequest:
    """Request for video generation with full specifications"""
    model_type: ModelType
    scene_description: str
    duration: float
    aspect_ratio: str = "16:9"
    style: str = "cinematic"
    temporal_consistency_priority: str = "high"  # low, medium, high, critical
    include_audio: bool = False
    custom_parameters: Dict[str, Any] = None


class VideoPromptGenerator:
    """Generator for optimized video prompts"""
    
    def __init__(self, catalog_path: str = "configs/video_prompting_catalog.json"):
        """Initialize generator"""
        self.analyzer = VideoPromptAnalyzer(catalog_path)
        
        with open(catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f)
    
    def parse_scene_description(self, description: str) -> Dict[str, str]:
        """Parse natural language scene description into components"""
        # Simple keyword-based parsing (can be enhanced with NLP)
        components = {
            "subject": "",
            "action": "",
            "environment": "",
            "lighting": "",
            "atmosphere": "",
            "camera": "",
            "style": ""
        }
        
        # Extract components using keyword matching
        keywords = {
            "subject": ["person", "character", "figure", "man", "woman", "child", "animal"],
            "action": ["walking", "running", "dancing", "sitting", "standing", "moving"],
            "environment": ["forest", "city", "room", "beach", "mountain", "desert", "sky"],
            "lighting": ["sunlight", "moonlight", "shadows", "bright", "dark", "golden hour"],
            "atmosphere": ["misty", "foggy", "clear", "cloudy", "serene", "dramatic"],
            "camera": ["camera", "zoom", "pan", "dolly", "static", "tracking"],
            "style": ["cinematic", "realistic", "artistic", "stylized", "animated"]
        }
        
        description_lower = description.lower()
        sentences = description.split('.')
        
        for component, component_keywords in keywords.items():
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in component_keywords):
                    components[component] = sentence.strip()
                    break
        
        # If components not found, distribute description
        if not components["subject"]:
            components["subject"] = sentences[0] if sentences else description
        
        return components
    
    def generate_temporal_config(
        self,
        model_type: ModelType,
        priority: str = "high"
    ) -> TemporalConsistencyConfig:
        """Generate temporal consistency configuration based on priority"""
        configs = {
            "low": TemporalConsistencyConfig(
                temporal_weight=0.5,
                motion_strength=0.7,
                frame_interpolation=24,
                guidance_scale=7.0
            ),
            "medium": TemporalConsistencyConfig(
                temporal_weight=0.7,
                motion_strength=0.5,
                frame_interpolation=30,
                guidance_scale=7.5
            ),
            "high": TemporalConsistencyConfig(
                temporal_weight=0.85,
                motion_strength=0.4,
                frame_interpolation=30,
                guidance_scale=8.0
            ),
            "critical": TemporalConsistencyConfig(
                seed=42,  # Fixed seed for maximum reproducibility
                temporal_weight=0.95,
                motion_strength=0.3,
                frame_interpolation=60,
                guidance_scale=9.0
            )
        }
        
        return configs.get(priority, configs["high"])
    
    def infer_camera_motion(self, description: str, style: str) -> CameraMotion:
        """Infer appropriate camera motion from description and style"""
        description_lower = description.lower()
        
        # Match camera motion keywords
        if "zoom" in description_lower:
            return CameraMotion(type="zoom", speed="medium", direction="in" if "in" in description_lower else "out")
        elif "pan" in description_lower:
            direction = "right" if "right" in description_lower else "left"
            return CameraMotion(type="pan", speed="slow", direction=direction)
        elif "orbit" in description_lower or "circle" in description_lower:
            return CameraMotion(type="orbit", speed="slow")
        elif "dolly" in description_lower:
            direction = "in" if "closer" in description_lower or "approach" in description_lower else "out"
            return CameraMotion(type="dolly", speed="slow", direction=direction)
        elif "crane" in description_lower or "rise" in description_lower:
            return CameraMotion(type="crane", speed="slow", direction="up")
        else:
            # Default based on style
            if style == "cinematic":
                return CameraMotion(type="dolly", speed="slow", direction="in", focal_length=50)
            else:
                return CameraMotion(type="static", focal_length=35)
    
    def generate_prompt_structure(
        self,
        request: VideoGenerationRequest
    ) -> PromptStructure:
        """Generate structured prompt from request"""
        # Parse scene description
        components = self.parse_scene_description(request.scene_description)
        
        # Infer camera motion
        camera = self.infer_camera_motion(
            request.scene_description,
            request.style
        )
        
        # Generate temporal config
        temporal_config = self.generate_temporal_config(
            request.model_type,
            request.temporal_consistency_priority
        )
        
        # Create prompt structure
        structure = PromptStructure(
            subject=components.get("subject", ""),
            action=components.get("action", ""),
            environment=components.get("environment", ""),
            lighting=components.get("lighting", "natural lighting"),
            atmosphere=components.get("atmosphere", "atmospheric"),
            camera=camera,
            style=request.style,
            temporal_config=temporal_config
        )
        
        return structure
    
    def generate_prompt(self, request: VideoGenerationRequest) -> str:
        """Generate optimized prompt for video generation"""
        structure = self.generate_prompt_structure(request)
        prompt = structure.to_prompt(request.model_type)
        
        return prompt
    
    def generate_model_parameters(
        self,
        request: VideoGenerationRequest
    ) -> Dict[str, Any]:
        """Generate model-specific parameters"""
        structure = self.generate_prompt_structure(request)
        
        # Base parameters
        parameters = {
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio,
            "style": request.style
        }
        
        # Add temporal consistency parameters
        temporal_config = structure.temporal_config
        
        # Model-specific parameter mapping
        model_params = self.analyzer.get_controllability_parameters(request.model_type)
        
        if "seed" in model_params and temporal_config.seed:
            parameters["seed"] = temporal_config.seed
        
        if "temporal_weight" in model_params:
            parameters["temporal_weight"] = temporal_config.temporal_weight
        
        if "temporal_consistency" in model_params:
            parameters["temporal_consistency"] = temporal_config.temporal_weight
        
        if "motion_strength" in model_params:
            parameters["motion_strength"] = temporal_config.motion_strength
        
        if "frame_interpolation" in model_params:
            parameters["frame_interpolation"] = temporal_config.frame_interpolation
        
        if "guidance_scale" in model_params:
            parameters["guidance_scale"] = temporal_config.guidance_scale
        
        # Camera-specific parameters
        if "camera_movement" in model_params:
            parameters["camera_movement"] = structure.camera.type
        
        if "camera_type" in model_params:
            camera_types = {
                "static": "tripod",
                "dolly": "steadicam",
                "orbit": "drone",
                "crane": "crane"
            }
            parameters["camera_type"] = camera_types.get(structure.camera.type, "steadicam")
        
        if "focal_length" in model_params and structure.camera.focal_length:
            parameters["focal_length"] = structure.camera.focal_length
        
        # Audio parameters
        if request.include_audio:
            if "audio_sync" in model_params:
                parameters["audio_sync"] = True
            if "sound_effects" in model_params:
                parameters["sound_effects"] = True
        
        # Add custom parameters
        if request.custom_parameters:
            parameters.update(request.custom_parameters)
        
        # Validate and optimize
        is_valid, messages = self.analyzer.validate_parameters(
            request.model_type,
            parameters
        )
        
        if is_valid:
            parameters = self.analyzer.optimize_for_temporal_consistency(
                request.model_type,
                parameters
            )
        
        return parameters
    
    def generate_multi_scene_prompts(
        self,
        scene_descriptions: List[str],
        model_type: ModelType,
        shared_config: Optional[VideoGenerationRequest] = None
    ) -> Dict[str, Any]:
        """Generate prompts for multiple scenes with coherence"""
        if shared_config is None:
            shared_config = VideoGenerationRequest(
                model_type=model_type,
                scene_description="",
                duration=5.0,
                temporal_consistency_priority="high"
            )
        
        # Generate structures for all scenes
        structures = []
        for description in scene_descriptions:
            request = VideoGenerationRequest(
                model_type=model_type,
                scene_description=description,
                duration=shared_config.duration,
                aspect_ratio=shared_config.aspect_ratio,
                style=shared_config.style,
                temporal_consistency_priority=shared_config.temporal_consistency_priority
            )
            structure = self.generate_prompt_structure(request)
            structures.append(structure)
        
        # Apply coherence
        base_subject = structures[0].subject
        base_style = structures[0].style
        base_seed = structures[0].temporal_config.seed or 42
        
        for i, structure in enumerate(structures):
            # Maintain character consistency
            if not structure.subject:
                structure.subject = base_subject
            
            # Maintain style consistency
            structure.style = base_style
            
            # Sequential seeds for consistency
            structure.temporal_config.seed = base_seed + i
        
        # Generate multi-scene plan
        plan = self.analyzer.generate_multi_scene_plan(
            structures,
            model_type
        )
        
        # Generate prompts and parameters
        result = {
            "model": model_type.value,
            "total_scenes": len(scene_descriptions),
            "scenes": []
        }
        
        for i, structure in enumerate(structures):
            scene_data = {
                "scene_number": i + 1,
                "prompt": structure.to_prompt(model_type),
                "parameters": self.generate_model_parameters(
                    VideoGenerationRequest(
                        model_type=model_type,
                        scene_description=scene_descriptions[i],
                        duration=shared_config.duration,
                        aspect_ratio=shared_config.aspect_ratio,
                        style=shared_config.style
                    )
                )
            }
            result["scenes"].append(scene_data)
        
        result["coherence_analysis"] = plan
        
        return result
    
    def apply_cinematic_rules(
        self,
        structure: PromptStructure,
        rules_path: str = "configs/movement_prediction_rules.json"
    ) -> Dict[str, Any]:
        """Apply ANIMAtiZE cinematic rules to prompt structure"""
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        # Map camera motion to applicable rules
        applicable_rules = self.analyzer.map_to_cinematic_rules(
            structure.camera,
            rules
        )
        
        # Apply rule-based enhancements
        enhancements = {
            "original_prompt": structure.to_prompt(ModelType.KLING),
            "applicable_rules": applicable_rules,
            "enhanced_components": {}
        }
        
        # Enhance based on rules
        for rule_id in applicable_rules:
            if "Composition-Guided" in rule_id:
                enhancements["enhanced_components"]["camera"] = (
                    f"{structure.camera.to_prompt_string()}, following compositional elements"
                )
            
            if "Emotional Framing" in rule_id:
                enhancements["enhanced_components"]["atmosphere"] = (
                    f"{structure.atmosphere}, with emotional framing progression"
                )
            
            if "Physics-Based" in rule_id:
                enhancements["enhanced_components"]["environment"] = (
                    f"{structure.environment}, with realistic physics-based motion"
                )
        
        return enhancements


if __name__ == "__main__":
    # Example usage
    generator = VideoPromptGenerator()
    
    # Single scene generation
    request = VideoGenerationRequest(
        model_type=ModelType.KLING,
        scene_description="A young woman in a red dress walks through a misty forest at golden hour. Camera slowly dollies in.",
        duration=8.0,
        aspect_ratio="16:9",
        style="cinematic",
        temporal_consistency_priority="high"
    )
    
    prompt = generator.generate_prompt(request)
    parameters = generator.generate_model_parameters(request)
    
    print("Generated Prompt:")
    print(prompt)
    print("\nGeneration Parameters:")
    print(json.dumps(parameters, indent=2))
    
    # Multi-scene generation
    scenes = [
        "A warrior stands on a cliff at sunrise, wind blowing through their cloak",
        "The warrior draws their sword, determination in their eyes",
        "The warrior charges into battle, camera tracking alongside"
    ]
    
    multi_scene_result = generator.generate_multi_scene_prompts(
        scenes,
        ModelType.SORA2
    )
    
    print("\n\nMulti-Scene Generation:")
    print(f"Total Scenes: {multi_scene_result['total_scenes']}")
    print(f"Character Consistency: {multi_scene_result['coherence_analysis']['consistency_checks']['character_consistency']}")
    
    for scene in multi_scene_result['scenes']:
        print(f"\nScene {scene['scene_number']}:")
        print(f"  Prompt: {scene['prompt'][:100]}...")
