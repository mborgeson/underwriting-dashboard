"""
Database Manager Module

This module handles all database operations for the Underwriting Dashboard application,
including creating and maintaining the SQLite database, storing data from Excel files,
updating existing data, and providing query functionality for the dashboard.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Union, Optional
from datetime import datetime

# Import configuration
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))  # Add project root to path
from config.config import DATABASE_PATH, DATABASE_TABLE

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Class to manage database operations for the Underwriting Dashboard.
    """
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        """
        Initialize the DatabaseManager with the database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def connect(self) -> None:
        """
        Connect to the SQLite database.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}", exc_info=True)
            raise
    
    def disconnect(self) -> None:
        """
        Disconnect from the SQLite database.
        """
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from database")
    
    def setup_database(self) -> None:
        """
        Set up the database tables if they don't exist.
        """
        try:
            self.connect()
            
            # Check if the table exists
            self.cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='{DATABASE_TABLE}'
            """)
            
            if not self.cursor.fetchone():
                logger.info(f"Creating table: {DATABASE_TABLE}")
                
                # Create the main data table with minimal fixed columns
                # We'll add additional columns dynamically as needed
                self.cursor.execute(f"""
                    CREATE TABLE {DATABASE_TABLE} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        File_Name TEXT,
                        Absolute_File_Path TEXT,
                        Deal_Stage_Subdirectory_Name TEXT,
                        Deal_Stage_Subdirectory_Path TEXT,
                        Last_Modified_Date TEXT,
                        File_Size_in_Bytes INTEGER,
                        Date_Uploaded TEXT,
                        Metadata TEXT
                    )
                """)
                
                # Create an index on the file path for faster lookups
                self.cursor.execute(f"""
                    CREATE INDEX idx_file_path ON {DATABASE_TABLE} (Absolute_File_Path)
                """)
                
                self.conn.commit()
                logger.info(f"Table {DATABASE_TABLE} created successfully")
            else:
                logger.info(f"Table {DATABASE_TABLE} already exists")
                
        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}", exc_info=True)
            raise
        finally:
            self.disconnect()
    
    def _sanitize_column_name(self, column_name: str) -> str:
        """
        Sanitize column names for use in SQL statements.
        
        Args:
            column_name: Original column name
            
        Returns:
            Sanitized column name
        """
        # Replace spaces, parentheses, and other special characters with underscores
        sanitized = column_name.replace(' ', '_')
        sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in sanitized)
        
        # Make sure it doesn't start with a number
        if sanitized[0].isdigit():
            sanitized = 'col_' + sanitized
            
        # Truncate to a reasonable length if needed
        if len(sanitized) > 63:  # Standard SQL maximum identifier length
            sanitized = sanitized[:63]
            
        return sanitized
    

    def _convert_value_for_sqlite(self, value: Any) -> Any:
        """
        Convert values to types that SQLite can handle.
        
        Args:
            value: The value to convert
            
        Returns:
            SQLite-compatible value
        """
        # Handle pandas Timestamp objects
        if pd.api.types.is_datetime64_any_dtype(type(value)) or hasattr(value, 'tzinfo'):
            return value.isoformat()
        
        # Handle numpy types
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            return float(value)
        if isinstance(value, np.ndarray):
            return value.tolist()
        
        # Return other types as-is
        return value     
    
    
    def _add_column_if_not_exists(self, column_name: str, column_type: str = "TEXT") -> None:
        """
        Add a column to the table if it doesn't already exist.
        
        Args:
            column_name: Name of the column to add
            column_type: SQL type of the column (default is TEXT)
        """
        try:
            # Check if the column exists
            self.cursor.execute(f"PRAGMA table_info({DATABASE_TABLE})")
            columns = [info[1] for info in self.cursor.fetchall()]
            
            sanitized_column = self._sanitize_column_name(column_name)
            
            if sanitized_column not in columns:
                logger.info(f"Adding column: {sanitized_column}")
                self.cursor.execute(f"""
                    ALTER TABLE {DATABASE_TABLE} 
                    ADD COLUMN {sanitized_column} {column_type}
                """)
                self.conn.commit()
        except Exception as e:
            logger.warning(f"Error adding column {column_name}: {str(e)}")
    
    def _ensure_schema_compatibility(self, df: pd.DataFrame) -> None:
        """
        Ensure the database schema is compatible with the DataFrame by adding any missing columns.
        
        Args:
            df: DataFrame to check against database schema
        """
        logger.info("Ensuring schema compatibility")
        
        try:
            # Get current column info from the table
            self.cursor.execute(f"PRAGMA table_info({DATABASE_TABLE})")
            existing_columns = [info[1] for info in self.cursor.fetchall()]
            
            # Check each DataFrame column and add it if not in the table
            for column in df.columns:
                # Skip core columns that we know already exist
                if column in ['File Name', 'Absolute File Path', 'Deal Stage Subdirectory Name', 
                             'Deal Stage Subdirectory Path', 'Last Modified Date', 'File Size in Bytes']:
                    continue
                
                sanitized_column = self._sanitize_column_name(column)
                if sanitized_column not in existing_columns:
                    # Determine column type based on DataFrame dtype
                    dtype = df[column].dtype
                    if pd.api.types.is_integer_dtype(dtype):
                        self._add_column_if_not_exists(column, "INTEGER")
                    elif pd.api.types.is_float_dtype(dtype):
                        self._add_column_if_not_exists(column, "REAL")
                    else:
                        self._add_column_if_not_exists(column, "TEXT")
        except Exception as e:
            logger.error(f"Error ensuring schema compatibility: {str(e)}", exc_info=True)
    
    def store_data(self, df: pd.DataFrame) -> None:
        """
        Store data from a DataFrame into the database.
        
        Args:
            df: DataFrame containing the data to store
        """
        if df.empty:
            logger.warning("Empty DataFrame provided, no data to store")
            return
        
        logger.info(f"Storing {len(df)} rows of data in the database")
        
        try:
            self.connect()
            
            # Ensure all required columns exist in the database
            self._ensure_schema_compatibility(df)
            
            # Process each row in the DataFrame
            current_date = datetime.now().strftime("%m-%d-%Y")
            
            for _, row in df.iterrows():
                file_path = row['Absolute File Path']
                
                # Check if this file is already in the database
                self.cursor.execute(f"""
                    SELECT id FROM {DATABASE_TABLE} 
                    WHERE Absolute_File_Path = ?
                """, (file_path,))
                
                existing_record = self.cursor.fetchone()
                
                # Prepare data for insertion, handling complex types
                row_data = {}
                metadata = {}
                
                for column, value in row.items():
                    sanitized_column = self._sanitize_column_name(column)
                    
                    # Convert complex types to JSON strings for metadata storage
                    if isinstance(value, (list, dict, pd.Series, np.ndarray)):
                        metadata[column] = value
                        continue
                    
                    # Handle NaN, None, etc.
                    if pd.isna(value):
                        row_data[sanitized_column] = None
                    else:
                        # Convert value to SQLite-compatible type
                        row_data[sanitized_column] = self._convert_value_for_sqlite(value)
                
                # Add the upload date
                row_data['Date_Uploaded'] = current_date
                
                # Store metadata as JSON
                row_data['Metadata'] = json.dumps(metadata, default=str)
                
                if existing_record:
                    # Update existing record
                    record_id = existing_record[0]
                    
                    # Construct the SQL update statement
                    set_clause = ", ".join([f"{col} = ?" for col in row_data.keys()])
                    values = list(row_data.values()) + [record_id]
                    
                    update_sql = f"""
                        UPDATE {DATABASE_TABLE}
                        SET {set_clause}
                        WHERE id = ?
                    """
                    
                    self.cursor.execute(update_sql, values)
                    logger.info(f"Updated record for: {file_path}")
                else:
                    # Insert new record
                    columns = ", ".join(row_data.keys())
                    placeholders = ", ".join(["?"] * len(row_data))
                    values = list(row_data.values())
                    
                    insert_sql = f"""
                        INSERT INTO {DATABASE_TABLE} ({columns})
                        VALUES ({placeholders})
                    """
                    
                    self.cursor.execute(insert_sql, values)
                    logger.info(f"Inserted new record for: {file_path}")
            
            # Commit the changes
            self.conn.commit()
            logger.info("Data storage completed successfully")
            
        except Exception as e:
            logger.error(f"Error storing data: {str(e)}", exc_info=True)
            if self.conn:
                self.conn.rollback()
        finally:
            self.disconnect()
    
    def delete_record(self, file_path: str) -> bool:
        """
        Delete a record from the database based on file path.
        
        Args:
            file_path: Absolute path of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.connect()
            
            self.cursor.execute(f"""
                DELETE FROM {DATABASE_TABLE} 
                WHERE Absolute_File_Path = ?
            """, (file_path,))
            
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                logger.info(f"Record deleted for: {file_path}")
                return True
            else:
                logger.warning(f"No record found to delete for: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting record: {str(e)}", exc_info=True)
            if self.conn:
                self.conn.rollback()
            return False
        finally:
            self.disconnect()
    
    def get_all_data(self) -> pd.DataFrame:
        """
        Retrieve all data from the database.
        
        Returns:
            DataFrame containing all data from the database
        """
        try:
            self.connect()
            
            # Get all data from the table
            query = f"SELECT * FROM {DATABASE_TABLE}"
            df = pd.read_sql_query(query, self.conn)
            
            logger.info(f"Retrieved {len(df)} rows from database")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving data: {str(e)}", exc_info=True)
            return pd.DataFrame()
        finally:
            self.disconnect()
    
    def get_filtered_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Retrieve filtered data from the database.
        
        Args:
            filters: Dictionary of column names and values to filter by
            
        Returns:
            DataFrame containing filtered data from the database
        """
        try:
            self.connect()
            
            # Construct WHERE clause from filters
            where_clauses = []
            values = []
            
            for column, value in filters.items():
                sanitized_column = self._sanitize_column_name(column)
                
                if isinstance(value, list):
                    # Handle list of values (IN clause)
                    placeholders = ", ".join(["?"] * len(value))
                    where_clauses.append(f"{sanitized_column} IN ({placeholders})")
                    values.extend(value)
                elif isinstance(value, dict) and value.get('operator') and value.get('value') is not None:
                    # Handle custom operators
                    operator = value['operator']
                    if operator in ['=', '!=', '<', '<=', '>', '>=', 'LIKE']:
                        where_clauses.append(f"{sanitized_column} {operator} ?")
                        values.append(value['value'])
                else:
                    # Simple equality
                    where_clauses.append(f"{sanitized_column} = ?")
                    values.append(value)
            
            # Build the query
            query = f"SELECT * FROM {DATABASE_TABLE}"
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Execute the query
            df = pd.read_sql_query(query, self.conn, params=values)
            
            logger.info(f"Retrieved {len(df)} filtered rows from database")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving filtered data: {str(e)}", exc_info=True)
            return pd.DataFrame()
        finally:
            self.disconnect()
    
    def search_data(self, search_term: str) -> pd.DataFrame:
        """
        Search for data in the database using a full-text search term.
        
        Args:
            search_term: Term to search for across all text columns
            
        Returns:
            DataFrame containing search results
        """
        try:
            self.connect()
            
            # Get all column names from the table
            self.cursor.execute(f"PRAGMA table_info({DATABASE_TABLE})")
            columns = [info[1] for info in self.cursor.fetchall()]
            
            # Only search in TEXT columns
            text_columns = []
            for column in columns:
                try:
                    col_type = self.cursor.execute(f"SELECT typeof({column}) FROM {DATABASE_TABLE} LIMIT 1").fetchone()
                    if col_type and col_type[0].upper() in ['TEXT', 'VARCHAR', 'CHAR', 'CLOB']:
                        text_columns.append(column)
                except:
                    # Skip columns that cause errors
                    pass
            
            # Construct the search query with LIKE clauses for each text column
            search_clauses = []
            values = []
            
            for column in text_columns:
                search_clauses.append(f"{column} LIKE ?")
                values.append(f"%{search_term}%")
            
            if not search_clauses:
                logger.warning("No text columns found for search")
                return pd.DataFrame()
            
            query = f"""
                SELECT * FROM {DATABASE_TABLE}
                WHERE {" OR ".join(search_clauses)}
            """
            
            # Execute the query
            df = pd.read_sql_query(query, self.conn, params=values)
            
            logger.info(f"Found {len(df)} rows matching search term: {search_term}")
            return df
            
        except Exception as e:
            logger.error(f"Error searching data: {str(e)}", exc_info=True)
            return pd.DataFrame()
        finally:
            self.disconnect()
    
def get_column_values(self, column_name: str) -> List[Any]:
    """
    Get unique values for a specific column, useful for populating filters.
    
    Args:
        column_name: Name of the column to get values for
        
    Returns:
        List of unique values for the column
    """
    try:
        self.connect()
        
        sanitized_column = self._sanitize_column_name(column_name)
        
        # Check if the column exists
        self.cursor.execute(f"PRAGMA table_info({DATABASE_TABLE})")
        columns = [info[1] for info in self.cursor.fetchall()]
        
        if sanitized_column not in columns:
            logger.warning(f"Column {column_name} does not exist in the database")
            return []
        
        # Get distinct values
        query = f"SELECT DISTINCT {sanitized_column} FROM {DATABASE_TABLE} WHERE {sanitized_column} IS NOT NULL"
        self.cursor.execute(query)
        
        # Extract values from result
        values = [row[0] for row in self.cursor.fetchall()]
        
        logger.info(f"Retrieved {len(values)} unique values for column: {column_name}")
        return values
        
    except Exception as e:
        logger.error(f"Error getting column values: {str(e)}", exc_info=True)
        return []
    finally:
        self.disconnect()

def setup_database() -> None:
    """
    Set up the database with the required tables.
    """
    try:
        db_manager = DatabaseManager()
        db_manager.setup_database()
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Error in database setup: {str(e)}", exc_info=True)

def store_data(df: pd.DataFrame) -> None:
    """
    Store data from a DataFrame into the database.
    
    Args:
        df: DataFrame containing the data to store
    """
    try:
        db_manager = DatabaseManager()
        db_manager.store_data(df)
        logger.info("Data storage completed successfully")
    except Exception as e:
        logger.error(f"Error in data storage: {str(e)}", exc_info=True)

def get_all_data() -> pd.DataFrame:
    """
    Retrieve all data from the database.
    
    Returns:
        DataFrame containing all data from the database
    """
    try:
        db_manager = DatabaseManager()
        return db_manager.get_all_data()
    except Exception as e:
        logger.error(f"Error retrieving all data: {str(e)}", exc_info=True)
        return pd.DataFrame()

def get_filtered_data(filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Retrieve filtered data from the database.
    
    Args:
        filters: Dictionary of column names and values to filter by
        
    Returns:
        DataFrame containing filtered data from the database
    """
    try:
        db_manager = DatabaseManager()
        return db_manager.get_filtered_data(filters)
    except Exception as e:
        logger.error(f"Error retrieving filtered data: {str(e)}", exc_info=True)
        return pd.DataFrame()

