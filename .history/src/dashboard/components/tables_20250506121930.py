# src/dashboard/components/tables.py

"""
Dashboard Tables Component

This module provides the data table functionality for the Underwriting Dashboard.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).resolve().parents[3])
sys.path.append(project_root)

def render_data_table(data):
    """Render an interactive data table with the provided data.
    
    Args:
        data: DataFrame containing the data to display
    """
    st.subheader("Deal Data")
    
    # Allow column selection
    if not data.empty:
        # Create a safe copy of the data for display
        safe_data = data.copy()
        
        # Pre-process problematic columns (like coordinates with mixed types)
        for col in safe_data.columns:
            col_lower = str(col).lower()
            # Handle coordinate columns that might contain non-numeric values
            if 'lat' in col_lower or 'lon' in col_lower or 'lng' in col_lower:
                # Convert to string to prevent conversion errors
                safe_data[col] = safe_data[col].astype(str)
        
        all_columns = safe_data.columns.tolist()
        
        # Define default columns to show
        default_columns = [
            'Propety_Info__Deal_Name_', 
            'Propety_Info__Deal_City_',
            'Propety_Info__Deal_State_',
            'Deal_Stage_Subdirectory_Name',
            'Last_Modified_Date'
        ]
        
        # Filter default columns to only include those that actually exist in the data
        default_columns = [col for col in default_columns if col in all_columns]
        
        # Allow column selection in an expander
        with st.expander("Select Columns to Display"):
            selected_columns = st.multiselect(
                "Choose columns",
                options=all_columns,
                default=default_columns
            )
        
        if not selected_columns:  # If no columns are selected, use defaults
            selected_columns = default_columns
        
        # Apply column selection
        display_data = safe_data[selected_columns].copy()
        
        # Create a clean display version with better column names
        display_data.columns = [col.replace('_', ' ').replace('__', ' - ') for col in selected_columns]
        
        # Display row count and pagination options
        row_count = len(display_data)
        st.write(f"Displaying {row_count} deals")
        
        page_size_options = [10, 25, 50, 100]
        col1, col2 = st.columns([1, 4])
        
        with col1:
            page_size = st.selectbox("Rows per page:", page_size_options, index=1)
        
        with col2:
            st.write("")  # Empty space for layout
        
        # Calculate number of pages
        n_pages = max(1, (row_count - 1) // page_size + 1)
        
        # Add page navigation if needed
        if n_pages > 1:
            page_col1, page_col2, page_col3 = st.columns([1, 3, 1])
            
            with page_col1:
                st.write("")  # Empty space for layout
            
            with page_col2:
                page_number = st.slider("Page", 1, n_pages, 1)
            
            with page_col3:
                st.write("")  # Empty space for layout
                
            # Calculate start and end indices for current page
            start_idx = (page_number - 1) * page_size
            end_idx = min(start_idx + page_size, row_count)
            
            # Get data for current page
            page_data = display_data.iloc[start_idx:end_idx]
        else:
            page_data = display_data
        
        try:
            # Display the table - use 'unsafe_allow_html' for better compatibility
            st.dataframe(
                page_data,
                use_container_width=True,
                height=min(600, 35 + 35 * len(page_data)),  # Dynamic height based on row count
                hide_index=True
            )
        except Exception as e:
            st.error(f"Error displaying data table: {str(e)}")
            st.write("Trying alternative display method...")
            
            # Fallback display method if the main one fails
            st.table(page_data.head(min(len(page_data), page_size)))
            st.warning("Limited display due to data type conversion issues. Export for full view.")
        
        # Export options
        export_col1, export_col2 = st.columns([1, 4])
        
        with export_col1:
            export_format = st.selectbox("Export format:", ["CSV", "Excel", "JSON"])
        
        with export_col2:
            if st.button("Export Selected Data"):
                if export_format == "CSV":
                    export_data = display_data.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=export_data,
                        file_name="underwriting_data.csv",
                        mime="text/csv"
                    )
                elif export_format == "Excel":
                    # Ensure io is imported
                    import io
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        display_data.to_excel(writer, sheet_name='Underwriting Data', index=False)
                    st.download_button(
                        label="Download Excel",
                        data=output.getvalue(),
                        file_name="underwriting_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                elif export_format == "JSON":
                    export_data = display_data.to_json(orient="records")
                    st.download_button(
                        label="Download JSON",
                        data=export_data,
                        file_name="underwriting_data.json",
                        mime="application/json"
                    )
    else:
        st.info("No data available to display. Try adjusting your filters or search criteria.")