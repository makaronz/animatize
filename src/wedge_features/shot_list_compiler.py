"""
Shot List Compiler - Wedge Feature #2

End-to-end production workflow integration creates switching costs.
Replaces 3-5 separate tools for shot planning and production management.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re


class ShotType(Enum):
    """Standard shot types"""
    ESTABLISHING = "establishing"
    WIDE = "wide"
    FULL = "full"
    MEDIUM = "medium"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    OVER_SHOULDER = "over_shoulder"
    POV = "pov"
    INSERT = "insert"
    TWO_SHOT = "two_shot"


class CameraMovement(Enum):
    """Camera movement types"""
    STATIC = "static"
    PAN = "pan"
    TILT = "tilt"
    DOLLY = "dolly"
    TRACK = "track"
    CRANE = "crane"
    HANDHELD = "handheld"
    STEADICAM = "steadicam"


@dataclass
class Shot:
    """Individual shot specification"""
    shot_number: str
    scene_number: str
    shot_type: ShotType
    description: str
    camera_movement: CameraMovement
    duration_estimate: float
    angle: str
    lens: Optional[str] = None
    location: Optional[str] = None
    cast: List[str] = field(default_factory=list)
    props: List[str] = field(default_factory=list)
    lighting_notes: Optional[str] = None
    audio_notes: Optional[str] = None
    vfx_notes: Optional[str] = None
    priority: int = 1
    coverage_type: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class Scene:
    """Scene containing multiple shots"""
    scene_number: str
    description: str
    location: str
    time_of_day: str
    shots: List[Shot] = field(default_factory=list)
    estimated_duration: float = 0.0
    required_cast: List[str] = field(default_factory=list)
    required_props: List[str] = field(default_factory=list)
    required_equipment: List[str] = field(default_factory=list)
    complexity_score: float = 0.0


@dataclass
class CoverageRequirement:
    """Coverage requirements for a scene"""
    master_shot: bool = True
    close_ups: int = 0
    inserts: int = 0
    reaction_shots: int = 0
    establishing_shot: bool = False
    safety_coverage: bool = True


class ShotListCompiler:
    """
    Shot List Compiler - Strategic Wedge Feature
    
    Creates defensible moat through:
    - End-to-end workflow integration (pre-production to post)
    - Intelligent shot breakdown from scripts
    - Automatic coverage suggestions
    - Resource optimization
    - Production scheduling integration
    
    Measurement Metrics:
    - Shot list completeness: 100% coverage validation
    - Time savings: 70%+ reduction vs manual
    - Accuracy: <5% missing shots in production
    - Adoption: 80%+ of projects use compiler
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "configs/shot_list_compiler.json"
        self.scenes: List[Scene] = []
        self.shot_counter = 0
        self.coverage_templates: Dict[str, CoverageRequirement] = {}
        
        self._load_config()
        self._initialize_coverage_templates()
    
    def _load_config(self):
        """Load compiler configuration"""
        config_path = Path(self.config_path)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                self.config = {}
        else:
            self.config = {}
    
    def _initialize_coverage_templates(self):
        """Initialize standard coverage templates"""
        self.coverage_templates = {
            'dialogue': CoverageRequirement(
                master_shot=True,
                close_ups=2,
                inserts=0,
                reaction_shots=2,
                establishing_shot=False,
                safety_coverage=True
            ),
            'action': CoverageRequirement(
                master_shot=True,
                close_ups=1,
                inserts=3,
                reaction_shots=1,
                establishing_shot=True,
                safety_coverage=True
            ),
            'establishing': CoverageRequirement(
                master_shot=False,
                close_ups=0,
                inserts=0,
                reaction_shots=0,
                establishing_shot=True,
                safety_coverage=False
            ),
            'montage': CoverageRequirement(
                master_shot=False,
                close_ups=0,
                inserts=5,
                reaction_shots=0,
                establishing_shot=False,
                safety_coverage=False
            )
        }
    
    def parse_script(self, script_text: str) -> List[Scene]:
        """
        Parse screenplay and extract scenes
        
        Args:
            script_text: Screenplay text
            
        Returns:
            List of parsed scenes
        """
        scenes = []
        
        scene_headers = re.findall(
            r'(INT\.|EXT\.)\s+([A-Z\s]+)\s+-\s+(DAY|NIGHT|MORNING|EVENING)',
            script_text,
            re.MULTILINE
        )
        
        for i, (int_ext, location, time) in enumerate(scene_headers):
            scene_number = f"SCENE_{i+1:03d}"
            
            scene = Scene(
                scene_number=scene_number,
                description=f"{int_ext} {location} - {time}",
                location=location.strip(),
                time_of_day=time,
                shots=[]
            )
            
            scenes.append(scene)
        
        self.scenes = scenes
        return scenes
    
    def generate_coverage(
        self,
        scene: Scene,
        scene_type: str = 'dialogue',
        custom_requirements: Optional[CoverageRequirement] = None
    ) -> List[Shot]:
        """
        Generate shot coverage for a scene
        
        Args:
            scene: Scene to generate coverage for
            scene_type: Type of scene (dialogue, action, etc.)
            custom_requirements: Custom coverage requirements
            
        Returns:
            List of generated shots
        """
        requirements = custom_requirements or self.coverage_templates.get(
            scene_type,
            self.coverage_templates['dialogue']
        )
        
        shots = []
        
        if requirements.establishing_shot:
            shots.append(self._create_shot(
                scene=scene,
                shot_type=ShotType.ESTABLISHING,
                description=f"Establishing shot of {scene.location}",
                camera_movement=CameraMovement.STATIC,
                duration_estimate=5.0
            ))
        
        if requirements.master_shot:
            shots.append(self._create_shot(
                scene=scene,
                shot_type=ShotType.WIDE,
                description=f"Master shot - {scene.description}",
                camera_movement=CameraMovement.STATIC,
                duration_estimate=scene.estimated_duration or 30.0
            ))
        
        for i in range(requirements.close_ups):
            shots.append(self._create_shot(
                scene=scene,
                shot_type=ShotType.CLOSE_UP,
                description=f"Close-up {i+1}",
                camera_movement=CameraMovement.STATIC,
                duration_estimate=10.0
            ))
        
        for i in range(requirements.inserts):
            shots.append(self._create_shot(
                scene=scene,
                shot_type=ShotType.INSERT,
                description=f"Insert {i+1}",
                camera_movement=CameraMovement.STATIC,
                duration_estimate=3.0
            ))
        
        for i in range(requirements.reaction_shots):
            shots.append(self._create_shot(
                scene=scene,
                shot_type=ShotType.MEDIUM,
                description=f"Reaction shot {i+1}",
                camera_movement=CameraMovement.STATIC,
                duration_estimate=5.0
            ))
        
        scene.shots.extend(shots)
        return shots
    
    def _create_shot(
        self,
        scene: Scene,
        shot_type: ShotType,
        description: str,
        camera_movement: CameraMovement,
        duration_estimate: float
    ) -> Shot:
        """Create a shot specification"""
        self.shot_counter += 1
        
        return Shot(
            shot_number=f"{scene.scene_number}_{self.shot_counter:03d}",
            scene_number=scene.scene_number,
            shot_type=shot_type,
            description=description,
            camera_movement=camera_movement,
            duration_estimate=duration_estimate,
            angle="eye level",
            location=scene.location
        )
    
    def suggest_additional_coverage(self, scene: Scene) -> List[Shot]:
        """Suggest additional coverage based on scene analysis"""
        suggestions = []
        
        if len(scene.shots) < 3:
            suggestions.append(self._create_shot(
                scene=scene,
                shot_type=ShotType.MEDIUM,
                description="Safety coverage - medium shot",
                camera_movement=CameraMovement.STATIC,
                duration_estimate=15.0
            ))
        
        has_establishing = any(s.shot_type == ShotType.ESTABLISHING for s in scene.shots)
        if not has_establishing and scene.scene_number.endswith("001"):
            suggestions.append(self._create_shot(
                scene=scene,
                shot_type=ShotType.ESTABLISHING,
                description=f"Establishing shot for new location",
                camera_movement=CameraMovement.CRANE,
                duration_estimate=8.0
            ))
        
        return suggestions
    
    def estimate_resources(self, scene: Scene) -> Dict:
        """Estimate required resources for a scene"""
        equipment = set()
        cast = set()
        props = set()
        
        for shot in scene.shots:
            if shot.camera_movement in [CameraMovement.DOLLY, CameraMovement.TRACK]:
                equipment.add("dolly_track")
            elif shot.camera_movement == CameraMovement.CRANE:
                equipment.add("crane")
            elif shot.camera_movement == CameraMovement.STEADICAM:
                equipment.add("steadicam")
            
            cast.update(shot.cast)
            props.update(shot.props)
            
            if shot.shot_type in [ShotType.CLOSE_UP, ShotType.EXTREME_CLOSE_UP]:
                equipment.add("macro_lens")
        
        return {
            'equipment': list(equipment),
            'cast': list(cast),
            'props': list(props),
            'estimated_setup_time': len(equipment) * 15,
            'estimated_shoot_time': sum(s.duration_estimate for s in scene.shots)
        }
    
    def optimize_shooting_order(self, scenes: List[Scene]) -> List[Scene]:
        """Optimize shooting order based on locations and resources"""
        location_groups = {}
        
        for scene in scenes:
            if scene.location not in location_groups:
                location_groups[scene.location] = []
            location_groups[scene.location].append(scene)
        
        optimized = []
        for location, location_scenes in sorted(location_groups.items()):
            location_scenes.sort(key=lambda s: s.time_of_day)
            optimized.extend(location_scenes)
        
        return optimized
    
    def export_shot_list(self, output_path: str, format: str = 'json') -> bool:
        """Export shot list in various formats"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                data = {
                    'scenes': [
                        {
                            'scene_number': scene.scene_number,
                            'description': scene.description,
                            'location': scene.location,
                            'time_of_day': scene.time_of_day,
                            'shots': [
                                {
                                    'shot_number': shot.shot_number,
                                    'shot_type': shot.shot_type.value,
                                    'description': shot.description,
                                    'camera_movement': shot.camera_movement.value,
                                    'duration_estimate': shot.duration_estimate,
                                    'angle': shot.angle,
                                    'lens': shot.lens,
                                    'cast': shot.cast,
                                    'props': shot.props
                                }
                                for shot in scene.shots
                            ]
                        }
                        for scene in self.scenes
                    ]
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif format == 'csv':
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'Scene', 'Shot', 'Type', 'Description', 'Movement',
                        'Duration', 'Location', 'Angle'
                    ])
                    
                    for scene in self.scenes:
                        for shot in scene.shots:
                            writer.writerow([
                                shot.scene_number,
                                shot.shot_number,
                                shot.shot_type.value,
                                shot.description,
                                shot.camera_movement.value,
                                shot.duration_estimate,
                                shot.location,
                                shot.angle
                            ])
            
            return True
        except Exception as e:
            self.logger.error(f"Error exporting shot list: {e}")
            return False
    
    def calculate_completeness_score(self) -> float:
        """Calculate shot list completeness score"""
        if not self.scenes:
            return 0.0
        
        total_score = 0.0
        
        for scene in self.scenes:
            scene_score = 0.0
            
            if len(scene.shots) > 0:
                scene_score += 0.3
            
            has_master = any(s.shot_type == ShotType.WIDE for s in scene.shots)
            if has_master:
                scene_score += 0.2
            
            has_closeup = any(s.shot_type == ShotType.CLOSE_UP for s in scene.shots)
            if has_closeup:
                scene_score += 0.2
            
            if scene.estimated_duration > 0:
                scene_score += 0.15
            
            if scene.location:
                scene_score += 0.15
            
            total_score += scene_score
        
        return (total_score / len(self.scenes)) * 100
