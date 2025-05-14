"""
File Finder Module

This module scans through deal directories to find Excel files that meet the
specified criteria for underwriting models.
"""

import os
import datetime
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Any

# Import configuration
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))  # Add project root to path
from config.config import (
    DEALS_ROOT, 
    DEAL_STAGE_DIRS, 
    FILE_TYPES, 
    FILE_INCLUDES, 
    FILE_EXCLUDES, 
    MIN_MODIFIED_DATE
)

# Configure logging
logger = logging.getLogger(__name__)

def get_deal_stage_name(directory_path: Path) -> str:
    """
    Extract the deal stage name from the directory path.
    
    Args:
        directory_path: Path object representing the directory
        
    Returns:
        The name of the deal stage (e.g., "0) Dead Deals")
    """
    return directory_path.name

def meets_file_criteria(file_path: Path) -> bool:
    """
    Check if the file meets the criteria for inclusion in the data processing.
    
    Args:
        file_path: Path object representing the file
        
    Returns:
        True if the file meets all criteria, False otherwise
    """
    # Check file extension
    if not any(str(file_path).lower().endswith(ext) for ext in FILE_TYPES):
        logger.debug(f"File {file_path} excluded: Not an approved Excel type")
        return False
    
    # Check filename includes required text
    file_name = file_path.name
    if not all(include in file_name for include in FILE_INCLUDES):
        logger.debug(f"File {file_path} excluded: Missing required text in filename")
        return False
    
    # Check filename does not include excluded text
    if any(exclude in file_name for exclude in FILE_EXCLUDES):
        logger.debug(f"File {file_path} excluded: Contains excluded text in filename")
        return False
    
    # Check last modified date
    try:
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        min_date = datetime.datetime.strptime(MIN_MODIFIED_DATE, "%Y-%m-%d")
        if mod_time < min_date:
            logger.debug(f"File {file_path} excluded: Last modified date too old")
            return False
    except Exception as e:
        logger.error(f"Error checking modified date for {file_path}: {str(e)}")
        return False
    
    return True

def collect_file_metadata(file_path: Path, deal_stage_dir: Path) -> Dict[str, Any]:
    """
    Collect metadata about a file.
    
    Args:
        file_path: Path object representing the file
        deal_stage_dir: Path object representing the deal stage directory
        
    Returns:
        Dictionary containing file metadata
    """
    try:
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        file_size = os.path.getsize(file_path)
        
        return {
            "File Name": file_path.name,
            "Absolute File Path": str(file_path),
            "Deal Stage Subdirectory Name": get_deal_stage_name(deal_stage_dir),
            "Deal Stage Subdirectory Path": str(deal_stage_dir),
            "Last Modified Date": mod_time,
            "File Size in Bytes": file_size
        }
    except Exception as e:
        logger.error(f"Error collecting metadata for {file_path}: {str(e)}")
        return {}

def find_uw_model_folder(deal_folder: Path) -> Path:
    """
    Find the "UW Model" folder within a deal folder.
    
    Args:
        deal_folder: Path object representing a deal folder
        
    Returns:
        Path to the UW Model folder if found, None otherwise
    """
    # Look for folder named "UW Model" (case insensitive)
    for folder in deal_folder.iterdir():
        if folder.is_dir() and folder.name.lower() == "uw model":
            return folder
    
    # If not found directly, search one level deeper
    for subfolder in deal_folder.iterdir():
        if subfolder.is_dir():
            for folder in subfolder.iterdir():
                if folder.is_dir() and folder.name.lower() == "uw model":
                    return folder
    
    return None

def find_underwriting_files() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Find Excel files that meet the criteria for underwriting models.
    
    Returns:
        Tuple containing two lists:
        1. List of dictionaries with metadata for files to include
        2. List of dictionaries with metadata for files to exclude
    """
    included_files = []
    excluded_files = []
    
    try:
        # Process each deal stage directory
        for deal_stage_dir in DEAL_STAGE_DIRS:
            deal_stage_path = Path(deal_stage_dir)
            
            if not deal_stage_path.exists():
                logger.warning(f"Deal stage directory does not exist: {deal_stage_path}")
                continue
                
            logger.info(f"Processing deal stage: {get_deal_stage_name(deal_stage_path)}")
            
            # Process each deal folder within the deal stage directory
            for deal_folder in deal_stage_path.iterdir():
                if not deal_folder.is_dir():
                    continue
                    
                logger.debug(f"Processing deal folder: {deal_folder.name}")
                
                # Find the UW Model folder
                uw_model_folder = find_uw_model_folder(deal_folder)
                
                if not uw_model_folder:
                    logger.debug(f"No UW Model folder found in {deal_folder.name}")
                    continue
                
                logger.debug(f"Found UW Model folder in {deal_folder.name}")
                
                # Process each file in the UW Model folder
                for file_path in uw_model_folder.iterdir():
                    if not file_path.is_file():
                        continue
                        
                    file_metadata = collect_file_metadata(file_path, deal_stage_path)
                    
                    if not file_metadata:
                        logger.warning(f"Could not collect metadata for {file_path}")
                        continue
                    
                    if meets_file_criteria(file_path):
                        included_files.append(file_metadata)
                        logger.info(f"Including file: {file_path.name}")
                    else:
                        excluded_files.append(file_metadata)
                        logger.debug(f"Excluding file: {file_path.name}")
    
    except Exception as e:
        logger.error(f"Error finding underwriting files: {str(e)}", exc_info=True)
    
    logger.info(f"Found {len(included_files)} files to include and {len(excluded_files)} files to exclude")
    return included_files, excluded_files

def display_results(included_files: List[Dict[str, Any]], excluded_files: List[Dict[str, Any]]) -> None:
    """
    Display the results of the file finding process.
    
    Args:
        included_files: List of dictionaries with metadata for files to include
        excluded_files: List of dictionaries with metadata for files to exclude
    """
    print(f"\nFound {len(included_files)} files to include:")
    for i, file in enumerate(included_files, 1):
        print(f"{i}. {file['File Name']} - {file['Deal Stage Subdirectory Name']} - {file['Last Modified Date']}")
    
    print(f"\nFound {len(excluded_files)} files to exclude:")
    for i, file in enumerate(excluded_files, 1):
        print(f"{i}. {file['File Name']} - {file['Deal Stage Subdirectory Name']} - {file['Last Modified Date']}")

if __name__ == "__main__":
    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Finding underwriting files...")
    included_files, excluded_files = find_underwriting_files()
    display_results(included_files, excluded_files)