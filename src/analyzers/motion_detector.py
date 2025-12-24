#!/usr/bin/env python3
"""
Motion Detection Module for ANIMAtiZE Framework
Analyzes video frames to detect motion patterns, optical flow, and movement characteristics.
"""

import cv2
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MotionDetector:
    """
    Motion detection and analysis for video processing.
    
    Features:
    - Frame differencing motion detection
    - Optical flow analysis
    - Motion vector calculation
    - Movement pattern classification
    - Motion intensity measurement
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize motion detector with configuration.
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config = self._load_config(config_path)
        self.motion_history = []
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=self.config.get('background_history', 500),
            varThreshold=self.config.get('var_threshold', 16),
            detectShadows=True
        )
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from JSON file or use defaults."""
        default_config = {
            "motion_threshold": 25,
            "min_contour_area": 100,
            "background_history": 500,
            "var_threshold": 16,
            "optical_flow_params": {
                "winSize": (15, 15),
                "maxLevel": 2,
                "criteria": (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
            },
            "frame_skip": 1,
            "output_format": "json",
            "save_frames": False,
            "cache_results": True
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
                
        return default_config
    
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
        Analyze motion in a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing motion analysis results
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
            
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            motion_data = {
                "timestamp": datetime.now().isoformat(),
                "video_path": video_path,
                "fps": fps,
                "total_frames": total_frames,
                "duration": total_frames / fps if fps > 0 else 0,
                "motion_events": [],
                "motion_intensity": [],
                "optical_flow_data": [],
                "summary": {}
            }
            
            prev_frame = None
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_count % self.config.get('frame_skip', 1) == 0:
                    # Convert to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Motion detection
                    motion_mask = self.background_subtractor.apply(gray)
                    motion_events = self._detect_motion_events(motion_mask)
                    
                    # Optical flow
                    if prev_frame is not None:
                        flow_data = self._calculate_optical_flow(prev_frame, gray)
                        motion_data["optical_flow_data"].append(flow_data)
                    
                    # Motion intensity
                    intensity = self._calculate_motion_intensity(motion_mask)
                    motion_data["motion_intensity"].append({
                        "frame": frame_count,
                        "intensity": intensity,
                        "events": len(motion_events)
                    })
                    
                    # Store motion events
                    if motion_events:
                        motion_data["motion_events"].extend([
                            {"frame": frame_count, **event} 
                            for event in motion_events
                        ])
                    
                    prev_frame = gray
                    
                frame_count += 1
                
            # Generate summary
            motion_data["summary"] = self._generate_summary(motion_data)
            
            return motion_data
            
        finally:
            cap.release()
    
    def _detect_motion_events(self, motion_mask: np.ndarray) -> List[Dict[str, Any]]:
        """Detect motion events from motion mask."""
        events = []
        
        # Find contours
        contours, _ = cv2.findContours(
            motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.config.get('min_contour_area', 100):
                x, y, w, h = cv2.boundingRect(contour)
                events.append({
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "area": int(area),
                    "center": [int(x + w//2), int(y + h//2)]
                })
        
        return events
    
    def _calculate_optical_flow(self, prev_frame: np.ndarray, 
                               curr_frame: np.ndarray) -> Dict[str, Any]:
        """Calculate optical flow between frames using Farneback method."""
        try:
            # Calculate dense optical flow using Farneback
            flow = cv2.calcOpticalFlowFarneback(
                prev_frame, curr_frame, None,
                pyr_scale=0.5,
                levels=3,
                winsize=15,
                iterations=3,
                poly_n=5,
                poly_sigma=1.2,
                flags=0
            )
            
            if flow is None:
                return {"magnitude": 0.0, "direction": 0.0, "mean_flow": [0.0, 0.0]}
                
            # Calculate flow statistics
            magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            
            return {
                "magnitude": float(np.mean(magnitude)),
                "direction": float(np.mean(angle)),
                "mean_flow": [float(np.mean(flow[..., 0])), float(np.mean(flow[..., 1]))]
            }
            
        except Exception as e:
            logger.warning(f"Optical flow calculation failed: {e}")
            return {"magnitude": 0.0, "direction": 0.0, "mean_flow": [0.0, 0.0]}
    
    def _calculate_motion_intensity(self, motion_mask: np.ndarray) -> float:
        """Calculate overall motion intensity from motion mask."""
        return float(np.sum(motion_mask > self.config.get('motion_threshold', 25)) / 
                    motion_mask.size)
    
    def _generate_summary(self, motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from motion data."""
        intensities = [item["intensity"] for item in motion_data["motion_intensity"]]
        events = motion_data["motion_events"]
        
        summary = {
            "total_motion_events": len(events),
            "average_intensity": np.mean(intensities) if intensities else 0,
            "max_intensity": np.max(intensities) if intensities else 0,
            "motion_density": len(events) / len(motion_data["motion_intensity"]) if motion_data["motion_intensity"] else 0,
            "dominant_motion_regions": self._find_dominant_regions(events),
            "motion_patterns": self._classify_motion_patterns(events)
        }
        
        return summary
    
    def _find_dominant_regions(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find dominant motion regions from events."""
        if not events:
            return []
            
        # Simple clustering of events by proximity
        regions = []
        for event in events:
            x, y = event["center"]
            found = False
            
            for region in regions:
                if abs(x - region["center"][0]) < 50 and abs(y - region["center"][1]) < 50:
                    region["count"] += 1
                    found = True
                    break
                    
            if not found:
                regions.append({"center": [x, y], "count": 1})
        
        # Sort by frequency
        return sorted(regions, key=lambda r: r["count"], reverse=True)[:3]
    
    def _classify_motion_patterns(self, events: List[Dict[str, Any]]) -> List[str]:
        """Classify motion patterns based on event distribution."""
        if len(events) < 10:
            return ["minimal"]
            
        # Simple pattern classification
        patterns = []
        
        if len(events) > 100:
            patterns.append("high_frequency")
        elif len(events) > 50:
            patterns.append("moderate_frequency")
        else:
            patterns.append("low_frequency")
            
        # Check for spatial distribution
        if events:
            x_coords = [e["center"][0] for e in events]
            y_coords = [e["center"][1] for e in events]
            
            x_range = max(x_coords) - min(x_coords)
            y_range = max(y_coords) - min(y_coords)
            
            if x_range > 200 or y_range > 200:
                patterns.append("distributed")
            else:
                patterns.append("localized")
        
        return patterns
    
    def save_analysis(self, analysis_data: Dict[str, Any], output_path: str) -> str:
        """
        Save analysis results to file.
        
        Args:
            analysis_data: Analysis results dictionary
            output_path: Path to save results
            
        Returns:
            Path where results were saved
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
            
        logger.info(f"Motion analysis saved to: {output_path}")
        return output_path
    
    def get_motion_timeline(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a timeline of motion events.
        
        Args:
            analysis_data: Analysis results
            
        Returns:
            List of motion events with timestamps
        """
        timeline = []
        
        for event in analysis_data.get("motion_events", []):
            frame_time = event["frame"] / analysis_data.get("fps", 30)
            timeline.append({
                "time": frame_time,
                "frame": event["frame"],
                "bbox": event["bbox"],
                "area": event["area"],
                "center": event["center"]
            })
            
        return sorted(timeline, key=lambda x: x["time"])


# Standalone usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python motion_detector.py <video_path>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    detector = MotionDetector()
    
    try:
        results = detector.analyze_video(video_path)
        output_path = f"motion_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        detector.save_analysis(results, output_path)
        
        print(f"Analysis complete. Results saved to: {output_path}")
        print(f"Total motion events: {results['summary']['total_motion_events']}")
        print(f"Average intensity: {results['summary']['average_intensity']:.3f}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)