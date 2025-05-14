# src/dashboard/components/maps.py

"""
Dashboard Maps Component

This module provides the map visualization functionality for the Underwriting Dashboard.
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import sys
from pathlib import Path
import numpy as np

# Add project root to path for imports
project_root = str(Path(__file__).resolve().parents[3])
sys.path.append(project_root)

def render_property_map(data):
    """Render a map visualization of the properties."""
    st.subheader("Property Map")
    
    # Check if we have location data
    lat_col = None
    lng_col = None
    
    # Try to find latitude/longitude columns
    for col in data.columns:
        col_lower = col.lower()
        if 'latitude' in col_lower or 'lat' in col_lower:
            lat_col = col
        if 'longitude' in col_lower or 'lng' in col_lower or 'long' in col_lower:
            lng_col = col
    
    if lat_col is None or lng_col is None:
        st.info("Location data (latitude/longitude) not found in the dataset. Unable to render map.")
        return
    
    # Filter to only rows with valid coordinates
    map_data = data.copy()
    
    # Convert coordinates to numeric
    try:
        map_data[lat_col] = pd.to_numeric(map_data[lat_col], errors='coerce')
        map_data[lng_col] = pd.to_numeric(map_data[lng_col], errors='coerce')
    except Exception as e:
        st.error(f"Error converting coordinates to numeric: {str(e)}")
        return
    
    # Filter out invalid values
    map_data = map_data[
        map_data[lat_col].notna() & 
        map_data[lng_col].notna() &
        (map_data[lat_col] != 0) &
        (map_data[lng_col] != 0)
    ]
    
    if map_data.empty:
        st.info("No valid location data found. Unable to render map.")
        return
    
    # Convert coordinates to numeric if they're not already
    map_data[lat_col] = pd.to_numeric(map_data[lat_col], errors='coerce')
    map_data[lng_col] = pd.to_numeric(map_data[lng_col], errors='coerce')
    
    # Drop rows with invalid coordinates
    map_data = map_data.dropna(subset=[lat_col, lng_col])
    
    # Calculate center of the map
    center_lat = map_data[lat_col].mean()
    center_lng = map_data[lng_col].mean()
    
    # Create the map
    m = folium.Map(location=[center_lat, center_lng], zoom_start=5)
    
    # Deal stage to color mapping
    stage_colors = {
        "0) Dead Deals": "gray",
        "1) Initial UW and Review": "blue",
        "2) Active UW and Review": "orange",
        "3) Deals Under Contract": "purple",
        "4) Closed Deals": "green",
        "5) Realized Deals": "red"
    }
    
    # Property name column
    property_name_col = 'Propety_Info__Deal_Name_' if 'Propety_Info__Deal_Name_' in map_data.columns else None
    
    # Add markers for each property
    for idx, row in map_data.iterrows():
        # Get deal stage for color
        if 'Deal_Stage_Subdirectory_Name' in row and row['Deal_Stage_Subdirectory_Name'] in stage_colors:
            color = stage_colors[row['Deal_Stage_Subdirectory_Name']]
        else:
            color = "blue"
        
        # Create popup content
        popup_content = ""
        if property_name_col:
            popup_content += f"<strong>{row[property_name_col]}</strong><br>"
        
        if 'Propety_Info__Deal_City_' in row:
            popup_content += f"City: {row['Propety_Info__Deal_City_']}<br>"
            
        if 'Propety_Info__Deal_State_' in row:
            popup_content += f"State: {row['Propety_Info__Deal_State_']}<br>"
        
        if 'Deal_Stage_Subdirectory_Name' in row:
            popup_content += f"Stage: {row['Deal_Stage_Subdirectory_Name']}<br>"
        
        # Add marker
        folium.Marker(
            location=[row[lat_col], row[lng_col]],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row[property_name_col] if property_name_col else "Property",
            icon=folium.Icon(color=color, icon="home")
        ).add_to(m)
    
    # Add a legend to the map
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 180px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white; padding: 8px;
                opacity: 0.8;">
    <p style="margin-bottom: 5px; font-weight: bold;">Deal Stages</p>
    '''
    
    for stage, color in stage_colors.items():
        legend_html += f'''
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="background-color: {color}; width: 20px; height: 20px; margin-right: 5px;"></div>
            <span>{stage}</span>
        </div>
        '''
    
    legend_html += '</div>'
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Display the map
    folium_static(m, width=1200, height=600)
    
    # Additional map options
    st.write("Map Options:")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Show Rent Comps"):
            st.info("Rent comparables functionality will be added in a future update.")
    
    with col2:
        if st.button("Show Sales Comps"):
            st.info("Sales comparables functionality will be added in a future update.")