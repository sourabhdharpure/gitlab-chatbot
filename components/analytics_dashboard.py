"""
Simple Analytics Dashboard - Clean and Functional
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    """Renders a simple analytics dashboard."""
    
    def render_dashboard(self, performance_monitor, chatbot_manager=None):
        """Render a simple analytics dashboard."""
        # Add comprehensive light theme styling
        st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff !important;
        }
        .main .block-container {
            background-color: #ffffff !important;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #1f2937 !important;
        }
        .stMarkdown p, .stMarkdown div, .stMarkdown span {
            color: #374151 !important;
        }
        .stMetric {
            background-color: #f8fafc !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 6px !important;
            padding: 1rem !important;
        }
        .stMetric > div {
            color: #1f2937 !important;
        }
        .stMetric > div > div {
            color: #374151 !important;
        }
        .stDataFrame {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        .stDataFrame table {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        .stDataFrame th {
            background-color: #f8fafc !important;
            color: #1f2937 !important;
        }
        .stDataFrame td {
            background-color: #ffffff !important;
            color: #374151 !important;
        }
        .stSelectbox > div > div {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        .stSlider > div > div {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        .stButton > button {
            background-color: #3b82f6 !important;
            color: white !important;
        }
        .stButton > button:hover {
            background-color: #2563eb !important;
            color: white !important;
        }
        .stExpander {
            background-color: #ffffff !important;
            border: 1px solid #e5e7eb !important;
        }
        .streamlit-expanderHeader {
            background-color: #f8fafc !important;
            color: #1f2937 !important;
        }
        .streamlit-expanderContent {
            background-color: #ffffff !important;
            color: #374151 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.title("Analytics Dashboard")
        
        # Get performance data
        metrics = performance_monitor.get_performance_summary()
        system_health = performance_monitor.get_system_health()
        
        if metrics.get('status') == 'no_data':
            st.info("No performance data available yet. Start chatting to see metrics!")
            return
        
        # Key Metrics Overview
        self._render_key_metrics(metrics)
        
        # Performance Charts
        self._render_performance_charts(performance_monitor)
        
        # System Health
        self._render_system_health(system_health)
    
    def _render_key_metrics(self, metrics):
        """Render key performance metrics simply."""
        st.subheader("Key Metrics")
        
        # First row - Basic metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", metrics.get('total_queries', 0))
        
        with col2:
            cache_rate = metrics.get('cache_hit_rate', 0)
            st.metric("Cache Hit Rate", f"{cache_rate:.1f}%")
        
        with col3:
            avg_time = metrics.get('avg_response_time', 0)
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
        
        with col4:
            error_rate = metrics.get('error_rate', 0)
            st.metric("Error Rate", f"{error_rate:.1f}%")
        
        # Second row - Token metrics
        st.subheader("Token Usage Analytics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tokens = metrics.get('total_tokens', 0)
            st.metric("Total Tokens", f"{total_tokens:,}")
        
        with col2:
            avg_tokens = metrics.get('avg_tokens_per_query', 0)
            st.metric("Avg Tokens/Query", f"{avg_tokens:.0f}")
        
        with col3:
            total_cost = metrics.get('total_cost_usd', 0)
            st.metric("Total Cost", f"${total_cost:.4f}")
        
        with col4:
            avg_cost = metrics.get('avg_cost_per_query', 0)
            st.metric("Avg Cost/Query", f"${avg_cost:.4f}")
    
    def _render_performance_charts(self, performance_monitor):
        """Render performance charts with consistent styling."""
        st.subheader("Performance Charts")
        
        # Get recent metrics for charts
        recent_metrics = list(performance_monitor.recent_metrics)
        if not recent_metrics:
            st.info("No recent performance data available.")
            return
        
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Response Time Chart
            self._render_response_time_chart(recent_metrics)
        
        with col2:
            # Cache Hit Rate Chart
            self._render_cache_hit_chart(recent_metrics)
        
        # Token Usage Charts
        st.subheader("Token Usage Trends")
        col1, col2 = st.columns(2)
        
        with col1:
            # Token Usage per Query Chart
            self._render_token_usage_chart(recent_metrics)
        
        with col2:
            # Cost per Query Chart
            self._render_cost_chart(recent_metrics)
        
        # Query Categories Chart
        self._render_query_categories_chart(performance_monitor)
    
    def _render_response_time_chart(self, recent_metrics):
        """Render response time trend chart."""
        if not recent_metrics:
            return
        
        # Prepare data
        queries = list(range(1, len(recent_metrics) + 1))
        response_times = [metric.response_time for metric in recent_metrics]
        
        # Create chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=queries,
            y=response_times,
            mode='lines+markers',
            name='Response Time',
            line=dict(color='#007aff', width=2),
            marker=dict(size=6, color='#007aff')
        ))
        
        fig.update_layout(
            title="Response Time Trend",
            xaxis_title="Query Number",
            yaxis_title="Response Time (seconds)",
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#374151', size=12),
            xaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            yaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_cache_hit_chart(self, recent_metrics):
        """Render cache hit rate chart."""
        if not recent_metrics:
            return
        
        # Calculate cache hit rate over time
        cache_hits = 0
        cache_rates = []
        
        for i, metric in enumerate(recent_metrics):
            if metric.cache_hit:
                cache_hits += 1
            cache_rate = (cache_hits / (i + 1)) * 100
            cache_rates.append(cache_rate)
        
        queries = list(range(1, len(recent_metrics) + 1))
        
        # Create chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=queries,
            y=cache_rates,
            mode='lines+markers',
            name='Cache Hit Rate',
            line=dict(color='#34c759', width=2),
            marker=dict(size=6, color='#34c759')
        ))
        
        fig.update_layout(
            title="Cache Hit Rate Trend",
            xaxis_title="Query Number",
            yaxis_title="Cache Hit Rate (%)",
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#374151', size=12),
            xaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            yaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_query_categories_chart(self, performance_monitor):
        """Render query categories chart."""
        if not performance_monitor.query_categories:
            return
        
        # Prepare data
        categories = list(performance_monitor.query_categories.keys())
        counts = list(performance_monitor.query_categories.values())
        
        if not categories:
            return
        
        # Create chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories,
            y=counts,
            marker_color='#ff9500'
        ))
        
        fig.update_layout(
            title="Queries by Category",
            xaxis_title="Category",
            yaxis_title="Count",
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#374151', size=12),
            xaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            yaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_system_health(self, system_health):
        """Render system health metrics."""
        st.subheader("System Health")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpu_usage = system_health.get('cpu_usage', 0)
            st.metric("CPU Usage", f"{cpu_usage:.1f}%")
        
        with col2:
            memory_usage = system_health.get('memory_usage', 0)
            st.metric("Memory Usage", f"{memory_usage:.1f}%")
        
        with col3:
            uptime = system_health.get('uptime', 0)
            st.metric("Uptime", f"{uptime:.1f}s")
    
    def _render_token_usage_chart(self, recent_metrics):
        """Render token usage per query chart."""
        if not recent_metrics:
            return
        
        # Prepare data
        queries = list(range(1, len(recent_metrics) + 1))
        total_tokens = [metric.total_tokens for metric in recent_metrics]
        input_tokens = [metric.input_tokens for metric in recent_metrics]
        output_tokens = [metric.output_tokens for metric in recent_metrics]
        
        # Create chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=queries,
            y=total_tokens,
            mode='lines+markers',
            name='Total Tokens',
            line=dict(color='#007aff', width=2),
            marker=dict(size=6, color='#007aff')
        ))
        
        fig.add_trace(go.Scatter(
            x=queries,
            y=input_tokens,
            mode='lines+markers',
            name='Input Tokens',
            line=dict(color='#34c759', width=2),
            marker=dict(size=6, color='#34c759')
        ))
        
        fig.add_trace(go.Scatter(
            x=queries,
            y=output_tokens,
            mode='lines+markers',
            name='Output Tokens',
            line=dict(color='#ff9500', width=2),
            marker=dict(size=6, color='#ff9500')
        ))
        
        fig.update_layout(
            title="Token Usage per Query",
            xaxis_title="Query Number",
            yaxis_title="Tokens",
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#374151', size=12),
            xaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            yaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_cost_chart(self, recent_metrics):
        """Render cost per query chart."""
        if not recent_metrics:
            return
        
        # Prepare data
        queries = list(range(1, len(recent_metrics) + 1))
        costs = [metric.cost_usd for metric in recent_metrics]
        
        # Create chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=queries,
            y=costs,
            mode='lines+markers',
            name='Cost per Query',
            line=dict(color='#ff3b30', width=2),
            marker=dict(size=6, color='#ff3b30')
        ))
        
        fig.update_layout(
            title="Cost per Query (USD)",
            xaxis_title="Query Number",
            yaxis_title="Cost (USD)",
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#374151', size=12),
            xaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            yaxis=dict(color='#374151', gridcolor='#e5e7eb'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    