"""
Fixed analytics components for the dashboard that handle mixed data types

This module provides functions for rendering different analytics visualizations
in the dashboard with improved type handling.
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Helper functions for data conversion and cleaning
def safe_numeric(df: pd.DataFrame, column: str) -> pd.Series:
    """Safely convert a column to numeric, handling errors gracefully."""
    if column not in df.columns:
        return pd.Series([np.nan] * len(df))
    
    try:
        return pd.to_numeric(df[column], errors='coerce')
    except Exception as e:
        logger.warning(f"Error converting {column} to numeric: {str(e)}")
        return pd.Series([np.nan] * len(df))

def find_column_by_type(df: pd.DataFrame, keywords: List[str], numeric: bool = True) -> Optional[str]:
    """Find a column by keywords and optionally ensure it's convertible to numeric."""
    for keyword in keywords:
        matches = [col for col in df.columns if keyword.lower() in col.lower()]
        
        for col in matches:
            if numeric:
                # Try to convert to numeric and check if we have valid values
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                if numeric_series.notna().sum() > 0:
                    return col
            else:
                # For non-numeric columns, just return the first match
                return col
    
    return None

def prepare_data_for_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for analysis by converting columns to appropriate types."""
    if df.empty:
        return df
    
    # Create a copy to avoid modifying the original
    data = df.copy()
    
    # Force date columns to datetime
    date_columns = [col for col in data.columns if 'date' in col.lower()]
    for col in date_columns:
        try:
            data[col] = pd.to_datetime(data[col], errors='coerce')
        except:
            pass
    
    # Find and convert numeric columns that might contain strings
    numeric_keywords = ['price', 'cost', 'rate', 'irr', 'value', 'size', 'amount', 'income']
    for keyword in numeric_keywords:
        cols = [col for col in data.columns if keyword.lower() in col.lower()]
        for col in cols:
            try:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            except:
                pass
    
    return data

# Analytics visualization functions
def render_deal_stage_distribution(data: pd.DataFrame) -> None:
    """Render the deal stage distribution visualization."""
    if data.empty:
        st.warning("No data available for deal stage distribution analysis.")
        return
    
    # Find deal stage column
    stage_col = find_column_by_type(
        data, 
        ['deal stage', 'stage', 'status'], 
        numeric=False
    )
    
    if not stage_col:
        st.warning("Could not find a deal stage column for analysis.")
        return
    
    # Count deals by stage
    try:
        stage_counts = data[stage_col].value_counts().reset_index()
        stage_counts.columns = ['Deal Stage', 'Count']
        
        # Create the visualization
        st.subheader("Deal Distribution by Stage")
        
        # Horizontal bar chart
        fig = px.bar(
            stage_counts,
            y='Deal Stage',
            x='Count',
            orientation='h',
            color='Count',
            color_continuous_scale='Blues',
            labels={'Count': 'Number of Deals'},
            height=400
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Number of Deals",
            yaxis_title="Deal Stage",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show the data table - DON'T USE EXPANDER HERE
        st.subheader("Deal Stage Data Table")
        st.dataframe(stage_counts)
    except Exception as e:
        st.error(f"Error rendering deal stage distribution: {str(e)}")
        logger.error(f"Error rendering deal stage distribution: {str(e)}", exc_info=True)

def render_geographic_analysis(data: pd.DataFrame) -> None:
    """Render geographic analysis visualizations."""
    if data.empty:
        st.warning("No data available for geographic analysis.")
        return
    
    try:
        # Prepare data for analysis
        analysis_data = prepare_data_for_analysis(data)
        
        # Find relevant columns
        state_col = find_column_by_type(analysis_data, ['state', 'province'], numeric=False)
        city_col = find_column_by_type(analysis_data, ['city', 'town', 'municipality'], numeric=False)
        cap_rate_col = find_column_by_type(analysis_data, ['cap rate', 'cap_rate', 'capitalization'])
        irr_col = find_column_by_type(analysis_data, ['irr', 'internal rate', 'return'])
        price_col = find_column_by_type(analysis_data, ['price', 'cost', 'value'])
        
        if not (state_col or city_col):
            st.warning("Could not find geographic columns (state/city) for analysis.")
            return
        
        # Create tabs for different geographic analyses
        geo_tabs = st.tabs(["State Analysis", "City Analysis", "Market Performance"])
        
        # State Analysis tab
        with geo_tabs[0]:
            if state_col:
                render_state_analysis(analysis_data, state_col, cap_rate_col, irr_col, price_col)
            else:
                st.warning("No state column found for state analysis.")
        
        # City Analysis tab
        with geo_tabs[1]:
            if city_col:
                render_city_analysis(analysis_data, city_col, cap_rate_col, irr_col, price_col) 
            else:
                st.warning("No city column found for city analysis.")
        
        # Market Performance tab
        with geo_tabs[2]:
            if state_col or city_col:
                location_col = state_col if state_col else city_col
                render_market_performance(analysis_data, location_col, cap_rate_col, irr_col, price_col)
            else:
                st.warning("No location column found for market performance analysis.")
    except Exception as e:
        st.error(f"Error rendering geographic analysis: {str(e)}")
        logger.error(f"Error rendering geographic analysis: {str(e)}", exc_info=True)

def render_state_analysis(
    data: pd.DataFrame, 
    state_col: str, 
    cap_rate_col: Optional[str], 
    irr_col: Optional[str],
    price_col: Optional[str]
) -> None:
    """Render state-level analysis."""
    try:
        # Count deals by state
        state_counts = data[state_col].value_counts().reset_index()
        state_counts.columns = ['State', 'Count']
        
        # Create metrics by state if available
        metrics = []
        
        if cap_rate_col:
            # Convert to numeric
            data['cap_rate_numeric'] = safe_numeric(data, cap_rate_col)
            
            # Group and calculate mean
            state_cap_rates = (
                data
                .groupby(state_col)['cap_rate_numeric']
                .mean()
                .reset_index()
            )
            state_cap_rates.columns = ['State', 'Avg Cap Rate']
            metrics.append(state_cap_rates)
        
        if irr_col:
            # Convert to numeric
            data['irr_numeric'] = safe_numeric(data, irr_col)
            
            # Group and calculate mean
            state_irrs = (
                data
                .groupby(state_col)['irr_numeric']
                .mean()
                .reset_index()
            )
            state_irrs.columns = ['State', 'Avg IRR']
            metrics.append(state_irrs)
        
        if price_col:
            # Convert to numeric
            data['price_numeric'] = safe_numeric(data, price_col)
            
            # Group and calculate mean
            state_prices = (
                data
                .groupby(state_col)['price_numeric']
                .mean()
                .reset_index()
            )
            state_prices.columns = ['State', 'Avg Price']
            metrics.append(state_prices)
        
        # Combine all metrics
        state_data = state_counts
        for metric_df in metrics:
            state_data = state_data.merge(metric_df, on='State', how='left')
        
        # Display charts
        st.subheader("Deal Distribution by State")
        
        # Bar chart of deal count by state
        fig = px.bar(
            state_data.sort_values('Count', ascending=False).head(10),
            x='State',
            y='Count',
            color='Count',
            color_continuous_scale='Blues',
            labels={'Count': 'Number of Deals'},
            height=400
        )
        
        fig.update_layout(
            xaxis_title="State",
            yaxis_title="Number of Deals",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # If we have metrics, show them
        if 'Avg Cap Rate' in state_data.columns or 'Avg IRR' in state_data.columns:
            st.subheader("Performance Metrics by State")
            
            cols = st.columns(len(metrics))
            
            for i, (col, metric_name) in enumerate(zip(cols, ['Avg Cap Rate', 'Avg IRR', 'Avg Price'])):
                if metric_name in state_data.columns:
                    with col:
                        metric_fig = px.bar(
                            state_data.sort_values('Count', ascending=False).head(10),
                            x='State',
                            y=metric_name,
                            color=metric_name,
                            color_continuous_scale='Viridis',
                            height=400
                        )
                        
                        metric_fig.update_layout(
                            xaxis_title="State",
                            yaxis_title=metric_name,
                            coloraxis_showscale=False,
                            margin=dict(l=10, r=10, t=10, b=10)
                        )
                        
                        st.plotly_chart(metric_fig, use_container_width=True)
        
        # Show the data table - DON'T USE EXPANDER HERE
        st.subheader("State Analysis Data Table")
        st.dataframe(state_data.sort_values('Count', ascending=False))
    except Exception as e:
        st.error(f"Error rendering state analysis: {str(e)}")
        logger.error(f"Error rendering state analysis: {str(e)}", exc_info=True)

def render_city_analysis(
    data: pd.DataFrame, 
    city_col: str, 
    cap_rate_col: Optional[str], 
    irr_col: Optional[str],
    price_col: Optional[str]
) -> None:
    """Render city-level analysis."""
    try:
        # Count deals by city
        city_counts = data[city_col].value_counts().reset_index()
        city_counts.columns = ['City', 'Count']
        
        # Create metrics by city if available
        metrics = []
        
        if cap_rate_col:
            # Convert to numeric
            data['cap_rate_numeric'] = safe_numeric(data, cap_rate_col)
            
            # Group and calculate mean
            city_cap_rates = (
                data
                .groupby(city_col)['cap_rate_numeric']
                .mean()
                .reset_index()
            )
            city_cap_rates.columns = ['City', 'Avg Cap Rate']
            metrics.append(city_cap_rates)
        
        if irr_col:
            # Convert to numeric
            data['irr_numeric'] = safe_numeric(data, irr_col)
            
            # Group and calculate mean
            city_irrs = (
                data
                .groupby(city_col)['irr_numeric']
                .mean()
                .reset_index()
            )
            city_irrs.columns = ['City', 'Avg IRR']
            metrics.append(city_irrs)
        
        if price_col:
            # Convert to numeric
            data['price_numeric'] = safe_numeric(data, price_col)
            
            # Group and calculate mean
            city_prices = (
                data
                .groupby(city_col)['price_numeric']
                .mean()
                .reset_index()
            )
            city_prices.columns = ['City', 'Avg Price']
            metrics.append(city_prices)
        
        # Combine all metrics
        city_data = city_counts
        for metric_df in metrics:
            city_data = city_data.merge(metric_df, on='City', how='left')
        
        # Display charts
        st.subheader("Deal Distribution by City")
        
        # Bar chart of deal count by city
        fig = px.bar(
            city_data.sort_values('Count', ascending=False).head(10),
            x='City',
            y='Count',
            color='Count',
            color_continuous_scale='Blues',
            labels={'Count': 'Number of Deals'},
            height=400
        )
        
        fig.update_layout(
            xaxis_title="City",
            yaxis_title="Number of Deals",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # If we have metrics, show them
        if 'Avg Cap Rate' in city_data.columns or 'Avg IRR' in city_data.columns:
            st.subheader("Performance Metrics by City")
            
            cols = st.columns(len(metrics))
            
            for i, (col, metric_name) in enumerate(zip(cols, ['Avg Cap Rate', 'Avg IRR', 'Avg Price'])):
                if metric_name in city_data.columns:
                    with col:
                        metric_fig = px.bar(
                            city_data.sort_values('Count', ascending=False).head(10),
                            x='City',
                            y=metric_name,
                            color=metric_name,
                            color_continuous_scale='Viridis',
                            height=400
                        )
                        
                        metric_fig.update_layout(
                            xaxis_title="City",
                            yaxis_title=metric_name,
                            coloraxis_showscale=False,
                            margin=dict(l=10, r=10, t=10, b=10)
                        )
                        
                        st.plotly_chart(metric_fig, use_container_width=True)
        
        # Show the data table - DON'T USE EXPANDER HERE
        st.subheader("City Analysis Data Table")
        st.dataframe(city_data.sort_values('Count', ascending=False))
    except Exception as e:
        st.error(f"Error rendering city analysis: {str(e)}")
        logger.error(f"Error rendering city analysis: {str(e)}", exc_info=True)

def render_market_performance(
    data: pd.DataFrame, 
    location_col: str, 
    cap_rate_col: Optional[str], 
    irr_col: Optional[str],
    price_col: Optional[str]
) -> None:
    """Render market performance analysis."""
    try:
        # Create scatter plot if we have the necessary columns
        if (cap_rate_col and irr_col) or (cap_rate_col and price_col) or (irr_col and price_col):
            st.subheader("Market Performance Comparison")
            
            # Create chart based on available metrics
            if cap_rate_col and irr_col:
                # Convert to numeric
                data['cap_rate_numeric'] = safe_numeric(data, cap_rate_col)
                data['irr_numeric'] = safe_numeric(data, irr_col)
                
                # Create scatter plot
                fig = px.scatter(
                    data,
                    x='cap_rate_numeric',
                    y='irr_numeric',
                    color=location_col,
                    hover_name=location_col,
                    labels={
                        'cap_rate_numeric': 'Cap Rate (%)',
                        'irr_numeric': 'IRR (%)'
                    },
                    height=500
                )
                
                fig.update_layout(
                    xaxis_title="Cap Rate (%)",
                    yaxis_title="IRR (%)",
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif cap_rate_col and price_col:
                # Convert to numeric
                data['cap_rate_numeric'] = safe_numeric(data, cap_rate_col)
                data['price_numeric'] = safe_numeric(data, price_col)
                
                # Create scatter plot
                fig = px.scatter(
                    data,
                    x='cap_rate_numeric',
                    y='price_numeric',
                    color=location_col,
                    hover_name=location_col,
                    labels={
                        'cap_rate_numeric': 'Cap Rate (%)',
                        'price_numeric': 'Price'
                    },
                    height=500
                )
                
                fig.update_layout(
                    xaxis_title="Cap Rate (%)",
                    yaxis_title="Price",
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif irr_col and price_col:
                # Convert to numeric
                data['irr_numeric'] = safe_numeric(data, irr_col)
                data['price_numeric'] = safe_numeric(data, price_col)
                
                # Create scatter plot
                fig = px.scatter(
                    data,
                    x='irr_numeric',
                    y='price_numeric',
                    color=location_col,
                    hover_name=location_col,
                    labels={
                        'irr_numeric': 'IRR (%)',
                        'price_numeric': 'Price'
                    },
                    height=500
                )
                
                fig.update_layout(
                    xaxis_title="IRR (%)",
                    yaxis_title="Price",
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("Not enough performance metrics found for market comparison.")
    except Exception as e:
        st.error(f"Error rendering market performance: {str(e)}")
        logger.error(f"Error rendering market performance: {str(e)}", exc_info=True)

def render_performance_metrics(data: pd.DataFrame) -> None:
    """Render performance metrics visualizations."""
    if data.empty:
        st.warning("No data available for performance metrics analysis.")
        return
    
    try:
        # Prepare data for analysis
        analysis_data = prepare_data_for_analysis(data)
        
        # Find relevant columns
        cap_rate_col = find_column_by_type(analysis_data, ['cap rate', 'cap_rate', 'capitalization'])
        irr_col = find_column_by_type(analysis_data, ['irr', 'internal rate', 'return'])
        price_col = find_column_by_type(analysis_data, ['price', 'cost', 'value'])
        noi_col = find_column_by_type(analysis_data, ['noi', 'net operating', 'operating income'])
        
        # Initialize metrics
        metrics = {}
        
        # Cap Rate
        if cap_rate_col:
            cap_rate_data = safe_numeric(analysis_data, cap_rate_col)
            cap_rate_data = cap_rate_data[cap_rate_data.notna()]
            
            if not cap_rate_data.empty:
                metrics['Cap Rate'] = {
                    'average': cap_rate_data.mean(),
                    'median': cap_rate_data.median(),
                    'min': cap_rate_data.min(),
                    'max': cap_rate_data.max(),
                    'data': cap_rate_data
                }
        
        # IRR
        if irr_col:
            irr_data = safe_numeric(analysis_data, irr_col)
            irr_data = irr_data[irr_data.notna()]
            
            if not irr_data.empty:
                metrics['IRR'] = {
                    'average': irr_data.mean(),
                    'median': irr_data.median(),
                    'min': irr_data.min(),
                    'max': irr_data.max(),
                    'data': irr_data
                }
        
        # Price
        if price_col:
            price_data = safe_numeric(analysis_data, price_col)
            price_data = price_data[price_data.notna()]
            
            if not price_data.empty:
                metrics['Price'] = {
                    'average': price_data.mean(),
                    'median': price_data.median(),
                    'min': price_data.min(),
                    'max': price_data.max(),
                    'data': price_data
                }
        
        # NOI
        if noi_col:
            noi_data = safe_numeric(analysis_data, noi_col)
            noi_data = noi_data[noi_data.notna()]
            
            if not noi_data.empty:
                metrics['NOI'] = {
                    'average': noi_data.mean(),
                    'median': noi_data.median(),
                    'min': noi_data.min(),
                    'max': noi_data.max(),
                    'data': noi_data
                }
        
        # Render metrics
        if not metrics:
            st.warning("No performance metrics found in the data.")
            return
        
        # Display summary metrics
        st.subheader("Performance Metrics Summary")
        
        # Create columns for metrics
        cols = st.columns(len(metrics))
        
        for i, (metric_name, metric_data) in enumerate(metrics.items()):
            with cols[i]:
                st.metric(
                    label=f"Average {metric_name}",
                    value=f"{metric_data['average']:.2f}" + ("%" if metric_name in ['Cap Rate', 'IRR'] else "")
                )
                
                st.metric(
                    label=f"Median {metric_name}",
                    value=f"{metric_data['median']:.2f}" + ("%" if metric_name in ['Cap Rate', 'IRR'] else "")
                )
        
        # Display distribution charts
        st.subheader("Performance Metrics Distribution")
        
        # Create tabs for different metrics
        metric_tabs = st.tabs(list(metrics.keys()))
        
        for i, (metric_name, metric_data) in enumerate(metrics.items()):
            with metric_tabs[i]:
                # Histogram
                hist_fig = px.histogram(
                    x=metric_data['data'],
                    histnorm='percent',
                    color_discrete_sequence=['#2563EB'],
                    labels={
                        'x': metric_name + (" (%)" if metric_name in ['Cap Rate', 'IRR'] else "")
                    },
                    height=400
                )
                
                hist_fig.update_layout(
                    xaxis_title=metric_name + (" (%)" if metric_name in ['Cap Rate', 'IRR'] else ""),
                    yaxis_title="Percent",
                    bargap=0.1,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                st.plotly_chart(hist_fig, use_container_width=True)
                
                # Box plot
                box_fig = px.box(
                    y=metric_data['data'],
                    color_discrete_sequence=['#2563EB'],
                    labels={
                        'y': metric_name + (" (%)" if metric_name in ['Cap Rate', 'IRR'] else "")
                    },
                    height=300
                )
                
                box_fig.update_layout(
                    yaxis_title=metric_name + (" (%)" if metric_name in ['Cap Rate', 'IRR'] else ""),
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                st.plotly_chart(box_fig, use_container_width=True)
                
                # Show statistics
                st.subheader(f"{metric_name} Statistics")
                
                stats_cols = st.columns(4)
                
                with stats_cols[0]:
                    st.metric("Average", f"{metric_data['average']:.2f}" + ("%" if metric_name in ['Cap Rate', 'IRR'] else ""))
                
                with stats_cols[1]:
                    st.metric("Median", f"{metric_data['median']:.2f}" + ("%" if metric_name in ['Cap Rate', 'IRR'] else ""))
                
                with stats_cols[2]:
                    st.metric("Minimum", f"{metric_data['min']:.2f}" + ("%" if metric_name in ['Cap Rate', 'IRR'] else ""))
                
                with stats_cols[3]:
                    st.metric("Maximum", f"{metric_data['max']:.2f}" + ("%" if metric_name in ['Cap Rate', 'IRR'] else ""))
    
    except Exception as e:
        st.error(f"Error rendering performance metrics: {str(e)}")
        logger.error(f"Error rendering performance metrics: {str(e)}", exc_info=True)

def render_deal_timeline(data: pd.DataFrame) -> None:
    """Render deal timeline visualizations."""
    if data.empty:
        st.warning("No data available for deal timeline analysis.")
        return
    
    try:
        # Prepare data for analysis
        analysis_data = prepare_data_for_analysis(data)
        
        # Find date columns
        date_cols = [col for col in analysis_data.columns if 'date' in col.lower()]
        
        if not date_cols:
            st.warning("No date columns found for timeline analysis.")
            return
        
        # Try to find the most useful date columns
        upload_date_col = next((col for col in date_cols if 'upload' in col.lower()), None)
        modified_date_col = next((col for col in date_cols if 'modified' in col.lower() or 'update' in col.lower()), None)
        close_date_col = next((col for col in date_cols if 'close' in col.lower() or 'closing' in col.lower()), None)
        
        # Pick the best available date column
        timeline_col = upload_date_col or modified_date_col or close_date_col or date_cols[0]
        
        # Convert to datetime
        analysis_data[timeline_col] = pd.to_datetime(analysis_data[timeline_col], errors='coerce')
        valid_dates = analysis_data[analysis_data[timeline_col].notna()]
        
        if valid_dates.empty:
            st.warning(f"No valid dates found in the {timeline_col} column.")
            return
        
        # Create timeline visualization
        st.subheader("Deal Timeline")
        
        # Time series of deals by month
        valid_dates['Month'] = valid_dates[timeline_col].dt.to_period('M')
        monthly_counts = valid_dates.groupby('Month').size().reset_index()
        monthly_counts['Month'] = monthly_counts['Month'].dt.to_timestamp()
        monthly_counts.columns = ['Month', 'Count']
        
        # Line chart
        fig = px.line(
            monthly_counts,
            x='Month',
            y='Count',
            markers=True,
            labels={
                'Month': 'Month',
                'Count': 'Number of Deals'
            },
            height=400
        )
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of Deals",
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Year-to-date comparison if we have multiple years
        years = valid_dates[timeline_col].dt.year.unique()
        
        if len(years) > 1:
            st.subheader("Year-to-Year Comparison")
            
            # Create year and month columns
            valid_dates['Year'] = valid_dates[timeline_col].dt.year
            valid_dates['MonthNum'] = valid_dates[timeline_col].dt.month
            
            # Group by year and month
            year_month_counts = valid_dates.groupby(['Year', 'MonthNum']).size().reset_index()
            year_month_counts.columns = ['Year', 'Month', 'Count']
            
            # Create cumulative counts by year
            cumulative_counts = []
            
            for year in years:
                year_data = year_month_counts[year_month_counts['Year'] == year].copy()
                year_data['Cumulative'] = year_data['Count'].cumsum()
                cumulative_counts.append(year_data)
            
            # Combine all years
            all_years = pd.concat(cumulative_counts)
            
            # Create line chart
            fig = px.line(
                all_years,
                x='Month',
                y='Cumulative',
                color='Year',
                markers=True,
                labels={
                    'Month': 'Month',
                    'Cumulative': 'Cumulative Deals',
                    'Year': 'Year'
                },
                height=400
            )
            
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Cumulative Deals",
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Update x-axis to show month names
            fig.update_xaxes(
                tickvals=list(range(1, 13)),
                ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error rendering deal timeline: {str(e)}")
        logger.error(f"Error rendering deal timeline: {str(e)}", exc_info=True)