"""
Prompt Expander Module for ANIMAtiZE Framework
Handles GPT-based prompt expansion for cinematic rule application
Extended with Director Intent Compiler and Control Map System
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
from datetime import datetime
import openai
from openai import OpenAI
import time
from functools import lru_cache


class PromptVersion(str, Enum):
    """Prompt schema versioning"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"


class SchemaVersion(str, Enum):
    """Control map schema versioning"""
    V1_0 = "1.0"
    V2_0 = "2.0"
    V3_0 = "3.0"


class CameraMotionType(str, Enum):
    """Camera motion vocabulary"""
    STATIC = "static"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    DOLLY_IN = "dolly_in"
    DOLLY_OUT = "dolly_out"
    TRACK_LEFT = "track_left"
    TRACK_RIGHT = "track_right"
    CRANE_UP = "crane_up"
    CRANE_DOWN = "crane_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    ORBIT_CLOCKWISE = "orbit_clockwise"
    ORBIT_COUNTER_CLOCKWISE = "orbit_counter_clockwise"
    HANDHELD = "handheld"
    STEADICAM = "steadicam"
    PUSH_IN = "push_in"
    PULL_OUT = "pull_out"


class TransitionType(str, Enum):
    """Shot transition types"""
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    MATCH_CUT = "match_cut"
    JUMP_CUT = "jump_cut"
    SMASH_CUT = "smash_cut"
    CROSSFADE = "crossfade"


class MotionStrength(str, Enum):
    """Motion intensity levels"""
    NONE = "none"
    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"
    EXTREME = "extreme"


@dataclass
class CameraMotion:
    """Camera motion control parameters"""
    motion_type: CameraMotionType
    strength: MotionStrength = MotionStrength.MODERATE
    speed: float = 1.0
    start_time: float = 0.0
    end_time: Optional[float] = None
    easing: str = "linear"
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class CharacterConsistency:
    """Character consistency control"""
    character_id: str
    reference_frames: List[int] = field(default_factory=list)
    feature_weights: Dict[str, float] = field(default_factory=dict)
    appearance_locked: bool = True
    expression_range: Optional[Tuple[str, str]] = None
    clothing_consistency: bool = True
    pose_reference: Optional[str] = None


@dataclass
class ReferenceFrame:
    """Reference frame specification"""
    frame_id: str
    timestamp: float
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    embeddings: Optional[Dict[str, Any]] = None
    weight: float = 1.0
    aspect: str = "full"


@dataclass
class ControlMap:
    """Control map for spatial/temporal guidance"""
    map_type: str
    map_data: Union[str, Dict[str, Any]]
    strength: float = 1.0
    start_frame: int = 0
    end_frame: Optional[int] = None
    preprocessor: Optional[str] = None
    conditioning_scale: float = 1.0


@dataclass
class Storyboard:
    """Storyboard panel specification"""
    panel_id: str
    shot_number: str
    description: str
    camera_angle: str
    composition: str
    duration: float
    reference_image: Optional[str] = None
    motion_notes: Optional[str] = None
    dialogue: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShotTransition:
    """Shot transition specification"""
    from_shot: str
    to_shot: str
    transition_type: TransitionType
    duration: float = 1.0
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeterminismConfig:
    """Determinism and reproducibility controls"""
    seed: Optional[int] = None
    use_fixed_seed: bool = False
    generation_seed: Optional[int] = None
    sampler_seed: Optional[int] = None
    noise_seed: Optional[int] = None
    seed_mode: str = "auto"
    reproducibility_level: str = "standard"


