"""
Golden Set Management for Regression Testing
Maintains reference outputs with hashes and embeddings for comparison
"""

import hashlib
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import cv2


@dataclass
class GoldenReference:
    """Reference output in golden set"""
    reference_id: str
    scenario_id: str
    video_path: str
    model_version: str
    created_at: str
    
    # Content hashes
    video_hash: str
    frame_hashes: List[str]
    
    # Embeddings (placeholders for CLIP/visual embeddings)
    visual_embeddings: Optional[List[float]] = None
    semantic_embedding: Optional[List[float]] = None
    
    # Metrics from evaluation
    metric_results: Dict[str, float] = None
    
    # Metadata
    duration_frames: int = 0
    resolution: tuple = None
    fps: float = 0.0
    file_size_bytes: int = 0
    
    # Validation
    expert_approved: bool = False
    approval_date: Optional[str] = None
    approver: Optional[str] = None
    notes: Optional[str] = None


class GoldenSetManager:
    """Manages golden reference set for regression testing"""
    
    def __init__(self, golden_set_path: str = "data/golden_set"):
        self.golden_set_path = Path(golden_set_path)
        self.golden_set_path.mkdir(parents=True, exist_ok=True)
        
        self.metadata_path = self.golden_set_path / "metadata.json"
        self.references: Dict[str, GoldenReference] = {}
        
        self._load_metadata()
    
    def _load_metadata(self):
        """Load existing golden set metadata"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                data = json.load(f)
                
            for ref_id, ref_data in data.get("references", {}).items():
                self.references[ref_id] = GoldenReference(**ref_data)
    
    def _save_metadata(self):
        """Save golden set metadata"""
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "total_references": len(self.references),
            "references": {
                ref_id: asdict(ref)
                for ref_id, ref in self.references.items()
            }
        }
        
        with open(self.metadata_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def compute_video_hash(self, video_path: str) -> str:
        """Compute SHA-256 hash of video file"""
        sha256 = hashlib.sha256()
        
        with open(video_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def compute_frame_hashes(self, video_path: str, sample_every: int = 10) -> List[str]:
        """
        Compute hashes for sampled frames
        
        Args:
            video_path: Path to video
            sample_every: Sample every Nth frame
        
        Returns:
            List of frame hashes
        """
        cap = cv2.VideoCapture(video_path)
        frame_hashes = []
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % sample_every == 0:
                # Convert frame to bytes and hash
                frame_bytes = frame.tobytes()
                frame_hash = hashlib.sha256(frame_bytes).hexdigest()
                frame_hashes.append(frame_hash)
            
            frame_idx += 1
        
        cap.release()
        return frame_hashes
    
    def extract_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata"""
        cap = cv2.VideoCapture(video_path)
        
        metadata = {
            "duration_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "fps": float(cap.get(cv2.CAP_PROP_FPS)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "file_size_bytes": Path(video_path).stat().st_size
        }
        
        cap.release()
        return metadata
    
    def add_reference(
        self,
        scenario_id: str,
        video_path: str,
        model_version: str,
        metric_results: Optional[Dict[str, float]] = None,
        expert_approved: bool = False,
        approver: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Add new reference to golden set
        
        Args:
            scenario_id: Test scenario ID
            video_path: Path to reference video
            model_version: Model version that generated this
            metric_results: Metric scores from evaluation
            expert_approved: Whether expert approved this reference
            approver: Name of approver
            notes: Optional notes
        
        Returns:
            Reference ID
        """
        # Generate reference ID
        reference_id = f"REF_{scenario_id}_{model_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Copy video to golden set directory
        video_path_obj = Path(video_path)
        golden_video_path = self.golden_set_path / f"{reference_id}{video_path_obj.suffix}"
        
        import shutil
        shutil.copy2(video_path, golden_video_path)
        
        # Compute hashes
        video_hash = self.compute_video_hash(str(golden_video_path))
        frame_hashes = self.compute_frame_hashes(str(golden_video_path))
        
        # Extract metadata
        video_metadata = self.extract_video_metadata(str(golden_video_path))
        
        # Create reference
        reference = GoldenReference(
            reference_id=reference_id,
            scenario_id=scenario_id,
            video_path=str(golden_video_path),
            model_version=model_version,
            created_at=datetime.now().isoformat(),
            video_hash=video_hash,
            frame_hashes=frame_hashes,
            metric_results=metric_results or {},
            duration_frames=video_metadata["duration_frames"],
            resolution=(video_metadata["width"], video_metadata["height"]),
            fps=video_metadata["fps"],
            file_size_bytes=video_metadata["file_size_bytes"],
            expert_approved=expert_approved,
            approval_date=datetime.now().isoformat() if expert_approved else None,
            approver=approver,
            notes=notes
        )
        
        self.references[reference_id] = reference
        self._save_metadata()
        
        return reference_id
    
    def get_reference(self, reference_id: str) -> Optional[GoldenReference]:
        """Get reference by ID"""
        return self.references.get(reference_id)
    
    def get_references_by_scenario(self, scenario_id: str) -> List[GoldenReference]:
        """Get all references for a scenario"""
        return [
            ref for ref in self.references.values()
            if ref.scenario_id == scenario_id
        ]
    
    def get_latest_reference(
        self,
        scenario_id: str,
        model_version: Optional[str] = None,
        expert_approved_only: bool = False
    ) -> Optional[GoldenReference]:
        """
        Get latest reference for a scenario
        
        Args:
            scenario_id: Test scenario ID
            model_version: Filter by model version (optional)
            expert_approved_only: Only return expert-approved references
        
        Returns:
            Latest matching reference or None
        """
        candidates = self.get_references_by_scenario(scenario_id)
        
        if model_version:
            candidates = [r for r in candidates if r.model_version == model_version]
        
        if expert_approved_only:
            candidates = [r for r in candidates if r.expert_approved]
        
        if not candidates:
            return None
        
        # Sort by creation date and return latest
        candidates.sort(key=lambda r: r.created_at, reverse=True)
        return candidates[0]
    
    def compare_videos(
        self,
        video_path1: str,
        video_path2: str,
        comparison_level: str = "hash"
    ) -> Dict[str, Any]:
        """
        Compare two videos
        
        Args:
            video_path1: First video path
            video_path2: Second video path
            comparison_level: 'hash' (exact match) or 'frames' (frame-by-frame)
        
        Returns:
            Comparison results
        """
        if comparison_level == "hash":
            hash1 = self.compute_video_hash(video_path1)
            hash2 = self.compute_video_hash(video_path2)
            
            return {
                "identical": hash1 == hash2,
                "hash1": hash1,
                "hash2": hash2
            }
        
        elif comparison_level == "frames":
            frame_hashes1 = self.compute_frame_hashes(video_path1, sample_every=5)
            frame_hashes2 = self.compute_frame_hashes(video_path2, sample_every=5)
            
            if len(frame_hashes1) != len(frame_hashes2):
                return {
                    "identical": False,
                    "reason": "frame_count_mismatch",
                    "frame_count1": len(frame_hashes1),
                    "frame_count2": len(frame_hashes2)
                }
            
            matching_frames = sum(
                1 for h1, h2 in zip(frame_hashes1, frame_hashes2) if h1 == h2
            )
            
            return {
                "identical": matching_frames == len(frame_hashes1),
                "matching_frames": matching_frames,
                "total_frames": len(frame_hashes1),
                "match_percentage": matching_frames / len(frame_hashes1) * 100
            }
        
        else:
            raise ValueError(f"Unknown comparison_level: {comparison_level}")
    
    def validate_reference(
        self,
        reference_id: str,
        approver: str,
        approved: bool = True,
        notes: Optional[str] = None
    ):
        """Mark reference as validated by expert"""
        if reference_id not in self.references:
            raise ValueError(f"Reference {reference_id} not found")
        
        reference = self.references[reference_id]
        reference.expert_approved = approved
        reference.approval_date = datetime.now().isoformat()
        reference.approver = approver
        
        if notes:
            reference.notes = notes
        
        self._save_metadata()
    
    def export_summary(self, output_path: str):
        """Export golden set summary"""
        summary = {
            "total_references": len(self.references),
            "expert_approved": sum(1 for r in self.references.values() if r.expert_approved),
            "by_scenario": {},
            "by_model_version": {},
            "references": []
        }
        
        # Group by scenario
        for ref in self.references.values():
            if ref.scenario_id not in summary["by_scenario"]:
                summary["by_scenario"][ref.scenario_id] = 0
            summary["by_scenario"][ref.scenario_id] += 1
            
            if ref.model_version not in summary["by_model_version"]:
                summary["by_model_version"][ref.model_version] = 0
            summary["by_model_version"][ref.model_version] += 1
            
            summary["references"].append({
                "reference_id": ref.reference_id,
                "scenario_id": ref.scenario_id,
                "model_version": ref.model_version,
                "expert_approved": ref.expert_approved,
                "created_at": ref.created_at
            })
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
