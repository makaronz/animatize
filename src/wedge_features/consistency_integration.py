"""
Consistency Integration Module

Integrates ConsistencyEngine with scene_analyzer.py and other components
Provides unified interface for consistency checking across the video generation pipeline
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np

from .consistency_engine import (
    ConsistencyEngine,
    ReferenceLibrary,
    ReferenceManager,
    StyleAnchor,
    CharacterReference,
    WorldReference,
    ReferenceFrame,
    ConsistencyType,
    ConsistencyViolation,
)

try:
    from src.analyzers.scene_analyzer import SceneAnalyzer
except ImportError:
    SceneAnalyzer = None


class ConsistencyOrchestrator:
    """
    Orchestrates consistency checking across the entire video generation pipeline
    
    Integrates:
    - Scene analysis from scene_analyzer.py
    - Reference management and storage
    - Cross-shot consistency validation
    - Character/world/style anchoring
    """

    def __init__(
        self,
        storage_path: str = "data/reference_library",
        config_path: Optional[str] = None,
        enable_scene_analyzer: bool = True,
    ):
        self.logger = logging.getLogger(__name__)
        
        self.consistency_engine = ConsistencyEngine(
            reference_library=ReferenceLibrary(storage_path),
            config_path=config_path,
        )
        
        self.scene_analyzer = None
        if enable_scene_analyzer and SceneAnalyzer:
            try:
                self.scene_analyzer = SceneAnalyzer(config_path)
                self.logger.info("SceneAnalyzer initialized successfully")
            except Exception as e:
                self.logger.warning(f"Could not initialize SceneAnalyzer: {e}")
        
        self.shot_registry: Dict[str, List[ReferenceFrame]] = {}
        self.active_style_anchor: Optional[str] = None
        self.active_world: Optional[str] = None
        self.active_characters: List[str] = []

    def process_shot_image(
        self,
        image_path: str,
        shot_id: str,
        frame_id: Optional[str] = None,
        timestamp: float = 0.0,
        use_scene_analyzer: bool = True,
    ) -> ReferenceFrame:
        """
        Process a shot image and create reference frame
        
        Args:
            image_path: Path to the image file
            shot_id: Identifier for the shot
            frame_id: Optional frame identifier (auto-generated if not provided)
            timestamp: Timestamp in seconds
            use_scene_analyzer: Whether to use scene analyzer for detailed analysis
            
        Returns:
            ReferenceFrame with extracted features
        """
        if frame_id is None:
            frame_id = f"{shot_id}_frame_{timestamp}"
        
        if use_scene_analyzer and self.scene_analyzer:
            try:
                scene_analysis = self.scene_analyzer.analyze_image(image_path)
                
                frame = self.consistency_engine.integrate_scene_analysis(
                    frame_id=frame_id,
                    scene_analysis=scene_analysis,
                    shot_id=shot_id,
                    timestamp=timestamp,
                )
                
                self.logger.info(f"Processed frame {frame_id} with scene analysis")
            except Exception as e:
                self.logger.warning(f"Scene analysis failed, falling back to direct extraction: {e}")
                frame = self.consistency_engine.create_reference_from_image(
                    frame_id=frame_id,
                    image_path=image_path,
                    shot_id=shot_id,
                    timestamp=timestamp,
                )
        else:
            frame = self.consistency_engine.create_reference_from_image(
                frame_id=frame_id,
                image_path=image_path,
                shot_id=shot_id,
                timestamp=timestamp,
            )
        
        if shot_id not in self.shot_registry:
            self.shot_registry[shot_id] = []
        self.shot_registry[shot_id].append(frame)
        
        self.consistency_engine.reference_library.add_frame(frame)
        
        return frame

    def create_style_anchor_from_image(
        self,
        image_path: str,
        anchor_id: str,
        name: str,
        description: str,
        reference_images: Optional[List[str]] = None,
    ) -> StyleAnchor:
        """
        Create a style anchor from a reference image
        
        Args:
            image_path: Path to the reference image
            anchor_id: Unique identifier for the style anchor
            name: Name of the style
            description: Description of the style
            reference_images: Additional reference image paths
            
        Returns:
            StyleAnchor object
        """
        style_features, style_embedding = self.consistency_engine.style_extractor.extract_style_from_image(
            image_path
        )
        
        color_palette = style_features.get("color_palette", [])
        lighting_style = style_features.get("lighting_style", {})
        texture_profile = style_features.get("texture_profile", {})
        
        style_anchor = StyleAnchor(
            anchor_id=anchor_id,
            name=name,
            description=description,
            style_embedding=style_embedding,
            visual_attributes=style_features,
            color_palette=color_palette,
            texture_profile=texture_profile,
            lighting_style=lighting_style,
            reference_images=[image_path] + (reference_images or []),
        )
        
        self.consistency_engine.reference_library.add_style_anchor(style_anchor)
        self.active_style_anchor = anchor_id
        
        self.logger.info(f"Created style anchor '{name}' ({anchor_id})")
        
        return style_anchor

    def create_character_reference(
        self,
        character_id: str,
        name: str,
        description: str,
        reference_image: str,
        facial_features: Optional[Dict] = None,
        body_proportions: Optional[Dict] = None,
        clothing: Optional[Dict] = None,
    ) -> CharacterReference:
        """
        Create a character reference from an image
        
        Args:
            character_id: Unique identifier for the character
            name: Character name
            description: Character description
            reference_image: Path to reference image
            facial_features: Dict of facial feature descriptions
            body_proportions: Dict of body proportion measurements
            clothing: Dict of clothing descriptions
            
        Returns:
            CharacterReference object
        """
        style_features, appearance_embedding = self.consistency_engine.style_extractor.extract_style_from_image(
            reference_image
        )
        
        color_scheme = style_features.get("color_palette", [])
        
        character_ref = CharacterReference(
            character_id=character_id,
            name=name,
            description=description,
            appearance_embedding=appearance_embedding,
            facial_features=facial_features or {},
            body_proportions=body_proportions or {},
            clothing=clothing or {},
            color_scheme=color_scheme,
            reference_images=[reference_image],
        )
        
        self.consistency_engine.reference_library.add_character(character_ref)
        
        if character_id not in self.active_characters:
            self.active_characters.append(character_id)
        
        self.logger.info(f"Created character reference '{name}' ({character_id})")
        
        return character_ref

    def create_world_reference(
        self,
        world_id: str,
        name: str,
        description: str,
        reference_image: str,
        time_of_day: Optional[str] = None,
        weather: Optional[str] = None,
        architectural_style: Optional[str] = None,
    ) -> WorldReference:
        """
        Create a world/environment reference
        
        Args:
            world_id: Unique identifier for the world
            name: World name
            description: World description
            reference_image: Path to reference image
            time_of_day: Time of day setting
            weather: Weather conditions
            architectural_style: Architectural style description
            
        Returns:
            WorldReference object
        """
        style_features, spatial_embedding = self.consistency_engine.style_extractor.extract_style_from_image(
            reference_image
        )
        
        lighting_conditions = style_features.get("lighting_style", {})
        
        world_ref = WorldReference(
            world_id=world_id,
            name=name,
            description=description,
            spatial_embedding=spatial_embedding,
            lighting_conditions=lighting_conditions,
            time_of_day=time_of_day,
            weather=weather,
            architectural_style=architectural_style,
            reference_images=[reference_image],
        )
        
        self.consistency_engine.reference_library.add_world(world_ref)
        self.active_world = world_id
        
        self.logger.info(f"Created world reference '{name}' ({world_id})")
        
        return world_ref

    def validate_shot_consistency(
        self,
        shot_id: str,
        check_types: Optional[List[ConsistencyType]] = None,
    ) -> Dict[str, Any]:
        """
        Validate consistency within a single shot
        
        Args:
            shot_id: Shot identifier
            check_types: Types of consistency to check
            
        Returns:
            Validation results
        """
        if shot_id not in self.shot_registry:
            return {"error": f"Shot {shot_id} not found in registry"}
        
        frames = self.shot_registry[shot_id]
        
        if len(frames) < 2:
            return {
                "shot_id": shot_id,
                "frame_count": len(frames),
                "message": "Not enough frames for consistency check",
            }
        
        violations = self.consistency_engine.validate_shot_sequence(frames, check_types)
        scores = self.consistency_engine.get_consistency_score(frames)
        
        return {
            "shot_id": shot_id,
            "frame_count": len(frames),
            "violations": [
                {
                    "type": v.violation_type.value,
                    "severity": v.severity,
                    "description": v.description,
                    "frames": [v.frame_a, v.frame_b],
                    "suggested_fix": v.suggested_fix,
                }
                for v in violations
            ],
            "scores": scores,
            "passed": len(violations) == 0,
        }

    def validate_sequence_consistency(
        self,
        shot_ids: List[str],
        check_types: Optional[List[ConsistencyType]] = None,
    ) -> Dict[str, Any]:
        """
        Validate consistency across multiple shots
        
        Args:
            shot_ids: List of shot identifiers
            check_types: Types of consistency to check
            
        Returns:
            Validation results
        """
        all_frames = []
        for shot_id in shot_ids:
            if shot_id in self.shot_registry:
                all_frames.extend(self.shot_registry[shot_id])
        
        if len(all_frames) < 2:
            return {
                "error": "Not enough frames for consistency check",
                "frame_count": len(all_frames),
            }
        
        report = self.consistency_engine.generate_consistency_report(all_frames)
        
        return {
            "sequence": shot_ids,
            "total_frames": len(all_frames),
            "report": report,
        }

    def validate_character_across_shots(
        self,
        character_id: str,
        shot_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Validate character consistency across shots
        
        Args:
            character_id: Character identifier
            shot_ids: Optional list of shot IDs (all shots if None)
            
        Returns:
            Character consistency validation results
        """
        shot_ids = shot_ids or list(self.shot_registry.keys())
        
        frames_with_character = []
        for shot_id in shot_ids:
            if shot_id in self.shot_registry:
                for frame in self.shot_registry[shot_id]:
                    if character_id in frame.character_ids:
                        frames_with_character.append(frame)
        
        result = self.consistency_engine.validator.validate_character_consistency(
            character_id, frames_with_character
        )
        
        return result

    def get_style_consistency_report(
        self,
        style_anchor_id: str,
        shot_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate style consistency report against a style anchor
        
        Args:
            style_anchor_id: Style anchor identifier
            shot_ids: Optional list of shot IDs
            
        Returns:
            Style consistency report
        """
        style_anchor = self.consistency_engine.reference_library.get_style(style_anchor_id)
        if not style_anchor:
            return {"error": f"Style anchor {style_anchor_id} not found"}
        
        shot_ids = shot_ids or list(self.shot_registry.keys())
        
        style_scores = []
        violations = []
        
        for shot_id in shot_ids:
            if shot_id in self.shot_registry:
                for frame in self.shot_registry[shot_id]:
                    if "style" in frame.embeddings:
                        similarity = self.consistency_engine.reference_manager._cosine_similarity(
                            style_anchor.style_embedding, frame.embeddings["style"]
                        )
                        style_scores.append({
                            "frame_id": frame.frame_id,
                            "shot_id": shot_id,
                            "similarity": float(similarity),
                        })
                        
                        if similarity < 0.85:
                            violations.append({
                                "frame_id": frame.frame_id,
                                "shot_id": shot_id,
                                "similarity": float(similarity),
                                "severity": 1.0 - similarity,
                            })
        
        mean_similarity = np.mean([s["similarity"] for s in style_scores]) if style_scores else 0.0
        
        return {
            "style_anchor": style_anchor_id,
            "style_name": style_anchor.name,
            "frames_analyzed": len(style_scores),
            "mean_similarity": float(mean_similarity),
            "violations": violations,
            "consistency_rating": "high" if len(violations) == 0 else "needs_review",
            "style_scores": style_scores,
        }

    def export_consistency_data(self, export_path: str) -> bool:
        """
        Export all consistency data and references
        
        Args:
            export_path: Path for export archive
            
        Returns:
            Success status
        """
        return self.consistency_engine.reference_library.export_library(export_path)

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for the consistency system
        
        Returns:
            Summary statistics
        """
        total_frames = sum(len(frames) for frames in self.shot_registry.values())
        
        return {
            "total_shots": len(self.shot_registry),
            "total_frames": total_frames,
            "characters": len(self.consistency_engine.reference_library.characters),
            "style_anchors": len(self.consistency_engine.reference_library.styles),
            "worlds": len(self.consistency_engine.reference_library.worlds),
            "active_style_anchor": self.active_style_anchor,
            "active_world": self.active_world,
            "active_characters": self.active_characters,
            "total_violations": len(self.consistency_engine.consistency_history),
        }


class ConsistencyMiddleware:
    """
    Middleware for integrating consistency checking into generation pipeline
    
    Can be used as a callback or wrapper around generation functions
    """

    def __init__(self, orchestrator: ConsistencyOrchestrator, auto_validate: bool = True):
        self.orchestrator = orchestrator
        self.auto_validate = auto_validate
        self.logger = logging.getLogger(__name__)
        self.current_shot_id = None
        self.frame_buffer: List[str] = []

    def before_shot(self, shot_id: str):
        """Call before starting a new shot"""
        self.current_shot_id = shot_id
        self.frame_buffer = []
        self.logger.info(f"Starting shot: {shot_id}")

    def after_frame_generated(self, image_path: str, timestamp: float = 0.0) -> Optional[Dict]:
        """
        Call after each frame is generated
        
        Args:
            image_path: Path to generated frame
            timestamp: Timestamp in seconds
            
        Returns:
            Validation results if auto_validate is enabled
        """
        if self.current_shot_id is None:
            self.logger.warning("No active shot, call before_shot() first")
            return None
        
        frame = self.orchestrator.process_shot_image(
            image_path=image_path,
            shot_id=self.current_shot_id,
            timestamp=timestamp,
        )
        
        self.frame_buffer.append(frame.frame_id)
        
        if self.auto_validate and len(self.frame_buffer) >= 2:
            validation = self.orchestrator.validate_shot_consistency(self.current_shot_id)
            
            if validation.get("violations"):
                self.logger.warning(
                    f"Consistency violations detected in {self.current_shot_id}: "
                    f"{len(validation['violations'])} issues"
                )
            
            return validation
        
        return None

    def after_shot(self) -> Dict[str, Any]:
        """Call after finishing a shot"""
        if self.current_shot_id is None:
            return {"error": "No active shot"}
        
        validation = self.orchestrator.validate_shot_consistency(self.current_shot_id)
        
        self.logger.info(
            f"Completed shot {self.current_shot_id}: "
            f"{len(self.frame_buffer)} frames, "
            f"{len(validation.get('violations', []))} violations"
        )
        
        self.current_shot_id = None
        self.frame_buffer = []
        
        return validation
