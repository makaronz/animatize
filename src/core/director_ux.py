"""
Director UX Control Surface for ANIMAtiZE Framework

Provides professional-grade control interface for video generation with:
- Professional controls (duration, fps, camera motion, shot types, transitions)
- Pro vs Auto modes
- Iteration workflow (compare, refine, lock parameters)
- Control presets (documentary, commercial, art house, action)
- Validation for all control parameters
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json
import uuid


class DirectorMode(str, Enum):
    """Operating modes for director interface"""

    AUTO = "auto"
    PRO = "pro"


class ShotType(str, Enum):
    """Standard shot types from film grammar"""

    EXTREME_WIDE = "extreme_wide"
    WIDE = "wide"
    FULL = "full"
    MEDIUM = "medium"
    CLOSEUP = "closeup"
    EXTREME_CLOSEUP = "extreme_closeup"
    OVER_SHOULDER = "over_shoulder"
    POV = "pov"
    INSERT = "insert"
    CUTAWAY = "cutaway"
    TWO_SHOT = "two_shot"
    GROUP_SHOT = "group_shot"


class CameraAngle(str, Enum):
    """Camera angle types"""

    EYE_LEVEL = "eye_level"
    HIGH_ANGLE = "high_angle"
    LOW_ANGLE = "low_angle"
    BIRDS_EYE = "birds_eye"
    WORMS_EYE = "worms_eye"
    DUTCH_ANGLE = "dutch_angle"
    OVERHEAD = "overhead"


class CameraMovementType(str, Enum):
    """Camera movement types from movement predictor and film grammar"""

    STATIC = "static"
    PAN = "pan"
    TILT = "tilt"
    DOLLY = "dolly"
    TRACK = "track"
    TRACKING_SHOT = "tracking_shot"
    CRANE = "crane"
    ZOOM = "zoom"
    ORBIT = "orbit"
    HANDHELD = "handheld"
    STEADICAM = "steadicam"
    PUSH = "push"
    SLOW_PUSH = "slow_push"
    PULL = "pull"
    WHIP_PAN = "whip_pan"
    SUBTLE_TILT = "subtle_tilt"


class TransitionStyle(str, Enum):
    """Transition types between shots"""

    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    MATCH_CUT = "match_cut"
    JUMP_CUT = "jump_cut"
    SMASH_CUT = "smash_cut"
    CROSSFADE = "crossfade"
    FADE_TO_BLACK = "fade_to_black"
    FADE_FROM_BLACK = "fade_from_black"


class MotionStrengthLevel(str, Enum):
    """Motion intensity levels"""

    NONE = "none"
    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"
    EXTREME = "extreme"


class StylePreset(str, Enum):
    """Visual style presets"""

    DOCUMENTARY = "documentary"
    COMMERCIAL = "commercial"
    ART_HOUSE = "art_house"
    ACTION = "action"
    DRAMA = "drama"
    THRILLER = "thriller"
    COMEDY = "comedy"
    HORROR = "horror"
    MUSIC_VIDEO = "music_video"
    CORPORATE = "corporate"
    EDITORIAL = "editorial"
    EXPERIMENTAL = "experimental"


class ValidationError(Exception):
    """Raised when control parameter validation fails"""

    pass


@dataclass
class CameraControl:
    """Professional camera control parameters"""

    movement_type: CameraMovementType = CameraMovementType.STATIC
    angle: CameraAngle = CameraAngle.EYE_LEVEL
    shot_type: ShotType = ShotType.MEDIUM
    focal_length: int = 50  # mm (12-200mm range)
    speed: float = 1.0  # 0.1-5.0
    strength: MotionStrengthLevel = MotionStrengthLevel.MODERATE
    easing: str = "linear"  # linear, ease_in, ease_out, ease_in_out
    start_time: float = 0.0
    end_time: Optional[float] = None

    def validate(self) -> List[str]:
        """Validate camera control parameters"""
        errors = []

        if self.focal_length < 12 or self.focal_length > 200:
            errors.append(f"Focal length {self.focal_length}mm out of range (12-200mm)")

        if self.speed < 0.1 or self.speed > 5.0:
            errors.append(f"Speed {self.speed} out of range (0.1-5.0)")

        if self.easing not in ["linear", "ease_in", "ease_out", "ease_in_out"]:
            errors.append(f"Invalid easing function: {self.easing}")

        if self.start_time < 0:
            errors.append(f"Start time cannot be negative: {self.start_time}")

        if self.end_time is not None and self.end_time <= self.start_time:
            errors.append(f"End time {self.end_time} must be after start time {self.start_time}")

        return errors

    def to_internal_params(self) -> Dict[str, Any]:
        """Convert to internal parameter format"""
        return {
            "camera_motion": {
                "type": self.movement_type.value,
                "speed": self.speed,
                "strength": self.strength.value,
                "easing": self.easing,
                "start_time": self.start_time,
                "end_time": self.end_time,
            },
            "camera_angle": self.angle.value,
            "shot_type": self.shot_type.value,
            "focal_length": self.focal_length,
        }


@dataclass
class TransitionControl:
    """Transition control parameters"""

    style: TransitionStyle = TransitionStyle.CUT
    duration: float = 1.0  # seconds
    offset: float = 0.0  # offset from end of shot
    parameters: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """Validate transition control parameters"""
        errors = []

        if self.duration < 0 or self.duration > 10.0:
            errors.append(f"Transition duration {self.duration}s out of range (0-10s)")

        if self.offset < 0:
            errors.append(f"Transition offset cannot be negative: {self.offset}")

        return errors

    def to_internal_params(self) -> Dict[str, Any]:
        """Convert to internal parameter format"""
        return {
            "transition_type": self.style.value,
            "duration": self.duration,
            "offset": self.offset,
            **self.parameters,
        }


@dataclass
class TimingControl:
    """Timing and tempo control"""

    duration: float = 5.0  # seconds (1-60s range)
    fps: int = 24  # frames per second (12, 24, 30, 60)
    speed_factor: float = 1.0  # 0.25-4.0 (slow motion / time lapse)
    start_offset: float = 0.0

    def validate(self) -> List[str]:
        """Validate timing control parameters"""
        errors = []

        if self.duration < 1.0 or self.duration > 60.0:
            errors.append(f"Duration {self.duration}s out of range (1-60s)")

        if self.fps not in [12, 24, 25, 30, 48, 60, 120]:
            errors.append(f"FPS {self.fps} not a standard value (12, 24, 25, 30, 48, 60, 120)")

        if self.speed_factor < 0.25 or self.speed_factor > 4.0:
            errors.append(f"Speed factor {self.speed_factor} out of range (0.25-4.0)")

        if self.start_offset < 0:
            errors.append(f"Start offset cannot be negative: {self.start_offset}")

        return errors

    def to_internal_params(self) -> Dict[str, Any]:
        """Convert to internal parameter format"""
        return {
            "duration": self.duration,
            "fps": self.fps,
            "speed_factor": self.speed_factor,
            "start_offset": self.start_offset,
        }


@dataclass
class MotionControl:
    """Subject and scene motion control"""

    overall_strength: MotionStrengthLevel = MotionStrengthLevel.MODERATE
    subject_motion: float = 0.5  # 0.0-1.0
    camera_motion: float = 0.5  # 0.0-1.0
    background_motion: float = 0.3  # 0.0-1.0
    motion_blur: bool = True
    motion_blur_amount: float = 0.5  # 0.0-1.0

    def validate(self) -> List[str]:
        """Validate motion control parameters"""
        errors = []

        if self.subject_motion < 0.0 or self.subject_motion > 1.0:
            errors.append(f"Subject motion {self.subject_motion} out of range (0.0-1.0)")

        if self.camera_motion < 0.0 or self.camera_motion > 1.0:
            errors.append(f"Camera motion {self.camera_motion} out of range (0.0-1.0)")

        if self.background_motion < 0.0 or self.background_motion > 1.0:
            errors.append(f"Background motion {self.background_motion} out of range (0.0-1.0)")

        if self.motion_blur_amount < 0.0 or self.motion_blur_amount > 1.0:
            errors.append(f"Motion blur amount {self.motion_blur_amount} out of range (0.0-1.0)")

        return errors

    def to_internal_params(self) -> Dict[str, Any]:
        """Convert to internal parameter format"""
        return {
            "motion_strength": self.overall_strength.value,
            "subject_motion": self.subject_motion,
            "camera_motion": self.camera_motion,
            "background_motion": self.background_motion,
            "motion_blur": self.motion_blur,
            "motion_blur_amount": self.motion_blur_amount,
        }


@dataclass
class ParameterLock:
    """Lock status for iteration workflow"""

    locked: bool = False
    locked_at: Optional[str] = None
    locked_value: Optional[Any] = None
    notes: str = ""


@dataclass
class GenerationComparison:
    """Comparison data for iteration workflow"""

    generation_id: str
    parameters: Dict[str, Any]
    result_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    rating: Optional[int] = None  # 1-5
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class DirectorControls:
    """Complete director control surface"""

    control_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mode: DirectorMode = DirectorMode.AUTO

    # Core controls
    camera: CameraControl = field(default_factory=CameraControl)
    timing: TimingControl = field(default_factory=TimingControl)
    motion: MotionControl = field(default_factory=MotionControl)
    transition: Optional[TransitionControl] = None

    # Style and creative direction
    style_preset: Optional[StylePreset] = None
    visual_style: str = "cinematic"
    mood: str = "neutral"
    color_grade: str = "natural"

    # Advanced controls (Pro mode)
    depth_of_field: float = 0.5  # 0.0-1.0
    lighting_style: str = "natural"
    composition_rule: str = "rule_of_thirds"
    aspect_ratio: str = "16:9"

    # Parameter locks for iteration
    locked_parameters: Dict[str, ParameterLock] = field(default_factory=dict)

    # Iteration history
    generation_history: List[GenerationComparison] = field(default_factory=list)

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    modified_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "1.0"

    def validate(self) -> Dict[str, Any]:
        """
        Validate all control parameters

        Returns:
            Dictionary with validation results
        """
        results = {"valid": True, "errors": [], "warnings": []}

        # Validate camera controls
        camera_errors = self.camera.validate()
        if camera_errors:
            results["errors"].extend([f"Camera: {e}" for e in camera_errors])
            results["valid"] = False

        # Validate timing controls
        timing_errors = self.timing.validate()
        if timing_errors:
            results["errors"].extend([f"Timing: {e}" for e in timing_errors])
            results["valid"] = False

        # Validate motion controls
        motion_errors = self.motion.validate()
        if motion_errors:
            results["errors"].extend([f"Motion: {e}" for e in motion_errors])
            results["valid"] = False

        # Validate transition controls
        if self.transition:
            transition_errors = self.transition.validate()
            if transition_errors:
                results["errors"].extend([f"Transition: {e}" for e in transition_errors])
                results["valid"] = False

        # Validate depth of field
        if self.depth_of_field < 0.0 or self.depth_of_field > 1.0:
            results["errors"].append(f"Depth of field {self.depth_of_field} out of range (0.0-1.0)")
            results["valid"] = False

        # Validate aspect ratio
        valid_ratios = ["16:9", "4:3", "21:9", "1:1", "9:16"]
        if self.aspect_ratio not in valid_ratios:
            results["warnings"].append(f"Unusual aspect ratio: {self.aspect_ratio}")

        # Pro mode validation
        if self.mode == DirectorMode.PRO:
            if self.camera.movement_type == CameraMovementType.STATIC and self.camera.speed > 1.0:
                results["warnings"].append("Static camera with speed > 1.0 has no effect")

        return results

    def lock_parameter(self, parameter_name: str, value: Any, notes: str = ""):
        """Lock a parameter for iteration refinement"""
        self.locked_parameters[parameter_name] = ParameterLock(
            locked=True, locked_at=datetime.utcnow().isoformat(), locked_value=value, notes=notes
        )
        self.modified_at = datetime.utcnow().isoformat()

    def unlock_parameter(self, parameter_name: str):
        """Unlock a parameter"""
        if parameter_name in self.locked_parameters:
            self.locked_parameters[parameter_name].locked = False
            self.modified_at = datetime.utcnow().isoformat()

    def add_comparison(self, comparison: GenerationComparison):
        """Add generation to comparison history"""
        self.generation_history.append(comparison)
        self.modified_at = datetime.utcnow().isoformat()

    def get_best_generation(self) -> Optional[GenerationComparison]:
        """Get highest rated generation"""
        rated = [g for g in self.generation_history if g.rating is not None]
        if not rated:
            return None
        return max(rated, key=lambda x: x.rating)

    def to_internal_params(self) -> Dict[str, Any]:
        """Convert all controls to internal parameter format"""
        params = {}

        # Camera parameters
        params.update(self.camera.to_internal_params())

        # Timing parameters
        params.update(self.timing.to_internal_params())

        # Motion parameters
        params.update(self.motion.to_internal_params())

        # Transition parameters
        if self.transition:
            params["transition"] = self.transition.to_internal_params()

        # Style parameters
        params.update(
            {
                "visual_style": self.visual_style,
                "mood": self.mood,
                "color_grade": self.color_grade,
                "depth_of_field": self.depth_of_field,
                "lighting_style": self.lighting_style,
                "composition_rule": self.composition_rule,
                "aspect_ratio": self.aspect_ratio,
            }
        )

        # Apply locked parameters
        for param_name, lock in self.locked_parameters.items():
            if lock.locked and lock.locked_value is not None:
                params[param_name] = lock.locked_value

        return params

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DirectorControls":
        """Create from dictionary"""
        camera_data = data.get("camera", {})
        camera = CameraControl(
            movement_type=CameraMovementType(camera_data.get("movement_type", "static")),
            angle=CameraAngle(camera_data.get("angle", "eye_level")),
            shot_type=ShotType(camera_data.get("shot_type", "medium")),
            focal_length=camera_data.get("focal_length", 50),
            speed=camera_data.get("speed", 1.0),
            strength=MotionStrengthLevel(camera_data.get("strength", "moderate")),
            easing=camera_data.get("easing", "linear"),
            start_time=camera_data.get("start_time", 0.0),
            end_time=camera_data.get("end_time"),
        )

        timing_data = data.get("timing", {})
        timing = TimingControl(
            duration=timing_data.get("duration", 5.0),
            fps=timing_data.get("fps", 24),
            speed_factor=timing_data.get("speed_factor", 1.0),
            start_offset=timing_data.get("start_offset", 0.0),
        )

        motion_data = data.get("motion", {})
        motion = MotionControl(
            overall_strength=MotionStrengthLevel(motion_data.get("overall_strength", "moderate")),
            subject_motion=motion_data.get("subject_motion", 0.5),
            camera_motion=motion_data.get("camera_motion", 0.5),
            background_motion=motion_data.get("background_motion", 0.3),
            motion_blur=motion_data.get("motion_blur", True),
            motion_blur_amount=motion_data.get("motion_blur_amount", 0.5),
        )

        transition = None
        if "transition" in data and data["transition"]:
            trans_data = data["transition"]
            transition = TransitionControl(
                style=TransitionStyle(trans_data.get("style", "cut")),
                duration=trans_data.get("duration", 1.0),
                offset=trans_data.get("offset", 0.0),
                parameters=trans_data.get("parameters", {}),
            )

        return cls(
            control_id=data.get("control_id", str(uuid.uuid4())),
            mode=DirectorMode(data.get("mode", "auto")),
            camera=camera,
            timing=timing,
            motion=motion,
            transition=transition,
            style_preset=StylePreset(data["style_preset"]) if "style_preset" in data and data["style_preset"] else None,
            visual_style=data.get("visual_style", "cinematic"),
            mood=data.get("mood", "neutral"),
            color_grade=data.get("color_grade", "natural"),
            depth_of_field=data.get("depth_of_field", 0.5),
            lighting_style=data.get("lighting_style", "natural"),
            composition_rule=data.get("composition_rule", "rule_of_thirds"),
            aspect_ratio=data.get("aspect_ratio", "16:9"),
            locked_parameters=data.get("locked_parameters", {}),
            generation_history=data.get("generation_history", []),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            modified_at=data.get("modified_at", datetime.utcnow().isoformat()),
            version=data.get("version", "1.0"),
        )


class PresetLibrary:
    """Library of professional style presets"""

    @staticmethod
    def get_preset(preset_type: StylePreset) -> DirectorControls:
        """Get a predefined style preset"""

        if preset_type == StylePreset.DOCUMENTARY:
            return DirectorControls(
                mode=DirectorMode.PRO,
                camera=CameraControl(
                    movement_type=CameraMovementType.HANDHELD,
                    angle=CameraAngle.EYE_LEVEL,
                    shot_type=ShotType.MEDIUM,
                    focal_length=35,
                    speed=0.8,
                    strength=MotionStrengthLevel.SUBTLE,
                ),
                timing=TimingControl(duration=8.0, fps=24),
                motion=MotionControl(
                    overall_strength=MotionStrengthLevel.SUBTLE, subject_motion=0.4, camera_motion=0.6
                ),
                transition=TransitionControl(style=TransitionStyle.CUT),
                style_preset=StylePreset.DOCUMENTARY,
                visual_style="naturalistic",
                mood="observational",
                color_grade="neutral",
                depth_of_field=0.7,
                lighting_style="natural",
                composition_rule="rule_of_thirds",
            )

        elif preset_type == StylePreset.COMMERCIAL:
            return DirectorControls(
                mode=DirectorMode.PRO,
                camera=CameraControl(
                    movement_type=CameraMovementType.DOLLY,
                    angle=CameraAngle.EYE_LEVEL,
                    shot_type=ShotType.MEDIUM,
                    focal_length=50,
                    speed=0.6,
                    strength=MotionStrengthLevel.MODERATE,
                    easing="ease_in_out",
                ),
                timing=TimingControl(duration=5.0, fps=30),
                motion=MotionControl(
                    overall_strength=MotionStrengthLevel.MODERATE,
                    subject_motion=0.5,
                    camera_motion=0.7,
                    motion_blur=True,
                ),
                transition=TransitionControl(style=TransitionStyle.DISSOLVE, duration=0.8),
                style_preset=StylePreset.COMMERCIAL,
                visual_style="polished",
                mood="aspirational",
                color_grade="vibrant",
                depth_of_field=0.4,
                lighting_style="three_point",
                composition_rule="golden_ratio",
            )

        elif preset_type == StylePreset.ART_HOUSE:
            return DirectorControls(
                mode=DirectorMode.PRO,
                camera=CameraControl(
                    movement_type=CameraMovementType.TRACKING_SHOT,
                    angle=CameraAngle.LOW_ANGLE,
                    shot_type=ShotType.WIDE,
                    focal_length=24,
                    speed=0.4,
                    strength=MotionStrengthLevel.SUBTLE,
                    easing="linear",
                ),
                timing=TimingControl(duration=12.0, fps=24, speed_factor=0.8),
                motion=MotionControl(
                    overall_strength=MotionStrengthLevel.SUBTLE, subject_motion=0.3, camera_motion=0.4
                ),
                transition=TransitionControl(style=TransitionStyle.FADE, duration=2.0),
                style_preset=StylePreset.ART_HOUSE,
                visual_style="atmospheric",
                mood="contemplative",
                color_grade="desaturated",
                depth_of_field=0.6,
                lighting_style="chiaroscuro",
                composition_rule="symmetry",
            )

        elif preset_type == StylePreset.ACTION:
            return DirectorControls(
                mode=DirectorMode.PRO,
                camera=CameraControl(
                    movement_type=CameraMovementType.HANDHELD,
                    angle=CameraAngle.EYE_LEVEL,
                    shot_type=ShotType.MEDIUM,
                    focal_length=35,
                    speed=1.8,
                    strength=MotionStrengthLevel.STRONG,
                ),
                timing=TimingControl(duration=3.0, fps=60, speed_factor=1.0),
                motion=MotionControl(
                    overall_strength=MotionStrengthLevel.EXTREME,
                    subject_motion=0.9,
                    camera_motion=0.8,
                    motion_blur=True,
                    motion_blur_amount=0.7,
                ),
                transition=TransitionControl(style=TransitionStyle.SMASH_CUT),
                style_preset=StylePreset.ACTION,
                visual_style="dynamic",
                mood="intense",
                color_grade="high_contrast",
                depth_of_field=0.3,
                lighting_style="dramatic",
                composition_rule="dynamic_diagonal",
            )

        elif preset_type == StylePreset.DRAMA:
            return DirectorControls(
                mode=DirectorMode.PRO,
                camera=CameraControl(
                    movement_type=CameraMovementType.SLOW_PUSH,
                    angle=CameraAngle.EYE_LEVEL,
                    shot_type=ShotType.CLOSEUP,
                    focal_length=85,
                    speed=0.5,
                    strength=MotionStrengthLevel.SUBTLE,
                    easing="ease_in",
                ),
                timing=TimingControl(duration=6.0, fps=24),
                motion=MotionControl(
                    overall_strength=MotionStrengthLevel.SUBTLE, subject_motion=0.3, camera_motion=0.5
                ),
                transition=TransitionControl(style=TransitionStyle.CROSSFADE, duration=1.5),
                style_preset=StylePreset.DRAMA,
                visual_style="intimate",
                mood="emotional",
                color_grade="warm",
                depth_of_field=0.2,
                lighting_style="soft",
                composition_rule="center_weighted",
            )

        elif preset_type == StylePreset.MUSIC_VIDEO:
            return DirectorControls(
                mode=DirectorMode.PRO,
                camera=CameraControl(
                    movement_type=CameraMovementType.ORBIT,
                    angle=CameraAngle.HIGH_ANGLE,
                    shot_type=ShotType.FULL,
                    focal_length=35,
                    speed=1.2,
                    strength=MotionStrengthLevel.STRONG,
                    easing="ease_in_out",
                ),
                timing=TimingControl(duration=4.0, fps=30),
                motion=MotionControl(
                    overall_strength=MotionStrengthLevel.STRONG, subject_motion=0.7, camera_motion=0.9, motion_blur=True
                ),
                transition=TransitionControl(style=TransitionStyle.WIPE, duration=0.5),
                style_preset=StylePreset.MUSIC_VIDEO,
                visual_style="stylized",
                mood="energetic",
                color_grade="saturated",
                depth_of_field=0.5,
                lighting_style="theatrical",
                composition_rule="balanced",
            )

        else:
            # Default preset
            return DirectorControls()

    @staticmethod
    def list_presets() -> List[Dict[str, str]]:
        """List all available presets with descriptions"""
        return [
            {
                "name": StylePreset.DOCUMENTARY.value,
                "description": "Naturalistic, observational style with handheld camera and subtle motion",
                "use_case": "Reality content, interviews, behind-the-scenes",
            },
            {
                "name": StylePreset.COMMERCIAL.value,
                "description": "Polished, professional look with smooth camera moves and vibrant colors",
                "use_case": "Product showcases, brand content, advertising",
            },
            {
                "name": StylePreset.ART_HOUSE.value,
                "description": "Atmospheric, contemplative style with slow movements and artistic framing",
                "use_case": "Artistic content, experimental videos, mood pieces",
            },
            {
                "name": StylePreset.ACTION.value,
                "description": "Dynamic, intense style with fast movement and high energy",
                "use_case": "Action sequences, sports, high-energy content",
            },
            {
                "name": StylePreset.DRAMA.value,
                "description": "Intimate, emotional style with close shots and subtle camera work",
                "use_case": "Character moments, emotional scenes, narrative content",
            },
            {
                "name": StylePreset.MUSIC_VIDEO.value,
                "description": "Stylized, energetic with bold camera moves and creative transitions",
                "use_case": "Music videos, performance content, creative projects",
            },
        ]


class IterationWorkflow:
    """Manages iteration and refinement workflow"""

    def __init__(self, controls: DirectorControls):
        self.controls = controls
        self.current_variation: Optional[Dict[str, Any]] = None

    def create_variation(self, parameter_changes: Dict[str, Any], preserve_locked: bool = True) -> DirectorControls:
        """Create a variation with modified parameters"""
        # Start with current controls
        variation = DirectorControls.from_dict(self.controls.to_dict())
        variation.control_id = str(uuid.uuid4())

        # Apply changes
        for param, value in parameter_changes.items():
            if preserve_locked and param in self.controls.locked_parameters:
                lock = self.controls.locked_parameters[param]
                if lock.locked:
                    continue  # Skip locked parameters

            # Apply change based on parameter path
            self._apply_parameter_change(variation, param, value)

        return variation

    def _apply_parameter_change(self, controls: DirectorControls, param_path: str, value: Any):
        """Apply a parameter change to controls"""
        parts = param_path.split(".")

        if parts[0] == "camera":
            if len(parts) > 1:
                setattr(controls.camera, parts[1], value)
        elif parts[0] == "timing":
            if len(parts) > 1:
                setattr(controls.timing, parts[1], value)
        elif parts[0] == "motion":
            if len(parts) > 1:
                setattr(controls.motion, parts[1], value)
        elif parts[0] == "transition":
            if controls.transition and len(parts) > 1:
                setattr(controls.transition, parts[1], value)
        else:
            setattr(controls, parts[0], value)

    def compare_generations(self, generations: List[GenerationComparison]) -> Dict[str, Any]:
        """Compare multiple generations and provide analysis"""
        if not generations:
            return {"error": "No generations to compare"}

        comparison = {
            "total_generations": len(generations),
            "rated_count": len([g for g in generations if g.rating is not None]),
            "generations": [],
        }

        # Sort by rating
        sorted_gens = sorted([g for g in generations if g.rating is not None], key=lambda x: x.rating, reverse=True)

        for gen in generations:
            gen_info = {
                "generation_id": gen.generation_id,
                "rating": gen.rating,
                "created_at": gen.created_at,
                "notes": gen.notes,
                "thumbnail": gen.thumbnail_url,
            }
            comparison["generations"].append(gen_info)

        if sorted_gens:
            comparison["best_generation"] = sorted_gens[0].generation_id
            comparison["average_rating"] = sum(g.rating for g in sorted_gens) / len(sorted_gens)

        return comparison

    def suggest_refinements(self, current_controls: DirectorControls, feedback: str) -> List[Dict[str, Any]]:
        """Suggest parameter refinements based on feedback"""
        suggestions = []

        feedback_lower = feedback.lower()

        # Motion-related suggestions
        if any(word in feedback_lower for word in ["too fast", "fast", "rushed"]):
            suggestions.append(
                {
                    "parameter": "camera.speed",
                    "current_value": current_controls.camera.speed,
                    "suggested_value": max(0.1, current_controls.camera.speed * 0.7),
                    "reason": "Reduce camera speed for smoother motion",
                }
            )

        if any(word in feedback_lower for word in ["too slow", "sluggish", "boring"]):
            suggestions.append(
                {
                    "parameter": "camera.speed",
                    "current_value": current_controls.camera.speed,
                    "suggested_value": min(5.0, current_controls.camera.speed * 1.3),
                    "reason": "Increase camera speed for more dynamic motion",
                }
            )

        # Duration suggestions
        if any(word in feedback_lower for word in ["too short", "quick"]):
            suggestions.append(
                {
                    "parameter": "timing.duration",
                    "current_value": current_controls.timing.duration,
                    "suggested_value": current_controls.timing.duration * 1.5,
                    "reason": "Increase duration for better pacing",
                }
            )

        if any(word in feedback_lower for word in ["too long", "dragging"]):
            suggestions.append(
                {
                    "parameter": "timing.duration",
                    "current_value": current_controls.timing.duration,
                    "suggested_value": max(2.0, current_controls.timing.duration * 0.7),
                    "reason": "Reduce duration for better pacing",
                }
            )

        # Motion strength suggestions
        if any(word in feedback_lower for word in ["chaotic", "unstable", "shaky"]):
            suggestions.append(
                {
                    "parameter": "motion.overall_strength",
                    "current_value": current_controls.motion.overall_strength.value,
                    "suggested_value": MotionStrengthLevel.SUBTLE.value,
                    "reason": "Reduce motion strength for stability",
                }
            )

        if any(word in feedback_lower for word in ["static", "stiff", "lifeless"]):
            suggestions.append(
                {
                    "parameter": "motion.overall_strength",
                    "current_value": current_controls.motion.overall_strength.value,
                    "suggested_value": MotionStrengthLevel.STRONG.value,
                    "reason": "Increase motion strength for more dynamism",
                }
            )

        return suggestions


class AutoModeAssistant:
    """Assistant for auto mode - simplifies control selection"""

    @staticmethod
    def suggest_controls(content_type: str, mood: str, duration: float) -> DirectorControls:
        """Suggest controls based on simple inputs"""

        # Map content types to presets
        content_preset_map = {
            "product": StylePreset.COMMERCIAL,
            "interview": StylePreset.DOCUMENTARY,
            "artistic": StylePreset.ART_HOUSE,
            "sport": StylePreset.ACTION,
            "story": StylePreset.DRAMA,
            "music": StylePreset.MUSIC_VIDEO,
        }

        preset_type = content_preset_map.get(content_type.lower(), None)

        if preset_type:
            controls = PresetLibrary.get_preset(preset_type)
        else:
            controls = DirectorControls(mode=DirectorMode.AUTO)

        # Adjust for mood
        controls.mood = mood
        controls.timing.duration = duration

        # Mood-based adjustments
        if mood.lower() in ["calm", "peaceful", "serene"]:
            controls.camera.speed = 0.5
            controls.motion.overall_strength = MotionStrengthLevel.SUBTLE
        elif mood.lower() in ["exciting", "energetic", "dynamic"]:
            controls.camera.speed = 1.5
            controls.motion.overall_strength = MotionStrengthLevel.STRONG
        elif mood.lower() in ["dramatic", "intense", "powerful"]:
            controls.camera.speed = 1.0
            controls.motion.overall_strength = MotionStrengthLevel.MODERATE

        return controls

    @staticmethod
    def get_quick_options() -> Dict[str, List[str]]:
        """Get simplified option lists for auto mode"""
        return {
            "content_types": ["product", "interview", "artistic", "sport", "story", "music"],
            "moods": ["calm", "exciting", "dramatic", "peaceful", "energetic", "mysterious"],
            "durations": ["short (3s)", "medium (5s)", "long (10s)", "extended (15s)"],
        }


class ControlVocabulary:
    """Professional control vocabulary and definitions"""

    @staticmethod
    def get_camera_motion_types() -> Dict[str, str]:
        """Get all camera motion types with descriptions"""
        return {
            "static": "Fixed camera position with no movement",
            "pan": "Horizontal rotation on a fixed axis",
            "tilt": "Vertical rotation on a fixed axis",
            "dolly": "Camera moves toward or away from subject on tracks",
            "track": "Camera moves alongside subject on tracks",
            "tracking_shot": "Smooth following movement tracking subject motion",
            "crane": "Camera movement on a crane for vertical sweeps",
            "zoom": "Lens focal length change, no camera movement",
            "orbit": "Circular movement around subject",
            "handheld": "Freehand camera with natural shake",
            "steadicam": "Stabilized handheld with smooth motion",
            "push": "Forward movement toward subject",
            "slow_push": "Gradual forward movement for subtle intimacy",
            "pull": "Backward movement away from subject",
            "whip_pan": "Extremely fast horizontal rotation",
            "subtle_tilt": "Gentle vertical movement for reveals",
        }

    @staticmethod
    def get_shot_types() -> Dict[str, str]:
        """Get all shot types with descriptions"""
        return {
            "extreme_wide": "Shows vast landscape or environment",
            "wide": "Shows full scene with context",
            "full": "Shows full subject from head to toe",
            "medium": "Shows subject from waist up",
            "closeup": "Shows subject's face or important detail",
            "extreme_closeup": "Shows tight detail, eyes, or object",
            "over_shoulder": "Shot over one person's shoulder at another",
            "pov": "Point of view from subject's perspective",
            "insert": "Close shot of important object or detail",
            "cutaway": "Shot of related action happening elsewhere",
            "two_shot": "Frames two subjects together",
            "group_shot": "Shows multiple subjects in frame",
        }

    @staticmethod
    def get_transition_types() -> Dict[str, str]:
        """Get all transition types with descriptions"""
        return {
            "cut": "Instant change between shots",
            "fade": "Gradual transition through black",
            "dissolve": "One shot gradually replaces another",
            "wipe": "One shot pushes another off screen",
            "match_cut": "Cut on similar visual element",
            "jump_cut": "Cut within same shot, time jump",
            "smash_cut": "Abrupt cut for dramatic effect",
            "crossfade": "Audio and video fade simultaneously",
            "fade_to_black": "Gradual fade to black",
            "fade_from_black": "Gradual reveal from black",
        }

    @staticmethod
    def get_motion_strength_levels() -> Dict[str, str]:
        """Get motion strength levels with descriptions"""
        return {
            "none": "No motion, completely static",
            "subtle": "Barely perceptible movement",
            "moderate": "Noticeable but controlled motion",
            "strong": "Pronounced, dynamic movement",
            "extreme": "Intense, high-energy motion",
        }

    @staticmethod
    def get_style_presets() -> Dict[str, Dict[str, str]]:
        """Get all style presets with detailed descriptions"""
        return {
            "documentary": {
                "description": "Naturalistic, observational style",
                "camera": "Handheld, subtle motion",
                "visual": "Neutral colors, natural lighting",
                "use_case": "Reality, interviews, behind-the-scenes",
            },
            "commercial": {
                "description": "Polished, professional look",
                "camera": "Smooth dolly, controlled motion",
                "visual": "Vibrant colors, three-point lighting",
                "use_case": "Products, brands, advertising",
            },
            "art_house": {
                "description": "Atmospheric, contemplative style",
                "camera": "Slow tracking, minimal motion",
                "visual": "Desaturated colors, dramatic lighting",
                "use_case": "Artistic, experimental, mood pieces",
            },
            "action": {
                "description": "Dynamic, high-energy style",
                "camera": "Fast handheld, extreme motion",
                "visual": "High contrast, dramatic lighting",
                "use_case": "Action, sports, high-energy",
            },
            "drama": {
                "description": "Intimate, emotional style",
                "camera": "Slow push, subtle motion",
                "visual": "Warm colors, soft lighting",
                "use_case": "Character moments, emotional scenes",
            },
            "music_video": {
                "description": "Stylized, creative style",
                "camera": "Orbit, strong motion",
                "visual": "Saturated colors, theatrical lighting",
                "use_case": "Music videos, performance, creative",
            },
        }


if __name__ == "__main__":
    # Example usage

    # 1. Create controls in Pro mode
    print("=== PRO MODE EXAMPLE ===")
    pro_controls = DirectorControls(mode=DirectorMode.PRO)
    pro_controls.camera.movement_type = CameraMovementType.DOLLY
    pro_controls.camera.shot_type = ShotType.CLOSEUP
    pro_controls.camera.speed = 0.8
    pro_controls.timing.duration = 7.0
    pro_controls.timing.fps = 30

    print(f"Control ID: {pro_controls.control_id}")

    # Validate
    validation = pro_controls.validate()
    print(f"Valid: {validation['valid']}")
    if validation["errors"]:
        print(f"Errors: {validation['errors']}")
    if validation["warnings"]:
        print(f"Warnings: {validation['warnings']}")

    print(f"Internal params: {json.dumps(pro_controls.to_internal_params(), indent=2)}")

    # 2. Use preset
    print("\n=== PRESET EXAMPLE ===")
    commercial = PresetLibrary.get_preset(StylePreset.COMMERCIAL)
    print(f"Commercial preset: {commercial.style_preset}")
    print(f"Camera: {commercial.camera.movement_type.value}, {commercial.camera.shot_type.value}")

    # Validate preset
    validation = commercial.validate()
    print(f"Valid: {validation['valid']}")

    # 3. Lock parameters and iterate
    print("\n=== ITERATION WORKFLOW ===")
    commercial.lock_parameter("camera.movement_type", CameraMovementType.DOLLY.value, "Perfect dolly motion")
    commercial.lock_parameter("timing.fps", 30, "30fps looks best")

    workflow = IterationWorkflow(commercial)
    variation = workflow.create_variation(
        {"camera.speed": 1.2, "motion.overall_strength": MotionStrengthLevel.STRONG.value}
    )

    print(f"Original camera speed: {commercial.camera.speed}")
    print(f"Variation camera speed: {variation.camera.speed}")

    # 4. Auto mode
    print("\n=== AUTO MODE EXAMPLE ===")
    auto_controls = AutoModeAssistant.suggest_controls(content_type="product", mood="exciting", duration=5.0)
    print(f"Auto mode preset: {auto_controls.style_preset}")
    print(f"Suggested camera: {auto_controls.camera.movement_type.value}")

    # 5. Control vocabulary
    print("\n=== CONTROL VOCABULARY ===")
    vocab = ControlVocabulary()
    print("\nCamera Motion Types:")
    for motion_type, description in list(vocab.get_camera_motion_types().items())[:3]:
        print(f"  {motion_type}: {description}")

    print("\nMotion Strength Levels:")
    for level, description in vocab.get_motion_strength_levels().items():
        print(f"  {level}: {description}")

    # 6. List presets
    print("\n=== AVAILABLE PRESETS ===")
    for preset in PresetLibrary.list_presets():
        print(f"{preset['name']}: {preset['description']}")
