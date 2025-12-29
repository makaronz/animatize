"""
Integration tests for Golden Set and Test Plan
"""

import pytest
import json
from pathlib import Path

from src.evaluation import (
    TestScenarioLibrary,
    MetricsEngine,
    GoldenSetManager,
    RegressionTestSuite,
    MovementType,
    DifficultyLevel
)


class TestGoldenSetIntegration:
    """Test complete golden set workflow"""

    def test_scenario_library_completeness(self):
        """Test that all 12+ test scenes are defined"""
        library = TestScenarioLibrary()

        # Verify we have all required scenario types
        assert len(library.scenarios) >= 25

        # Check portrait scenes
        assert library.get_scenario("TS_CHAR_004") is not None    # Facial expression
        assert library.get_scenario("TS_CHAR_005") is not None    # Head turn

        # Check landscape scenes
        assert library.get_scenario("TS_CAM_001") is not None     # Pan
        assert library.get_scenario("TS_LIGHT_001") is not None  # Day/night

        # Check multi-character
        assert library.get_scenario("TS_CHAR_001") is not None    # Walk
        assert library.get_scenario("TS_CHAR_002") is not None    # Sprint

        # Check dynamic motion
        assert library.get_scenario("TS_CHAR_006") is not None    # Rotation
        assert library.get_scenario("TS_CAM_006") is not None     # Tracking

        # Check lighting change
        assert library.get_scenario("TS_LIGHT_003") is not None   # Intensity
        assert library.get_scenario("TS_LIGHT_004") is not None   # Color temp

        # Check multi-shot sequences
        assert library.get_multi_scene_scenario("TS_MULTI_001") is not None
        assert library.get_multi_scene_scenario("TS_MULTI_002") is not None

        # Check edge cases
        assert library.get_scenario("TS_ENV_002") is not None    # Water
        assert library.get_scenario("TS_ENV_003") is not None    # Particles
        assert library.get_scenario("TS_ENV_004") is not None    # Weather

    def test_acceptance_criteria_defined(self):
        """Test that all scenarios have acceptance criteria"""
        library = TestScenarioLibrary()

        for scenario_id, scenario in library.scenarios.items():
            # All scenarios must have thresholds
            assert scenario.min_temporal_consistency > 0
            assert scenario.min_instruction_following > 0
            assert scenario.min_clip_similarity > 0
            assert scenario.min_ssim > 0
            assert scenario.min_perceptual_quality > 0

            # Performance thresholds
            assert scenario.max_latency_ms > 0
            assert scenario.min_throughput_fps > 0

    def test_golden_prompt_library_exists(self):
        """Test that golden prompt library is accessible"""
        prompt_library_path = Path("data/golden_prompts/prompt_library.json")
        assert prompt_library_path.exists()

        with open(prompt_library_path, 'r') as f:
            library = json.load(f)

        assert "version" in library
        assert "prompts" in library
        assert len(library["prompts"]) > 0

        # Check prompt structure
        for prompt_id, prompt in library["prompts"].items():
            assert "prompt_id" in prompt
            assert "category" in prompt
            assert "canonical_prompt" in prompt
            assert "tested_scenarios" in prompt
            assert "expert_validated" in prompt

    def test_golden_set_workflow(self, temp_dir, sample_test_video):
        """Test complete golden set workflow"""
        # Initialize managers
        golden_set = GoldenSetManager(temp_dir)
        library = TestScenarioLibrary()
        metrics_engine = MetricsEngine()

        # Get a scenario
        scenario = library.get_scenario("TS_CHAR_001")
        assert scenario is not None

        # Compute metrics
        results = metrics_engine.compute_all(
            video_path=sample_test_video,
            reference_data={"prompt": scenario.prompt}
        )

        metric_results = {name: r.score for name, r in results.items()}

        # Add to golden set
        ref_id = golden_set.add_reference(
            scenario_id="TS_CHAR_001",
            video_path=sample_test_video,
            model_version="v1.0.0-test",
            metric_results=metric_results,
            expert_approved=True,
            approver="test@example.com"
        )

        assert ref_id is not None

        # Retrieve reference
        reference = golden_set.get_reference(ref_id)
        assert reference is not None
        assert reference.expert_approved is True
        assert reference.metric_results is not None

    def test_regression_workflow(self, temp_dir, sample_test_video):
        """Test regression testing workflow"""
        # Setup
        golden_set = GoldenSetManager(temp_dir)
        library = TestScenarioLibrary()
        metrics_engine = MetricsEngine()

        # Add baseline reference
        golden_set.add_reference(
            scenario_id="TS_CHAR_001",
            video_path=sample_test_video,
            model_version="v1.0.0",
            metric_results={
                "temporal_consistency": 0.89,
                "ssim": 0.82,
                "perceptual_quality": 0.85
            },
            expert_approved=True,
            approver="test@example.com"
        )

        # Create regression suite
        regression_suite = RegressionTestSuite(
            golden_set_manager=golden_set,
            metrics_engine=metrics_engine,
            scenario_library=library
        )

        # Run regression test
        result = regression_suite.run_regression_test(
            test_video_path=sample_test_video,
            scenario_id="TS_CHAR_001",
            test_version="v1.1.0",
            baseline_version="v1.0.0"
        )

        assert result is not None
        assert result.scenario_id == "TS_CHAR_001"
        assert result.test_version == "v1.1.0"
        assert result.baseline_version == "v1.0.0"

    def test_coverage_summary(self):
        """Test that coverage summary includes all scene types"""
        library = TestScenarioLibrary()
        coverage = library.get_coverage_summary()

        # Check all movement types are covered
        movement_types = coverage["by_movement_type"]

        assert movement_types.get("character_walk", 0) > 0
        assert movement_types.get("character_facial", 0) > 0
        assert movement_types.get("camera_pan", 0) > 0
        assert movement_types.get("lighting_day_night", 0) > 0
        assert movement_types.get("environment_water", 0) > 0

        # Check difficulty distribution
        difficulty = coverage["by_difficulty"]
        assert difficulty.get("basic", 0) > 0
        assert difficulty.get("intermediate", 0) > 0
        assert difficulty.get("advanced", 0) > 0
        assert difficulty.get("expert", 0) > 0


