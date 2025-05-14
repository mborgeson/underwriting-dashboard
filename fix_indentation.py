#!/usr/bin/env python
"""
Fix indentation in the settings.py file
"""
import sys
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_indentation():
    """Fix indentation in the settings.py file."""
    project_root = Path(__file__).parent
    settings_path = project_root / "src" / "config" / "settings.py"
    
    if not os.path.exists(settings_path):
        logger.error(f"Settings file not found at: {settings_path}")
        return False
    
    logger.info(f"Fixing indentation in settings file at: {settings_path}")
    
    try:
        with open(settings_path, "r") as f:
            lines = f.readlines()
        
        # Find the indentation issue with _get_list_env
        fixed_lines = []
        for line in lines:
            # Fix the indentation for the _get_list_env method
            if "def _get_list_env(self, env_var: str, default: List[str]) -> List[str]:" in line and not line.startswith("    def "):
                fixed_lines.append("    def _get_list_env(self, env_var: str, default: List[str]) -> List[str]:\n")
            else:
                fixed_lines.append(line)
        
        # Write the fixed content
        with open(settings_path, "w") as f:
            f.writelines(fixed_lines)
        
        logger.info("Successfully fixed indentation in settings.py")
        return True
    except Exception as e:
        logger.error(f"Error fixing indentation in settings.py: {str(e)}")
        return False

def main():
    """Main function to run the fix."""
    logger.info("Starting indentation fix...")
    
    if fix_indentation():
        logger.info("Indentation fix completed successfully!")
        logger.info("\nYou can now run the dashboard with: python run_dashboard.py")
        return 0
    else:
        logger.error("Failed to fix indentation")
        return 1

if __name__ == "__main__":
    sys.exit(main())