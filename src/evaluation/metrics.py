"""
Video Generation Evaluation Metrics
Comprehensive metrics for assessing video quality and adherence to instructions
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import cv2
from skimage.metrics import structural_similarity as ssim
from abc import ABC, abstractmethod


@dataclass
class MetricResult:
    """Result from a metric evaluation"""
    metric_name: str
    score: float
    passed: bool
    threshold: float
    details: Optional[Dict[str, Any]] = None
    frame_scores: Optional[List[float]] = None


class VideoMetric(ABC):
    """Base class for video evaluation metrics"""
    
    def __init__(self, threshold: float = 0.0):
        self.threshold = threshold
    
    @abstractmethod
    def compute(self, video_path: str, reference_data: Optional[Any] = None) -> MetricResult:
        """Compute metric for a video"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get metric name"""
        pass


class TemporalConsistencyMetric(VideoMetric):
    """Measures temporal consistency across frames"""
    
    def __init__(self, threshold: float = 0.85):
        super().__init__(threshold)
    
    def get_name(self) -> str:
        return "temporal_consistency"
    
    def compute(self, video_path: str, reference_data: Optional[Any] = None) -> MetricResult:
        """
        Compute temporal consistency using frame-to-frame similarity
        Higher scores indicate more consistent motion
        """
        cap = cv2.VideoCapture(video_path)
        frame_scores = []
        prev_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Compute SSIM between consecutive frames
                score = ssim(prev_frame, gray_frame)
                frame_scores.append(score)
            
            prev_frame = gray_frame
        
        cap.release()
        
        if not frame_scores:
            return MetricResult(
                metric_name=self.get_name(),
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "No frames processed"}
            )
        
        avg_score = float(np.mean(frame_scores))
        std_score = float(np.std(frame_scores))
        
        return MetricResult(
            metric_name=self.get_name(),
            score=avg_score,
            passed=avg_score >= self.threshold,
            threshold=self.threshold,
            frame_scores=frame_scores,
            details={
                "mean": avg_score,
                "std": std_score,
                "min": float(np.min(frame_scores)),
                "max": float(np.max(frame_scores)),
                "num_frames": len(frame_scores)
            }
        )


class OpticalFlowConsistencyMetric(VideoMetric):
    """Measures motion consistency using optical flow"""
    
    def __init__(self, threshold: float = 0.80):
        super().__init__(threshold)
    
    def get_name(self) -> str:
        return "optical_flow_consistency"
    
    def compute(self, video_path: str, reference_data: Optional[Any] = None) -> MetricResult:
        """Compute optical flow consistency across frames"""
        cap = cv2.VideoCapture(video_path)
        
        ret, prev_frame = cap.read()
        if not ret:
            cap.release()
            return MetricResult(
                metric_name=self.get_name(),
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "Could not read video"}
            )
        
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        flow_magnitudes = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None,
                pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, poly_n=5, poly_sigma=1.2, flags=0
            )
            
            # Calculate flow magnitude
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            avg_magnitude = np.mean(magnitude)
            flow_magnitudes.append(avg_magnitude)
            
            prev_gray = gray
            frame_count += 1
        
        cap.release()
        
        if not flow_magnitudes:
            return MetricResult(
                metric_name=self.get_name(),
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "No flow computed"}
            )
        
        # Consistency is inverse of variation in flow magnitude
        flow_std = float(np.std(flow_magnitudes))
        flow_mean = float(np.mean(flow_magnitudes))
        
        # Normalize consistency score (lower variation = higher consistency)
        if flow_mean > 0:
            consistency_score = 1.0 - min(flow_std / flow_mean, 1.0)
        else:
            consistency_score = 0.0
        
        return MetricResult(
            metric_name=self.get_name(),
            score=consistency_score,
            passed=consistency_score >= self.threshold,
            threshold=self.threshold,
            frame_scores=flow_magnitudes,
            details={
                "mean_flow": flow_mean,
                "std_flow": flow_std,
                "consistency_score": consistency_score,
                "num_frames": frame_count
            }
        )


