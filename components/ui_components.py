"""
Simple UI Components - Clean and Functional
"""

import streamlit as st
import os
from datetime import datetime

class UIComponents:
    """Handles simple UI components."""
    
    def __init__(self):
        self.setup_simple_css()
    
    def setup_simple_css(self):
        """Setup minimal CSS."""
        st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        div[data-testid="stToolbar"] {display:none;}
        </style>
        """, unsafe_allow_html=True)
    
    def setup_sidebar(self):
        """Setup simple sidebar."""
        pass  # Handled in main app
    
    def render_simple_chat(self, chatbot_manager, performance_monitor, cache_manager):
        """Render a simple, functional chat interface."""
        chatbot = chatbot_manager.get_chatbot()
        
        if not chatbot:
            st.error("Chatbot not initialized.")
            return
        
        st.title("GitLab AI Assistant")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm your GitLab AI Assistant. How can I help you?"}
            ]
        
        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about GitLab..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        import time
                        start_time = time.time()
                        response, sources = chatbot.chat(prompt)
                        response_time = time.time() - start_time
                        
                        # Record query metrics for analytics
                        performance_monitor.record_query(
                            query=prompt,
                            response_time=response_time,
                            cache_hit=False,  # We'll improve this later
                            confidence_score=0.8,  # Default confidence
                            error=None
                        )
                        
                        st.write(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error: {e}")
                        # Record error in performance monitor
                        performance_monitor.record_query(
                            query=prompt,
                            response_time=0.0,
                            cache_hit=False,
                            confidence_score=0.0,
                            error=str(e)
                        )
    
    def render_setup_interface(self, chatbot_manager, performance_monitor):
        """Render simple setup interface."""
        st.title("GitLab AI Assistant")
        st.info("Initializing... Please wait.")