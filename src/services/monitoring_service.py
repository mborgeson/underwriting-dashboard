"""
Monitoring Service

This module provides services for file monitoring operations, coordinating
between the file monitoring system and data processing/database components.
"""

import logging
import threading
from typing import Callable, Optional
import time

from src.file_monitoring.monitor import FileMonitor
from src.services.file_service import FileService
from src.config.settings import settings

logger = logging.getLogger(__name__)

class MonitoringService:
    """Service for file monitoring operations."""
    
    def __init__(self):
        """Initialize the monitoring service."""
        self.monitor = None
        self.monitoring_thread = None
        self.is_running = False
    
    def start_monitoring(self, callback: Optional[Callable] = None) -> bool:
        """
        Start the file monitoring service.
        
        Args:
            callback: Optional callback function to run when files change
            
        Returns:
            True if monitoring started successfully, False otherwise
        """
        try:
            if self.is_running:
                logger.info("Monitoring is already running")
                return True
                
            # Create file monitor with the file service update method as callback
            self.monitor = FileMonitor(
                directories=settings.deal_stage_dirs,
                file_types=settings.file_types,
                callback=callback or self._handle_file_changes
            )
            
            # Start monitoring in a background thread
            self.monitoring_thread = threading.Thread(
                target=self._run_monitoring_thread,
                daemon=True
            )
            self.monitoring_thread.start()
            self.is_running = True
            
            logger.info("File monitoring started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {str(e)}", exc_info=True)
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Stop the file monitoring service.
        
        Returns:
            True if monitoring was stopped successfully, False otherwise
        """
        try:
            if not self.is_running:
                logger.info("Monitoring is not running")
                return True
                
            # Stop the monitor
            if self.monitor:
                self.monitor.stop()
                
            self.is_running = False
            logger.info("File monitoring stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {str(e)}", exc_info=True)
            return False
    
    def _run_monitoring_thread(self) -> None:
        """Run the file monitoring thread."""
        try:
            if self.monitor:
                logger.info("Starting monitoring thread")
                self.monitor.start()
        except Exception as e:
            logger.error(f"Error in monitoring thread: {str(e)}", exc_info=True)
            self.is_running = False
    
    def _handle_file_changes(self, changed_files: list) -> None:
        """
        Handle file changes detected by the monitor.
        
        Args:
            changed_files: List of changed file paths
        """
        try:
            logger.info(f"Detected changes in {len(changed_files)} files")
            
            # Update the database with the latest data
            success = FileService.update_database()
            
            if success:
                logger.info("Database updated successfully after file changes")
            else:
                logger.warning("Failed to update database after file changes")
                
        except Exception as e:
            logger.error(f"Error handling file changes: {str(e)}", exc_info=True)

# Create a global instance
monitoring_service = MonitoringService()