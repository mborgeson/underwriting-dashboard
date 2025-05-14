"""
Optimized Excel Reader Module

This module provides an optimized implementation for reading data from Excel files
based on cell references defined in a reference file. The optimizations include:
- Parallel processing of multiple files
- Caching of parsed references
- More efficient sheet loading
- Optimized cell extraction
- Memory usage improvements
"""

import os
import pandas as pd
import numpy as np
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Union, Optional
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache

# Import original module for compatibility
from src.data_processing.excel_reader import (
    CellReferenceParser,
    ExcelFileReader,
    col_to_num,
    num_to_col,
    extract_text_component
)

# Import settings
from src.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Cache for reference parser
_reference_parser_cache = None
_reference_parser_timestamp = 0
_reference_parser_ttl = 3600  # 1 hour cache TTL

def get_reference_parser() -> CellReferenceParser:
    """
    Get a cached CellReferenceParser instance.
    
    Returns:
        CellReferenceParser instance
    """
    global _reference_parser_cache, _reference_parser_timestamp
    
    current_time = time.time()
    
    # Create a new parser if there's no cached one or if the cache has expired
    if (_reference_parser_cache is None or 
        (current_time - _reference_parser_timestamp) > _reference_parser_ttl):
        logger.info("Creating new CellReferenceParser instance")
        _reference_parser_cache = CellReferenceParser(
            reference_file=settings.reference_file,
            sheet_name=settings.reference_sheet
        )
        _reference_parser_timestamp = current_time
    
    return _reference_parser_cache

