"""
Temporal Control Layer - Wedge Feature #5

Precision control enables professional use cases with frame-accurate editing.
"""

import json
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class EasingFunction(Enum):
    """Easing functions for motion curves"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    CUBIC_BEZIER = "cubic_bezier"


@dataclass
class Keyframe:
    """Individual keyframe specification"""
    time: float
    value: Dict[str, float]
    easing: EasingFunction = EasingFunction.LINEAR
    bezier_points: Optional[Tuple[float, float, float, float]] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class MotionCurve:
    """Motion curve with keyframes"""
    name: str
    keyframes: List[Keyframe]
    interpolation: str = "cubic"
    fps: int = 24


class KeyframeEditor:
    """
    Keyframe editor for precise temporal control
    Sub-frame accuracy for professional workflows
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.curves: Dict[str, MotionCurve] = {}
    
    def add_keyframe(
        self,
        curve_name: str,
        time: float,
        value: Dict[str, float],
        easing: EasingFunction = EasingFunction.LINEAR
    ) -> bool:
        """Add keyframe to motion curve"""
        if curve_name not in self.curves:
            self.curves[curve_name] = MotionCurve(
                name=curve_name,
                keyframes=[]
            )
        
        keyframe = Keyframe(time=time, value=value, easing=easing)
        self.curves[curve_name].keyframes.append(keyframe)
        self.curves[curve_name].keyframes.sort(key=lambda k: k.time)
        
        return True
    
    def interpolate_value(
        self,
        curve_name: str,
        time: float,
        parameter: str
    ) -> Optional[float]:
        """Interpolate value at specific time"""
        if curve_name not in self.curves:
            return None
        
        curve = self.curves[curve_name]
        keyframes = curve.keyframes
        
        if not keyframes:
            return None
        
        if time <= keyframes[0].time:
            return keyframes[0].value.get(parameter)
        
        if time >= keyframes[-1].time:
            return keyframes[-1].value.get(parameter)
        
        for i in range(len(keyframes) - 1):
            kf1 = keyframes[i]
            kf2 = keyframes[i + 1]
            
            if kf1.time <= time <= kf2.time:
                t = (time - kf1.time) / (kf2.time - kf1.time)
                
                v1 = kf1.value.get(parameter, 0.0)
                v2 = kf2.value.get(parameter, 0.0)
                
                t_eased = self._apply_easing(t, kf1.easing)
                
                return v1 + (v2 - v1) * t_eased
        
        return None
    
    def _apply_easing(self, t: float, easing: EasingFunction) -> float:
        """Apply easing function to time value"""
        if easing == EasingFunction.LINEAR:
            return t
        elif easing == EasingFunction.EASE_IN:
            return t * t
        elif easing == EasingFunction.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif easing == EasingFunction.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        return t


class TemporalControlLayer:
    """
    Temporal Control Layer - Strategic Wedge Feature
    
    Measurement Metrics:
    - Keyframe accuracy: ±16ms (sub-frame at 60fps)
    - Motion smoothness: >90% user satisfaction
    - Professional adoption: 30%+ of pro users
    """
    
    def __init__(self, fps: int = 24):
        self.logger = logging.getLogger(__name__)
        self.fps = fps
        self.frame_duration = 1.0 / fps
        self.keyframe_editor = KeyframeEditor()
        self.timeline: List[Dict] = []
    
    def add_motion_keyframe(
        self,
        time: float,
        camera_position: Optional[Tuple[float, float, float]] = None,
        camera_rotation: Optional[Tuple[float, float, float]] = None,
        zoom: Optional[float] = None
    ) -> bool:
        """Add motion keyframe with camera parameters"""
        values = {}
        
        if camera_position:
            values.update({
                'pos_x': camera_position[0],
                'pos_y': camera_position[1],
                'pos_z': camera_position[2]
            })
        
        if camera_rotation:
            values.update({
                'rot_x': camera_rotation[0],
                'rot_y': camera_rotation[1],
                'rot_z': camera_rotation[2]
            })
        
        if zoom is not None:
            values['zoom'] = zoom
        
        return self.keyframe_editor.add_keyframe(
            'camera_motion',
            time,
            values
        )
    
    def generate_frame_sequence(
        self,
        duration: float,
        fps: Optional[int] = None
    ) -> List[Dict]:
        """Generate interpolated frame sequence"""
        fps = fps or self.fps
        num_frames = int(duration * fps)
        
        frames = []
        for frame_num in range(num_frames):
            time = frame_num / fps
            
            frame_data = {
                'frame': frame_num,
                'time': time,
                'camera': {}
            }
            
            for param in ['pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z', 'zoom']:
                value = self.keyframe_editor.interpolate_value('camera_motion', time, param)
                if value is not None:
                    frame_data['camera'][param] = value
            
            frames.append(frame_data)
        
        return frames
    
    def apply_speed_ramp(
        self,
        start_time: float,
        end_time: float,
        start_speed: float = 1.0,
        end_speed: float = 1.0
    ) -> bool:
        """Apply speed ramping effect"""
        self.keyframe_editor.add_keyframe(
            'playback_speed',
            start_time,
            {'speed': start_speed},
            EasingFunction.EASE_IN_OUT
        )
        
        self.keyframe_editor.add_keyframe(
            'playback_speed',
            end_time,
            {'speed': end_speed},
            EasingFunction.EASE_IN_OUT
        )
        
        return True
    
    def export_to_nle(self, output_path: str, format: str = 'edl') -> bool:
        """Export timeline to NLE format (EDL, XML, etc.)"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'edl':
                self._export_edl(output_path)
            elif format == 'xml':
                self._export_xml(output_path)
            else:
                self._export_json(output_path)
            
            return True
        except Exception as e:
            self.logger.error(f"Error exporting to NLE: {e}")
            return False
    
    def _export_edl(self, output_path: str):
        """Export as EDL (Edit Decision List)"""
        with open(output_path, 'w') as f:
            f.write("TITLE: ANIMAtiZE Export\n")
            f.write("FCM: NON-DROP FRAME\n\n")
            
            for i, item in enumerate(self.timeline, 1):
                f.write(f"{i:03d}  001      V     C        "
                       f"{item.get('in', '00:00:00:00')} "
                       f"{item.get('out', '00:00:00:00')} "
                       f"{item.get('rec_in', '00:00:00:00')} "
                       f"{item.get('rec_out', '00:00:00:00')}\n")
    
    def _export_xml(self, output_path: str):
        """Export as XML"""
        import xml.etree.ElementTree as ET
        
        root = ET.Element('xmeml', version='5')
        sequence = ET.SubElement(root, 'sequence')
        ET.SubElement(sequence, 'name').text = 'ANIMAtiZE_Export'
        ET.SubElement(sequence, 'duration').text = str(len(self.timeline) * self.frame_duration)
        
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    def _export_json(self, output_path: str):
        """Export as JSON"""
        data = {
            'fps': self.fps,
            'timeline': self.timeline,
            'curves': {
                name: {
                    'keyframes': [
                        {
                            'time': kf.time,
                            'value': kf.value,
                            'easing': kf.easing.value
                        }
                        for kf in curve.keyframes
                    ]
                }
                for name, curve in self.keyframe_editor.curves.items()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
