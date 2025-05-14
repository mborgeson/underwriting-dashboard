"""
Task Scheduler Setup for File Monitoring

This module creates a scheduled task that runs the file monitoring script
at system startup or user login.
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('task_scheduler_setup')

def create_task(task_name="UnderwritingMonitor", run_at_startup=True, run_as_user=True):
    """
    Create a scheduled task to run the file monitoring script.
    
    Args:
        task_name: Name of the task
        run_at_startup: Whether to run the task at system startup
        run_as_user: Whether to run the task as the current user
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get paths
        project_root = Path(__file__).resolve().parents[2]
        script_path = project_root / "src" / "file_monitoring" / "monitor.py"
        python_exe = sys.executable
        
        # Create a batch file to run the script
        batch_file = project_root / "run_monitoring.bat"
        with open(batch_file, 'w') as f:
            f.write(f'@echo off\n')
            f.write(f'cd /d "{project_root}"\n')
            f.write(f'"{python_exe}" -m src.file_monitoring.monitor\n')
        
        logger.info(f"Created batch file: {batch_file}")
        
        # Build the task command
        trigger = "ONSTART" if run_at_startup else "ONLOGON"
        
        cmd = [
            "schtasks",
            "/Create",
            "/F",  # Force creation, overwrite if exists
            "/TN", task_name,
            "/TR", str(batch_file),
            "/SC", trigger,
            "/RL", "HIGHEST"  # Run with highest privileges
        ]
        
        # If running as current user
        if run_as_user:
            cmd.extend(["/RU", os.environ["USERNAME"]])
        
        # Run the command
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Task '{task_name}' created successfully")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"Failed to create task: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Error creating scheduled task: {str(e)}", exc_info=True)
        return False

def delete_task(task_name="UnderwritingMonitor"):
    """
    Delete a scheduled task.
    
    Args:
        task_name: Name of the task
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ["schtasks", "/Delete", "/F", "/TN", task_name]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Task '{task_name}' deleted successfully")
            return True
        else:
            logger.error(f"Failed to delete task: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Error deleting scheduled task: {str(e)}", exc_info=True)
        return False

def main():
    """
    Main function to parse arguments and create or delete the task.
    """
    parser = argparse.ArgumentParser(description="Set up or remove a scheduled task for file monitoring")
    
    parser.add_argument("action", choices=["create", "delete"], help="Whether to create or delete the task")
    parser.add_argument("--name", default="UnderwritingMonitor", help="Name of the task")
    parser.add_argument("--startup", action="store_true", help="Run at system startup (default is user logon)")
    
    args = parser.parse_args()
    
    if args.action == "create":
        success = create_task(args.name, args.startup)
    else:
        success = delete_task(args.name)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()