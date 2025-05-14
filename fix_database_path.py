#!/usr/bin/env python
"""
Fix Database Path Script

This script updates the database configuration to ensure the dashboard
can connect to the database file properly in both Windows and WSL environments.
"""
import os
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def update_config_settings():
    """Update the settings.py file to use absolute paths with platform detection."""
    from src.config.settings import settings
    
    # Get the actual database file path
    db_path = project_root / "database" / "underwriting_models.db"
    
    if os.path.exists(db_path):
        logger.info(f"Found database at: {db_path}")
        
        # Create a .env file to override settings
        env_file = project_root / ".env"
        
        # Create reasonable default for deals root if it doesn't exist
        deals_root = os.path.join(os.path.dirname(project_root), "Deals")
        
        with open(env_file, "w") as f:
            f.write(f"DATABASE_PATH={db_path.absolute()}\n")
            f.write(f"DEALS_ROOT={deals_root}\n")
            f.write(f"DEBUG=True\n")
        
        logger.info(f"Created .env file with database path at: {env_file}")
        logger.info(f"Database path set to: {db_path.absolute()}")
        logger.info(f"Deals root set to: {deals_root}")
        
        # Check if deals root exists
        if not os.path.exists(deals_root):
            logger.warning(f"Deals root directory does not exist: {deals_root}")
            logger.warning("You may need to update the DEALS_ROOT environment variable in the .env file")
        return True
    else:
        logger.error(f"Database file not found at: {db_path}")
        return False

def check_database_table():
    """Check if the database table exists and is accessible."""
    import sqlite3
    
    db_path = project_root / "database" / "underwriting_models.db"
    
    if not os.path.exists(db_path):
        logger.error(f"Database file does not exist at: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='underwriting_model_data';")
        result = cursor.fetchone()
        
        if result:
            logger.info("Database table 'underwriting_model_data' exists")
            
            # Check row count
            cursor.execute("SELECT COUNT(*) FROM underwriting_model_data;")
            count = cursor.fetchone()[0]
            logger.info(f"Database contains {count} rows of data")
            
            # Check column count
            cursor.execute("PRAGMA table_info(underwriting_model_data);")
            columns = cursor.fetchall()
            logger.info(f"Database table has {len(columns)} columns")
            
            conn.close()
            return True
        else:
            logger.error("Database table 'underwriting_model_data' does not exist")
            conn.close()
            return False
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        return False

def fix_connection_in_db_manager():
    """Update the database manager to ensure proper connection handling."""
    # Create fixed database manager 
    db_manager_path = project_root / "src" / "database" / "db_manager_fixed.py"
    
    try:
        # Create a fixed version that ensures proper path handling
        with open(db_manager_path, "w") as f:
            f.write("""#!/usr/bin/env python
\"\"\"
Fixed Database Manager

This is a simplified version of the database manager that ensures
proper connection to the database file in both Windows and WSL environments.
\"\"\"
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
    \"\"\"Database manager with connection handling and query methods\"\"\"
    
    def __init__(self, db_path=None):
        \"\"\"Initialize the database manager\"\"\"
        self.db_path = db_path or DATABASE_PATH
        self.conn = None
        self.cursor = None
        self.table_name = "underwriting_model_data"
        self._column_cache = None
        self.connect()
    
    def connect(self):
        \"\"\"Connect to the database\"\"\"
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
        \"\"\"Disconnect from the database\"\"\"
        if self.cursor:
            self.cursor.close()
            self.cursor = None
            logger.info("Database cursor released")
        
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")
    
    def _get_columns(self) -> List[str]:
        \"\"\"Get the column names from the database\"\"\"
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
        \"\"\"Execute a SQL query\"\"\"
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
        \"\"\"Get all data from the database\"\"\"
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
        \"\"\"Get filtered data from the database\"\"\"
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
    \"\"\"Get all data from the database\"\"\"
    db = DatabaseManager()
    data = db.get_all_data()
    db.disconnect()
    return data

def get_filtered_data(filters=None, search_term=None):
    \"\"\"Get filtered data from the database\"\"\"
    db = DatabaseManager()
    data = db.get_filtered_data(filters, search_term)
    db.disconnect()
    return data

def search_data(search_term):
    \"\"\"Search data in the database\"\"\"
    return get_filtered_data(search_term=search_term)

def get_aggregated_data(group_by, metrics):
    \"\"\"Get aggregated data from the database\"\"\"
    db = DatabaseManager()
    data = db.get_all_data()
    db.disconnect()
    
    # Convert column names for grouping
    group_cols = [col.replace(' ', '_') for col in group_by]
    
    # Group by and aggregate
    result = data.groupby(group_by)[metrics].agg(['mean', 'sum', 'count'])
    return result

def get_data_paginated(page=1, page_size=100, filters=None, search_term=None):
    \"\"\"Get paginated data from the database\"\"\"
    db = DatabaseManager()
    data = db.get_filtered_data(filters, search_term)
    db.disconnect()
    
    # Calculate pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return data.iloc[start_idx:end_idx]
""")
        logger.info(f"Created fixed database manager at: {db_manager_path}")
        
        # Now update the dashboard service to use the fixed version
        dashboard_service_path = project_root / "src" / "services" / "dashboard_service.py"
        
        if os.path.exists(dashboard_service_path):
            with open(dashboard_service_path, "r") as f:
                content = f.read()
            
            # Update the import to use the fixed version
            if "from src.database.db_manager_optimized import" in content:
                content = content.replace(
                    "from src.database.db_manager_optimized import", 
                    "from src.database.db_manager_fixed import"
                )
                
                with open(dashboard_service_path, "w") as f:
                    f.write(content)
                
                logger.info(f"Updated dashboard service to use fixed database manager")
                return True
            else:
                logger.warning(f"Import statement not found in dashboard service")
                return False
        else:
            logger.error(f"Dashboard service file not found at: {dashboard_service_path}")
            return False
    except Exception as e:
        logger.error(f"Error fixing database connection: {str(e)}")
        return False