class SSIMMetric(VideoMetric):
    """Structural Similarity Index Metric"""
    
    def __init__(self, threshold: float = 0.75):
        super().__init__(threshold)
    
    def get_name(self) -> str:
        return "ssim"
    
    def compute(self, video_path: str, reference_data: Optional[str] = None) -> MetricResult:
        """
        Compute SSIM between generated video and reference
        If no reference, compute average SSIM between consecutive frames
        """
        if reference_data is None:
            # Use temporal SSIM (frame-to-frame)
            return self._compute_temporal_ssim(video_path)
        else:
            # Use reference comparison
            return self._compute_reference_ssim(video_path, reference_data)
    
    def _compute_temporal_ssim(self, video_path: str) -> MetricResult:
        """Compute SSIM between consecutive frames"""
        cap = cv2.VideoCapture(video_path)
        ssim_scores = []
        prev_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                score = ssim(prev_frame, gray)
                ssim_scores.append(score)
            
            prev_frame = gray
        
        cap.release()
        
        if not ssim_scores:
            return MetricResult(
                metric_name=self.get_name(),
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "No frames processed"}
            )
        
        avg_score = float(np.mean(ssim_scores))
        
        return MetricResult(
            metric_name=self.get_name(),
            score=avg_score,
            passed=avg_score >= self.threshold,
            threshold=self.threshold,
            frame_scores=ssim_scores,
            details={
                "mean": avg_score,
                "std": float(np.std(ssim_scores)),
                "num_frames": len(ssim_scores)
            }
        )
    
    def _compute_reference_ssim(self, video_path: str, reference_path: str) -> MetricResult:
        """Compute SSIM against reference video"""
        cap1 = cv2.VideoCapture(video_path)
        cap2 = cv2.VideoCapture(reference_path)
        ssim_scores = []
        
        while True:
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()
            
            if not ret1 or not ret2:
                break
            
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Resize if needed
            if gray1.shape != gray2.shape:
                gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
            
            score = ssim(gray1, gray2)
            ssim_scores.append(score)
        
        cap1.release()
        cap2.release()
        
        if not ssim_scores:
            return MetricResult(
                metric_name=self.get_name(),
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "No matching frames"}
            )
        
        avg_score = float(np.mean(ssim_scores))
        
        return MetricResult(
            metric_name=self.get_name(),
            score=avg_score,
            passed=avg_score >= self.threshold,
            threshold=self.threshold,
            frame_scores=ssim_scores,
            details={"mean": avg_score, "num_frames": len(ssim_scores)}
        )


class PerceptualQualityMetric(VideoMetric):
    """Perceptual quality using multiple image quality indicators"""
    
    def __init__(self, threshold: float = 0.80):
        super().__init__(threshold)
    
    def get_name(self) -> str:
        return "perceptual_quality"
    
    def compute(self, video_path: str, reference_data: Optional[Any] = None) -> MetricResult:
        """
        Compute perceptual quality using:
        - Sharpness (Laplacian variance)
        - Contrast
        - Brightness consistency
        """
        cap = cv2.VideoCapture(video_path)
        sharpness_scores = []
        contrast_scores = []
        brightness_scores = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            sharpness_scores.append(sharpness)
            
            # Contrast (standard deviation)
            contrast = gray.std()
            contrast_scores.append(contrast)
            
            # Brightness (mean)
            brightness = gray.mean()
            brightness_scores.append(brightness)
        
        cap.release()
        
        if not sharpness_scores:
            return MetricResult(
                metric_name=self.get_name(),
                score=0.0,
                passed=False,
                threshold=self.threshold,
                details={"error": "No frames processed"}
            )
        
        # Normalize and combine metrics
        # Higher sharpness = better (normalize to 0-1 range)
        avg_sharpness = float(np.mean(sharpness_scores))
        norm_sharpness = min(avg_sharpness / 1000.0, 1.0)  # Typical range 0-1000
        
        # Moderate contrast is good (normalize to 0-1 range)
        avg_contrast = float(np.mean(contrast_scores))
        norm_contrast = min(avg_contrast / 128.0, 1.0)  # Typical range 0-128
        
        # Brightness consistency (lower std = better)
        brightness_std = float(np.std(brightness_scores))
        norm_brightness_consistency = 1.0 - min(brightness_std / 128.0, 1.0)
        
        # Combined perceptual quality score
        quality_score = (norm_sharpness * 0.4 + 
                        norm_contrast * 0.3 + 
                        norm_brightness_consistency * 0.3)
        
        return MetricResult(
            metric_name=self.get_name(),
            score=quality_score,
            passed=quality_score >= self.threshold,
            threshold=self.threshold,
            details={
                "sharpness": avg_sharpness,
                "contrast": avg_contrast,
                "brightness_std": brightness_std,
                "normalized_sharpness": norm_sharpness,
                "normalized_contrast": norm_contrast,
                "brightness_consistency": norm_brightness_consistency,
                "num_frames": len(sharpness_scores)
            }
        )


