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

def render_geographic_analysis(data):
    """
    Render comprehensive geographic analysis of real estate deals.
    
    Args:
        data: DataFrame containing deal data
    """
    st.subheader("Geographic Distribution Analysis")
    
    # Check if we have geographic data
    state_col = None
    city_col = None
    lat_col = None
    lng_col = None
    
    # Find relevant geographic columns
    for col in data.columns:
        col_lower = str(col).lower()
        if 'state' in col_lower and 'comp' not in col_lower:
            state_col = col
        if 'city' in col_lower and 'comp' not in col_lower:
            city_col = col
        if ('lat' in col_lower) and ('comp' not in col_lower):
            lat_col = col
        if (('lon' in col_lower) or ('lng' in col_lower)) and ('comp' not in col_lower):
            lng_col = col
    
    # Check for performance metrics
    cap_rate_col = None
    irr_col = None
    price_col = None
    
    for col in data.columns:
        col_lower = str(col).lower()
        if 'cap' in col_lower and 'rate' in col_lower:
            cap_rate_col = col
        if 'irr' in col_lower:
            irr_col = col
        if 'price' in col_lower or 'value' in col_lower:
            price_col = col
    
    if not any([state_col, city_col, lat_col, lng_col]):
        st.warning("Geographic information not available in the data.")
        return
    
    # Create tabs for different geographic analyses
    tabs = []
    tab_names = []
    
    # State Analysis tab
    if state_col:
        tab_names.append("State Analysis")
        tabs.append(lambda: render_state_analysis(data, state_col, cap_rate_col, irr_col, price_col))
    
    # City Analysis tab
    if city_col:
        tab_names.append("City Analysis")
        tabs.append(lambda: render_city_analysis(data, city_col, cap_rate_col, irr_col, price_col))
    
    # Heat Map tab (if we have lat/lng)
    if lat_col and lng_col:
        tab_names.append("Deal Concentration")
        tabs.append(lambda: render_deal_heatmap(data, lat_col, lng_col, city_col, state_col))
    
    # Market Comparison tab
    if (city_col or state_col) and (cap_rate_col or irr_col or price_col):
        tab_names.append("Market Comparison")
        tabs.append(lambda: render_market_comparison(data, city_col, state_col, cap_rate_col, irr_col, price_col))
    
    # Create the tabs
    if tab_names:
        tab_objects = st.tabs(tab_names)
        
        for i, tab_func in enumerate(tabs):
            with tab_objects[i]:
                tab_func()
    else:
        st.info("Insufficient geographic data for analysis.")

