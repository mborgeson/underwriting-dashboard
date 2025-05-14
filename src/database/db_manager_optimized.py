"""
Optimized Database Manager Module

This module provides an optimized implementation of database operations for the
Underwriting Dashboard, including connection pooling, batch operations, and
improved query performance.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import logging
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Tuple, Union, Optional, Callable
from datetime import datetime
from contextlib import contextmanager
from functools import lru_cache

# Import configuration
from src.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool = {}
_connection_lock = threading.Lock()

class DatabaseManager:
    """
    Optimized class to manage database operations for the Underwriting Dashboard.
    Includes connection pooling, prepared statements, and batch operations.
    """
    
    def __init__(self, db_path: Path = None):
        """
        Initialize the DatabaseManager with the database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path or settings.database_path
        self.table_name = settings.database_table
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connection and cursor
        self.conn = None
        self.cursor = None
        
        # Prepared statements cache
        self._prepared_statements = {}
        
        # Column cache
        self._column_cache = None
        self._column_cache_time = 0
        self._column_cache_ttl = 60  # Cache TTL in seconds
        
        # Initialize indexes cache
        self._indexes = set()
        
    @contextmanager
    def connection(self):
        """
        Context manager for database connections.
        
        Yields:
            SQLite connection object
        """
        conn = self._get_connection()
        try:
            yield conn
        finally:
            # Connection is returned to the pool, not closed
            pass
    
    def _get_connection(self):
        """
        Get a connection from the pool or create a new one.
        
        Returns:
            SQLite connection object
        """
        thread_id = threading.get_ident()
        
        with _connection_lock:
            if thread_id not in _connection_pool:
                # Create a new connection for this thread
                conn = sqlite3.connect(self.db_path)
                
                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Optimize SQLite settings
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA cache_size = 10000")
                conn.execute("PRAGMA temp_store = MEMORY")
                
                # Register adapters and converters
                sqlite3.register_adapter(np.int64, lambda val: int(val))
                sqlite3.register_adapter(np.float64, lambda val: float(val))
                
                # Store the connection in the pool
                _connection_pool[thread_id] = conn
                logger.debug(f"Created new database connection for thread {thread_id}")
            
            return _connection_pool[thread_id]
    
    def connect(self):
        """
        Connect to the SQLite database.
        """
        try:
            # If we already have a valid connection and cursor, don't reconnect
            if self.conn is not None and self.cursor is not None:
                try:
                    # Test the connection with a simple query
                    self.cursor.execute("SELECT 1")
                    return  # Connection is good, no need to reconnect
                except sqlite3.Error:
                    # Connection is stale, continue with reconnection
                    logger.warning("Stale database connection detected, reconnecting...")
                    self.cursor = None
            
            # Get a connection from the pool
            self.conn = self._get_connection()
            
            # Create a new cursor
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
            
            # Load indexes into cache
            self._load_indexes()
            
        except sqlite3.Error as se:
            logger.error(f"SQLite error connecting to database: {str(se)}", exc_info=True)
            self.cursor = None
            self.conn = None
            raise
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}", exc_info=True)
            self.cursor = None
            self.conn = None
            raise
    
    def disconnect(self):
        """
        Disconnect from the SQLite database.
        Note: In connection pooling, we don't actually close the connection,
        but we do release the cursor.
        """
        if self.cursor is not None:
            try:
                self.cursor.close()
            except Exception as e:
                logger.warning(f"Error closing cursor: {str(e)}")
            finally:
                self.cursor = None
                logger.info("Database cursor released")
    
    def _load_indexes(self):
        """
        Load existing indexes into cache.
        """
        if self.cursor is None:
            logger.warning("Cannot load indexes - cursor is None")
            self._indexes = set()
            return
            
        try:
            # Verify the cursor is valid with a simple test
            try:
                self.cursor.execute("SELECT 1")
            except sqlite3.Error:
                logger.warning("Invalid cursor detected when loading indexes, reconnecting...")
                self.connect()
                if self.cursor is None:
                    logger.error("Failed to reconnect when loading indexes")
                    self._indexes = set()
                    return
                    
            # Load indexes
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{self.table_name}'")
            self._indexes = {row[0] for row in self.cursor.fetchall()}
            logger.debug(f"Loaded {len(self._indexes)} indexes into cache")
        except sqlite3.Error as se:
            logger.warning(f"SQLite error loading indexes: {str(se)}")
            self._indexes = set()
        except Exception as e:
            logger.warning(f"Error loading indexes: {str(e)}", exc_info=True)
            self._indexes = set()
    
    def _ensure_index(self, column_name: str, unique: bool = False):
        """
        Create an index on the column if it doesn't exist.
        
        Args:
            column_name: Column to create index on
            unique: Whether the index should be unique
        """
        sanitized_column = self._sanitize_column_name(column_name)
        index_name = f"idx_{self.table_name}_{sanitized_column}"
        
        # Check cache first
        if index_name in self._indexes:
            return
            
        # Create connection if needed
        if self.cursor is None:
            try:
                self.connect()
            except Exception as e:
                logger.error(f"Failed to connect when creating index: {str(e)}")
                return
                
        try:
            # Verify the cursor is valid
            if self.cursor is None:
                logger.error("No valid cursor available for creating index")
                return
                
            # Create the index
            unique_str = "UNIQUE" if unique else ""
            self.cursor.execute(f"CREATE {unique_str} INDEX IF NOT EXISTS {index_name} ON {self.table_name} ({sanitized_column})")
            self.conn.commit()
            
            # Update the index cache
            self._indexes.add(index_name)
            logger.info(f"Created index on column {sanitized_column}")
            
        except sqlite3.Error as se:
            logger.warning(f"SQLite error creating index on {sanitized_column}: {str(se)}")
            # If there's a connection error, force reconnection next time
            self.cursor = None
        except Exception as e:
            logger.warning(f"Error creating index on {sanitized_column}: {str(e)}", exc_info=True)
    
    def setup_database(self):
        """
        Set up the database tables if they don't exist.
        """
        try:
            self.connect()
            
            # Check if the table exists
            self.cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='{self.table_name}'
            """)
            
            if not self.cursor.fetchone():
                logger.info(f"Creating table: {self.table_name}")
                
                # Create the main data table with minimal fixed columns
                # We'll add additional columns dynamically as needed
                self.cursor.execute(f"""
                    CREATE TABLE {self.table_name} (
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
                
                # Create indexes on frequently queried columns
                self._ensure_index("Absolute_File_Path")
                self._ensure_index("Deal_Stage_Subdirectory_Name")
                self._ensure_index("Last_Modified_Date")
                
                self.conn.commit()
                logger.info(f"Table {self.table_name} created successfully")
            else:
                logger.info(f"Table {self.table_name} already exists")
                
                # Create indexes if they don't exist
                self._ensure_index("Absolute_File_Path")
                self._ensure_index("Deal_Stage_Subdirectory_Name")
                self._ensure_index("Last_Modified_Date")
                
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
        if sanitized and sanitized[0].isdigit():
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
    
    def _get_columns(self, refresh: bool = False) -> List[str]:
        """
        Get the list of columns in the database table with caching.
        
        Args:
            refresh: Whether to force refresh the cache
            
        Returns:
            List of column names
        """
        current_time = time.time()
        
        # Return cached columns if available and not expired
        if not refresh and self._column_cache is not None and (current_time - self._column_cache_time) < self._column_cache_ttl:
            return self._column_cache
        
        # Track whether we need to disconnect at the end
        created_connection = False
        
        try:
            # Make sure we have a connection and cursor
            if self.conn is None or self.cursor is None:
                self.connect()
                created_connection = True
                
            # Double-check that cursor is available after connection attempt
            if self.cursor is None:
                logger.error("Failed to establish a database cursor")
                return self._column_cache or []
                
            # Execute the pragma query to get column info
            self.cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = [info[1] for info in self.cursor.fetchall()]
            
            # Update cache
            self._column_cache = columns
            self._column_cache_time = current_time
            
            return columns
        except sqlite3.Error as se:
            logger.error(f"SQLite error getting columns: {str(se)}")
            # If we have a connection error, force reconnection on next attempt
            self.cursor = None
            return self._column_cache or []
        except Exception as e:
            logger.error(f"Error getting columns: {str(e)}", exc_info=True)
            # Return empty list or cached columns if available
            return self._column_cache or []
        finally:
            # Only disconnect if we created the connection in this method
            if created_connection:
                self.disconnect()
    
    def _add_column_if_not_exists(self, column_name: str, column_type: str = "TEXT") -> None:
        """
        Add a column to the table if it doesn't already exist.
        
        Args:
            column_name: Name of the column to add
            column_type: SQL type of the column (default is TEXT)
        """
        try:
            # Get current columns (cached)
            columns = self._get_columns()
            
            sanitized_column = self._sanitize_column_name(column_name)
            
            if sanitized_column not in columns:
                logger.info(f"Adding column: {sanitized_column}")
                self.cursor.execute(f"""
                    ALTER TABLE {self.table_name} 
                    ADD COLUMN {sanitized_column} {column_type}
                """)
                self.conn.commit()
                
                # Invalidate column cache
                self._column_cache = None
                
        except Exception as e:
            logger.warning(f"Error adding column {column_name}: {str(e)}")
    
    def _ensure_schema_compatibility(self, df: pd.DataFrame) -> None:
        """
        Ensure the database schema is compatible with the DataFrame by adding any missing columns.
        Optimized to check all columns in a single pass.
        
        Args:
            df: DataFrame to check against database schema
        """
        logger.info("Ensuring schema compatibility")
        
        try:
            # Get current columns
            existing_columns = self._get_columns(refresh=True)
            
            # Batch add missing columns
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
    
    def batch_store_data(self, df: pd.DataFrame, batch_size: int = 50) -> None:
        """
        Store data from a DataFrame into the database using batch operations.
        
        Args:
            df: DataFrame containing the data to store
            batch_size: Number of records to process in each batch
        """
        if df.empty:
            logger.warning("Empty DataFrame provided, no data to store")
            return
        
        logger.info(f"Batch storing {len(df)} rows of data in the database")
        
        try:
            self.connect()
            
            # Ensure all required columns exist in the database
            self._ensure_schema_compatibility(df)
            
            # Process rows in batches
            current_date = datetime.now().strftime("%m-%d-%Y")
            
            # Get all existing file paths in one query
            self.cursor.execute(f"""
                SELECT Absolute_File_Path, id FROM {self.table_name}
            """)
            existing_files = dict(self.cursor.fetchall())
            
            # Prepare data for batch operations
            updates = []
            inserts = []
            
            for _, row in df.iterrows():
                file_path = row['Absolute File Path']
                
                # Prepare data, handling complex types
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
                
                # Check if this file is already in the database
                if file_path in existing_files:
                    # Update existing record
                    record_id = existing_files[file_path]
                    updates.append((row_data, record_id))
                else:
                    # Insert new record
                    inserts.append(row_data)
            
            # Process updates in batches
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i+batch_size]
                if not batch:
                    continue
                
                # Group updates with the same columns
                update_groups = {}
                for row_data, record_id in batch:
                    columns_key = tuple(sorted(row_data.keys()))
                    if columns_key not in update_groups:
                        update_groups[columns_key] = []
                    update_groups[columns_key].append((row_data, record_id))
                
                # Execute each group separately
                for columns_key, group in update_groups.items():
                    # Construct the SQL update statement
                    set_clause = ", ".join([f"{col} = ?" for col in columns_key])
                    update_sql = f"""
                        UPDATE {self.table_name}
                        SET {set_clause}
                        WHERE id = ?
                    """
                    
                    # Prepare batch parameters
                    batch_params = []
                    for row_data, record_id in group:
                        params = [row_data[col] for col in columns_key]
                        params.append(record_id)
                        batch_params.append(params)
                    
                    # Execute batch update
                    for params in batch_params:
                        self.cursor.execute(update_sql, params)
                    
                    logger.info(f"Updated {len(group)} records in batch")
            
            # Process inserts in batches
            for i in range(0, len(inserts), batch_size):
                batch = inserts[i:i+batch_size]
                if not batch:
                    continue
                
                # Group inserts with the same columns
                insert_groups = {}
                for row_data in batch:
                    columns_key = tuple(sorted(row_data.keys()))
                    if columns_key not in insert_groups:
                        insert_groups[columns_key] = []
                    insert_groups[columns_key].append(row_data)
                
                # Execute each group separately
                for columns_key, group in insert_groups.items():
                    columns = list(columns_key)
                    columns_str = ", ".join(columns)
                    placeholders = ", ".join(["?"] * len(columns))
                    insert_sql = f"""
                        INSERT INTO {self.table_name} ({columns_str})
                        VALUES ({placeholders})
                    """
                    
                    # Prepare batch parameters
                    batch_params = []
                    for row_data in group:
                        params = [row_data[col] for col in columns]
                        batch_params.append(params)
                    
                    # Execute batch insert
                    self.cursor.executemany(insert_sql, batch_params)
                    
                    logger.info(f"Inserted {len(group)} new records in batch")
            
            # Commit the changes
            self.conn.commit()
            logger.info("Batch data storage completed successfully")
            
        except Exception as e:
            logger.error(f"Error in batch store_data: {str(e)}", exc_info=True)
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            self.disconnect()
    
    def store_data(self, df: pd.DataFrame) -> None:
        """
        Store data from a DataFrame into the database, using batch operations.
        
        Args:
            df: DataFrame containing the data to store
        """
        return self.batch_store_data(df)
    
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
                DELETE FROM {self.table_name} 
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
    
    def batch_delete_records(self, file_paths: List[str]) -> int:
        """
        Delete multiple records from the database based on file paths.
        
        Args:
            file_paths: List of absolute file paths to delete
            
        Returns:
            Number of records deleted
        """
        if not file_paths:
            return 0
            
        try:
            self.connect()
            
            # Prepare the SQL with parameterized query
            placeholders = ', '.join(['?'] * len(file_paths))
            delete_sql = f"""
                DELETE FROM {self.table_name} 
                WHERE Absolute_File_Path IN ({placeholders})
            """
            
            self.cursor.execute(delete_sql, file_paths)
            self.conn.commit()
            
            deleted_count = self.cursor.rowcount
            logger.info(f"Deleted {deleted_count} records in batch")
            return deleted_count
                
        except Exception as e:
            logger.error(f"Error in batch delete: {str(e)}", exc_info=True)
            if self.conn:
                self.conn.rollback()
            return 0
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
            
            # Use a more optimized query with limit/offset
            query = f"SELECT * FROM {self.table_name}"
            df = pd.read_sql_query(query, self.conn)
            
            logger.info(f"Retrieved {len(df)} rows from database")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving data: {str(e)}", exc_info=True)
            return pd.DataFrame()
        finally:
            self.disconnect()
    
    def get_data_paginated(self, offset: int = 0, limit: int = 100, order_by: str = None) -> pd.DataFrame:
        """
        Retrieve paginated data from the database.
        
        Args:
            offset: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column to sort by
            
        Returns:
            DataFrame containing paginated data from the database
        """
        try:
            self.connect()
            
            # Construct the query with pagination
            query = f"SELECT * FROM {self.table_name}"
            
            # Add ordering if specified
            if order_by:
                sanitized_order = self._sanitize_column_name(order_by)
                query += f" ORDER BY {sanitized_order}"
            
            # Add pagination
            query += f" LIMIT {limit} OFFSET {offset}"
            
            df = pd.read_sql_query(query, self.conn)
            
            logger.info(f"Retrieved {len(df)} rows from database (paginated)")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving paginated data: {str(e)}", exc_info=True)
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
                
                # Add index for this column if it's frequently filtered
                if column in ['Deal_Stage_Subdirectory_Name', 'Last_Modified_Date']:
                    self._ensure_index(sanitized_column)
                
                if isinstance(value, list):
                    # Handle list of values (IN clause)
                    placeholders = ", ".join(["?"] * len(value))
                    where_clauses.append(f"{sanitized_column} IN ({placeholders})")
                    values.extend(value)
                elif isinstance(value, dict) and value.get('operator') and value.get('value') is not None:
                    # Handle custom operators
                    operator = value['operator']
                    if operator == 'BETWEEN' and isinstance(value['value'], tuple) and len(value['value']) == 2:
                        where_clauses.append(f"{sanitized_column} BETWEEN ? AND ?")
                        values.extend(value['value'])
                    elif operator in ['=', '!=', '<', '<=', '>', '>=', 'LIKE']:
                        where_clauses.append(f"{sanitized_column} {operator} ?")
                        values.append(value['value'])
                else:
                    # Simple equality
                    where_clauses.append(f"{sanitized_column} = ?")
                    values.append(value)
            
            # Build the query
            query = f"SELECT * FROM {self.table_name}"
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
        Optimized search for data in the database using a full-text search.
        
        Args:
            search_term: Term to search for across all text columns
            
        Returns:
            DataFrame containing search results
        """
        try:
            self.connect()
            
            # Get text columns more efficiently with column cache
            columns = self._get_columns()
            
            # Only search in TEXT columns - use type detection to avoid extra queries
            self.cursor.execute(f"SELECT * FROM {self.table_name} LIMIT 1")
            column_types = {column[0]: column[1] for column in self.cursor.description}
            
            text_columns = [col for col in columns if col in column_types and 
                            isinstance(column_types[col], str) and 
                            column_types[col].upper() in ['TEXT', 'VARCHAR', 'CHAR', 'CLOB']]
            
            if not text_columns:
                logger.warning("No text columns found for search")
                return pd.DataFrame()
            
            # Construct the search query with LIKE clauses for each text column
            search_clauses = []
            values = []
            
            for column in text_columns:
                search_clauses.append(f"{column} LIKE ?")
                values.append(f"%{search_term}%")
            
            query = f"""
                SELECT * FROM {self.table_name}
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
    
    @lru_cache(maxsize=32)
    def get_column_values(self, column_name: str) -> List[Any]:
        """
        Get unique values for a specific column, useful for populating filters.
        Uses LRU caching for improved performance.
        
        Args:
            column_name: Name of the column to get values for
            
        Returns:
            List of unique values for the column
        """
        try:
            self.connect()
            
            sanitized_column = self._sanitize_column_name(column_name)
            
            # Check if the column exists using the column cache
            columns = self._get_columns()
            
            if sanitized_column not in columns:
                logger.warning(f"Column {column_name} does not exist in the database")
                return []
            
            # Get distinct values with an index if frequently queried
            self._ensure_index(sanitized_column)
            
            query = f"SELECT DISTINCT {sanitized_column} FROM {self.table_name} WHERE {sanitized_column} IS NOT NULL"
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
    
    # Advanced data query methods
    
    def get_aggregated_data(self, 
                           group_by: List[str], 
                           metrics: Dict[str, str], 
                           filters: Dict[str, Any] = None,
                           limit: int = 1000) -> pd.DataFrame:
        """
        Get aggregated data for dashboard metrics and charts.
        
        Args:
            group_by: List of columns to group by
            metrics: Dictionary mapping column names to aggregate functions (sum, avg, count, etc.)
            filters: Dictionary of filters to apply
            limit: Maximum number of results to return
            
        Returns:
            DataFrame with aggregated data
        """
        try:
            self.connect()
            
            # Validate columns
            columns = self._get_columns()
            valid_group_by = [self._sanitize_column_name(col) for col in group_by if self._sanitize_column_name(col) in columns]
            
            if not valid_group_by:
                logger.warning("No valid group by columns provided")
                return pd.DataFrame()
            
            # Prepare aggregate expressions
            agg_expressions = []
            for col, func in metrics.items():
                sanitized_col = self._sanitize_column_name(col)
                if sanitized_col in columns:
                    if func.lower() in ['sum', 'avg', 'min', 'max', 'count']:
                        # Convert 'avg' to 'avg'
                        sql_func = 'AVG' if func.lower() == 'avg' else func.upper()
                        agg_expressions.append(f"{sql_func}({sanitized_col}) AS {sanitized_col}_{func.lower()}")
            
            if not agg_expressions:
                logger.warning("No valid aggregate expressions")
                return pd.DataFrame()
            
            # Construct query
            select_clause = ", ".join(valid_group_by + agg_expressions)
            group_by_clause = ", ".join(valid_group_by)
            
            query = f"""
                SELECT {select_clause}
                FROM {self.table_name}
            """
            
            # Add filters if provided
            params = []
            if filters:
                where_clauses = []
                
                for column, value in filters.items():
                    sanitized_column = self._sanitize_column_name(column)
                    if sanitized_column not in columns:
                        continue
                        
                    if isinstance(value, list):
                        placeholders = ", ".join(["?"] * len(value))
                        where_clauses.append(f"{sanitized_column} IN ({placeholders})")
                        params.extend(value)
                    elif isinstance(value, dict) and value.get('operator') and value.get('value') is not None:
                        operator = value['operator']
                        if operator in ['=', '!=', '<', '<=', '>', '>=', 'LIKE']:
                            where_clauses.append(f"{sanitized_column} {operator} ?")
                            params.append(value['value'])
                    else:
                        where_clauses.append(f"{sanitized_column} = ?")
                        params.append(value)
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            # Add group by and limit
            query += f"""
                GROUP BY {group_by_clause}
                LIMIT {limit}
            """
            
            # Execute query
            if params:
                df = pd.read_sql_query(query, self.conn, params=params)
            else:
                df = pd.read_sql_query(query, self.conn)
            
            logger.info(f"Retrieved {len(df)} rows of aggregated data")
            return df
            
        except Exception as e:
            logger.error(f"Error getting aggregated data: {str(e)}", exc_info=True)
            return pd.DataFrame()
        finally:
            self.disconnect()
    
    def get_row_count(self) -> int:
        """
        Get the total number of rows in the database.
        
        Returns:
            Total number of rows
        """
        try:
            self.connect()
            
            self.cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            count = self.cursor.fetchone()[0]
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting row count: {str(e)}", exc_info=True)
            return 0
        finally:
            self.disconnect()
    
    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """
        Execute a custom SQL query.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of query results
        """
        try:
            self.connect()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            
            # If this was a write operation, commit changes
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.conn.commit()
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}", exc_info=True)
            if self.conn and query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.conn.rollback()
            return []
        finally:
            self.disconnect()
    
    def process_excel_batch(self, dataframes: List[pd.DataFrame], batch_size: int = 100) -> bool:
        """
        Process multiple Excel files efficiently in a single batch operation.
        
        Args:
            dataframes: List of DataFrames from different Excel files
            batch_size: Size of each batch for processing
            
        Returns:
            True if successful, False otherwise
        """
        if not dataframes:
            logger.warning("No dataframes provided for batch processing")
            return False
            
        try:
            # Combine all dataframes into one for more efficient processing
            combined_df = pd.concat(dataframes, ignore_index=True)
            
            if combined_df.empty:
                logger.warning("Empty combined DataFrame, nothing to process")
                return False
                
            # Process the combined data
            logger.info(f"Batch processing {len(combined_df)} rows from {len(dataframes)} Excel files")
            self.batch_store_data(combined_df, batch_size)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in batch Excel processing: {str(e)}", exc_info=True)
            return False
    
    def optimize_database(self):
        """
        Optimize the database by running VACUUM and ANALYZE.
        """
        try:
            self.connect()
            
            logger.info("Running database optimization...")
            
            # Run ANALYZE to update statistics
            self.cursor.execute("ANALYZE")
            
            # Run VACUUM to rebuild the database file
            self.cursor.execute("VACUUM")
            
            logger.info("Database optimization completed")
            
        except Exception as e:
            logger.error(f"Error optimizing database: {str(e)}", exc_info=True)
        finally:
            self.disconnect()

