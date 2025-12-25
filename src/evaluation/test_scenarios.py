"""
Test Scenarios for Video Generation Evaluation
Comprehensive coverage of movement types and edge cases
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import json
from pathlib import Path


class MovementType(Enum):
    """Movement type classifications"""
    CHARACTER_WALK = "character_walk"
    CHARACTER_RUN = "character_run"
    CHARACTER_GESTURE = "character_gesture"
    CHARACTER_FACIAL = "character_facial"
    CHARACTER_HEAD_TURN = "character_head_turn"
    CHARACTER_BODY_ROTATION = "character_body_rotation"
    
    CAMERA_PAN = "camera_pan"
    CAMERA_TILT = "camera_tilt"
    CAMERA_ZOOM = "camera_zoom"
    CAMERA_DOLLY = "camera_dolly"
    CAMERA_ORBIT = "camera_orbit"
    CAMERA_TRACKING = "camera_tracking"
    
    ENVIRONMENT_WIND = "environment_wind"
    ENVIRONMENT_WATER = "environment_water"
    ENVIRONMENT_PARTICLES = "environment_particles"
    ENVIRONMENT_WEATHER = "environment_weather"
    ENVIRONMENT_VEGETATION = "environment_vegetation"
    
    LIGHTING_DAY_NIGHT = "lighting_day_night"
    LIGHTING_SHADOWS = "lighting_shadows"
    LIGHTING_INTENSITY = "lighting_intensity"
    LIGHTING_COLOR_SHIFT = "lighting_color_shift"
    
    MULTI_SCENE_CONTINUITY = "multi_scene_continuity"
    MULTI_SCENE_TRANSITION = "multi_scene_transition"


class DifficultyLevel(Enum):
    """Test scenario difficulty"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class TestScenario:
    """Individual test scenario definition"""
    scenario_id: str
    name: str
    description: str
    movement_type: MovementType
    difficulty: DifficultyLevel
    
    # Input specifications
    input_image_path: str
    prompt: str
    duration_frames: int
    
    # Expected outputs
    expected_motion_vectors: Optional[Dict[str, Any]] = None
    expected_quality_range: Dict[str, tuple] = field(default_factory=dict)
    
    # Quality thresholds
    min_temporal_consistency: float = 0.85
    min_instruction_following: float = 0.90
    min_clip_similarity: float = 0.80
    min_ssim: float = 0.75
    min_perceptual_quality: float = 0.80
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    reference_videos: List[str] = field(default_factory=list)
    expert_validated: bool = False
    validation_date: Optional[str] = None
    
    # Performance expectations
    max_latency_ms: float = 5000.0
    min_throughput_fps: float = 1.0


@dataclass
class MultiSceneScenario:
    """Multi-scene continuity test scenario"""
    scenario_id: str
    name: str
    description: str
    scenes: List[TestScenario]
    
    # Continuity requirements
    character_consistency_threshold: float = 0.95
    lighting_consistency_threshold: float = 0.85
    style_consistency_threshold: float = 0.90
    
    # Transition requirements
    transition_smoothness: float = 0.88
    temporal_alignment: float = 0.92


