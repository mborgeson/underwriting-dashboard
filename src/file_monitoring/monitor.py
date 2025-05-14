"""
File Monitoring Module

This module provides file system monitoring capabilities to detect changes
in underwriting files and trigger updates when changes occur.
"""

import logging
import os
import time
from pathlib import Path
from typing import List, Callable, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

from src.config.settings import settings

logger = logging.getLogger(__name__)

class UWFileHandler(FileSystemEventHandler):
    """
    Event handler for underwriting file changes.
    
    This handler detects changes to Excel files and notifies
    the callback function when relevant files are modified.
    """
    
    def __init__(
        self, 
        file_types: List[str], 
        file_includes: List[str],
        file_excludes: List[str],
        callback: Callable[[List[str]], None]
    ):
        """
        Initialize the file handler.
        
        Args:
            file_types: List of file extensions to monitor (e.g., ['.xlsb', '.xlsm'])
            file_includes: List of strings that must be in filename to be included
            file_excludes: List of strings that exclude a file if in filename
            callback: Function to call when relevant files change
        """
        self.file_types = [ft.lower() for ft in file_types]
        self.file_includes = file_includes
        self.file_excludes = file_excludes
        self.callback = callback
        self.changed_files: Set[str] = set()
        self.last_event_time = time.time()
        self.cooldown_period = 5  # seconds to wait after last event before processing
    
    def on_modified(self, event):
        """Handle file modified events."""
        if not event.is_directory and self._is_relevant_file(event.src_path):
            self._handle_file_change(event.src_path)
    
    def on_created(self, event):
        """Handle file created events."""
        if not event.is_directory and self._is_relevant_file(event.src_path):
            self._handle_file_change(event.src_path)
    
    def _is_relevant_file(self, file_path: str) -> bool:
        """
        Check if a file is relevant for monitoring.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file should be monitored, False otherwise
        """
        path = Path(file_path)
        file_ext = path.suffix.lower()
        file_name = path.name.lower()
        
        # Check file extension
        if file_ext not in self.file_types:
            return False
            
        # Check includes
        if self.file_includes and not any(inc.lower() in file_name for inc in self.file_includes):
            return False
            
        # Check excludes
        if any(exc.lower() in file_name for exc in self.file_excludes):
            return False
            
        return True
    
    def _handle_file_change(self, file_path: str) -> None:
        """
        Handle a file change event.
        
        This adds the file to the changed files set and schedules a callback
        if one isn't already scheduled.
        
        Args:
            file_path: Path to the changed file
        """
        self.changed_files.add(file_path)
        self.last_event_time = time.time()
        
    def process_pending_changes(self) -> None:
        """
        Process any pending file changes.
        
        This checks if the cooldown period has elapsed since the last event,
        and if so, calls the callback with the list of changed files and clears
        the set.
        """
        if not self.changed_files:
            return
            
        # If enough time has passed since the last event
        if time.time() - self.last_event_time >= self.cooldown_period:
            try:
                # Make a copy and clear the set to avoid missing events during callback
                changed_files = list(self.changed_files)
                self.changed_files.clear()
                
                # Call the callback
                logger.info(f"Processing {len(changed_files)} changed files")
                self.callback(changed_files)
                
            except Exception as e:
                logger.error(f"Error processing file changes: {str(e)}", exc_info=True)

class FileMonitor:
    """
    File system monitor for underwriting files.
    
    This class manages monitoring of directories for file changes and
    calls a callback function when relevant files are modified.
    """
    
    def __init__(
        self, 
        directories: List[Path],
        file_types: Optional[List[str]] = None,
        file_includes: Optional[List[str]] = None,
        file_excludes: Optional[List[str]] = None,
        callback: Optional[Callable[[List[str]], None]] = None
    ):
        """
        Initialize the file monitor.
        
        Args:
            directories: List of directories to monitor
            file_types: List of file extensions to monitor (e.g., ['.xlsb', '.xlsm'])
            file_includes: List of strings that must be in filename to be included
            file_excludes: List of strings that exclude a file if in filename
            callback: Function to call when relevant files change
        """
        self.directories = [str(d) for d in directories if os.path.isdir(d)]
        self.file_types = file_types or settings.file_types
        self.file_includes = file_includes or settings.file_includes
        self.file_excludes = file_excludes or settings.file_excludes
        self.callback = callback or self._default_callback
        
        self.observer = Observer()
        self.handler = UWFileHandler(
            self.file_types,
            self.file_includes,
            self.file_excludes,
            self.callback
        )
        self.is_running = False
    
    def start(self) -> None:
        """Start monitoring the configured directories."""
        try:
            # Set up observers for each directory
            for directory in self.directories:
                if os.path.isdir(directory):
                    logger.info(f"Watching directory: {directory}")
                    self.observer.schedule(self.handler, directory, recursive=True)
                else:
                    logger.warning(f"Directory not found: {directory}")
            
            # Start the observer
            self.observer.start()
            self.is_running = True
            
            # Check for pending changes periodically
            try:
                while self.is_running:
                    self.handler.process_pending_changes()
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
                
        except Exception as e:
            logger.error(f"Error starting file monitor: {str(e)}", exc_info=True)
            self.stop()
    
    def stop(self) -> None:
        """Stop monitoring."""
        self.is_running = False
        self.observer.stop()
        self.observer.join()
        logger.info("File monitoring stopped")
    
    def _default_callback(self, changed_files: List[str]) -> None:
        """
        Default callback for file changes.
        
        Args:
            changed_files: List of changed file paths
        """
        logger.info(f"Detected changes in files: {changed_files}")
        # This does nothing by default, should be overridden by caller

def start_monitoring():
    """
    Start the file monitoring process.
    
    This is a legacy wrapper function for backward compatibility.
    New code should use the MonitoringService.
    """
    from src.services.monitoring_service import monitoring_service
    return monitoring_service.start_monitoring()