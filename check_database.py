"""
Script to check database contents and troubleshoot dashboard data issues.
"""

import pandas as pd
import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.database.db_manager_optimized import DatabaseManager, get_all_data, store_data

def check_database():
    """Check if the database has data and display useful information."""
    print("Checking database...")
    
    try:
        # Initialize the database manager
        db_manager = DatabaseManager()
        
        # Check if the database file exists
        if not db_manager.db_path.exists():
            print(f"Database file does not exist at: {db_manager.db_path}")
            return False
            
        # Connect to the database
        db_manager.connect()
        
        # Get table information
        db_manager.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table'")
        tables = db_manager.cursor.fetchall()
        print(f"Available tables: {tables}")
        
        # Get row count
        row_count = db_manager.get_row_count()
        print(f"Total rows in {db_manager.table_name}: {row_count}")
        
        if row_count == 0:
            print("No data found in the database. Let's create some sample data.")
            create_sample_data()
            return
            
        # Get column information
        columns = db_manager._get_columns()
        print(f"Available columns: {columns}")
        
        # Get a sample of the data safely
        try:
            db_manager.cursor.execute(f"SELECT * FROM {db_manager.table_name} LIMIT 5")
            sample_data = db_manager.cursor.fetchall()
            print("\nSample data (first 5 rows):")
            for row in sample_data:
                print(row)
        except Exception as e:
            print(f"Error fetching sample data: {str(e)}")
            
            # Try an alternative approach
            print("Trying alternative approach to get sample data...")
            try:
                # Reconnect to ensure we have a valid connection
                db_manager.disconnect()
                db_manager.connect()
                
                # Execute the query
                db_manager.cursor.execute(f"SELECT * FROM {db_manager.table_name} LIMIT 5")
                sample_data = db_manager.cursor.fetchall()
                print("Sample data (first 5 rows):")
                for row in sample_data:
                    print(row)
            except Exception as inner_e:
                print(f"Alternative approach also failed: {str(inner_e)}")
            
        # Load all data using the get_all_data function
        print("\nTrying to load all data with get_all_data()...")
        all_data = get_all_data()
        print(f"get_all_data() returned a DataFrame with {len(all_data)} rows and {len(all_data.columns)} columns")
        
        if len(all_data) > 0:
            print(f"Column names: {all_data.columns.tolist()}")
            print("\nFirst row:")
            print(all_data.iloc[0])
            
        db_manager.disconnect()
        return True
        
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_data():
    """Create sample data in the database for testing."""
    print("Creating sample data...")
    
    # Create a test DataFrame
    data = {
        'File Name': [f"Test_File_{i}.xlsb" for i in range(10)],
        'Absolute File Path': [f"/test/path/Test_File_{i}.xlsb" for i in range(10)],
        'Deal Stage Subdirectory Name': ['Active UW', 'Closed', 'Active UW', 'Under Contract', 'Closed', 
                                         'Realized', 'Initial UW', 'Active UW', 'Under Contract', 'Closed'],
        'Deal Stage Subdirectory Path': [f"/test/path/{stage}" for stage in 
                                        ['Active UW', 'Closed', 'Active UW', 'Under Contract', 'Closed', 
                                         'Realized', 'Initial UW', 'Active UW', 'Under Contract', 'Closed']],
        'Last Modified Date': pd.date_range(start='1/1/2024', periods=10).strftime('%Y-%m-%d').tolist(),
        'File Size in Bytes': [i * 100000 for i in range(10)],
        'Purchase Price': [i * 5000000 for i in range(10)],
        'Cap Rate': [0.05 + (i * 0.005) for i in range(10)],
        'IRR': [0.15 + (i * 0.01) for i in range(10)],
        'NOI': [i * 250000 for i in range(10)],
        'Property Type': ['Multifamily', 'Office', 'Retail', 'Industrial', 'Multifamily', 
                         'Office', 'Retail', 'Industrial', 'Multifamily', 'Office'],
        'Market': ['Phoenix', 'Chicago', 'Atlanta', 'New York', 'Los Angeles', 
                  'Dallas', 'Boston', 'Seattle', 'Denver', 'Miami'],
        'State': ['AZ', 'IL', 'GA', 'NY', 'CA', 'TX', 'MA', 'WA', 'CO', 'FL']
    }
    
    df = pd.DataFrame(data)
    
    # Store in database
    try:
        store_data(df)
        print(f"Successfully added {len(df)} sample records to the database")
        
        # Verify the data was added
        all_data = get_all_data()
        print(f"Database now has {len(all_data)} records")
        
    except Exception as e:
        print(f"Error creating sample data: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()