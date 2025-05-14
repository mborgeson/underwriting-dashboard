"""
File Monitoring Module

This module monitors deal directories for changes to Excel files that match the
underwriting model criteria, and automatically updates the database when changes
are detected.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Set, Optional, List, Any
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Import configuration
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))  # Add project root to path
from config.config import (
    DEALS_ROOT, 
    DEAL_STAGE_DIRS, 
    FILE_TYPES, 
    FILE_INCLUDES, 
    FILE_EXCLUDES, 
    MIN_MODIFIED_DATE,
    MONITORING_INTERVAL
)

# Import our modules
from src.data_processing.file_finder import meets_file_criteria, collect_file_metadata, find_uw_model_folder
from src.data_processing.excel_reader import process_excel_files
from src.database.db_manager import store_data

# Configure logging
logger = logging.getLogger(__name__)

class DebounceManager:
    """
    Manages debouncing of file events to prevent processing the same file multiple times
    when multiple events occur in quick succession.
    """
    
    def __init__(self, debounce_period: float = 2.0):
        """
        Initialize the DebounceManager.
        
        Args:
            debounce_period: Time in seconds to wait before processing a file after an event
        """
        self.debounce_period = debounce_period
        self.last_events: Dict[str, float] = {}
        self.queued_files: Set[str] = set()
    
    def add_event(self, file_path: str) -> bool:
        """
        Add a file event and determine if it should be processed now.
        
        Args:
            file_path: Path to the file that triggered the event
            
        Returns:
            True if the file should be processed, False if it should be debounced
        """
        current_time = time.time()
        
        # If this file has had an event recently, debounce it
        if file_path in self.last_events:
            if current_time - self.last_events[file_path] < self.debounce_period:
                self.last_events[file_path] = current_time
                self.queued_files.add(file_path)
                return False
        
        # Update the last event time
        self.last_events[file_path] = current_time
        
        # If this was a queued file, remove it from the queue
        if file_path in self.queued_files:
            self.queued_files.remove(file_path)
        
        return True
    
    def get_ready_files(self) -> List[str]:
        """
        Get files that are ready to be processed after their debounce period has elapsed.
        
        Returns:
            List of file paths that are ready to be processed
        """
        current_time = time.time()
        ready_files = []
        files_to_remove = []
        
        for file_path in self.queued_files:
            if current_time - self.last_events[file_path] >= self.debounce_period:
                ready_files.append(file_path)
                files_to_remove.append(file_path)
        
        # Remove processed files from the queue
        for file_path in files_to_remove:
            self.queued_files.remove(file_path)
        
        return ready_files

class UnderwritingModelEventHandler(FileSystemEventHandler):
    """
    Custom event handler for file system events related to underwriting model Excel files.
    """
    
    def __init__(self):
        """
        Initialize the event handler.
        """
        self.debounce_manager = DebounceManager()
        self.last_processed_time = time.time()
    
    def process_file(self, file_path: str, deal_stage_dir: Optional[str] = None) -> None:
        """
        Process a file that has been created or modified.
        
        Args:
            file_path: Path to the file to process
            deal_stage_dir: Path to the deal stage directory containing the file
        """
        try:
            # Check if the file exists and meets the criteria
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists() or not file_path_obj.is_file():
                logger.warning(f"File does not exist or is not a file: {file_path}")
                return
            
            # Determine the deal stage directory if not provided
            if deal_stage_dir is None:
                for stage_dir in DEAL_STAGE_DIRS:
                    if file_path.startswith(str(stage_dir)):
                        deal_stage_dir = stage_dir
                        break
            
            if deal_stage_dir is None:
                logger.warning(f"Could not determine deal stage directory for file: {file_path}")
                return
            
            # Check if the file meets the criteria
            if not meets_file_criteria(file_path_obj):
                logger.debug(f"File does not meet criteria: {file_path}")
                return
            
            # Log that we're processing the file
            logger.info(f"Processing file: {file_path}")
            
            # Collect metadata about the file
            file_metadata = collect_file_metadata(file_path_obj, Path(deal_stage_dir))
            
            # Process the file and update the database
            result_df = process_excel_files([file_metadata])
            
            if not result_df.empty:
                store_data(result_df)
                logger.info(f"Updated database with data from: {file_path}")
            else:
                logger.warning(f"No data extracted from file: {file_path}")
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}", exc_info=True)
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Handle a file modification event.
        
        Args:
            event: The file system event
        """
        if not event.is_directory and event.src_path.lower().endswith(tuple(FILE_TYPES)):
            if self.debounce_manager.add_event(event.src_path):
                logger.debug(f"File modified: {event.src_path}")
                self.process_file(event.src_path)
    
    def on_created(self, event: FileSystemEvent) -> None:
        """
        Handle a file creation event.
        
        Args:
            event: The file system event
        """
        if not event.is_directory and event.src_path.lower().endswith(tuple(FILE_TYPES)):
            if self.debounce_manager.add_event(event.src_path):
                logger.debug(f"File created: {event.src_path}")
                self.process_file(event.src_path)
    
    def on_moved(self, event: FileSystemEvent) -> None:
        """
        Handle a file move/rename event.
        
        Args:
            event: The file system event
        """
        # Handle destination file if it's an Excel file
        if not event.is_directory and event.dest_path.lower().endswith(tuple(FILE_TYPES)):
            if self.debounce_manager.add_event(event.dest_path):
                logger.debug(f"File moved/renamed to: {event.dest_path}")
                self.process_file(event.dest_path)
    
    def process_pending_files(self) -> None:
        """
        Process any files that are ready after their debounce period.
        """
        ready_files = self.debounce_manager.get_ready_files()
        for file_path in ready_files:
            logger.debug(f"Processing debounced file: {file_path}")
            self.process_file(file_path)

