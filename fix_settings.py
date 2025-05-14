#!/usr/bin/env python
"""
Quick fix for the settings.py file to make DEALS_ROOT optional
"""
import sys
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_settings_file():
    """Update the settings.py file to make DEALS_ROOT optional."""
    project_root = Path(__file__).parent
    settings_path = project_root / "src" / "config" / "settings.py"
    
    if not os.path.exists(settings_path):
        logger.error(f"Settings file not found at: {settings_path}")
        return False
    
    logger.info(f"Updating settings file at: {settings_path}")
    
    try:
        with open(settings_path, "r") as f:
            content = f.read()
        
        # Replace the method that checks DEALS_ROOT
        if "def _path_from_env(self, env_var: str, default: Optional[Path] = None) -> Path:" in content:
            # Find the start of the method
            method_start = content.find("def _path_from_env(self, env_var: str, default: Optional[Path] = None) -> Path:")
            # Find the end of the method (next def or end of class)
            next_def = content.find("def ", method_start + 1)
            if next_def == -1:
                next_def = len(content)
            
            # Extract the method content
            method_content = content[method_start:next_def]
            
            # Create the new method content
            new_method_content = '''def _path_from_env(self, env_var: str, default: Optional[Path] = None) -> Path:
        """Get a path from an environment variable, with an optional default."""
        path_str = os.getenv(env_var)
        if path_str:
            return Path(path_str)
        if default is not None:
            return default
        
        # Special case for DEALS_ROOT
        if env_var == "DEALS_ROOT":
            logger.warning(f"DEALS_ROOT environment variable not set, using default empty path")
            return Path()
        
        raise ValueError(f"Required path environment variable {env_var} not set")
'''
            
            # Replace the method
            new_content = content.replace(method_content, new_method_content)
            
            # Write the updated content
            with open(settings_path, "w") as f:
                f.write(new_content)
            
            logger.info("Successfully updated settings.py to make DEALS_ROOT optional")
            return True
        else:
            logger.error("Could not find _path_from_env method in settings.py")
            return False
    except Exception as e:
        logger.error(f"Error updating settings.py: {str(e)}")
        return False

def main():
    """Main function to run the fix."""
    logger.info("Starting settings fix...")
    
    if update_settings_file():
        logger.info("Settings fix completed successfully!")
        logger.info("\nYou can now run the dashboard with: python run_dashboard.py")
        return 0
    else:
        logger.error("Failed to update settings file")
        return 1

if __name__ == "__main__":
    sys.exit(main())