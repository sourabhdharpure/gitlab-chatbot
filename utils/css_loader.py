"""CSS loader utility for Streamlit applications."""

import streamlit as st
from pathlib import Path


def load_css(css_file_path: str) -> None:
    """
    Load CSS from an external file and inject it into the Streamlit app.
    
    Args:
        css_file_path: Path to the CSS file relative to the project root
    """
    try:
        css_path = Path(css_file_path)
        if css_path.exists():
            with open(css_path, 'r') as f:
                css_content = f.read()
            
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        else:
            st.warning(f"CSS file not found: {css_file_path}")
    except Exception as e:
        st.error(f"Error loading CSS: {str(e)}")


def load_app_styles() -> None:
    """Load the main application styles."""
    load_css("static/css/app_styles.css")
