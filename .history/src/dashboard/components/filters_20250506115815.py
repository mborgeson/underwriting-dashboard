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

def render_sidebar_filters():
    """Render the sidebar filters for the dashboard."""
    st.sidebar.title("Filters")
    
    # Search box
    st.sidebar.subheader("Search")
    search_term = st.sidebar.text_input(
        "Search all fields",
        value=st.session_state.get('search_term', ''),
        help="Enter keywords to search across all fields"
    )
    
    if search_term != st.session_state.get('search_term', ''):
        st.session_state['search_term'] = search_term
        st.session_state['data'] = None  # Force data reload
    
    st.sidebar.markdown("---")
    
    # Deal Stage filter
    st.sidebar.subheader("Deal Stage")
    
    db_manager = DatabaseManager()
    deal_stages = db_manager.get_column_values("Deal_Stage_Subdirectory_Name")
    
    selected_stages = st.sidebar.multiselect(
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
    
    st.sidebar.markdown("---")
    
    # Property filters
    st.sidebar.subheader("Property Details")
    
    # City filter
    cities = db_manager.get_column_values("Propety_Info__Deal_City_")
    selected_cities = st.sidebar.multiselect(
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
    selected_states = st.sidebar.multiselect(
        "States",
        options=states,
        default=st.session_state.get('filters', {}).get('Propety_Info__Deal_State_', [])
    )
    
    if selected_states:
        st.session_state['filters']['Propety_Info__Deal_State_'] = selected_states
    elif 'Propety_Info__Deal_State_' in st.session_state['filters']:
        del st.session_state['filters']['Propety_Info__Deal_State_']
        st.session_state['data'] = None  # Force data reload
    
    st.sidebar.markdown("---")
    
    # Date filter
    st.sidebar.subheader("Date Filters")
    
    date_col_options = ["Last_Modified_Date", "Date_Uploaded"]
    date_column = st.sidebar.selectbox(
        "Date Column",
        options=date_col_options,
        index=0
    )
    
    # Get min and max dates from database
    min_date_str = db_manager.get_column_values(f"MIN({date_column})")
    max_date_str = db_manager.get_column_values(f"MAX({date_column})")
    
    min_date = datetime.now().replace(year=datetime.now().year - 1)
    max_date = datetime.now()
    
    try:
        if min_date_str and min_date_str[0]:
            min_date = pd.to_datetime(min_date_str[0])
        if max_date_str and max_date_str[0]:
            max_date = pd.to_datetime(max_date_str[0])
    except:
        pass
    
    date_range = st.sidebar.date_input(
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
    
    st.sidebar.markdown("---")
    
    # Advanced filters - shown in an expander
    with st.sidebar.expander("Advanced Filters"):
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
    
    # Reset filters button
    if st.sidebar.button("Reset All Filters"):
        st.session_state['filters'] = {}
        st.session_state['search_term'] = ""
        st.session_state['data'] = None  # Force data reload
        st.experimental_rerun()
    
    # Display active filters
    if st.session_state['filters'] or st.session_state['search_term']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Active Filters")
        
        if st.session_state['search_term']:
            st.sidebar.markdown(f"🔍 Search: **{st.session_state['search_term']}**")
        
        for key, value in st.session_state['filters'].items():
            display_key = key.replace('_', ' ').replace('__', ' - ')
            if isinstance(value, dict) and 'operator' in value:
                if value['operator'] == 'BETWEEN':
                    st.sidebar.markdown(f"📊 {display_key}: **{value['value'][0]}** to **{value['value'][1]}**")
                else:
                    st.sidebar.markdown(f"📊 {display_key} {value['operator']} **{value['value']}**")
            elif isinstance(value, list):
                st.sidebar.markdown(f"📊 {display_key}: **{', '.join(str(v) for v in value)}**")
            else:
                st.sidebar.markdown(f"📊 {display_key}: **{value}**")