@dataclass
class Shot:
    """Individual shot specification"""
    shot_id: str
    scene_id: str
    prompt: str
    camera_motion: Optional[CameraMotion] = None
    characters: List[CharacterConsistency] = field(default_factory=list)
    reference_frames: List[ReferenceFrame] = field(default_factory=list)
    control_maps: List[ControlMap] = field(default_factory=list)
    fps: int = 24
    duration: float = 5.0
    motion_strength: MotionStrength = MotionStrength.MODERATE
    determinism: Optional[DeterminismConfig] = None
    storyboard_ref: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Scene:
    """Multi-shot scene specification"""
    scene_id: str
    description: str
    shots: List[Shot] = field(default_factory=list)
    transitions: List[ShotTransition] = field(default_factory=list)
    global_characters: List[CharacterConsistency] = field(default_factory=list)
    scene_fps: int = 24
    total_duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelSpecificPrompt:
    """Model-specific compiled prompt"""
    provider: str
    model: str
    compiled_prompt: str
    control_parameters: Dict[str, Any]
    requires_preprocessing: bool = False
    preprocessing_steps: List[str] = field(default_factory=list)
    api_format: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DirectorIntent:
    """High-level director intent specification"""
    intent_id: str
    narrative_description: str
    style_references: List[str] = field(default_factory=list)
    mood: Optional[str] = None
    pacing: Optional[str] = None
    visual_theme: Optional[str] = None
    target_providers: List[str] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
    storyboards: List[Storyboard] = field(default_factory=list)
    global_determinism: Optional[DeterminismConfig] = None
    prompt_version: PromptVersion = PromptVersion.V2_0
    schema_version: SchemaVersion = SchemaVersion.V3_0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompilationResult:
    """Result of prompt compilation"""
    intent_id: str
    model_prompts: List[ModelSpecificPrompt]
    shot_list: List[Shot]
    scene_breakdown: List[Scene]
    control_vocabulary: Dict[str, Any]
    seed_manifest: Dict[str, int]
    compilation_metadata: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    prompt_version: PromptVersion = PromptVersion.V2_0
    schema_version: SchemaVersion = SchemaVersion.V3_0
    compilation_time: float = 0.0


@dataclass
class ExpansionRequest:
    """Request structure for prompt expansion"""
    base_prompt: str
    rules: List[Dict[str, Any]]
    context: Optional[Dict[str, Any]] = None
    max_tokens: int = 500
    temperature: float = 0.7


@dataclass
class ExpansionResult:
    """Result structure from prompt expansion"""
    expanded_prompt: str
    used_rules: List[str]
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]


class SeedManager:
    """Manages seed generation and tracking for reproducibility"""
    
    def __init__(self, base_seed: Optional[int] = None):
        self.base_seed = base_seed or int(time.time())
        self.seed_history: Dict[str, int] = {}
        self.logger = logging.getLogger(__name__)
    
    def generate_seed(self, context: str) -> int:
        """Generate deterministic seed for given context"""
        hash_input = f"{self.base_seed}:{context}"
        hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
        seed = hash_value % (2**31)
        self.seed_history[context] = seed
        return seed
    
    def get_or_create_seed(self, context: str, fixed_seed: Optional[int] = None) -> int:
        """Get existing seed or create new one"""
        if fixed_seed is not None:
            self.seed_history[context] = fixed_seed
            return fixed_seed
        
        if context in self.seed_history:
            return self.seed_history[context]
        
        return self.generate_seed(context)
    
    def export_manifest(self) -> Dict[str, int]:
        """Export seed manifest for reproducibility"""
        return self.seed_history.copy()
    
    def import_manifest(self, manifest: Dict[str, int]):
        """Import seed manifest"""
        self.seed_history.update(manifest)


