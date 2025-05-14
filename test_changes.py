#!/usr/bin/env python
"""
Test script to verify the architecture changes work properly.
"""

import sys
import logging

# Configure basic logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that imports work correctly with the new package structure."""
    logger.info("Testing imports...")
    
    # Test importing from src package
    try:
        import src
        logger.info("✓ Successfully imported src package")
    except ImportError as e:
        logger.error(f"✗ Failed to import src package: {str(e)}")
        return False
    
    # Test importing settings
    try:
        from src.config.settings import settings
        logger.info(f"✓ Successfully imported settings: {settings.project_root}")
    except ImportError as e:
        logger.error(f"✗ Failed to import settings: {str(e)}")
        return False
    
    # Test importing services
    try:
        from src.services.file_service import FileService
        from src.services.dashboard_service import DashboardService
        from src.services.monitoring_service import MonitoringService
        logger.info("✓ Successfully imported services")
    except ImportError as e:
        logger.error(f"✗ Failed to import services: {str(e)}")
        return False
    
    # Test importing other modules
    try:
        from src.file_monitoring.monitor import FileMonitor
        logger.info("✓ Successfully imported file monitoring")
    except ImportError as e:
        logger.error(f"✗ Failed to import file monitoring: {str(e)}")
        return False
    
    return True

def test_settings():
    """Test that settings are loaded correctly."""
    logger.info("Testing settings...")
    
    try:
        from src.config.settings import settings
        
        # Check critical settings
        if not settings.project_root:
            logger.error("✗ Project root not set")
            return False
        
        logger.info(f"✓ Project root: {settings.project_root}")
        logger.info(f"✓ Database path: {settings.database_path}")
        logger.info(f"✓ Logs directory: {settings.logs_dir}")
        
        # Check deal directories
        if not settings.deals_root:
            logger.warning("! Deals root not set")
        else:
            logger.info(f"✓ Deals root: {settings.deals_root}")
            
        if not settings.deal_stage_dirs:
            logger.warning("! Deal stage directories not set")
        else:
            logger.info(f"✓ Found {len(settings.deal_stage_dirs)} deal stage directories")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error testing settings: {str(e)}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting tests...")
    
    tests = [
        ("Import Tests", test_imports),
        ("Settings Tests", test_settings),
    ]
    
    success = True
    for name, test_func in tests:
        logger.info(f"\n===== {name} =====")
        if not test_func():
            success = False
    
    if success:
        logger.info("\n✓ All tests passed!")
        return 0
    else:
        logger.error("\n✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())