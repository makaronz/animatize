#!/usr/bin/env python3
"""
Script to validate an existing golden reference
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import GoldenSetManager, MetricsEngine, TestScenarioLibrary  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Validate golden reference video"
    )
    parser.add_argument(
        "--reference-id",
        required=True,
        help="Reference ID to validate"
    )
    parser.add_argument(
        "--approver",
        help="Email of person approving (for marking as approved)"
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Validation notes"
    )
    parser.add_argument(
        "--golden-set-path",
        default="data/golden_set",
        help="Path to golden set directory"
    )
    parser.add_argument(
        "--recompute-metrics",
        action="store_true",
        help="Recompute metrics"
    )

    args = parser.parse_args()

    # Initialize managers
    golden_set = GoldenSetManager(args.golden_set_path)

    # Get reference
    reference = golden_set.get_reference(args.reference_id)
    if not reference:
        print(f"Error: Reference not found: {args.reference_id}")
        return 1

    print(f"Reference ID: {reference.reference_id}")
    print(f"Scenario: {reference.scenario_id}")
    print(f"Model Version: {reference.model_version}")
    print(f"Created: {reference.created_at}")
    print(f"Video: {reference.video_path}")
    print(f"Duration: {reference.duration_frames} frames @ {reference.fps} fps")
    print(f"Resolution: {reference.resolution}")
    print(f"Expert Approved: {reference.expert_approved}")

    if reference.expert_approved:
        print(f"Approved by: {reference.approver}")
        print(f"Approval Date: {reference.approval_date}")

    # Check video exists
    video_path = Path(reference.video_path)
    if not video_path.exists():
        print(f"\n⚠️  Warning: Video file not found: {reference.video_path}")
        return 1

    # Recompute metrics if requested
    if args.recompute_metrics:
        print("\nRecomputing metrics...")

        scenario_library = TestScenarioLibrary()
        scenario = scenario_library.get_scenario(reference.scenario_id)

        metrics_engine = MetricsEngine()
        if scenario:
            metrics_engine.update_thresholds({
                "temporal_consistency": scenario.min_temporal_consistency,
                "ssim": scenario.min_ssim,
                "perceptual_quality": scenario.min_perceptual_quality
            })

        results = metrics_engine.compute_all(
            video_path=reference.video_path,
            reference_data={"prompt": scenario.prompt if scenario else ""}
        )

        print("\nMetric Results:")
        all_passed = True
        for name, result in results.items():
            status = "✓" if result.passed else "✗"
            print(f"  {status} {name}: {result.score:.3f} (threshold: {result.threshold:.3f})")
            if not result.passed:
                all_passed = False

        if all_passed:
            print("\n✓ All metrics passed!")
        else:
            print("\n⚠️  Some metrics did not meet thresholds")

    # Display existing metrics
    elif reference.metric_results:
        print("\nStored Metrics:")
        for name, score in reference.metric_results.items():
            print(f"  {name}: {score:.3f}")

    # Mark as approved if requested
    if args.approver:
        print(f"\nMarking as approved by {args.approver}...")
        golden_set.validate_reference(
            reference_id=args.reference_id,
            approver=args.approver,
            approved=True,
            notes=args.notes
        )
        print("✓ Reference validated and marked as approved")

    return 0


if __name__ == "__main__":
    sys.exit(main())
