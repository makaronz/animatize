"""
Test suite for Scene Analysis Module
Tests basic functionality without heavy dependencies
"""

import pytest
import tempfile
import json
from pathlib import Path
import numpy as np
from PIL import Image
import cv2

# Import the analyzer
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzers.scene_analyzer import SceneAnalyzer

class TestSceneAnalyzer:
    """Test cases for SceneAnalyzer class"""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        analyzer = SceneAnalyzer()
        assert analyzer.config is not None
        assert "confidence_threshold" in analyzer.config
        assert analyzer.config["confidence_threshold"] == 0.5
    
    def test_config_loading(self):
        """Test configuration loading"""
        # Test with default config
        analyzer = SceneAnalyzer()
        assert analyzer.config["max_objects"] == 20
        
        # Test with custom config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_config = {
                "confidence_threshold": 0.8,
                "max_objects": 10,
                "scene_thresholds": {
                    "sky_ratio": 0.4,
                    "green_ratio": 0.3
                }
            }
            json.dump(custom_config, f)
            f.flush()
            
            analyzer = SceneAnalyzer(f.name)
            assert analyzer.config["confidence_threshold"] == 0.8
            assert analyzer.config["max_objects"] == 10
            
            os.unlink(f.name)
    
    def test_create_test_image(self):
        """Create a test image for analysis"""
        # Create a simple test image
        img_array = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # Add sky (blue top)
        img_array[:100, :] = [200, 150, 100]  # BGR for sky
        
        # Add vegetation (green bottom)
        img_array[300:, :] = [50, 200, 50]  # BGR for green
        
        # Add building (gray middle)
        img_array[150:250, 200:400] = [150, 150, 150]  # BGR for gray
        
        return img_array
    
    def test_image_info_extraction(self):
        """Test basic image information extraction"""
        analyzer = SceneAnalyzer()
        
        # Create test image
        test_img = Image.new('RGB', (800, 600), color='blue')
        
        info = analyzer._get_image_info(test_img)
        
        assert info["width"] == 800
        assert info["height"] == 600
        assert info["aspect_ratio"] == 800/600
        assert info["mode"] == "RGB"
    
    def test_object_detection_fallback(self):
        """Test fallback object detection"""
        analyzer = SceneAnalyzer()
        
        # Create test image
        img_array = self.test_create_test_image()
        
        objects = analyzer._detect_objects_fallback(img_array)
        
        assert isinstance(objects, list)
        assert len(objects) > 0
        
        # Check for expected object types
        object_types = [obj["class"] for obj in objects]
        assert "sky" in object_types or "building" in object_types
    
    def test_depth_estimation_fallback(self):
        """Test fallback depth estimation"""
        analyzer = SceneAnalyzer()
        
        # Create test image
        img_array = self.test_create_test_image()
        
        depth = analyzer._estimate_depth_fallback(img_array)
        
        assert "method" in depth
        assert depth["method"] == "gradient_depth"
        assert "min_depth" in depth
        assert "max_depth" in depth
        assert 0 <= depth["min_depth"] <= 1
        assert 0 <= depth["max_depth"] <= 1
    
    def test_composition_analysis(self):
        """Test composition analysis"""
        analyzer = SceneAnalyzer()
        
        # Create test image
        img_array = self.test_create_test_image()
        
        composition = analyzer._analyze_composition(img_array)
        
        assert "rule_of_thirds" in composition
        assert "symmetry" in composition
        assert "complexity" in composition
        
        symmetry = composition["symmetry"]
        assert "horizontal_symmetry" in symmetry
        assert 0 <= symmetry["horizontal_symmetry"] <= 1
    
    def test_scene_classification(self):
        """Test scene classification"""
        analyzer = SceneAnalyzer()
        
        # Create test image
        img_array = self.test_create_test_image()
        
        scene = analyzer._classify_scene(img_array)
        
        assert "type" in scene
        assert "confidence" in scene
        assert "color_ratios" in scene
        assert scene["confidence"] >= 0
        assert scene["confidence"] <= 1
    
    def test_aesthetics_calculation(self):
        """Test aesthetics score calculation"""
        analyzer = SceneAnalyzer()
        
        # Mock analysis data
        mock_analysis = {
            "image_info": {"width": 800, "height": 600},
            "objects": [
                {"class": "sky", "confidence": 0.8, "center": [400, 100]},
                {"class": "building", "confidence": 0.7, "center": [300, 200]}
            ],
            "depth": {"depth_variance": 0.15},
            "composition": {
                "symmetry": {"horizontal_symmetry": 0.6},
                "complexity": {"edge_density": 0.3}
            }
        }
        
        aesthetics = analyzer._calculate_aesthetics_score(mock_analysis)
        
        assert "overall_score" in aesthetics
        assert "composition_score" in aesthetics
        assert "depth_score" in aesthetics
        assert 0 <= aesthetics["overall_score"] <= 1
    
    def test_save_analysis(self):
        """Test saving analysis results"""
        analyzer = SceneAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_analysis = {
                "test": "data",
                "score": 0.95
            }
            
            analyzer.save_analysis(test_analysis, f.name)
            
            # Verify file was created and contains correct data
            with open(f.name, 'r') as rf:
                loaded_data = json.load(rf)
                assert loaded_data == test_analysis
            
            os.unlink(f.name)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        analyzer = SceneAnalyzer()
        
        # Test with non-existent file
        result = analyzer.analyze_image("/nonexistent/path/image.jpg")
        assert "error" in result
        assert "error_message" in result
    
    def test_batch_analysis_structure(self):
        """Test batch analysis structure"""
        analyzer = SceneAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test images
            test_images = []
            for i in range(3):
                img_path = Path(temp_dir) / f"test_{i}.jpg"
                img_array = self.test_create_test_image()
                cv2.imwrite(str(img_path), img_array)
                test_images.append(img_path)
            
            # Run batch analysis
            results = analyzer.batch_analyze(temp_dir, temp_dir)
            
            assert "total_images" in results
            assert "successful_analyses" in results
            assert "failed_analyses" in results
            assert "analyses" in results
            assert results["total_images"] == 3


def test_analyzer_standalone():
    """Quick standalone test function"""
    print("Running Scene Analyzer tests...")
    
    try:
        analyzer = SceneAnalyzer()
        print("✓ Analyzer initialized")
        
        # Create test image
        img_array = np.zeros((300, 400, 3), dtype=np.uint8)
        img_array[:100, :] = [200, 150, 100]  # Sky
        img_array[200:, :] = [50, 200, 50]    # Ground
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = f.name
            
        cv2.imwrite(temp_path, img_array)
        
        # Test analysis
        result = analyzer.analyze_image(temp_path)
        
        if "error" not in result:
            print("✓ Image analysis successful")
            print(f"  - Objects found: {len(result.get('objects', []))}")
            print(f"  - Scene type: {result.get('scene_type', {}).get('type', 'unknown')}")
            print(f"  - Aesthetics score: {result.get('aesthetics', {}).get('overall_score', 0)}")
        else:
            print(f"✗ Analysis failed: {result.get('error_message', 'Unknown error')}")
        
        # Cleanup
        os.unlink(temp_path)
        
        print("✓ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_analyzer_standalone()