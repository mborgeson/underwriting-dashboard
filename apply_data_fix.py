#!/usr/bin/env python
"""
Apply data type fix to the dashboard.

This script modifies the dashboard app.py file to use our fixed data processing utility.
"""
import os
import sys
from pathlib import Path
import logging
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def apply_fix():
    """Apply the data processing fix to the dashboard."""
    project_root = Path(__file__).parent
    dashboard_app_path = project_root / "src" / "dashboard" / "app.py"
    
    if not os.path.exists(dashboard_app_path):
        logger.error(f"Dashboard app not found at {dashboard_app_path}")
        return False
    
    # Create backup
    backup_path = str(dashboard_app_path) + ".bak"
    shutil.copy2(dashboard_app_path, backup_path)
    logger.info(f"Created backup of dashboard app at {backup_path}")
    
    try:
        # Read dashboard app content
        with open(dashboard_app_path, "r") as f:
            content = f.read()
        
        # Replace import statement for data_processing
        if "from src.dashboard.utils.data_processing import" in content:
            # Update import to use our fixed version
            updated_content = content.replace(
                "from src.dashboard.utils.data_processing import process_data_for_display, get_key_metrics",
                "from src.dashboard.utils.data_processing_fix import process_data_for_display, get_key_metrics"
            )
            
            # Write updated content
            with open(dashboard_app_path, "w") as f:
                f.write(updated_content)
            
            logger.info("Successfully applied data processing fix to dashboard app")
            return True
        else:
            logger.error("Could not find data_processing import in dashboard app")
            return False
    except Exception as e:
        logger.error(f"Error applying fix: {str(e)}")
        
        # Restore from backup
        shutil.copy2(backup_path, dashboard_app_path)
        logger.info("Restored dashboard app from backup due to error")
        return False

def main():
    """Main function."""
    logger.info("Applying data processing fix to dashboard...")
    
    if apply_fix():
        logger.info("Data processing fix applied successfully!")
        logger.info("\nYou can now run the dashboard with:")
        logger.info("- run_dashboard_fixed.bat (on Windows)")
        logger.info("- python run_fixed_dashboard.py")
        return 0
    else:
        logger.error("Failed to apply data processing fix")
        return 1

if __name__ == "__main__":
    sys.exit(main())