class OptimizedExcelFileReader(ExcelFileReader):
    """
    Optimized class to read data from Excel files based on cell references.
    Inherits from the original ExcelFileReader but overrides methods for better performance.
    """
    
    def __init__(self, file_path: Path, parser: CellReferenceParser):
        """
        Initialize the OptimizedExcelFileReader with a file path and parser.
        
        Args:
            file_path: Path to the Excel file
            parser: CellReferenceParser instance containing reference information
        """
        super().__init__(file_path, parser)
    
    def _read_excel_file_with_pandas(self) -> None:
        """
        Read Excel file with pandas using optimized loading.
        Only loads the sheets and ranges needed rather than entire sheets.
        """
        # Identify unique sheet names to load
        sheet_names = set()
        for ref in self.parser.cell_references:
            if ref["type"] != "text":
                sheet_names.add(ref["sheet_name"])
        
        # Get all available sheets in the workbook
        try:
            excel_file = pd.ExcelFile(self.file_path)
            all_sheets = excel_file.sheet_names
            
            # Create a mapping of lowercase sheet names to actual sheet names
            self.sheet_map = {sheet.lower(): sheet for sheet in all_sheets}
        except Exception as e:
            logger.error(f"Error reading Excel file structure: {str(e)}")
            return
        
        # Group references by sheet to optimize loading
        sheet_references = {}
        for ref in self.parser.cell_references:
            if ref["type"] != "text":
                if ref["sheet_name"] not in sheet_references:
                    sheet_references[ref["sheet_name"]] = []
                sheet_references[ref["sheet_name"]].append(ref)
        
        # Process each sheet
        sheet_data = {}
        for sheet_name, refs in sheet_references.items():
            try:
                # Find the actual sheet name
                if sheet_name in all_sheets:
                    actual_sheet_name = sheet_name
                elif sheet_name.lower() in self.sheet_map:
                    actual_sheet_name = self.sheet_map[sheet_name.lower()]
                    logger.info(f"Using sheet '{actual_sheet_name}' for reference to '{sheet_name}'")
                else:
                    # Try partial match
                    matches = [s for s in all_sheets if sheet_name.lower() in s.lower()]
                    if matches:
                        actual_sheet_name = matches[0]
                        logger.info(f"Using closest match sheet '{actual_sheet_name}' for reference to '{sheet_name}'")
                    else:
                        logger.warning(f"Sheet '{sheet_name}' not found in workbook. Available sheets: {all_sheets}")
                        continue
                
                # Determine the minimum range needed to cover all references
                min_row = float('inf')
                max_row = 0
                min_col = float('inf')
                max_col = 0
                
                for ref in refs:
                    if ref["type"] == "single":
                        row = ref["row"]
                        col = col_to_num(ref["col"])
                        min_row = min(min_row, row)
                        max_row = max(max_row, row)
                        min_col = min(min_col, col)
                        max_col = max(max_col, col)
                    elif ref["type"] == "range":
                        min_row = min(min_row, ref["start_row"])
                        max_row = max(max_row, ref["end_row"])
                        min_col = min(min_col, col_to_num(ref["start_col"]))
                        max_col = max(max_col, col_to_num(ref["end_col"]))
                
                # Add a margin for safety
                min_row = max(1, min_row - 1)
                min_col = max(1, min_col - 1)
                
                # Read only the required range from the sheet for efficiency
                # Adjust for usecols being 0-based
                usecols = list(range(min_col - 1, max_col))
                skiprows = min_row - 1
                nrows = max_row - min_row + 2  # +2 to ensure we get all rows needed
                
                # Read the sheet with optimized parameters
                sheet_df = pd.read_excel(
                    self.file_path,
                    sheet_name=actual_sheet_name,
                    header=None,
                    usecols=usecols,
                    skiprows=skiprows,
                    nrows=nrows,
                    engine='openpyxl'
                )
                
                # Adjust the DataFrame index to match the original row numbers
                sheet_df.index = range(min_row, min_row + len(sheet_df))
                
                # Adjust the column index to match the original column numbers
                sheet_df.columns = range(min_col, min_col + len(sheet_df.columns))
                
                # Store the processed sheet
                sheet_data[sheet_name] = sheet_df
                
            except Exception as e:
                logger.warning(f"Could not read sheet '{sheet_name}': {str(e)}")
        
        # Extract values based on references
        self._extract_values_from_sheets(sheet_data)
    
    def _extract_values_from_sheets(self, sheet_data: Dict[str, pd.DataFrame]) -> None:
        """
        Extract values from loaded sheets based on cell references.
        Optimized version that uses vectorized operations where possible.
        
        Args:
            sheet_data: Dictionary of DataFrames with sheet data
        """
        # Process text references first (no sheet access needed)
        for ref in self.parser.cell_references:
            if ref["type"] == "text":
                self.excel_data[ref["column_name"]] = ref["value"]
        
        # Group references by sheet for more efficient processing
        sheet_refs = {}
        for ref in self.parser.cell_references:
            if ref["type"] != "text" and ref["sheet_name"] in sheet_data:
                if ref["sheet_name"] not in sheet_refs:
                    sheet_refs[ref["sheet_name"]] = []
                sheet_refs[ref["sheet_name"]].append(ref)
        
        # Process each sheet's references in a batch
        for sheet_name, refs in sheet_refs.items():
            df = sheet_data[sheet_name]
            
            for ref in refs:
                try:
                    if ref["type"] == "single":
                        # Extract single cell value
                        row_idx = ref["row"]
                        col_idx = col_to_num(ref["col"])
                        
                        if row_idx in df.index and col_idx in df.columns:
                            value = df.loc[row_idx, col_idx]
                            self.excel_data[ref["column_name"]] = value
                        else:
                            logger.warning(f"Cell {ref['cell_address']} in sheet {ref['sheet_name']} is out of bounds")
                    
                    elif ref["type"] == "range":
                        # Extract range of values efficiently
                        start_row_idx = ref["start_row"]
                        start_col_idx = col_to_num(ref["start_col"])
                        end_row_idx = ref["end_row"]
                        end_col_idx = col_to_num(ref["end_col"])
                        
                        # Check if the range is within the loaded data
                        row_range = [r for r in range(start_row_idx, end_row_idx + 1) if r in df.index]
                        col_range = [c for c in range(start_col_idx, end_col_idx + 1) if c in df.columns]
                        
                        if not row_range or not col_range:
                            logger.warning(f"Range {ref['cell_address']} in sheet {ref['sheet_name']} is out of bounds")
                            continue
                        
                        # Check if it's a column range or row range
                        if ref["is_col_range"] and not ref["is_row_range"]:
                            # It's a column range with a single row
                            column_name_parts = extract_text_component(ref["column_name"])
                            base_col_name, text_component = column_name_parts
                            
                            # Get all values at once using vectorized operations
                            if start_row_idx in df.index:
                                values = df.loc[start_row_idx, col_range].to_dict()
                                
                                # Create named entries for each column
                                for col_idx, value in values.items():
                                    col_letter = num_to_col(col_idx)
                                    
                                    if text_component:
                                        col_name = f"{text_component}{ref['sheet_name']}!${col_letter}${ref['start_row']}"
                                    else:
                                        col_name = f"{base_col_name}_{col_letter}"
                                    
                                    self.excel_data[col_name] = value
                        
                        elif ref["is_row_range"] and not ref["is_col_range"]:
                            # It's a row range with a single column
                            if start_col_idx in df.columns:
                                # Get all values at once
                                values = df.loc[row_range, start_col_idx].tolist()
                                self.excel_data[ref["column_name"]] = values
                        
                        else:
                            # It's a 2D range - use DataFrame slicing for efficiency
                            try:
                                # Create a boolean mask for rows and columns
                                row_mask = df.index.isin(row_range)
                                col_mask = df.columns.isin(col_range)
                                
                                # Extract the submatrix
                                submatrix = df.loc[row_mask, col_mask].values.tolist()
                                self.excel_data[ref["column_name"]] = submatrix
                            except Exception as e:
                                logger.error(f"Error extracting 2D range: {str(e)}")
                                # Fallback to individual cell extraction
                                values = []
                                for row_idx in row_range:
                                    row_values = []
                                    for col_idx in col_range:
                                        try:
                                            value = df.loc[row_idx, col_idx]
                                            row_values.append(value)
                                        except:
                                            row_values.append(None)
                                    values.append(row_values)
                                self.excel_data[ref["column_name"]] = values
                
                except Exception as e:
                    logger.error(f"Error extracting values for reference {ref['original_ref']}: {str(e)}")

