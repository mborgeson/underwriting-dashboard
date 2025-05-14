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
from src.data_processing.excel_reader_optimized import process_excel_files
from src.database.db_manager_optimized import store_data, process_excel_batch

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
            
    @staticmethod
    def batch_process_files(max_files: int = None) -> bool:
        """
        Find and process multiple files in efficient batches.
        
        Args:
            max_files: Maximum number of files to process (None for all)
            
        Returns:
            True if the database was successfully updated, False otherwise
        """
        try:
            included_files, _ = FileService.find_files()
            
            if not included_files:
                logger.warning("No underwriting files found to process")
                return False
                
            # Limit the number of files if specified
            if max_files and len(included_files) > max_files:
                included_files = included_files[:max_files]
                
            logger.info(f"Batch processing {len(included_files)} files")
            
            # Process files in smaller chunks for memory efficiency
            chunk_size = 5  # Process 5 files at a time
            dataframes = []
            
            for i in range(0, len(included_files), chunk_size):
                chunk = included_files[i:i+chunk_size]
                logger.info(f"Processing chunk of {len(chunk)} files ({i+1}-{i+len(chunk)} of {len(included_files)})")
                
                # Process this chunk of files
                chunk_data = FileService.process_files(chunk)
                
                if not chunk_data.empty:
                    dataframes.append(chunk_data)
            
            if not dataframes:
                logger.warning("No data extracted from any files")
                return False
                
            # Use the batch processing feature for better performance
            result = process_excel_batch(dataframes)
            
            if result:
                logger.info(f"Successfully batch processed {len(included_files)} files")
            else:
                logger.warning("Batch processing completed but with errors")
                
            return result
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}", exc_info=True)
            return False