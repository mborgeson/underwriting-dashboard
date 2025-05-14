#!/usr/bin/env python
"""
Update the dashboard app to use the fixed analytics components
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

def update_app():
    """Update the dashboard app to use the fixed analytics component."""
    project_root = Path(__file__).parent
    dashboard_app_path = project_root / "src" / "dashboard" / "app.py"
    
    if not os.path.exists(dashboard_app_path):
        logger.error(f"Dashboard app not found at {dashboard_app_path}")
        return False
    
    # Create backup
    backup_path = str(dashboard_app_path) + ".analytics.bak"
    shutil.copy2(dashboard_app_path, backup_path)
    logger.info(f"Created backup of dashboard app at {backup_path}")
    
    try:
        # Read dashboard app content
        with open(dashboard_app_path, "r") as f:
            content = f.read()
        
        # Update the analytics import
        if "from src.dashboard.components.analytics import" in content:
            # Update import to use our fixed version
            import_index = content.find("from src.dashboard.components.analytics import")
            import_end = content.find(")", import_index) + 1
            
            # Replace the import with our fixed version
            original_import = content[import_index:import_end]
            fixed_import = "from src.dashboard.components.analytics_fix import (\n    render_deal_stage_distribution,\n    render_geographic_analysis,\n    render_performance_metrics,\n    render_deal_timeline\n)"
            
            updated_content = content.replace(original_import, fixed_import)
            
            # Write updated content
            with open(dashboard_app_path, "w") as f:
                f.write(updated_content)
            
            logger.info("Successfully updated analytics import in dashboard app")
            return True
        else:
            logger.error("Could not find analytics import in dashboard app")
            return False
    except Exception as e:
        logger.error(f"Error updating analytics import: {str(e)}")
        
        # Restore from backup
        shutil.copy2(backup_path, dashboard_app_path)
        logger.info("Restored dashboard app from backup due to error")
        return False

def main():
    """Main function."""
    logger.info("Updating dashboard app to use fixed analytics...")
    
    if update_app():
        logger.info("Analytics update applied successfully!")
        logger.info("\nYou can now run the dashboard with:")
        logger.info("- run_dashboard_fixed.bat (on Windows)")
        logger.info("- python run_fixed_dashboard.py")
        return 0
    else:
        logger.error("Failed to update analytics")
        return 1

if __name__ == "__main__":
    sys.exit(main())