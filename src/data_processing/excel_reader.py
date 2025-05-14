"""
Excel Reader Module

This module reads data from Excel files based on cell references defined in a reference file.
It supports various types of cell references including single cells, ranges, and composite references.
"""

import os
import pandas as pd
import numpy as np
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Union, Optional
from datetime import datetime
# import pyxlsb

try:
    import pyxlsb
    XLSB_SUPPORT = True
except ImportError:
    logging.warning("pyxlsb not installed. Will not be able to read .xlsb files.")
    XLSB_SUPPORT = False

# Import configuration
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))  # Add project root to path
from config.config import REFERENCE_FILE, REFERENCE_SHEET

# Configure logging
logger = logging.getLogger(__name__)

# Standalone utility functions
def extract_text_component(column_name: str) -> Tuple[str, Optional[str]]:
    """
    Extract the text component from a column name if present.
    
    Args:
        column_name: The column name to check
        
    Returns:
        Tuple of (cleaned_column_name, text_component)
    """
    # Check if there's a text component followed by a cell reference
    if " - " in column_name and "!" in column_name:
        parts = column_name.split(" - ", 1)
        text_component = parts[0] + " - "
        cell_ref = parts[1]
        return cell_ref, text_component
    
    return column_name, None

def col_to_num(col_str: str) -> int:
    """
    Convert Excel column letters to a number.
    For example: A -> 1, Z -> 26, AA -> 27, etc.
    
    Args:
        col_str: Column string (e.g., 'A', 'BC')
        
    Returns:
        Column number
    """
    num = 0
    for c in col_str:
        num = num * 26 + (ord(c.upper()) - ord('A') + 1)
    return num

def num_to_col(num: int) -> str:
    """
    Convert a number to Excel column letters.
    For example: 1 -> A, 26 -> Z, 27 -> AA, etc.
    
    Args:
        num: Column number
        
    Returns:
        Column string
    """
    letters = ""
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters

class CellReferenceParser:
    """
    Class to parse Excel cell references from the reference file and extract values from Excel files.
    """
    
    def __init__(self, reference_file: Path = REFERENCE_FILE, sheet_name: str = REFERENCE_SHEET):
        """
        Initialize the CellReferenceParser with the reference file.
        
        Args:
            reference_file: Path to the reference Excel file
            sheet_name: Name of the sheet in the reference file containing the cell references
        """
        self.reference_file = reference_file
        self.sheet_name = sheet_name
        self.reference_df = None
        self.cell_references = []
        
        # Load the reference data
        self._load_reference_file()
        
    def _load_reference_file(self) -> None:
        """
        Load the reference file and extract cell references.
        """
        try:
            logger.info(f"Loading reference file: {self.reference_file}")
            self.reference_df = pd.read_excel(self.reference_file, sheet_name=self.sheet_name)
            
            # Check if required columns exist
            required_columns = ["Values Reference Range", "DataFrame Column Names"]
            for col in required_columns:
                if col not in self.reference_df.columns:
                    raise ValueError(f"Required column '{col}' not found in reference file")
            
            # Extract cell references
            self._parse_cell_references()
            
        except Exception as e:
            logger.error(f"Error loading reference file: {str(e)}", exc_info=True)
            raise
    
    def _parse_cell_references(self) -> None:
        """
        Parse the cell references from the reference dataframe.
        """
        logger.info("Parsing cell references from reference file")
        
        # Get the cell references and column names
        values_ref_col = "Values Reference Range"
        column_names_col = "DataFrame Column Names"
        
        # Process each row in the reference file
        for idx, row in self.reference_df.iterrows():
            value_ref = row[values_ref_col]
            column_name = row[column_names_col]
            
            # Skip rows with missing data
            if pd.isna(value_ref) or pd.isna(column_name):
                continue
                
            # Parse the cell reference
            reference_info = self._parse_reference_structure(value_ref, column_name)
            if reference_info:
                self.cell_references.append(reference_info)
    
    def _parse_reference_structure(self, value_ref: str, column_name: str) -> Dict[str, Any]:
        """
        Parse a single cell reference structure.
        
        Args:
            value_ref: The cell reference string (e.g., 'Assumptions (Summary)'!$D$6)
            column_name: The name to use for the column in the output DataFrame
            
        Returns:
            Dictionary containing parsed reference information
        """
        try:
            # Check if it's a cell reference or just text
            if "!" in value_ref:
                # It's a cell reference
                sheet_name, cell_address = value_ref.split("!")
                
                # Clean up sheet name (remove quotes)
                sheet_name = sheet_name.strip("'")
                
                # Parse cell address
                is_range = ":" in cell_address
                
                if is_range:
                    # It's a range reference
                    start_cell, end_cell = cell_address.split(":")
                    
                    # Extract column and row from start cell
                    start_col_match = re.search(r"[$]?([A-Z]+)", start_cell)
                    start_row_match = re.search(r"[$]?(\d+)", start_cell)
                    
                    if not start_col_match or not start_row_match:
                        logger.warning(f"Invalid cell address format for start cell: {start_cell}")
                        return None
                        
                    start_col = start_col_match.group(1)
                    start_row = int(start_row_match.group(1))
                    
                    # Extract column and row from end cell
                    end_col_match = re.search(r"[$]?([A-Z]+)", end_cell)
                    end_row_match = re.search(r"[$]?(\d+)", end_cell)
                    
                    if not end_col_match or not end_row_match:
                        logger.warning(f"Invalid cell address format for end cell: {end_cell}")
                        return None
                        
                    end_col = end_col_match.group(1)
                    end_row = int(end_row_match.group(1))
                    
                    # Check if it's a column or row range
                    is_col_range = start_col != end_col
                    is_row_range = start_row != end_row
                    
                    return {
                        "type": "range",
                        "sheet_name": sheet_name,
                        "cell_address": cell_address,
                        "start_col": start_col,
                        "start_row": start_row,
                        "end_col": end_col,
                        "end_row": end_row,
                        "is_col_range": is_col_range,
                        "is_row_range": is_row_range,
                        "column_name": column_name,
                        "original_ref": value_ref
                    }
                    
                else:
                    # It's a single cell reference
                    col_match = re.search(r"[$]?([A-Z]+)", cell_address)
                    row_match = re.search(r"[$]?(\d+)", cell_address)
                    
                    if not col_match or not row_match:
                        logger.warning(f"Invalid cell address format: {cell_address}")
                        return None
                        
                    col = col_match.group(1)
                    row = int(row_match.group(1))
                    
                    return {
                        "type": "single",
                        "sheet_name": sheet_name,
                        "cell_address": cell_address,
                        "col": col,
                        "row": row,
                        "column_name": column_name,
                        "original_ref": value_ref
                    }
            else:
                # It's a text value reference
                return {
                    "type": "text",
                    "value": value_ref,
                    "column_name": column_name,
                    "original_ref": value_ref
                }
                
        except Exception as e:
            logger.error(f"Error parsing reference structure '{value_ref}': {str(e)}")
            return None

