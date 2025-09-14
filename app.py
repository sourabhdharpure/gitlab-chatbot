"""
GitLab AI Chatbot - Simple and Functional
"""

import streamlit as st
import os
from components.chatbot_manager import ChatbotManager
from components.performance_monitor import PerformanceMonitor
from components.cache_manager import CacheManager
from components.ui_components import UIComponents
from components.analytics_dashboard import AnalyticsDashboard

def main():
    st.set_page_config(
        page_title="GitLab AI Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add CSS to ensure sidebar is always accessible
    st.markdown("""
    <style>
    /* Force sidebar to be visible */
    .css-1d391kg {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Ensure sidebar is always shown */
    .sidebar .sidebar-content {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Make sure sidebar doesn't get hidden */
    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize components
    chatbot_manager = ChatbotManager()
    performance_monitor = PerformanceMonitor()
    cache_manager = CacheManager()
    ui_components = UIComponents()
    analytics_dashboard = AnalyticsDashboard()
    
    # Set API key (hardcoded for deployment)
    api_key = "AIzaSyBUdEgO4KT3HLN1qAvtJYCod3eCOw8Q_LU"
    if not st.session_state.get("api_key"):
        st.session_state.api_key = api_key
        os.environ["GOOGLE_API_KEY"] = api_key
    
    # Initialize chatbot
    if st.session_state.get("api_key") and not st.session_state.get('chatbot_ready', False):
        with st.spinner("Initializing..."):
            if chatbot_manager.initialize_chatbot(st.session_state.get("api_key")):
                st.session_state.chatbot_ready = True
                st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.title("GitLab AI Assistant")
        st.markdown("---")
        
        if st.button("Analytics Dashboard"):
            st.session_state.show_analytics = True
            st.rerun()
        
        if st.button("Back to Chat"):
            st.session_state.show_analytics = False
            st.rerun()
    
    # Main content
    if st.session_state.get('chatbot_ready', False):
        # Add menu options at the top
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("📊 Analytics", help="View Analytics Dashboard"):
                st.session_state.show_analytics = True
                st.rerun()
        
        with col2:
            if st.button("💬 Chat", help="Back to Chat"):
                st.session_state.show_analytics = False
                st.rerun()
        
        with col3:
            st.write("")  # Empty space
        
        if st.session_state.get('show_analytics', False):
            analytics_dashboard.render_dashboard(performance_monitor, chatbot_manager)
        else:
            ui_components.render_simple_chat(chatbot_manager, performance_monitor, cache_manager)
    else:
        st.info("Initializing GitLab AI Assistant...")

if __name__ == "__main__":
    main()