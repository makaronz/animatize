"""
Video Prompt Generator for AI Video Generation Models

Generates optimized prompts for various AI video models based on
temporal consistency requirements and cinematic rules.
Enhanced with video-specific controls and versioning.
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib

from src.analyzers.video_prompt_analyzer import (
    ModelType,
    PromptStructure,
    CameraMotion,
    TemporalConsistencyConfig,
    VideoPromptAnalyzer,
)


@dataclass
class VideoControlParameters:
    """Video-specific control parameters for generation"""

    camera_motion: CameraMotion = field(default_factory=lambda: CameraMotion())
    duration_seconds: float = 5.0
    fps: int = 24
    shot_type: str = "medium"  # wide, medium, close-up, extreme_close-up
    transitions: Optional[str] = None  # fade, cut, dissolve, wipe, cross_dissolve
    motion_strength: float = 0.5

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate video control parameters"""
        errors = []

        if self.duration_seconds <= 0 or self.duration_seconds > 60:
            errors.append("duration_seconds must be between 0 and 60")

        if self.fps not in [24, 25, 30, 60]:
            errors.append("fps must be 24, 25, 30, or 60")

        if self.shot_type not in ["wide", "medium", "close-up", "extreme_close-up", "establishing"]:
            errors.append("shot_type must be one of: wide, medium, close-up, extreme_close-up, establishing")

        if self.transitions and self.transitions not in ["fade", "cut", "dissolve", "wipe", "cross_dissolve"]:
            errors.append("transitions must be one of: fade, cut, dissolve, wipe, cross_dissolve")

        if self.motion_strength < 0.0 or self.motion_strength > 1.0:
            errors.append("motion_strength must be between 0.0 and 1.0")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["camera_motion"] = {
            "type": self.camera_motion.type,
            "speed": self.camera_motion.speed,
            "direction": self.camera_motion.direction,
            "focal_length": self.camera_motion.focal_length,
        }
        return data


@dataclass
class DeterminismConfig:
    """Configuration for deterministic/reproducible generation"""

    seed: Optional[int] = None
    enable_seed_management: bool = True
    seed_increment_per_scene: int = 1
    use_hash_based_seed: bool = False
    seed_hash_source: Optional[str] = None

    def generate_seed(self, scene_index: int = 0, prompt_text: Optional[str] = None) -> int:
        """Generate reproducible seed based on configuration"""
        if self.seed is not None:
            return self.seed + (scene_index * self.seed_increment_per_scene)

        if self.use_hash_based_seed and prompt_text:
            hash_obj = hashlib.md5(prompt_text.encode())
            return int(hash_obj.hexdigest()[:8], 16) % (2**31)

        if self.seed_hash_source:
            hash_obj = hashlib.md5(self.seed_hash_source.encode())
            return int(hash_obj.hexdigest()[:8], 16) % (2**31)

        return 42


@dataclass
class PromptVersion:
    """Version tracking for prompts"""

    prompt_version: str = "1.0.0"
    schema_version: str = "2.0.0"
    generator_version: str = "2.0.0"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CinematicRuleApplication:
    """Tracks which cinematic rules were applied"""

    rule_ids: List[str] = field(default_factory=list)
    rule_names: List[str] = field(default_factory=list)
    enhancements: Dict[str, str] = field(default_factory=dict)
    total_rules_applied: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CompiledPrompt:
    """Fully compiled video prompt with all metadata"""

    prompt_text: str
    model_type: ModelType
    control_parameters: VideoControlParameters
    determinism_config: DeterminismConfig
    version: PromptVersion
    cinematic_rules: CinematicRuleApplication
    temporal_config: TemporalConsistencyConfig
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        return {
            "prompt_text": self.prompt_text,
            "model_type": self.model_type.value,
            "control_parameters": self.control_parameters.to_dict(),
            "determinism": {
                "seed": self.determinism_config.seed,
                "enable_seed_management": self.determinism_config.enable_seed_management,
                "seed_increment_per_scene": self.determinism_config.seed_increment_per_scene,
            },
            "version": self.version.to_dict(),
            "cinematic_rules": self.cinematic_rules.to_dict(),
            "temporal_config": {
                "seed": self.temporal_config.seed,
                "temporal_weight": self.temporal_config.temporal_weight,
                "motion_strength": self.temporal_config.motion_strength,
                "frame_interpolation": self.temporal_config.frame_interpolation,
                "guidance_scale": self.temporal_config.guidance_scale,
            },
            "metadata": self.metadata,
        }


