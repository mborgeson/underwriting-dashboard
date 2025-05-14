# src/dashboard/utils/data_processing.py

"""
Dashboard Data Processing Utilities

This module provides data processing utilities for the Underwriting Dashboard.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def process_data_for_display(data: pd.DataFrame) -> pd.DataFrame:
    """Process data for display in the dashboard.
    
    Args:
        data: Raw DataFrame from the database
        
    Returns:
        Processed DataFrame ready for display
    """
    if data.empty:
        return data
    
    # Create a copy to avoid modifying the original
    processed_data = data.copy()
    
    # Convert date columns to datetime
    date_columns = [
        'Last_Modified_Date', 
        'Date_Uploaded'
    ]
    
    for col in date_columns:
        if col in processed_data.columns:
            processed_data[col] = pd.to_datetime(processed_data[col], errors='coerce')
    
    # Format percentage columns
    percentage_columns = [
        'Exit_Cap_Rate',
        'Levered_IRR',
        'Unlevered_IRR',
        'Cash_on_Cash',
        'Loan_to_Value'
    ]
    
    for col in processed_data.columns:
        col_lower = col.lower()
        if any(term in col_lower for term in ['percentage', 'percent', 'rate', 'irr', 'yield', 'return']):
            processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')
    
    # Format currency columns
    currency_columns = [
        'Purchase_Price',
        'Sale_Price',
        'Total_Cost',
        'NOI',
        'Revenue'
    ]
    
    for col in processed_data.columns:
        col_lower = col.lower()
        if any(term in col_lower for term in ['price', 'cost', 'value', 'amount', '$', 'dollar', 'revenue', 'income']):
            processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')
    
    # Handle JSON metadata column if present
    if 'Metadata' in processed_data.columns:
        try:
            # This would need to be expanded based on the actual structure of your metadata
            pass
        except:
            pass
    
    return processed_data

def get_key_metrics(data: pd.DataFrame) -> Dict[str, Any]:
    """Calculate key metrics from the data for dashboard display.
    
    Args:
        data: Processed DataFrame
        
    Returns:
        Dictionary of key metrics
    """
    metrics = {
        'total_deals': len(data),
        'average_cap_rate': 0.0,
        'average_irr': 0.0,
        'total_deal_size': 0.0
    }
    
    # Cap Rate calculation
    cap_rate_columns = [col for col in data.columns if 'cap_rate' in col.lower()]
    if cap_rate_columns:
        cap_rates = data[cap_rate_columns[0]].dropna()
        if not cap_rates.empty:
            # Convert to numeric, assuming percentage values
            cap_rates = pd.to_numeric(cap_rates, errors='coerce')
            metrics['average_cap_rate'] = cap_rates.mean()
    
    # IRR calculation
    irr_columns = [col for col in data.columns if 'irr' in col.lower()]
    if irr_columns:
        irrs = data[irr_columns[0]].dropna()
        if not irrs.empty:
            # Convert to numeric, assuming percentage values
            irrs = pd.to_numeric(irrs, errors='coerce')
            metrics['average_irr'] = irrs.mean()
    
    # Total deal size calculation
    price_columns = [col for col in data.columns if any(term in col.lower() for term in ['purchase_price', 'acquisition_price', 'deal_size'])]
    if price_columns:
        prices = data[price_columns[0]].dropna()
        if not prices.empty:
            # Convert to numeric
            prices = pd.to_numeric(prices, errors='coerce')
            # Sum and convert to millions
            metrics['total_deal_size'] = prices.sum() / 1000000
    
    return metrics