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

def render_sidebar_filters(compact=False):
    """Render the sidebar filters for the dashboard with mobile optimization."""
    st.sidebar.title("Filters" if not compact else "📊 Filters")
    
    # Search box - same for both mobile and desktop
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
    
    # If on mobile, use an expander for deal stage filters to save space
    if compact:
        with st.sidebar.expander("Deal Stage", expanded=False):
            render_deal_stage_filters()
    else:
        st.sidebar.subheader("Deal Stage")
        render_deal_stage_filters()
    
    st.sidebar.markdown("---")
    
    # Property filters - more compact on mobile
    if compact:
        with st.sidebar.expander("Property Details", expanded=False):
            render_property_filters()
    else:
        st.sidebar.subheader("Property Details")
        render_property_filters()
    
    st.sidebar.markdown("---")
    
    # Date filters
    if compact:
        with st.sidebar.expander("Date Filters", expanded=False):
            render_date_filters()
    else:
        st.sidebar.subheader("Date Filters")
        render_date_filters()
    
    st.sidebar.markdown("---")
    
    # Advanced filters - always in expander
    with st.sidebar.expander("Advanced Filters"):
        render_advanced_filters()
    
    # Reset filters button
    if st.sidebar.button("Reset All Filters"):
        st.session_state['filters'] = {}
        st.session_state['search_term'] = ""
        st.session_state['data'] = None  # Force data reload
        st.experimental_rerun()