"""
Error Handling System Example

This script demonstrates how to use the error handling system in the 
Underwriting Dashboard application.
"""

import logging
import sys
from pathlib import Path
import time
import random
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import error handling utilities
from src.utils.error_handler import (
    ApplicationError,
    DatabaseError,
    FileError,
    ConfigError,
    ErrorSeverity,
    error_handler,
    capture_errors,
    error_registry
)

from src.utils.error_monitor import (
    ErrorReport,
    EmailReporter,
    error_monitor
)

# Example 1: Using the error_handler decorator
@error_handler(error_type=DatabaseError, severity=ErrorSeverity.ERROR)
def example_database_operation():
    """Simulate a database operation that might fail."""
    logger.info("Attempting database operation...")
    if random.random() < 0.5:
        raise Exception("Database connection failed: Connection timeout")
    
    return "Database operation succeeded"

# Example 2: Using the capture_errors decorator with context
@capture_errors(error_type=FileError, default_return=None)
def example_file_operation(file_path):
    """Simulate a file operation that might fail."""
    logger.info(f"Attempting to read file: {file_path}")
    
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Simulate file operation success
    return f"File {file_path} processed successfully"

# Example 3: Manual error handling
def example_config_operation():
    """Simulate a configuration operation with manual error handling."""
    try:
        logger.info("Checking configuration...")
        
        # Simulate a configuration error
        if random.random() < 0.7:
            missing_key = "IMPORTANT_SETTING"
            raise KeyError(f"Missing required configuration: {missing_key}")
        
        return "Configuration is valid"
        
    except Exception as e:
        # Create and register a custom error
        error = ConfigError(
            message=f"Configuration validation failed: {str(e)}",
            severity=ErrorSeverity.WARNING,
            cause=e,
            details={"timestamp": datetime.now().isoformat()}
        )
        
        # Add to registry
        error_registry.register(error)
        
        # Log the error
        logger.warning(f"Configuration error: {error}")
        
        return None

def main():
    """Main function to demonstrate error handling."""
    print("\n=== Error Handling System Example ===\n")
    
    # Run several operations to demonstrate error handling
    num_iterations = 10
    print(f"Running {num_iterations} iterations of example operations...\n")
    
    for i in range(num_iterations):
        print(f"\nIteration {i+1}:")
        
        # Database operation
        result = example_database_operation()
        print(f"Database operation result: {result}")
        
        # File operation
        file_path = f"/path/to/file_{i}.txt"
        result = example_file_operation(file_path)
        print(f"File operation result: {result}")
        
        # Config operation
        result = example_config_operation()
        print(f"Config operation result: {result}")
        
        # Sleep briefly
        time.sleep(0.1)
    
    # Generate error summary
    print("\n=== Error Summary ===")
    summary = ErrorReport.generate_summary()
    print(f"Total errors: {summary['total_errors']}")
    print(f"By severity: {summary['by_severity']}")
    print(f"By type: {summary['by_type']}")
    
    # Generate and save a report
    report_path = Path("error_report_example.html")
    print(f"\nGenerating error report to {report_path}...")
    ErrorReport.save_report_to_file(report_path)
    print(f"Report saved to {report_path}")
    
    # Analyze errors
    print("\n=== Database Error Analysis ===")
    db_analysis = error_monitor.analyze_database_errors()
    print(f"Database errors: {db_analysis['database_errors']}")
    if db_analysis['database_errors'] > 0:
        print(f"Common patterns: {db_analysis.get('common_patterns', [])}")
    
    print("\n=== File Error Analysis ===")
    file_analysis = error_monitor.analyze_file_errors()
    print(f"File errors: {file_analysis['file_errors']}")
    if file_analysis['file_errors'] > 0:
        print(f"By extension: {file_analysis.get('by_extension', {})}")
    
    print("\nExporting errors to log file...")
    error_registry.export_to_log(Path("example_error_log.txt"))
    print("Errors exported to example_error_log.txt")
    
    print("\nError handling example completed.")
    print("Open error_report_example.html in a browser to view the HTML error report.")

if __name__ == "__main__":
    main()