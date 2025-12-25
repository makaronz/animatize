"""
Pytest configuration and shared fixtures
This file is automatically loaded by pytest
"""

import sys
from pathlib import Path

# Add src to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import fixtures from fixtures module
from tests.fixtures.video_generation_fixtures import *  # noqa: F403, E402
import pytest  # noqa: E402


# Additional global fixtures can be defined here


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup test environment before any tests run

    Scope: session (runs once)
    Autouse: Yes (runs automatically)
    """
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("ci_reports").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)

    yield

    # Cleanup after all tests (optional)
    # Add any cleanup logic here if needed
