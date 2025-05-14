"""
Setup utility for Python package structure initialization.

This module ensures that the project's package structure is properly set up
and eliminates the need for sys.path manipulation throughout the codebase.
"""

import os
import sys
from pathlib import Path

# Get the absolute path to the project root
project_root = Path(__file__).resolve().parent.parent

# Export project root to be used in any module that imports this
PROJECT_ROOT = project_root

def init_package_paths():
    """
    Initialize the Python package structure by adding the project root
    to the Python path if it's not already there.
    
    This should be called from __init__.py files, not directly in module code.
    """
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))