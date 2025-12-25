#!/usr/bin/env python3
"""
Script to export golden set summary
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import GoldenSetManager, TestScenarioLibrary  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Export golden set summary"
    )
    parser.add_argument(
        "--output",
        default="reports/golden_set_summary.json",
        help="Output path for summary"
    )
    parser.add_argument(
        "--golden-set-path",
        default="data/golden_set",
        help="Path to golden set directory"
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format"
    )

    args = parser.parse_args()

    # Initialize managers
    golden_set = GoldenSetManager(args.golden_set_path)
    scenario_library = TestScenarioLibrary()

    # Generate summary
    if args.format == "json":
        golden_set.export_summary(args.output)
        print(f"✓ Summary exported to: {args.output}")

    elif args.format == "markdown":
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write("# Golden Set Summary\n\n")
            f.write(f"**Total References**: {len(golden_set.references)}\n")
            f.write(f"**Expert Approved**: {sum(1 for r in golden_set.references.values() if r.expert_approved)}\n\n")

            # Group by scenario
            f.write("## References by Scenario\n\n")
            scenario_counts = {}
            for ref in golden_set.references.values():
                if ref.scenario_id not in scenario_counts:
                    scenario_counts[ref.scenario_id] = []
                scenario_counts[ref.scenario_id].append(ref)

            for scenario_id, refs in sorted(scenario_counts.items()):
                scenario = scenario_library.get_scenario(scenario_id)
                scenario_name = scenario.name if scenario else scenario_id

                f.write(f"### {scenario_id}: {scenario_name}\n\n")
                f.write(f"Total: {len(refs)} | Approved: {sum(1 for r in refs if r.expert_approved)}\n\n")

                for ref in sorted(refs, key=lambda r: r.created_at, reverse=True):
                    status = "✓" if ref.expert_approved else "○"
                    f.write(f"- {status} `{ref.reference_id}`\n")
                    f.write(f"  - Model: {ref.model_version}\n")
                    f.write(f"  - Created: {ref.created_at}\n")
                    if ref.expert_approved:
                        f.write(f"  - Approved by: {ref.approver}\n")
                    if ref.metric_results:
                        metrics_str = ', '.join(
                            f'{k}={v:.2f}' for k, v in list(ref.metric_results.items())[:3]
                        )
                        f.write(f"  - Metrics: {metrics_str}\n")
                    f.write("\n")

        print(f"✓ Markdown summary exported to: {args.output}")

    # Print console summary
    print("\nGolden Set Statistics:")
    print(f"  Total References: {len(golden_set.references)}")
    print(f"  Expert Approved: {sum(1 for r in golden_set.references.values() if r.expert_approved)}")

    # Count by scenario
    scenario_counts = {}
    for ref in golden_set.references.values():
        scenario_counts[ref.scenario_id] = scenario_counts.get(ref.scenario_id, 0) + 1

    print(f"\n  Scenarios Covered: {len(scenario_counts)}")
    print(f"  Avg References per Scenario: {len(golden_set.references) / len(scenario_counts):.1f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