def create_mock_deal_structure():
    """Create a mock deal structure for testing."""
    try:
        # Read the .env file to get the deals root
        env_file = project_root / ".env"
        deals_root = None
        
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("DEALS_ROOT="):
                    deals_root = line.strip().split("=", 1)[1]
        
        if not deals_root:
            logger.error("DEALS_ROOT not found in .env file")
            return False
        
        # Create the deal stage directories
        deals_path = Path(deals_root)
        os.makedirs(deals_path, exist_ok=True)
        
        deal_stages = [
            "0) Dead Deals",
            "1) Initial UW and Review",
            "2) Active UW and Review",
            "3) Deals Under Contract",
            "4) Closed Deals", 
            "5) Realized Deals"
        ]
        
        for stage in deal_stages:
            stage_path = deals_path / stage
            os.makedirs(stage_path, exist_ok=True)
            logger.info(f"Created deal stage directory: {stage_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating mock deal structure: {str(e)}")
        return False

def update_settings_for_testing():
    """Update settings.py to make DEALS_ROOT optional for testing."""
    try:
        settings_path = project_root / "src" / "config" / "settings.py"
        
        with open(settings_path, "r") as f:
            content = f.read()
        
        # Update the _path_from_env method to allow None for DEALS_ROOT
        if "raise ValueError(f\"Required path environment variable {env_var} not set\")" in content:
            content = content.replace(
                "raise ValueError(f\"Required path environment variable {env_var} not set\")",
                "if env_var == 'DEALS_ROOT':\n            logger.warning(f\"Environment variable {env_var} not set, using empty path\")\n            return Path()\n        raise ValueError(f\"Required path environment variable {env_var} not set\")"
            )
            
            with open(settings_path, "w") as f:
                f.write(content)
            
            logger.info(f"Updated settings.py to make DEALS_ROOT optional")
            return True
        else:
            logger.warning(f"Could not find the target line in settings.py")
            return False
    except Exception as e:
        logger.error(f"Error updating settings.py: {str(e)}")
        return False

def main():
    """Main function to run the fix."""
    logger.info("Starting database path fix...")
    
    # Update configuration settings
    if not update_config_settings():
        logger.error("Failed to update configuration settings")
        return 1
    
    # Check database table
    if not check_database_table():
        logger.error("Failed to verify database table")
        return 1
    
    # Fix connection in database manager
    if not fix_connection_in_db_manager():
        logger.error("Failed to fix connection in database manager")
        return 1
    
    # Update settings to make DEALS_ROOT optional
    if not update_settings_for_testing():
        logger.warning("Failed to update settings.py, but continuing...")
    
    # Create mock deal structure
    if not create_mock_deal_structure():
        logger.warning("Failed to create mock deal structure, but continuing...")
    
    logger.info("Database path fix completed successfully!")
    logger.info("\nInstructions:")
    logger.info("1. Run the dashboard with: python run_dashboard.py")
    logger.info("2. The dashboard should now properly connect to the database.")
    logger.info("3. If you encounter issues with DEALS_ROOT, edit the .env file")
    logger.info("   and set DEALS_ROOT to the actual path of your deals directory.")
    return 0

if __name__ == "__main__":
    sys.exit(main())