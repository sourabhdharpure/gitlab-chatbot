# Import necessary libraries
import os
import sys

# Fix for sqlite3 version issues on Streamlit Cloud
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # pysqlite3 not available, use system sqlite3
    pass

import streamlit as st
import os
from datetime import datetime
from typing import Dict, List, Optional

# Import custom components
from components.chatbot_manager import ChatbotManager
from components.performance_monitor import PerformanceMonitor
from components.cache_manager import CacheManager
from components.ui_components import UIComponents
from components.analytics_dashboard import AnalyticsDashboard
from components.smart_suggestions import SmartSuggestions
from components.transparency_guardrails import TransparencyGuardrails
from components.tech_doc_viewer import TechDocViewer

# Import utilities
from utils.css_loader import load_app_styles

def main():
    """Main application function."""
    
    # Set page config
    st.set_page_config(
        page_title="GitLab AI Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load application styles
    load_app_styles()

    # Get API key (hardcoded with environment variable fallback)
    api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyCB1kGPxF-JqBmDrpQA8MDeyVNC29hNyn0")
    if not api_key:
        st.error("🔑 Google API Key not found!")
        st.info("Please set the GOOGLE_API_KEY environment variable or add it to your Streamlit secrets.")
        st.code("export GOOGLE_API_KEY=your_actual_api_key_here", language="bash")
        st.stop()
    
    # Initialize components with caching for performance
    @st.cache_resource
    def initialize_components(api_key):
        """Initialize all components with caching for better performance."""
        cache_manager = CacheManager()
        chatbot_manager = ChatbotManager(api_key, cache_manager)
        performance_monitor = PerformanceMonitor()
        ui_components = UIComponents()
        analytics_dashboard = AnalyticsDashboard()
        smart_suggestions = SmartSuggestions()
        transparency_guardrails = TransparencyGuardrails()
        tech_doc_viewer = TechDocViewer()
        
        # Initialize chatbot
        if not chatbot_manager.initialize_chatbot():
            st.error("Failed to initialize chatbot. Please check the configuration.")
            st.stop()
        
        return (chatbot_manager, performance_monitor, cache_manager, ui_components, 
                analytics_dashboard, smart_suggestions, transparency_guardrails, tech_doc_viewer)
    
    # Fast initialization with caching
    (chatbot_manager, performance_monitor, cache_manager, ui_components, 
     analytics_dashboard, smart_suggestions, transparency_guardrails, tech_doc_viewer) = initialize_components(api_key)
    
    # Initialize session state flags
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = True
    if "show_analytics" not in st.session_state:
        st.session_state.show_analytics = False
    if "show_guardrails" not in st.session_state:
        st.session_state.show_guardrails = False
    if "show_docs" not in st.session_state:
        st.session_state.show_docs = False

    # Top navigation
    st.title("GitLab AI Assistant")
    st.markdown("*Your intelligent companion for all things GitLab*")
    
    # Navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Chat", type="primary" if st.session_state.show_chat else "secondary"):
            st.session_state.show_chat = True
            st.session_state.show_analytics = False
            st.session_state.show_guardrails = False
            st.session_state.show_docs = False
            st.rerun()
    
    with col2:
        if st.button("Analytics", type="primary" if st.session_state.show_analytics else "secondary"):
            st.session_state.show_chat = False
            st.session_state.show_analytics = True
            st.session_state.show_guardrails = False
            st.session_state.show_docs = False
            st.rerun()
    
    with col3:
        if st.button("Guardrails", type="primary" if st.session_state.show_guardrails else "secondary"):
            st.session_state.show_chat = False
            st.session_state.show_analytics = False
            st.session_state.show_guardrails = True
            st.session_state.show_docs = False
            st.rerun()
    
    with col4:
        if st.button("Docs", type="primary" if st.session_state.show_docs else "secondary"):
            st.session_state.show_chat = False
            st.session_state.show_analytics = False
            st.session_state.show_guardrails = False
            st.session_state.show_docs = True
            st.rerun()

    # Sidebar with smart suggestions
    smart_suggestions.render_suggestions_sidebar()

    # Main content based on navigation
    if st.session_state.show_chat:
        # Enhanced chat interface
        ui_components.render_enhanced_chat(
            chatbot_manager,
            performance_monitor,
            cache_manager,
            smart_suggestions,
            transparency_guardrails
        )
        
    elif st.session_state.show_analytics:
        analytics_dashboard.render_dashboard(performance_monitor)
        
    elif st.session_state.show_guardrails:
        transparency_guardrails.render_learning_dashboard()
        
    elif st.session_state.show_docs:
        # Documentation viewer
        tech_doc_viewer.render_documentation_viewer()

if __name__ == "__main__":
    main()
