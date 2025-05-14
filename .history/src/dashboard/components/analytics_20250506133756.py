"""
Analytics Components for Underwriting Dashboard

This module provides advanced data visualization components for analyzing real estate deals.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

def render_deal_stage_distribution(data):
    """
    Render a visualization of deal distribution across stages.
    
    Args:
        data: DataFrame containing deal data
    """
    if 'Deal_Stage_Subdirectory_Name' not in data.columns:
        st.warning("Deal stage information not available in the data.")
        return
    
    # Count deals by stage
    stage_counts = data['Deal_Stage_Subdirectory_Name'].value_counts().reset_index()
    stage_counts.columns = ['Deal Stage', 'Count']
    
    # Order stages logically
    stage_order = [
        "0) Dead Deals",
        "1) Initial UW and Review", 
        "2) Active UW and Review",
        "3) Deals Under Contract",
        "4) Closed Deals",
        "5) Realized Deals"
    ]
    
    # Filter to only include stages that exist in the data
    stage_order = [stage for stage in stage_order if stage in stage_counts['Deal Stage'].values]
    
    # Sort by the defined order
    if stage_order:
        stage_counts['Order'] = stage_counts['Deal Stage'].apply(
            lambda x: stage_order.index(x) if x in stage_order else 999)
        stage_counts = stage_counts.sort_values('Order').drop(columns=['Order'])
    
    # Create the visualization
    st.subheader("Deal Stage Distribution")
    
    # Create tabs for different visualization types
    tab1, tab2 = st.tabs(["Bar Chart", "Pie Chart"])
    
    with tab1:
        fig = px.bar(
            stage_counts, 
            x='Deal Stage', 
            y='Count',
            text='Count',
            color='Deal Stage',
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Number of Deals by Stage"
        )
        
        fig.update_layout(
            xaxis_title="Deal Stage",
            yaxis_title="Number of Deals",
            legend_title="Deal Stage",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insightful metrics
        cols = st.columns(3)
        
        with cols[0]:
            active_deals = sum(stage_counts[stage_counts['Deal Stage'].isin([
                "1) Initial UW and Review", 
                "2) Active UW and Review",
                "3) Deals Under Contract"
            ])]['Count'])
            
            st.metric("Active Pipeline", active_deals)
            
        with cols[1]:
            closed_deals = sum(stage_counts[stage_counts['Deal Stage'].isin([
                "4) Closed Deals",
                "5) Realized Deals"
            ])]['Count'])
            
            st.metric("Closed/Realized Deals", closed_deals)
            
        with cols[2]:
            if "0) Dead Deals" in stage_counts['Deal Stage'].values:
                dead_deals = stage_counts[stage_counts['Deal Stage'] == "0) Dead Deals"]['Count'].iloc[0]
                
                # Calculate dead deal ratio if we have any pipeline deals
                if active_deals > 0:
                    dead_ratio = dead_deals / (dead_deals + active_deals)
                    st.metric("Dead Deal Ratio", f"{dead_ratio:.1%}")
                else:
                    st.metric("Dead Deals", dead_deals)
            else:
                st.metric("Dead Deals", 0)
    
    with tab2:
        fig = px.pie(
            stage_counts, 
            values='Count', 
            names='Deal Stage',
            color='Deal Stage',
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Deal Stage Distribution"
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hole=0.4
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_geographic_distribution(data):
    """
    Render visualizations of geographic distribution of deals.
    
    Args:
        data: DataFrame containing deal data
    """
    # Check if we have geographic data
    state_col = None
    city_col = None
    
    for col in data.columns:
        col_lower = str(col).lower()
        if 'state' in col_lower and 'comp' not in col_lower:
            state_col = col
        if 'city' in col_lower and 'comp' not in col_lower:
            city_col = col
    
    if not state_col and not city_col:
        st.warning("Geographic information not available in the data.")
        return
    
    st.subheader("Geographic Distribution")
    
    # Create tabs for different geographic analyses
    tab1, tab2 = st.tabs(["By State", "By City"])
    
    with tab1:
        if state_col:
            # Count deals by state
            state_counts = data[state_col].value_counts().reset_index()
            state_counts.columns = ['State', 'Count']
            
            if len(state_counts) > 0:
                # Create the visualization
                fig = px.choropleth(
                    state_counts,
                    locations='State',
                    locationmode="USA-states",
                    color='Count',
                    scope="usa",
                    color_continuous_scale=px.colors.sequential.Blues,
                    title="Deal Distribution by State"
                )
                
                fig.update_layout(
                    geo=dict(
                        showlakes=True,
                        lakecolor='rgb(255, 255, 255)',
                    ),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show top states
                st.write("Top States by Deal Count:")
                st.dataframe(
                    state_counts.head(5),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No state data available for visualization.")
        else:
            st.info("State information not available in the data.")
    
    with tab2:
        if city_col:
            # Count deals by city
            city_counts = data[city_col].value_counts().reset_index()
            city_counts.columns = ['City', 'Count']
            city_counts = city_counts.sort_values('Count', ascending=False).head(15)
            
            if len(city_counts) > 0:
                # Create the visualization
                fig = px.bar(
                    city_counts,
                    x='Count',
                    y='City',
                    orientation='h',
                    color='Count',
                    color_continuous_scale=px.colors.sequential.Blues,
                    title="Top Cities by Deal Count"
                )
                
                fig.update_layout(
                    xaxis_title="Number of Deals",
                    yaxis_title="City",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No city data available for visualization.")
        else:
            st.info("City information not available in the data.")

def render_performance_metrics(data):
    """
    Render visualizations of key performance metrics.
    
    Args:
        data: DataFrame containing deal data
    """
    st.subheader("Performance Metrics Analysis")
    
    # Find relevant performance columns
    performance_cols = {}
    
    for metric_type, keywords in {
        'cap_rate': ['cap', 'rate'],
        'irr': ['irr', 'return'],
        'coc': ['cash', 'coc', 'yield'],
        'ltv': ['ltv', 'loan to value', 'leverage']
    }.items():
        for col in data.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in keywords) and 'comp' not in col_lower:
                performance_cols[metric_type] = col
                break
    
    if not performance_cols:
        st.warning("Performance metric data not available.")
        return
    
    # Create visualizations for available metrics
    tab_names = []
    tab_functions = []
    
    # Cap Rate Analysis
    if 'cap_rate' in performance_cols:
        tab_names.append("Cap Rate")
        tab_functions.append(lambda: render_cap_rate_analysis(data, performance_cols['cap_rate']))
    
    # IRR Analysis
    if 'irr' in performance_cols:
        tab_names.append("IRR")
        tab_functions.append(lambda: render_irr_analysis(data, performance_cols['irr']))
    
    # Other metrics can be added similarly
    
    if tab_names:
        tabs = st.tabs(tab_names)
        
        for i, tab_func in enumerate(tab_functions):
            with tabs[i]:
                tab_func()
    else:
        st.info("No performance metrics found for visualization.")

def render_cap_rate_analysis(data, cap_rate_col):
    """
    Render cap rate analysis visualizations.
    
    Args:
        data: DataFrame containing deal data
        cap_rate_col: Name of the cap rate column
    """
    # Convert to numeric, coercing errors
    cap_rates = pd.to_numeric(data[cap_rate_col], errors='coerce')
    
    # Remove outliers for better visualization (optional)
    q1 = cap_rates.quantile(0.05)
    q3 = cap_rates.quantile(0.95)
    iqr = q3 - q1
    cap_rates_filtered = cap_rates[(cap_rates >= q1 - 1.5 * iqr) & (cap_rates <= q3 + 1.5 * iqr)]
    
    # Create the visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        fig = px.histogram(
            cap_rates_filtered,
            x=cap_rates_filtered,
            nbins=20,
            color_discrete_sequence=['#3366CC'],
            title="Cap Rate Distribution"
        )
        
        fig.update_layout(
            xaxis_title="Cap Rate (%)",
            yaxis_title="Number of Deals",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Box plot
        fig = px.box(
            cap_rates_filtered,
            y=cap_rates_filtered,
            color_discrete_sequence=['#3366CC'],
            title="Cap Rate Statistical Distribution"
        )
        
        fig.update_layout(
            yaxis_title="Cap Rate (%)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    st.subheader("Cap Rate Statistics")
    
    metric_cols = st.columns(5)
    with metric_cols[0]:
        st.metric("Average", f"{cap_rates.mean():.2f}%")
    with metric_cols[1]:
        st.metric("Median", f"{cap_rates.median():.2f}%")
    with metric_cols[2]:
        st.metric("Min", f"{cap_rates.min():.2f}%")
    with metric_cols[3]:
        st.metric("Max", f"{cap_rates.max():.2f}%")
    with metric_cols[4]:
        st.metric("StdDev", f"{cap_rates.std():.2f}%")

def render_irr_analysis(data, irr_col):
    """
    Render IRR analysis visualizations.
    
    Args:
        data: DataFrame containing deal data
        irr_col: Name of the IRR column
    """
    # Convert to numeric, coercing errors
    irr_values = pd.to_numeric(data[irr_col], errors='coerce')
    
    # Remove outliers for better visualization (optional)
    q1 = irr_values.quantile(0.05)
    q3 = irr_values.quantile(0.95)
    iqr = q3 - q1
    irr_filtered = irr_values[(irr_values >= q1 - 1.5 * iqr) & (irr_values <= q3 + 1.5 * iqr)]
    
    # Create the visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        fig = px.histogram(
            irr_filtered,
            x=irr_filtered,
            nbins=20,
            color_discrete_sequence=['#3366CC'],
            title="IRR Distribution"
        )
        
        fig.update_layout(
            xaxis_title="IRR (%)",
            yaxis_title="Number of Deals",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Create IRR target zones
        fig = go.Figure()
        
        # Add histogram
        fig.add_trace(go.Histogram(
            x=irr_filtered,
            opacity=0.7,
            name="IRR",
            marker_color='#3366CC'
        ))
        
        # Add vertical lines for target zones
        fig.add_vline(x=15, line_width=2, line_dash="dash", line_color="red")
        fig.add_vline(x=20, line_width=2, line_dash="dash", line_color="green")
        
        # Add annotations
        fig.add_annotation(
            x=12.5, y=0.85, xref="x", yref="paper",
            text="Below Target",
            showarrow=False, 
            font=dict(color="red")
        )
        
        fig.add_annotation(
            x=17.5, y=0.85, xref="x", yref="paper",
            text="Target Zone",
            showarrow=False, 
            font=dict(color="green")
        )
        
        fig.add_annotation(
            x=25, y=0.85, xref="x", yref="paper",
            text="Exceeds Target",
            showarrow=False, 
            font=dict(color="blue")
        )
        
        fig.update_layout(
            title="IRR Performance vs Targets",
            xaxis_title="IRR (%)",
            yaxis_title="Number of Deals",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    st.subheader("IRR Statistics")
    
    metric_cols = st.columns(5)
    with metric_cols[0]:
        st.metric("Average", f"{irr_values.mean():.2f}%")
    with metric_cols[1]:
        st.metric("Median", f"{irr_values.median():.2f}%")
    with metric_cols[2]:
        st.metric("Min", f"{irr_values.min():.2f}%")
    with metric_cols[3]:
        st.metric("Max", f"{irr_values.max():.2f}%")
    with metric_cols[4]:
        st.metric("StdDev", f"{irr_values.std():.2f}%")
    
    # Add IRR target achievement
    target_irr = 15.0
    achieved = sum(irr_values >= target_irr) / len(irr_values)
    
    st.metric("Deals Meeting IRR Target", f"{achieved:.1%}")

def render_deal_timeline(data):
    """
    Render timeline visualization of deals.
    
    Args:
        data: DataFrame containing deal data
    """
    st.subheader("Deal Timeline Analysis")
    
    # Check for date column
    date_cols = []
    for col in data.columns:
        col_lower = str(col).lower()
        if 'date' in col_lower or 'time' in col_lower:
            date_cols.append(col)
    
    if not date_cols:
        st.warning("Date information not available for timeline analysis.")
        return
    
    # Let user select date column
    date_col = st.selectbox("Select date column for timeline:", date_cols)
    
    if date_col:
        # Convert to datetime
        try:
            timeline_data = data.copy()
            timeline_data[date_col] = pd.to_datetime(timeline_data[date_col], errors='coerce')
            timeline_data = timeline_data.dropna(subset=[date_col])
            
            # Check if we have a property name column
            property_col = None
            for col in timeline_data.columns:
                col_lower = str(col).lower()
                if ('name' in col_lower or 'property' in col_lower) and 'comp' not in col_lower:
                    property_col = col
                    break
            
            # Check if we have a deal stage column
            stage_col = 'Deal_Stage_Subdirectory_Name' if 'Deal_Stage_Subdirectory_Name' in timeline_data.columns else None
            
            if timeline_data.empty:
                st.warning("No valid date data available after conversion.")
                return
            
            # Sort by date
            timeline_data = timeline_data.sort_values(date_col)
            
            # Group by month/year
            timeline_data['Month_Year'] = timeline_data[date_col].dt.strftime('%Y-%m')
            monthly_counts = timeline_data.groupby('Month_Year').size().reset_index(name='Count')
            
            # Ensure chronological order
            monthly_counts['Month_Year_Dt'] = pd.to_datetime(monthly_counts['Month_Year'] + '-01')
            monthly_counts = monthly_counts.sort_values('Month_Year_Dt')
            
            # Create timeline visualization
            fig = px.bar(
                monthly_counts,
                x='Month_Year',
                y='Count',
                title="Deal Activity Over Time",
                color_discrete_sequence=['#3366CC']
            )
            
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Number of Deals",
                xaxis=dict(tickangle=45)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Deal scatter plot
            if property_col and stage_col:
                # Create a timeline scatter plot
                fig = px.scatter(
                    timeline_data,
                    x=date_col,
                    y=property_col,
                    color=stage_col,
                    title="Deal Timeline",
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    hover_data=[property_col, stage_col, date_col]
                )
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Property",
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error creating timeline visualization: {str(e)}")

def render_enhanced_analytics(data):
    """
    Render enhanced analytics dashboard with multiple visualization components.
    
    Args:
        data: DataFrame containing deal data
    """
    if data.empty:
        st.warning("No data available for analytics.")
        return
    
    # Create metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Deals", len(data))
    
    with col2:
        # Count unique cities
        city_col = None
        for col in data.columns:
            if 'city' in str(col).lower() and 'comp' not in str(col).lower():
                city_col = col
                break
        
        if city_col:
            unique_cities = data[city_col].nunique()
            st.metric("Unique Markets", unique_cities)
        else:
            st.metric("Markets", "N/A")
    
    with col3:
        # Get average deal size if available
        price_col = None
        for col in data.columns:
            col_lower = str(col).lower()
            if 'price' in col_lower or 'value' in col_lower or 'cost' in col_lower:
                price_col = col
                break
        
        if price_col:
            avg_price = pd.to_numeric(data[price_col], errors='coerce').mean()
            if not pd.isna(avg_price):
                formatted_price = f"${avg_price:,.0f}"
                st.metric("Avg Deal Size", formatted_price)
            else:
                st.metric("Avg Deal Size", "N/A")
        else:
            st.metric("Avg Deal Size", "N/A")
    
    with col4:
        # Latest activity date
        date_col = None
        for col in data.columns:
            col_lower = str(col).lower()
            if 'date' in col_lower or 'time' in col_lower:
                date_col = col
                break
        
        if date_col:
            try:
                latest_date = pd.to_datetime(data[date_col], errors='coerce').max()
                if not pd.isna(latest_date):
                    st.metric("Latest Activity", latest_date.strftime('%Y-%m-%d'))
                else:
                    st.metric("Latest Activity", "N/A")
            except:
                st.metric("Latest Activity", "N/A")
        else:
            st.metric("Latest Activity", "N/A")
    
    # Add expandable sections for different analytics
    with st.expander("Deal Stage Analysis", expanded=True):
        render_deal_stage_distribution(data)
    
    with st.expander("Geographic Analysis", expanded=False):
        render_geographic_distribution(data)
    
    with st.expander("Performance Metrics", expanded=False):
        render_performance_metrics(data)
    
    with st.expander("Deal Timeline", expanded=False):
        render_deal_timeline(data)