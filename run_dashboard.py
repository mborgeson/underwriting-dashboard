#!/usr/bin/env python
"""
Dashboard Runner Script

This script properly initializes the Python path and launches the Streamlit dashboard.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path for proper imports
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import to ensure package structure is initialized
import src

def main():
    """Run the Streamlit dashboard."""
    dashboard_path = project_root / "src" / "dashboard" / "app.py"
    
    if not dashboard_path.exists():
        print(f"ERROR: Dashboard file not found at {dashboard_path}")
        return 1
    
    print(f"Launching Streamlit dashboard at: {dashboard_path}")
    
    # Make sure PYTHONPATH includes the project root
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{project_root}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = str(project_root)
    
    # Use subprocess.run to block until Streamlit exits
    try:
        subprocess.run(
            ["streamlit", "run", str(dashboard_path)],
            env=env,
            check=True
        )
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except Exception as e:
        print(f"Error running dashboard: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())