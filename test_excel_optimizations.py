"""
Test script to verify Excel processing optimizations are working correctly.
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

def test_excel_processing():
    """Test the optimized Excel processing functionality without actual files."""
    from src.data_processing.excel_reader_optimized import OptimizedExcelFileReader, get_reference_parser
    
    # Test the parser cache functionality
    logger.info("Testing reference parser caching...")
    start_time = time.time()
    parser1 = get_reference_parser()
    elapsed_time1 = time.time() - start_time
    
    start_time = time.time()
    parser2 = get_reference_parser()
    elapsed_time2 = time.time() - start_time
    
    # Second call should be significantly faster if caching works
    logger.info(f"First parser creation: {elapsed_time1:.6f}s")
    logger.info(f"Second parser creation (cached): {elapsed_time2:.6f}s")
    
    # Verify it's the same object (memory address)
    is_same_object = parser1 is parser2
    logger.info(f"Parsers are the same object: {is_same_object}")
    
    return is_same_object

def main():
    """Run the tests."""
    print("\n=== Testing Excel Processing Optimizations ===\n")
    
    excel_test_result = test_excel_processing()
    
    print("\n=== Test Results ===")
    print(f"Excel optimizations: {'PASSED' if excel_test_result else 'FAILED'}")
    
    return excel_test_result

if __name__ == "__main__":
    main()