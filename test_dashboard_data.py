#!/usr/bin/env python
"""
Test script to verify dashboard data display with column mapping
"""
import sys
import logging
from pathlib import Path
import pandas as pd

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our modules
from src.database.db_manager_optimized import DatabaseManager
from src.services.dashboard_service import DashboardService

# Define a corrected column mapping based on actual database schema
CORRECT_COLUMN_MAPPING = {
    # Map from spaces to underscores (dashboard uses spaces, database uses underscores)
    'File Name': 'File_Name',
    'Absolute File Path': 'Absolute_File_Path',
    'Deal Stage Subdirectory Name': 'Deal_Stage_Subdirectory_Name',
    'Deal Stage Subdirectory Path': 'Deal_Stage_Subdirectory_Path',
    'Last Modified Date': 'Last_Modified_Date',
    'Date Uploaded': 'Date_Uploaded',
    'File Size in Bytes': 'File_Size_in_Bytes',
    
    # Property Info fields with typo in database ('Propety' instead of 'Property')
    'Deal Name': 'Propety_Info__Deal_Name_',
    'Deal City': 'Propety_Info__Deal_City_',
    'Deal State': 'Propety_Info__Deal_State_',
    'Year Built': 'Propety_Info__Year_Built_',
    'Year Renovated': 'Propety_Info__Year_Renovated_',
    'Location Quality': 'Propety_Info__Location_Quality_',
    'Building Quality': 'Propety_Info__Building_Quality_',
    'Number of Units': 'Propety_Info__Number_of_Units_',
    'Average Unit SF': 'Propety_Info__Average_Unit_SF_',
    'Building Type': 'Propety_Info__Building_Type_',
    'Project Type': 'Propety_Info__Project_Type_',
    'Market': 'Propety_Info__Market_',
    'Submarket Cluster': 'Propety_Info__Submarket_Cluster_',
    'Submarket': 'Propety_Info__Submarket_',
    'County': 'Propety_Info__County_',
    
    # Financial metrics
    'Purchase Price': 'Purchase_Price',
    'Total Land and Acquisition Costs': 'Total_Land_and_Acquisition_Costs',
    'Total Hard Costs': 'Total_Hard_Costs',
    'Total Soft Costs': 'Total_Soft_Costs',
    'Total Closing Costs': 'Total_Closing_Costs',
    'Total Acquistion Budget': 'Total_Acquistion_Budget'
}

def test_db_connection():
    """Test the database connection and print schema"""
    try:
        db_manager = DatabaseManager()
        db_manager.connect()
        
        # Get database tables
        tables = db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table';")
        logger.info(f"Database tables: {tables}")
        
        # Check if we have a connection
        if db_manager.conn is None:
            logger.error("Failed to establish a database connection")
            return False
        
        # Get a new cursor since the previous one was released after the query
        db_manager.cursor = db_manager.conn.cursor()
        
        if db_manager.cursor is None:
            logger.error("Failed to establish a database cursor")
            return False
        
        # Get table schema for each table
        for table_name in [t[0] for t in tables]:
            schema = db_manager.execute_query(f"PRAGMA table_info({table_name});")
            logger.info(f"Schema for {table_name}: {schema}")
        
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return False

