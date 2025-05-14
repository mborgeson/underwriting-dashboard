"""
File Service

This module provides services for file-related operations, including finding
and processing underwriting files. It coordinates between the file_finder and
excel_reader components.
"""

import logging
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
from pathlib import Path

from src.data_processing.file_finder import find_underwriting_files
from src.data_processing.excel_reader import process_excel_files
from src.database.db_manager import store_data

logger = logging.getLogger(__name__)

class FileService:
    """Service for file operations related to underwriting models."""
    
    @staticmethod
    def find_files() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Find underwriting files based on configured criteria.
        
        Returns:
            Tuple containing lists of included and excluded files
        """
        logger.info("Finding underwriting files")
        return find_underwriting_files()
    
    @staticmethod
    def process_files(file_list: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Process a list of underwriting files to extract data.
        
        Args:
            file_list: List of file information dictionaries
            
        Returns:
            DataFrame containing the extracted data
        """
        logger.info(f"Processing {len(file_list)} underwriting files")
        return process_excel_files(file_list)
    
    @staticmethod
    def find_and_process_files() -> Optional[pd.DataFrame]:
        """
        Find and process underwriting files in a single operation.
        
        Returns:
            DataFrame of processed data or None if no files were found/processed
        """
        try:
            included_files, _ = FileService.find_files()
            
            if not included_files:
                logger.warning("No underwriting files found to process")
                return None
                
            data = FileService.process_files(included_files)
            
            if data.empty:
                logger.warning("No data extracted from underwriting files")
                return None
                
            return data
            
        except Exception as e:
            logger.error(f"Error finding and processing files: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def update_database() -> bool:
        """
        Find files, process them, and update the database.
        
        Returns:
            True if the database was successfully updated, False otherwise
        """
        try:
            data = FileService.find_and_process_files()
            
            if data is None:
                return False
                
            store_data(data)
            logger.info(f"Successfully updated database with {len(data)} records")
            return True
            
        except Exception as e:
            logger.error(f"Error updating database: {str(e)}", exc_info=True)
            return False