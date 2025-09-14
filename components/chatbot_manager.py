"""
Chatbot Manager - Handles chatbot initialization and operations
"""

import streamlit as st
import os
import logging
from datetime import datetime
from typing import Tuple

# Import chatbot components
try:
    from src.chatbot import create_chatbot_from_config, GitLabChatbot
    from src.vector_store import build_vector_store_from_data, VectorStore
except ImportError:
    from chatbot import create_chatbot_from_config, GitLabChatbot
    from vector_store import build_vector_store_from_data, VectorStore

from .gitlab_context_manager import GitLabContextManager

logger = logging.getLogger(__name__)

class ChatbotManager:
    """Manages chatbot initialization and operations."""
    
    def __init__(self):
        self.chatbot = None
        self.vector_store = None
        self.context_manager = GitLabContextManager()
    
    def initialize_chatbot(self, api_key: str) -> bool:
        """Initialize the chatbot with API key."""
        try:
            if not api_key:
                logger.error("No API key provided")
                st.error("No API key provided")
                return False
            
            # Set environment variable
            os.environ["GOOGLE_API_KEY"] = api_key
            logger.info("API key set in environment")
            
            # Build vector store
            logger.info("Loading vector database...")
            try:
                self.vector_store = build_vector_store_from_data("data/chunks.json")
                logger.info("Vector store loaded successfully")
            except Exception as e:
                logger.error(f"Error loading vector store: {e}")
                st.error(f"Error loading vector store: {e}")
                return False
            
            # Create chatbot
            logger.info("Initializing AI Assistant...")
            try:
                self.chatbot = create_chatbot_from_config()
                logger.info("Chatbot created successfully")
            except Exception as e:
                logger.error(f"Error creating chatbot: {e}")
                st.error(f"Error creating chatbot: {e}")
                return False
            
            st.session_state.chatbot = self.chatbot
            st.session_state.vector_store = self.vector_store
            st.session_state.chatbot_ready = True
            
            logger.info("Chatbot initialized successfully!")
            st.success("Chatbot initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Chatbot initialization error: {e}")
            st.error(f"Chatbot initialization error: {e}")
            return False
    
    def get_chatbot(self):
        """Get the current chatbot instance."""
        return st.session_state.get('chatbot')
    
    def get_vector_store(self):
        """Get the current vector store instance."""
        return st.session_state.get('vector_store')
    
    def process_query_with_context(self, query: str) -> Tuple[str, str, bool, str]:
        """
        Process query with GitLab context enforcement.
        
        Returns:
            Tuple[processed_query, system_prompt, should_redirect, redirect_message]
        """
        # Check if query should be redirected
        if self.context_manager.should_redirect_to_gitlab(query):
            redirect_msg = self.context_manager.get_redirect_prompt(query)
            return query, "", True, redirect_msg
        
        # Rewrite query for GitLab context
        processed_query = self.context_manager.rewrite_query_for_gitlab_context(query)
        
        # Get appropriate system prompt
        system_prompt = self.context_manager.get_system_prompt(query)
        
        return processed_query, system_prompt, False, ""
    
    def update_context_after_response(self, query: str, response: str):
        """Update conversation context after generating response."""
        self.context_manager.update_conversation_context(query, response)
    
    def get_context_summary(self):
        """Get current conversation context summary."""
        return self.context_manager.get_context_summary()
