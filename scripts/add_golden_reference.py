#!/usr/bin/env python3
"""
Script to add a new golden reference video to the test set
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import GoldenSetManager, TestScenarioLibrary, MetricsEngine  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Add new golden reference video"
    )
    parser.add_argument(
        "--scenario",
        required=True,
        help="Scenario ID (e.g., TS_CHAR_001)"
    )
    parser.add_argument(
        "--video",
        required=True,
        help="Path to reference video"
    )
    parser.add_argument(
        "--model-version",
        required=True,
        help="Model version that generated this video"
    )
    parser.add_argument(
        "--approver",
        required=True,
        help="Email of person approving this reference"
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional notes about this reference"
    )
    parser.add_argument(
        "--golden-set-path",
        default="data/golden_set",
        help="Path to golden set directory"
    )
    parser.add_argument(
        "--compute-metrics",
        action="store_true",
        help="Compute metrics before adding"
    )

    args = parser.parse_args()

    # Validate inputs
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video file not found: {args.video}")
        return 1

    # Initialize managers
    golden_set = GoldenSetManager(args.golden_set_path)
    scenario_library = TestScenarioLibrary()

    # Validate scenario
    scenario = scenario_library.get_scenario(args.scenario)
    if not scenario:
        print(f"Error: Unknown scenario ID: {args.scenario}")
        print(f"Valid scenarios: {', '.join(scenario_library.scenarios.keys())}")
        return 1

    # Compute metrics if requested
    metric_results = None
    if args.compute_metrics:
        print(f"Computing metrics for {args.video}...")
        metrics_engine = MetricsEngine()

        # Update thresholds from scenario
        metrics_engine.update_thresholds({
            "temporal_consistency": scenario.min_temporal_consistency,
            "instruction_following": scenario.min_instruction_following,
            "clip_similarity": scenario.min_clip_similarity,
            "ssim": scenario.min_ssim,
            "perceptual_quality": scenario.min_perceptual_quality
        })

        # Compute all metrics
        results = metrics_engine.compute_all(
            video_path=str(video_path),
            reference_data={"prompt": scenario.prompt}
        )

        # Extract scores
        metric_results = {
            name: result.score
            for name, result in results.items()
        }

        # Print results
        print("\nMetric Results:")
        for name, score in metric_results.items():
            passed = results[name].passed
            status = "✓" if passed else "✗"
            print(f"  {status} {name}: {score:.3f}")

        # Check if all metrics passed
        all_passed = all(r.passed for r in results.values())
        if not all_passed:
            print("\n⚠️  Warning: Some metrics did not meet thresholds")
            response = input("Continue adding to golden set? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return 0

    # Add reference
    print(f"\nAdding reference for {args.scenario}...")
    ref_id = golden_set.add_reference(
        scenario_id=args.scenario,
        video_path=str(video_path),
        model_version=args.model_version,
        metric_results=metric_results,
        expert_approved=True,
        approver=args.approver,
        notes=args.notes
    )

    print(f"✓ Successfully added reference: {ref_id}")
    print(f"  Scenario: {scenario.name}")
    print(f"  Model Version: {args.model_version}")
    print(f"  Approved by: {args.approver}")

    if metric_results:
        print(f"  Metrics computed: {len(metric_results)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
