"""
Performance Benchmarking System
Measures latency, throughput, and resource utilization
"""

import time
import psutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
from collections import deque


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single run"""
    test_id: str
    scenario_id: str
    model_version: str
    
    # Timing metrics
    latency_ms: float
    processing_time_ms: float
    queue_time_ms: float = 0.0
    
    # Throughput metrics
    frames_generated: int = 0
    fps: float = 0.0
    tokens_per_second: float = 0.0
    
    # Resource utilization
    peak_memory_mb: float = 0.0
    avg_cpu_percent: float = 0.0
    avg_gpu_utilization: float = 0.0  # If available
    
    # Quality vs speed tradeoff
    quality_score: float = 0.0
    efficiency_score: float = 0.0  # quality / latency
    
    timestamp: str = ""
    metadata: Dict[str, Any] = None


@dataclass
class BenchmarkResult:
    """Aggregated benchmark results"""
    benchmark_id: str
    scenario_id: str
    model_version: str
    num_runs: int
    
    # Latency statistics
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    
    # Throughput statistics
    avg_fps: float
    peak_fps: float
    
    # Resource statistics
    avg_memory_mb: float
    peak_memory_mb: float
    avg_cpu_percent: float
    
    # Pass/fail criteria
    passed: bool
    latency_threshold_ms: float
    throughput_threshold_fps: float
    
    individual_runs: List[PerformanceMetrics]
    timestamp: str


class PerformanceMonitor:
    """Monitors system resources during execution"""
    
    def __init__(self, sample_interval: float = 0.1):
        self.sample_interval = sample_interval
        self.cpu_samples: deque = deque(maxlen=1000)
        self.memory_samples: deque = deque(maxlen=1000)
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self.process = psutil.Process()
    
    def start(self):
        """Start monitoring"""
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop(self) -> Dict[str, float]:
        """Stop monitoring and return statistics"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        
        return self.get_statistics()
    
    def _monitor_loop(self):
        """Monitoring loop"""
        while self._monitoring:
            try:
                # CPU usage
                cpu_percent = self.process.cpu_percent(interval=None)
                self.cpu_samples.append(cpu_percent)
                
                # Memory usage
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.memory_samples.append(memory_mb)
                
            except Exception:
                pass
            
            time.sleep(self.sample_interval)
    
    def get_statistics(self) -> Dict[str, float]:
        """Get monitoring statistics"""
        stats = {
            "avg_cpu_percent": 0.0,
            "peak_cpu_percent": 0.0,
            "avg_memory_mb": 0.0,
            "peak_memory_mb": 0.0
        }
        
        if self.cpu_samples:
            stats["avg_cpu_percent"] = sum(self.cpu_samples) / len(self.cpu_samples)
            stats["peak_cpu_percent"] = max(self.cpu_samples)
        
        if self.memory_samples:
            stats["avg_memory_mb"] = sum(self.memory_samples) / len(self.memory_samples)
            stats["peak_memory_mb"] = max(self.memory_samples)
        
        return stats


