"""
Technical Documentation Viewer - Clean, readable documentation interface
"""

import streamlit as st
import os
from typing import Dict, List, Optional

class TechDocViewer:
    """Handles technical documentation display and navigation."""
    
    def __init__(self):
        self.docs = {
            "README.md": {
                "title": "Project Overview",
                "description": "Main project documentation and setup guide",
                "sections": [
                    "Project Description",
                    "Features",
                    "Installation",
                    "Usage",
                    "Advanced Features",
                    "Performance & Optimization",
                    "Project Structure",
                    "Contributing",
                    "License"
                ]
            },
            "TECHNICAL_DOCUMENTATION.md": {
                "title": "Technical Documentation",
                "description": "Detailed technical specifications and API documentation",
                "sections": [
                    "Architecture Overview",
                    "Component Specifications",
                    "Advanced Features",
                    "Performance Optimization",
                    "Security Considerations",
                    "Deployment Guide",
                    "API Reference",
                    "Troubleshooting"
                ]
            },
            "API_DOCUMENTATION.md": {
                "title": "API Documentation",
                "description": "API endpoints and integration guide",
                "sections": [
                    "Authentication",
                    "Endpoints",
                    "Request/Response Formats",
                    "Error Handling",
                    "Rate Limiting",
                    "SDK Examples"
                ]
            },
            "PROJECT_SUMMARY.md": {
                "title": "Project Summary",
                "description": "High-level project overview and technical approach",
                "sections": [
                    "Project Overview",
                    "Technical Approach",
                    "Key Features",
                    "Performance Metrics",
                    "Future Enhancements"
                ]
            }
        }
    
    def render_documentation_viewer(self):
        """Render the main documentation viewer interface."""
        st.title("Technical Documentation")
        st.markdown("---")
        
        # Comprehensive light theme styling for documentation
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
            font-weight: 600;
            margin: 1rem 0 0.5rem 0;
        }
        
        .stMarkdown p, .stMarkdown div, .stMarkdown span {
            color: #374151 !important;
            font-size: 14px;
            line-height: 1.6;
            margin: 0.5rem 0;
        }
        
        .stMarkdown code {
            background-color: #f3f4f6 !important;
            color: #1f2937 !important;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .stMarkdown pre {
            background-color: #f8fafc !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 6px;
            color: #1f2937 !important;
            padding: 1rem;
            overflow-x: auto;
        }
        
        .stMarkdown strong {
            color: #1f2937 !important;
            font-weight: 600;
        }
        
        .stMarkdown ul, .stMarkdown ol {
            color: #374151 !important;
            font-size: 14px;
            margin: 0.5rem 0;
        }
        
        .stMarkdown li {
            color: #374151 !important;
            font-size: 14px;
            margin: 0.25rem 0;
        }
        
        .stMarkdown table {
            background-color: #ffffff !important;
            color: #1f2937 !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 6px;
        }
        
        .stMarkdown th {
            background-color: #f8fafc !important;
            color: #1f2937 !important;
            font-weight: 600;
            padding: 0.75rem;
        }
        
        .stMarkdown td {
            background-color: #ffffff !important;
            color: #374151 !important;
            padding: 0.75rem;
        }
        
        .stMarkdown a {
            color: #3b82f6 !important;
            text-decoration: none;
        }
        
        .stMarkdown a:hover {
            color: #2563eb !important;
            text-decoration: underline;
        }
        
        .streamlit-expanderHeader {
            font-size: 14px !important;
            color: #1f2937 !important;
            background-color: #f9fafb !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 4px;
            padding: 0.5rem;
        }
        
        .streamlit-expanderContent {
            font-size: 13px !important;
            color: #374151 !important;
            background-color: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            border-top: none;
            padding: 0.75rem;
        }
        
        .stDataFrame {
            font-size: 12px !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 6px;
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
        
        .stButton > button {
            font-size: 13px !important;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            background-color: #3b82f6 !important;
            color: white !important;
        }
        
        .stButton > button:hover {
            background-color: #2563eb !important;
            color: white !important;
        }
        
        .stSelectbox > div > div {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Direct document display without navigation
        # Show README by default
        selected_doc = "README.md"
        self._render_document_content(selected_doc)
    
    def _render_document_content(self, doc_name: str):
        """Render the selected document content."""
        doc_info = self.docs[doc_name]
        
        # Document header
        st.subheader(doc_info["title"])
        st.markdown(f"*{doc_info['description']}*")
        st.markdown("---")
        
        # Read and display document content
        try:
            if os.path.exists(doc_name):
                with open(doc_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Process and display content
                self._display_processed_content(content, doc_name)
            else:
                st.error(f"Document {doc_name} not found.")
        except Exception as e:
            st.error(f"Error reading document: {str(e)}")
    
    def _display_processed_content(self, content: str, doc_name: str):
        """Display processed markdown content with enhanced formatting."""
        
        # Split content into sections
        sections = self._split_into_sections(content)
        
        # Navigation removed - direct content display
        st.markdown("---")
        
        # Display sections
        for i, (title, content) in enumerate(sections):
            with st.container():
                # Section header with anchor
                st.markdown(f"### {title}")
                
                # Add spacing
                st.markdown("")
                
                # Process and display content
                processed_content = self._process_markdown_content(content)
                st.markdown(processed_content, unsafe_allow_html=True)
                
                # Add separator between sections
                if i < len(sections) - 1:
                    st.markdown("---")
                    st.markdown("")
    
    def _split_into_sections(self, content: str) -> List[tuple]:
        """Split markdown content into sections based on headers."""
        lines = content.split('\n')
        sections = []
        current_section = []
        current_title = "Introduction"
        
        for line in lines:
            # Check for headers (##, ###, ####)
            if line.startswith('##') and not line.startswith('###'):
                # Save previous section
                if current_section:
                    sections.append((current_title, '\n'.join(current_section)))
                
                # Start new section
                current_title = line.replace('#', '').strip()
                current_section = []
            else:
                current_section.append(line)
        
        # Add last section
        if current_section:
            sections.append((current_title, '\n'.join(current_section)))
        
        return sections
    
    def _process_markdown_content(self, content: str) -> str:
        """Process markdown content for better display."""
        # Convert code blocks to proper format
        content = content.replace('```python', '<div class="code-block"><pre><code class="language-python">')
        content = content.replace('```json', '<div class="code-block"><pre><code class="language-json">')
        content = content.replace('```yaml', '<div class="code-block"><pre><code class="language-yaml">')
        content = content.replace('```bash', '<div class="code-block"><pre><code class="language-bash">')
        content = content.replace('```', '</code></pre></div>')
        
        # Convert inline code
        content = content.replace('`', '<code>')
        
        # Convert bold text
        content = content.replace('**', '<strong>')
        content = content.replace('**', '</strong>')
        
        # Convert italic text
        content = content.replace('*', '<em>')
        content = content.replace('*', '</em>')
        
        # Convert lists
        lines = content.split('\n')
        processed_lines = []
        in_list = False
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                processed_lines.append(f'<li>{line.strip()[2:]}</li>')
            elif line.strip().startswith('* '):
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                processed_lines.append(f'<li>{line.strip()[2:]}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                processed_lines.append(line)
        
        if in_list:
            processed_lines.append('</ul>')
        
        return '\n'.join(processed_lines)
    
    def render_quick_reference(self):
        """Render a quick reference guide."""
        st.title("Quick Reference")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Getting Started")
            st.markdown("""
            **1. Installation**
            ```bash
            pip install -r requirements.txt
            ```
            
            **2. Run the app**
            ```bash
            streamlit run app.py
            ```
            
            **3. Access the chatbot**
            - Open your browser to the provided URL
            - Start asking GitLab-related questions
            """)
        
        with col2:
            st.subheader("Key Features")
            st.markdown("""
            **Core Features:**
            - AI-powered GitLab assistance
            - Semantic search and retrieval
            - Real-time analytics
            - Transparency and safety features
            
            **Advanced Features:**
            - Smart suggestions
            - Performance monitoring
            - Bias detection
            - User feedback system
            """)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Project Structure")
            st.markdown("""
            ```
            gitlab-chatbot/
            ├── app.py                 # Main Streamlit application
            ├── components/           # UI and feature components
            │   ├── analytics_dashboard.py
            │   ├── cache_manager.py
            │   ├── chatbot_manager.py
            │   ├── gitlab_context_manager.py
            │   ├── performance_monitor.py
            │   ├── smart_suggestions.py
            │   ├── tech_doc_viewer.py
            │   ├── transparency_guardrails.py
            │   └── ui_components.py
            ├── src/                  # Core AI and data processing
            │   ├── chatbot.py
            │   ├── data_manager.py
            │   ├── data_processor.py
            │   ├── data_persistence.py
            │   ├── hybrid_search.py
            │   ├── prompt_manager.py
            │   ├── utils.py
            │   └── vector_store.py
            ├── data/                 # Data storage and cache
            │   ├── chroma_db/
            │   ├── chunks.json
            │   ├── documents.json
            │   └── performance_metrics.json
            └── docs/                 # Documentation files
                ├── README.md
                ├── TECHNICAL_DOCUMENTATION.md
                ├── API_DOCUMENTATION.md
                └── PROJECT_SUMMARY.md
            ```
            """)
        
        with col2:
            st.subheader("Useful Links")
            st.markdown("""
            **Documentation:**
            - [README.md](README.md) - Project overview
            - [Technical Docs](TECHNICAL_DOCUMENTATION.md) - Detailed specs
            - [API Docs](API_DOCUMENTATION.md) - API reference
            
            **External:**
            - [GitLab Handbook](https://about.gitlab.com/handbook/)
            - [Streamlit Docs](https://docs.streamlit.io/)
            - [ChromaDB Docs](https://docs.trychroma.com/)
            """)
    
    def render_architecture_flow(self):
        """Render the system architecture and query processing flow."""
        st.title("System Architecture")
        st.markdown("---")
        
        # Architecture Overview
        st.subheader("Architecture Overview")
        st.markdown("""
        The GitLab AI Assistant follows a modular, microservices-inspired architecture designed for scalability, 
        maintainability, and enterprise-grade performance. The system is built on a foundation of modern AI 
        technologies and best practices.
        """)
        
        # Query Processing Flow
        st.subheader("Query Processing Flow")
        
        # Create a visual flow diagram using Streamlit
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4>Step-by-Step Query Processing</h4>
        <ol>
        <li><strong>User Input:</strong> User submits query through Streamlit interface</li>
        <li><strong>Query Validation:</strong> System validates and preprocesses the input</li>
        <li><strong>Template Check:</strong> Check for pre-computed template responses</li>
        <li><strong>Context Enhancement:</strong> Enhance query with GitLab-specific context</li>
        <li><strong>Vector Search:</strong> Retrieve relevant documents using ChromaDB</li>
        <li><strong>LLM Processing:</strong> Generate response using Google Gemini 1.5 Flash</li>
        <li><strong>Response Enhancement:</strong> Add sources, confidence scores, and safety checks</li>
        <li><strong>User Delivery:</strong> Display response with transparency features</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # System Components
        st.subheader("System Components")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Core Components:**
            - **Chatbot Manager:** Central orchestration and state management
            - **Vector Store:** Document retrieval and semantic search
            - **LLM Integration:** Google Gemini 1.5 Flash for response generation
            - **Cache Manager:** Multi-layer caching for performance optimization
            """)
        
        with col2:
            st.markdown("""
            **Advanced Features:**
            - **Smart Suggestions:** Context-aware recommendations
            - **Transparency Guardrails:** Bias detection and safety features
            - **Analytics Dashboard:** Performance monitoring and insights
            - **Tech Doc Viewer:** Interactive documentation system
            """)
        
        # Data Flow Diagram
        st.subheader("Query Processing Flow")
        
        # Create a visual flow using Streamlit components
        st.markdown("**Step-by-Step Process:**")
        
        # Step 1
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown("""
            **1. User Input**
            - Query submitted via UI
            - Input validation
            - Preprocessing
            """)
        
        with col2:
            st.markdown("""
            **2. Template Check**
            - Check pre-computed responses
            - Fast template matching
            - Zero API cost
            """)
        
        with col3:
            st.markdown("""
            **3. Context Enhancement**
            - GitLab-specific context
            - Query optimization
            - Intent recognition
            """)
        
        st.markdown("---")
        
        # Step 2
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown("""
            **4. Cache Check**
            - Semantic cache lookup
            - Response cache check
            - Performance optimization
            """)
        
        with col2:
            st.markdown("""
            **5. Vector Search**
            - ChromaDB retrieval
            - Document similarity
            - Source identification
            """)
        
        with col3:
            st.markdown("""
            **6. LLM Processing**
            - Google Gemini 1.5 Flash
            - Response generation
            - Token optimization
            """)
        
        st.markdown("---")
        
        # Step 3
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown("""
            **7. Safety Checks**
            - Bias detection
            - Sensitive data scan
            - Content validation
            """)
        
        with col2:
            st.markdown("""
            **8. Transparency**
            - Confidence scoring
            - Decision trail
            - Source attribution
            """)
        
        with col3:
            st.markdown("""
            **9. User Delivery**
            - Response display
            - Feedback collection
            - Learning integration
            """)
        
        # Simple ASCII flow
        st.markdown("**Simplified Flow:**")
        st.code("""
User Query → Validation → Template Check → Cache Check
     ↓              ↓              ↓              ↓
Context Enhancement ← Vector Search ← LLM Processing
     ↓
Safety Checks → Transparency → User Interface → Feedback
        """)
        
        # Visual Architecture Diagram
        st.subheader("System Architecture")
        
        # Create a visual representation using columns and containers
        st.markdown("**Core System Components:**")
        
        # Top row - User Interface
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; text-align: center; margin: 5px;">
            <strong>User Interface</strong><br>
            Streamlit Web App
            </div>
            """, unsafe_allow_html=True)
        
        # Middle row - Processing Layer
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.markdown("""
            <div style="background-color: #f3e5f5; padding: 8px; border-radius: 5px; text-align: center; margin: 5px;">
            <strong>Query Processing</strong><br>
            Validation & Enhancement
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="background-color: #e8f5e8; padding: 8px; border-radius: 5px; text-align: center; margin: 5px;">
            <strong>Vector Search</strong><br>
            ChromaDB Retrieval
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div style="background-color: #fff3e0; padding: 8px; border-radius: 5px; text-align: center; margin: 5px;">
            <strong>LLM Processing</strong><br>
            Google Gemini 1.5 Flash
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div style="background-color: #fce4ec; padding: 8px; border-radius: 5px; text-align: center; margin: 5px;">
            <strong>Safety Checks</strong><br>
            Bias & Content Detection
            </div>
            """, unsafe_allow_html=True)
        
        # Bottom row - Data Layer
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="background-color: #f1f8e9; padding: 10px; border-radius: 5px; text-align: center; margin: 5px;">
            <strong>Data Layer</strong><br>
            ChromaDB + Cache + Analytics
            </div>
            """, unsafe_allow_html=True)
        
        # Performance Characteristics
        st.subheader("Performance Characteristics")
        
        metrics_data = {
            "Metric": ["Response Time", "Cache Hit Rate", "Token Efficiency", "Cost per Query"],
            "Target": ["< 2 seconds", "> 60%", "Optimized", "< $0.01"],
            "Current": ["1.2 seconds", "65%", "65% reduction", "$0.008"]
        }
        
        import pandas as pd
        df = pd.DataFrame(metrics_data)
        st.dataframe(df, use_container_width=True)
        
        # Security and Safety
        st.subheader("Security and Safety Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Data Protection:**
            - Sensitive data detection and redaction
            - API key protection
            - Secure token handling
            - Privacy-preserving analytics
            """)
        
        with col2:
            st.markdown("""
            **Bias Prevention:**
            - Multi-category bias detection
            - Inclusive language suggestions
            - Cultural sensitivity checks
            - Continuous learning from feedback
            """)
    
    def render_technical_specifications(self):
        """Render detailed technical specifications."""
        st.title("Technical Specifications")
        st.markdown("---")
        
        # Technology Stack
        st.subheader("Technology Stack")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Frontend:**
            - Streamlit 1.28.0+
            - Python 3.8+
            - HTML/CSS/JavaScript
            """)
        
        with col2:
            st.markdown("""
            **Backend:**
            - Python 3.8+
            - ChromaDB 0.3.29
            - Google Generative AI
            - Sentence Transformers
            """)
        
        with col3:
            st.markdown("""
            **Infrastructure:**
            - SQLite 3.35.0+
            - pysqlite3-binary
            - Plotly for visualizations
            - Pandas for data processing
            """)
        
        # API Specifications
        st.subheader("API Specifications")
        
        st.markdown("""
        **Google Gemini 1.5 Flash:**
        - Model: gemini-1.5-flash
        - Max Tokens: 512 (optimized)
        - Temperature: 0.7
        - Pricing: $0.000075/1K input tokens, $0.0003/1K output tokens
        """)
        
        # Database Schema
        st.subheader("Database Schema")
        
        st.markdown("""
        **ChromaDB Collections:**
        - **documents:** Main document storage with embeddings
        - **metadata:** Document metadata and source information
        - **chunks:** Text chunks for semantic search
        
        **Performance Metrics:**
        - **queries:** Query performance data
        - **responses:** Response quality metrics
        - **feedback:** User feedback and ratings
        """)
        
        # Configuration
        st.subheader("Configuration")
        
        st.markdown("""
        **Key Configuration Parameters:**
        - **chunk_size:** 1000 characters
        - **chunk_overlap:** 200 characters
        - **max_tokens:** 512 (optimized)
        - **temperature:** 0.7
        - **cache_ttl:** 3600 seconds
        """)
    
    def render_troubleshooting_guide(self):
        """Render a troubleshooting guide."""
        st.title("Troubleshooting Guide")
        
        # Common issues
        st.subheader("Common Issues")
        
        with st.expander("App won't start", expanded=False):
            st.markdown("""
            **Symptoms:** Error when running `streamlit run app.py`
            
            **Solutions:**
            1. Check Python version: `python --version` (should be 3.8+)
            2. Install dependencies: `pip install -r requirements.txt`
            3. Check for port conflicts: Try `streamlit run app.py --server.port 8502`
            4. Verify API key is set correctly
            """)
        
        with st.expander("ChromaDB errors", expanded=False):
            st.markdown("""
            **Symptoms:** SQLite version errors or database issues
            
            **Solutions:**
            1. Clear ChromaDB: Delete `data/chroma_db/` folder
            2. Reinstall pysqlite3: `pip install pysqlite3-binary`
            3. Check SQLite version compatibility
            4. Restart the application
            """)
        
        with st.expander("API errors", expanded=False):
            st.markdown("""
            **Symptoms:** Gemini API errors or rate limiting
            
            **Solutions:**
            1. Verify API key is correct and active
            2. Check API quota and billing
            3. Implement retry logic for rate limits
            4. Use template responses for common questions
            """)
        
        with st.expander("Performance issues", expanded=False):
            st.markdown("""
            **Symptoms:** Slow responses or high memory usage
            
            **Solutions:**
            1. Enable caching in settings
            2. Reduce max_tokens in configuration
            3. Optimize vector store queries
            4. Monitor memory usage with analytics
            """)
        
        # Debug information
        st.subheader("Debug Information")
        
        if st.button("Show System Info"):
            import platform
            import sys
            
            st.markdown(f"**Python Version:** {sys.version}")
            st.markdown(f"**Platform:** {platform.platform()}")
            st.markdown(f"**Streamlit Version:** {st.__version__}")
            
            # Check dependencies
            try:
                import chromadb
                st.markdown(f"**ChromaDB Version:** {chromadb.__version__}")
            except ImportError:
                st.error("ChromaDB not installed")
            
            try:
                import google.generativeai
                st.markdown("**Google Generative AI:** Installed")
            except ImportError:
                st.error("Google Generative AI not installed")
    
    def render_feature_guide(self):
        """Render a feature usage guide."""
        st.title("Feature Usage Guide")
        
        # Feature categories
        features = {
            "Core Chatbot": [
                "Ask any GitLab-related question",
                "Get contextual responses with sources",
                "View confidence scores and decision trails",
                "Rate responses to help improve the system"
            ],
            "Smart Suggestions": [
                "Context-aware recommendations in sidebar",
                "Follow-up questions after responses",
                "Proactive engagement based on queries",
                "Clickable suggestions for quick access"
            ],
            "Analytics Dashboard": [
                "View performance metrics and trends",
                "Monitor token usage and costs",
                "Track response times and cache hits",
                "Analyze query patterns and categories"
            ],
            "Transparency Features": [
                "Source confidence scoring",
                "Decision trail visualization",
                "Bias detection and safety checks",
                "Sensitive data protection"
            ],
            "Advanced Features": [
                "Multi-layer caching system",
                "Template responses for common questions",
                "User feedback and learning system",
                "Performance monitoring and optimization"
            ]
        }
        
        for category, items in features.items():
            with st.expander(category, expanded=False):
                for item in items:
                    st.markdown(f"• {item}")
        
        st.markdown("---")
        
        # Usage tips
        st.subheader("Usage Tips")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Getting Better Responses:**
            - Be specific in your questions
            - Use GitLab terminology when possible
            - Ask follow-up questions for clarification
            - Rate responses to help the system learn
            """)
        
        with col2:
            st.markdown("""
            **Maximizing Features:**
            - Check the sidebar for smart suggestions
            - Use the analytics dashboard to monitor usage
            - Explore the transparency features for insights
            - Provide feedback to improve responses
            """)
