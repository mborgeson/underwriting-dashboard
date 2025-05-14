# src/dashboard/components/filters.py

"""
Dashboard Filters Component

This module provides the sidebar filters for the Underwriting Dashboard.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.database.db_manager import DatabaseManager
from config.config import DATABASE_TABLE
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).resolve().parents[3])
sys.path.append(project_root)

from src.database.db_manager import get_column_values, DatabaseManager

def render_deal_stage_filters():
    """Render deal stage filter components."""
    db_manager = DatabaseManager()
    deal_stages = db_manager.get_column_values("Deal_Stage_Subdirectory_Name")
    
    selected_stages = st.multiselect(
        "Select Deal Stages",
        options=deal_stages,
        default=st.session_state.get('filters', {}).get('Deal_Stage_Subdirectory_Name', [])
    )
    
    if 'filters' not in st.session_state:
        st.session_state['filters'] = {}
        
    # Update filters in session state
    if selected_stages:
        st.session_state['filters']['Deal_Stage_Subdirectory_Name'] = selected_stages
    elif 'Deal_Stage_Subdirectory_Name' in st.session_state['filters']:
        del st.session_state['filters']['Deal_Stage_Subdirectory_Name']
        st.session_state['data'] = None  # Force data reload

def render_property_filters():
    """Render property filter components."""
    db_manager = DatabaseManager()
    
    # City filter
    cities = db_manager.get_column_values("Propety_Info__Deal_City_")
    selected_cities = st.multiselect(
        "Cities",
        options=cities,
        default=st.session_state.get('filters', {}).get('Propety_Info__Deal_City_', [])
    )
    
    if selected_cities:
        st.session_state['filters']['Propety_Info__Deal_City_'] = selected_cities
    elif 'Propety_Info__Deal_City_' in st.session_state['filters']:
        del st.session_state['filters']['Propety_Info__Deal_City_']
        st.session_state['data'] = None  # Force data reload
    
    # State filter
    states = db_manager.get_column_values("Propety_Info__Deal_State_")
    selected_states = st.multiselect(
        "States",
        options=states,
        default=st.session_state.get('filters', {}).get('Propety_Info__Deal_State_', [])
    )
    
    if selected_states:
        st.session_state['filters']['Propety_Info__Deal_State_'] = selected_states
    elif 'Propety_Info__Deal_State_' in st.session_state['filters']:
        del st.session_state['filters']['Propety_Info__Deal_State_']
        st.session_state['data'] = None  # Force data reload

def render_date_filters():
    """Render date filter components."""
    date_col_options = ["Last_Modified_Date", "Date_Uploaded"]
    date_column = st.selectbox(
        "Date Column",
        options=date_col_options,
        index=0
    )
    
    # Get min and max dates safely
    try:
        db_manager = DatabaseManager()
        db_manager.connect()
        
        # Use proper SQL syntax for min/max
        min_query = f"SELECT MIN({date_column}) FROM {DATABASE_TABLE}"
        max_query = f"SELECT MAX({date_column}) FROM {DATABASE_TABLE}"
        
        db_manager.cursor.execute(min_query)
        min_date_str = db_manager.cursor.fetchone()[0]
        
        db_manager.cursor.execute(max_query)
        max_date_str = db_manager.cursor.fetchone()[0]
        
        db_manager.disconnect()
        
        min_date = datetime.now().replace(year=datetime.now().year - 1)
        max_date = datetime.now()
        
        if min_date_str:
            min_date = pd.to_datetime(min_date_str)
        if max_date_str:
            max_date = pd.to_datetime(max_date_str)
    except Exception as e:
        # Fallback to default date range if query fails
        st.warning(f"Using default date range (last year to now)")
        min_date = datetime.now().replace(year=datetime.now().year - 1)
        max_date = datetime.now()
    
    date_range = st.date_input(
        "Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        date_filter = {
            'operator': 'BETWEEN',
            'value': (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        }
        st.session_state['filters'][date_column] = date_filter
    elif date_column in st.session_state['filters']:
        del st.session_state['filters'][date_column]
        st.session_state['data'] = None  # Force data reload

def render_advanced_filters():
    """Render advanced filter components."""
    # Performance metrics filters
    st.subheader("Performance Metrics")
    
    # Cap Rate filter
    cap_rate_col = "Exit_Cap_Rate"
    min_cap, max_cap = 3.0, 10.0
    
    cap_rate_range = st.slider(
        "Cap Rate (%)",
        min_value=min_cap,
        max_value=max_cap,
        value=(min_cap, max_cap),
        step=0.1
    )
    
    if cap_rate_range != (min_cap, max_cap):
        cap_filter = {
            'operator': 'BETWEEN',
            'value': cap_rate_range
        }
        st.session_state['filters'][cap_rate_col] = cap_filter
    elif cap_rate_col in st.session_state['filters']:
        del st.session_state['filters'][cap_rate_col]
        st.session_state['data'] = None  # Force data reload
    
    # IRR filter
    irr_col = "Levered_IRR"
    min_irr, max_irr = 10.0, 30.0
    
    irr_range = st.slider(
        "IRR (%)",
        min_value=min_irr,
        max_value=max_irr,
        value=(min_irr, max_irr),
        step=0.5
    )
    
    if irr_range != (min_irr, max_irr):
        irr_filter = {
            'operator': 'BETWEEN',
            'value': irr_range
        }
        st.session_state['filters'][irr_col] = irr_filter
    elif irr_col in st.session_state['filters']:
        del st.session_state['filters'][irr_col]
        st.session_state['data'] = None  # Force data reload

def render_sidebar_filters(compact=False):
    """Render the sidebar filters for the dashboard with mobile optimization."""
    # Remove debug text
    
    st.sidebar.title("Filters" if not compact else "📊 Filters")
    
    # Search box
    st.sidebar.subheader("Search")
    search_term = st.sidebar.text_input(
        "Search all fields",
        value=st.session_state.get('search_term', '')
    )
    
    if search_term != st.session_state.get('search_term', ''):
        st.session_state['search_term'] = search_term
        st.session_state['data'] = None  # Force data reload
    
    st.sidebar.markdown("---")
    
    # Deal Stage filter
    st.sidebar.subheader("Deal Stage")
    
    # Get real deal stages from database when ready
    deal_stages = ["0) Dead Deals", "1) Initial UW and Review", "2) Active UW and Review", 
                  "3) Deals Under Contract", "4) Closed Deals", "5) Realized Deals"]
    
    selected_stages = st.sidebar.multiselect(
        "Select Deal Stages",
        options=deal_stages,
        default=[]
    )
    
    if 'filters' not in st.session_state:
        st.session_state['filters'] = {}
        
    # Update filters in session state
    if selected_stages:
        st.session_state['filters']['Deal_Stage_Subdirectory_Name'] = selected_stages
    elif 'Deal_Stage_Subdirectory_Name' in st.session_state['filters']:
        del st.session_state['filters']['Deal_Stage_Subdirectory_Name']
        st.session_state['data'] = None  # Force data reload
    
    st.sidebar.markdown("---")
    
    # Property filters
    st.sidebar.subheader("Property Details")
    
    # Cities filter
    cities = ["Phoenix", "Chicago", "Atlanta", "New York", "Los Angeles"]
    selected_cities = st.sidebar.multiselect(
        "Cities",
        options=cities,
        default=[]
    )
    
    # States filter
    states = ["AZ", "IL", "GA", "NY", "CA"]
    selected_states = st.sidebar.multiselect(
        "States",
        options=states,
        default=[]
    )
    
    st.sidebar.markdown("---")
    
    # Date filters
    st.sidebar.subheader("Date Filters")
    
    date_col_options = ["Last_Modified_Date", "Date_Uploaded"]
    date_column = st.sidebar.selectbox(
        "Date Column",
        options=date_col_options,
        index=0
    )
    
    # Date range picker
    min_date = datetime.now().replace(year=datetime.now().year - 1)
    max_date = datetime.now()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date.date(), max_date.date())
    )
    
    st.sidebar.markdown("---")
    
    # Reset filters button
    if st.sidebar.button("Reset All Filters"):
        st.session_state['filters'] = {}
        st.session_state['search_term'] = ""
        st.session_state['data'] = None  # Force data reload
        st.experimental_rerun()
    
    # Debug info section removed