# src/dashboard/components/maps.py

"""
Dashboard Maps Component

This module provides the map visualization functionality for the Underwriting Dashboard.
"""

import streamlit as st
import pandas as pd
import folium
import streamlit_folium
from streamlit_folium import folium_static
import sys
from pathlib import Path
import numpy as np

# Add project root to path for imports
project_root = str(Path(__file__).resolve().parents[3])
sys.path.append(project_root)

def render_property_map(data):
    """Render a map visualization of the properties.
    
    Args:
        data: DataFrame containing the property data to display on the map
    """
    st.subheader("Property Map")
    
    # Check for the presence of data
    if data.empty:
        st.info("No data available to display on the map.")
        return
    
    # Fix for conversion errors - properly handle latitude/longitude columns
    lat_col = None
    lng_col = None
    
    # Try to find the right latitude/longitude columns by examining column names
    for col in data.columns:
        col_str = str(col).lower()
        if 'lat' in col_str and lat_col is None:
            lat_col = col
        if ('lon' in col_str or 'lng' in col_str) and lng_col is None:
            lng_col = col
    
    if lat_col is None or lng_col is None:
        st.info("Location data (latitude/longitude) not found in the dataset. Unable to render map.")
        st.write("Available columns:", data.columns.tolist())
        return
    
    # Create a copy for mapping to avoid modifying the original
    map_data = data.copy()
    
    # Debug output
    st.write(f"Using columns for mapping: Latitude = {lat_col}, Longitude = {lng_col}")
    
    # Handle data conversion properly with defensive error checking
    try:
        # First ensure the columns exist
        if lat_col not in map_data.columns or lng_col not in map_data.columns:
            st.error(f"Column {lat_col} or {lng_col} not found in dataset")
            return
            
        # Remove any rows where lat/lng are strings that can't be converted to numbers
        # (like literal "Latitude" or "Longitude" values)
        def is_numeric_or_convertible(x):
            if pd.isna(x):
                return False
            try:
                float(x)
                return True
            except (ValueError, TypeError):
                return False
        
        # Filter rows that have valid lat/lng values
        valid_lat = map_data[lat_col].apply(is_numeric_or_convertible)
        valid_lng = map_data[lng_col].apply(is_numeric_or_convertible)
        map_data = map_data[valid_lat & valid_lng].copy()
        
        # Now convert to numeric values
        map_data[lat_col] = pd.to_numeric(map_data[lat_col], errors='coerce')
        map_data[lng_col] = pd.to_numeric(map_data[lng_col], errors='coerce')
        
        # Drop rows with NaN values from conversion or zeros
        map_data = map_data.dropna(subset=[lat_col, lng_col])
        map_data = map_data[(map_data[lat_col] != 0) & (map_data[lng_col] != 0)]
        
        # Sanity check the values (latitudes between -90 and 90, longitudes between -180 and 180)
        map_data = map_data[
            (map_data[lat_col] >= -90) & (map_data[lat_col] <= 90) &
            (map_data[lng_col] >= -180) & (map_data[lng_col] <= 180)
        ]
        
        if map_data.empty:
            st.warning("No valid geographic coordinates found in the data after filtering.")
            return
            
        # Calculate center for the map
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
        property_col = None
        for col in map_data.columns:
            if 'name' in str(col).lower() and 'property' in str(col).lower():
                property_col = col
                break
        
        if property_col is None:
            # Fallback to first column if no property name is found
            property_col = map_data.columns[0]
        
        # Add markers for each property
        for idx, row in map_data.iterrows():
            # Get deal stage for color
            color = "blue"  # Default color
            
            if 'Deal_Stage_Subdirectory_Name' in row:
                stage = row['Deal_Stage_Subdirectory_Name']
                if stage in stage_colors:
                    color = stage_colors[stage]
            
            # Create popup content
            popup_content = ""
            
            # Add property name if available
            if property_col in row:
                popup_content += f"<strong>{row[property_col]}</strong><br>"
            
            # Add city/state if available
            for field in ['City', 'State', 'Address']:
                for col in map_data.columns:
                    if field.lower() in str(col).lower():
                        popup_content += f"{field}: {row[col]}<br>"
                        break
            
            # Add deal stage if available
            if 'Deal_Stage_Subdirectory_Name' in row:
                popup_content += f"Stage: {row['Deal_Stage_Subdirectory_Name']}<br>"
            
            # Add marker
            folium.Marker(
                location=[float(row[lat_col]), float(row[lng_col])],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=str(row[property_col]) if property_col in row else "Property",
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
        st.write(f"Displaying {len(map_data)} properties on the map")
        folium_static(m, width=800, height=600)
        
    except Exception as e:
        st.error(f"Error rendering map: {str(e)}")
        st.write("Try adjusting your filters to include properties with valid coordinates.")