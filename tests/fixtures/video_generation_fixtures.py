"""
Pytest Fixtures for Video Generation Testing
Provides reusable test fixtures for regression testing
"""

import pytest
import tempfile
import shutil
import json
import numpy as np
import cv2
from datetime import datetime

from src.evaluation import (
    TestScenarioLibrary,
    MetricsEngine,
    GoldenSetManager,
    RegressionTestSuite,
    ModelComparisonEngine,
    PerformanceBenchmark,
    MovementType,
    DifficultyLevel
)


# ============================================================================
# Session-scoped fixtures (persist for entire test session)
# ============================================================================

@pytest.fixture(scope="session")
def golden_set_manager(tmp_path_factory):
    """
    Provides golden set manager for test session

    Scope: session (shared across all tests)
    """
    golden_path = tmp_path_factory.mktemp("golden_set")
    manager = GoldenSetManager(str(golden_path))
    return manager


@pytest.fixture(scope="session")
def scenario_library():
    """
    Provides test scenario library

    Scope: session (shared across all tests)
    Returns: TestScenarioLibrary with all 25+ test scenarios
    """
    return TestScenarioLibrary()


@pytest.fixture(scope="session")
def metrics_engine():
    """
    Provides metrics computation engine

    Scope: session (shared across all tests)
    Returns: MetricsEngine with all registered metrics
    """
    return MetricsEngine()


@pytest.fixture(scope="session")
def regression_suite(golden_set_manager, metrics_engine, scenario_library):
    """
    Provides regression test suite

    Scope: session (shared across all tests)
    Returns: RegressionTestSuite configured with managers
    """
    return RegressionTestSuite(
        golden_set_manager=golden_set_manager,
        metrics_engine=metrics_engine,
        scenario_library=scenario_library
    )


@pytest.fixture(scope="session")
def model_comparison_engine(metrics_engine, scenario_library):
    """
    Provides model comparison engine

    Scope: session
    Returns: ModelComparisonEngine for comparing model versions
    """
    return ModelComparisonEngine(
        metrics_engine=metrics_engine,
        scenario_library=scenario_library
    )


@pytest.fixture(scope="session")
def performance_benchmark(tmp_path_factory):
    """
    Provides performance benchmarking system

    Scope: session
    Returns: PerformanceBenchmark for latency/throughput testing
    """
    results_dir = tmp_path_factory.mktemp("benchmark_results")
    return PerformanceBenchmark(results_dir=str(results_dir))


# ============================================================================
# Function-scoped fixtures (fresh instance per test)
# ============================================================================

@pytest.fixture
def temp_dir():
    """
    Creates temporary directory for test

    Scope: function (fresh for each test)
    Cleanup: Automatic after test
    """
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_test_video(tmp_path):
    """
    Generates a sample test video for testing

    Scope: function
    Returns: Path to generated test video (60 frames, 640x480, 30fps)
    """
    video_path = tmp_path / "test_video.mp4"
    create_sample_video(str(video_path), frames=60, fps=30.0)
    return str(video_path)


@pytest.fixture
def sample_test_video_high_quality(tmp_path):
    """
    Generates high-quality test video

    Scope: function
    Returns: Path to 1080p test video
    """
    video_path = tmp_path / "test_video_hq.mp4"
    create_sample_video(
        str(video_path),
        frames=60,
        fps=30.0,
        resolution=(1920, 1080)
    )
    return str(video_path)


@pytest.fixture
def sample_test_video_long(tmp_path):
    """
    Generates longer test video for extended tests

    Scope: function
    Returns: Path to 120-frame test video
    """
    video_path = tmp_path / "test_video_long.mp4"
    create_sample_video(str(video_path), frames=120, fps=30.0)
    return str(video_path)


# ============================================================================
# Parametrized fixtures (run tests with multiple parameters)
# ============================================================================