@dataclass
class VideoGenerationRequest:
    """Request for video generation with full specifications"""

    model_type: ModelType
    scene_description: str
    duration: float = 5.0
    aspect_ratio: str = "16:9"
    style: str = "cinematic"
    temporal_consistency_priority: str = "high"
    include_audio: bool = False
    custom_parameters: Dict[str, Any] = None
    control_parameters: Optional[VideoControlParameters] = None
    determinism_config: Optional[DeterminismConfig] = None


class VideoPromptCompiler:
    """
    Enhanced Video Prompt Compiler with Director Intent Compilation

    Compiles director intent into model-specific video prompts with:
    - Video-specific control parameters
    - Versioning and schema tracking
    - Cinematic rules integration
    - Determinism controls
    """

    def __init__(
        self,
        catalog_path: str = "configs/video_prompting_catalog.json",
        rules_path: str = "configs/movement_prediction_rules.json",
    ):
        """Initialize compiler with catalogs and rules"""
        self.analyzer = VideoPromptAnalyzer(catalog_path)

        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

        with open(rules_path, "r", encoding="utf-8") as f:
            self.cinematic_rules = json.load(f)

        self.compiler_version = "2.0.0"
        self.schema_version = "2.0.0"

    def load_cinematic_rules(self, rules_path: str = None) -> Dict[str, Any]:
        """Load cinematic rules from JSON"""
        if rules_path:
            with open(rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self.cinematic_rules

    def parse_director_intent(self, intent_description: str) -> Dict[str, Any]:
        """Parse director's intent into structured components"""
        components = {
            "subject": "",
            "action": "",
            "environment": "",
            "lighting": "",
            "atmosphere": "",
            "camera": "",
            "style": "",
            "emotional_tone": "",
            "narrative_purpose": "",
        }

        keywords = {
            "subject": ["person", "character", "figure", "man", "woman", "child", "animal", "subject"],
            "action": ["walking", "running", "dancing", "sitting", "standing", "moving", "performs", "doing"],
            "environment": ["forest", "city", "room", "beach", "mountain", "desert", "sky", "location", "setting"],
            "lighting": ["sunlight", "moonlight", "shadows", "bright", "dark", "golden hour", "lit by", "lighting"],
            "atmosphere": ["misty", "foggy", "clear", "cloudy", "serene", "dramatic", "tense", "peaceful"],
            "camera": ["camera", "zoom", "pan", "dolly", "static", "tracking", "shot", "angle"],
            "style": ["cinematic", "realistic", "artistic", "stylized", "animated", "documentary"],
            "emotional_tone": ["joyful", "somber", "tense", "peaceful", "mysterious", "uplifting"],
            "narrative_purpose": ["establish", "reveal", "emphasize", "transition", "conclude"],
        }

        sentences = intent_description.split(".")

        for component, component_keywords in keywords.items():
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in component_keywords):
                    components[component] = sentence.strip()
                    break

        if not components["subject"]:
            components["subject"] = sentences[0] if sentences else intent_description

        return components

    def infer_shot_type(self, description: str, style: str) -> str:
        """Infer shot type from description and style"""
        description_lower = description.lower()

        if any(kw in description_lower for kw in ["wide", "landscape", "establishing", "panoramic"]):
            return "wide"
        elif any(kw in description_lower for kw in ["close-up", "closeup", "face", "eyes", "detail"]):
            return "close-up"
        elif any(kw in description_lower for kw in ["extreme close", "macro", "intimate"]):
            return "extreme_close-up"
        else:
            return "medium"

    def infer_camera_motion(self, description: str, style: str) -> CameraMotion:
        """Infer appropriate camera motion from description and style"""
        description_lower = description.lower()

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
            if style == "cinematic":
                return CameraMotion(type="dolly", speed="slow", direction="in", focal_length=50)
            else:
                return CameraMotion(type="static", focal_length=35)

    def apply_cinematic_rules_to_intent(
        self, intent_components: Dict[str, Any], control_params: VideoControlParameters
    ) -> CinematicRuleApplication:
        """Apply 47+ cinematic rules to director intent"""
        rules_data = self.cinematic_rules
        applicable_rules = []
        rule_names = []
        enhancements = {}

        movement_rules = rules_data.get("movement_prediction_rules", [])

        for rule in movement_rules:
            rule_id = rule.get("id", "")
            rule_name = rule.get("rule_name", "")
            category = rule.get("category", "")
            must_do = rule.get("must_do", False)

            apply_rule = False

            if category == "camera_movement":
                if control_params.camera_motion.type in ["pan", "tilt", "orbit", "zoom", "dolly", "crane"]:
                    apply_rule = True
                    if "Composition-Guided" in rule_name:
                        enhancements["camera_composition"] = (
                            f"{control_params.camera_motion.to_prompt_string()} "
                            "following compositional flow and leading lines"
                        )
                    elif "Depth Layer Parallax" in rule_name:
                        enhancements["parallax"] = (
                            "Foreground, midground, and background layers move at different speeds creating depth"
                        )
                    elif "Emotional Framing" in rule_name:
                        enhancements["framing"] = f"{control_params.shot_type} shot progresses with emotional intensity"

            elif category == "character_action":
                if intent_components.get("action"):
                    apply_rule = True
                    if "Pose-to-Action" in rule_name:
                        enhancements["action_continuity"] = (
                            f"{intent_components.get('action', '')} continues naturally from body position and momentum"
                        )
                    elif "Emotional Momentum" in rule_name:
                        enhancements["emotional_flow"] = (
                            f"Emotional state evolves naturally through {intent_components.get('action', '')}"
                        )
                    elif "Interaction Anticipation" in rule_name:
                        enhancements["interaction"] = (
                            "Character interactions with environment follow natural gaze and gesture patterns"
                        )

            elif category == "environment_animation":
                if intent_components.get("environment"):
                    apply_rule = True
                    if "Physics-Based" in rule_name:
                        enhancements["physics"] = (
                            f"Environmental elements in {intent_components.get('environment', '')} "
                            "follow realistic physics"
                        )
                    elif "Atmospheric Response" in rule_name:
                        enhancements["atmosphere"] = (
                            f"{intent_components.get('atmosphere', '')} atmosphere with natural environmental response"
                        )

            if apply_rule or must_do:
                applicable_rules.append(rule_id)
                rule_names.append(rule_name)

        return CinematicRuleApplication(
            rule_ids=applicable_rules,
            rule_names=rule_names,
            enhancements=enhancements,
            total_rules_applied=len(applicable_rules),
        )

    def generate_temporal_config(
        self,
        model_type: ModelType,
        priority: str = "high",
        determinism: Optional[DeterminismConfig] = None,
        scene_index: int = 0,
        prompt_text: Optional[str] = None,
    ) -> TemporalConsistencyConfig:
        """Generate temporal consistency configuration with determinism"""
        configs = {
            "low": TemporalConsistencyConfig(
                temporal_weight=0.5, motion_strength=0.7, frame_interpolation=24, guidance_scale=7.0
            ),
            "medium": TemporalConsistencyConfig(
                temporal_weight=0.7, motion_strength=0.5, frame_interpolation=30, guidance_scale=7.5
            ),
            "high": TemporalConsistencyConfig(
                temporal_weight=0.85, motion_strength=0.4, frame_interpolation=30, guidance_scale=8.0
            ),
            "critical": TemporalConsistencyConfig(
                temporal_weight=0.95, motion_strength=0.3, frame_interpolation=60, guidance_scale=9.0
            ),
        }

        config = configs.get(priority, configs["high"])

        if determinism and determinism.enable_seed_management:
            config.seed = determinism.generate_seed(scene_index, prompt_text)

        return config

    def compile_prompt_structure(self, request: VideoGenerationRequest, scene_index: int = 0) -> PromptStructure:
        """Compile structured prompt from director intent"""
        components = self.parse_director_intent(request.scene_description)

        if request.control_parameters:
            camera = request.control_parameters.camera_motion
            motion_strength = request.control_parameters.motion_strength
        else:
            camera = self.infer_camera_motion(request.scene_description, request.style)
            motion_strength = 0.5

        temporal_config = self.generate_temporal_config(
            request.model_type,
            request.temporal_consistency_priority,
            request.determinism_config,
            scene_index,
            request.scene_description,
        )

        temporal_config.motion_strength = motion_strength

        structure = PromptStructure(
            subject=components.get("subject", ""),
            action=components.get("action", ""),
            environment=components.get("environment", ""),
            lighting=components.get("lighting", "natural lighting"),
            atmosphere=components.get("atmosphere", "atmospheric"),
            camera=camera,
            style=request.style,
            temporal_config=temporal_config,
        )

        return structure

    def compile_model_specific_prompt(
        self,
        structure: PromptStructure,
        model_type: ModelType,
        cinematic_rules: CinematicRuleApplication,
        control_params: VideoControlParameters,
    ) -> str:
        """Compile model-specific prompt with cinematic rule enhancements"""
        base_prompt = structure.to_prompt(model_type)

        enhancements_text = []
        for key, enhancement in cinematic_rules.enhancements.items():
            enhancements_text.append(enhancement)

        if enhancements_text:
            enhanced_prompt = f"{base_prompt} {' '.join(enhancements_text)}"
        else:
            enhanced_prompt = base_prompt

        shot_descriptor = f"{control_params.shot_type} shot"
        if shot_descriptor.lower() not in enhanced_prompt.lower():
            enhanced_prompt = f"{shot_descriptor}: {enhanced_prompt}"

        fps_descriptor = f"{control_params.fps}fps"
        if model_type in [ModelType.KLING, ModelType.SORA2, ModelType.RUNWAY]:
            enhanced_prompt = f"{enhanced_prompt} [{fps_descriptor}]"

        return enhanced_prompt

    def compile_video_prompt(self, request: VideoGenerationRequest, scene_index: int = 0) -> CompiledPrompt:
        """
        Compile complete video prompt from director intent

        Returns fully compiled prompt with all metadata, controls, and versioning
        """
        if request.control_parameters is None:
            request.control_parameters = VideoControlParameters(
                camera_motion=self.infer_camera_motion(request.scene_description, request.style),
                duration_seconds=request.duration,
                fps=24,
                shot_type=self.infer_shot_type(request.scene_description, request.style),
                motion_strength=0.5,
            )

        if request.determinism_config is None:
            request.determinism_config = DeterminismConfig(seed=42, enable_seed_management=True)

        is_valid, messages = request.control_parameters.validate()
        if not is_valid:
            raise ValueError(f"Invalid control parameters: {messages}")

        structure = self.compile_prompt_structure(request, scene_index)

        intent_components = self.parse_director_intent(request.scene_description)
        cinematic_rules = self.apply_cinematic_rules_to_intent(intent_components, request.control_parameters)

        prompt_text = self.compile_model_specific_prompt(
            structure, request.model_type, cinematic_rules, request.control_parameters
        )

        version = PromptVersion(
            prompt_version="1.0.0",
            schema_version=self.schema_version,
            generator_version=self.compiler_version,
            model_type=request.model_type.value,
        )

        metadata = {
            "scene_index": scene_index,
            "director_intent": request.scene_description,
            "rules_applied_count": cinematic_rules.total_rules_applied,
            "temporal_priority": request.temporal_consistency_priority,
            "style": request.style,
            "aspect_ratio": request.aspect_ratio,
        }

        compiled = CompiledPrompt(
            prompt_text=prompt_text,
            model_type=request.model_type,
            control_parameters=request.control_parameters,
            determinism_config=request.determinism_config,
            version=version,
            cinematic_rules=cinematic_rules,
            temporal_config=structure.temporal_config,
            metadata=metadata,
        )

        return compiled

    def compile_model_parameters(self, compiled_prompt: CompiledPrompt) -> Dict[str, Any]:
        """Generate model-specific parameters from compiled prompt"""
        params = compiled_prompt.control_parameters
        temporal = compiled_prompt.temporal_config

        model_params = self.analyzer.get_controllability_parameters(compiled_prompt.model_type)

        parameters = {
            "duration": params.duration_seconds,
            "aspect_ratio": compiled_prompt.metadata.get("aspect_ratio", "16:9"),
            "style": compiled_prompt.metadata.get("style", "cinematic"),
            "fps": params.fps,
            "shot_type": params.shot_type,
        }

        if "seed" in model_params and temporal.seed:
            parameters["seed"] = temporal.seed

        if "temporal_weight" in model_params:
            parameters["temporal_weight"] = temporal.temporal_weight

        if "temporal_consistency" in model_params:
            parameters["temporal_consistency"] = temporal.temporal_weight

        if "motion_strength" in model_params:
            parameters["motion_strength"] = params.motion_strength

        if "frame_interpolation" in model_params:
            parameters["frame_interpolation"] = temporal.frame_interpolation

        if "guidance_scale" in model_params:
            parameters["guidance_scale"] = temporal.guidance_scale

        if "camera_movement" in model_params:
            parameters["camera_movement"] = params.camera_motion.type

        if "camera_speed" in model_params:
            parameters["camera_speed"] = params.camera_motion.speed

        if "focal_length" in model_params and params.camera_motion.focal_length:
            parameters["focal_length"] = params.camera_motion.focal_length

        if params.transitions:
            if "transition_type" in model_params:
                parameters["transition_type"] = params.transitions

        is_valid, messages = self.analyzer.validate_parameters(compiled_prompt.model_type, parameters)

        if is_valid:
            parameters = self.analyzer.optimize_for_temporal_consistency(compiled_prompt.model_type, parameters)

        return parameters

    def compile_multi_scene_prompts(
        self,
        scene_descriptions: List[str],
        model_type: ModelType,
        shared_config: Optional[VideoGenerationRequest] = None,
    ) -> Dict[str, Any]:
        """Compile prompts for multiple scenes with coherence"""
        if shared_config is None:
            shared_config = VideoGenerationRequest(
                model_type=model_type,
                scene_description="",
                duration=5.0,
                temporal_consistency_priority="high",
                determinism_config=DeterminismConfig(seed=42, enable_seed_management=True),
            )

        compiled_scenes = []
        for i, description in enumerate(scene_descriptions):
            request = VideoGenerationRequest(
                model_type=model_type,
                scene_description=description,
                duration=shared_config.duration,
                aspect_ratio=shared_config.aspect_ratio,
                style=shared_config.style,
                temporal_consistency_priority=shared_config.temporal_consistency_priority,
                determinism_config=shared_config.determinism_config,
            )

            compiled = self.compile_video_prompt(request, scene_index=i)
            compiled_scenes.append(compiled)

        result = {
            "version": {"schema_version": self.schema_version, "compiler_version": self.compiler_version},
            "model": model_type.value,
            "total_scenes": len(scene_descriptions),
            "coherence_strategy": {
                "determinism_enabled": shared_config.determinism_config.enable_seed_management,
                "base_seed": shared_config.determinism_config.seed,
                "seed_increment": shared_config.determinism_config.seed_increment_per_scene,
            },
            "scenes": [],
        }

        for i, compiled in enumerate(compiled_scenes):
            scene_data = {
                "scene_number": i + 1,
                "compiled_prompt": compiled.to_dict(),
                "parameters": self.compile_model_parameters(compiled),
            }
            result["scenes"].append(scene_data)

        base_subject = compiled_scenes[0].prompt_text.split()[0] if compiled_scenes else ""
        result["consistency_analysis"] = {
            "character_consistency": all(base_subject in scene.prompt_text for scene in compiled_scenes),
            "style_uniformity": len(set(s.metadata.get("style") for s in compiled_scenes)) == 1,
            "rules_applied_per_scene": [s.cinematic_rules.total_rules_applied for s in compiled_scenes],
            "average_rules_applied": sum(s.cinematic_rules.total_rules_applied for s in compiled_scenes)
            / len(compiled_scenes),
        }

        return result


