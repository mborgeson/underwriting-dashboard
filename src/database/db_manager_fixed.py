#!/usr/bin/env python
"""
Fixed Database Manager

This is a simplified version of the database manager that ensures
proper connection to the database file in both Windows and WSL environments.
"""
import os
import sqlite3
import pandas as pd
import logging
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# CRITICAL FIX: Get the absolute path to the database file
PROJECT_ROOT = Path(__file__).absolute().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "database" / "underwriting_models.db"
DATABASE_PATH = os.environ.get("DATABASE_PATH", str(DEFAULT_DB_PATH))

class DatabaseManager:
    """Database manager with connection handling and query methods"""
    
    def __init__(self, db_path=None):
        """Initialize the database manager"""
        self.db_path = db_path or DATABASE_PATH
        self.conn = None
        self.cursor = None
        self.table_name = "underwriting_model_data"
        self._column_cache = None
        self.connect()
    
    def connect(self):
        """Connect to the database"""
        try:
            # Print the path to help debug
            logger.info(f"Connecting to database: {self.db_path}")
            
            # Make sure the path exists
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Connect to the database
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Enable WAL mode for better concurrency
            self.cursor.execute("PRAGMA journal_mode=WAL;")
            
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            self.conn = None
            self.cursor = None
            return False
    
    def disconnect(self):
        """Disconnect from the database"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
            logger.info("Database cursor released")
        
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")
    
    def _get_columns(self) -> List[str]:
        """Get the column names from the database"""
        if self._column_cache:
            return self._column_cache
        
        try:
            if self.conn is None or self.cursor is None:
                self.connect()
            
            if self.cursor is None:
                logger.error("Failed to establish a database cursor")
                return []
            
            # Get the column names
            self.cursor.execute(f"PRAGMA table_info({self.table_name});")
            columns = [col[1] for col in self.cursor.fetchall()]
            self._column_cache = columns
            return columns
        except Exception as e:
            logger.error(f"Error getting columns: {str(e)}")
            return []
    
    def execute_query(self, query, params=None):
        """Execute a SQL query"""
        try:
            if self.conn is None or self.cursor is None:
                self.connect()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return []
    
    def get_all_data(self):
        """Get all data from the database"""
        try:
            if self.conn is None:
                self.connect()
            
            # Check if table exists
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';")
            if not self.cursor.fetchone():
                logger.error(f"Table {self.table_name} does not exist")
                return pd.DataFrame()
            
            # Get all data
            query = f"SELECT * FROM {self.table_name}"
            df = pd.read_sql_query(query, self.conn)
            
            # Convert column names with underscores to spaces for dashboard
            column_mapping = {col: col.replace('_', ' ') for col in df.columns if '_' in col}
            df = df.rename(columns=column_mapping)
            
            return df
        except Exception as e:
            logger.error(f"Error getting all data: {str(e)}")
            return pd.DataFrame()
    
    def get_filtered_data(self, filters=None, search_term=None):
        """Get filtered data from the database"""
        try:
            if self.conn is None:
                self.connect()
            
            # Start with base query
            query = f"SELECT * FROM {self.table_name}"
            params = []
            
            # Add filters
            if filters:
                # Convert filters with spaces to underscores
                db_filters = {}
                for key, value in filters.items():
                    db_key = key.replace(' ', '_')
                    db_filters[db_key] = value
                
                # Build WHERE clause
                where_clauses = []
                for key, value in db_filters.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            # Add search term
            if search_term:
                columns = self._get_columns()
                search_clauses = []
                
                for col in columns:
                    search_clauses.append(f"{col} LIKE ?")
                    params.append(f"%{search_term}%")
                
                if search_clauses:
                    if "WHERE" in query:
                        query += " AND (" + " OR ".join(search_clauses) + ")"
                    else:
                        query += " WHERE " + " OR ".join(search_clauses)
            
            # Execute query
            df = pd.read_sql_query(query, self.conn, params=params)
            
            # Convert column names with underscores to spaces for dashboard
            column_mapping = {col: col.replace('_', ' ') for col in df.columns if '_' in col}
            df = df.rename(columns=column_mapping)
            
            logger.info(f"Retrieved {len(df)} filtered rows from database")
            return df
        except Exception as e:
            logger.error(f"Error getting filtered data: {str(e)}")
            return pd.DataFrame()

# Functions to use directly
def get_all_data():
    """Get all data from the database"""
    db = DatabaseManager()
    data = db.get_all_data()
    db.disconnect()
    return data

def get_filtered_data(filters=None, search_term=None):
    """Get filtered data from the database"""
    db = DatabaseManager()
    data = db.get_filtered_data(filters, search_term)
    db.disconnect()
    return data

def search_data(search_term):
    """Search data in the database"""
    return get_filtered_data(search_term=search_term)

def get_aggregated_data(group_by, metrics):
    """Get aggregated data from the database"""
    db = DatabaseManager()
    data = db.get_all_data()
    db.disconnect()
    
    # Convert column names for grouping
    group_cols = [col.replace(' ', '_') for col in group_by]
    
    # Group by and aggregate
    result = data.groupby(group_by)[metrics].agg(['mean', 'sum', 'count'])
    return result

def get_data_paginated(page=1, page_size=100, filters=None, search_term=None):
    """Get paginated data from the database"""
    db = DatabaseManager()
    data = db.get_filtered_data(filters, search_term)
    db.disconnect()
    
    # Calculate pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return data.iloc[start_idx:end_idx]