class ExcelFileReader:
    """
    Class to read data from Excel files based on cell references.
    """
    
    def __init__(self, file_path: Path, parser: CellReferenceParser):
        """
        Initialize the ExcelFileReader with a file path and parser.
        
        Args:
            file_path: Path to the Excel file
            parser: CellReferenceParser instance containing reference information
        """
        self.file_path = file_path
        self.parser = parser
        self.excel_data = {}
        self.sheet_map = {}  # Mapping between reference sheet names and actual sheet names
    
    def read_excel_file(self) -> Dict[str, Any]:
        """
        Read data from the Excel file according to the reference information.
        
        Returns:
            Dictionary of extracted values
        """
        logger.info(f"Reading Excel file: {self.file_path}")
        
        try:
            # Process according to file type
            if str(self.file_path).lower().endswith('.xlsb'):
                self._read_xlsb_file()
            else:  # .xlsm or other Excel format
                self._read_excel_file_with_pandas()
                
            return self.excel_data
            
        except Exception as e:
            logger.error(f"Error reading Excel file {self.file_path}: {str(e)}", exc_info=True)
            return {}
    
    def _read_excel_file_with_pandas(self) -> None:
        """
        Read Excel file with pandas.
        """
        # Identify unique sheet names to load
        sheet_names = set()
        for ref in self.parser.cell_references:
            if ref["type"] != "text":
                sheet_names.add(ref["sheet_name"])
        
        # Read each required sheet
        sheet_data = {}
        
        # Get all available sheets in the workbook
        try:
            excel_file = pd.ExcelFile(self.file_path)
            all_sheets = excel_file.sheet_names
            
            # Create a mapping of lowercase sheet names to actual sheet names
            self.sheet_map = {sheet.lower(): sheet for sheet in all_sheets}
        except Exception as e:
            logger.error(f"Error reading Excel file structure: {str(e)}")
            return
        
        for sheet_name in sheet_names:
            try:
                # Try exact match first
                if sheet_name in all_sheets:
                    actual_sheet_name = sheet_name
                # Then try case-insensitive match
                elif sheet_name.lower() in self.sheet_map:
                    actual_sheet_name = self.sheet_map[sheet_name.lower()]
                    logger.info(f"Using sheet '{actual_sheet_name}' for reference to '{sheet_name}'")
                # Then try partial match (for incomplete sheet names)
                else:
                    # Check if any sheet name contains the requested sheet name
                    matches = [s for s in all_sheets if sheet_name.lower() in s.lower()]
                    if matches:
                        actual_sheet_name = matches[0]
                        logger.info(f"Using closest match sheet '{actual_sheet_name}' for reference to '{sheet_name}'")
                    else:
                        logger.warning(f"Sheet '{sheet_name}' not found in workbook. Available sheets: {all_sheets}")
                        continue
                        
                sheet_data[sheet_name] = pd.read_excel(
                    self.file_path, 
                    sheet_name=actual_sheet_name,
                    header=None,  # Don't use headers since we're accessing by cell reference
                    engine='openpyxl'  # Use openpyxl for .xlsm files
                )
            except Exception as e:
                logger.warning(f"Could not read sheet '{sheet_name}': {str(e)}")
        
        # Extract values based on references
        self._extract_values_from_sheets(sheet_data)
    
    def _read_xlsb_file(self) -> None:
        """
        Read Excel Binary file (.xlsb).
        """
        if not 'pyxlsb' in sys.modules:
            logger.error("Cannot read .xlsb file: pyxlsb module not available")
            return
            
        # Identify unique sheet names to load
        sheet_names = set()
        for ref in self.parser.cell_references:
            if ref["type"] != "text":
                sheet_names.add(ref["sheet_name"])
        
        # Read each required sheet
        sheet_data = {}
        
        try:
            # First get all available sheet names
            with pyxlsb.open_workbook(self.file_path) as wb:
                all_sheets = wb.sheets
                
                # Create a mapping of lowercase sheet names to actual sheet names
                self.sheet_map = {sheet.lower(): sheet for sheet in all_sheets}
                
                for sheet_name in sheet_names:
                    try:
                        # Try exact match first
                        if sheet_name in all_sheets:
                            actual_sheet_name = sheet_name
                        # Then try case-insensitive match
                        elif sheet_name.lower() in self.sheet_map:
                            actual_sheet_name = self.sheet_map[sheet_name.lower()]
                            logger.info(f"Using sheet '{actual_sheet_name}' for reference to '{sheet_name}'")
                        # Then try partial match (for incomplete sheet names)
                        else:
                            # Check if any sheet name contains the requested sheet name
                            matches = [s for s in all_sheets if sheet_name.lower() in s.lower()]
                            if matches:
                                actual_sheet_name = matches[0]
                                logger.info(f"Using closest match sheet '{actual_sheet_name}' for reference to '{sheet_name}'")
                            else:
                                logger.warning(f"Sheet '{sheet_name}' not found in workbook. Available sheets: {all_sheets}")
                                continue
                    
                        # Read sheet data into a list of lists
                        with wb.get_sheet(actual_sheet_name) as sheet:
                            rows = []
                            for row in sheet.rows():
                                rows.append([cell.v if cell else None for cell in row])
                            
                            # Convert to DataFrame
                            sheet_data[sheet_name] = pd.DataFrame(rows)
                    except Exception as e:
                        logger.warning(f"Could not read sheet '{sheet_name}': {str(e)}")
        except Exception as e:
            logger.error(f"Error opening .xlsb file: {str(e)}")
            return
        
        # Extract values based on references
        self._extract_values_from_sheets(sheet_data)
    
    def _extract_values_from_sheets(self, sheet_data: Dict[str, pd.DataFrame]) -> None:
        """
        Extract values from loaded sheets based on cell references.
        
        Args:
            sheet_data: Dictionary of DataFrames with sheet data
        """
        # Process each reference
        for ref in self.parser.cell_references:
            try:
                if ref["type"] == "text":
                    # Just use the text value directly
                    self.excel_data[ref["column_name"]] = ref["value"]
                    
                elif ref["type"] == "single":
                    # Extract single cell value
                    if ref["sheet_name"] in sheet_data:
                        # Adjust for zero-based indexing in pandas
                        row_idx = ref["row"] - 1
                        col_idx = col_to_num(ref["col"]) - 1
                        
                        if row_idx < len(sheet_data[ref["sheet_name"]]) and col_idx < len(sheet_data[ref["sheet_name"]].columns):
                            value = sheet_data[ref["sheet_name"]].iloc[row_idx, col_idx]
                            self.excel_data[ref["column_name"]] = value
                        else:
                            logger.warning(f"Cell {ref['cell_address']} in sheet {ref['sheet_name']} is out of bounds")
                    else:
                        logger.warning(f"Sheet {ref['sheet_name']} not found in workbook")
                
                elif ref["type"] == "range":
                    # Extract range of values
                    if ref["sheet_name"] in sheet_data:
                        start_row_idx = ref["start_row"] - 1
                        start_col_idx = col_to_num(ref["start_col"]) - 1
                        end_row_idx = ref["end_row"] - 1
                        end_col_idx = col_to_num(ref["end_col"]) - 1
                        
                        # Check if it's a column range or row range
                        if ref["is_col_range"] and not ref["is_row_range"]:
                            # It's a column range with a single row
                            column_name_parts = extract_text_component(ref["column_name"])
                            base_col_name, text_component = column_name_parts
                            
                            for col_idx in range(start_col_idx, end_col_idx + 1):
                                if col_idx < len(sheet_data[ref["sheet_name"]].columns):
                                    col_letter = num_to_col(col_idx + 1)
                                    
                                    # Create column name with text component if it exists
                                    if text_component:
                                        col_name = f"{text_component}{ref['sheet_name']}!${col_letter}${ref['start_row']}"
                                    else:
                                        col_name = f"{base_col_name}_{col_letter}"
                                    
                                    value = sheet_data[ref["sheet_name"]].iloc[start_row_idx, col_idx]
                                    self.excel_data[col_name] = value
                        
                        elif ref["is_row_range"] and not ref["is_col_range"]:
                            # It's a row range with a single column
                            values = []
                            for row_idx in range(start_row_idx, end_row_idx + 1):
                                if row_idx < len(sheet_data[ref["sheet_name"]]):
                                    value = sheet_data[ref["sheet_name"]].iloc[row_idx, start_col_idx]
                                    values.append(value)
                            
                            self.excel_data[ref["column_name"]] = values
                        
                        else:
                            # It's a 2D range
                            values = []
                            for row_idx in range(start_row_idx, end_row_idx + 1):
                                row_values = []
                                for col_idx in range(start_col_idx, end_col_idx + 1):
                                    if (row_idx < len(sheet_data[ref["sheet_name"]]) and 
                                        col_idx < len(sheet_data[ref["sheet_name"]].columns)):
                                        value = sheet_data[ref["sheet_name"]].iloc[row_idx, col_idx]
                                        row_values.append(value)
                                values.append(row_values)
                            
                            self.excel_data[ref["column_name"]] = values
                    else:
                        logger.warning(f"Sheet {ref['sheet_name']} not found in workbook")
            
            except Exception as e:
                logger.error(f"Error extracting values for reference {ref['original_ref']}: {str(e)}")

