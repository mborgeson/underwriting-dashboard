# src/dashboard/app.py

"""
Underwriting Dashboard Application

This is the main entry point for the Streamlit dashboard application.
It loads data from the SQLite database and renders the dashboard interface.
"""

import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from pathlib import Path
from datetime import datetime
import sqlite3
import json
from PIL import Image

# Add project root to path for imports
project_root = str(Path(__file__).resolve().parents[2])
sys.path.append(project_root)

# Import modules
from src.database.db_manager import get_all_data, get_filtered_data, search_data
from src.dashboard.components.filters import render_sidebar_filters
from src.dashboard.components.tables import render_data_table
from src.dashboard.components.maps import render_property_map
from src.dashboard.utils.data_processing import process_data_for_display, get_key_metrics
from config.config import DATABASE_PATH, DATABASE_TABLE

# Add imports for responsive components
from src.dashboard.utils.responsive import set_device_type, is_mobile_device, get_screen_info
from src.dashboard.components.layout import responsive_row, mobile_friendly_tabs

# Page configuration
st.set_page_config(
    page_title="B&R Capital - Underwriting Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
def load_css():
    """Load custom CSS styles."""
    css = """
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }
        .subheader {
            font-size: 1.5rem;
            color: #2563EB;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #F3F4F6;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #1E3A8A;
        }
        .metric-label {
            font-size: 1rem;
            color: #4B5563;
        }
        .footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #E5E7EB;
            color: #6B7280;
            font-size: 0.875rem;
        }
        /* Mobile optimizations */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
            }
            .metric-card {
                padding: 0.75rem;
            }
            .metric-value {
                font-size: 1.5rem;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def add_mobile_css():
    """Add responsive CSS to the dashboard."""
    
    mobile_css = """
    <style>
        /* Base responsive grid system */
        .row {
            display: flex;
            flex-wrap: wrap;
            margin: 0 -0.5rem;
        }
        
        /* CSS continues with all the mobile styles... */
    </style>
    """
    
    return st.markdown(mobile_css, unsafe_allow_html=True)

# Initialize session state for filters and search
def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'filters' not in st.session_state:
        st.session_state['filters'] = {}
    
    if 'search_term' not in st.session_state:
        st.session_state['search_term'] = ""
    
    if 'data' not in st.session_state:
        st.session_state['data'] = None
    
    if 'last_refresh' not in st.session_state:
        st.session_state['last_refresh'] = datetime.now()
    
    if 'view_mode' not in st.session_state:
        st.session_state['view_mode'] = "table"  # table, map, or details

def load_data():
    """Load data from the database based on current filters and search term."""
    try:
        # Check if there are active filters
        if st.session_state['filters']:
            data = get_filtered_data(st.session_state['filters'])
        elif st.session_state['search_term']:
            data = search_data(st.session_state['search_term'])
        else:
            data = get_all_data()
        
        # Process data for display
        if not data.empty:
            data = process_data_for_display(data)
        
        st.session_state['data'] = data
        st.session_state['last_refresh'] = datetime.now()
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def refresh_data():
    """Force a data refresh."""
    st.session_state['data'] = None
    return load_data()

def render_header(is_mobile=False):
    """Render the dashboard header."""
    if not is_mobile:
        # Desktop layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown('<div class="main-header">B&R Capital Underwriting Dashboard</div>', unsafe_allow_html=True)
            st.markdown('<div class="subheader">Real Estate Deal Analysis & Tracking</div>', unsafe_allow_html=True)
        
        with col2:
            refresh_col, download_col = st.columns(2)
            
            with refresh_col:
                if st.button("🔄 Refresh", help="Refresh data from the database"):
                    refresh_data()
            
            with download_col:
                if not st.session_state['data'] is None and not st.session_state['data'].empty:
                    csv = st.session_state['data'].to_csv(index=False)
                    st.download_button(
                        label="📥 Export",
                        data=csv,
                        file_name=f"underwriting_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        help="Download the current data as CSV"
                    )
    else:
        # Mobile layout - more compact
        st.markdown('<div class="main-header">B&R Capital Dashboard</div>', unsafe_allow_html=True)
        
        # Single row of buttons
        button_col1, button_col2 = st.columns(2)
        
        with button_col1:
            if st.button("🔄 Refresh", help="Refresh data from the database"):
                refresh_data()
        
        with button_col2:
            if not st.session_state['data'] is None and not st.session_state['data'].empty:
                csv = st.session_state['data'].to_csv(index=False)
                st.download_button(
                    label="📥 Export",
                    data=csv,
                    file_name=f"underwriting_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    help="Download the current data as CSV"
                )

def render_metrics(data):
    """Render key metrics at the top of the dashboard."""
    if data.empty:
        st.warning("No data available to display metrics.")
        return
    
    metrics = get_key_metrics(data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['total_deals']}</div>
                <div class="metric-label">Total Deals</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['average_cap_rate']:.2f}%</div>
                <div class="metric-label">Avg Cap Rate</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['average_irr']:.2f}%</div>
                <div class="metric-label">Avg IRR</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">${metrics['total_deal_size']:,.0f}M</div>
                <div class="metric-label">Total Deal Size</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

def render_metrics_mobile(data):
    """Render key metrics optimized for mobile display."""
    if data.empty:
        st.warning("No data available to display metrics.")
        return
    
    metrics = get_key_metrics(data)
    
    # Use 2 columns instead of 4 for mobile
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['total_deals']}</div>
                <div class="metric-label">Total Deals</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['average_cap_rate']:.2f}%</div>
                <div class="metric-label">Avg Cap Rate</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['average_irr']:.2f}%</div>
                <div class="metric-label">Avg IRR</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">${metrics['total_deal_size']:,.0f}M</div>
                <div class="metric-label">Total Deal Size</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

def render_main_content(data):
    """Render the main content area of the dashboard."""
    if data.empty:
        st.warning("No data available. Try adjusting your filters or search criteria.")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Table View", "Map View", "Analytics"])
    
    with tab1:
        render_data_table(data)
    
    with tab2:
        render_property_map(data)
    
    with tab3:
        render_analytics(data)

def render_analytics(data, is_mobile=False):
    """Render analytics charts and visualizations."""
    st.subheader("Deal Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Deal stages breakdown
        if 'Deal_Stage_Subdirectory_Name' in data.columns:
            stage_counts = data['Deal_Stage_Subdirectory_Name'].value_counts().reset_index()
            stage_counts.columns = ['Deal Stage', 'Count']
            
            fig = px.pie(
                stage_counts, 
                values='Count', 
                names='Deal Stage', 
                title='Deals by Stage',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Geographic distribution
        if 'Propety_Info__Deal_City_' in data.columns:
            city_counts = data['Propety_Info__Deal_City_'].value_counts().reset_index()
            city_counts.columns = ['City', 'Count']
            city_counts = city_counts.sort_values('Count', ascending=True).tail(10)  # Top 10
            
            fig = px.bar(
                city_counts,
                x='Count',
                y='City',
                orientation='h',
                title='Top 10 Cities by Deal Count',
                color='Count',
                color_continuous_scale=px.colors.sequential.Blues
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics over time if date columns are available
    date_col = None
    for col in ['Last_Modified_Date', 'Date_Uploaded']:
        if col in data.columns:
            date_col = col
            break
    
    if date_col and 'Propety_Info__Deal_Name_' in data.columns:
        try:
            timeline_data = data.copy()
            timeline_data[date_col] = pd.to_datetime(timeline_data[date_col])
            timeline_data = timeline_data.sort_values(date_col)
            
            st.subheader("Deal Timeline")
            fig = px.scatter(
                timeline_data,
                x=date_col,
                y='Propety_Info__Deal_Name_',
                color='Deal_Stage_Subdirectory_Name' if 'Deal_Stage_Subdirectory_Name' in timeline_data.columns else None,
                title='Deal Timeline',
                height=600
            )
            fig.update_traces(marker=dict(size=12))
            fig.update_layout(yaxis_title="Deal Name", xaxis_title="Date")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering timeline: {str(e)}")

def render_footer():
    """Render the dashboard footer."""
    st.markdown(
        """
        <div class="footer">
            <p>B&R Capital Underwriting Dashboard | Last updated: {last_refresh}</p>
            <p>© {year} B&R Capital. All rights reserved.</p>
        </div>
        """.format(
            last_refresh=st.session_state['last_refresh'].strftime("%Y-%m-%d %H:%M:%S"),
            year=datetime.now().year
        ),
        unsafe_allow_html=True
    )


def run_dashboard():
    """Main function to run the dashboard."""
    # Set device type for responsive design
    set_device_type()
    
    # Load custom CSS including mobile optimizations
    load_css()
    
    # Add mobile CSS
    add_mobile_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Get screen information
    screen_info = get_screen_info()
    
    # Add debug info for device detection
    st.write(f"Detected device: {'Mobile' if is_mobile_device() else 'Desktop'}")    
    st.session_state['is_mobile'] = screen_info['is_mobile']
    
    # Render sidebar filters - conditional: more compact on mobile
    render_sidebar_filters(compact=screen_info['is_mobile'])
    
    # Load data if not already loaded
    if st.session_state['data'] is None:
        data = load_data()
    else:
        data = st.session_state['data']
    
    # Render header with responsive layout
    render_header(is_mobile=screen_info['is_mobile'])
    
    # Render key metrics with responsive layout
    if screen_info['is_mobile']:
        # On mobile, use 2 columns instead of 4
        render_metrics_mobile(data)
    else:
        render_metrics(data)
    
    # Render main content with mobile-friendly tabs
    tabs_dict = {
        "Table View": lambda: render_data_table(data, is_mobile=screen_info['is_mobile']),
        "Map View": lambda: render_property_map(data),
        "Analytics": lambda: render_analytics(data, is_mobile=screen_info['is_mobile'])
    }
    mobile_friendly_tabs(tabs_dict)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    run_dashboard()