class PerformanceBenchmark:
    """Performance benchmarking system"""
    
    def __init__(self, results_dir: str = "data/benchmarks"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[BenchmarkResult] = []
    
    def benchmark_inference(
        self,
        inference_fn: Callable,
        scenario_id: str,
        model_version: str,
        num_runs: int = 10,
        latency_threshold_ms: float = 5000.0,
        throughput_threshold_fps: float = 1.0,
        **inference_kwargs
    ) -> BenchmarkResult:
        """
        Benchmark inference function
        
        Args:
            inference_fn: Function to benchmark (should return video path)
            scenario_id: Test scenario ID
            model_version: Model version
            num_runs: Number of runs for averaging
            latency_threshold_ms: Maximum acceptable latency
            throughput_threshold_fps: Minimum acceptable throughput
            **inference_kwargs: Arguments to pass to inference_fn
        
        Returns:
            BenchmarkResult with statistics
        """
        individual_runs: List[PerformanceMetrics] = []
        
        for run_idx in range(num_runs):
            monitor = PerformanceMonitor()
            
            # Start monitoring
            monitor.start()
            
            # Time the inference
            start_time = time.time()
            try:
                result = inference_fn(**inference_kwargs)
                success = True
            except Exception as e:
                result = None
                success = False
                print(f"Run {run_idx + 1} failed: {e}")
            
            end_time = time.time()
            
            # Stop monitoring
            resource_stats = monitor.stop()
            
            # Calculate metrics
            latency_ms = (end_time - start_time) * 1000
            
            # Extract additional metrics from result if available
            frames_generated = 0
            fps = 0.0
            
            if success and isinstance(result, dict):
                frames_generated = result.get("frames_generated", 0)
                processing_time = result.get("processing_time", latency_ms / 1000)
                if processing_time > 0 and frames_generated > 0:
                    fps = frames_generated / processing_time
            
            run_metrics = PerformanceMetrics(
                test_id=f"PERF_{scenario_id}_{run_idx}",
                scenario_id=scenario_id,
                model_version=model_version,
                latency_ms=latency_ms,
                processing_time_ms=latency_ms,
                frames_generated=frames_generated,
                fps=fps,
                peak_memory_mb=resource_stats["peak_memory_mb"],
                avg_cpu_percent=resource_stats["avg_cpu_percent"],
                timestamp=datetime.now().isoformat(),
                metadata={"run_index": run_idx, "success": success}
            )
            
            individual_runs.append(run_metrics)
            
            # Small delay between runs
            time.sleep(0.5)
        
        # Aggregate statistics
        latencies = [r.latency_ms for r in individual_runs]
        fps_values = [r.fps for r in individual_runs if r.fps > 0]
        memory_values = [r.peak_memory_mb for r in individual_runs]
        cpu_values = [r.avg_cpu_percent for r in individual_runs]
        
        import numpy as np
        
        avg_latency = float(np.mean(latencies))
        median_latency = float(np.median(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        p99_latency = float(np.percentile(latencies, 99))
        
        benchmark_result = BenchmarkResult(
            benchmark_id=f"BENCH_{scenario_id}_{model_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scenario_id=scenario_id,
            model_version=model_version,
            num_runs=num_runs,
            avg_latency_ms=avg_latency,
            median_latency_ms=median_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            min_latency_ms=float(np.min(latencies)),
            max_latency_ms=float(np.max(latencies)),
            avg_fps=float(np.mean(fps_values)) if fps_values else 0.0,
            peak_fps=float(np.max(fps_values)) if fps_values else 0.0,
            avg_memory_mb=float(np.mean(memory_values)),
            peak_memory_mb=float(np.max(memory_values)),
            avg_cpu_percent=float(np.mean(cpu_values)),
            passed=(
                avg_latency <= latency_threshold_ms and
                (not fps_values or np.mean(fps_values) >= throughput_threshold_fps)
            ),
            latency_threshold_ms=latency_threshold_ms,
            throughput_threshold_fps=throughput_threshold_fps,
            individual_runs=individual_runs,
            timestamp=datetime.now().isoformat()
        )
        
        self.results.append(benchmark_result)
        return benchmark_result
    
    def compare_performance(
        self,
        baseline_results: BenchmarkResult,
        test_results: BenchmarkResult
    ) -> Dict[str, Any]:
        """
        Compare performance between two benchmark results
        
        Returns:
            Comparison report
        """
        latency_delta = test_results.avg_latency_ms - baseline_results.avg_latency_ms
        latency_improvement_pct = (
            -latency_delta / baseline_results.avg_latency_ms * 100
            if baseline_results.avg_latency_ms > 0 else 0
        )
        
        throughput_delta = test_results.avg_fps - baseline_results.avg_fps
        throughput_improvement_pct = (
            throughput_delta / baseline_results.avg_fps * 100
            if baseline_results.avg_fps > 0 else 0
        )
        
        memory_delta = test_results.avg_memory_mb - baseline_results.avg_memory_mb
        memory_improvement_pct = (
            -memory_delta / baseline_results.avg_memory_mb * 100
            if baseline_results.avg_memory_mb > 0 else 0
        )
        
        return {
            "scenario_id": test_results.scenario_id,
            "baseline_version": baseline_results.model_version,
            "test_version": test_results.model_version,
            "latency": {
                "baseline_ms": baseline_results.avg_latency_ms,
                "test_ms": test_results.avg_latency_ms,
                "delta_ms": latency_delta,
                "improvement_pct": latency_improvement_pct,
                "faster": latency_delta < 0
            },
            "throughput": {
                "baseline_fps": baseline_results.avg_fps,
                "test_fps": test_results.avg_fps,
                "delta_fps": throughput_delta,
                "improvement_pct": throughput_improvement_pct,
                "faster": throughput_delta > 0
            },
            "memory": {
                "baseline_mb": baseline_results.avg_memory_mb,
                "test_mb": test_results.avg_memory_mb,
                "delta_mb": memory_delta,
                "improvement_pct": memory_improvement_pct,
                "more_efficient": memory_delta < 0
            },
            "overall_faster": latency_delta < 0 or throughput_delta > 0,
            "overall_more_efficient": memory_delta < 0
        }
    
    def generate_benchmark_report(
        self,
        results: Optional[List[BenchmarkResult]] = None,
        output_path: str = "reports/benchmark_report.json"
    ):
        """Generate benchmark report"""
        if results is None:
            results = self.results
        
        if not results:
            report = {
                "status": "no_benchmarks_run",
                "timestamp": datetime.now().isoformat()
            }
        else:
            passed = sum(1 for r in results if r.passed)
            failed = len(results) - passed
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_benchmarks": len(results),
                    "passed": passed,
                    "failed": failed,
                    "pass_rate": passed / len(results) * 100
                },
                "results": []
            }
            
            for result in results:
                report["results"].append({
                    "benchmark_id": result.benchmark_id,
                    "scenario_id": result.scenario_id,
                    "model_version": result.model_version,
                    "passed": result.passed,
                    "latency_ms": {
                        "avg": result.avg_latency_ms,
                        "median": result.median_latency_ms,
                        "p95": result.p95_latency_ms,
                        "p99": result.p99_latency_ms,
                        "threshold": result.latency_threshold_ms,
                        "meets_threshold": result.avg_latency_ms <= result.latency_threshold_ms
                    },
                    "throughput_fps": {
                        "avg": result.avg_fps,
                        "peak": result.peak_fps,
                        "threshold": result.throughput_threshold_fps,
                        "meets_threshold": result.avg_fps >= result.throughput_threshold_fps
                    },
                    "resources": {
                        "avg_memory_mb": result.avg_memory_mb,
                        "peak_memory_mb": result.peak_memory_mb,
                        "avg_cpu_percent": result.avg_cpu_percent
                    }
                })
        
        # Save report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def save_detailed_results(self, benchmark_result: BenchmarkResult):
        """Save detailed benchmark results"""
        output_path = self.results_dir / f"{benchmark_result.benchmark_id}.json"
        
        data = asdict(benchmark_result)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