# Module-level functions for backward compatibility
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

def get_column_values(column_name: str) -> List[Any]:
    """
    Get unique values for a specific column, useful for populating filters.
    
    Args:
        column_name: Name of the column to get values for
        
    Returns:
        List of unique values for the column
    """
    try:
        db_manager = DatabaseManager()
        return db_manager.get_column_values(column_name)
    except Exception as e:
        logger.error(f"Error getting column values: {str(e)}", exc_info=True)
        return []

def get_data_paginated(offset: int = 0, limit: int = 100, order_by: str = None) -> pd.DataFrame:
    """
    Retrieve paginated data from the database.
    
    Args:
        offset: Number of records to skip
        limit: Maximum number of records to return
        order_by: Column to sort by
        
    Returns:
        DataFrame containing paginated data from the database
    """
    try:
        db_manager = DatabaseManager()
        return db_manager.get_data_paginated(offset, limit, order_by)
    except Exception as e:
        logger.error(f"Error retrieving paginated data: {str(e)}", exc_info=True)
        return pd.DataFrame()

def get_aggregated_data(group_by: List[str], metrics: Dict[str, str], 
                        filters: Dict[str, Any] = None, limit: int = 1000) -> pd.DataFrame:
    """
    Get aggregated data for dashboard metrics and charts.
    
    Args:
        group_by: List of columns to group by
        metrics: Dictionary mapping column names to aggregate functions (sum, avg, count, etc.)
        filters: Dictionary of filters to apply
        limit: Maximum number of results to return
        
    Returns:
        DataFrame with aggregated data
    """
    try:
        db_manager = DatabaseManager()
        return db_manager.get_aggregated_data(group_by, metrics, filters, limit)
    except Exception as e:
        logger.error(f"Error getting aggregated data: {str(e)}", exc_info=True)
        return pd.DataFrame()