def search_data(search_term: str) -> pd.DataFrame:
    """
    Search for data in the database using a full-text search term.
    
    Args:
        search_term: Term to search for across all text columns
        
    Returns:
        DataFrame containing search results
    """
    try:
        db_manager = DatabaseManager()
        return db_manager.search_data(search_term)
    except Exception as e:
        logger.error(f"Error searching data: {str(e)}", exc_info=True)
        return pd.DataFrame()

if __name__ == "__main__":
    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the database setup
    print("Setting up database...")
    setup_database()
    
    # Import file finder and excel reader for testing
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from data_processing.file_finder import find_underwriting_files
    from data_processing.excel_reader import process_excel_files
    
    print("Finding underwriting files...")
    included_files, _ = find_underwriting_files()
    
    if included_files:
        print(f"Processing the first file: {included_files[0]['File Name']}")
        test_file = [included_files[0]]
        result_df = process_excel_files(test_file)
        
        if not result_df.empty:
            print(f"Storing data with {len(result_df)} rows and {len(result_df.columns)} columns")
            store_data(result_df)
            
            # Test retrieval
            print("Retrieving all data from database...")
            all_data = get_all_data()
            print(f"Retrieved {len(all_data)} rows from database")
            
            # Display columns
            print("\nDatabase columns:")
            print(all_data.columns.tolist()[:10])  # Show first 10 columns
        else:
            print("No data extracted from file to store")
    else:
        print("No files found to process")