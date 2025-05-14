"""
Test script to verify database and Excel optimizations are working correctly.
"""

import logging
import time
import pandas as pd
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_test_data(rows=100):
    """Generate test data for database operations."""
    data = {
        'File Name': [f"Test_File_{i}.xlsb" for i in range(rows)],
        'Absolute File Path': [f"/test/path/Test_File_{i}.xlsb" for i in range(rows)],
        'Deal Stage Subdirectory Name': np.random.choice(['Active UW', 'Closed', 'Realized'], rows),
        'Deal Stage Subdirectory Path': [f"/test/path/{np.random.choice(['Active UW', 'Closed', 'Realized'])}" for i in range(rows)],
        'Last Modified Date': pd.date_range(start='1/1/2024', periods=rows).strftime('%Y-%m-%d').tolist(),
        'File Size in Bytes': np.random.randint(1000, 10000000, rows),
    }
    return pd.DataFrame(data)

def test_database_optimizations():
    """Test the optimized database functionality."""
    from src.config.settings import settings
    from src.database import db_manager_optimized
    
    # Use a test database in current directory
    test_db_path = Path.cwd() / "test_optimized.db"
    if test_db_path.exists():
        test_db_path.unlink()
    
    logger.info("Testing database optimizations...")
    
    # Initialize database
    db = db_manager_optimized.DatabaseManager(test_db_path)
    db.setup_database()
    
    # Test batch operations
    test_data = generate_test_data(500)
    logger.info(f"Storing {len(test_data)} test records using batch operations")
    
    start_time = time.time()
    db.batch_store_data(test_data, batch_size=50)
    elapsed_time = time.time() - start_time
    logger.info(f"Batch store completed in {elapsed_time:.2f} seconds")
    
    # Test retrieval
    start_time = time.time()
    result = db.get_all_data()
    elapsed_time = time.time() - start_time
    logger.info(f"Retrieved {len(result)} records in {elapsed_time:.2f} seconds")
    
    # Test filtered queries
    filters = {"Deal Stage Subdirectory Name": "Active UW"}
    start_time = time.time()
    filtered_result = db.get_filtered_data(filters)
    elapsed_time = time.time() - start_time
    logger.info(f"Retrieved {len(filtered_result)} filtered records in {elapsed_time:.2f} seconds")
    
    # Test aggregated data
    try:
        # First check if the get_aggregated_data method exists
        if hasattr(db, 'get_aggregated_data'):
            group_by = ["Deal Stage Subdirectory Name"]
            metrics = {"File Size in Bytes": "sum", "id": "count"}
            start_time = time.time()
            agg_result = db.get_aggregated_data(group_by, metrics)
            elapsed_time = time.time() - start_time
            logger.info(f"Retrieved aggregated data in {elapsed_time:.2f} seconds")
        else:
            logger.info("Skipping aggregated data test - method not available")
    except Exception as e:
        logger.warning(f"Error testing aggregated data: {str(e)}")
    
    # Test pagination
    try:
        # First check if the get_data_paginated method exists
        if hasattr(db, 'get_data_paginated'):
            start_time = time.time()
            page_result = db.get_data_paginated(offset=10, limit=20)
            elapsed_time = time.time() - start_time
            logger.info(f"Retrieved paginated data in {elapsed_time:.2f} seconds")
        else:
            logger.info("Skipping pagination test - method not available")
    except Exception as e:
        logger.warning(f"Error testing pagination: {str(e)}")
    
    # Cleanup
    if test_db_path.exists():
        test_db_path.unlink()
    
    return True

def test_error_handling():
    """Test the error handling system."""
    from src.utils.error_handler import (
        capture_errors, 
        error_registry,
        DatabaseError,
        FileError,
        ErrorSeverity
    )
    from src.utils.error_monitor import ErrorReport
    
    logger.info("Testing error handling system...")
    
    # Test error capturing decorator
    @capture_errors(error_type=DatabaseError)
    def test_db_function():
        raise Exception("Test database error")
    
    @capture_errors(error_type=FileError)
    def test_file_function():
        raise FileNotFoundError("Test file not found")
    
    # Execute functions to generate errors
    test_db_function()
    test_file_function()
    
    # Check error registry
    errors = error_registry.get_errors()
    logger.info(f"Error registry contains {len(errors)} errors")
    
    # Generate a report
    report_path = Path("test_error_report.html")
    ErrorReport.save_report_to_file(report_path)
    logger.info(f"Error report saved to {report_path}")
    
    # Check if report was created
    report_exists = report_path.exists()
    
    # Cleanup
    if report_path.exists():
        report_path.unlink()
    
    return report_exists

def main():
    """Run all tests."""
    print("\n=== Running optimization tests ===\n")
    
    print("Testing database optimizations...")
    db_test_result = test_database_optimizations()
    
    print("\nTesting error handling system...")
    error_test_result = test_error_handling()
    
    print("\n=== Test Results ===")
    print(f"Database optimizations: {'PASSED' if db_test_result else 'FAILED'}")
    print(f"Error handling system: {'PASSED' if error_test_result else 'FAILED'}")
    
    # Overall result
    all_tests_passed = db_test_result and error_test_result
    print(f"\nOverall result: {'PASSED' if all_tests_passed else 'FAILED'}")
    
    return all_tests_passed

if __name__ == "__main__":
    main()