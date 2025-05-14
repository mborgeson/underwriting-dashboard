"""
Configuration settings for the Underwriting Dashboard application.

This module provides a centralized, flexible configuration system that can
load settings from environment variables and config files.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

logger = logging.getLogger(__name__)

class Settings:
    """Configuration settings manager for the application."""
    
    def __init__(self):
        """Initialize settings with values from environment variables or defaults."""
        # Base directories
        self.project_root = self._get_project_root()
        self.database_dir = self._path_from_env("DATABASE_DIR", self.project_root / "database")
        self.logs_dir = self._path_from_env("LOGS_DIR", self.project_root / "logs")
        
        # Ensure directories exist
        os.makedirs(self.database_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Database settings
        self.database_path = self._path_from_env("DATABASE_PATH", self.database_dir / "underwriting_models.db")
        self.database_table = os.getenv("DATABASE_TABLE", "underwriting_model_data")
        
        # Deal directories
        self.deals_root = self._path_from_env("DEALS_ROOT", None)
        self.deal_stage_dirs = self._get_deal_stage_dirs()
        
        # Reference file
        self.reference_file = self._path_from_env("REFERENCE_FILE", self.project_root / "prompt" / "Underwriting Dashboard Project - Cell Value References.xlsx")
        self.reference_sheet = os.getenv("REFERENCE_SHEET", "UW Model - Cell Reference Table")
        
        # File criteria
        self.file_types = self._get_list_env("FILE_TYPES", [".xlsb", ".xlsm"])
        self.file_includes = self._get_list_env("FILE_INCLUDES", ["UW Model vCurrent"])
        self.file_excludes = self._get_list_env("FILE_EXCLUDES", ["Speedboat"])
        self.min_modified_date = os.getenv("MIN_MODIFIED_DATE", "2024-07-15")
        
        # Monitoring settings
        self.monitoring_interval = int(os.getenv("MONITORING_INTERVAL", "60"))
        
    def _get_project_root(self) -> Path:
        """Get the project root directory."""
        # Try environment variable first
        env_root = os.getenv("PROJECT_ROOT")
        if env_root:
            return Path(env_root)
        
        # Fall back to detecting from the current file location
        try:
            # Go up to find the project root (src/config/settings.py -> src -> project root)
            return Path(__file__).resolve().parent.parent.parent
        except Exception as e:
            logger.warning(f"Could not detect project root: {str(e)}")
            # Default to current working directory as last resort
            return Path.cwd()
    
    def _path_from_env(self, env_var: str, default: Optional[Path] = None) -> Path:
        """Get a path from an environment variable, with an optional default."""
        path_str = os.getenv(env_var)
        if path_str:
            return Path(path_str)
        if default is not None:
            return default
        raise ValueError(f"Required path environment variable {env_var} not set")
    
    def _get_list_env(self, env_var: str, default: List[str]) -> List[str]:
        """Get a list from a comma-separated environment variable string."""
        list_str = os.getenv(env_var)
        if list_str:
            return [item.strip() for item in list_str.split(",")]
        return default
    
    def _get_deal_stage_dirs(self) -> List[Path]:
        """Get the deal stage directories."""
        # Try environment variable for deal stage directories
        env_stages = os.getenv("DEAL_STAGE_DIRS")
        if env_stages:
            return [Path(dir_path.strip()) for dir_path in env_stages.split(",")]
        
        # If deals_root is specified, use default subdirectories
        if self.deals_root:
            return [
                self.deals_root / "0) Dead Deals",
                self.deals_root / "1) Initial UW and Review",
                self.deals_root / "2) Active UW and Review",
                self.deals_root / "3) Deals Under Contract",
                self.deals_root / "4) Closed Deals",
                self.deals_root / "5) Realized Deals"
            ]
        
        # No defaults available
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to a dictionary for serialization."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Path):
                result[key] = str(value)
            elif isinstance(value, list) and all(isinstance(item, Path) for item in value):
                result[key] = [str(item) for item in value]
            else:
                result[key] = value
        return result
    
    def save_to_file(self, file_path: str) -> None:
        """Save settings to a file for debugging or reference."""
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

# Create a global settings instance
settings = Settings()