def process_excel_files(file_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process a list of Excel files and extract data based on cell references.
    
    Args:
        file_list: List of dictionaries with file metadata
        
    Returns:
        DataFrame containing extracted data from all files
    """
    logger.info(f"Processing {len(file_list)} Excel files")
    
    # Initialize parser
    try:
        parser = CellReferenceParser()
    except Exception as e:
        logger.error(f"Error initializing CellReferenceParser: {str(e)}", exc_info=True)
        return pd.DataFrame()
    
    # Process each file
    all_data = []
    for file_info in file_list:
        try:
            file_path = Path(file_info["Absolute File Path"])
            
            # Read data from the Excel file
            reader = ExcelFileReader(file_path, parser)
            excel_data = reader.read_excel_file()
            
            if excel_data:
                # Combine file metadata with extracted data
                combined_data = {**file_info, **excel_data}
                all_data.append(combined_data)
                logger.info(f"Successfully processed file: {file_path.name}")
            else:
                logger.warning(f"No data extracted from file: {file_path.name}")
        
        except Exception as e:
            logger.error(f"Error processing file {file_info['File Name']}: {str(e)}", exc_info=True)
    
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
    from file_finder import find_underwriting_files
    
    print("Finding underwriting files...")
    included_files, _ = find_underwriting_files()
    
    if included_files:
        print(f"Processing {len(included_files)} Excel files...")
        result_df = process_excel_files(included_files)
        
        if not result_df.empty:
            print(f"Extracted data with {len(result_df)} rows and {len(result_df.columns)} columns")
            print("\nColumn names:")
            for col in result_df.columns:
                print(f"- {col}")
            
            # Preview the data
            print("\nData preview:")
            pd.set_option('display.max_columns', 10)
            pd.set_option('display.width', 1000)
            print(result_df.head(5))
        else:
            print("No data extracted from files")
    else:
        print("No files found to process")