class TestMetricsCompleteness:
    """Test that all required metrics are implemented"""

    def test_temporal_metrics_available(self):
        """Test temporal consistency metrics are available"""
        engine = MetricsEngine()

        assert "temporal_consistency" in engine.metrics
        assert "optical_flow_consistency" in engine.metrics

    def test_quality_metrics_available(self):
        """Test quality metrics are available"""
        engine = MetricsEngine()

        assert "ssim" in engine.metrics
        assert "perceptual_quality" in engine.metrics

    def test_semantic_metrics_available(self):
        """Test semantic alignment metrics are available"""
        engine = MetricsEngine()

        assert "clip_similarity" in engine.metrics
        assert "instruction_following" in engine.metrics

    def test_metric_thresholds_configurable(self):
        """Test that metric thresholds can be updated"""
        engine = MetricsEngine()

        # Update thresholds
        engine.update_thresholds({
            "temporal_consistency": 0.95,
            "ssim": 0.90
        })

        assert engine.metrics["temporal_consistency"].threshold == 0.95
        assert engine.metrics["ssim"].threshold == 0.90


class TestScenarioCategorization:
    """Test scenario categorization and filtering"""

    def test_filter_by_movement_type(self):
        """Test filtering scenarios by movement type"""
        library = TestScenarioLibrary()

        char_scenarios = library.get_scenarios_by_type(MovementType.CHARACTER_WALK)
        assert len(char_scenarios) > 0
        assert all(s.movement_type == MovementType.CHARACTER_WALK for s in char_scenarios)

    def test_filter_by_difficulty(self):
        """Test filtering scenarios by difficulty"""
        library = TestScenarioLibrary()

        expert_scenarios = library.get_scenarios_by_difficulty(DifficultyLevel.EXPERT)
        assert len(expert_scenarios) > 0
        assert all(s.difficulty == DifficultyLevel.EXPERT for s in expert_scenarios)

    def test_multi_scene_scenarios(self):
        """Test multi-scene scenario structure"""
        library = TestScenarioLibrary()

        multi_scene = library.get_multi_scene_scenario("TS_MULTI_001")
        assert multi_scene is not None
        assert len(multi_scene.scenes) >= 3

        # Check continuity thresholds
        assert multi_scene.character_consistency_threshold >= 0.95
        assert multi_scene.lighting_consistency_threshold >= 0.80
        assert multi_scene.style_consistency_threshold >= 0.90


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflow"""

    def test_full_evaluation_pipeline(self, temp_dir, sample_test_video):
        """Test complete evaluation pipeline from scenario to report"""
        from src.evaluation import EvaluationHarness

        harness = EvaluationHarness(
            golden_set_path=temp_dir,
            output_dir=temp_dir
        )

        # Evaluate video
        result = harness.evaluate_video(
            video_path=sample_test_video,
            scenario_id="TS_CHAR_001",
            model_version="v1.0.0-test",
            save_to_golden_set=True,
            expert_approved=True
        )

        assert "scenario_id" in result
        assert "metrics" in result
        assert "summary" in result
        assert "golden_reference_id" in result

    def test_ci_integration(self, temp_dir, sample_test_video):
        """Test CI integration workflow"""
        from src.evaluation.ci_integration import CIIntegration, CITestConfig

        ci = CIIntegration(golden_set_path=temp_dir)

        # Create test manifest
        test_videos = {
            "TS_CHAR_001": sample_test_video,
        }

        config = CITestConfig(
            test_version="v1.0.0-ci",
            baseline_version="v0.9.0",
            max_failures=0,
            max_degradations=2,
            min_pass_rate=80.0
        )

        # Note: This will fail without baseline, but tests the interface
        results = ci.run_ci_tests(test_videos, config)

        assert "status" in results
        assert "summary" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
