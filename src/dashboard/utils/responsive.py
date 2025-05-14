"""
Responsive Utilities

This module provides utilities for responsive design and mobile detection.
"""

# --- Import Fix for Streamlit ---
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ---------------------------


import streamlit as st
import re

def is_mobile_device():
    """
    Detect if the user is on a mobile device based on browser user agent.
    
    Returns:
        Boolean indicating if the user is on a mobile device
    """
    # Try to get the user agent from Streamlit's session state
    if 'device_type' in st.session_state:
        return st.session_state['device_type'] == 'mobile'
    
    # Default to desktop if we can't detect
    return False

def set_device_type():
    """
    Set the device type in session state for responsive design.
    This relies on JavaScript to detect the device type.
    """
    detect_script = """
    <script>
    // Detect if this is a mobile device
    function isMobileDevice() {
        return (window.innerWidth <= 768) || 
               (navigator.userAgent.match(/Android/i) ||
                navigator.userAgent.match(/webOS/i) ||
                navigator.userAgent.match(/iPhone/i) ||
                navigator.userAgent.match(/iPad/i) ||
                navigator.userAgent.match(/iPod/i) ||
                navigator.userAgent.match(/BlackBerry/i) ||
                navigator.userAgent.match(/Windows Phone/i));
    }
    
    // Set a cookie with the device type
    document.cookie = "deviceType=" + (isMobileDevice() ? "mobile" : "desktop") + "; path=/";
    </script>
    """
    
    st.markdown(detect_script, unsafe_allow_html=True)

def get_screen_info():
    """
    Get information about the screen size and device.
    This functionality is limited in Streamlit but can be approximated.
    
    Returns:
        Dictionary with screen information
    """
    info = {
        'is_mobile': is_mobile_device(),
        'browser_width': 'Unknown (detected via session)'
    }
    
    return info

def adapt_component_for_mobile(desktop_component, mobile_component):
    """
    Show different components based on device type.
    
    Args:
        desktop_component: Component to show on desktop
        mobile_component: Component to show on mobile
        
    Returns:
        The appropriate component for the device
    """
    if is_mobile_device():
        return mobile_component
    else:
        return desktop_component

def get_mobile_friendly_columns(num_columns):
    """
    Get a mobile-friendly number of columns.
    
    Args:
        num_columns: Desired number of columns on desktop
        
    Returns:
        Number of columns to use based on device
    """
    if is_mobile_device():
        # On mobile, use fewer columns
        return min(2, num_columns)
    else:
        return num_columns