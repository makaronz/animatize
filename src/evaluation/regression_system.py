"""
Regression Testing System
Automated comparison of model versions and detection of quality regressions
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from .metrics import MetricsEngine, MetricResult
from .golden_set import GoldenSetManager, GoldenReference
from .test_scenarios import TestScenarioLibrary, TestScenario


class RegressionStatus(Enum):
    """Status of regression test"""
    PASS = "pass"
    FAIL = "fail"
    DEGRADED = "degraded"
    IMPROVED = "improved"
    UNSTABLE = "unstable"
    ERROR = "error"


@dataclass
class RegressionResult:
    """Result of regression test comparison"""
    test_id: str
    scenario_id: str
    status: RegressionStatus
    
    # Version comparison
    baseline_version: str
    test_version: str
    
    # Metric comparisons
    metric_deltas: Dict[str, float]  # metric_name -> delta (positive = improvement)
    metrics_passed: int
    metrics_failed: int
    metrics_degraded: int
    
    # Overall scores
    baseline_avg_score: float
    test_avg_score: float
    delta_percentage: float
    
    # Details
    failing_metrics: List[str]
    degraded_metrics: List[str]
    improved_metrics: List[str]
    
    timestamp: str
    notes: Optional[str] = None


class RegressionTestSuite:
    """Suite for running regression tests"""
    
    def __init__(
        self,
        golden_set_manager: GoldenSetManager,
        metrics_engine: MetricsEngine,
        scenario_library: TestScenarioLibrary
    ):
        self.golden_set = golden_set_manager
        self.metrics = metrics_engine
        self.scenarios = scenario_library
        self.results: List[RegressionResult] = []
    
    def run_regression_test(
        self,
        test_video_path: str,
        scenario_id: str,
        test_version: str,
        baseline_version: Optional[str] = None,
        degradation_threshold: float = 0.05  # 5% degradation tolerance
    ) -> RegressionResult:
        """
        Run regression test comparing test video against baseline
        
        Args:
            test_video_path: Path to video to test
            scenario_id: Test scenario ID
            test_version: Version being tested
            baseline_version: Baseline version (uses latest if None)
            degradation_threshold: Allowed degradation percentage
        
        Returns:
            RegressionResult with comparison details
        """
        # Get baseline reference
        baseline_ref = self.golden_set.get_latest_reference(
            scenario_id=scenario_id,
            model_version=baseline_version,
            expert_approved_only=True
        )
        
        if not baseline_ref:
            return RegressionResult(
                test_id=f"REG_{scenario_id}_{test_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                scenario_id=scenario_id,
                status=RegressionStatus.ERROR,
                baseline_version=baseline_version or "unknown",
                test_version=test_version,
                metric_deltas={},
                metrics_passed=0,
                metrics_failed=0,
                metrics_degraded=0,
                baseline_avg_score=0.0,
                test_avg_score=0.0,
                delta_percentage=0.0,
                failing_metrics=[],
                degraded_metrics=[],
                improved_metrics=[],
                timestamp=datetime.now().isoformat(),
                notes="No approved baseline found"
            )
        
        # Get scenario thresholds
        scenario = self.scenarios.get_scenario(scenario_id)
        if scenario:
            self.metrics.update_thresholds({
                "temporal_consistency": scenario.min_temporal_consistency,
                "instruction_following": scenario.min_instruction_following,
                "clip_similarity": scenario.min_clip_similarity,
                "ssim": scenario.min_ssim,
                "perceptual_quality": scenario.min_perceptual_quality
            })
        
        # Compute metrics for test video
        test_metrics = self.metrics.compute_all(
            video_path=test_video_path,
            reference_data={
                "prompt": scenario.prompt if scenario else "",
                "reference_video": baseline_ref.video_path
            }
        )
        
        # Compare with baseline
        baseline_metrics = baseline_ref.metric_results or {}
        
        metric_deltas = {}
        failing_metrics = []
        degraded_metrics = []
        improved_metrics = []
        
        metrics_passed = 0
        metrics_failed = 0
        metrics_degraded = 0
        
        for metric_name, test_result in test_metrics.items():
            if metric_name not in baseline_metrics:
                continue
            
            baseline_score = baseline_metrics[metric_name]
            test_score = test_result.score
            delta = test_score - baseline_score
            delta_percentage = (delta / baseline_score * 100) if baseline_score > 0 else 0
            
            metric_deltas[metric_name] = delta
            
            # Classify metric result
            if not test_result.passed:
                metrics_failed += 1
                failing_metrics.append(metric_name)
            elif delta < -degradation_threshold:
                metrics_degraded += 1
                degraded_metrics.append(metric_name)
            elif delta > degradation_threshold:
                improved_metrics.append(metric_name)
                metrics_passed += 1
            else:
                metrics_passed += 1
        
        # Calculate overall scores
        baseline_scores = [s for s in baseline_metrics.values() if isinstance(s, (int, float))]
        test_scores = [r.score for r in test_metrics.values()]
        
        baseline_avg = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0
        test_avg = sum(test_scores) / len(test_scores) if test_scores else 0
        delta_pct = ((test_avg - baseline_avg) / baseline_avg * 100) if baseline_avg > 0 else 0
        
        # Determine overall status
        if metrics_failed > 0:
            status = RegressionStatus.FAIL
        elif metrics_degraded > len(metric_deltas) * 0.3:  # >30% metrics degraded
            status = RegressionStatus.DEGRADED
        elif len(improved_metrics) > metrics_degraded:
            status = RegressionStatus.IMPROVED
        elif delta_pct >= -degradation_threshold * 100:
            status = RegressionStatus.PASS
        else:
            status = RegressionStatus.UNSTABLE
        
        result = RegressionResult(
            test_id=f"REG_{scenario_id}_{test_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scenario_id=scenario_id,
            status=status,
            baseline_version=baseline_ref.model_version,
            test_version=test_version,
            metric_deltas=metric_deltas,
            metrics_passed=metrics_passed,
            metrics_failed=metrics_failed,
            metrics_degraded=metrics_degraded,
            baseline_avg_score=baseline_avg,
            test_avg_score=test_avg,
            delta_percentage=delta_pct,
            failing_metrics=failing_metrics,
            degraded_metrics=degraded_metrics,
            improved_metrics=improved_metrics,
            timestamp=datetime.now().isoformat()
        )
        
        self.results.append(result)
        return result
    
    def run_full_regression_suite(
        self,
        test_videos: Dict[str, str],  # scenario_id -> video_path
        test_version: str,
        baseline_version: Optional[str] = None
    ) -> Dict[str, RegressionResult]:
        """
        Run regression tests for multiple scenarios
        
        Args:
            test_videos: Mapping of scenario IDs to test video paths
            test_version: Version being tested
            baseline_version: Baseline version
        
        Returns:
            Dictionary mapping scenario IDs to results
        """
        results = {}
        
        for scenario_id, video_path in test_videos.items():
            result = self.run_regression_test(
                test_video_path=video_path,
                scenario_id=scenario_id,
                test_version=test_version,
                baseline_version=baseline_version
            )
            results[scenario_id] = result
        
        return results
    
    def generate_regression_report(
        self,
        results: Optional[List[RegressionResult]] = None,
        output_path: str = "reports/regression_report.json"
    ):
        """Generate detailed regression test report"""
        if results is None:
            results = self.results
        
        if not results:
            report = {
                "status": "no_tests_run",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Aggregate statistics
            total_tests = len(results)
            passed = sum(1 for r in results if r.status == RegressionStatus.PASS)
            failed = sum(1 for r in results if r.status == RegressionStatus.FAIL)
            degraded = sum(1 for r in results if r.status == RegressionStatus.DEGRADED)
            improved = sum(1 for r in results if r.status == RegressionStatus.IMPROVED)
            unstable = sum(1 for r in results if r.status == RegressionStatus.UNSTABLE)
            errors = sum(1 for r in results if r.status == RegressionStatus.ERROR)
            
            overall_status = "FAIL" if failed > 0 else ("DEGRADED" if degraded > 0 else "PASS")
            
            report = {
                "overall_status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "degraded": degraded,
                    "improved": improved,
                    "unstable": unstable,
                    "errors": errors,
                    "pass_rate": passed / total_tests * 100 if total_tests > 0 else 0
                },
                "results": [asdict(r) for r in results],
                "failing_scenarios": [
                    r.scenario_id for r in results
                    if r.status in [RegressionStatus.FAIL, RegressionStatus.DEGRADED]
                ],
                "improved_scenarios": [
                    r.scenario_id for r in results
                    if r.status == RegressionStatus.IMPROVED
                ]
            }
        
        # Save report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


class ModelComparisonEngine:
    """Engine for comparing different models or versions"""
    
    def __init__(
        self,
        metrics_engine: MetricsEngine,
        scenario_library: TestScenarioLibrary
    ):
        self.metrics = metrics_engine
        self.scenarios = scenario_library
    
    def compare_models(
        self,
        model_a_videos: Dict[str, str],  # scenario_id -> video_path
        model_b_videos: Dict[str, str],
        model_a_name: str,
        model_b_name: str
    ) -> Dict[str, Any]:
        """
        Compare two models across multiple scenarios
        
        Args:
            model_a_videos: Videos from model A
            model_b_videos: Videos from model B
            model_a_name: Name/version of model A
            model_b_name: Name/version of model B
        
        Returns:
            Comparison report
        """
        comparisons = {}
        
        common_scenarios = set(model_a_videos.keys()) & set(model_b_videos.keys())
        
        for scenario_id in common_scenarios:
            scenario = self.scenarios.get_scenario(scenario_id)
            
            if scenario:
                self.metrics.update_thresholds({
                    "temporal_consistency": scenario.min_temporal_consistency,
                    "instruction_following": scenario.min_instruction_following,
                    "clip_similarity": scenario.min_clip_similarity,
                    "ssim": scenario.min_ssim,
                    "perceptual_quality": scenario.min_perceptual_quality
                })
            
            # Compute metrics for both models
            metrics_a = self.metrics.compute_all(
                video_path=model_a_videos[scenario_id],
                reference_data={"prompt": scenario.prompt if scenario else ""}
            )
            
            metrics_b = self.metrics.compute_all(
                video_path=model_b_videos[scenario_id],
                reference_data={"prompt": scenario.prompt if scenario else ""}
            )
            
            # Compare metrics
            metric_comparison = {}
            for metric_name in metrics_a.keys():
                if metric_name in metrics_b:
                    score_a = metrics_a[metric_name].score
                    score_b = metrics_b[metric_name].score
                    
                    metric_comparison[metric_name] = {
                        f"{model_a_name}_score": score_a,
                        f"{model_b_name}_score": score_b,
                        "delta": score_b - score_a,
                        "winner": model_b_name if score_b > score_a else (
                            model_a_name if score_a > score_b else "tie"
                        )
                    }
            
            comparisons[scenario_id] = {
                "scenario_name": scenario.name if scenario else scenario_id,
                "metrics": metric_comparison
            }
        
        # Calculate overall winner
        model_a_wins = 0
        model_b_wins = 0
        ties = 0
        
        for scenario_data in comparisons.values():
            for metric_data in scenario_data["metrics"].values():
                winner = metric_data["winner"]
                if winner == model_a_name:
                    model_a_wins += 1
                elif winner == model_b_name:
                    model_b_wins += 1
                else:
                    ties += 1
        
        report = {
            "model_a": model_a_name,
            "model_b": model_b_name,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "scenarios_compared": len(common_scenarios),
                f"{model_a_name}_wins": model_a_wins,
                f"{model_b_name}_wins": model_b_wins,
                "ties": ties,
                "overall_winner": model_b_name if model_b_wins > model_a_wins else (
                    model_a_name if model_a_wins > model_b_wins else "tie"
                )
            },
            "comparisons": comparisons
        }
        
        return report
    
    def save_comparison_report(self, report: Dict[str, Any], output_path: str):
        """Save model comparison report"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
