#!/usr/bin/env python
"""
Script to check database schema
"""
import sqlite3
import sys
from pathlib import Path

# Database path
db_path = Path(__file__).parent / "database" / "underwriting_models.db"
print(f"Checking database at: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Get schema for each table
for table_name in [t[0] for t in tables]:
    print(f"\nSchema for {table_name}:")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

# Get sample data from underwriting_model_data
try:
    print("\nSample data from underwriting_model_data:")
    cursor.execute("SELECT * FROM underwriting_model_data LIMIT 3;")
    sample_data = cursor.fetchall()
    if sample_data:
        # Get column names
        cursor.execute("PRAGMA table_info(underwriting_model_data);")
        col_names = [col[1] for col in cursor.fetchall()]
        print(f"Columns: {col_names}")
        
        # Print sample data
        for row in sample_data:
            print(f"\nRow data:")
            for i, value in enumerate(row):
                if i < len(col_names):
                    print(f"  {col_names[i]}: {value}")
    else:
        print("No data found in table")
except Exception as e:
    print(f"Error getting sample data: {str(e)}")

# Close connection
conn.close()