def process_excel_batch(dataframes: List[pd.DataFrame], batch_size: int = 100) -> bool:
    """
    Process multiple Excel files efficiently in a single batch operation.
    
    Args:
        dataframes: List of DataFrames from different Excel files
        batch_size: Size of each batch for processing
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_manager = DatabaseManager()
        return db_manager.process_excel_batch(dataframes, batch_size)
    except Exception as e:
        logger.error(f"Error in batch Excel processing: {str(e)}", exc_info=True)
        return False

def optimize_database() -> None:
    """
    Optimize the database by running VACUUM and ANALYZE.
    """
    try:
        db_manager = DatabaseManager()
        db_manager.optimize_database()
        logger.info("Database optimization completed successfully")
    except Exception as e:
        logger.error(f"Error optimizing database: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the database setup and optimization
    print("Setting up and optimizing database...")
    setup_database()
    optimize_database()
    
    # Import test code
    from src.data_processing.file_finder import find_underwriting_files
    from src.data_processing.excel_reader import process_excel_files
    
    print("Finding underwriting files...")
    included_files, _ = find_underwriting_files()
    
    if included_files:
        print(f"Processing the first file: {included_files[0]['File Name']}")
        test_file = [included_files[0]]
        result_df = process_excel_files(test_file)
        
        if not result_df.empty:
            print(f"Storing data with {len(result_df)} rows and {len(result_df.columns)} columns")
            store_data(result_df)
            
            # Test retrieval with timer
            import time
            start_time = time.time()
            
            print("Retrieving all data from database...")
            all_data = get_all_data()
            
            end_time = time.time()
            print(f"Retrieved {len(all_data)} rows from database in {end_time - start_time:.2f} seconds")
            
            # Display columns
            print("\nDatabase columns:")
            print(all_data.columns.tolist()[:10])  # Show first 10 columns
        else:
            print("No data extracted from file to store")
    else:
        print("No files found to process")