"""
Test suite for Movement Predictor Module
Tests movement prediction from static images using cinematic rules
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.analyzers.movement_predictor import MovementPredictor

class TestMovementPredictor(unittest.TestCase):
    """Test cases for Movement Predictor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.predictor = MovementPredictor()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test images
        self.create_test_images()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_images(self):
        """Create test images for movement prediction"""
        # Test image 1: Standing person
        self.standing_img_path = os.path.join(self.temp_dir, "standing.jpg")
        standing_img = np.ones((400, 300, 3), dtype=np.uint8) * 255
        # Add person-like shape
        cv2.rectangle(standing_img, (120, 150), (180, 350), (0, 0, 0), -1)
        cv2.imwrite(self.standing_img_path, standing_img)
        
        # Test image 2: Horizontal lines (for camera movement)
        self.horizontal_img_path = os.path.join(self.temp_dir, "horizontal.jpg")
        horizontal_img = np.ones((400, 600, 3), dtype=np.uint8) * 200
        for y in range(50, 350, 50):
            cv2.line(horizontal_img, (0, y), (600, y), (100, 100, 100), 2)
        cv2.imwrite(self.horizontal_img_path, horizontal_img)
        
        # Test image 3: Diagonal lines (for tracking)
        self.diagonal_img_path = os.path.join(self.temp_dir, "diagonal.jpg")
        diagonal_img = np.ones((400, 600, 3), dtype=np.uint8) * 180
        cv2.line(diagonal_img, (0, 0), (600, 400), (255, 255, 255), 3)
        cv2.imwrite(self.diagonal_img_path, diagonal_img)
        
        # Test image 4: Green vegetation
        self.green_img_path = os.path.join(self.temp_dir, "green.jpg")
        green_img = np.zeros((400, 600, 3), dtype=np.uint8)
        green_img[:, :] = [50, 150, 50]  # Green color
        cv2.imwrite(self.green_img_path, green_img)
    
    def test_initialization(self):
        """Test MovementPredictor initialization"""
        self.assertIsNotNone(self.predictor.rules)
        self.assertIsInstance(self.predictor.rules, dict)
    
    def test_load_rules(self):
        """Test rule loading functionality"""
        rules = self.predictor._load_rules()
        self.assertIsInstance(rules, dict)
        # Should have categories from movement_prediction_rules.json
        self.assertIn('categories', rules)
    
    def test_analyze_standing_image(self):
        """Test analysis of standing person image"""
        analysis = self.predictor.analyze_image(self.standing_img_path)
        
        self.assertNotIn('error', analysis)
        self.assertIn('movement_predictions', analysis)
        self.assertIn('character_actions', analysis['movement_predictions'])
        self.assertIn('camera_movements', analysis['movement_predictions'])
        self.assertIn('environment_animations', analysis['movement_predictions'])
    
    def test_analyze_horizontal_lines(self):
        """Test analysis of horizontal lines image"""
        analysis = self.predictor.analyze_image(self.horizontal_img_path)
        
        self.assertNotIn('error', analysis)
        
        # Check for horizontal camera movement
        camera_moves = analysis['movement_predictions']['camera_movements']
        self.assertTrue(len(camera_moves) > 0)
        
        # Should include pan movement
        pan_moves = [m for m in camera_moves if 'pan' in m['type'].lower()]
        self.assertTrue(len(pan_moves) > 0)
    
    def test_analyze_diagonal_lines(self):
        """Test analysis of diagonal lines image"""
        analysis = self.predictor.analyze_image(self.diagonal_img_path)
        
        self.assertNotIn('error', analysis)
        
        # Check for tracking movement
        camera_moves = analysis['movement_predictions']['camera_movements']
        tracking_moves = [m for m in camera_moves if 'tracking' in m['type'].lower()]
        self.assertTrue(len(tracking_moves) > 0)
    
    def test_analyze_green_image(self):
        """Test analysis of green vegetation image"""
        analysis = self.predictor.analyze_image(self.green_img_path)
        
        self.assertNotIn('error', analysis)
        
        # Check for vegetation movement
        env_moves = analysis['movement_predictions']['environment_animations']
        vegetation_moves = [m for m in env_moves if 'vegetation' in m['element'].lower()]
        self.assertTrue(len(vegetation_moves) > 0)
    
    def test_character_movement_analysis(self):
        """Test character movement analysis specifically"""
        cv_image = cv2.imread(self.standing_img_path)
        character_moves = self.predictor._analyze_character_movement(cv_image)
        
        self.assertIsInstance(character_moves, list)
        if character_moves:
            move = character_moves[0]
            self.assertIn('pose_type', move)
            self.assertIn('predicted_action', move)
            self.assertIn('justification', move)
            self.assertIn('confidence', move)
            self.assertGreater(move['confidence'], 0)
    
    def test_camera_movement_analysis(self):
        """Test camera movement analysis specifically"""
        cv_image = cv2.imread(self.horizontal_img_path)
        camera_moves = self.predictor._analyze_camera_movement(cv_image)
        
        self.assertIsInstance(camera_moves, list)
        for move in camera_moves:
            self.assertIn('type', move)
            self.assertIn('direction', move)
            self.assertIn('justification', move)
            self.assertIn('confidence', move)
    
    def test_environmental_motion_analysis(self):
        """Test environmental motion analysis specifically"""
        cv_image = cv2.imread(self.green_img_path)
        env_moves = self.predictor._analyze_environmental_motion(cv_image)
        
        self.assertIsInstance(env_moves, list)
        for move in env_moves:
            self.assertIn('element', move)
            self.assertIn('motion', move)
            self.assertIn('justification', move)
            self.assertIn('confidence', move)
    
    def test_movement_justification_validation(self):
        """Test movement justification validation"""
        valid_movement = {
            'justification': 'natural gravity-based movement',
            'confidence': 0.8
        }
        
        invalid_movement = {
            'justification': '',
            'confidence': 0.5
        }
        
        context = {}
        
        self.assertTrue(self.predictor.validate_movement_justification(valid_movement, context))
        self.assertFalse(self.predictor.validate_movement_justification(invalid_movement, context))
    
    def test_generate_movement_prompts(self):
        """Test movement prompt generation"""
        analysis = self.predictor.analyze_image(self.standing_img_path)
        prompts = analysis.get('generated_prompts', [])
        
        self.assertIsInstance(prompts, list)
        self.assertTrue(len(prompts) > 0)
        
        # Should have combined prompt as first item
        if prompts:
            combined_prompt = prompts[0]
            self.assertIn('Cinematic sequence', combined_prompt)
    
    def test_save_analysis(self):
        """Test saving analysis results"""
        analysis = self.predictor.analyze_image(self.standing_img_path)
        output_path = os.path.join(self.temp_dir, "test_analysis.json")
        
        success = self.predictor.save_analysis(analysis, output_path)
        self.assertTrue(success)
        
        # Verify file was created and contains valid JSON
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, analysis)
    
    def test_get_cinematic_movement_prompt(self):
        """Test getting complete cinematic movement prompt"""
        prompt = self.predictor.get_cinematic_movement_prompt(self.standing_img_path)
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        self.assertIn('Cinematic sequence', prompt)
    
    def test_error_handling(self):
        """Test error handling for invalid image"""
        invalid_path = "/nonexistent/image.jpg"
        analysis = self.predictor.analyze_image(invalid_path)
        
        self.assertIn('error', analysis)
        self.assertIn('No such file', str(analysis['error']))
    
    def test_empty_image_handling(self):
        """Test handling of empty/minimal images"""
        empty_path = os.path.join(self.temp_dir, "empty.jpg")
        empty_img = np.ones((10, 10, 3), dtype=np.uint8) * 255
        cv2.imwrite(empty_path, empty_img)
        
        analysis = self.predictor.analyze_image(empty_path)
        
        # Should not crash, even with minimal content
        self.assertIsInstance(analysis, dict)
        self.assertIn('movement_predictions', analysis)

class TestMovementRules(unittest.TestCase):
    """Test movement prediction rules"""
    
    def test_rules_structure(self):
        """Test rules JSON structure"""
        rules_path = "/Users/arkadiuszfudali/mkr_notez/animatize-framework/configs/movement_prediction_rules.json"
        
        if os.path.exists(rules_path):
            with open(rules_path, 'r') as f:
                rules = json.load(f)
            
            self.assertIn('metadata', rules)
            self.assertIn('categories', rules)
            self.assertIn('rules', rules)
            self.assertIn('prompt_templates', rules)
            self.assertIn('validation_rules', rules)

if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)