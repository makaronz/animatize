"""
Evaluation Harness Orchestrator
Main interface for running comprehensive video generation evaluations
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from .test_scenarios import TestScenarioLibrary, TestScenario
from .metrics import MetricsEngine, MetricResult
from .golden_set import GoldenSetManager
from .regression_system import RegressionTestSuite, ModelComparisonEngine
from .performance_benchmarks import PerformanceBenchmark
from .report_generator import ReportGenerator, generate_all_reports
from .ci_integration import CIIntegration


class EvaluationHarness:
    """
    Main evaluation harness for video generation systems
    Orchestrates all evaluation components
    """
    
    def __init__(
        self,
        golden_set_path: str = "data/golden_set",
        output_dir: str = "evaluation_results"
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.scenario_library = TestScenarioLibrary()
        self.metrics_engine = MetricsEngine()
        self.golden_set = GoldenSetManager(golden_set_path)
        
        self.regression_suite = RegressionTestSuite(
            golden_set_manager=self.golden_set,
            metrics_engine=self.metrics_engine,
            scenario_library=self.scenario_library
        )
        
        self.comparison_engine = ModelComparisonEngine(
            metrics_engine=self.metrics_engine,
            scenario_library=self.scenario_library
        )
        
        self.performance_benchmark = PerformanceBenchmark(
            results_dir=str(self.output_dir / "benchmarks")
        )
        
        self.report_generator = ReportGenerator(
            output_dir=str(self.output_dir / "reports")
        )
    
    def evaluate_video(
        self,
        video_path: str,
        scenario_id: str,
        model_version: str,
        save_to_golden_set: bool = False,
        expert_approved: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate a single video against a test scenario
        
        Args:
            video_path: Path to video file
            scenario_id: Test scenario ID
            model_version: Model version that generated video
            save_to_golden_set: Whether to add to golden set
            expert_approved: Mark as expert-approved in golden set
        
        Returns:
            Evaluation results
        """
        scenario = self.scenario_library.get_scenario(scenario_id)
        if not scenario:
            return {
                "error": f"Scenario {scenario_id} not found",
                "available_scenarios": list(self.scenario_library.scenarios.keys())
            }
        
        # Update metric thresholds from scenario
        self.metrics_engine.update_thresholds({
            "temporal_consistency": scenario.min_temporal_consistency,
            "instruction_following": scenario.min_instruction_following,
            "clip_similarity": scenario.min_clip_similarity,
            "ssim": scenario.min_ssim,
            "perceptual_quality": scenario.min_perceptual_quality
        })
        
        # Compute metrics
        metric_results = self.metrics_engine.compute_all(
            video_path=video_path,
            reference_data={
                "prompt": scenario.prompt,
                "expected_duration": scenario.duration_frames
            }
        )
        
        # Check if all metrics passed
        all_passed = all(result.passed for result in metric_results.values())
        
        # Extract metric scores
        metric_scores = {
            name: result.score
            for name, result in metric_results.items()
        }
        
        results = {
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "model_version": model_version,
            "video_path": video_path,
            "timestamp": datetime.now().isoformat(),
            "all_metrics_passed": all_passed,
            "metrics": {
                name: {
                    "score": result.score,
                    "passed": result.passed,
                    "threshold": result.threshold,
                    "details": result.details
                }
                for name, result in metric_results.items()
            },
            "summary": {
                "total_metrics": len(metric_results),
                "passed_metrics": sum(1 for r in metric_results.values() if r.passed),
                "failed_metrics": sum(1 for r in metric_results.values() if not r.passed)
            }
        }
        
        # Save to golden set if requested
        if save_to_golden_set:
            reference_id = self.golden_set.add_reference(
                scenario_id=scenario_id,
                video_path=video_path,
                model_version=model_version,
                metric_results=metric_scores,
                expert_approved=expert_approved
            )
            results["golden_reference_id"] = reference_id
        
        return results
    
    def evaluate_scenario_suite(
        self,
        videos: Dict[str, str],  # scenario_id -> video_path
        model_version: str,
        save_best_to_golden_set: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate multiple videos against their scenarios
        
        Args:
            videos: Mapping of scenario IDs to video paths
            model_version: Model version
            save_best_to_golden_set: Save passing videos to golden set
        
        Returns:
            Aggregated evaluation results
        """
        results = {}
        
        for scenario_id, video_path in videos.items():
            eval_result = self.evaluate_video(
                video_path=video_path,
                scenario_id=scenario_id,
                model_version=model_version,
                save_to_golden_set=False
            )
            
            # Save to golden set if requested and passed all metrics
            if save_best_to_golden_set and eval_result.get("all_metrics_passed", False):
                # Re-save with golden set flag
                self.golden_set.add_reference(
                    scenario_id=scenario_id,
                    video_path=video_path,
                    model_version=model_version,
                    metric_results={
                        name: data['score'] 
                        for name, data in eval_result['metrics'].items()
                    },
                    expert_approved=False
                )
            
            results[scenario_id] = eval_result
        
        # Aggregate statistics
        total = len(results)
        all_passed = sum(1 for r in results.values() if r.get("all_metrics_passed", False))
        
        summary = {
            "model_version": model_version,
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": total,
            "all_passed": all_passed,
            "pass_rate": (all_passed / total * 100) if total > 0 else 0,
            "results": results
        }
        
        # Save results
        output_path = self.output_dir / f"evaluation_{model_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def run_regression_tests(
        self,
        test_videos: Dict[str, str],
        test_version: str,
        baseline_version: Optional[str] = None,
        generate_report: bool = True
    ) -> Dict[str, Any]:
        """
        Run regression tests comparing against golden set
        
        Args:
            test_videos: Test videos to evaluate
            test_version: Version being tested
            baseline_version: Baseline version (uses latest if None)
            generate_report: Generate HTML/MD reports
        
        Returns:
            Regression test results
        """
        # Run regression tests
        regression_results = self.regression_suite.run_full_regression_suite(
            test_videos=test_videos,
            test_version=test_version,
            baseline_version=baseline_version
        )
        
        # Generate regression report
        self.regression_suite.generate_regression_report(
            results=list(regression_results.values()),
            output_path=str(self.output_dir / "regression_report.json")
        )
        
        # Generate formatted reports if requested
        if generate_report:
            report_data = {
                "summary": {
                    "total_tests": len(regression_results),
                    "passed": sum(1 for r in regression_results.values() if r.status.value == "pass"),
                    "failed": sum(1 for r in regression_results.values() if r.status.value == "fail"),
                    "degraded": sum(1 for r in regression_results.values() if r.status.value == "degraded"),
                    "overall_status": "PASS"  # Determine from results
                },
                "results": [
                    {
                        "scenario_id": r.scenario_id,
                        "status": r.status.value,
                        "delta_percentage": r.delta_percentage,
                        "failing_metrics": r.failing_metrics,
                        "degraded_metrics": r.degraded_metrics
                    }
                    for r in regression_results.values()
                ]
            }
            
            generate_all_reports(
                comparison_data=report_data,
                title=f"Regression Test Report: {test_version}",
                output_dir=str(self.output_dir / "reports")
            )
        
        return {
            "test_version": test_version,
            "baseline_version": baseline_version,
            "results": regression_results
        }
    
    def compare_models(
        self,
        model_a_videos: Dict[str, str],
        model_b_videos: Dict[str, str],
        model_a_name: str,
        model_b_name: str,
        generate_report: bool = True
    ) -> Dict[str, Any]:
        """
        Compare two models across scenarios
        
        Args:
            model_a_videos: Videos from model A
            model_b_videos: Videos from model B
            model_a_name: Name of model A
            model_b_name: Name of model B
            generate_report: Generate comparison reports
        
        Returns:
            Comparison results
        """
        # Run comparison
        comparison = self.comparison_engine.compare_models(
            model_a_videos=model_a_videos,
            model_b_videos=model_b_videos,
            model_a_name=model_a_name,
            model_b_name=model_b_name
        )
        
        # Save comparison
        output_path = self.output_dir / f"comparison_{model_a_name}_vs_{model_b_name}.json"
        self.comparison_engine.save_comparison_report(comparison, str(output_path))
        
        # Generate formatted reports if requested
        if generate_report:
            generate_all_reports(
                comparison_data=comparison,
                title=f"Model Comparison: {model_a_name} vs {model_b_name}",
                output_dir=str(self.output_dir / "reports")
            )
        
        return comparison
    
    def benchmark_performance(
        self,
        inference_fn: Callable,
        scenario_id: str,
        model_version: str,
        num_runs: int = 10,
        **inference_kwargs
    ) -> Dict[str, Any]:
        """
        Benchmark inference performance
        
        Args:
            inference_fn: Function to benchmark
            scenario_id: Test scenario ID
            model_version: Model version
            num_runs: Number of runs
            **inference_kwargs: Arguments for inference_fn
        
        Returns:
            Benchmark results
        """
        scenario = self.scenario_library.get_scenario(scenario_id)
        
        if not scenario:
            return {"error": f"Scenario {scenario_id} not found"}
        
        # Run benchmark
        benchmark_result = self.performance_benchmark.benchmark_inference(
            inference_fn=inference_fn,
            scenario_id=scenario_id,
            model_version=model_version,
            num_runs=num_runs,
            latency_threshold_ms=scenario.max_latency_ms,
            throughput_threshold_fps=scenario.min_throughput_fps,
            **inference_kwargs
        )
        
        # Save detailed results
        self.performance_benchmark.save_detailed_results(benchmark_result)
        
        # Generate report
        self.performance_benchmark.generate_benchmark_report(
            results=[benchmark_result],
            output_path=str(self.output_dir / "benchmark_report.json")
        )
        
        return {
            "benchmark_id": benchmark_result.benchmark_id,
            "passed": benchmark_result.passed,
            "avg_latency_ms": benchmark_result.avg_latency_ms,
            "avg_fps": benchmark_result.avg_fps
        }
    
    def export_scenario_library(self, output_path: Optional[str] = None):
        """Export test scenario library"""
        if output_path is None:
            output_path = str(self.output_dir / "test_scenarios.json")
        
        self.scenario_library.export_library(output_path)
    
    def export_golden_set_summary(self, output_path: Optional[str] = None):
        """Export golden set summary"""
        if output_path is None:
            output_path = str(self.output_dir / "golden_set_summary.json")
        
        self.golden_set.export_summary(output_path)
    
    def get_test_coverage_report(self) -> Dict[str, Any]:
        """Get test coverage summary"""
        coverage = self.scenario_library.get_coverage_summary()
        
        golden_set_stats = {
            "total_references": len(self.golden_set.references),
            "expert_approved": sum(
                1 for r in self.golden_set.references.values()
                if r.expert_approved
            ),
            "by_scenario": {}
        }
        
        for scenario_id in self.scenario_library.scenarios.keys():
            refs = self.golden_set.get_references_by_scenario(scenario_id)
            golden_set_stats["by_scenario"][scenario_id] = len(refs)
        
        return {
            "test_scenarios": coverage,
            "golden_set": golden_set_stats,
            "timestamp": datetime.now().isoformat()
        }