class TestScenarioLibrary:
    """Library of test scenarios covering all movement types"""
    
    def __init__(self):
        self.scenarios: Dict[str, TestScenario] = {}
        self.multi_scene_scenarios: Dict[str, MultiSceneScenario] = {}
        self._initialize_scenarios()
    
    def _initialize_scenarios(self):
        """Initialize comprehensive test scenario library"""
        
        # CHARACTER MOVEMENT SCENARIOS (6 types)
        self.scenarios["TS_CHAR_001"] = TestScenario(
            scenario_id="TS_CHAR_001",
            name="Natural Walking - Forward",
            description="Character walks naturally towards camera with realistic gait",
            movement_type=MovementType.CHARACTER_WALK,
            difficulty=DifficultyLevel.BASIC,
            input_image_path="test_assets/characters/standing_person_01.jpg",
            prompt="Person walks naturally forward with steady, confident gait",
            duration_frames=60,
            min_temporal_consistency=0.88,
            min_ssim=0.80,
            tags=["character", "locomotion", "basic"],
            max_latency_ms=4000.0
        )
        
        self.scenarios["TS_CHAR_002"] = TestScenario(
            scenario_id="TS_CHAR_002",
            name="Sprint Running - Lateral",
            description="Character sprints laterally across frame with dynamic motion",
            movement_type=MovementType.CHARACTER_RUN,
            difficulty=DifficultyLevel.INTERMEDIATE,
            input_image_path="test_assets/characters/athletic_person_01.jpg",
            prompt="Athlete sprints left to right with powerful, dynamic running motion",
            duration_frames=48,
            min_temporal_consistency=0.85,
            min_instruction_following=0.88,
            tags=["character", "high-speed", "intermediate"],
            max_latency_ms=4500.0
        )
        
        self.scenarios["TS_CHAR_003"] = TestScenario(
            scenario_id="TS_CHAR_003",
            name="Hand Gesture Communication",
            description="Character makes expressive hand gestures while speaking",
            movement_type=MovementType.CHARACTER_GESTURE,
            difficulty=DifficultyLevel.INTERMEDIATE,
            input_image_path="test_assets/characters/portrait_person_01.jpg",
            prompt="Person gestures expressively with hands while explaining something",
            duration_frames=72,
            min_temporal_consistency=0.87,
            min_perceptual_quality=0.85,
            tags=["character", "gesture", "expressive"],
            max_latency_ms=4200.0
        )
        
        self.scenarios["TS_CHAR_004"] = TestScenario(
            scenario_id="TS_CHAR_004",
            name="Subtle Facial Expression",
            description="Micro-expressions and subtle facial movements",
            movement_type=MovementType.CHARACTER_FACIAL,
            difficulty=DifficultyLevel.ADVANCED,
            input_image_path="test_assets/characters/close_up_face_01.jpg",
            prompt="Subtle smile forming with slight eye movement and eyebrow raise",
            duration_frames=36,
            min_temporal_consistency=0.92,
            min_perceptual_quality=0.88,
            min_clip_similarity=0.85,
            tags=["character", "facial", "subtle", "advanced"],
            max_latency_ms=3800.0
        )
        
        self.scenarios["TS_CHAR_005"] = TestScenario(
            scenario_id="TS_CHAR_005",
            name="Head Turn with Eye Tracking",
            description="Character turns head while eyes track a moving object",
            movement_type=MovementType.CHARACTER_HEAD_TURN,
            difficulty=DifficultyLevel.ADVANCED,
            input_image_path="test_assets/characters/profile_person_01.jpg",
            prompt="Head turns 90 degrees from profile to camera while eyes track movement",
            duration_frames=48,
            min_temporal_consistency=0.90,
            min_instruction_following=0.92,
            tags=["character", "head", "eyes", "complex"],
            max_latency_ms=4100.0
        )
        
        self.scenarios["TS_CHAR_006"] = TestScenario(
            scenario_id="TS_CHAR_006",
            name="Full Body Rotation",
            description="Character performs 360-degree rotation maintaining form",
            movement_type=MovementType.CHARACTER_BODY_ROTATION,
            difficulty=DifficultyLevel.EXPERT,
            input_image_path="test_assets/characters/full_body_01.jpg",
            prompt="Person rotates smoothly 360 degrees showing all sides",
            duration_frames=96,
            min_temporal_consistency=0.88,
            min_ssim=0.78,
            min_perceptual_quality=0.85,
            tags=["character", "rotation", "complex", "expert"],
            max_latency_ms=5000.0
        )
        
        # CAMERA MOVEMENT SCENARIOS (6 types)
        self.scenarios["TS_CAM_001"] = TestScenario(
            scenario_id="TS_CAM_001",
            name="Slow Horizontal Pan",
            description="Smooth horizontal pan revealing landscape details",
            movement_type=MovementType.CAMERA_PAN,
            difficulty=DifficultyLevel.BASIC,
            input_image_path="test_assets/scenes/landscape_vista_01.jpg",
            prompt="Slow, steady pan from left to right revealing scenic vista",
            duration_frames=72,
            min_temporal_consistency=0.90,
            min_ssim=0.82,
            tags=["camera", "pan", "landscape"],
            max_latency_ms=3500.0
        )
        
        self.scenarios["TS_CAM_002"] = TestScenario(
            scenario_id="TS_CAM_002",
            name="Vertical Tilt - Bottom to Top",
            description="Camera tilts upward from ground to sky",
            movement_type=MovementType.CAMERA_TILT,
            difficulty=DifficultyLevel.BASIC,
            input_image_path="test_assets/scenes/building_base_01.jpg",
            prompt="Camera tilts upward from building base to top revealing architecture",
            duration_frames=60,
            min_temporal_consistency=0.89,
            min_instruction_following=0.90,
            tags=["camera", "tilt", "architecture"],
            max_latency_ms=3600.0
        )
        
        self.scenarios["TS_CAM_003"] = TestScenario(
            scenario_id="TS_CAM_003",
            name="Dynamic Zoom In",
            description="Smooth zoom maintaining focus and detail",
            movement_type=MovementType.CAMERA_ZOOM,
            difficulty=DifficultyLevel.INTERMEDIATE,
            input_image_path="test_assets/scenes/subject_wide_01.jpg",
            prompt="Smooth zoom in from wide shot to close-up maintaining sharp focus",
            duration_frames=54,
            min_temporal_consistency=0.87,
            min_perceptual_quality=0.86,
            tags=["camera", "zoom", "focus"],
            max_latency_ms=4000.0
        )
        
        self.scenarios["TS_CAM_004"] = TestScenario(
            scenario_id="TS_CAM_004",
            name="Forward Dolly Push",
            description="Camera moves forward through space maintaining composition",
            movement_type=MovementType.CAMERA_DOLLY,
            difficulty=DifficultyLevel.INTERMEDIATE,
            input_image_path="test_assets/scenes/corridor_entrance_01.jpg",
            prompt="Camera dollies forward through corridor with smooth motion parallax",
            duration_frames=84,
            min_temporal_consistency=0.88,
            min_ssim=0.79,
            tags=["camera", "dolly", "movement"],
            max_latency_ms=4300.0
        )
        
        self.scenarios["TS_CAM_005"] = TestScenario(
            scenario_id="TS_CAM_005",
            name="Circular Orbit Shot",
            description="Camera orbits around subject maintaining constant distance",
            movement_type=MovementType.CAMERA_ORBIT,
            difficulty=DifficultyLevel.ADVANCED,
            input_image_path="test_assets/scenes/central_subject_01.jpg",
            prompt="Camera orbits 180 degrees around subject maintaining framing",
            duration_frames=96,
            min_temporal_consistency=0.86,
            min_instruction_following=0.89,
            min_perceptual_quality=0.85,
            tags=["camera", "orbit", "complex"],
            max_latency_ms=4800.0
        )
        
        self.scenarios["TS_CAM_006"] = TestScenario(
            scenario_id="TS_CAM_006",
            name="Dynamic Subject Tracking",
            description="Camera follows moving subject maintaining composition",
            movement_type=MovementType.CAMERA_TRACKING,
            difficulty=DifficultyLevel.ADVANCED,
            input_image_path="test_assets/scenes/moving_subject_01.jpg",
            prompt="Camera tracks running subject keeping them centered in frame",
            duration_frames=90,
            min_temporal_consistency=0.87,
            min_clip_similarity=0.83,
            tags=["camera", "tracking", "dynamic"],
            max_latency_ms=4600.0
        )
        
        # ENVIRONMENT MOVEMENT SCENARIOS (5 types)
        self.scenarios["TS_ENV_001"] = TestScenario(
            scenario_id="TS_ENV_001",
            name="Wind Through Trees",
            description="Natural wind movement affecting foliage realistically",
            movement_type=MovementType.ENVIRONMENT_WIND,
            difficulty=DifficultyLevel.INTERMEDIATE,
            input_image_path="test_assets/environments/forest_scene_01.jpg",
            prompt="Gentle wind rustles through tree leaves with natural swaying motion",
            duration_frames=72,
            min_temporal_consistency=0.85,
            min_perceptual_quality=0.82,
            tags=["environment", "wind", "nature"],
            max_latency_ms=4200.0
        )
        
        self.scenarios["TS_ENV_002"] = TestScenario(
            scenario_id="TS_ENV_002",
            name="Flowing Water Surface",
            description="Water surface with realistic wave and reflection dynamics",
            movement_type=MovementType.ENVIRONMENT_WATER,
            difficulty=DifficultyLevel.ADVANCED,
            input_image_path="test_assets/environments/water_scene_01.jpg",
            prompt="Water surface with gentle waves and realistic reflections moving",
            duration_frames=84,
            min_temporal_consistency=0.84,
            min_ssim=0.76,
            min_perceptual_quality=0.84,
            tags=["environment", "water", "reflections"],
            max_latency_ms=4700.0
        )
        
        self.scenarios["TS_ENV_003"] = TestScenario(
            scenario_id="TS_ENV_003",
            name="Particle Simulation - Dust",
            description="Dust particles floating with realistic physics",
            movement_type=MovementType.ENVIRONMENT_PARTICLES,
            difficulty=DifficultyLevel.ADVANCED,
            input_image_path="test_assets/environments/dusty_room_01.jpg",
            prompt="Dust particles float and drift through air with natural motion",
            duration_frames=60,
            min_temporal_consistency=0.83,
            min_perceptual_quality=0.83,
            tags=["environment", "particles", "physics"],
            max_latency_ms=4400.0
        )
        
        self.scenarios["TS_ENV_004"] = TestScenario(
            scenario_id="TS_ENV_004",
            name="Weather Transition - Rain",
            description="Rain beginning and intensifying naturally",
            movement_type=MovementType.ENVIRONMENT_WEATHER,
            difficulty=DifficultyLevel.EXPERT,
            input_image_path="test_assets/environments/cloudy_scene_01.jpg",
            prompt="Rain begins falling, starting light and gradually intensifying",
            duration_frames=96,
            min_temporal_consistency=0.82,
            min_instruction_following=0.88,
            min_perceptual_quality=0.84,
            tags=["environment", "weather", "transition", "expert"],
            max_latency_ms=5000.0
        )
        
        self.scenarios["TS_ENV_005"] = TestScenario(
            scenario_id="TS_ENV_005",
            name="Vegetation Growth",
            description="Plants swaying and responding to environment",
            movement_type=MovementType.ENVIRONMENT_VEGETATION,
            difficulty=DifficultyLevel.INTERMEDIATE,
            input_image_path="test_assets/environments/garden_scene_01.jpg",
            prompt="Plants and flowers sway gently in breeze with natural movement",
            duration_frames=78,
            min_temporal_consistency=0.85,
            min_ssim=0.78,
            tags=["environment", "vegetation", "organic"],
            max_latency_ms=4300.0
        )
        
        # LIGHTING CHANGE SCENARIOS (4 types)
        self.scenarios["TS_LIGHT_001"] = TestScenario(
            scenario_id="TS_LIGHT_001",
            name="Day to Night Transition",
            description="Natural lighting transition from day to night",
            movement_type=MovementType.LIGHTING_DAY_NIGHT,
            difficulty=DifficultyLevel.ADVANCED,
            input_image_path="test_assets/lighting/daytime_scene_01.jpg",
            prompt="Scene transitions from bright day to dusk with natural color grading",
            duration_frames=120,
            min_temporal_consistency=0.86,
            min_instruction_following=0.90,
            min_perceptual_quality=0.87,
            tags=["lighting", "transition", "time-of-day"],
            max_latency_ms=4900.0
        )
        
        self.scenarios["TS_LIGHT_002"] = TestScenario(
            scenario_id="TS_LIGHT_002",
            name="Shadow Movement",
            description="Shadows moving realistically across scene",
            movement_type=MovementType.LIGHTING_SHADOWS,
            difficulty=DifficultyLevel.INTERMEDIATE,
            input_image_path="test_assets/lighting/sunlit_scene_01.jpg",
            prompt="Shadows sweep across scene as if sun is moving through sky",
            duration_frames=84,
            min_temporal_consistency=0.87,
            min_clip_similarity=0.82,
            tags=["lighting", "shadows", "sun-position"],
            max_latency_ms=4400.0
        )
        
        self.scenarios["TS_LIGHT_003"] = TestScenario(
            scenario_id="TS_LIGHT_003",
            name="Light Intensity Change",
            description="Dynamic light intensity adjustment maintaining quality",
            movement_type=MovementType.LIGHTING_INTENSITY,
            difficulty=DifficultyLevel.INTERMEDIATE,
            input_image_path="test_assets/lighting/moderate_lit_01.jpg",
            prompt="Scene lighting gradually brightens revealing more details",
            duration_frames=60,
            min_temporal_consistency=0.88,
            min_perceptual_quality=0.85,
            tags=["lighting", "exposure", "intensity"],
            max_latency_ms=4100.0
        )
        
        self.scenarios["TS_LIGHT_004"] = TestScenario(
            scenario_id="TS_LIGHT_004",
            name="Color Temperature Shift",
            description="Lighting color temperature changes naturally",
            movement_type=MovementType.LIGHTING_COLOR_SHIFT,
            difficulty=DifficultyLevel.ADVANCED,
            input_image_path="test_assets/lighting/neutral_scene_01.jpg",
            prompt="Lighting shifts from warm sunset tones to cool blue evening",
            duration_frames=72,
            min_temporal_consistency=0.85,
            min_instruction_following=0.89,
            min_clip_similarity=0.81,
            tags=["lighting", "color", "temperature"],
            max_latency_ms=4500.0
        )
        
        # MULTI-SCENE CONTINUITY SCENARIOS (2 complex scenarios)
        self._initialize_multi_scene_scenarios()
    
    def _initialize_multi_scene_scenarios(self):
        """Initialize multi-scene continuity test scenarios"""
        
        # Multi-scene scenario 1: Character consistency across scenes
        scene1 = TestScenario(
            scenario_id="TS_MULTI_001_S1",
            name="Multi-Scene: Character Indoor",
            description="Character in indoor setting - scene 1",
            movement_type=MovementType.MULTI_SCENE_CONTINUITY,
            difficulty=DifficultyLevel.EXPERT,
            input_image_path="test_assets/multi_scene/indoor_character_01.jpg",
            prompt="Character walks through indoor hallway with consistent appearance",
            duration_frames=60,
            min_temporal_consistency=0.90,
            tags=["multi-scene", "character", "indoor"]
        )
        
        scene2 = TestScenario(
            scenario_id="TS_MULTI_001_S2",
            name="Multi-Scene: Character Transition",
            description="Character transitioning between spaces - scene 2",
            movement_type=MovementType.MULTI_SCENE_TRANSITION,
            difficulty=DifficultyLevel.EXPERT,
            input_image_path="test_assets/multi_scene/doorway_character_01.jpg",
            prompt="Same character exits doorway maintaining identity and appearance",
            duration_frames=48,
            min_temporal_consistency=0.90,
            tags=["multi-scene", "transition"]
        )
        
        scene3 = TestScenario(
            scenario_id="TS_MULTI_001_S3",
            name="Multi-Scene: Character Outdoor",
            description="Character in outdoor setting - scene 3",
            movement_type=MovementType.MULTI_SCENE_CONTINUITY,
            difficulty=DifficultyLevel.EXPERT,
            input_image_path="test_assets/multi_scene/outdoor_character_01.jpg",
            prompt="Same character continues walking in outdoor environment",
            duration_frames=60,
            min_temporal_consistency=0.90,
            tags=["multi-scene", "character", "outdoor"]
        )
        
        self.multi_scene_scenarios["TS_MULTI_001"] = MultiSceneScenario(
            scenario_id="TS_MULTI_001",
            name="Character Continuity - Indoor to Outdoor",
            description="Character maintains identity across three connected scenes",
            scenes=[scene1, scene2, scene3],
            character_consistency_threshold=0.95,
            lighting_consistency_threshold=0.82,
            style_consistency_threshold=0.92,
            transition_smoothness=0.88
        )
        
        # Multi-scene scenario 2: Lighting continuity
        light_scene1 = TestScenario(
            scenario_id="TS_MULTI_002_S1",
            name="Multi-Scene: Morning Light",
            description="Scene with morning lighting - scene 1",
            movement_type=MovementType.MULTI_SCENE_CONTINUITY,
            difficulty=DifficultyLevel.EXPERT,
            input_image_path="test_assets/multi_scene/morning_landscape_01.jpg",
            prompt="Landscape with warm morning sunlight and long shadows",
            duration_frames=72,
            min_temporal_consistency=0.88,
            tags=["multi-scene", "lighting", "morning"]
        )
        
        light_scene2 = TestScenario(
            scenario_id="TS_MULTI_002_S2",
            name="Multi-Scene: Midday Light",
            description="Same location at midday - scene 2",
            movement_type=MovementType.MULTI_SCENE_CONTINUITY,
            difficulty=DifficultyLevel.EXPERT,
            input_image_path="test_assets/multi_scene/midday_landscape_01.jpg",
            prompt="Same landscape with bright midday light and minimal shadows",
            duration_frames=72,
            min_temporal_consistency=0.88,
            tags=["multi-scene", "lighting", "midday"]
        )
        
        self.multi_scene_scenarios["TS_MULTI_002"] = MultiSceneScenario(
            scenario_id="TS_MULTI_002",
            name="Lighting Continuity - Time Progression",
            description="Location maintains spatial consistency across lighting changes",
            scenes=[light_scene1, light_scene2],
            character_consistency_threshold=0.85,
            lighting_consistency_threshold=0.88,
            style_consistency_threshold=0.93,
            transition_smoothness=0.85
        )
    
    def get_scenario(self, scenario_id: str) -> Optional[TestScenario]:
        """Get single scenario by ID"""
        return self.scenarios.get(scenario_id)
    
    def get_multi_scene_scenario(self, scenario_id: str) -> Optional[MultiSceneScenario]:
        """Get multi-scene scenario by ID"""
        return self.multi_scene_scenarios.get(scenario_id)
    
    def get_scenarios_by_type(self, movement_type: MovementType) -> List[TestScenario]:
        """Get all scenarios of a specific movement type"""
        return [s for s in self.scenarios.values() if s.movement_type == movement_type]
    
    def get_scenarios_by_difficulty(self, difficulty: DifficultyLevel) -> List[TestScenario]:
        """Get all scenarios of a specific difficulty"""
        return [s for s in self.scenarios.values() if s.difficulty == difficulty]
    
    def export_library(self, output_path: str):
        """Export scenario library to JSON"""
        data = {
            "version": "1.0.0",
            "total_scenarios": len(self.scenarios),
            "total_multi_scene": len(self.multi_scene_scenarios),
            "scenarios": {
                sid: {
                    "scenario_id": s.scenario_id,
                    "name": s.name,
                    "description": s.description,
                    "movement_type": s.movement_type.value,
                    "difficulty": s.difficulty.value,
                    "input_image_path": s.input_image_path,
                    "prompt": s.prompt,
                    "duration_frames": s.duration_frames,
                    "thresholds": {
                        "temporal_consistency": s.min_temporal_consistency,
                        "instruction_following": s.min_instruction_following,
                        "clip_similarity": s.min_clip_similarity,
                        "ssim": s.min_ssim,
                        "perceptual_quality": s.min_perceptual_quality
                    },
                    "performance": {
                        "max_latency_ms": s.max_latency_ms,
                        "min_throughput_fps": s.min_throughput_fps
                    },
                    "tags": s.tags,
                    "expert_validated": s.expert_validated
                }
                for sid, s in self.scenarios.items()
            }
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_coverage_summary(self) -> Dict:
        """Get summary of test coverage"""
        return {
            "total_scenarios": len(self.scenarios),
            "multi_scene_scenarios": len(self.multi_scene_scenarios),
            "by_movement_type": {
                mt.value: len(self.get_scenarios_by_type(mt))
                for mt in MovementType
            },
            "by_difficulty": {
                dl.value: len(self.get_scenarios_by_difficulty(dl))
                for dl in DifficultyLevel
            },
            "expert_validated": sum(1 for s in self.scenarios.values() if s.expert_validated)
        }
