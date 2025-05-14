"""
Underwriting Dashboard - Main Application

This script initializes and runs the underwriting dashboard application.
It uses the service layer to coordinate between components.
"""

import logging
import subprocess
import sys
import os
from pathlib import Path

# Import the package to initialize paths
import src

# Import settings
from src.config.settings import settings

# Set up logging
logging.basicConfig(
    filename=settings.logs_dir / "app.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize and run the underwriting dashboard application."""
    try:
        logger.info("Starting Underwriting Dashboard application")
        
        # Import services
        from src.database.db_manager import setup_database
        from src.services.file_service import FileService
        from src.services.monitoring_service import monitoring_service
        
        # Initial setup
        logger.info("Setting up database")
        setup_database()
        
        # Process files and update database
        logger.info("Processing files and updating database")
        if not FileService.update_database():
            logger.warning("No files processed or database update failed")
        
        # Start monitoring in the background
        logger.info("Starting file monitoring")
        monitoring_service.start_monitoring()
        
        # Launch Streamlit dashboard
        logger.info("Starting dashboard")
        dashboard_script = Path(__file__).parent / "run_dashboard.py"
        
        print(f"Launching Streamlit dashboard...")
        
        if dashboard_script.exists():
            # Use subprocess for better handling
            subprocess.Popen([sys.executable, str(dashboard_script)])
            print(f"Streamlit dashboard started at http://localhost:8501")
        else:
            print(f"ERROR: Dashboard launcher script not found at {dashboard_script}")
            logger.error(f"Dashboard launcher script not found at {dashboard_script}")
        
    except Exception as e:
        logger.error(f"Error in main application: {str(e)}", exc_info=True)
        print(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())