@pytest.fixture(params=[
    "TS_CHAR_001",  # Character walk
    "TS_CHAR_004",  # Facial expression
    "TS_CAM_001",   # Camera pan
    "TS_LIGHT_001",  # Day to night
    "TS_ENV_002",   # Water surface
])
def scenario_id(request):
    """
    Parametrized fixture for testing multiple scenarios

    Usage: Tests using this fixture will run once for each scenario
    """
    return request.param


@pytest.fixture(params=[
    DifficultyLevel.BASIC,
    DifficultyLevel.INTERMEDIATE,
    DifficultyLevel.ADVANCED,
    DifficultyLevel.EXPERT
])
def difficulty_level(request):
    """
    Parametrized fixture for testing different difficulty levels
    """
    return request.param


@pytest.fixture(params=[
    MovementType.CHARACTER_WALK,
    MovementType.CAMERA_PAN,
    MovementType.LIGHTING_DAY_NIGHT,
    MovementType.ENVIRONMENT_WATER
])
def movement_type(request):
    """
    Parametrized fixture for testing different movement types
    """
    return request.param


# ============================================================================
# Configuration fixtures
# ============================================================================

@pytest.fixture
def test_config():
    """
    Provides standard test configuration

    Returns: Dict with test parameters
    """
    return {
        "test_version": "v1.0.0-test",
        "baseline_version": "v0.9.0",
        "degradation_threshold": 0.05,
        "max_latency_ms": 5000.0,
        "min_temporal_consistency": 0.85,
        "min_clip_score": 0.80,
        "min_ssim": 0.75,
        "min_perceptual_quality": 0.80
    }


@pytest.fixture
def strict_test_config():
    """
    Provides strict test configuration for critical tests

    Returns: Dict with stricter thresholds
    """
    return {
        "test_version": "v1.0.0-test",
        "baseline_version": "v0.9.0",
        "degradation_threshold": 0.02,  # Only 2% degradation allowed
        "max_latency_ms": 4000.0,
        "min_temporal_consistency": 0.90,
        "min_clip_score": 0.85,
        "min_ssim": 0.80,
        "min_perceptual_quality": 0.85
    }


@pytest.fixture
def ci_test_config():
    """
    Provides CI/CD test configuration

    Returns: CITestConfig object
    """
    from src.evaluation.ci_integration import CITestConfig

    return CITestConfig(
        test_version="v1.0.0-ci",
        baseline_version="main",
        scenarios=None,    # All scenarios
        max_failures=0,
        max_degradations=2,
        min_pass_rate=95.0,
        run_performance_tests=True,
        output_dir="ci_reports"
    )


# ============================================================================
# Data fixtures
# ============================================================================

@pytest.fixture
def golden_reference_videos(golden_set_manager, scenario_library, sample_test_video):
    """
    Loads or creates golden reference videos for all scenarios

    Returns: Dict mapping scenario_id to GoldenReference
    """
    references = {}

    # Add sample references for testing
    for scenario_id in ["TS_CHAR_001", "TS_CHAR_004", "TS_CAM_001"]:
        scenario = scenario_library.get_scenario(scenario_id)
        if scenario:
            ref_id = golden_set_manager.add_reference(
                scenario_id=scenario_id,
                video_path=sample_test_video,
                model_version="v1.0.0",
                metric_results={
                    "temporal_consistency": 0.89,
                    "ssim": 0.82,
                    "perceptual_quality": 0.85
                },
                expert_approved=True,
                approver="test_fixture"
            )
            references[scenario_id] = golden_set_manager.get_reference(ref_id)

    return references


@pytest.fixture
def test_videos_manifest(tmp_path, sample_test_video):
    """
    Creates test videos manifest for CI testing

    Returns: Dict with video paths for scenarios
    """
    manifest = {
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "videos": {
            "TS_CHAR_001": sample_test_video,
            "TS_CHAR_004": sample_test_video,
            "TS_CAM_001": sample_test_video,
        }
    }

    manifest_path = tmp_path / "test_videos_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    return manifest


# ============================================================================
# Mock fixtures
# ============================================================================

