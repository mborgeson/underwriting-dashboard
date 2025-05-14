"""
Dashboard Service

This module provides services for dashboard-related operations, acting as
an intermediary between the database and the dashboard UI.
"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd

from src.database.db_manager_fixed import (
    get_all_data, 
    get_filtered_data, 
    search_data,
    get_aggregated_data,
    get_data_paginated
)

# Add column name mapping to handle different formats
COLUMN_MAPPING = {
    # Map from spaces to underscores (dashboard uses spaces, database uses underscores)
    'File Name': 'File_Name',
    'Absolute File Path': 'Absolute_File_Path',
    'Deal Stage Subdirectory Name': 'Deal_Stage_Subdirectory_Name',
    'Deal Stage Subdirectory Path': 'Deal_Stage_Subdirectory_Path',
    'Last Modified Date': 'Last_Modified_Date',
    'Date Uploaded': 'Date_Uploaded',
    'File Size in Bytes': 'File_Size_in_Bytes',
    
    # Property Info fields with typo in database ('Propety' instead of 'Property')
    'Deal Name': 'Propety_Info__Deal_Name_',
    'Deal City': 'Propety_Info__Deal_City_',
    'Deal State': 'Propety_Info__Deal_State_',
    'Year Built': 'Propety_Info__Year_Built_',
    'Year Renovated': 'Propety_Info__Year_Renovated_',
    'Location Quality': 'Propety_Info__Location_Quality_',
    'Building Quality': 'Propety_Info__Building_Quality_',
    'Number of Units': 'Propety_Info__Number_of_Units_',
    'Average Unit SF': 'Propety_Info__Average_Unit_SF_',
    'Building Type': 'Propety_Info__Building_Type_',
    'Project Type': 'Propety_Info__Project_Type_',
    'Market': 'Propety_Info__Market_',
    'Submarket Cluster': 'Propety_Info__Submarket_Cluster_',
    'Submarket': 'Propety_Info__Submarket_',
    'County': 'Propety_Info__County_',
    
    # Financial metrics
    'Purchase Price': 'Purchase_Price',
    'Total Land and Acquisition Costs': 'Total_Land_and_Acquisition_Costs',
    'Total Hard Costs': 'Total_Hard_Costs',
    'Total Soft Costs': 'Total_Soft_Costs',
    'Total Closing Costs': 'Total_Closing_Costs',
    'Total Acquistion Budget': 'Total_Acquistion_Budget'
}

logger = logging.getLogger(__name__)

class DashboardService:
    """Service for dashboard data operations."""
    
    @staticmethod
    def _map_filters_to_db_columns(filters: Dict[str, Any]) -> Dict[str, Any]:
        """Map filter column names to database column names."""
        if not filters:
            return {}
            
        mapped_filters = {}
        for key, value in filters.items():
            # If the key is in our mapping, use the mapped column name
            if key in COLUMN_MAPPING:
                mapped_filters[COLUMN_MAPPING[key]] = value
            else:
                # Otherwise use the original key
                mapped_filters[key] = value
                
        return mapped_filters
    
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
            # Map filter keys to database column names
            mapped_filters = DashboardService._map_filters_to_db_columns(filters) if filters else {}
            
            if mapped_filters and any(mapped_filters.values()):
                logger.info(f"Getting filtered data with filters: {mapped_filters}")
                return get_filtered_data(mapped_filters)
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
    
    @staticmethod
    def get_paginated_data(page: int = 1, page_size: int = 50, order_by: str = None) -> pd.DataFrame:
        """
        Get paginated data for efficient dashboard loading.
        
        Args:
            page: Page number (1-based)
            page_size: Number of records per page
            order_by: Column to order by
            
        Returns:
            DataFrame with paginated data
        """
        try:
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Get paginated data
            return get_data_paginated(offset, page_size, order_by)
            
        except Exception as e:
            logger.error(f"Error getting paginated data: {str(e)}", exc_info=True)
            return pd.DataFrame()
    
    @staticmethod
    def get_dashboard_metrics(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get key metrics for the dashboard.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Dictionary of metrics
        """
        try:
            # Define metrics to calculate
            metrics = {
                "Property Value": "sum",
                "Acquisition Price": "sum",
                "NOI": "sum",
                "id": "count"  # Count of records
            }
            
            # Get aggregated data
            agg_data = get_aggregated_data(
                group_by=["Deal Stage"],
                metrics=metrics,
                filters=filters,
                limit=100
            )
            
            if agg_data.empty:
                return {
                    "total_properties": 0,
                    "total_value": 0,
                    "avg_price": 0,
                    "total_noi": 0
                }
            
            # Calculate totals
            total_properties = agg_data["id_count"].sum() if "id_count" in agg_data.columns else 0
            
            # Check different possible column names for property value
            if "Property_Value_sum" in agg_data.columns:
                total_value = agg_data["Property_Value_sum"].sum()
            elif "Property Value_sum" in agg_data.columns:
                total_value = agg_data["Property Value_sum"].sum()
            else:
                total_value = 0
            
            # Check different possible column names for aggregated values
            if "Acquisition_Price_sum" in agg_data.columns:
                total_price = agg_data["Acquisition_Price_sum"].sum()
            elif "Acquisition Price_sum" in agg_data.columns:
                total_price = agg_data["Acquisition Price_sum"].sum()
            else:
                total_price = 0
                
            if "NOI_sum" in agg_data.columns:
                total_noi = agg_data["NOI_sum"].sum()
            else:
                total_noi = 0
            
            # Calculate averages
            avg_price = total_price / total_properties if total_properties > 0 else 0
            
            return {
                "total_properties": total_properties,
                "total_value": total_value,
                "avg_price": avg_price,
                "total_noi": total_noi,
                "metrics_by_stage": agg_data.to_dict(orient="records")
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {str(e)}", exc_info=True)
            return {
                "total_properties": 0,
                "total_value": 0,
                "avg_price": 0,
                "total_noi": 0
            }