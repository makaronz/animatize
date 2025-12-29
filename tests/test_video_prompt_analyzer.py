"""
Unit tests for Video Prompt Analyzer and Generator
"""

import unittest
from src.analyzers.video_prompt_analyzer import (
    VideoPromptAnalyzer,
    ModelType,
    PromptStructure,
    CameraMotion,
    TemporalConsistencyConfig,
    SceneTransition,
)
from src.generators.video_prompt_generator import (
    VideoPromptCompiler,
    VideoControlParameters,
    DeterminismConfig,
    PromptVersion,
    CinematicRuleApplication,
    CompiledPrompt,
    VideoGenerationRequest,
)


class TestTemporalConsistencyConfig(unittest.TestCase):
    """Test TemporalConsistencyConfig validation"""

    def test_valid_config(self):
        """Test valid configuration"""
        config = TemporalConsistencyConfig(
            seed=42, temporal_weight=0.8, motion_strength=0.5, frame_interpolation=24, guidance_scale=7.5
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
        camera = CameraMotion(type="dolly", speed="slow", direction="in", focal_length=50)
        prompt = camera.to_prompt_string()
        self.assertIn("dolly", prompt.lower())
        self.assertIn("in", prompt.lower())
        self.assertIn("slow", prompt.lower())
        self.assertIn("50mm", prompt.lower())


class TestPromptStructure(unittest.TestCase):
    """Test PromptStructure generation"""

    def setUp(self):
        """Set up test prompt structure"""
        self.camera = CameraMotion(type="dolly", speed="slow", direction="in", focal_length=50)
        self.structure = PromptStructure(
            subject="A young woman in a red dress",
            action="walking through",
            environment="a misty forest",
            lighting="golden hour sunlight",
            atmosphere="ethereal and serene",
            camera=self.camera,
            style="cinematic",
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
        params = {"aspect_ratio": "16:9", "duration": 5, "camera_movement": "dolly", "style": "cinematic"}
        is_valid, messages = self.analyzer.validate_parameters(ModelType.KLING, params)
        self.assertTrue(is_valid)

    def test_validate_parameters_invalid(self):
        """Test parameter validation with invalid params"""
        params = {"aspect_ratio": "32:9", "camera_movement": "invalid_type"}  # Invalid  # Invalid
        is_valid, messages = self.analyzer.validate_parameters(ModelType.KLING, params)
        self.assertFalse(is_valid)
        self.assertGreater(len(messages), 0)

    def test_optimize_for_temporal_consistency(self):
        """Test temporal consistency optimization"""
        params = {"motion_strength": 0.9}  # Too high
        optimized = self.analyzer.optimize_for_temporal_consistency(ModelType.WAN, params)
        self.assertIn("seed", optimized)
        self.assertIn("temporal_consistency", optimized)
        self.assertLessEqual(optimized.get("motion_strength", 0), 0.7)

    def test_analyze_prompt_quality(self):
        """Test prompt quality analysis"""
        prompt = (
            "A young woman in a red dress walks through a misty forest at golden hour. "
            "Camera slowly dollies in. Cinematic style."
        )
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
                style="cinematic",
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


class TestVideoControlParameters(unittest.TestCase):
    """Test VideoControlParameters validation and functionality"""

    def test_valid_control_params(self):
        """Test valid control parameters"""
        camera = CameraMotion(type="dolly", speed="slow", direction="in")
        params = VideoControlParameters(
            camera_motion=camera, duration_seconds=8.0, fps=24, shot_type="medium", motion_strength=0.5
        )
        is_valid, errors = params.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_invalid_duration(self):
        """Test invalid duration"""
        params = VideoControlParameters(duration_seconds=100.0)
        is_valid, errors = params.validate()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_invalid_fps(self):
        """Test invalid fps"""
        params = VideoControlParameters(fps=45)
        is_valid, errors = params.validate()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_invalid_shot_type(self):
        """Test invalid shot type"""
        params = VideoControlParameters(shot_type="invalid")
        is_valid, errors = params.validate()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_to_dict(self):
        """Test conversion to dictionary"""
        camera = CameraMotion(type="pan", speed="medium")
        params = VideoControlParameters(camera_motion=camera, fps=30)
        data = params.to_dict()
        self.assertIn("camera_motion", data)
        self.assertIn("fps", data)
        self.assertEqual(data["fps"], 30)


class TestDeterminismConfig(unittest.TestCase):
    """Test DeterminismConfig seed management"""

    def test_fixed_seed(self):
        """Test fixed seed generation"""
        config = DeterminismConfig(seed=42, enable_seed_management=True)
        seed = config.generate_seed(scene_index=0)
        self.assertEqual(seed, 42)

    def test_incremental_seed(self):
        """Test incremental seed for multiple scenes"""
        config = DeterminismConfig(seed=100, seed_increment_per_scene=10)
        seed1 = config.generate_seed(scene_index=0)
        seed2 = config.generate_seed(scene_index=1)
        seed3 = config.generate_seed(scene_index=2)
        self.assertEqual(seed1, 100)
        self.assertEqual(seed2, 110)
        self.assertEqual(seed3, 120)

    def test_hash_based_seed(self):
        """Test hash-based seed generation"""
        config = DeterminismConfig(use_hash_based_seed=True)
        prompt = "A warrior stands on a cliff"
        seed = config.generate_seed(prompt_text=prompt)
        self.assertIsInstance(seed, int)
        self.assertGreater(seed, 0)

        # Same prompt should generate same seed
        seed2 = config.generate_seed(prompt_text=prompt)
        self.assertEqual(seed, seed2)

    def test_default_seed(self):
        """Test default seed fallback"""
        config = DeterminismConfig(enable_seed_management=True)
        seed = config.generate_seed()
        self.assertEqual(seed, 42)


class TestPromptVersion(unittest.TestCase):
    """Test PromptVersion tracking"""

    def test_version_creation(self):
        """Test version creation with defaults"""
        version = PromptVersion(model_type="kling")
        self.assertEqual(version.prompt_version, "1.0.0")
        self.assertEqual(version.schema_version, "2.0.0")
        self.assertIsNotNone(version.created_at)

    def test_version_to_dict(self):
        """Test conversion to dictionary"""
        version = PromptVersion(prompt_version="1.5.0", model_type="sora2")
        data = version.to_dict()
        self.assertIn("prompt_version", data)
        self.assertIn("schema_version", data)
        self.assertEqual(data["prompt_version"], "1.5.0")


class TestCinematicRuleApplication(unittest.TestCase):
    """Test CinematicRuleApplication tracking"""

    def test_rule_application(self):
        """Test rule application tracking"""
        rules = CinematicRuleApplication(
            rule_ids=["movement_001", "movement_002", "movement_003"],
            rule_names=["Pose-to-Action", "Camera Flow", "Physics-Based"],
            enhancements={"camera": "enhanced camera motion"},
            total_rules_applied=3,
        )
        self.assertEqual(rules.total_rules_applied, 3)
        self.assertEqual(len(rules.rule_ids), 3)
        self.assertIn("camera", rules.enhancements)

    def test_to_dict(self):
        """Test conversion to dictionary"""
        rules = CinematicRuleApplication(rule_ids=["movement_001"], total_rules_applied=1)
        data = rules.to_dict()
        self.assertIn("rule_ids", data)
        self.assertIn("total_rules_applied", data)


class TestVideoPromptCompiler(unittest.TestCase):
    """Test VideoPromptCompiler functionality"""

    def setUp(self):
        """Set up compiler"""
        self.compiler = VideoPromptCompiler()

    def test_parse_director_intent(self):
        """Test parsing director intent"""
        intent = "A young woman in a red dress walks through a misty forest at golden hour. Camera dollies in slowly."
        components = self.compiler.parse_director_intent(intent)
        self.assertIn("subject", components)
        self.assertIn("action", components)
        self.assertIn("environment", components)
        self.assertIn("camera", components)

    def test_infer_shot_type(self):
        """Test inferring shot type from description"""
        wide = self.compiler.infer_shot_type("wide establishing shot of landscape", "cinematic")
        self.assertEqual(wide, "wide")

        closeup = self.compiler.infer_shot_type("close-up of her face showing emotion", "cinematic")
        self.assertEqual(closeup, "close-up")

        medium = self.compiler.infer_shot_type("character walking through forest", "cinematic")
        self.assertEqual(medium, "medium")

    def test_infer_camera_motion(self):
        """Test inferring camera motion"""
        dolly = self.compiler.infer_camera_motion("camera dolly in slowly", "cinematic")
        self.assertEqual(dolly.type, "dolly")
        self.assertEqual(dolly.direction, "in")

        pan = self.compiler.infer_camera_motion("camera pans left", "cinematic")
        self.assertEqual(pan.type, "pan")
        self.assertEqual(pan.direction, "left")

    def test_compile_video_prompt(self):
        """Test complete prompt compilation"""
        request = VideoGenerationRequest(
            model_type=ModelType.KLING,
            scene_description="A warrior stands on a cliff at sunrise",
            duration=5.0,
            style="cinematic",
            temporal_consistency_priority="high",
        )

        compiled = self.compiler.compile_video_prompt(request)

        self.assertIsInstance(compiled, CompiledPrompt)
        self.assertIn("warrior", compiled.prompt_text.lower())
        self.assertIsNotNone(compiled.control_parameters)
        self.assertIsNotNone(compiled.determinism_config)
        self.assertIsNotNone(compiled.version)
        self.assertIsNotNone(compiled.cinematic_rules)

    def test_compile_with_control_parameters(self):
        """Test compilation with explicit control parameters"""
        camera = CameraMotion(type="dolly", speed="slow", direction="in", focal_length=50)
        controls = VideoControlParameters(
            camera_motion=camera, duration_seconds=8.0, fps=24, shot_type="medium", motion_strength=0.4
        )

        request = VideoGenerationRequest(
            model_type=ModelType.SORA2, scene_description="A woman walks through a forest", control_parameters=controls
        )

        compiled = self.compiler.compile_video_prompt(request)
        self.assertEqual(compiled.control_parameters.fps, 24)
        self.assertEqual(compiled.control_parameters.shot_type, "medium")
        self.assertEqual(compiled.control_parameters.motion_strength, 0.4)

    def test_compile_with_determinism(self):
        """Test compilation with determinism config"""
        determinism = DeterminismConfig(seed=12345, enable_seed_management=True, seed_increment_per_scene=100)

        request = VideoGenerationRequest(
            model_type=ModelType.KLING, scene_description="Test scene", determinism_config=determinism
        )

        compiled = self.compiler.compile_video_prompt(request, scene_index=0)
        self.assertEqual(compiled.temporal_config.seed, 12345)

        compiled2 = self.compiler.compile_video_prompt(request, scene_index=1)
        self.assertEqual(compiled2.temporal_config.seed, 12445)

    def test_apply_cinematic_rules(self):
        """Test cinematic rules application"""
        intent = self.compiler.parse_director_intent("A character walks through a forest with camera tracking")
        controls = VideoControlParameters(camera_motion=CameraMotion(type="dolly", speed="slow"), shot_type="medium")

        rules = self.compiler.apply_cinematic_rules_to_intent(intent, controls)

        self.assertIsInstance(rules, CinematicRuleApplication)
        self.assertGreater(rules.total_rules_applied, 0)
        self.assertGreater(len(rules.rule_ids), 0)

    def test_compile_model_parameters(self):
        """Test model-specific parameter compilation"""
        request = VideoGenerationRequest(model_type=ModelType.KLING, scene_description="Test scene", duration=5.0)

        compiled = self.compiler.compile_video_prompt(request)
        params = self.compiler.compile_model_parameters(compiled)

        self.assertIn("duration", params)
        self.assertIn("fps", params)
        self.assertIn("shot_type", params)
        self.assertEqual(params["duration"], 5.0)

    def test_compile_multi_scene_prompts(self):
        """Test multi-scene prompt compilation"""
        scenes = ["A warrior stands on a cliff", "The warrior draws their sword", "The warrior charges forward"]

        result = self.compiler.compile_multi_scene_prompts(scenes, ModelType.SORA2)

        self.assertEqual(result["total_scenes"], 3)
        self.assertIn("version", result)
        self.assertIn("coherence_strategy", result)
        self.assertIn("scenes", result)
        self.assertEqual(len(result["scenes"]), 3)

        # Check seed progression
        seed1 = result["scenes"][0]["compiled_prompt"]["temporal_config"]["seed"]
        seed2 = result["scenes"][1]["compiled_prompt"]["temporal_config"]["seed"]
        self.assertEqual(seed2, seed1 + 1)

    def test_versioning(self):
        """Test version tracking in compiled prompts"""
        request = VideoGenerationRequest(model_type=ModelType.KLING, scene_description="Test scene")

        compiled = self.compiler.compile_video_prompt(request)

        self.assertEqual(compiled.version.schema_version, "2.0.0")
        self.assertEqual(compiled.version.generator_version, "2.0.0")
        self.assertIsNotNone(compiled.version.created_at)

    def test_compiled_prompt_export(self):
        """Test exporting compiled prompt to dict"""
        request = VideoGenerationRequest(model_type=ModelType.KLING, scene_description="Test scene", duration=5.0)

        compiled = self.compiler.compile_video_prompt(request)
        data = compiled.to_dict()

        self.assertIn("prompt_text", data)
        self.assertIn("model_type", data)
        self.assertIn("control_parameters", data)
        self.assertIn("determinism", data)
        self.assertIn("version", data)
        self.assertIn("cinematic_rules", data)
        self.assertIn("temporal_config", data)
        self.assertIn("metadata", data)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with legacy VideoPromptGenerator"""

    def setUp(self):
        """Set up generator"""
        from src.generators.video_prompt_generator import VideoPromptGenerator

        self.generator = VideoPromptGenerator()

    def test_legacy_generate_prompt(self):
        """Test legacy generate_prompt method"""
        request = VideoGenerationRequest(
            model_type=ModelType.KLING, scene_description="A woman walks through a forest", duration=5.0
        )

        prompt = self.generator.generate_prompt(request)
        self.assertIsInstance(prompt, str)
        self.assertIn("woman", prompt.lower())

    def test_legacy_generate_parameters(self):
        """Test legacy generate_model_parameters method"""
        request = VideoGenerationRequest(model_type=ModelType.KLING, scene_description="Test scene", duration=5.0)

        params = self.generator.generate_model_parameters(request)
        self.assertIsInstance(params, dict)
        self.assertIn("duration", params)

    def test_legacy_multi_scene(self):
        """Test legacy multi-scene generation"""
        scenes = ["Scene 1", "Scene 2", "Scene 3"]
        result = self.generator.generate_multi_scene_prompts(scenes, ModelType.KLING)

        self.assertIn("total_scenes", result)
        self.assertEqual(result["total_scenes"], 3)


if __name__ == "__main__":
    unittest.main()
