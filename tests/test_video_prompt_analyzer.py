"""
Unit tests for Video Prompt Analyzer
"""

import unittest
import json
from src.analyzers.video_prompt_analyzer import (
    VideoPromptAnalyzer,
    ModelType,
    PromptStructure,
    CameraMotion,
    TemporalConsistencyConfig,
    SceneTransition
)


class TestTemporalConsistencyConfig(unittest.TestCase):
    """Test TemporalConsistencyConfig validation"""
    
    def test_valid_config(self):
        """Test valid configuration"""
        config = TemporalConsistencyConfig(
            seed=42,
            temporal_weight=0.8,
            motion_strength=0.5,
            frame_interpolation=24,
            guidance_scale=7.5
        )
        is_valid, errors = config.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_temporal_weight(self):
        """Test invalid temporal_weight"""
        config = TemporalConsistencyConfig(temporal_weight=1.5)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_invalid_frame_interpolation(self):
        """Test invalid frame_interpolation"""
        config = TemporalConsistencyConfig(frame_interpolation=45)
        is_valid, errors = config.validate()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestCameraMotion(unittest.TestCase):
    """Test CameraMotion functionality"""
    
    def test_static_camera(self):
        """Test static camera prompt"""
        camera = CameraMotion(type="static")
        prompt = camera.to_prompt_string()
        self.assertIn("static", prompt.lower())
        self.assertIn("no movement", prompt.lower())
    
    def test_dolly_camera(self):
        """Test dolly camera with direction"""
        camera = CameraMotion(
            type="dolly",
            speed="slow",
            direction="in",
            focal_length=50
        )
        prompt = camera.to_prompt_string()
        self.assertIn("dolly", prompt.lower())
        self.assertIn("in", prompt.lower())
        self.assertIn("slow", prompt.lower())
        self.assertIn("50mm", prompt.lower())


class TestPromptStructure(unittest.TestCase):
    """Test PromptStructure generation"""
    
    def setUp(self):
        """Set up test prompt structure"""
        self.camera = CameraMotion(
            type="dolly",
            speed="slow",
            direction="in",
            focal_length=50
        )
        self.structure = PromptStructure(
            subject="A young woman in a red dress",
            action="walking through",
            environment="a misty forest",
            lighting="golden hour sunlight",
            atmosphere="ethereal and serene",
            camera=self.camera,
            style="cinematic"
        )
    
    def test_kling_prompt(self):
        """Test Kling-specific prompt format"""
        prompt = self.structure.to_prompt(ModelType.KLING)
        self.assertIn("young woman", prompt.lower())
        self.assertIn("red dress", prompt.lower())
        self.assertIn("forest", prompt.lower())
        self.assertIn("camera", prompt.lower())
    
    def test_wan_prompt(self):
        """Test WAN-specific prompt format"""
        prompt = self.structure.to_prompt(ModelType.WAN)
        self.assertIn("->", prompt)
        self.assertIn("style:", prompt.lower())
    
    def test_sora2_prompt(self):
        """Test Sora 2 prompt format"""
        prompt = self.structure.to_prompt(ModelType.SORA2)
        self.assertIn("scene:", prompt.lower())
        self.assertIn("lighting:", prompt.lower())


class TestVideoPromptAnalyzer(unittest.TestCase):
    """Test VideoPromptAnalyzer functionality"""
    
    def setUp(self):
        """Set up analyzer"""
        self.analyzer = VideoPromptAnalyzer()
    
    def test_get_model_info(self):
        """Test retrieving model information"""
        info = self.analyzer.get_model_info(ModelType.KLING)
        self.assertIsNotNone(info)
        self.assertIn("provider", info)
        self.assertIn("max_duration", info)
        self.assertIn("controllability_parameters", info)
    
    def test_get_temporal_critical_params(self):
        """Test identifying temporal critical parameters"""
        critical = self.analyzer.get_temporal_critical_params(ModelType.KLING)
        self.assertIsInstance(critical, list)
        self.assertGreater(len(critical), 0)
        self.assertIn("camera_movement", critical)
    
    def test_validate_parameters_valid(self):
        """Test parameter validation with valid params"""
        params = {
            "aspect_ratio": "16:9",
            "duration": 5,
            "camera_movement": "dolly",
            "style": "cinematic"
        }
        is_valid, messages = self.analyzer.validate_parameters(ModelType.KLING, params)
        self.assertTrue(is_valid)
    
    def test_validate_parameters_invalid(self):
        """Test parameter validation with invalid params"""
        params = {
            "aspect_ratio": "32:9",  # Invalid
            "camera_movement": "invalid_type"  # Invalid
        }
        is_valid, messages = self.analyzer.validate_parameters(ModelType.KLING, params)
        self.assertFalse(is_valid)
        self.assertGreater(len(messages), 0)
    
    def test_optimize_for_temporal_consistency(self):
        """Test temporal consistency optimization"""
        params = {
            "motion_strength": 0.9  # Too high
        }
        optimized = self.analyzer.optimize_for_temporal_consistency(
            ModelType.WAN,
            params
        )
        self.assertIn("seed", optimized)
        self.assertIn("temporal_consistency", optimized)
        self.assertLessEqual(optimized.get("motion_strength", 0), 0.7)
    
    def test_analyze_prompt_quality(self):
        """Test prompt quality analysis"""
        prompt = "A young woman in a red dress walks through a misty forest at golden hour. Camera slowly dollies in. Cinematic style."
        quality = self.analyzer.analyze_prompt_quality(prompt, ModelType.KLING)
        
        self.assertIn("score", quality)
        self.assertGreater(quality["score"], 50)
        self.assertIn("completeness", quality)
        self.assertIn("suggestions", quality)
    
    def test_generate_multi_scene_plan(self):
        """Test multi-scene coherence planning"""
        camera = CameraMotion(type="dolly", speed="slow")
        scenes = [
            PromptStructure(
                subject="Character A",
                action="walking",
                environment="forest",
                lighting="golden hour",
                atmosphere="serene",
                camera=camera,
                style="cinematic"
            )
            for _ in range(3)
        ]
        
        plan = self.analyzer.generate_multi_scene_plan(scenes, ModelType.KLING)
        
        self.assertEqual(plan["total_scenes"], 3)
        self.assertIn("consistency_checks", plan)
        self.assertIn("character_consistency", plan["consistency_checks"])
        self.assertIn("scene_prompts", plan)
    
    def test_map_to_cinematic_rules(self):
        """Test mapping to ANIMAtiZE rules"""
        camera = CameraMotion(type="dolly", speed="slow", direction="in")
        rules = self.analyzer.map_to_cinematic_rules(camera, {})
        
        self.assertIsInstance(rules, list)
        self.assertGreater(len(rules), 0)
        # Dolly should map to emotional framing
        self.assertTrue(any("Emotional Framing" in rule for rule in rules))


class TestSceneTransition(unittest.TestCase):
    """Test SceneTransition functionality"""
    
    def test_fade_transition(self):
        """Test fade transition"""
        transition = SceneTransition(type="fade", duration=0.5)
        prompt = transition.to_prompt_string()
        self.assertIn("fade", prompt.lower())
        self.assertIn("0.5", prompt)
    
    def test_cut_transition(self):
        """Test cut transition"""
        transition = SceneTransition(type="cut", duration=0.0)
        prompt = transition.to_prompt_string()
        self.assertIn("cut", prompt.lower())


if __name__ == "__main__":
    unittest.main()
