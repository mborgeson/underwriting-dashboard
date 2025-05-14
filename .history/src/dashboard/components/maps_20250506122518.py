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
    """Render a map visualization of the properties and rent comps."""
    st.subheader("Property Map")
    
    # Check for the presence of data
    if data.empty:
        st.info("No data available to display on the map.")
        return
    
    try:
        # PART 1: FIND MAIN PROPERTY COORDINATES
        main_lat_col = None
        main_lng_col = None
        
        # Find main property coordinates
        for col in data.columns:
            col_str = str(col).lower()
            # Look for primary property coordinates (avoiding 'comp' in the name)
            if 'latitude' in col_str and 'comp' not in col_str and main_lat_col is None:
                main_lat_col = col
            if ('longitude' in col_str or 'lng' in col_str) and 'comp' not in col_str and main_lng_col is None:
                main_lng_col = col
        
        # PART 2: FIND RENT COMP COORDINATES
        # Create lists to store rent comp columns
        rent_comp_cols = []
        
        # Find all columns related to rent comps with coordinates
        for col in data.columns:
            col_str = str(col).lower()
            if ('rent comp' in col_str or 'rentcomp' in col_str) and ('lat' in col_str or 'lon' in col_str or 'lng' in col_str):
                rent_comp_cols.append(col)
        
        # Check if we have the necessary data
        if (main_lat_col is None or main_lng_col is None) and not rent_comp_cols:
            st.info("No location data found in the dataset. Unable to render map.")
            return
        
        # Create a copy for mapping to avoid modifying the original
        map_data = data.copy()
        
        # PART 3: PREPARE THE MAP
        # Calculate center for the map (using main property if available)
        center_lat = None
        center_lng = None
        
        # Try to get center from main property
        if main_lat_col is not None and main_lng_col is not None:
            try:
                valid_coords = pd.to_numeric(map_data[main_lat_col], errors='coerce').notna() & \
                               pd.to_numeric(map_data[main_lng_col], errors='coerce').notna()
                              
                if valid_coords.any():
                    center_lat = pd.to_numeric(map_data.loc[valid_coords, main_lat_col]).mean()
                    center_lng = pd.to_numeric(map_data.loc[valid_coords, main_lng_col]).mean()
            except Exception as e:
                st.warning(f"Error calculating map center: {str(e)}")
        
        # Default center if we couldn't determine from data
        if center_lat is None or center_lng is None:
            center_lat = 37.0902  # Default to somewhere in the US
            center_lng = -95.7129
        
        # Create the map
        m = folium.Map(location=[center_lat, center_lng], zoom_start=5)
        
        # PART 4: ADD MAIN PROPERTIES TO MAP
        if main_lat_col is not None and main_lng_col is not None:
            # Deal stage to color mapping
            stage_colors = {
                "0) Dead Deals": "gray",
                "1) Initial UW and Review": "blue",
                "2) Active UW and Review": "orange", 
                "3) Deals Under Contract": "purple",
                "4) Closed Deals": "green",
                "5) Realized Deals": "red"
            }
            
            # Get property name column
            property_col = None
            for col in map_data.columns:
                if 'name' in str(col).lower() and 'property' in str(col).lower():
                    property_col = col
                    break
            
            if property_col is None:
                # Fallback to first column if no property name is found
                property_col = map_data.columns[0]
            
            # Process rows with valid coordinates
            for idx, row in map_data.iterrows():
                try:
                    # Extract and convert coordinates
                    lat_val = pd.to_numeric(row[main_lat_col], errors='coerce')
                    lng_val = pd.to_numeric(row[main_lng_col], errors='coerce')
                    
                    # Skip invalid coordinates
                    if pd.isna(lat_val) or pd.isna(lng_val) or lat_val == 0 or lng_val == 0:
                        continue
                    
                    # Check coordinate validity
                    if lat_val < -90 or lat_val > 90 or lng_val < -180 or lng_val > 180:
                        continue
                    
                    # Get deal stage for color
                    color = "blue"  # Default color
                    if 'Deal_Stage_Subdirectory_Name' in row:
                        stage = row['Deal_Stage_Subdirectory_Name']
                        if stage in stage_colors:
                            color = stage_colors[stage]
                    
                    # Create popup content
                    popup_content = f"<strong>Main Property</strong><br>"
                    
                    # Add property name if available
                    if property_col in row:
                        popup_content += f"<strong>{row[property_col]}</strong><br>"
                    
                    # Add city/state if available
                    for field in ['City', 'State', 'Address']:
                        for col in map_data.columns:
                            if field.lower() in str(col).lower() and 'comp' not in str(col).lower():
                                popup_content += f"{field}: {row[col]}<br>"
                                break
                    
                    # Add deal stage if available
                    if 'Deal_Stage_Subdirectory_Name' in row:
                        popup_content += f"Stage: {row['Deal_Stage_Subdirectory_Name']}<br>"
                    
                    # Add marker
                    folium.Marker(
                        location=[float(lat_val), float(lng_val)],
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=str(row[property_col]) if property_col in row else "Main Property",
                        icon=folium.Icon(color=color, icon="home")
                    ).add_to(m)
                except Exception as e:
                    continue  # Skip this row if there's an error
        
        # PART 5: ADD RENT COMPS TO MAP
        added_comps = 0
        
        # Group rent comp columns by comp number
        comp_groups = {}
        for col in rent_comp_cols:
            col_str = str(col).lower()
            # Extract comp number (assuming format like "Rent Comp 1 Latitude")
            for i in range(1, 20):  # Support up to 20 comps
                if f"comp {i}" in col_str or f"comp{i}" in col_str:
                    if i not in comp_groups:
                        comp_groups[i] = {"lat": None, "lng": None, "name": None}
                    
                    if "lat" in col_str:
                        comp_groups[i]["lat"] = col
                    elif "lon" in col_str or "lng" in col_str:
                        comp_groups[i]["lng"] = col
                    
                    # Also try to find name columns for comps
                    name_col = None
                    for potential_name_col in data.columns:
                        potential_name = str(potential_name_col).lower()
                        if (f"comp {i} name" in potential_name or 
                            f"comp{i} name" in potential_name or
                            f"comp {i}_name" in potential_name):
                            comp_groups[i]["name"] = potential_name_col
                            break
        
        # Process each comp group
        for idx, row in map_data.iterrows():
            for comp_num, comp_cols in comp_groups.items():
                try:
                    # Skip if we don't have both lat and lng
                    if comp_cols["lat"] is None or comp_cols["lng"] is None:
                        continue
                    
                    # Extract and convert coordinates
                    lat_val = pd.to_numeric(row[comp_cols["lat"]], errors='coerce')
                    lng_val = pd.to_numeric(row[comp_cols["lng"]], errors='coerce')
                    
                    # Skip invalid coordinates
                    if pd.isna(lat_val) or pd.isna(lng_val) or lat_val == 0 or lng_val == 0:
                        continue
                    
                    # Check coordinate validity
                    if lat_val < -90 or lat_val > 90 or lng_val < -180 or lng_val > 180:
                        continue
                    
                    # Create popup content
                    popup_content = f"<strong>Rent Comp #{comp_num}</strong><br>"
                    
                    # Add comp name if available
                    if comp_cols["name"] is not None and comp_cols["name"] in row:
                        popup_content += f"<strong>{row[comp_cols['name']]}</strong><br>"
                    
                    # Add main property reference
                    if property_col in row:
                        popup_content += f"Referenced by: {row[property_col]}<br>"
                    
                    # Add coordinates
                    popup_content += f"Latitude: {lat_val}<br>"
                    popup_content += f"Longitude: {lng_val}<br>"
                    
                    # Add marker with different icon for rent comps
                    folium.Marker(
                        location=[float(lat_val), float(lng_val)],
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=f"Rent Comp #{comp_num}",
                        icon=folium.Icon(color="green", icon="building", prefix="fa")
                    ).add_to(m)
                    
                    added_comps += 1
                except Exception as e:
                    continue  # Skip this comp if there's an error
        
        # PART 6: CREATE THE LEGEND
        # Add a legend to the map
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 220px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color:white; padding: 8px;
                    opacity: 0.8;">
        <p style="margin-bottom: 5px; font-weight: bold;">Map Legend</p>
        '''
        
        # Main properties legend section
        legend_html += '<p style="margin-bottom: 3px; margin-top: 8px;"><b>Main Properties</b></p>'
        
        for stage, color in stage_colors.items():
            legend_html += f'''
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: {color}; width: 20px; height: 20px; margin-right: 5px;"></div>
                <span>{stage}</span>
            </div>
            '''
        
        # Rent comps legend section
        legend_html += '''
        <p style="margin-bottom: 3px; margin-top: 8px;"><b>Rent Comps</b></p>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="background-color: green; width: 20px; height: 20px; margin-right: 5px;"></div>
            <span>Rent Comparables</span>
        </div>
        '''
        
        legend_html += '</div>'
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # PART 7: DISPLAY THE MAP
        st.write(f"Map shows {len(map_data)} main properties and {added_comps} rent comps")
        folium_static(m, width=800, height=600)
        
    except Exception as e:
        st.error(f"Error rendering map: {str(e)}")
        st.write("Try adjusting your filters to include properties with valid coordinates.")