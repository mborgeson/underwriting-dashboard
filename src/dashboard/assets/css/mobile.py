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
        
        .col {
            flex: 1 0 0%;
            padding: 0 0.5rem;
        }
        
        /* Responsive breakpoints */
        @media (max-width: 768px) {
            /* General mobile styling */
            body {
                font-size: 14px; /* Slightly smaller base font on mobile */
            }
            
            .main-header {
                font-size: 1.8rem !important; /* Smaller header on mobile */
                margin-bottom: 0.5rem !important;
            }
            
            .subheader {
                font-size: 1.2rem !important;
                margin-bottom: 0.5rem !important;
            }
            
            /* Make columns stack vertically on mobile */
            .row {
                flex-direction: column;
            }
            
            .col {
                flex: 1 0 100%;
                margin-bottom: 1rem;
            }
            
            /* Adjust metric cards for mobile */
            .metric-card {
                padding: 0.8rem !important;
                margin-bottom: 0.8rem !important;
            }
            
            .metric-value {
                font-size: 1.4rem !important;
            }
            
            /* Make tables more mobile-friendly */
            .dataframe-container {
                overflow-x: auto; /* Enable horizontal scrolling for tables */
                max-width: 100%;
            }
            
            /* Enhance touch targets */
            button, select, .stButton>button, .stSelectbox>div>div>select {
                min-height: 44px !important; /* Minimum touch target size */
                margin-bottom: 0.8rem !important;
            }
            
            /* Improve filter visibility */
            .streamlit-expanderHeader {
                font-size: 1.1rem !important;
                padding: 0.6rem !important;
            }
            
            /* Optimize sliders for touch */
            .stSlider > div > div {
                height: 2.5rem !important;
            }
            
            /* Full-width map on mobile */
            .folium-map {
                width: 100% !important;
                max-width: 100% !important;
            }
        }
        
        /* Small mobile devices */
        @media (max-width: 480px) {
            body {
                font-size: 13px;
            }
            
            .main-header {
                font-size: 1.5rem !important;
            }
            
            /* Further adjustments for very small screens */
            .metric-card {
                padding: 0.6rem !important;
            }
            
            .metric-value {
                font-size: 1.2rem !important;
            }
        }
        
        /* Mobile-specific utility classes */
        .mobile-only {
            display: none;
        }
        
        .desktop-only {
            display: block;
        }
        
        @media (max-width: 768px) {
            .mobile-only {
                display: block;
            }
            
            .desktop-only {
                display: none;
            }
            
            /* Adjust Streamlit-specific elements */
            .stTabs [data-baseweb="tab-panel"] {
                padding-top: 0.5rem !important;
            }
            
            /* Only modify sidebar on actual mobile devices or when we want mobile layout */
            body.mobile-view div[data-testid="stSidebar"] {
                width: 100% !important;
                min-width: 100% !important;
            }
            
            /* Keep sidebar visible on desktop regardless of window size */
            body:not(.mobile-view) div[data-testid="stSidebar"] {
                width: 250px !important;
                min-width: 250px !important;
                display: flex !important;
            }
        }
    </style>
    """
    
    return st.markdown(mobile_css, unsafe_allow_html=True)