class InstructionFollowingMetric(VideoMetric):
    """Placeholder for instruction following metric (requires CLIP or similar)"""
    
    def __init__(self, threshold: float = 0.90):
        super().__init__(threshold)
    
    def get_name(self) -> str:
        return "instruction_following"
    
    def compute(self, video_path: str, reference_data: Optional[Dict] = None) -> MetricResult:
        """
        Compute instruction following score
        In production, this would use CLIP or similar models
        For now, returns a placeholder
        """
        prompt = reference_data.get("prompt", "") if reference_data else ""
        
        # Placeholder implementation
        # In production: extract frames, encode with CLIP, compare with prompt embedding
        
        return MetricResult(
            metric_name=self.get_name(),
            score=0.0,
            passed=False,
            threshold=self.threshold,
            details={
                "status": "not_implemented",
                "note": "Requires CLIP model integration",
                "prompt": prompt
            }
        )


class CLIPSimilarityMetric(VideoMetric):
    """Placeholder for CLIP-based semantic similarity"""
    
    def __init__(self, threshold: float = 0.80):
        super().__init__(threshold)
    
    def get_name(self) -> str:
        return "clip_similarity"
    
    def compute(self, video_path: str, reference_data: Optional[Dict] = None) -> MetricResult:
        """
        Compute CLIP similarity between video frames and prompt
        Placeholder implementation
        """
        prompt = reference_data.get("prompt", "") if reference_data else ""
        
        return MetricResult(
            metric_name=self.get_name(),
            score=0.0,
            passed=False,
            threshold=self.threshold,
            details={
                "status": "not_implemented",
                "note": "Requires CLIP model (torch/transformers)",
                "prompt": prompt
            }
        )


class MetricsEngine:
    """Engine for computing all video evaluation metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, VideoMetric] = {}
        self._register_default_metrics()
    
    def _register_default_metrics(self):
        """Register default metrics"""
        self.register_metric(TemporalConsistencyMetric())
        self.register_metric(OpticalFlowConsistencyMetric())
        self.register_metric(SSIMMetric())
        self.register_metric(PerceptualQualityMetric())
        self.register_metric(InstructionFollowingMetric())
        self.register_metric(CLIPSimilarityMetric())
    
    def register_metric(self, metric: VideoMetric):
        """Register a new metric"""
        self.metrics[metric.get_name()] = metric
    
    def compute_all(
        self,
        video_path: str,
        reference_data: Optional[Dict] = None,
        enabled_metrics: Optional[List[str]] = None
    ) -> Dict[str, MetricResult]:
        """
        Compute all enabled metrics for a video
        
        Args:
            video_path: Path to video file
            reference_data: Optional reference data (prompt, reference video, etc.)
            enabled_metrics: List of metric names to compute (None = all)
        
        Returns:
            Dictionary mapping metric names to results
        """
        results = {}
        
        metrics_to_compute = (
            {k: v for k, v in self.metrics.items() if k in enabled_metrics}
            if enabled_metrics
            else self.metrics
        )
        
        for name, metric in metrics_to_compute.items():
            try:
                result = metric.compute(video_path, reference_data)
                results[name] = result
            except Exception as e:
                results[name] = MetricResult(
                    metric_name=name,
                    score=0.0,
                    passed=False,
                    threshold=metric.threshold,
                    details={"error": str(e)}
                )
        
        return results
    
    def update_thresholds(self, thresholds: Dict[str, float]):
        """Update thresholds for metrics"""
        for metric_name, threshold in thresholds.items():
            if metric_name in self.metrics:
                self.metrics[metric_name].threshold = threshold
