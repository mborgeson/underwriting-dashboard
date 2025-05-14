# pytest configuration and fixtures

import pytest
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Define fixtures that can be used across tests
@pytest.fixture
def sample_config():
    """Provide a sample configuration for testing."""
    return {
        "deal_directories": ["./tests/test_data/sample_deals"],
        "database_path": "./tests/test_data/test.db",
        "log_file": "./tests/test_data/test.log"
    }
