#!/usr/bin/env python
"""
Simple script to test importing the dashboard components
"""
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import to verify component loading
print("Testing imports...")
import pandas as pd
from src.services.dashboard_service import DashboardService
from src.config.settings import settings
from src.dashboard.utils.data_processing import process_data_for_display, get_key_metrics

print("\nTesting data retrieval...")
try:
    # Get sample data
    data = DashboardService.get_dashboard_data()
    
    # Print summary
    if data.empty:
        print("WARNING: No data returned from dashboard service")
    else:
        print(f"SUCCESS: Retrieved {len(data)} rows of data")
        print(f"Columns: {list(data.columns)[:5]}...")
        print(f"\nFirst row sample data:")
        print(data.iloc[0][['File_Name', 'Propety_Info__Deal_Name_', 'Propety_Info__Deal_City_']].to_dict())
        
        # Test data processing
        print("\nTesting data processing...")
        processed_data = process_data_for_display(data)
        print(f"Processed data shape: {processed_data.shape}")
        
        # Test metrics
        print("\nTesting metrics calculation...")
        metrics = get_key_metrics(data)
        print(f"Metrics: {metrics}")
        
    print("\nAll tests completed successfully!")
except Exception as e:
    print(f"ERROR: {str(e)}")
    
    # Print more details
    import traceback
    print("\nTraceback:")
    traceback.print_exc()