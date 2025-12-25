"""
Unit Tests for Video Generation Evaluation System
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import numpy as np
import cv2

from src.evaluation import (
    EvaluationHarness,
    TestScenarioLibrary,
    MetricsEngine,
    GoldenSetManager,
    RegressionTestSuite,
    ModelComparisonEngine,
    PerformanceBenchmark,
    MovementType,
    DifficultyLevel
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_video(temp_dir):
    """Create a sample video file for testing"""
    video_path = Path(temp_dir) / "test_video.mp4"
    
    # Create a simple video (30 frames, 640x480)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
    
    for i in range(30):
        # Create frame with changing color
        frame = np.ones((480, 640, 3), dtype=np.uint8) * (i * 8)
        out.write(frame)
    
    out.release()
    return str(video_path)


class TestScenarioLibrary:
    """Test scenario library functionality"""
    
    def test_library_initialization(self):
        """Test scenario library initializes correctly"""
        library = TestScenarioLibrary()
        
        assert len(library.scenarios) > 0
        assert len(library.multi_scene_scenarios) > 0
    
    def test_get_scenario(self):
        """Test retrieving scenario by ID"""
        library = TestScenarioLibrary()
        
        scenario = library.get_scenario("TS_CHAR_001")
        assert scenario is not None
        assert scenario.scenario_id == "TS_CHAR_001"
        assert scenario.movement_type == MovementType.CHARACTER_WALK
    
    def test_get_scenarios_by_type(self):
        """Test filtering scenarios by movement type"""
        library = TestScenarioLibrary()
        
        char_scenarios = library.get_scenarios_by_type(MovementType.CHARACTER_WALK)
        assert len(char_scenarios) > 0
        assert all(s.movement_type == MovementType.CHARACTER_WALK for s in char_scenarios)
    
    def test_get_scenarios_by_difficulty(self):
        """Test filtering scenarios by difficulty"""
        library = TestScenarioLibrary()
        
        basic_scenarios = library.get_scenarios_by_difficulty(DifficultyLevel.BASIC)
        assert len(basic_scenarios) > 0
        assert all(s.difficulty == DifficultyLevel.BASIC for s in basic_scenarios)
    
    def test_coverage_summary(self):
        """Test coverage summary generation"""
        library = TestScenarioLibrary()
        
        coverage = library.get_coverage_summary()
        assert "total_scenarios" in coverage
        assert "by_movement_type" in coverage
        assert "by_difficulty" in coverage
        assert coverage["total_scenarios"] > 0


class TestMetricsEngine:
    """Test metrics engine functionality"""
    
    def test_metrics_initialization(self):
        """Test metrics engine initializes with default metrics"""
        engine = MetricsEngine()
        
        assert "temporal_consistency" in engine.metrics
        assert "ssim" in engine.metrics
        assert "perceptual_quality" in engine.metrics
    
    def test_temporal_consistency_metric(self, sample_video):
        """Test temporal consistency metric computation"""
        engine = MetricsEngine()
        
        result = engine.metrics["temporal_consistency"].compute(sample_video)
        
        assert result is not None
        assert 0 <= result.score <= 1
        assert result.metric_name == "temporal_consistency"
        assert result.threshold > 0
    
    def test_ssim_metric(self, sample_video):
        """Test SSIM metric computation"""
        engine = MetricsEngine()
        
        result = engine.metrics["ssim"].compute(sample_video)
        
        assert result is not None
        assert 0 <= result.score <= 1
        assert result.metric_name == "ssim"
    
    def test_perceptual_quality_metric(self, sample_video):
        """Test perceptual quality metric"""
        engine = MetricsEngine()
        
        result = engine.metrics["perceptual_quality"].compute(sample_video)
        
        assert result is not None
        assert 0 <= result.score <= 1
        assert result.metric_name == "perceptual_quality"
        assert "details" in result.__dict__
    
    def test_compute_all_metrics(self, sample_video):
        """Test computing all metrics at once"""
        engine = MetricsEngine()
        
        results = engine.compute_all(sample_video)
        
        assert len(results) > 0
        assert "temporal_consistency" in results
        assert "ssim" in results
        assert all(isinstance(r, type(results["temporal_consistency"])) for r in results.values())
    
    def test_update_thresholds(self):
        """Test updating metric thresholds"""
        engine = MetricsEngine()
        
        engine.update_thresholds({
            "temporal_consistency": 0.95,
            "ssim": 0.90
        })
        
        assert engine.metrics["temporal_consistency"].threshold == 0.95
        assert engine.metrics["ssim"].threshold == 0.90


class TestGoldenSetManager:
    """Test golden set management"""
    
    def test_golden_set_initialization(self, temp_dir):
        """Test golden set manager initialization"""
        manager = GoldenSetManager(temp_dir)
        
        assert manager.golden_set_path.exists()
        assert manager.metadata_path.exists()
    
    def test_add_reference(self, temp_dir, sample_video):
        """Test adding reference to golden set"""
        manager = GoldenSetManager(temp_dir)
        
        ref_id = manager.add_reference(
            scenario_id="TS_CHAR_001",
            video_path=sample_video,
            model_version="v1.0.0",
            metric_results={"temporal_consistency": 0.90},
            expert_approved=True,
            approver="test_user"
        )
        
        assert ref_id is not None
        assert ref_id in manager.references
        
        reference = manager.get_reference(ref_id)
        assert reference.scenario_id == "TS_CHAR_001"
        assert reference.model_version == "v1.0.0"
        assert reference.expert_approved is True
    
    def test_get_latest_reference(self, temp_dir, sample_video):
        """Test getting latest reference for scenario"""
        manager = GoldenSetManager(temp_dir)
        
        # Add two references
        manager.add_reference(
            scenario_id="TS_CHAR_001",
            video_path=sample_video,
            model_version="v1.0.0",
            expert_approved=True
        )
        
        import time
        time.sleep(0.1)  # Ensure different timestamps
        
        manager.add_reference(
            scenario_id="TS_CHAR_001",
            video_path=sample_video,
            model_version="v2.0.0",
            expert_approved=True
        )
        
        latest = manager.get_latest_reference(
            scenario_id="TS_CHAR_001",
            expert_approved_only=True
        )
        
        assert latest is not None
        assert latest.model_version == "v2.0.0"
    
    def test_compute_video_hash(self, temp_dir, sample_video):
        """Test video hash computation"""
        manager = GoldenSetManager(temp_dir)
        
        hash1 = manager.compute_video_hash(sample_video)
        hash2 = manager.compute_video_hash(sample_video)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hash length


class TestEvaluationHarness:
    """Test main evaluation harness"""
    
    def test_harness_initialization(self, temp_dir):
        """Test harness initialization"""
        harness = EvaluationHarness(
            golden_set_path=temp_dir,
            output_dir=temp_dir
        )
        
        assert harness.scenario_library is not None
        assert harness.metrics_engine is not None
        assert harness.golden_set is not None
    
    def test_evaluate_video(self, temp_dir, sample_video):
        """Test evaluating a single video"""
        harness = EvaluationHarness(
            golden_set_path=temp_dir,
            output_dir=temp_dir
        )
        
        result = harness.evaluate_video(
            video_path=sample_video,
            scenario_id="TS_CHAR_001",
            model_version="v1.0.0"
        )
        
        assert "scenario_id" in result
        assert "metrics" in result
        assert "summary" in result
        assert result["scenario_id"] == "TS_CHAR_001"
    
    def test_get_test_coverage_report(self, temp_dir):
        """Test coverage report generation"""
        harness = EvaluationHarness(
            golden_set_path=temp_dir,
            output_dir=temp_dir
        )
        
        coverage = harness.get_test_coverage_report()
        
        assert "test_scenarios" in coverage
        assert "golden_set" in coverage
        assert coverage["test_scenarios"]["total_scenarios"] > 0


class TestPerformanceBenchmark:
    """Test performance benchmarking"""
    
    def test_benchmark_initialization(self, temp_dir):
        """Test benchmark initialization"""
        benchmark = PerformanceBenchmark(results_dir=temp_dir)
        
        assert benchmark.results_dir.exists()
    
    def test_benchmark_inference(self, temp_dir):
        """Test benchmarking inference function"""
        benchmark = PerformanceBenchmark(results_dir=temp_dir)
        
        def mock_inference(**kwargs):
            import time
            time.sleep(0.1)
            return {"frames_generated": 30, "processing_time": 0.1}
        
        result = benchmark.benchmark_inference(
            inference_fn=mock_inference,
            scenario_id="TS_CHAR_001",
            model_version="v1.0.0",
            num_runs=3,
            prompt="test"
        )
        
        assert result is not None
        assert result.num_runs == 3
        assert result.avg_latency_ms > 0
        assert len(result.individual_runs) == 3


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_end_to_end_evaluation(self, temp_dir, sample_video):
        """Test complete evaluation workflow"""
        harness = EvaluationHarness(
            golden_set_path=temp_dir,
            output_dir=temp_dir
        )
        
        # Step 1: Evaluate and save to golden set
        result = harness.evaluate_video(
            video_path=sample_video,
            scenario_id="TS_CHAR_001",
            model_version="v1.0.0",
            save_to_golden_set=True,
            expert_approved=True
        )
        
        assert "golden_reference_id" in result
        
        # Step 2: Evaluate new version
        result2 = harness.evaluate_video(
            video_path=sample_video,
            scenario_id="TS_CHAR_001",
            model_version="v2.0.0"
        )
        
        assert result2 is not None
        
        # Step 3: Get coverage report
        coverage = harness.get_test_coverage_report()
        assert coverage["golden_set"]["total_references"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