class ControlVocabulary:
    """Defines and validates control vocabulary"""
    
    CAMERA_MOTION = [motion.value for motion in CameraMotionType]
    MOTION_STRENGTH = [strength.value for strength in MotionStrength]
    TRANSITIONS = [trans.value for trans in TransitionType]
    
    CONTROL_PARAMETERS = {
        'camera_motion': {
            'types': CAMERA_MOTION,
            'strength': MOTION_STRENGTH,
            'speed': {'min': 0.1, 'max': 5.0},
            'easing': ['linear', 'ease_in', 'ease_out', 'ease_in_out']
        },
        'character_consistency': {
            'feature_weights': ['face', 'body', 'clothing', 'hair'],
            'appearance_locked': [True, False],
            'expression_range': ['neutral', 'happy', 'sad', 'angry', 'surprised']
        },
        'reference_frames': {
            'weight': {'min': 0.0, 'max': 1.0},
            'aspect': ['full', 'face', 'body', 'detail']
        },
        'motion_strength': MOTION_STRENGTH,
        'control_maps': {
            'types': ['depth', 'normal', 'edge', 'pose', 'segmentation'],
            'strength': {'min': 0.0, 'max': 2.0},
            'conditioning_scale': {'min': 0.0, 'max': 2.0}
        },
        'fps': [12, 15, 24, 25, 30, 48, 50, 60, 120],
        'shot_transitions': TRANSITIONS
    }
    
    @classmethod
    def validate_control(cls, control_type: str, value: Any) -> Tuple[bool, Optional[str]]:
        """Validate control parameter"""
        if control_type not in cls.CONTROL_PARAMETERS:
            return False, f"Unknown control type: {control_type}"
        
        spec = cls.CONTROL_PARAMETERS[control_type]
        
        if isinstance(spec, list):
            if value not in spec:
                return False, f"Invalid value {value} for {control_type}"
        elif isinstance(spec, dict):
            pass
        
        return True, None
    
    @classmethod
    def get_vocabulary(cls) -> Dict[str, Any]:
        """Get complete control vocabulary"""
        return cls.CONTROL_PARAMETERS.copy()