def start_monitoring(polling_interval: int = MONITORING_INTERVAL) -> None:
    """
    Start monitoring the deal directories for changes to underwriting model Excel files.
    
    Args:
        polling_interval: Interval in seconds for checking file changes
    """
    try:
        logger.info("Starting file monitoring")
        
        # Create event handler
        event_handler = UnderwritingModelEventHandler()
        
        # Create observer
        observer = Observer()
        
        # Schedule monitoring for each deal stage directory
        for deal_stage_dir in DEAL_STAGE_DIRS:
            path = Path(deal_stage_dir)
            if path.exists() and path.is_dir():
                logger.info(f"Monitoring directory: {path}")
                observer.schedule(event_handler, str(path), recursive=True)
            else:
                logger.warning(f"Directory does not exist, skipping: {path}")
        
        # Start the observer
        observer.start()
        logger.info("File monitoring started successfully")
        
        try:
            while True:
                # Process any pending debounced files
                event_handler.process_pending_files()
                
                # Sleep for a bit
                time.sleep(polling_interval)
        except KeyboardInterrupt:
            observer.stop()
            logger.info("File monitoring stopped by user")
        
        observer.join()
        
    except Exception as e:
        logger.error(f"Error starting file monitoring: {str(e)}", exc_info=True)

def run_initial_scan() -> None:
    """
    Run an initial scan of all deal directories to process existing files.
    """
    try:
        logger.info("Running initial scan of deal directories")
        
        # Import the function from file_finder
        from src.data_processing.file_finder import find_underwriting_files
        
        # Find all underwriting files
        included_files, _ = find_underwriting_files()
        
        if included_files:
            logger.info(f"Processing {len(included_files)} existing files")
            
            # Process the files and update the database
            result_df = process_excel_files(included_files)
            
            if not result_df.empty:
                store_data(result_df)
                logger.info(f"Updated database with data from {len(included_files)} files")
            else:
                logger.warning("No data extracted from existing files")
        else:
            logger.info("No existing files found to process")
            
    except Exception as e:
        logger.error(f"Error in initial scan: {str(e)}", exc_info=True)

if __name__ == "__main__":
    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run initial scan
    print("Running initial scan...")
    run_initial_scan()
    
    # Start monitoring
    print("Starting file monitoring...")
    start_monitoring()