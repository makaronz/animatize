"""
CI/CD Integration Hooks
Provides integration with continuous integration systems
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .regression_system import RegressionTestSuite, RegressionStatus, RegressionResult
from .performance_benchmarks import PerformanceBenchmark, BenchmarkResult
from .test_scenarios import TestScenarioLibrary
from .metrics import MetricsEngine
from .golden_set import GoldenSetManager


@dataclass
class CITestConfig:
    """Configuration for CI test run"""
    test_version: str
    baseline_version: Optional[str] = None
    
    # Test selection
    scenarios: List[str] = None  # None = all scenarios
    
    # Thresholds
    max_failures: int = 0
    max_degradations: int = 2
    min_pass_rate: float = 95.0  # percentage
    
    # Performance
    run_performance_tests: bool = True
    performance_regression_threshold: float = 10.0  # percentage
    
    # Output
    output_dir: str = "ci_reports"
    fail_fast: bool = False


class CIIntegration:
    """CI/CD integration system"""
    
    def __init__(
        self,
        golden_set_path: str = "data/golden_set",
        scenarios_path: Optional[str] = None
    ):
        self.golden_set = GoldenSetManager(golden_set_path)
        self.metrics_engine = MetricsEngine()
        self.scenario_library = TestScenarioLibrary()
        
        self.regression_suite = RegressionTestSuite(
            golden_set_manager=self.golden_set,
            metrics_engine=self.metrics_engine,
            scenario_library=self.scenario_library
        )
        
        self.performance_benchmark = PerformanceBenchmark()
    
    def run_ci_tests(
        self,
        test_videos: Dict[str, str],  # scenario_id -> video_path
        config: CITestConfig
    ) -> Dict[str, Any]:
        """
        Run CI test suite
        
        Args:
            test_videos: Test videos to evaluate
            config: CI test configuration
        
        Returns:
            CI test results with pass/fail status
        """
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Filter scenarios if specified
        if config.scenarios:
            test_videos = {
                sid: path for sid, path in test_videos.items()
                if sid in config.scenarios
            }
        
        # Run regression tests
        print(f"Running regression tests for {len(test_videos)} scenarios...")
        regression_results = self.regression_suite.run_full_regression_suite(
            test_videos=test_videos,
            test_version=config.test_version,
            baseline_version=config.baseline_version
        )
        
        # Analyze results
        total_tests = len(regression_results)
        failures = sum(
            1 for r in regression_results.values()
            if r.status == RegressionStatus.FAIL
        )
        degradations = sum(
            1 for r in regression_results.values()
            if r.status == RegressionStatus.DEGRADED
        )
        passes = sum(
            1 for r in regression_results.values()
            if r.status in [RegressionStatus.PASS, RegressionStatus.IMPROVED]
        )
        
        pass_rate = (passes / total_tests * 100) if total_tests > 0 else 0
        
        # Determine overall pass/fail
        ci_passed = (
            failures <= config.max_failures and
            degradations <= config.max_degradations and
            pass_rate >= config.min_pass_rate
        )
        
        # Generate regression report
        regression_report_path = output_dir / "regression_report.json"
        self.regression_suite.generate_regression_report(
            results=list(regression_results.values()),
            output_path=str(regression_report_path)
        )
        
        ci_results = {
            "status": "PASS" if ci_passed else "FAIL",
            "timestamp": datetime.now().isoformat(),
            "test_version": config.test_version,
            "baseline_version": config.baseline_version,
            "summary": {
                "total_tests": total_tests,
                "passed": passes,
                "failed": failures,
                "degraded": degradations,
                "pass_rate": pass_rate,
                "ci_passed": ci_passed
            },
            "thresholds": {
                "max_failures": config.max_failures,
                "max_degradations": config.max_degradations,
                "min_pass_rate": config.min_pass_rate
            },
            "reports": {
                "regression": str(regression_report_path)
            }
        }
        
        # Run performance tests if enabled
        if config.run_performance_tests:
            print("Running performance benchmarks...")
            performance_results = self._run_performance_tests(
                test_videos=test_videos,
                config=config
            )
            
            perf_report_path = output_dir / "performance_report.json"
            self.performance_benchmark.generate_benchmark_report(
                output_path=str(perf_report_path)
            )
            
            ci_results["performance"] = performance_results
            ci_results["reports"]["performance"] = str(perf_report_path)
        
        # Save CI results
        ci_results_path = output_dir / "ci_results.json"
        with open(ci_results_path, 'w') as f:
            json.dump(ci_results, f, indent=2)
        
        print(f"\nCI Test Results: {ci_results['status']}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Failures: {failures}/{total_tests}")
        print(f"Degradations: {degradations}/{total_tests}")
        
        return ci_results
    
    def _run_performance_tests(
        self,
        test_videos: Dict[str, str],
        config: CITestConfig
    ) -> Dict[str, Any]:
        """Run performance tests"""
        # Note: This is a placeholder. In production, you'd benchmark
        # the actual inference function, not pre-generated videos
        
        perf_results = {
            "status": "skipped",
            "note": "Performance benchmarking requires inference function"
        }
        
        return perf_results
    
    def generate_ci_badge(
        self,
        ci_results: Dict[str, Any],
        output_path: str = "ci_reports/badge.json"
    ):
        """Generate CI badge data"""
        status = ci_results["status"]
        pass_rate = ci_results["summary"]["pass_rate"]
        
        badge = {
            "schemaVersion": 1,
            "label": "video-gen-tests",
            "message": f"{status} ({pass_rate:.0f}%)",
            "color": "brightgreen" if status == "PASS" else "red"
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(badge, f, indent=2)
        
        return badge
    
    def export_github_actions_summary(
        self,
        ci_results: Dict[str, Any],
        output_path: str = "ci_reports/github_summary.md"
    ):
        """Export GitHub Actions summary markdown"""
        status = ci_results["status"]
        summary = ci_results["summary"]
        
        icon = "✅" if status == "PASS" else "❌"
        
        markdown = f"""# {icon} Video Generation CI Results

