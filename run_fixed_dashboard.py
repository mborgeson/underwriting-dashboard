#\!/usr/bin/env python
"""
Script to run the fixed dashboard with all bug fixes applied.
This script sets up the necessary environment variables and launches the Streamlit app.
"""

import os
import sys
import subprocess
from pathlib import Path

# Set the project directory as the current working directory
project_dir = Path(__file__).resolve().parent
os.chdir(project_dir)

# Add the project directory to Python path
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Set environment variables needed for the application
os.environ["DEALS_ROOT"] = str(project_dir)
os.environ["PYTHONPATH"] = str(project_dir) + os.pathsep + os.environ.get("PYTHONPATH", "")

# Database path setup
database_path = project_dir / "database" / "underwriting_models.db"
os.environ["DATABASE_PATH"] = str(database_path)

# Windows-friendly path handling
os.environ["DATABASE_PATH"] = os.environ["DATABASE_PATH"].replace("\\", "/")

print(f"Starting dashboard application...")
print(f"Project directory: {project_dir}")
print(f"Database path: {os.environ['DATABASE_PATH']}")

# Run the Streamlit application
try:
    subprocess.run(["streamlit", "run", str(project_dir / "src" / "dashboard" / "app.py")], check=True)
except Exception as e:
    print(f"Error launching dashboard: {e}")
    sys.exit(1)
