# Dashboard package initialization

"""
Dashboard Package

This package contains all the components for the Streamlit dashboard.
It includes the main application entry point and UI components.
"""

# Ensure proper imports when running through Streamlit
import os
import sys
from pathlib import Path

# Make sure project root is in path when running through Streamlit
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