class VideoPromptGenerator(VideoPromptCompiler):
    """
    Legacy VideoPromptGenerator maintained for backward compatibility
    Inherits from VideoPromptCompiler
    """

    def __init__(self, catalog_path: str = "configs/video_prompting_catalog.json"):
        super().__init__(catalog_path)

    def parse_scene_description(self, description: str) -> Dict[str, str]:
        """Legacy method - calls parse_director_intent"""
        return self.parse_director_intent(description)

    def generate_prompt_structure(self, request: VideoGenerationRequest) -> PromptStructure:
        """Legacy method - calls compile_prompt_structure"""
        return self.compile_prompt_structure(request)

    def generate_prompt(self, request: VideoGenerationRequest) -> str:
        """Legacy method - compiles and returns prompt text"""
        compiled = self.compile_video_prompt(request)
        return compiled.prompt_text

    def generate_model_parameters(self, request: VideoGenerationRequest) -> Dict[str, Any]:
        """Legacy method - compiles and returns parameters"""
        compiled = self.compile_video_prompt(request)
        return self.compile_model_parameters(compiled)

    def generate_multi_scene_prompts(
        self,
        scene_descriptions: List[str],
        model_type: ModelType,
        shared_config: Optional[VideoGenerationRequest] = None,
    ) -> Dict[str, Any]:
        """Legacy method - calls compile_multi_scene_prompts"""
        return self.compile_multi_scene_prompts(scene_descriptions, model_type, shared_config)

    def apply_cinematic_rules(
        self, structure: PromptStructure, rules_path: str = "configs/movement_prediction_rules.json"
    ) -> Dict[str, Any]:
        """Legacy method for applying cinematic rules"""
        with open(rules_path, "r", encoding="utf-8") as f:
            rules = json.load(f)

        applicable_rules = self.analyzer.map_to_cinematic_rules(structure.camera, rules)

        enhancements = {
            "original_prompt": structure.to_prompt(ModelType.KLING),
            "applicable_rules": applicable_rules,
            "enhanced_components": {},
        }

        for rule_id in applicable_rules:
            if "Composition-Guided" in rule_id:
                enhancements["enhanced_components"][
                    "camera"
                ] = f"{structure.camera.to_prompt_string()}, following compositional elements"

            if "Emotional Framing" in rule_id:
                enhancements["enhanced_components"][
                    "atmosphere"
                ] = f"{structure.atmosphere}, with emotional framing progression"

            if "Physics-Based" in rule_id:
                enhancements["enhanced_components"][
                    "environment"
                ] = f"{structure.environment}, with realistic physics-based motion"

        return enhancements


