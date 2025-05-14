"""
Dashboard Service

This module provides services for dashboard-related operations, acting as
an intermediary between the database and the dashboard UI.
"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd

from src.database.db_manager import (
    get_all_data, 
    get_filtered_data, 
    search_data
)

logger = logging.getLogger(__name__)

class DashboardService:
    """Service for dashboard data operations."""
    
    @staticmethod
    def get_dashboard_data(
        filters: Optional[Dict[str, Any]] = None, 
        search_term: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get data for the dashboard based on filters and search criteria.
        
        Args:
            filters: Dictionary of filter criteria
            search_term: Optional search term to filter results
            
        Returns:
            DataFrame of filtered data
        """
        try:
            if filters and any(filters.values()):
                logger.info(f"Getting filtered data with filters: {filters}")
                return get_filtered_data(filters)
            elif search_term:
                logger.info(f"Searching data with term: {search_term}")
                return search_data(search_term)
            else:
                logger.info("Getting all data")
                return get_all_data()
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}", exc_info=True)
            # Return empty DataFrame instead of raising exception
            return pd.DataFrame()
    
    @staticmethod
    def get_filter_options() -> Dict[str, List[Any]]:
        """
        Get available filter options for the dashboard.
        
        Returns:
            Dictionary of filter field names and their possible values
        """
        try:
            # Get all data to extract unique values for filters
            data = get_all_data()
            
            filter_options = {}
            
            # Fields that are typically used for filtering
            filter_fields = [
                "Deal Stage", "Property Type", "Market", "Sub-Market", 
                "Deal Status", "Property Class"
            ]
            
            # Get unique values for each filter field that exists in the data
            for field in filter_fields:
                if field in data.columns:
                    unique_values = data[field].dropna().unique().tolist()
                    # Sort values for better user experience
                    unique_values.sort()
                    filter_options[field] = unique_values
            
            return filter_options
            
        except Exception as e:
            logger.error(f"Error getting filter options: {str(e)}", exc_info=True)
            return {}