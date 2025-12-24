"""
Consistency Engine with Reference Management - Wedge Feature #3

Solves critical pain point of cross-shot consistency that competitors struggle with.
Maintains character identity, lighting, spatial relationships across scenes.
"""

import json
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import hashlib


class ConsistencyType(Enum):
    """Types of consistency to maintain"""
    CHARACTER_IDENTITY = "character_identity"
    LIGHTING = "lighting"
    COLOR_GRADING = "color_grading"
    SPATIAL_RELATIONSHIP = "spatial_relationship"
    OBJECT_APPEARANCE = "object_appearance"
    ENVIRONMENTAL = "environmental"
    TEMPORAL = "temporal"


@dataclass
class ReferenceFrame:
    """Reference frame for consistency checking"""
    frame_id: str
    shot_id: str
    timestamp: float
    embeddings: Dict[str, np.ndarray] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    color_histogram: Optional[np.ndarray] = None
    lighting_profile: Optional[Dict] = None
    character_positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    object_registry: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsistencyViolation:
    """Detected consistency violation"""
    violation_type: ConsistencyType
    severity: float
    description: str
    frame_a: str
    frame_b: str
    suggested_fix: str
    confidence: float


class ReferenceManager:
    """
    Manages reference frames for consistency checking
    
    Stores and retrieves reference images/embeddings for:
    - Character appearances
    - Lighting setups
    - Spatial layouts
    - Object continuity
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.storage_path = storage_path or "data/reference_library"
        self.references: Dict[str, ReferenceFrame] = {}
        self.character_library: Dict[str, List[str]] = {}
        self.object_library: Dict[str, List[str]] = {}
        
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
    
    def add_reference(
        self,
        frame: ReferenceFrame,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Add a new reference frame"""
        try:
            self.references[frame.frame_id] = frame
            
            if tags:
                for tag in tags:
                    if tag.startswith('character:'):
                        char_name = tag.split(':')[1]
                        if char_name not in self.character_library:
                            self.character_library[char_name] = []
                        self.character_library[char_name].append(frame.frame_id)
                    
                    elif tag.startswith('object:'):
                        obj_name = tag.split(':')[1]
                        if obj_name not in self.object_library:
                            self.object_library[obj_name] = []
                        self.object_library[obj_name].append(frame.frame_id)
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding reference: {e}")
            return False
    
    def get_reference(self, frame_id: str) -> Optional[ReferenceFrame]:
        """Retrieve a reference frame"""
        return self.references.get(frame_id)
    
    def get_character_references(self, character_name: str) -> List[ReferenceFrame]:
        """Get all references for a character"""
        frame_ids = self.character_library.get(character_name, [])
        return [self.references[fid] for fid in frame_ids if fid in self.references]
    
    def get_similar_references(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Find similar references using embedding similarity"""
        similarities = []
        
        for frame_id, frame in self.references.items():
            if 'visual' not in frame.embeddings:
                continue
            
            similarity = self._cosine_similarity(
                query_embedding,
                frame.embeddings['visual']
            )
            similarities.append((frame_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class ConsistencyEngine:
    """
    Consistency Engine - Strategic Wedge Feature
    
    Creates defensible moat through:
    - Multi-model ensemble for identity preservation
    - Proprietary consistency corpus
    - Real-time validation with immediate feedback
    - Learning system that improves from corrections
    
    Measurement Metrics:
    - Cross-shot consistency: >85% match
    - Character identity: >95% F1 score
    - Lighting coherence: <10% ΔRGB variance
    - Spatial accuracy: <5% position deviation
    """
    
    def __init__(
        self,
        reference_manager: Optional[ReferenceManager] = None,
        config_path: Optional[str] = None
    ):
        self.logger = logging.getLogger(__name__)
        self.reference_manager = reference_manager or ReferenceManager()
        self.config_path = config_path or "configs/consistency_engine.json"
        self.consistency_history: List[ConsistencyViolation] = []
        self.thresholds = {
            'character_identity': 0.95,
            'lighting': 0.85,
            'color_grading': 0.90,
            'spatial_relationship': 0.88,
            'object_appearance': 0.92
        }
        
        self._load_config()
    
    def _load_config(self):
        """Load configuration"""
        config_path = Path(self.config_path)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.thresholds.update(config.get('thresholds', {}))
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
    
    def check_character_consistency(
        self,
        frame_a: ReferenceFrame,
        frame_b: ReferenceFrame,
        character_name: str
    ) -> Optional[ConsistencyViolation]:
        """Check character appearance consistency between frames"""
        if 'character' not in frame_a.embeddings or 'character' not in frame_b.embeddings:
            return None
        
        similarity = self.reference_manager._cosine_similarity(
            frame_a.embeddings['character'],
            frame_b.embeddings['character']
        )
        
        threshold = self.thresholds['character_identity']
        
        if similarity < threshold:
            return ConsistencyViolation(
                violation_type=ConsistencyType.CHARACTER_IDENTITY,
                severity=1.0 - similarity,
                description=f"Character '{character_name}' appearance mismatch",
                frame_a=frame_a.frame_id,
                frame_b=frame_b.frame_id,
                suggested_fix="Re-generate with reference frame or adjust prompt",
                confidence=0.9
            )
        
        return None
    
    def check_lighting_consistency(
        self,
        frame_a: ReferenceFrame,
        frame_b: ReferenceFrame
    ) -> Optional[ConsistencyViolation]:
        """Check lighting consistency between frames"""
        if not frame_a.lighting_profile or not frame_b.lighting_profile:
            return None
        
        intensity_diff = abs(
            frame_a.lighting_profile.get('intensity', 0) -
            frame_b.lighting_profile.get('intensity', 0)
        )
        
        color_temp_diff = abs(
            frame_a.lighting_profile.get('color_temperature', 5500) -
            frame_b.lighting_profile.get('color_temperature', 5500)
        )
        
        if intensity_diff > 0.2 or color_temp_diff > 1000:
            return ConsistencyViolation(
                violation_type=ConsistencyType.LIGHTING,
                severity=max(intensity_diff, color_temp_diff / 5000),
                description=f"Lighting mismatch: intensity Δ{intensity_diff:.2f}, temp Δ{color_temp_diff}K",
                frame_a=frame_a.frame_id,
                frame_b=frame_b.frame_id,
                suggested_fix="Adjust lighting to match reference",
                confidence=0.85
            )
        
        return None
    
    def check_color_consistency(
        self,
        frame_a: ReferenceFrame,
        frame_b: ReferenceFrame
    ) -> Optional[ConsistencyViolation]:
        """Check color grading consistency"""
        if frame_a.color_histogram is None or frame_b.color_histogram is None:
            return None
        
        hist_diff = np.sum(np.abs(frame_a.color_histogram - frame_b.color_histogram))
        
        threshold = self.thresholds['color_grading']
        
        if hist_diff > (1.0 - threshold):
            return ConsistencyViolation(
                violation_type=ConsistencyType.COLOR_GRADING,
                severity=float(hist_diff),
                description=f"Color grading mismatch: histogram diff {hist_diff:.3f}",
                frame_a=frame_a.frame_id,
                frame_b=frame_b.frame_id,
                suggested_fix="Apply color matching LUT or grade adjustment",
                confidence=0.88
            )
        
        return None
    
    def check_spatial_consistency(
        self,
        frame_a: ReferenceFrame,
        frame_b: ReferenceFrame,
        object_id: str
    ) -> Optional[ConsistencyViolation]:
        """Check spatial relationship consistency"""
        if object_id not in frame_a.character_positions or object_id not in frame_b.character_positions:
            return None
        
        pos_a = frame_a.character_positions[object_id]
        pos_b = frame_b.character_positions[object_id]
        
        distance = np.sqrt((pos_a[0] - pos_b[0])**2 + (pos_a[1] - pos_b[1])**2)
        
        threshold = 0.12
        
        if distance > threshold:
            return ConsistencyViolation(
                violation_type=ConsistencyType.SPATIAL_RELATIONSHIP,
                severity=float(distance),
                description=f"Spatial position mismatch for {object_id}: {distance:.3f}",
                frame_a=frame_a.frame_id,
                frame_b=frame_b.frame_id,
                suggested_fix="Adjust framing or object position",
                confidence=0.80
            )
        
        return None
    
    def validate_shot_sequence(
        self,
        frames: List[ReferenceFrame],
        check_types: Optional[List[ConsistencyType]] = None
    ) -> List[ConsistencyViolation]:
        """Validate consistency across a sequence of frames"""
        violations = []
        
        check_types = check_types or [
            ConsistencyType.CHARACTER_IDENTITY,
            ConsistencyType.LIGHTING,
            ConsistencyType.COLOR_GRADING
        ]
        
        for i in range(len(frames) - 1):
            frame_a = frames[i]
            frame_b = frames[i + 1]
            
            if ConsistencyType.CHARACTER_IDENTITY in check_types:
                for char_name in frame_a.character_positions.keys():
                    violation = self.check_character_consistency(frame_a, frame_b, char_name)
                    if violation:
                        violations.append(violation)
            
            if ConsistencyType.LIGHTING in check_types:
                violation = self.check_lighting_consistency(frame_a, frame_b)
                if violation:
                    violations.append(violation)
            
            if ConsistencyType.COLOR_GRADING in check_types:
                violation = self.check_color_consistency(frame_a, frame_b)
                if violation:
                    violations.append(violation)
        
        self.consistency_history.extend(violations)
        return violations
    
    def get_consistency_score(self, frames: List[ReferenceFrame]) -> Dict[str, float]:
        """Calculate overall consistency scores"""
        violations = self.validate_shot_sequence(frames)
        
        total_checks = len(frames) - 1
        if total_checks == 0:
            return {'overall': 1.0}
        
        violation_counts = {}
        for v in violations:
            v_type = v.violation_type.value
            violation_counts[v_type] = violation_counts.get(v_type, 0) + 1
        
        scores = {
            'overall': 1.0 - (len(violations) / (total_checks * 3)),
            'character_identity': 1.0 - (violation_counts.get('character_identity', 0) / total_checks),
            'lighting': 1.0 - (violation_counts.get('lighting', 0) / total_checks),
            'color_grading': 1.0 - (violation_counts.get('color_grading', 0) / total_checks),
            'total_violations': len(violations),
            'avg_severity': float(np.mean([v.severity for v in violations])) if violations else 0.0
        }
        
        return scores
    
    def generate_consistency_report(self, frames: List[ReferenceFrame]) -> Dict:
        """Generate detailed consistency report"""
        violations = self.validate_shot_sequence(frames)
        scores = self.get_consistency_score(frames)
        
        return {
            'summary': {
                'total_frames': len(frames),
                'total_violations': len(violations),
                'consistency_score': scores['overall'],
                'pass_threshold': scores['overall'] >= 0.85
            },
            'scores_by_type': {
                'character_identity': scores.get('character_identity', 1.0),
                'lighting': scores.get('lighting', 1.0),
                'color_grading': scores.get('color_grading', 1.0)
            },
            'violations': [
                {
                    'type': v.violation_type.value,
                    'severity': v.severity,
                    'description': v.description,
                    'frames': [v.frame_a, v.frame_b],
                    'suggested_fix': v.suggested_fix,
                    'confidence': v.confidence
                }
                for v in violations
            ],
            'recommendations': self._generate_recommendations(violations)
        }
    
    def _generate_recommendations(self, violations: List[ConsistencyViolation]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        character_violations = [v for v in violations if v.violation_type == ConsistencyType.CHARACTER_IDENTITY]
        if len(character_violations) > 2:
            recommendations.append(
                "HIGH PRIORITY: Multiple character identity violations detected. "
                "Consider using reference images or fine-tuning character embeddings."
            )
        
        lighting_violations = [v for v in violations if v.violation_type == ConsistencyType.LIGHTING]
        if len(lighting_violations) > 1:
            recommendations.append(
                "Lighting inconsistency detected. Apply consistent lighting keywords "
                "or use color grading to match reference frames."
            )
        
        severe_violations = [v for v in violations if v.severity > 0.5]
        if severe_violations:
            recommendations.append(
                f"{len(severe_violations)} severe violations require immediate attention. "
                "Review suggested fixes in detail."
            )
        
        return recommendations
