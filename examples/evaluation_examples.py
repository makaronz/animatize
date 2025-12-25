"""
Example Usage of Video Generation Evaluation System

This script demonstrates how to use the evaluation harness for:
1. Evaluating individual videos
2. Running regression tests
3. Comparing models
4. Performance benchmarking
5. CI/CD integration
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import (
    EvaluationHarness,
    TestScenarioLibrary,
    MovementType,
    DifficultyLevel
)


def example_1_evaluate_single_video():
    """Example: Evaluate a single video"""
    print("=" * 60)
    print("Example 1: Evaluate Single Video")
    print("=" * 60)
    
    harness = EvaluationHarness(
        golden_set_path="data/golden_set",
        output_dir="evaluation_results"
    )
    
    # Evaluate a video against a test scenario
    result = harness.evaluate_video(
        video_path="path/to/test_video.mp4",
        scenario_id="TS_CHAR_001",  # Natural Walking scenario
        model_version="v1.0.0",
        save_to_golden_set=False,
        expert_approved=False
    )
    
    print(f"\nScenario: {result['scenario_name']}")
    print(f"All metrics passed: {result['all_metrics_passed']}")
    print(f"\nMetrics:")
    for metric_name, metric_data in result['metrics'].items():
        status = "✅" if metric_data['passed'] else "❌"
        print(f"  {status} {metric_name}: {metric_data['score']:.3f} (threshold: {metric_data['threshold']:.3f})")
    
    return result


def example_2_evaluate_scenario_suite():
    """Example: Evaluate multiple scenarios"""
    print("\n" + "=" * 60)
    print("Example 2: Evaluate Scenario Suite")
    print("=" * 60)
    
    harness = EvaluationHarness()
    
    # Prepare multiple test videos
    test_videos = {
        "TS_CHAR_001": "path/to/walking_video.mp4",
        "TS_CHAR_002": "path/to/running_video.mp4",
        "TS_CAM_001": "path/to/pan_video.mp4",
        "TS_ENV_001": "path/to/wind_video.mp4"
    }
    
    # Evaluate all videos
    results = harness.evaluate_scenario_suite(
        videos=test_videos,
        model_version="v1.0.0",
        save_best_to_golden_set=True  # Save passing videos to golden set
    )
    
    print(f"\nTotal scenarios: {results['total_scenarios']}")
    print(f"Passed: {results['all_passed']}")
    print(f"Pass rate: {results['pass_rate']:.1f}%")
    
    return results


def example_3_run_regression_tests():
    """Example: Run regression tests against baseline"""
    print("\n" + "=" * 60)
    print("Example 3: Regression Testing")
    print("=" * 60)
    
    harness = EvaluationHarness()
    
    # New version videos to test
    test_videos = {
        "TS_CHAR_001": "path/to/v2_walking_video.mp4",
        "TS_CHAR_002": "path/to/v2_running_video.mp4",
        "TS_CAM_001": "path/to/v2_pan_video.mp4"
    }
    
    # Run regression tests comparing to v1.0.0 baseline
    results = harness.run_regression_tests(
        test_videos=test_videos,
        test_version="v2.0.0",
        baseline_version="v1.0.0",
        generate_report=True
    )
    
    print(f"\nRegression Test: v2.0.0 vs v1.0.0")
    for scenario_id, result in results['results'].items():
        print(f"\n  {scenario_id}:")
        print(f"    Status: {result.status.value}")
        print(f"    Delta: {result.delta_percentage:+.2f}%")
        if result.failing_metrics:
            print(f"    Failing: {', '.join(result.failing_metrics)}")
        if result.degraded_metrics:
            print(f"    Degraded: {', '.join(result.degraded_metrics)}")
    
    return results


def example_4_compare_two_models():
    """Example: Compare two different models"""
    print("\n" + "=" * 60)
    print("Example 4: Model Comparison")
    print("=" * 60)
    
    harness = EvaluationHarness()
    
    # Model A videos
    model_a_videos = {
        "TS_CHAR_001": "path/to/modelA_walking.mp4",
        "TS_CAM_001": "path/to/modelA_pan.mp4",
        "TS_ENV_001": "path/to/modelA_wind.mp4"
    }
    
    # Model B videos
    model_b_videos = {
        "TS_CHAR_001": "path/to/modelB_walking.mp4",
        "TS_CAM_001": "path/to/modelB_pan.mp4",
        "TS_ENV_001": "path/to/modelB_wind.mp4"
    }
    
    # Compare models
    comparison = harness.compare_models(
        model_a_videos=model_a_videos,
        model_b_videos=model_b_videos,
        model_a_name="ModelA",
        model_b_name="ModelB",
        generate_report=True
    )
    
    print(f"\nModel Comparison: {comparison['model_a']} vs {comparison['model_b']}")
    print(f"Scenarios compared: {comparison['summary']['scenarios_compared']}")
    print(f"{comparison['model_a']} wins: {comparison['summary'][f'{comparison['model_a']}_wins']}")
    print(f"{comparison['model_b']} wins: {comparison['summary'][f'{comparison['model_b']}_wins']}")
    print(f"Overall winner: {comparison['summary']['overall_winner']}")
    
    return comparison


def example_5_performance_benchmark():
    """Example: Benchmark inference performance"""
    print("\n" + "=" * 60)
    print("Example 5: Performance Benchmarking")
    print("=" * 60)
    
    harness = EvaluationHarness()
    
    # Mock inference function
    def mock_inference_fn(prompt, duration_frames, **kwargs):
        """Simulated inference function"""
        import time
        import random
        
        # Simulate processing time
        time.sleep(random.uniform(2.0, 3.0))
        
        return {
            "video_path": "output_video.mp4",
            "frames_generated": duration_frames,
            "processing_time": 2.5
        }
    
    # Benchmark the inference
    result = harness.benchmark_performance(
        inference_fn=mock_inference_fn,
        scenario_id="TS_CHAR_001",
        model_version="v1.0.0",
        num_runs=5,
        prompt="Person walks forward",
        duration_frames=60
    )
    
    print(f"\nBenchmark ID: {result['benchmark_id']}")
    print(f"Passed: {result['passed']}")
    print(f"Average latency: {result['avg_latency_ms']:.0f}ms")
    print(f"Average FPS: {result['avg_fps']:.2f}")
    
    return result


def example_6_explore_test_scenarios():
    """Example: Explore available test scenarios"""
    print("\n" + "=" * 60)
    print("Example 6: Explore Test Scenarios")
    print("=" * 60)
    
    library = TestScenarioLibrary()
    
    # Get coverage summary
    coverage = library.get_coverage_summary()
    
    print(f"\nTotal scenarios: {coverage['total_scenarios']}")
    print(f"Multi-scene scenarios: {coverage['multi_scene_scenarios']}")
    
    print("\nBy movement type:")
    for movement_type, count in coverage['by_movement_type'].items():
        print(f"  {movement_type}: {count}")
    
    print("\nBy difficulty:")
    for difficulty, count in coverage['by_difficulty'].items():
        print(f"  {difficulty}: {count}")
    
    # Get scenarios by type
    character_scenarios = library.get_scenarios_by_type(MovementType.CHARACTER_WALK)
    print(f"\nCharacter walking scenarios:")
    for scenario in character_scenarios:
        print(f"  - {scenario.scenario_id}: {scenario.name}")
        print(f"    Prompt: {scenario.prompt}")
        print(f"    Min temporal consistency: {scenario.min_temporal_consistency}")
    
    # Get advanced scenarios
    advanced_scenarios = library.get_scenarios_by_difficulty(DifficultyLevel.ADVANCED)
    print(f"\nAdvanced difficulty scenarios: {len(advanced_scenarios)}")
    for scenario in advanced_scenarios:
        print(f"  - {scenario.scenario_id}: {scenario.name}")
    
    return coverage


def example_7_golden_set_management():
    """Example: Manage golden reference set"""
    print("\n" + "=" * 60)
    print("Example 7: Golden Set Management")
    print("=" * 60)
    
    from src.evaluation import GoldenSetManager
    
    golden_set = GoldenSetManager("data/golden_set")
    
    # Add a reference to golden set
    reference_id = golden_set.add_reference(
        scenario_id="TS_CHAR_001",
        video_path="path/to/reference_video.mp4",
        model_version="v1.0.0",
        metric_results={
            "temporal_consistency": 0.92,
            "ssim": 0.85,
            "perceptual_quality": 0.88
        },
        expert_approved=True,
        approver="expert_reviewer",
        notes="Excellent walking motion"
    )
    
    print(f"\nAdded reference: {reference_id}")
    
    # Get references for a scenario
    references = golden_set.get_references_by_scenario("TS_CHAR_001")
    print(f"\nReferences for TS_CHAR_001: {len(references)}")
    
    # Get latest approved reference
    latest = golden_set.get_latest_reference(
        scenario_id="TS_CHAR_001",
        expert_approved_only=True
    )
    
    if latest:
        print(f"\nLatest approved reference:")
        print(f"  ID: {latest.reference_id}")
        print(f"  Model version: {latest.model_version}")
        print(f"  Expert approved: {latest.expert_approved}")
        print(f"  Approver: {latest.approver}")
    
    # Export summary
    golden_set.export_summary("evaluation_results/golden_set_summary.json")
    print("\nGolden set summary exported")
    
    return golden_set


def example_8_ci_integration():
    """Example: CI/CD integration"""
    print("\n" + "=" * 60)
    print("Example 8: CI/CD Integration")
    print("=" * 60)
    
    from src.evaluation import CIIntegration, CITestConfig
    
    ci = CIIntegration(
        golden_set_path="data/golden_set"
    )
    
    # Configure CI tests
    config = CITestConfig(
        test_version="v2.0.0",
        baseline_version="v1.0.0",
        scenarios=["TS_CHAR_001", "TS_CAM_001"],  # Test specific scenarios
        max_failures=0,
        max_degradations=1,
        min_pass_rate=95.0,
        run_performance_tests=True,
        output_dir="ci_reports",
        fail_fast=False
    )
    
    # Test videos
    test_videos = {
        "TS_CHAR_001": "path/to/test_walking.mp4",
        "TS_CAM_001": "path/to/test_pan.mp4"
    }
    
    # Run CI tests
    results = ci.run_ci_tests(
        test_videos=test_videos,
        config=config
    )
    
    print(f"\nCI Status: {results['status']}")
    print(f"Pass Rate: {results['summary']['pass_rate']:.1f}%")
    print(f"Failures: {results['summary']['failed']}")
    print(f"Degradations: {results['summary']['degraded']}")
    
    # Generate artifacts
    ci.generate_ci_badge(results, "ci_reports/badge.json")
    ci.export_github_actions_summary(results, "ci_reports/summary.md")
    
    print("\nCI artifacts generated in ci_reports/")
    
    return results


def example_9_export_test_coverage():
    """Example: Export test coverage report"""
    print("\n" + "=" * 60)
    print("Example 9: Test Coverage Report")
    print("=" * 60)
    
    harness = EvaluationHarness()
    
    # Get coverage report
    coverage = harness.get_test_coverage_report()
    
    print(f"\nTest Scenarios:")
    print(f"  Total: {coverage['test_scenarios']['total_scenarios']}")
    print(f"  Expert validated: {coverage['test_scenarios']['expert_validated']}")
    
    print(f"\nGolden Set:")
    print(f"  Total references: {coverage['golden_set']['total_references']}")
    print(f"  Expert approved: {coverage['golden_set']['expert_approved']}")
    
    # Export scenario library
    harness.export_scenario_library("evaluation_results/test_scenarios.json")
    print("\nTest scenarios exported to evaluation_results/test_scenarios.json")
    
    # Export golden set summary
    harness.export_golden_set_summary("evaluation_results/golden_set_summary.json")
    print("Golden set summary exported to evaluation_results/golden_set_summary.json")
    
    return coverage


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("VIDEO GENERATION EVALUATION SYSTEM - EXAMPLES")
    print("=" * 60)
    
    # Note: Most examples use placeholder paths
    # In production, replace with actual video file paths
    
    try:
        # Example 1: Single video evaluation
        # example_1_evaluate_single_video()
        
        # Example 2: Multiple scenario evaluation
        # example_2_evaluate_scenario_suite()
        
        # Example 3: Regression testing
        # example_3_run_regression_tests()
        
        # Example 4: Model comparison
        # example_4_compare_two_models()
        
        # Example 5: Performance benchmarking
        # example_5_performance_benchmark()
        
        # Example 6: Explore test scenarios (no file dependencies)
        example_6_explore_test_scenarios()
        
        # Example 7: Golden set management
        # example_7_golden_set_management()
        
        # Example 8: CI integration
        # example_8_ci_integration()
        
        # Example 9: Export coverage (no file dependencies)
        example_9_export_test_coverage()
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
