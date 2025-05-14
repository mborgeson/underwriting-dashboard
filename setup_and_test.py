#!/usr/bin/env python
"""
Setup and Test Script for Underwriting Dashboard

This script installs required dependencies, configures the environment,
and tests the key functionality of the Underwriting Dashboard application.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import shutil
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_pip_requirements():
    """Check and install required packages."""
    logger.info("Checking and installing required packages...")
    
    try:
        # Install requirements
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing dependencies: {str(e)}")
        logger.error(f"Error output: {e.stderr}")
        return False

def check_env_file():
    """Check if .env file exists and create it if not."""
    logger.info("Checking .env file...")
    
    env_file = Path(".env")
    template_file = Path(".env.template")
    
    if not env_file.exists():
        if template_file.exists():
            # Copy template to .env
            shutil.copy(template_file, env_file)
            logger.info("Created .env file from template")
            
            # Update with actual paths
            with open(env_file, "r") as f:
                content = f.read()
            
            # Replace project root with actual path
            project_root = str(Path.cwd())
            content = content.replace("/path/to/project/root", project_root)
            
            with open(env_file, "w") as f:
                f.write(content)
            
            logger.info("Updated .env file with correct paths")
        else:
            logger.error(".env.template file not found")
            return False
    else:
        logger.info(".env file already exists")
    
    return True

def test_imports():
    """Test that imports work properly."""
    logger.info("Testing imports...")
    
    try:
        import src
        from src.config.settings import settings
        from src.services.file_service import FileService
        from src.services.dashboard_service import DashboardService
        from src.services.monitoring_service import MonitoringService
        
        logger.info("All modules imported successfully")
        logger.info(f"Project root: {settings.project_root}")
        return True
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        return False

def test_database_setup():
    """Test database setup functionality."""
    logger.info("Testing database setup...")
    
    try:
        from src.database.db_manager import setup_database
        
        # Run database setup
        setup_database()
        
        # Check if database file exists
        from src.config.settings import settings
        if settings.database_path.exists():
            logger.info(f"Database created successfully at {settings.database_path}")
            return True
        else:
            logger.error(f"Database file not created at {settings.database_path}")
            return False
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        return False

def test_basic_functionality():
    """Run a basic test of the application's functionality."""
    logger.info("Testing basic functionality...")
    
    try:
        # Import key modules for testing
        from src.config.settings import settings
        from src.services.file_service import FileService
        from src.database.db_manager import get_all_data
        
        # Check if we can get data from the database
        data = get_all_data()
        logger.info(f"Retrieved {len(data) if not data.empty else 0} records from database")
        
        # Test file monitoring setup
        from src.services.monitoring_service import monitoring_service
        
        # Test starting monitoring without actually running it
        if hasattr(monitoring_service.monitor, 'directories'):
            logger.info(f"File monitoring would watch {len(monitoring_service.monitor.directories)} directories")
        
        logger.info("Basic functionality tests passed")
        return True
    except Exception as e:
        logger.error(f"Error in basic functionality test: {str(e)}")
        return False

def main():
    """Run setup and tests."""
    logger.info("Starting setup and tests...")
    
    # Check requirements
    if not check_pip_requirements():
        return 1
    
    # Check .env file
    if not check_env_file():
        return 1
    
    # Run tests
    tests = [
        ("Import Tests", test_imports),
        ("Database Setup", test_database_setup),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    success = True
    for name, test_func in tests:
        logger.info(f"Running {name}...")
        if not test_func():
            success = False
    
    if success:
        logger.info("All tests passed successfully!")
        logger.info("\nTo run the application, use: python main.py")
        return 0
    else:
        logger.error("Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())