class PromptCompiler:
    """
    Compiles Director Intent into model-specific prompts with control parameters
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.seed_manager = SeedManager()
        self.control_vocabulary = ControlVocabulary()
        
        self.provider_adapters = {
            'runway': self._compile_for_runway,
            'pika': self._compile_for_pika,
            'sora': self._compile_for_sora,
            'veo': self._compile_for_veo,
            'flux': self._compile_for_flux
        }
    
    def compile(self, intent: DirectorIntent) -> CompilationResult:
        """
        Compile director intent into model-specific prompts
        
        Args:
            intent: High-level director intent
            
        Returns:
            Compilation result with model-specific prompts and controls
        """
        start_time = time.time()
        
        model_prompts = []
        all_shots = []
        warnings = []
        
        if intent.global_determinism:
            self._configure_determinism(intent.global_determinism)
        
        for scene in intent.scenes:
            for shot in scene.shots:
                all_shots.append(shot)
                
                if shot.determinism is None and intent.global_determinism:
                    shot.determinism = intent.global_determinism
                
                if shot.determinism and shot.determinism.use_fixed_seed:
                    context = f"scene:{scene.scene_id}:shot:{shot.shot_id}"
                    shot.determinism.seed = self.seed_manager.get_or_create_seed(
                        context,
                        shot.determinism.seed
                    )
        
        for provider in intent.target_providers:
            if provider in self.provider_adapters:
                try:
                    provider_prompts = self.provider_adapters[provider](intent)
                    model_prompts.extend(provider_prompts)
                except Exception as e:
                    self.logger.error(f"Error compiling for {provider}: {e}")
                    warnings.append(f"Failed to compile for {provider}: {str(e)}")
            else:
                warnings.append(f"No adapter for provider: {provider}")
        
        result = CompilationResult(
            intent_id=intent.intent_id,
            model_prompts=model_prompts,
            shot_list=all_shots,
            scene_breakdown=intent.scenes,
            control_vocabulary=self.control_vocabulary.get_vocabulary(),
            seed_manifest=self.seed_manager.export_manifest(),
            compilation_metadata={
                'intent_version': intent.prompt_version.value,
                'schema_version': intent.schema_version.value,
                'num_scenes': len(intent.scenes),
                'num_shots': len(all_shots),
                'providers': intent.target_providers,
                'has_storyboards': len(intent.storyboards) > 0
            },
            warnings=warnings,
            prompt_version=intent.prompt_version,
            schema_version=intent.schema_version,
            compilation_time=time.time() - start_time
        )
        
        return result
    
    def _configure_determinism(self, config: DeterminismConfig):
        """Configure determinism settings"""
        if config.seed is not None:
            self.seed_manager.base_seed = config.seed
    
    def _compile_for_runway(self, intent: DirectorIntent) -> List[ModelSpecificPrompt]:
        """Compile prompts for Runway Gen-3"""
        prompts = []
        
        for scene in intent.scenes:
            for shot in scene.shots:
                prompt_text = self._enhance_prompt_for_runway(shot, intent)
                
                control_params = {
                    'duration': shot.duration,
                    'fps': shot.fps,
                    'motion_amount': self._map_motion_strength(shot.motion_strength),
                }
                
                if shot.camera_motion:
                    control_params['camera_motion'] = {
                        'type': shot.camera_motion.motion_type.value,
                        'speed': shot.camera_motion.speed,
                        'strength': shot.camera_motion.strength.value
                    }
                
                if shot.determinism and shot.determinism.seed:
                    control_params['seed'] = shot.determinism.seed
                
                if shot.reference_frames:
                    control_params['image_prompt'] = shot.reference_frames[0].image_url or shot.reference_frames[0].image_path
                
                prompts.append(ModelSpecificPrompt(
                    provider='runway',
                    model='gen3',
                    compiled_prompt=prompt_text,
                    control_parameters=control_params,
                    api_format={
                        'text_prompt': prompt_text,
                        **control_params
                    }
                ))
        
        return prompts
    
    def _compile_for_pika(self, intent: DirectorIntent) -> List[ModelSpecificPrompt]:
        """Compile prompts for Pika"""
        prompts = []
        
        for scene in intent.scenes:
            for shot in scene.shots:
                prompt_text = self._enhance_prompt_for_pika(shot, intent)
                
                control_params = {
                    'fps': shot.fps,
                    'motion': self._map_motion_strength_pika(shot.motion_strength),
                }
                
                if shot.camera_motion:
                    control_params['camera'] = self._map_camera_motion_pika(shot.camera_motion)
                
                if shot.determinism and shot.determinism.seed:
                    control_params['seed'] = shot.determinism.seed
                
                prompts.append(ModelSpecificPrompt(
                    provider='pika',
                    model='pika-1.5',
                    compiled_prompt=prompt_text,
                    control_parameters=control_params,
                    api_format={
                        'prompt': prompt_text,
                        'parameters': control_params
                    }
                ))
        
        return prompts
    
    def _compile_for_sora(self, intent: DirectorIntent) -> List[ModelSpecificPrompt]:
        """Compile prompts for OpenAI Sora"""
        prompts = []
        
        for scene in intent.scenes:
            for shot in scene.shots:
                prompt_text = self._enhance_prompt_for_sora(shot, intent)
                
                control_params = {
                    'duration': shot.duration,
                    'resolution': self._get_resolution_for_shot(shot)
                }
                
                if shot.determinism and shot.determinism.seed:
                    control_params['seed'] = shot.determinism.seed
                
                prompts.append(ModelSpecificPrompt(
                    provider='sora',
                    model='sora-1.0',
                    compiled_prompt=prompt_text,
                    control_parameters=control_params,
                    api_format={
                        'prompt': prompt_text,
                        **control_params
                    }
                ))
        
        return prompts
    
    def _compile_for_veo(self, intent: DirectorIntent) -> List[ModelSpecificPrompt]:
        """Compile prompts for Google Veo"""
        prompts = []
        
        for scene in intent.scenes:
            for shot in scene.shots:
                prompt_text = self._enhance_prompt_for_veo(shot, intent)
                
                control_params = {
                    'duration_seconds': shot.duration,
                    'fps': shot.fps,
                }
                
                if shot.camera_motion:
                    control_params['camera_motion'] = shot.camera_motion.motion_type.value
                
                if shot.determinism and shot.determinism.seed:
                    control_params['seed'] = shot.determinism.seed
                
                prompts.append(ModelSpecificPrompt(
                    provider='veo',
                    model='veo-1',
                    compiled_prompt=prompt_text,
                    control_parameters=control_params,
                    api_format={
                        'prompt': prompt_text,
                        'options': control_params
                    }
                ))
        
        return prompts
    
    def _compile_for_flux(self, intent: DirectorIntent) -> List[ModelSpecificPrompt]:
        """Compile prompts for Flux (image generation)"""
        prompts = []
        
        for storyboard in intent.storyboards:
            prompt_text = self._enhance_prompt_for_flux(storyboard, intent)
            
            control_params = {
                'guidance_scale': 7.5,
                'num_inference_steps': 50
            }
            
            if intent.global_determinism and intent.global_determinism.seed:
                control_params['seed'] = self.seed_manager.generate_seed(f"storyboard:{storyboard.panel_id}")
            
            prompts.append(ModelSpecificPrompt(
                provider='flux',
                model='flux-1-dev',
                compiled_prompt=prompt_text,
                control_parameters=control_params,
                api_format={
                    'prompt': prompt_text,
                    **control_params
                }
            ))
        
        return prompts
    
    def _enhance_prompt_for_runway(self, shot: Shot, intent: DirectorIntent) -> str:
        """Enhance prompt with Runway-specific language"""
        parts = [shot.prompt]
        
        if intent.visual_theme:
            parts.append(f"Visual theme: {intent.visual_theme}")
        
        if shot.camera_motion:
            parts.append(f"Camera movement: {shot.camera_motion.motion_type.value}")
        
        if intent.mood:
            parts.append(f"Mood: {intent.mood}")
        
        return ". ".join(parts)
    
    def _enhance_prompt_for_pika(self, shot: Shot, intent: DirectorIntent) -> str:
        """Enhance prompt with Pika-specific language"""
        parts = [shot.prompt]
        
        if shot.motion_strength != MotionStrength.MODERATE:
            parts.append(f"{shot.motion_strength.value} motion")
        
        return ". ".join(parts)
    
    def _enhance_prompt_for_sora(self, shot: Shot, intent: DirectorIntent) -> str:
        """Enhance prompt with Sora-specific language"""
        parts = [shot.prompt]
        
        if intent.visual_theme:
            parts.append(f"in {intent.visual_theme} style")
        
        for character in shot.characters:
            if character.appearance_locked:
                parts.append(f"maintaining consistent appearance for {character.character_id}")
        
        return ". ".join(parts)
    
    def _enhance_prompt_for_veo(self, shot: Shot, intent: DirectorIntent) -> str:
        """Enhance prompt with Veo-specific language"""
        parts = [shot.prompt]
        
        if shot.camera_motion:
            motion_desc = self._describe_camera_motion(shot.camera_motion)
            parts.append(motion_desc)
        
        return ". ".join(parts)
    
    def _enhance_prompt_for_flux(self, storyboard: Storyboard, intent: DirectorIntent) -> str:
        """Enhance prompt for Flux image generation"""
        parts = [storyboard.description]
        
        parts.append(f"Camera angle: {storyboard.camera_angle}")
        parts.append(f"Composition: {storyboard.composition}")
        
        if intent.visual_theme:
            parts.append(f"Style: {intent.visual_theme}")
        
        return ". ".join(parts)
    
    def _map_motion_strength(self, strength: MotionStrength) -> int:
        """Map motion strength to Runway's scale (1-10)"""
        mapping = {
            MotionStrength.NONE: 0,
            MotionStrength.SUBTLE: 3,
            MotionStrength.MODERATE: 5,
            MotionStrength.STRONG: 8,
            MotionStrength.EXTREME: 10
        }
        return mapping.get(strength, 5)
    
    def _map_motion_strength_pika(self, strength: MotionStrength) -> float:
        """Map motion strength to Pika's scale (0.0-1.0)"""
        mapping = {
            MotionStrength.NONE: 0.0,
            MotionStrength.SUBTLE: 0.25,
            MotionStrength.MODERATE: 0.5,
            MotionStrength.STRONG: 0.75,
            MotionStrength.EXTREME: 1.0
        }
        return mapping.get(strength, 0.5)
    
    def _map_camera_motion_pika(self, motion: CameraMotion) -> Dict[str, Any]:
        """Map camera motion to Pika's format"""
        motion_map = {
            CameraMotionType.PAN_LEFT: {'pan': -1.0},
            CameraMotionType.PAN_RIGHT: {'pan': 1.0},
            CameraMotionType.TILT_UP: {'tilt': 1.0},
            CameraMotionType.TILT_DOWN: {'tilt': -1.0},
            CameraMotionType.ZOOM_IN: {'zoom': 1.0},
            CameraMotionType.ZOOM_OUT: {'zoom': -1.0},
        }
        
        base_motion = motion_map.get(motion.motion_type, {})
        
        for key in base_motion:
            base_motion[key] *= motion.speed
        
        return base_motion
    
    def _describe_camera_motion(self, motion: CameraMotion) -> str:
        """Generate natural language description of camera motion"""
        speed_desc = "slowly" if motion.speed < 0.5 else "quickly" if motion.speed > 1.5 else ""
        strength_desc = motion.strength.value
        
        motion_name = motion.motion_type.value.replace('_', ' ')
        
        parts = [p for p in [speed_desc, strength_desc, motion_name] if p]
        return " ".join(parts)
    
    def _get_resolution_for_shot(self, shot: Shot) -> Tuple[int, int]:
        """Determine resolution from shot metadata"""
        if 'resolution' in shot.metadata:
            return tuple(shot.metadata['resolution'])
        return (1920, 1080)