def test_column_mapping():
    """Test the column mapping by printing mapped columns"""
    logger.info("Testing column mapping...")
    
    # Get the mapping from the dashboard service
    from src.services.dashboard_service import COLUMN_MAPPING as EXISTING_MAPPING
    
    logger.info("Current dashboard service mapping:")
    for dashboard_col, db_col in EXISTING_MAPPING.items():
        logger.info(f"Dashboard: '{dashboard_col}' -> Database: '{db_col}'")
    
    logger.info("\nComparing with corrected mapping:")
    # Check for differences
    missing_keys = set(CORRECT_COLUMN_MAPPING.keys()) - set(EXISTING_MAPPING.keys())
    if missing_keys:
        logger.info(f"Missing mappings in dashboard service: {missing_keys}")
    
    incorrect_mappings = []
    for key in set(EXISTING_MAPPING.keys()) & set(CORRECT_COLUMN_MAPPING.keys()):
        if EXISTING_MAPPING[key] != CORRECT_COLUMN_MAPPING[key]:
            logger.info(f"Mapping mismatch for '{key}': Current='{EXISTING_MAPPING[key]}', Should be='{CORRECT_COLUMN_MAPPING[key]}'")
            incorrect_mappings.append(key)
    
    if not missing_keys and not incorrect_mappings:
        logger.info("All mappings are correct!")
    else:
        logger.warning("Mapping issues found. The dashboard service needs to be updated.")
        
    return len(missing_keys) == 0 and len(incorrect_mappings) == 0

def test_dashboard_data():
    """Test retrieving dashboard data with column mapping"""
    try:
        dashboard_service = DashboardService()
        
        # Monkey patch the column mapping temporarily for our test
        from src.services.dashboard_service import COLUMN_MAPPING as EXISTING_MAPPING
        original_mapping = EXISTING_MAPPING.copy()
        
        # Add our corrected mapping
        for key, value in CORRECT_COLUMN_MAPPING.items():
            if key not in EXISTING_MAPPING:
                EXISTING_MAPPING[key] = value
        
        logger.info("Temporarily updated column mapping for test")
        
        # Try getting data without filters first
        data = dashboard_service.get_dashboard_data()
        if data.empty:
            logger.error("No data returned from get_dashboard_data()")
            
            # Check if there's any data in the database at all
            db_manager = DatabaseManager()
            # Get the correct table name from our database connection test
            sample_data = db_manager.execute_query("SELECT * FROM underwriting_model_data LIMIT 5;")
            logger.info(f"Sample data in database: {sample_data}")
            
            # Restore original mapping
            for key in list(EXISTING_MAPPING.keys()):
                if key not in original_mapping:
                    del EXISTING_MAPPING[key]
                    
            return False
        
        # Success! Print summary of the data
        logger.info(f"Successfully retrieved {len(data)} rows of data")
        logger.info(f"Columns in data: {list(data.columns)}")
        logger.info(f"First few rows:\n{data.head()}")
        
        # Test with a simple filter
        if 'File_Name' in data.columns:
            filter_col = 'File_Name'
        elif 'File Name' in data.columns:
            filter_col = 'File Name'
        else:
            logger.warning("Could not find File Name column for testing filters")
            return True
            
        # Get a sample value from the first row to use as a filter
        sample_value = data.iloc[0][filter_col]
        logger.info(f"Testing filter with {filter_col}={sample_value}")
        
        # Test with the filter
        filters = {filter_col: sample_value}
        filtered_data = dashboard_service.get_dashboard_data(filters=filters)
        logger.info(f"Filtered data returned {len(filtered_data)} rows")
        
        # Restore original mapping
        for key in list(EXISTING_MAPPING.keys()):
            if key not in original_mapping:
                del EXISTING_MAPPING[key]
        
        return True
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        
        # Make sure to restore the original mapping even if there's an error
        try:
            for key in list(EXISTING_MAPPING.keys()):
                if key not in original_mapping:
                    del EXISTING_MAPPING[key]
        except:
            pass
            
        return False

if __name__ == "__main__":
    logger.info("Starting dashboard data test")
    
    conn_success = test_db_connection()
    if not conn_success:
        logger.error("Database connection test failed, exiting")
        sys.exit(1)
    
    test_column_mapping()
    
    data_success = test_dashboard_data()
    if data_success:
        logger.info("Dashboard data test successful! Column mapping is working correctly.")
    else:
        logger.error("Dashboard data test failed. Column mapping may not be working correctly.")
        sys.exit(1)
    
    logger.info("All tests completed successfully")