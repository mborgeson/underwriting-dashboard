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
    
    # DEBUGGING: Add a section to explore available columns
    with st.expander("Debug Column Information"):
        st.write("Available columns in dataset:")
        columns_df = pd.DataFrame({'Column Name': data.columns})
        st.dataframe(columns_df)
        
        # Add filter to check specific column contents
        col_to_check = st.selectbox("Select column to view values:", data.columns)
        if col_to_check:
            st.write(f"Values in column '{col_to_check}':")
            st.write(data[col_to_check].head(10))
    
    try:
        # PART 1: FIND MAIN PROPERTY COORDINATES
        main_lat_col = None
        main_lng_col = None
        
        # Find main property coordinates - more flexible patterns
        for col in data.columns:
            col_str = str(col).lower()
            
            # Look for primary property latitude (avoiding comp/comparable in the name)
            if (('lat' in col_str) and 
                ('comp' not in col_str) and 
                ('comparable' not in col_str) and 
                main_lat_col is None):
                main_lat_col = col
                
            # Look for primary property longitude
            if (('lon' in col_str or 'lng' in col_str) and 
                ('comp' not in col_str) and 
                ('comparable' not in col_str) and 
                main_lng_col is None):
                main_lng_col = col
        
        # PART 2: FIND RENT COMP COORDINATES - More flexible matching
        rent_comp_lat_cols = []
        rent_comp_lng_cols = []
        
        # Look for any columns that might be rent comp coordinates
        for col in data.columns:
            col_str = str(col).lower()
            
            # Match rent comp latitude columns with more flexible patterns
            if (('lat' in col_str) and 
                (('comp' in col_str) or ('comparable' in col_str))):
                rent_comp_lat_cols.append(col)
                
            # Match rent comp longitude columns
            if ((('lon' in col_str) or ('lng' in col_str)) and 
                (('comp' in col_str) or ('comparable' in col_str))):
                rent_comp_lng_cols.append(col)
        
        # DEBUGGING: Show found coordinate columns
        with st.expander("Coordinate Columns Detected"):
            st.write("Main Property Coordinates:")
            st.write(f"Latitude Column: {main_lat_col}")
            st.write(f"Longitude Column: {main_lng_col}")
            
            st.write("Rent Comp Coordinates:")
            st.write(f"Latitude Columns: {rent_comp_lat_cols}")
            st.write(f"Longitude Columns: {rent_comp_lng_cols}")
        
        # Check if we have the necessary data
        if (main_lat_col is None or main_lng_col is None) and (not rent_comp_lat_cols or not rent_comp_lng_cols):
            st.warning("No location data found in the dataset. Unable to render map.")
            st.write("Try selecting columns with latitude/longitude data.")
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
        main_properties_added = 0
        
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
                col_str = str(col).lower()
                if (('name' in col_str) and 
                    (('property' in col_str) or ('deal' in col_str)) and
                    ('comp' not in col_str)):
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
                    if pd.isna(lat_val) or pd.isna(lng_val) or abs(lat_val) < 0.001 or abs(lng_val) < 0.001:
                        continue
                    
                    # Check coordinate validity (use broader range to be safe)
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
                    
                    # Add coordinates
                    popup_content += f"Latitude: {lat_val}<br>"
                    popup_content += f"Longitude: {lng_val}<br>"
                    
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
                    
                    main_properties_added += 1
                except Exception as e:
                    st.warning(f"Error adding main property: {str(e)}")
                    continue
        
        # PART 5: ADD RENT COMPS TO MAP - Direct column matching approach
        rent_comps_added = 0
        
        # Pair lat/lng columns that might belong together
        coord_pairs = []
        
        # First try to match by numeric pattern (e.g., "comp 1", "comp 2")
        for lat_col in rent_comp_lat_cols:
            lat_col_lower = str(lat_col).lower()
            
            # Try to find matching number pattern
            for lng_col in rent_comp_lng_cols:
                lng_col_lower = str(lng_col).lower()
                
                # Check if both columns have the same comp number
                matched = False
                for i in range(1, 21):  # Up to 20 comps
                    if (f"comp {i}" in lat_col_lower or f"comp{i}" in lat_col_lower) and \
                       (f"comp {i}" in lng_col_lower or f"comp{i}" in lng_col_lower):
                        coord_pairs.append((lat_col, lng_col, f"Rent Comp {i}"))
                        matched = True
                        break
                
                if matched:
                    break
        
        # For any unmatched columns, try simple pattern matching
        used_lat_cols = [pair[0] for pair in coord_pairs]
        used_lng_cols = [pair[1] for pair in coord_pairs]
        
        for lat_col in rent_comp_lat_cols:
            if lat_col in used_lat_cols:
                continue
                
            lat_col_base = str(lat_col).lower().replace('latitude', '').replace('lat', '')
            
            for lng_col in rent_comp_lng_cols:
                if lng_col in used_lng_cols:
                    continue
                    
                lng_col_base = str(lng_col).lower().replace('longitude', '').replace('long', '').replace('lng', '')
                
                # If the base parts match, pair them
                if lat_col_base.strip() == lng_col_base.strip():
                    coord_pairs.append((lat_col, lng_col, f"Rent Comp"))
                    used_lat_cols.append(lat_col)
                    used_lng_cols.append(lng_col)
                    break
        
        # DEBUGGING: Show coordinate pairs
        with st.expander("Rent Comp Coordinate Pairs"):
            for lat_col, lng_col, name in coord_pairs:
                st.write(f"{name}: {lat_col} + {lng_col}")
        
        # Process each coordinate pair
        for idx, row in map_data.iterrows():
            for lat_col, lng_col, name in coord_pairs:
                try:
                    # Extract and convert coordinates
                    lat_val = pd.to_numeric(row[lat_col], errors='coerce')
                    lng_val = pd.to_numeric(row[lng_col], errors='coerce')
                    
                    # Skip invalid coordinates - more lenient checking
                    if pd.isna(lat_val) or pd.isna(lng_val):
                        continue
                    
                    # Special handling for weird data patterns like dashes
                    if isinstance(row[lat_col], str) and '-' in row[lat_col] and len(row[lat_col].strip()) <= 1:
                        continue
                    
                    if isinstance(row[lng_col], str) and '-' in row[lng_col] and len(row[lng_col].strip()) <= 1:
                        continue
                    
                    # Skip obvious zeros or very small values (likely placeholders)
                    if abs(lat_val) < 0.001 or abs(lng_val) < 0.001:
                        continue
                    
                    # More lenient coordinate validity checking
                    if lat_val < -90 or lat_val > 90 or lng_val < -180 or lng_val > 180:
                        continue
                    
                    # Create popup content
                    popup_content = f"<strong>{name}</strong><br>"
                    
                    # Find associated name if possible
                    name_col = None
                    lat_col_parts = str(lat_col).split()
                    for col in map_data.columns:
                        col_str = str(col).lower()
                        if 'name' in col_str and any(part.lower() in col_str for part in lat_col_parts if len(part) > 2):
                            name_col = col
                            break
                    
                    # Add name if found
                    if name_col and name_col in row and not pd.isna(row[name_col]):
                        popup_content += f"<strong>{row[name_col]}</strong><br>"
                    
                    # Add main property reference
                    if property_col in row:
                        popup_content += f"Referenced by: {row[property_col]}<br>"
                    
                    # Add coordinates
                    popup_content += f"Latitude: {lat_val}<br>"
                    popup_content += f"Longitude: {lng_val}<br>"
                    
                    # Add rent information if available
                    for col in map_data.columns:
                        col_str = str(col).lower()
                        if ('rent' in col_str or 'price' in col_str) and any(part.lower() in col_str for part in lat_col_parts if len(part) > 2):
                            if col in row and not pd.isna(row[col]):
                                popup_content += f"Rent: {row[col]}<br>"
                                break
                    
                    # Add marker with more visible styling for rent comps
                    folium.Marker(
                        location=[float(lat_val), float(lng_val)],
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=name,
                        icon=folium.Icon(color="green", icon="building", prefix="fa")
                    ).add_to(m)
                    
                    # Add a circle to make it more visible
                    folium.CircleMarker(
                        location=[float(lat_val), float(lng_val)],
                        radius=8,
                        color="green",
                        fill=True,
                        fill_color="green",
                        fill_opacity=0.2
                    ).add_to(m)
                    
                    rent_comps_added += 1
                except Exception as e:
                    st.warning(f"Error adding rent comp: {str(e)}")
                    continue
        
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
        if main_properties_added == 0 and rent_comps_added == 0:
            st.warning("No valid coordinates found to display on the map.")
            return
            
        st.write(f"Map shows {main_properties_added} main properties and {rent_comps_added} rent comps")
        folium_static(m, width=800, height=600)
        
    except Exception as e:
        st.error(f"Error rendering map: {str(e)}")
        st.write("Try adjusting your filters to include properties with valid coordinates.")