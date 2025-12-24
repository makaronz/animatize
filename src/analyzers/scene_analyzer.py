"""
Scene Analysis Module for ANIMAtiZE Framework
Computer vision analysis for generated images
Optimized for minimal dependencies
"""

import cv2
import numpy as np
from PIL import Image, ImageStat
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class SceneAnalyzer:
    """
    Lightweight scene analysis for generated images
    Provides object detection, depth estimation, and composition analysis
    without heavy dependencies
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Analysis cache
        self.analysis_cache = {}
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration for scene analysis"""
        default_config = {
            "confidence_threshold": 0.5,
            "max_objects": 20,
            "composition_weights": {
                "rule_of_thirds": 0.3,
                "symmetry": 0.3,
                "depth": 0.4
            },
            "scene_thresholds": {
                "sky_ratio": 0.3,
                "green_ratio": 0.2,
                "building_ratio": 0.3,
                "water_ratio": 0.1
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                default_config.update(config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Comprehensive image analysis using OpenCV and PIL
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing all analysis results
        """
        if image_path in self.analysis_cache:
            return self.analysis_cache[image_path]
        
        try:
            # Load image
            image = Image.open(image_path)
            cv_image = cv2.imread(image_path)
            
            if cv_image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Perform analysis
            image_info = self._get_image_info(image)
            objects = self._detect_objects_fallback(cv_image)
            depth = self._estimate_depth_fallback(cv_image)
            composition = self._analyze_composition(cv_image)
            scene_type = self._classify_scene(cv_image)
            
            # Build analysis structure
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "image_info": image_info,
                "objects": objects,
                "depth": depth,
                "composition": composition,
                "scene_type": scene_type
            }
            
            # Calculate aesthetics after all other data is ready
            analysis["aesthetics"] = self._calculate_aesthetics_score(analysis)
            
            # Cache results
            self.analysis_cache[image_path] = analysis
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze image {image_path}: {e}")
            return self._get_error_analysis(str(e))
    
    def _get_image_info(self, image: Image.Image) -> Dict:
        """Extract basic image information"""
        stat = ImageStat.Stat(image)
        
        return {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
            "aspect_ratio": round(image.width / image.height, 3),
            "mean_brightness": sum(stat.mean) / len(stat.mean),
            "std_dev": sum(stat.stddev) / len(stat.stddev)
        }
    
    def _detect_objects_fallback(self, image: np.ndarray) -> List[Dict]:
        """Object detection using color segmentation and contour detection"""
        objects = []
        height, width = image.shape[:2]
        
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for common objects
        color_ranges = {
            "sky": [(100, 50, 50), (130, 255, 255)],
            "vegetation": [(35, 50, 50), (85, 255, 255)],
            "building": [(0, 0, 50), (180, 50, 200)],
            "water": [(100, 50, 50), (140, 255, 255)],
            "ground": [(10, 50, 50), (35, 255, 255)]
        }
        
        for obj_class, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, lower, upper)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > (width * height * 0.01):  # Filter small objects
                    x, y, w, h = cv2.boundingRect(contour)
                    confidence = min(area / (width * height), 1.0)
                    
                    objects.append({
                        "class": obj_class,
                        "confidence": round(confidence, 2),
                        "bbox": [x, y, w, h],
                        "center": [x + w//2, y + h//2],
                        "area": area
                    })
        
        # Sort by confidence and limit to max_objects
        objects.sort(key=lambda x: x["confidence"], reverse=True)
        return objects[:self.config["max_objects"]]
    
    def _estimate_depth_fallback(self, image: np.ndarray) -> Dict:
        """Depth estimation using image gradients and edge analysis"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Gradient magnitude as depth proxy
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Normalize to 0-1 range
        gradient_norm = (gradient_magnitude - gradient_magnitude.min()) / (gradient_magnitude.max() - gradient_magnitude.min())
        
        # Create depth map (inverted: high gradient = near, low gradient = far)
        depth_map = 1.0 - gradient_norm
        
        return {
            "method": "gradient_depth",
            "min_depth": float(depth_map.min()),
            "max_depth": float(depth_map.max()),
            "mean_depth": float(depth_map.mean()),
            "depth_variance": float(depth_map.var()),
            "depth_complexity": float(np.std(gradient_norm))
        }
    
    def _analyze_composition(self, image: np.ndarray) -> Dict:
        """Analyze image composition using OpenCV"""
        height, width = image.shape[:2]
        
        # Rule of thirds analysis
        third_width = width // 3
        third_height = height // 3
        
        # Edge detection for leading lines
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Symmetry analysis
        left_half = image[:, :width//2]
        right_half = image[:, width//2:]
        right_half_flipped = cv2.flip(right_half, 1)
        
        # Calculate symmetry score
        left_gray = cv2.cvtColor(left_half, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_half_flipped, cv2.COLOR_BGR2GRAY)
        
        # Resize to same dimensions
        if left_gray.shape != right_gray.shape:
            right_gray = cv2.resize(right_gray, (left_gray.shape[1], left_gray.shape[0]))
        
        diff = cv2.absdiff(left_gray, right_gray)
        symmetry_score = 1.0 - (np.mean(diff) / 255.0)
        
        # Vertical symmetry
        top_half = image[:height//2, :]
        bottom_half = image[height//2:, :]
        bottom_flipped = cv2.flip(bottom_half, 0)
        
        top_gray = cv2.cvtColor(top_half, cv2.COLOR_BGR2GRAY)
        bottom_gray = cv2.cvtColor(bottom_flipped, cv2.COLOR_BGR2GRAY)
        
        if top_gray.shape != bottom_gray.shape:
            bottom_gray = cv2.resize(bottom_gray, (top_gray.shape[1], top_gray.shape[0]))
        
        vert_diff = cv2.absdiff(top_gray, bottom_gray)
        vertical_symmetry = 1.0 - (np.mean(vert_diff) / 255.0)
        
        # Edge density for complexity
        edge_density = float(np.sum(edges > 0) / (width * height))
        
        return {
            "rule_of_thirds": {
                "grid": [[0, third_width, 2*third_width], [0, third_height, 2*third_height]],
                "key_points": [[third_width, third_height], [2*third_width, third_height], 
                             [third_width, 2*third_height], [2*third_width, 2*third_height]]
            },
            "symmetry": {
                "horizontal_symmetry": round(symmetry_score, 3),
                "vertical_symmetry": round(vertical_symmetry, 3)
            },
            "complexity": {
                "edge_density": round(edge_density, 3),
                "texture_complexity": round(self._calculate_texture_complexity(gray), 3)
            }
        }
    
    def _calculate_texture_complexity(self, gray_image: np.ndarray) -> float:
        """Calculate texture complexity using local standard deviation"""
        # Calculate local standard deviation
        kernel = np.ones((5, 5), np.float32) / 25
        local_mean = cv2.filter2D(gray_image.astype(np.float32), -1, kernel)
        local_mean_sq = cv2.filter2D((gray_image.astype(np.float32) ** 2), -1, kernel)
        local_var = local_mean_sq - (local_mean ** 2)
        
        return float(np.sqrt(np.mean(local_var)))
    
    def _classify_scene(self, image: np.ndarray) -> Dict:
        """Classify the scene type based on visual features"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        height, width = image.shape[:2]
        total_pixels = width * height
        
        # Color-based classification
        color_ranges = {
            "sky": [(100, 50, 50), (130, 255, 255)],
            "vegetation": [(35, 50, 50), (85, 255, 255)],
            "building": [(0, 0, 50), (180, 50, 200)],
            "water": [(100, 50, 50), (140, 255, 255)]
        }
        
        ratios = {}
        for scene_type, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, lower, upper)
            pixel_count = cv2.countNonZero(mask)
            ratios[scene_type] = pixel_count / total_pixels
        
        # Determine dominant scene type
        thresholds = self.config["scene_thresholds"]
        
        if ratios["sky"] > thresholds["sky_ratio"] and ratios["vegetation"] > thresholds["green_ratio"]:
            scene_type = "landscape"
            confidence = min(ratios["sky"] + ratios["vegetation"], 1.0)
        elif ratios["building"] > thresholds["building_ratio"]:
            scene_type = "urban"
            confidence = ratios["building"]
        elif ratios["water"] > thresholds["water_ratio"]:
            scene_type = "water_scene"
            confidence = ratios["water"]
        elif ratios["vegetation"] > thresholds["green_ratio"]:
            scene_type = "nature"
            confidence = ratios["vegetation"]
        elif ratios["sky"] > 0.5:
            scene_type = "sky"
            confidence = ratios["sky"]
        else:
            scene_type = "mixed"
            confidence = 0.5
        
        return {
            "type": scene_type,
            "confidence": round(confidence, 2),
            "color_ratios": {k: round(v, 3) for k, v in ratios.items()}
        }
    
    def _calculate_aesthetics_score(self, analysis: Dict) -> Dict:
        """Calculate overall aesthetics score based on analysis"""
        weights = self.config["composition_weights"]
        
        # Composition score
        composition_score = 0.0
        if "composition" in analysis:
            comp = analysis["composition"]
            symmetry = comp["symmetry"]["horizontal_symmetry"]
            composition_score += weights["symmetry"] * symmetry
            
            # Rule of thirds score based on object placement
            if "objects" in analysis:
                objects = analysis["objects"]
                rule_thirds_score = self._calculate_rule_of_thirds_score(objects, analysis["image_info"])
                composition_score += weights["rule_of_thirds"] * rule_thirds_score
        
        # Depth score
        depth_score = 0.0
        if "depth" in analysis:
            depth = analysis["depth"]
            depth_variance = depth.get("depth_variance", 0)
            depth_score = min(depth_variance * 10, 1.0) * weights["depth"]
        
        # Color harmony score
        color_score = 0.7  # Placeholder - could be enhanced with color theory
        
        # Overall aesthetics score
        total_score = (composition_score + depth_score + color_score) / 3.0
        
        return {
            "overall_score": round(total_score, 3),
            "composition_score": round(composition_score, 3),
            "depth_score": round(depth_score, 3),
            "color_score": round(color_score, 3),
            "breakdown": {
                "symmetry": round(analysis.get("composition", {}).get("symmetry", {}).get("horizontal_symmetry", 0), 3),
                "depth_variance": round(analysis.get("depth", {}).get("depth_variance", 0), 3),
                "edge_density": round(analysis.get("composition", {}).get("complexity", {}).get("edge_density", 0), 3)
            }
        }
    
    def _calculate_rule_of_thirds_score(self, objects: List[Dict], image_info: Dict) -> float:
        """Calculate how well objects align with rule of thirds"""
        if not objects:
            return 0.0
        
        width = image_info["width"]
        height = image_info["height"]
        
        # Rule of thirds intersection points
        third_points = [
            (width // 3, height // 3),
            (2 * width // 3, height // 3),
            (width // 3, 2 * height // 3),
            (2 * width // 3, 2 * height // 3)
        ]
        
        score = 0.0
        for obj in objects:
            center = obj["center"]
            
            # Find closest third point
            min_distance = float('inf')
            for point in third_points:
                distance = np.sqrt((center[0] - point[0])**2 + (center[1] - point[1])**2)
                min_distance = min(min_distance, distance)
            
            # Convert distance to score (closer = higher score)
            max_distance = np.sqrt(width**2 + height**2) / 6
            obj_score = max(0, 1 - (min_distance / max_distance))
            score += obj_score * obj["confidence"]
        
        return score / len(objects) if objects else 0.0
    
    def save_analysis(self, analysis: Dict, output_path: str):
        """Save analysis results to JSON file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            self.logger.info(f"Analysis saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save analysis: {e}")
    
    def batch_analyze(self, image_dir: str, output_dir: str) -> Dict:
        """Analyze multiple images in a directory"""
        image_dir = Path(image_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            "total_images": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "analyses": {}
        }
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        for image_file in image_dir.iterdir():
            if image_file.suffix.lower() in image_extensions:
                results["total_images"] += 1
                
                try:
                    analysis = self.analyze_image(str(image_file))
                    
                    # Save individual analysis
                    output_file = output_dir / f"{image_file.stem}_analysis.json"
                    self.save_analysis(analysis, str(output_file))
                    
                    results["analyses"][str(image_file)] = analysis
                    results["successful_analyses"] += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to analyze {image_file}: {e}")
                    results["failed_analyses"] += 1
        
        return results
    
    def _get_error_analysis(self, error_msg: str) -> Dict:
        """Return error analysis structure"""
        return {
            "error": True,
            "error_message": error_msg,
            "timestamp": datetime.now().isoformat()
        }


# Simple usage example
if __name__ == "__main__":
    # Basic test
    analyzer = SceneAnalyzer()
    print("Scene Analyzer initialized successfully")
    print("Dependencies: OpenCV, PIL, NumPy")