@pytest.fixture
def video_generator_mock():
    """
    Mock video generator function for testing

    Returns: Callable that simulates video generation
    """
    def generate(prompt: str, duration_frames: int = 60, **kwargs):
        """Mock generation function"""
        import time
        time.sleep(0.1)  # Simulate processing

        return {
            "video_path": "/mock/output.mp4",
            "frames_generated": duration_frames,
            "processing_time": 0.1,
            "model_version": "v1.0.0-mock"
        }

    return generate


@pytest.fixture
def inference_function_mock():
    """
    Mock inference function for performance benchmarking

    Returns: Callable that simulates model inference
    """
    def inference(prompt: str, **kwargs):
        """Mock inference"""
        import time
        time.sleep(0.05)  # Simulate inference time

        return {
            "output": "mock_video.mp4",
            "latency_ms": 50.0,
            "frames": 60
        }

    return inference


# ============================================================================
# Scenario fixtures
# ============================================================================

@pytest.fixture
def portrait_scenarios(scenario_library):
    """
    Returns all portrait test scenarios
    """
    return [
        scenario_library.get_scenario("TS_CHAR_004"),  # Facial expression
        scenario_library.get_scenario("TS_CHAR_005"),  # Head turn
    ]


@pytest.fixture
def landscape_scenarios(scenario_library):
    """
    Returns all landscape test scenarios
    """
    return [
        scenario_library.get_scenario("TS_CAM_001"),   # Pan
        scenario_library.get_scenario("TS_LIGHT_001"),  # Day to night
    ]


@pytest.fixture
def multi_character_scenarios(scenario_library):
    """
    Returns multi-character test scenarios
    """
    return [
        scenario_library.get_scenario("TS_CHAR_001"),  # Walk
        scenario_library.get_scenario("TS_CHAR_002"),  # Sprint
    ]


@pytest.fixture
def edge_case_scenarios(scenario_library):
    """
    Returns edge case test scenarios
    """
    return [
        scenario_library.get_scenario("TS_ENV_002"),  # Water
        scenario_library.get_scenario("TS_ENV_003"),  # Particles
        scenario_library.get_scenario("TS_ENV_004"),  # Rain
    ]


@pytest.fixture
def multi_scene_scenario(scenario_library):
    """
    Returns multi-scene continuity scenario
    """
    return scenario_library.get_multi_scene_scenario("TS_MULTI_001")


# ============================================================================
# Helper functions
# ============================================================================

def create_sample_video(
    output_path: str,
    frames: int = 60,
    fps: float = 30.0,
    resolution: tuple = (640, 480)
):
    """
    Create a sample video for testing

    Args:
        output_path: Path to save video
        frames: Number of frames to generate
        fps: Frame rate
        resolution: Video resolution (width, height)
    """
    width, height = resolution
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for i in range(frames):
        # Create frame with gradient and moving pattern
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Add vertical gradient
        gradient = np.linspace(0, 255, height).astype(np.uint8)
        frame[:, :, 0] = gradient[:, np.newaxis]

        # Add horizontal moving pattern
        x_offset = (i * 10) % width
        frame[:, x_offset:min(x_offset+50, width), 1] = 255

        # Add temporal variation
        brightness = int((np.sin(i * 0.1) + 1) * 127)
        frame[:, :, 2] = brightness

        out.write(frame)

    out.release()


# ============================================================================
# Autouse fixtures (run automatically)
# ============================================================================

@pytest.fixture(autouse=True)
def reset_metrics_engine(metrics_engine):
    """
    Reset metrics engine thresholds before each test

    Scope: function
    Autouse: Yes (runs before every test)
    """
    # Reset to default thresholds
    metrics_engine.update_thresholds({
        "temporal_consistency": 0.85,
        "optical_flow_consistency": 0.80,
        "ssim": 0.75,
        "perceptual_quality": 0.80,
        "instruction_following": 0.90,
        "clip_similarity": 0.80
    })
    yield


# ============================================================================
# Markers and configuration
# ============================================================================

def pytest_configure(config):
    """
    Configure custom pytest markers
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance benchmarks"
    )
    config.addinivalue_line(
        "markers", "requires_golden: marks tests requiring golden set"
    )