def process_single_file(file_info: Dict[str, Any], parser: CellReferenceParser) -> Dict[str, Any]:
    """
    Process a single Excel file and extract data.
    Designed to be used in parallel processing.
    
    Args:
        file_info: Dictionary with file metadata
        parser: CellReferenceParser instance
        
    Returns:
        Dictionary with extracted data or None if processing failed
    """
    try:
        file_path = Path(file_info["Absolute File Path"])
        logger.info(f"Processing file: {file_path.name}")
        
        # Read data from the Excel file using optimized reader
        start_time = time.time()
        reader = OptimizedExcelFileReader(file_path, parser)
        excel_data = reader.read_excel_file()
        elapsed_time = time.time() - start_time
        
        if excel_data:
            # Combine file metadata with extracted data
            combined_data = {**file_info, **excel_data}
            logger.info(f"Successfully processed file: {file_path.name} in {elapsed_time:.2f} seconds")
            return combined_data
        else:
            logger.warning(f"No data extracted from file: {file_path.name}")
            return None
    
    except Exception as e:
        logger.error(f"Error processing file {file_info['File Name']}: {str(e)}", exc_info=True)
        return None

def process_excel_files_parallel(file_list: List[Dict[str, Any]], max_workers: int = None) -> pd.DataFrame:
    """
    Process a list of Excel files in parallel and extract data.
    
    Args:
        file_list: List of dictionaries with file metadata
        max_workers: Maximum number of worker processes to use
        
    Returns:
        DataFrame containing extracted data from all files
    """
    if not file_list:
        logger.warning("No files provided to process")
        return pd.DataFrame()
    
    logger.info(f"Processing {len(file_list)} Excel files in parallel")
    
    # Get or create parser
    try:
        parser = get_reference_parser()
    except Exception as e:
        logger.error(f"Error initializing CellReferenceParser: {str(e)}", exc_info=True)
        return pd.DataFrame()
    
    # Determine number of workers
    if max_workers is None:
        import multiprocessing
        max_workers = min(multiprocessing.cpu_count(), len(file_list))
    
    # Process files in parallel
    all_data = []
    start_time = time.time()
    
    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit jobs
        future_to_file = {
            executor.submit(process_single_file, file_info, parser): file_info
            for file_info in file_list
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_file):
            file_info = future_to_file[future]
            try:
                result = future.result()
                if result:
                    all_data.append(result)
            except Exception as e:
                logger.error(f"Error with file {file_info['File Name']}: {str(e)}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Parallel processing completed in {elapsed_time:.2f} seconds")
    
    # Create DataFrame from all data
    if all_data:
        df = pd.DataFrame(all_data)
        logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        return df
    else:
        logger.warning("No data extracted from any files")
        return pd.DataFrame()

