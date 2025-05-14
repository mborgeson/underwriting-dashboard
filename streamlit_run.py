#!/usr/bin/env python
"""
Streamlit Dashboard Runner

This script properly sets up the Python path and then runs the Streamlit dashboard.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Set up the environment and run the Streamlit dashboard."""
    # Get the absolute path to the project root directory
    project_root = Path(__file__).resolve().parent
    
    # Add the project root to the Python path
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Get the absolute path to the dashboard app
    dashboard_path = project_root / "src" / "dashboard" / "app.py"
    
    print(f"Running dashboard from: {dashboard_path}")
    print(f"PYTHONPATH set to: {os.environ['PYTHONPATH']}")
    
    # Run Streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", str(dashboard_path)]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()