def render_state_analysis(data, state_col, cap_rate_col=None, irr_col=None, price_col=None):
    """
    Render state-level analysis with interactive map and metrics.
    
    Args:
        data: DataFrame containing deal data
        state_col: Column name containing state information
        cap_rate_col: Column name for cap rate (optional)
        irr_col: Column name for IRR (optional)
        price_col: Column name for property price/value (optional)
    """
    # Count deals by state
    state_counts = data[state_col].value_counts().reset_index()
    state_counts.columns = ['State', 'Count']
    
    if len(state_counts) == 0:
        st.info("No state data available for analysis.")
        return
    
    # Calculate performance metrics by state if available
    metrics_available = []
    
    if cap_rate_col:
        state_cap_rates = data.groupby(state_col)[cap_rate_col].mean().reset_index()
        state_cap_rates.columns = ['State', 'Avg Cap Rate']
        metrics_available.append(('Avg Cap Rate', 'Avg_Cap_Rate'))
    else:
        state_cap_rates = None
    
    if irr_col:
        state_irr = data.groupby(state_col)[irr_col].mean().reset_index()
        state_irr.columns = ['State', 'Avg IRR']
        metrics_available.append(('Avg IRR', 'Avg_IRR'))
    else:
        state_irr = None
    
    if price_col:
        state_prices = data.groupby(state_col)[price_col].mean().reset_index()
        state_prices.columns = ['State', 'Avg Deal Size']
        metrics_available.append(('Avg Deal Size', 'Avg_Deal_Size'))
    else:
        state_prices = None
    
    # Create selectable metrics for the map
    metric_options = ['Deal Count'] + [m[0] for m in metrics_available]
    selected_metric = st.selectbox("Select Metric for Map", options=metric_options)
    
    # Create the map based on selected metric
    if selected_metric == 'Deal Count':
        map_data = state_counts
        map_column = 'Count'
        color_scale = 'Blues'
        hover_template = '<b>%{location}</b><br>Deals: %{z}<extra></extra>'
    elif selected_metric == 'Avg Cap Rate' and cap_rate_col:
        map_data = state_cap_rates
        map_column = 'Avg Cap Rate'
        color_scale = 'RdYlGn_r'  # Lower cap rates are generally better (green)
        hover_template = '<b>%{location}</b><br>Cap Rate: %{z:.2f}%<extra></extra>'
    elif selected_metric == 'Avg IRR' and irr_col:
        map_data = state_irr
        map_column = 'Avg IRR'
        color_scale = 'RdYlGn'  # Higher IRR is better (green)
        hover_template = '<b>%{location}</b><br>IRR: %{z:.2f}%<extra></extra>'
    elif selected_metric == 'Avg Deal Size' and price_col:
        map_data = state_prices
        map_column = 'Avg Deal Size'
        color_scale = 'Viridis'
        hover_template = '<b>%{location}</b><br>Avg Deal Size: $%{z:,.0f}<extra></extra>'
    else:
        map_data = state_counts
        map_column = 'Count'
        color_scale = 'Blues'
        hover_template = '<b>%{location}</b><br>Deals: %{z}<extra></extra>'
    
    # Create the choropleth map
    fig = px.choropleth(
        map_data,
        locations='State',
        locationmode="USA-states",
        color=map_column,
        scope="usa",
        color_continuous_scale=color_scale,
        title=f"State Analysis by {selected_metric}"
    )
    
    fig.update_layout(
        geo=dict(
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
        ),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show data table with multiple metrics
    if len(metrics_available) > 0:
        st.subheader("State Performance Comparison")
        
        # Merge all available metrics
        comparison_data = state_counts.copy()
        
        if state_cap_rates is not None:
            comparison_data = pd.merge(comparison_data, state_cap_rates, on='State', how='left')
        
        if state_irr is not None:
            comparison_data = pd.merge(comparison_data, state_irr, on='State', how='left')
        
        if state_prices is not None:
            comparison_data = pd.merge(comparison_data, state_prices, on='State', how='left')
        
        # Format numeric columns
        for col in comparison_data.columns:
            if 'Cap Rate' in col or 'IRR' in col:
                comparison_data[col] = comparison_data[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
            elif 'Deal Size' in col:
                comparison_data[col] = comparison_data[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
        
        # Sort by count
        comparison_data = comparison_data.sort_values('Count', ascending=False)
        
        # Show the table
        st.dataframe(
            comparison_data,
            use_container_width=True,
            hide_index=True
        )

def render_city_analysis(data, city_col, cap_rate_col=None, irr_col=None, price_col=None):
    """
    Render city-level analysis with visualizations and metrics.
    
    Args:
        data: DataFrame containing deal data
        city_col: Column name containing city information
        cap_rate_col: Column name for cap rate (optional)
        irr_col: Column name for IRR (optional)
        price_col: Column name for property price/value (optional)
    """
    # Count deals by city
    city_counts = data[city_col].value_counts().reset_index()
    city_counts.columns = ['City', 'Count']
    
    if len(city_counts) == 0:
        st.info("No city data available for analysis.")
        return
    
    # Calculate performance metrics by city if available
    metrics_available = []
    
    if cap_rate_col:
        city_cap_rates = data.groupby(city_col)[cap_rate_col].mean().reset_index()
        city_cap_rates.columns = ['City', 'Avg Cap Rate']
        metrics_available.append(('Avg Cap Rate', 'Avg_Cap_Rate'))
    else:
        city_cap_rates = None
    
    if irr_col:
        city_irr = data.groupby(city_col)[irr_col].mean().reset_index()
        city_irr.columns = ['City', 'Avg IRR']
        metrics_available.append(('Avg IRR', 'Avg_IRR'))
    else:
        city_irr = None
    
    if price_col:
        city_prices = data.groupby(city_col)[price_col].mean().reset_index()
        city_prices.columns = ['City', 'Avg Deal Size']
        metrics_available.append(('Avg Deal Size', 'Avg_Deal_Size'))
    else:
        city_prices = None
    
    # Create visualization options
    metric_options = ['Deal Count'] + [m[0] for m in metrics_available]
    selected_metric = st.selectbox("Select Metric for Visualization", options=metric_options)
    
    # Limit to top N cities for better visualization
    num_cities = min(15, len(city_counts))
    top_n = st.slider("Number of Top Cities to Display", min_value=5, max_value=30, value=num_cities)
    
    # Create the visualization based on selected metric
    if selected_metric == 'Deal Count':
        viz_data = city_counts.sort_values('Count', ascending=False).head(top_n)
        y_column = 'City'
        x_column = 'Count'
        color_column = 'Count'
        title = f"Top {top_n} Cities by Deal Count"
        color_scale = 'Blues'
    elif selected_metric == 'Avg Cap Rate' and cap_rate_col:
        # Join count data with cap rate data
        viz_data = pd.merge(city_counts, city_cap_rates, on='City', how='inner')
        viz_data = viz_data.sort_values('Count', ascending=False).head(top_n)
        y_column = 'City'
        x_column = 'Avg Cap Rate'
        color_column = 'Avg Cap Rate'
        title = f"Average Cap Rate by City (Top {top_n} Cities by Deal Count)"
        color_scale = 'RdYlGn_r'  # Lower cap rates are generally better (green)
    elif selected_metric == 'Avg IRR' and irr_col:
        # Join count data with IRR data
        viz_data = pd.merge(city_counts, city_irr, on='City', how='inner')
        viz_data = viz_data.sort_values('Count', ascending=False).head(top_n)
        y_column = 'City'
        x_column = 'Avg IRR'
        color_column = 'Avg IRR'
        title = f"Average IRR by City (Top {top_n} Cities by Deal Count)"
        color_scale = 'RdYlGn'  # Higher IRR is better (green)
    elif selected_metric == 'Avg Deal Size' and price_col:
        # Join count data with price data
        viz_data = pd.merge(city_counts, city_prices, on='City', how='inner')
        viz_data = viz_data.sort_values('Count', ascending=False).head(top_n)
        y_column = 'City'
        x_column = 'Avg Deal Size'
        color_column = 'Avg Deal Size'
        title = f"Average Deal Size by City (Top {top_n} Cities by Deal Count)"
        color_scale = 'Viridis'
    else:
        viz_data = city_counts.sort_values('Count', ascending=False).head(top_n)
        y_column = 'City'
        x_column = 'Count'
        color_column = 'Count'
        title = f"Top {top_n} Cities by Deal Count"
        color_scale = 'Blues'
    
    # Create horizontal bar chart
    fig = px.bar(
        viz_data,
        y=y_column,
        x=x_column,
        color=color_column,
        orientation='h',
        color_continuous_scale=color_scale,
        title=title,
        height=600
    )
    
    fig.update_layout(
        yaxis=dict(autorange="reversed"),  # Show top values at the top
        xaxis_title=selected_metric,
        yaxis_title="City",
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show data table with all metrics for top cities
    if len(metrics_available) > 0:
        st.subheader("City Performance Comparison")
        
        # Merge all available metrics
        comparison_data = city_counts.copy()
        
        if city_cap_rates is not None:
            comparison_data = pd.merge(comparison_data, city_cap_rates, on='City', how='left')
        
        if city_irr is not None:
            comparison_data = pd.merge(comparison_data, city_irr, on='City', how='left')
        
        if city_prices is not None:
            comparison_data = pd.merge(comparison_data, city_prices, on='City', how='left')
        
        # Format numeric columns
        for col in comparison_data.columns:
            if 'Cap Rate' in col or 'IRR' in col:
                comparison_data[col] = comparison_data[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
            elif 'Deal Size' in col:
                comparison_data[col] = comparison_data[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
        
        # Sort by count and limit to top N
        comparison_data = comparison_data.sort_values('Count', ascending=False).head(top_n)
        
        # Show the table
        st.dataframe(
            comparison_data,
            use_container_width=True,
            hide_index=True
        )

def render_deal_heatmap(data, lat_col, lng_col, city_col=None, state_col=None):
    """
    Render a heatmap showing deal concentration.
    
    Args:
        data: DataFrame containing deal data
        lat_col: Column name for latitude
        lng_col: Column name for longitude
        city_col: Column name for city (optional, for labeling)
        state_col: Column name for state (optional, for labeling)
    """
    st.subheader("Deal Concentration Heatmap")
    
    # Convert coordinates to numeric values
    map_data = data.copy()
    map_data[lat_col] = pd.to_numeric(map_data[lat_col], errors='coerce')
    map_data[lng_col] = pd.to_numeric(map_data[lng_col], errors='coerce')
    
    # Drop rows with invalid coordinates
    map_data = map_data.dropna(subset=[lat_col, lng_col])
    map_data = map_data[(map_data[lat_col] != 0) & (map_data[lng_col] != 0)]
    map_data = map_data[(map_data[lat_col] >= -90) & (map_data[lat_col] <= 90) &
                         (map_data[lng_col] >= -180) & (map_data[lng_col] <= 180)]
    
    if len(map_data) == 0:
        st.warning("No valid coordinate data available for heatmap.")
        return
    
    # Add color-coding by deal stage if available
    stage_col = None
    for col in map_data.columns:
        if 'stage' in str(col).lower():
            stage_col = col
            break
    
    # Create map center based on average coordinates
    center_lat = map_data[lat_col].mean()
    center_lng = map_data[lng_col].mean()
    
    # Create map
    st.write(f"Showing concentration of {len(map_data)} properties")
    
    # Create the map using Plotly
    fig = px.density_mapbox(
        map_data, 
        lat=lat_col, 
        lon=lng_col, 
        radius=10,
        center=dict(lat=center_lat, lon=center_lng), 
        zoom=4,
        mapbox_style="open-street-map",
        title="Property Concentration Heat Map"
    )
    
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Also show a scatter map with deal points
    if stage_col:
        # Create color mapping for deal stages
        stage_colors = {
            "0) Dead Deals": "gray",
            "1) Initial UW and Review": "blue",
            "2) Active UW and Review": "orange", 
            "3) Deals Under Contract": "purple",
            "4) Closed Deals": "green",
            "5) Realized Deals": "red"
        }
        
        # Create hover text
        hover_text = []
        for _, row in map_data.iterrows():
            text = []
            if city_col and city_col in row:
                text.append(f"City: {row[city_col]}")
            if state_col and state_col in row:
                text.append(f"State: {row[state_col]}")
            if stage_col and stage_col in row:
                text.append(f"Stage: {row[stage_col]}")
            hover_text.append("<br>".join(text))
        
        # Create the map using Plotly
        fig = px.scatter_mapbox(
            map_data, 
            lat=lat_col, 
            lon=lng_col, 
            color=stage_col if stage_col else None,
            hover_name=city_col if city_col else None,
            hover_data=[state_col] if state_col else None,
            color_discrete_map=stage_colors if stage_col else None,
            center=dict(lat=center_lat, lon=center_lng), 
            zoom=4,
            mapbox_style="open-street-map",
            title="Individual Property Locations"
        )
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

def render_market_comparison(data, city_col=None, state_col=None, cap_rate_col=None, irr_col=None, price_col=None):
    """
    Render market comparison analysis.
    
    Args:
        data: DataFrame containing deal data
        city_col: Column name for city
        state_col: Column name for state
        cap_rate_col: Column name for cap rate
        irr_col: Column name for IRR
        price_col: Column name for property price/value
    """
    st.subheader("Market Performance Comparison")
    
    # Check what we can compare
    location_options = []
    if city_col:
        location_options.append(("City", city_col))
    if state_col:
        location_options.append(("State", state_col))
    
    metric_options = []
    if cap_rate_col:
        metric_options.append(("Cap Rate", cap_rate_col))
    if irr_col:
        metric_options.append(("IRR", irr_col))
    if price_col:
        metric_options.append(("Deal Size", price_col))
    
    if not location_options or not metric_options:
        st.warning("Insufficient data for market comparison.")
        return
    
    # Create interface for comparison
    col1, col2 = st.columns(2)
    
    with col1:
        location_type = st.selectbox(
            "Group By",
            options=[opt[0] for opt in location_options],
            index=0
        )
    
    with col2:
        metric_type = st.selectbox(
            "Compare By",
            options=[opt[0] for opt in metric_options],
            index=0
        )
    
    # Get the actual column names
    location_col = next((opt[1] for opt in location_options if opt[0] == location_type), None)
    metric_col = next((opt[1] for opt in metric_options if opt[0] == metric_type), None)
    
    if not location_col or not metric_col:
        st.error("Could not determine columns for comparison.")
        return
    
    # Convert metric to numeric
    data_for_viz = data.copy()
    data_for_viz[metric_col] = pd.to_numeric(data_for_viz[metric_col], errors='coerce')
    
    # Group by location and calculate metrics
    grouped_data = data_for_viz.groupby(location_col)[metric_col].agg(['mean', 'median', 'std', 'count']).reset_index()
    grouped_data.columns = [location_type, f'Avg {metric_type}', f'Median {metric_type}', f'StdDev {metric_type}', 'Deal Count']
    
    # Filter to only locations with at least 2 deals for more meaningful comparison
    grouped_data = grouped_data[grouped_data['Deal Count'] >= 2].sort_values('Deal Count', ascending=False)
    
    if len(grouped_data) == 0:
        st.warning("No locations with enough deals for meaningful comparison.")
        return
    
    # Limit to top N locations
    max_locations = len(grouped_data)
    num_locations = min(15, max_locations)
    top_n = st.slider(f"Number of Top {location_type}s to Compare", min_value=5, max_value=30, value=num_locations)
    
    comparison_data = grouped_data.head(top_n)
    
    # Visualization options
    viz_options = [f'Avg {metric_type}', f'Median {metric_type}', f'StdDev {metric_type}', 'Deal Count']
    viz_metric = st.radio("Visualization Metric", options=viz_options)
    
    # Create the visualization
    fig = px.bar(
        comparison_data,
        x=location_type,
        y=viz_metric,
        color=viz_metric,
        title=f"{viz_metric} by {location_type}",
        color_continuous_scale='RdYlGn' if metric_type in ['IRR'] else 'RdYlGn_r' if metric_type in ['Cap Rate'] else 'Viridis'
    )
    
    fig.update_layout(
        xaxis_title=location_type,
        yaxis_title=viz_metric,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show comparative statistics
    st.subheader(f"{location_type} Performance Statistics")
    
    # Add portfolio average for reference
    portfolio_avg = data_for_viz[metric_col].mean()
    portfolio_median = data_for_viz[metric_col].median()
    
    metric_cols = st.columns(2)
    
    with metric_cols[0]:
        st.metric("Portfolio Average", f"{portfolio_avg:.2f}%" if metric_type in ['Cap Rate', 'IRR'] else f"${portfolio_avg:,.0f}")
    
    with metric_cols[1]:
        st.metric("Portfolio Median", f"{portfolio_median:.2f}%" if metric_type in ['Cap Rate', 'IRR'] else f"${portfolio_median:,.0f}")
    
    # Format the table
    display_data = comparison_data.copy()
    
    # Format numeric columns
    for col in display_data.columns:
        if 'Cap Rate' in col or 'IRR' in col:
            display_data[col] = display_data[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
        elif 'Deal Size' in col:
            display_data[col] = display_data[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
        elif 'StdDev' in col:
            display_data[col] = display_data[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
    
    # Show the comparison table
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )
    
    # Create an above/below average visualization
    st.subheader(f"{location_type}s Relative to Portfolio Average")
    
    # Calculate percentage difference from portfolio average
    comparison_data['Difference'] = (comparison_data[f'Avg {metric_type}'] - portfolio_avg) / portfolio_avg * 100
    
    # Determine if higher is better
    higher_is_better = metric_type == 'IRR'
    
    # Create color mapping
    comparison_data['Color'] = comparison_data['Difference'].apply(
        lambda x: 'green' if (x > 0 and higher_is_better) or (x < 0 and not higher_is_better) else 'red'
    )
    
    # Create the comparison chart
    fig = px.bar(
        comparison_data,
        x=location_type,
        y='Difference',
        color='Color',
        color_discrete_map={'green': 'green', 'red': 'red'},
        title=f"{location_type} Performance Relative to Portfolio Average ({metric_type})",
    )
    
    fig.update_layout(
        xaxis_title=location_type,
        yaxis_title=f"% Difference from Portfolio Average",
        showlegend=False,
        height=500
    )
    
    # Add a zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig, use_container_width=True)


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
        