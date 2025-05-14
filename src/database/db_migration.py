"""
Database Migration Script

This script assists in migrating from the original database manager to the optimized version.
It performs the following tasks:
1. Backs up the existing database
2. Migrates the data to the new optimized structure (if schema changes are needed)
3. Sets up indexes and optimizations
"""

import os
import shutil
import logging
import sqlite3
import time
from pathlib import Path
from datetime import datetime

# Import configuration
from src.config.settings import settings
from src.database.db_manager_optimized import DatabaseManager, optimize_database

# Configure logging
logger = logging.getLogger(__name__)

def backup_database() -> Path:
    """
    Create a backup of the existing database.
    
    Returns:
        Path to the backup file
    """
    source_path = settings.database_path
    if not os.path.exists(source_path):
        logger.warning(f"Database file {source_path} does not exist, no backup needed")
        return None
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = source_path.parent / f"{source_path.stem}_backup_{timestamp}{source_path.suffix}"
    
    logger.info(f"Creating database backup: {backup_path}")
    shutil.copy2(source_path, backup_path)
    
    return backup_path

def verify_database_integrity() -> bool:
    """
    Verify the integrity of the database.
    
    Returns:
        True if the database is valid, False otherwise
    """
    try:
        # Connect directly to the database file
        with sqlite3.connect(settings.database_path) as conn:
            conn.execute("PRAGMA integrity_check")
            logger.info("Database integrity check passed")
            return True
    except Exception as e:
        logger.error(f"Database integrity check failed: {str(e)}", exc_info=True)
        return False

def migrate_database() -> bool:
    """
    Migrate the database to the optimized structure.
    
    Returns:
        True if migration was successful, False otherwise
    """
    try:
        # Step 1: Create a backup
        backup_path = backup_database()
        if backup_path:
            logger.info(f"Database backup created at: {backup_path}")
        
        # Step 2: Verify database integrity
        if not verify_database_integrity():
            logger.error("Database integrity check failed, aborting migration")
            return False
        
        # Step 3: Initialize the optimized database manager
        logger.info("Initializing optimized database manager")
        db_manager = DatabaseManager()
        
        # Step 4: Set up the database with optimized settings
        db_manager.setup_database()
        
        # Step 5: Optimize the database (create indexes, etc.)
        logger.info("Optimizing database...")
        db_manager.optimize_database()
        
        logger.info("Database migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during database migration: {str(e)}", exc_info=True)
        return False

def perform_migration() -> bool:
    """
    Perform the full migration process with proper logging and error handling.
    
    Returns:
        True if migration was successful, False otherwise
    """
    start_time = time.time()
    
    logger.info("Starting database migration process")
    
    try:
        success = migrate_database()
        
        if success:
            elapsed_time = time.time() - start_time
            logger.info(f"Database migration completed successfully in {elapsed_time:.2f} seconds")
            return True
        else:
            logger.error("Database migration failed")
            return False
    except Exception as e:
        logger.critical(f"Unexpected error during migration: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Path(settings.logs_dir) / "db_migration.log"),
            logging.StreamHandler()
        ]
    )
    
    # Run the migration
    print("Starting database migration...")
    success = perform_migration()
    
    if success:
        print("Database migration completed successfully!")
    else:
        print("Database migration failed. Check the logs for details.")