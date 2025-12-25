"""
Video Generation Evaluation System

Comprehensive evaluation harness for video generation models including:
- Test scenarios covering all movement types
- Quality metrics (temporal consistency, SSIM, perceptual quality, etc.)
- Golden set management with hashes and embeddings
- Regression testing system
- Performance benchmarking (latency, throughput)
- CI/CD integration
- Automated comparison reports
"""

from .evaluation_harness import EvaluationHarness
from .test_scenarios import (
    TestScenarioLibrary,
    TestScenario,
    MultiSceneScenario,
    MovementType,
    DifficultyLevel
)
from .metrics import (
    MetricsEngine,
    MetricResult,
    TemporalConsistencyMetric,
    OpticalFlowConsistencyMetric,
    SSIMMetric,
    PerceptualQualityMetric,
    InstructionFollowingMetric,
    CLIPSimilarityMetric
)
from .golden_set import GoldenSetManager, GoldenReference
from .regression_system import (
    RegressionTestSuite,
    ModelComparisonEngine,
    RegressionResult,
    RegressionStatus
)
from .performance_benchmarks import (
    PerformanceBenchmark,
    PerformanceMetrics,
    BenchmarkResult,
    PerformanceMonitor
)
from .ci_integration import CIIntegration, CITestConfig, ci_main
from .report_generator import ReportGenerator, generate_all_reports

__all__ = [
    # Main harness
    "EvaluationHarness",
    
    # Test scenarios
    "TestScenarioLibrary",
    "TestScenario",
    "MultiSceneScenario",
    "MovementType",
    "DifficultyLevel",
    
    # Metrics
    "MetricsEngine",
    "MetricResult",
    "TemporalConsistencyMetric",
    "OpticalFlowConsistencyMetric",
    "SSIMMetric",
    "PerceptualQualityMetric",
    "InstructionFollowingMetric",
    "CLIPSimilarityMetric",
    
    # Golden set
    "GoldenSetManager",
    "GoldenReference",
    
    # Regression testing
    "RegressionTestSuite",
    "ModelComparisonEngine",
    "RegressionResult",
    "RegressionStatus",
    
    # Performance
    "PerformanceBenchmark",
    "PerformanceMetrics",
    "BenchmarkResult",
    "PerformanceMonitor",
    
    # CI/CD
    "CIIntegration",
    "CITestConfig",
    "ci_main",
    
    # Reports
    "ReportGenerator",
    "generate_all_reports"
]

__version__ = "1.0.0"
