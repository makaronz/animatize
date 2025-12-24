"""
ANiMAtiZE Movement Prediction Module
Analyzes static images to generate justified cinematic movement prompts
"""

import json
import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

class MovementPredictor:
    """
    Predicts justified cinematic movements from static images
    using film directing principles and physics-based analysis
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "configs/movement_prediction_rules.json"
        self.rules = self._load_rules()
        self.logger = logging.getLogger(__name__)
        
    def _load_rules(self) -> Dict:
        """Load movement prediction rules from JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Rules file not found: {self.config_path}")
            return {}
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze static image and generate justified movement predictions
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with movement predictions and justifications
        """
        try:
            image = Image.open(image_path)
            cv_image = cv2.imread(image_path)
            
            analysis = {
                "image_path": image_path,
                "image_size": image.size,
                "movement_predictions": {
                    "character_actions": self._analyze_character_movement(cv_image),
                    "camera_movements": self._analyze_camera_movement(cv_image),
                    "environment_animations": self._analyze_environmental_motion(cv_image)
                },
                "justifications": {},
                "generated_prompts": []
            }
            
            # Generate final prompts
            analysis["generated_prompts"] = self._generate_movement_prompts(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_character_movement(self, image: np.ndarray) -> List[Dict]:
        """Analyze character pose and predict justified movements"""
        predictions = []
        
        # Basic pose analysis using OpenCV
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect body contours and key points
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Simple pose analysis based on contour shape
            x, y, w, h = cv2.boundingRect(largest_contour)
            aspect_ratio = w / h
            
            # Determine pose type and predict movement
            if aspect_ratio > 1.5:
                pose = "standing/walking"
                predicted_action = "taking next step forward"
                justification = "upright stance indicates walking motion"
            elif aspect_ratio < 0.7:
                pose = "sitting/crouching"
                predicted_action = "rising to standing position"
                justification = "compressed posture suggests upward movement"
            else:
                pose = "standing neutral"
                predicted_action = "shifting weight or gesturing"
                justification = "balanced stance allows subtle movements"
            
            predictions.append({
                "pose_type": pose,
                "predicted_action": predicted_action,
                "justification": justification,
                "confidence": 0.7,
                "movement_category": "character_action"
            })
        
        return predictions
    
    def _analyze_camera_movement(self, image: np.ndarray) -> List[Dict]:
        """Analyze composition to determine justified camera movements"""
        predictions = []
        
        # Analyze composition elements
        height, width = image.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Rule of thirds analysis
        third_x, third_y = width // 3, height // 3
        
        # Detect leading lines using edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
        
        camera_movements = []
        
        if lines is not None:
            # Find dominant lines for camera movement guidance
            lines_list = lines.tolist() if hasattr(lines, 'tolist') else lines
            horizontal_lines = [line for line in lines_list if abs(line[0][3] - line[0][1]) < 20]
            vertical_lines = [line for line in lines_list if abs(line[0][2] - line[0][0]) < 20]
            
            # Create sets for comparison to avoid array issues
            horizontal_set = set(tuple(line[0]) for line in horizontal_lines)
            vertical_set = set(tuple(line[0]) for line in vertical_lines)
            
            diagonal_lines = [line for line in lines_list 
                            if tuple(line[0]) not in horizontal_set and tuple(line[0]) not in vertical_set]
            
            if diagonal_lines:
                camera_movements.append({
                    "type": "tracking_shot",
                    "direction": "along diagonal",
                    "justification": "diagonal lines naturally guide viewer movement",
                    "confidence": 0.8
                })
            
            if horizontal_lines:
                camera_movements.append({
                    "type": "pan",
                    "direction": "horizontal",
                    "justification": "horizontal lines suggest lateral movement",
                    "confidence": 0.7
                })
        
        # Add default camera movements based on composition
        camera_movements.extend([
            {
                "type": "slow_push",
                "direction": "forward",
                "justification": "gradual intimacy with subject",
                "confidence": 0.6
            },
            {
                "type": "subtle_tilt",
                "direction": "vertical",
                "justification": "reveal vertical elements in scene",
                "confidence": 0.5
            }
        ])
        
        return camera_movements
    
    def _analyze_environmental_motion(self, image: np.ndarray) -> List[Dict]:
        """Analyze environmental elements for justified animation"""
        predictions = []
        
        # Analyze lighting and atmosphere
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Detect light sources and shadows
        brightness = np.mean(hsv[:, :, 2])
        
        if isinstance(brightness, (int, float, np.number)) and brightness > 200:
            # Bright scene - predict shadow movement
            predictions.append({
                "element": "shadows",
                "motion": "gradual shift as light source moves",
                "justification": "bright lighting creates defined shadows that change over time",
                "confidence": 0.7
            })
        
        # Detect potential moving elements
        # Look for elements that typically move (leaves, fabric, etc.)
        green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
        green_pixels = cv2.countNonZero(green_mask)
        
        if isinstance(green_pixels, (int, np.integer)) and green_pixels > 1000:
            predictions.append({
                "element": "vegetation",
                "motion": "gentle swaying in breeze",
                "justification": "presence of green elements suggests natural movement",
                "confidence": 0.6
            })
        
        # Check for fabric-like textures
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        texture_variance = np.var(gray)
        
        if isinstance(texture_variance, (int, float, np.number)) and texture_variance > 100:
            predictions.append({
                "element": "fabric/textiles",
                "motion": "subtle movement from air currents",
                "justification": "textured surfaces often respond to environmental forces",
                "confidence": 0.5
            })
        
        return predictions
    
    def _generate_movement_prompts(self, analysis: Dict) -> List[str]:
        """Generate comprehensive movement prompts based on analysis"""
        prompts = []
        
        # Character movement prompts
        for char_move in analysis["movement_predictions"]["character_actions"]:
            prompt = f"Character {char_move['predicted_action']} - {char_move['justification']}"
            prompts.append(prompt)
        
        # Camera movement prompts
        for cam_move in analysis["movement_predictions"]["camera_movements"]:
            prompt = f"Camera {cam_move['type']} {cam_move['direction']} - {cam_move['justification']}"
            prompts.append(prompt)
        
        # Environmental prompts
        for env_move in analysis["movement_predictions"]["environment_animations"]:
            prompt = f"{env_move['element']} {env_move['motion']} - {env_move['justification']}"
            prompts.append(prompt)
        
        # Combined cinematic prompt
        if prompts:
            combined_prompt = "Cinematic sequence: " + "; ".join(prompts[:3]) + \
                        " - all movements must be subtle, justified, and serve the narrative"
            prompts.insert(0, combined_prompt)
        
        return prompts
    
    def validate_movement_justification(self, movement: Dict, image_context: Dict) -> bool:
        """
        Validate that a movement is justified by the image content
        
        Args:
            movement: Movement prediction with justification
            image_context: Context from image analysis
            
        Returns:
            True if movement is justified
        """
        # Check against must_do rules
        if not movement.get('justification'):
            return False
        
        # Basic physics validation
        if 'gravity' in movement.get('justification', '').lower():
            return True
        
        if 'natural' in movement.get('justification', '').lower():
            return True
        
        if 'composition' in movement.get('justification', '').lower():
            return True
        
        return False
    
    def save_analysis(self, analysis: Dict, output_path: str) -> bool:
        """Save analysis results to JSON file"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving analysis: {str(e)}")
            return False
    
    def get_cinematic_movement_prompt(self, image_path: str) -> str:
        """
        Generate a complete cinematic movement prompt for video generation
        
        Args:
            image_path: Path to the static image
            
        Returns:
            Comprehensive movement prompt
        """
        analysis = self.analyze_image(image_path)
        
        if "error" in analysis:
            return f"Error analyzing image: {analysis['error']}"
        
        # Build comprehensive prompt
        prompts = analysis.get('generated_prompts', [])
        
        if not prompts:
            return "No justified movements detected - static scene"
        
        # Use the combined prompt as primary
        primary_prompt = prompts[0] if prompts else ""
        
        # Add technical specifications
        technical_specs = (
            "Technical requirements: 24fps, cinematic motion blur, smooth keyframes, "
            "natural timing, physics-based movement, emotional coherence"
        )
        
        return f"{primary_prompt}. {technical_specs}"

# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        predictor = MovementPredictor()
        
        analysis = predictor.analyze_image(image_path)
        
        print("=== Movement Analysis ===")
        print(json.dumps(analysis, indent=2))
        
        cinematic_prompt = predictor.get_cinematic_movement_prompt(image_path)
        print(f"\n=== Cinematic Movement Prompt ===")
        print(cinematic_prompt)
    else:
        print("Usage: python movement_predictor.py <image_path>")