class PromptExpander:
    """GPT-based prompt expansion service with compilation support"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """Initialize the prompt expander with OpenAI API"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided or found in environment")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        self.templates_dir = Path(__file__).parent.parent / "configs" / "templates"
        self.templates = self._load_templates()
        
        self.cache = {}
        self.cache_ttl = 3600
        
        self.compiler = PromptCompiler()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load prompt templates from templates directory"""
        templates = {}
        template_files = [
            "base_expansion.txt",
            "cinematic_expansion.txt",
            "motion_prompt.txt",
            "composition_focus.txt"
        ]
        
        for template_file in template_files:
            template_path = self.templates_dir / template_file
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    templates[template_file.replace('.txt', '')] = f.read()
        
        return templates
    
    @lru_cache(maxsize=128)
    def _get_cache_key(self, request: ExpansionRequest) -> str:
        """Generate cache key for request"""
        rules_str = json.dumps(request.rules, sort_keys=True)
        context_str = json.dumps(request.context or {}, sort_keys=True)
        return f"{request.base_prompt}_{rules_str}_{context_str}"
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if result is cached and not expired"""
        if cache_key not in self.cache:
            return False
        
        timestamp, _ = self.cache[cache_key]
        return time.time() - timestamp < self.cache_ttl
    
    def _get_cached_result(self, cache_key: str) -> Optional[ExpansionResult]:
        """Get cached result if available"""
        if self._is_cached(cache_key):
            _, result = self.cache[cache_key]
            return result
        return None
    
    def _cache_result(self, cache_key: str, result: ExpansionResult):
        """Cache the expansion result"""
        self.cache[cache_key] = (time.time(), result)
    
    def expand_prompt(self, request: ExpansionRequest) -> ExpansionResult:
        """Expand a prompt using cinematic rules and GPT"""
        start_time = time.time()
        
        cache_key = self._get_cache_key(request)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info("Returning cached result")
            return cached_result
        
        try:
            system_prompt = self._build_system_prompt(request)
            user_prompt = self._build_user_prompt(request)
            
            response = self._call_openai_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            expanded_prompt = response.choices[0].message.content.strip()
            
            used_rules = [rule['id'] for rule in request.rules]
            
            confidence = self._calculate_confidence(expanded_prompt, request.rules)
            
            result = ExpansionResult(
                expanded_prompt=expanded_prompt,
                used_rules=used_rules,
                confidence=confidence,
                processing_time=time.time() - start_time,
                metadata={
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens,
                    "cached": False
                }
            )
            
            self._cache_result(cache_key, result)
            
            self.logger.info(f"Prompt expansion completed in {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Error expanding prompt: {str(e)}")
            raise
    
    def compile_director_intent(self, intent: DirectorIntent) -> CompilationResult:
        """
        Compile director intent into model-specific prompts
        
        Args:
            intent: High-level director intent specification
            
        Returns:
            Compilation result with prompts and control parameters
        """
        return self.compiler.compile(intent)
    
    def _build_system_prompt(self, request: ExpansionRequest) -> str:
        """Build system prompt for GPT"""
        base_template = self.templates.get("base_expansion", """
        You are an expert cinematographer and AI prompt engineer. Your task is to expand basic prompts into detailed, cinematic prompts using provided rules and context.
        
        Guidelines:
        - Maintain the original intent while adding cinematic depth
        - Apply relevant rules naturally without being mechanical
        - Focus on visual storytelling and emotional impact
        - Use specific, evocative language
        - Ensure technical accuracy in cinematography terms
        """)
        
        return base_template
    
    def _build_user_prompt(self, request: ExpansionRequest) -> str:
        """Build user prompt with rules and context"""
        rules_text = "\n".join([
            f"- {rule['name']}: {rule['snippet']} (priority: {rule['priority']})"
            for rule in request.rules
        ])
        
        context_text = ""
        if request.context:
            context_text = f"\nContext: {json.dumps(request.context, indent=2)}"
        
        prompt = f"""
        Base prompt: {request.base_prompt}
        
        Apply these cinematic rules:
        {rules_text}
        
        {context_text}
        
        Expand this into a detailed, cinematic prompt that incorporates the rules naturally while maintaining the original creative intent.
        """
        
        return prompt
    
    def _call_openai_with_retry(self, system_prompt: str, user_prompt: str, 
                               max_tokens: int, temperature: float, max_retries: int = 3) -> Any:
        """Call OpenAI API with retry logic"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=30
                )
                return response
                
            except openai.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Rate limit hit, retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    raise
            
            except openai.APIError as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise
    
    def _calculate_confidence(self, expanded_prompt: str, rules: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on prompt quality"""
        
        confidence = 0.5
        
        cinematic_keywords = [
            "camera", "shot", "angle", "lighting", "composition", "depth", "focus",
            "movement", "tracking", "zoom", "pan", "tilt", "dolly", "crane"
        ]
        
        keyword_count = sum(1 for keyword in cinematic_keywords if keyword in expanded_prompt.lower())
        confidence += min(keyword_count * 0.05, 0.3)
        
        rule_count = len(rules)
        confidence += min(rule_count * 0.02, 0.2)
        
        descriptive_indicators = [
            "beautiful", "dramatic", "elegant", "smooth", "dynamic", "cinematic"
        ]
        
        descriptive_count = sum(1 for indicator in descriptive_indicators if indicator in expanded_prompt.lower())
        confidence += min(descriptive_count * 0.03, 0.15)
        
        return min(confidence, 1.0)
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        self.logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cached_items": len(self.cache),
            "max_cache_size": 128,
            "cache_ttl": self.cache_ttl
        }


if __name__ == "__main__":
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        expander = PromptExpander(api_key=api_key)
        
        test_request = ExpansionRequest(
            base_prompt="A person walking through a city street",
            rules=[
                {"id": "rule_003", "name": "Pan Following", "snippet": "smooth horizontal pan tracking movement", "priority": 0.9},
                {"id": "rule_016", "name": "Golden Hour Lighting", "snippet": "warm golden hour light creating long shadows", "priority": 0.9}
            ],
            context={"time_of_day": "evening", "mood": "contemplative"}
        )
        
        result = expander.expand_prompt(test_request)
        print(f"Expanded: {result.expanded_prompt}")
        print(f"Confidence: {result.confidence}")
        print(f"Processing time: {result.processing_time}s")
    else:
        print("Please set OPENAI_API_KEY environment variable")
