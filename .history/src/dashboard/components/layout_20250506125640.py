"""
Dashboard Layout Components

This module provides responsive layout components for the dashboard.
"""

import streamlit as st

def responsive_row(*args, columns=None, mobile_stacking=True):
    """
    Create a responsive row layout that adapts to screen size.
    
    Args:
        *args: Components to place in the row
        columns: Optional list of column widths (must sum to 12)
        mobile_stacking: Whether to stack columns on mobile
        
    Returns:
        The created columns with components inside
    """
    # Default to equal width columns if not specified
    if columns is None:
        columns = [1] * len(args)
    
    # Create the columns
    cols = st.columns(columns)
    
    # Add components to columns
    for i, component in enumerate(args):
        if i < len(cols):
            with cols[i]:
                # Each component is a function that takes the column as argument
                if callable(component):
                    component()
                else:
                    st.write(component)
    
    return cols

def adaptive_container(content_function, wide_layout=True, mobile_padding=True):
    """
    Create a container that adapts its layout based on screen size.
    
    Args:
        content_function: Function containing the content to display
        wide_layout: Whether to use full width on desktop
        mobile_padding: Whether to add extra padding on mobile
    """
    # Add mobile-specific CSS class
    mobile_class = "mobile-container" if mobile_padding else ""
    
    # Create the container
    with st.container():
        # Add a div with mobile-specific class for CSS targeting
        st.markdown(f'<div class="{mobile_class}">', unsafe_allow_html=True)
        
        # Render the content
        content_function()
        
        # Close the div
        st.markdown('</div>', unsafe_allow_html=True)

def mobile_friendly_tabs(tabs_dict):
    """
    Create tabs that are optimized for both desktop and mobile viewing.
    
    Args:
        tabs_dict: Dictionary of tab labels to content functions
        
    Returns:
        The created tabs
    """
    # Create the tabs
    tab_objects = st.tabs(list(tabs_dict.keys()))
    
    # Add content to each tab
    for i, (label, content_function) in enumerate(tabs_dict.items()):
        with tab_objects[i]:
            if callable(content_function):
                content_function()
            else:
                st.write(content_function)
    
    return tab_objects

def collapsible_section(title, content_function, expanded=False, mobile_always_collapsed=True):
    """
    Create a section that can be collapsed, with mobile-specific behavior.
    
    Args:
        title: The section title
        content_function: Function containing the content to display
        expanded: Whether the section is expanded by default on desktop
        mobile_always_collapsed: Whether to always collapse on mobile
    """
    # Create the expander
    with st.expander(title, expanded=expanded):
        # Render the content
        content_function()