## Summary
- **Status**: {status}
- **Test Version**: {ci_results['test_version']}
- **Baseline Version**: {ci_results.get('baseline_version', 'N/A')}
- **Pass Rate**: {summary['pass_rate']:.1f}%

## Results
- ✅ **Passed**: {summary['passed']}
- ❌ **Failed**: {summary['failed']}
- ⚠️ **Degraded**: {summary['degraded']}
- 📊 **Total Tests**: {summary['total_tests']}

## Thresholds
- Max Failures: {ci_results['thresholds']['max_failures']}
- Max Degradations: {ci_results['thresholds']['max_degradations']}
- Min Pass Rate: {ci_results['thresholds']['min_pass_rate']}%

## Reports
"""
        
        for report_type, report_path in ci_results.get("reports", {}).items():
            markdown += f"- [{report_type.title()} Report]({report_path})\n"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(markdown)
        
        return markdown


def ci_main(
    test_videos_path: str,
    test_version: str,
    baseline_version: Optional[str] = None,
    scenarios: Optional[List[str]] = None,
    output_dir: str = "ci_reports"
) -> int:
    """
    Main entry point for CI integration
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    # Load test videos manifest
    with open(test_videos_path, 'r') as f:
        test_videos_manifest = json.load(f)
    
    test_videos = test_videos_manifest.get("videos", {})
    
    # Create CI config
    config = CITestConfig(
        test_version=test_version,
        baseline_version=baseline_version,
        scenarios=scenarios,
        output_dir=output_dir
    )
    
    # Run CI tests
    ci = CIIntegration()
    results = ci.run_ci_tests(test_videos=test_videos, config=config)
    
    # Generate artifacts
    ci.generate_ci_badge(results)
    ci.export_github_actions_summary(results)
    
    # Return exit code
    return 0 if results["status"] == "PASS" else 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Generation CI Tests")
    parser.add_argument("--test-videos", required=True, help="Path to test videos manifest JSON")
    parser.add_argument("--test-version", required=True, help="Version being tested")
    parser.add_argument("--baseline-version", help="Baseline version for comparison")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenarios to test")
    parser.add_argument("--output-dir", default="ci_reports", help="Output directory")
    
    args = parser.parse_args()
    
    exit_code = ci_main(
        test_videos_path=args.test_videos,
        test_version=args.test_version,
        baseline_version=args.baseline_version,
        scenarios=args.scenarios,
        output_dir=args.output_dir
    )
    
    sys.exit(exit_code)