if __name__ == "__main__":
    # Example usage of enhanced compiler
    compiler = VideoPromptCompiler()

    # Example 1: Single scene with full control
    control_params = VideoControlParameters(
        camera_motion=CameraMotion(type="dolly", speed="slow", direction="in", focal_length=50),
        duration_seconds=8.0,
        fps=24,
        shot_type="medium",
        motion_strength=0.4,
    )

    determinism = DeterminismConfig(seed=12345, enable_seed_management=True, seed_increment_per_scene=100)

    request = VideoGenerationRequest(
        model_type=ModelType.KLING,
        scene_description=(
            "A young woman in a red dress walks through a misty forest at golden hour. "
            "Camera slowly dollies in."
        ),
        duration=8.0,
        aspect_ratio="16:9",
        style="cinematic",
        temporal_consistency_priority="high",
        control_parameters=control_params,
        determinism_config=determinism,
    )

    compiled = compiler.compile_video_prompt(request)
    parameters = compiler.compile_model_parameters(compiled)

    print("=== Enhanced Video Prompt Compiler ===")
    print("\nCompiled Prompt:")
    print(compiled.prompt_text)

    print("\n\nVersion Info:")
    print(json.dumps(compiled.version.to_dict(), indent=2))

    print("\n\nCinematic Rules Applied:")
    print(f"Total Rules: {compiled.cinematic_rules.total_rules_applied}")
    print("Rule IDs:", compiled.cinematic_rules.rule_ids[:3])

    print("\n\nControl Parameters:")
    print(json.dumps(compiled.control_parameters.to_dict(), indent=2))

    print("\n\nDeterminism Config:")
    print(f"Seed: {compiled.temporal_config.seed}")

    print("\n\nModel Parameters:")
    print(json.dumps(parameters, indent=2))

    print("\n\nFull Export:")
    print(json.dumps(compiled.to_dict(), indent=2))

    # Example 2: Multi-scene compilation
    scenes = [
        "A warrior stands on a cliff at sunrise, wind blowing through their cloak",
        "The warrior draws their sword, determination in their eyes",
        "The warrior charges into battle, camera tracking alongside",
    ]

    multi_scene_result = compiler.compile_multi_scene_prompts(
        scenes,
        ModelType.SORA2,
        VideoGenerationRequest(
            model_type=ModelType.SORA2,
            scene_description="",
            duration=6.0,
            determinism_config=DeterminismConfig(seed=99999),
        ),
    )

    print("\n\n=== Multi-Scene Compilation ===")
    print(f"Total Scenes: {multi_scene_result['total_scenes']}")
    print(f"Schema Version: {multi_scene_result['version']['schema_version']}")
    print(f"Average Rules Applied: {multi_scene_result['consistency_analysis']['average_rules_applied']:.1f}")
    print(f"\nScene 1 Seed: {multi_scene_result['scenes'][0]['compiled_prompt']['temporal_config']['seed']}")
    print(f"Scene 2 Seed: {multi_scene_result['scenes'][1]['compiled_prompt']['temporal_config']['seed']}")
    print(f"Scene 3 Seed: {multi_scene_result['scenes'][2]['compiled_prompt']['temporal_config']['seed']}")