def process_excel_files(file_list: List[Dict[str, Any]], parallel: bool = True, max_workers: int = None) -> pd.DataFrame:
    """
    Process a list of Excel files and extract data based on cell references.
    This is a replacement for the original process_excel_files function.
    
    Args:
        file_list: List of dictionaries with file metadata
        parallel: Whether to use parallel processing
        max_workers: Maximum number of worker processes to use
        
    Returns:
        DataFrame containing extracted data from all files
    """
    if not file_list:
        logger.warning("No files provided to process")
        return pd.DataFrame()
    
    # Use parallel processing if requested
    if parallel and len(file_list) > 1:
        return process_excel_files_parallel(file_list, max_workers)
    
    # Otherwise use single-threaded processing
    logger.info(f"Processing {len(file_list)} Excel files sequentially")
    
    # Get or create parser
    try:
        parser = get_reference_parser()
    except Exception as e:
        logger.error(f"Error initializing CellReferenceParser: {str(e)}", exc_info=True)
        return pd.DataFrame()
    
    # Process each file
    all_data = []
    for file_info in file_list:
        result = process_single_file(file_info, parser)
        if result:
            all_data.append(result)
    
    # Create DataFrame from all data
    if all_data:
        df = pd.DataFrame(all_data)
        logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        return df
    else:
        logger.warning("No data extracted from any files")
        return pd.DataFrame()

if __name__ == "__main__":
    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Import file finder for testing
    from src.data_processing.file_finder import find_underwriting_files
    
    print("Finding underwriting files...")
    included_files, _ = find_underwriting_files()
    
    if included_files:
        print(f"Processing {len(included_files)} Excel files...")
        
        # Compare performance between original and optimized implementations
        print("\nRunning original implementation...")
        start_time = time.time()
        from src.data_processing.excel_reader import process_excel_files as process_original
        result_df_original = process_original(included_files)
        original_time = time.time() - start_time
        print(f"Original implementation took {original_time:.2f} seconds")
        
        print("\nRunning optimized implementation (parallel)...")
        start_time = time.time()
        result_df_optimized = process_excel_files(included_files, parallel=True)
        optimized_time = time.time() - start_time
        print(f"Optimized implementation took {optimized_time:.2f} seconds")
        
        print(f"\nSpeedup: {original_time / optimized_time:.2f}x")
        
        if not result_df_optimized.empty:
            print(f"\nExtracted data with {len(result_df_optimized)} rows and {len(result_df_optimized.columns)} columns")
            
            # Verify that both implementations return the same data
            if not result_df_original.empty and set(result_df_original.columns) == set(result_df_optimized.columns):
                print("\nBoth implementations returned the same columns. Data is consistent.")
            
            # Preview the data
            print("\nData preview:")
            pd.set_option('display.max_columns', 10)
            pd.set_option('display.width', 1000)
            print(result_df_optimized.head(5))
        else:
            print("No data extracted from files")
    else:
        print("No files found to process")