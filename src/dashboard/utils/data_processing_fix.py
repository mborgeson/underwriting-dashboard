"""
Data processing utilities for the dashboard with fixes for data type issues
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

def fix_data_types(data: pd.DataFrame) -> pd.DataFrame:
    """
    Fix data types to ensure compatibility with PyArrow/Streamlit.
    
    Args:
        data: DataFrame to fix
        
    Returns:
        DataFrame with fixed data types
    """
    if data.empty:
        return data
    
    # Create a copy to avoid modifying the original
    df = data.copy()
    
    # Loop through columns and handle problematic types
    for col in df.columns:
        # Check if column is object type (string)
        if df[col].dtype == 'object':
            # First try to convert to numeric
            try:
                # Try first with coercion (NaN for failures)
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                
                # If the conversion didn't create too many NaNs, use it
                if numeric_series.isna().sum() <= df[col].isna().sum() + (len(df) * 0.1):  # Allow 10% more NaNs
                    df[col] = numeric_series
                    continue
            except:
                pass
            
            # Try date conversion
            try:
                date_series = pd.to_datetime(df[col], errors='coerce')
                if date_series.isna().sum() <= df[col].isna().sum() + (len(df) * 0.1):  # Allow 10% more NaNs
                    df[col] = date_series
                    continue
            except:
                pass
            
            # Convert any remaining NaN-like values to proper NaN
            df[col] = df[col].replace(['nan', 'None', 'null', 'NA', 'N/A', ''], np.nan)
            
            # Handle special case for '[Year Built]' which causes the specific error
            if 'Year Built' in col and df[col].astype(str).str.contains('\[Year Built\]').any():
                # Replace the specific problem value with NaN
                df[col] = df[col].replace('[Year Built]', np.nan)
            
        # For numeric columns that may contain strings
        elif pd.api.types.is_numeric_dtype(df[col]):
            # Ensure numeric columns don't have string values
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                # If conversion fails, convert to string
                df[col] = df[col].astype(str)
    
    logger.info(f"Fixed data types for DataFrame with {len(df)} rows")
    return df

def process_data_for_display(data: pd.DataFrame) -> pd.DataFrame:
    """
    Process data for display in the dashboard.
    
    Args:
        data: Raw data from the database
        
    Returns:
        Processed data ready for display
    """
    if data.empty:
        return data
    
    # Create a copy to avoid modifying the original
    df = data.copy()
    
    # Fix data types for Streamlit/PyArrow
    df = fix_data_types(df)
    
    # Format dates for better display
    for col in df.columns:
        if 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass
    
    # Convert NaN to display as empty string
    df = df.fillna('')
    
    return df

def get_key_metrics(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate key metrics from the data.
    
    Args:
        data: DataFrame containing the data
        
    Returns:
        Dictionary of metrics
    """
    if data.empty:
        return {
            'total_deals': 0,
            'average_cap_rate': 0,
            'average_irr': 0,
            'total_deal_size': 0
        }
    
    metrics = {}
    
    # Count of deals
    metrics['total_deals'] = len(data)
    
    # Try to get cap rate
    cap_rate_cols = [col for col in data.columns if 'cap' in col.lower() and 'rate' in col.lower()]
    if cap_rate_cols:
        cap_rates = []
        for col in cap_rate_cols:
            # Convert to numeric, ignoring errors
            try:
                values = pd.to_numeric(data[col], errors='coerce')
                values = values[values > 0]  # Only positive values
                if not values.empty:
                    cap_rates.extend(values.tolist())
            except:
                pass
        
        # Calculate average cap rate
        if cap_rates:
            metrics['average_cap_rate'] = sum(cap_rates) / len(cap_rates)
        else:
            metrics['average_cap_rate'] = 0
    else:
        metrics['average_cap_rate'] = 0
    
    # Try to get IRR
    irr_cols = [col for col in data.columns if 'irr' in col.lower()]
    if irr_cols:
        irrs = []
        for col in irr_cols:
            try:
                values = pd.to_numeric(data[col], errors='coerce')
                values = values[values > 0]  # Only positive values
                if not values.empty:
                    irrs.extend(values.tolist())
            except:
                pass
        
        # Calculate average IRR
        if irrs:
            metrics['average_irr'] = sum(irrs) / len(irrs)
        else:
            metrics['average_irr'] = 0
    else:
        metrics['average_irr'] = 0
    
    # Try to get deal size
    price_cols = [col for col in data.columns if 'price' in col.lower() or 'cost' in col.lower()]
    if price_cols:
        total_deal_size = 0
        for col in price_cols:
            try:
                values = pd.to_numeric(data[col], errors='coerce')
                values = values[values > 0]  # Only positive values
                if not values.empty:
                    # Use the largest column sum as the deal size
                    col_sum = values.sum()
                    if col_sum > total_deal_size:
                        total_deal_size = col_sum
            except:
                pass
        
        # Convert to millions for display
        metrics['total_deal_size'] = total_deal_size / 1000000
    else:
        metrics['total_deal_size'] = 0
    
    return metrics