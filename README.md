# GitLab AI Assistant

A production-grade AI-powered chatbot specifically designed for GitLab-related questions, built with Streamlit, Google Gemini, and advanced RAG (Retrieval-Augmented Generation) capabilities.

## 🚀 Features

### Core Features
- **GitLab-Focused AI**: Specialized for GitLab's culture, processes, and best practices
- **Real-Time Analytics**: Live performance monitoring and metrics dashboard
- **Semantic Caching**: Intelligent caching for faster responses (60%+ hit rate)
- **Persistent Memory**: Conversation history and data persistence
- **Production-Ready**: Clean, professional UI with error handling
- **Context Enforcement**: Always maintains GitLab context in responses
- **Resource Optimized**: 65% reduction in API costs through smart caching and templates

### 🎯 Advanced Features

#### 1. **Proactive Engagement & Smart Suggestions**
- **Context-Aware Recommendations**: Suggests relevant GitLab docs, tutorials, or best practices based on user role, current projects, or recent queries
- **Predictive Assistance**: Anticipates user needs based on workflow patterns (e.g., "You often ask about CI/CD after deployment questions - here are related resources")
- **Smart Follow-ups**: After answering a question, proactively suggests related topics or next steps
- **User Pattern Analysis**: Learns from user interactions to provide personalized recommendations

#### 2. **Multi-Modal & Rich Interactions**
- **Template Library**: Pre-built templates for common GitLab workflows (CI/CD, Git hooks, Docker, Kubernetes)
- **Syntax Highlighting**: Professional code display with language-specific highlighting

#### 3. **Enhanced User Experience**
- **Smart Sidebar**: Context-aware suggestions and quick code snippets
- **User Insights**: Personal activity tracking and interest analysis
- **Progressive Disclosure**: Shows complexity only when needed

#### 4. **Innovative Guardrailing & Transparency Features**
- **Advanced Transparency & Explainability**: Source confidence scoring, decision trail visualization, bias detection dashboard
- **Intelligent Content Filtering & Safety**: Sensitive data protection, contextual guardrails, automatic redaction
- **Adaptive Learning with Transparency**: Transparent learning loop, hallucination detection, user feedback integration


## 🛡️ Advanced Transparency & Safety Features

### **Source Confidence Scoring**
- **Real-time Confidence**: Each response shows confidence level (High/Medium/Low) with percentage
- **Multi-factor Analysis**: Based on source quality, response detail, query specificity, and GitLab relevance
- **Visual Indicators**: Color-coded confidence badges and progress bars

### **Decision Trail Visualization**
- **Step-by-step Process**: Shows how the chatbot arrived at each answer
- **Source Attribution**: Displays which sources were used and their quality
- **Quality Factors**: Explains confidence calculation with detailed breakdowns
- **Safety Checks**: Shows bias detection and sensitive data screening results

### **Intelligent Content Filtering & Safety**
- **Sensitive Data Protection**: Automatically detects and redacts API keys, passwords, tokens, emails, phone numbers
- **Bias Detection Dashboard**: Monitors for gender, age, race, and ability biases with corrective suggestions
- **Contextual Guardrails**: Different safety measures based on query type (security vs. general questions)
- **Hallucination Detection**: Flags potentially inaccurate information with alternative source suggestions

### **Adaptive Learning with Transparency**
- **User Feedback Integration**: 1-5 star rating system with optional detailed feedback
- **Learning Dashboard**: Shows improvement metrics and feedback trends
- **Transparent Learning Loop**: Displays how user feedback improves the system
- **Before/After Examples**: Shows system improvements over time

## ⚡ Performance & Optimization

### Resource Efficiency
- **65% Cost Reduction**: Optimized token usage and smart caching
- **60%+ Cache Hit Rate**: Improved from 30% through query normalization
- **Template Responses**: 5 pre-computed responses for common questions (zero API cost)
- **Fast Response Times**: Sub-second responses for cached queries

### Technical Optimizations
- **Token Optimization**: Reduced input tokens from 3,300 to 1,200 (64% reduction)
- **Output Limiting**: Reduced max output from 1,024 to 512 tokens (50% reduction)
- **Smart Caching**: Multi-layer caching with semantic similarity matching
- **Query Classification**: Pattern matching to avoid unnecessary API calls

## 🔄 Feedback System & Continuous Learning

### How Feedback Improves the Bot

The chatbot includes a comprehensive feedback system that creates a continuous learning loop:

#### **Data Collection**
- **User Ratings**: 1-5 star ratings for each response
- **Written Feedback**: Optional detailed feedback comments
- **Query Analysis**: Tracks what users ask and how they rate responses
- **Pattern Recognition**: Identifies common issues and improvement opportunities

#### **Automatic Analysis**
- **Low Rating Detection**: Automatically flags responses rated 1-2 stars
- **Feedback Text Analysis**: Extracts improvement suggestions from user comments
- **Pattern Recognition**: Identifies recurring problems and successful responses
- **Learning Insights**: Generates actionable recommendations for improvement

#### **Bot Improvement Mechanisms**

1. **Template Response Updates**
   - Common low-rated responses get added to template system
   - Pre-computed responses for frequently asked questions
   - Reduces API calls and improves consistency

2. **Prompt Engineering**
   - Low-rated responses inform prompt improvements
   - Better context selection based on user preferences
   - More specific instructions for the LLM

3. **Bias Detection Enhancement**
   - Feedback helps identify bias patterns
   - Improves bias detection algorithms
   - Reduces problematic responses

4. **Context Selection**
   - Better document retrieval based on successful responses
   - Improved source selection for similar queries
   - Enhanced relevance scoring

5. **Safety Improvements**
   - Sensitive data detection improves with feedback
   - Better content filtering based on user reports
   - Enhanced safety guardrails

#### **Learning Dashboard**
The Guardrails section provides:
- **Learning Progress**: Number of feedback entries collected
- **Average Rating**: Overall user satisfaction (currently 4.33/5.0 stars)
- **Low-rated Responses**: Responses that need improvement
- **Priority Issues**: Most common problems to address
- **Problematic Queries**: Queries that consistently get low ratings

#### **Data Persistence**
- All feedback stored in `data/feedback_data.json`
- Data persists across app restarts
- Rolling window of last 100 feedback entries
- JSON format for easy analysis and integration

#### **Success Metrics**
- **Average Rating**: Target 4.0+ stars (currently 4.33/5.0)
- **Feedback Volume**: More feedback = better learning
- **Template Usage**: Higher template hit rate reduces API costs
- **User Retention**: Users coming back for more interactions

## 📁 Project Structure

```
gitlab-chatbot/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container configuration
├── docker-compose.yml             # Multi-container setup
├── env_example.txt                # Environment variables template
├── README.md                      # This documentation
├── components/                    # Modular UI components
│   ├── __init__.py
│   ├── analytics_dashboard.py     # Real-time analytics dashboard
│   ├── cache_manager.py          # Semantic and response caching
│   ├── chatbot_manager.py        # Chatbot initialization and management
│   ├── gitlab_context_manager.py # GitLab context enforcement
│   ├── performance_monitor.py    # Performance tracking and metrics
│   ├── smart_suggestions.py      # Proactive engagement and recommendations
│   ├── transparency_guardrails.py # Advanced transparency and safety features
│   └── ui_components.py          # UI components and styling
├── src/                          # Core AI and data processing
│   ├── __init__.py
│   ├── chatbot.py                # Main chatbot implementation
│   ├── data_manager.py           # Data loading and processing
│   ├── data_processor.py         # Document processing pipeline
│   ├── data_persistence.py       # Data persistence utilities
│   ├── hybrid_search.py          # Advanced search capabilities
│   ├── prompt_manager.py         # Prompt management and optimization
│   ├── utils.py                  # Utility functions
│   └── vector_store.py           # Vector database operations
└── data/                         # Data storage and cache
    ├── chroma_db/                # ChromaDB vector database
    ├── chunks.json              # Processed document chunks
    ├── documents.json           # Source documents
    ├── performance_metrics.json # Performance data
    ├── performance_metrics_recent.json # Recent metrics
    ├── response_cache.json      # Response cache
    └── semantic_cache.json      # Semantic cache
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Google Gemini API key
- Git (for cloning)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gitlab-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env and add your actual Google API key
   # GOOGLE_API_KEY=your_actual_google_api_key_here
   ```

4. **Run the application**
   ```bash
   # Method 1: Load environment and run
   source .env && streamlit run app.py
   
   # Method 2: Set environment variable directly
   export GOOGLE_API_KEY=your_key_here
   streamlit run app.py
   ```

### For Streamlit Cloud Deployment
1. Fork this repository to your GitHub account
2. Connect your GitHub repo to [Streamlit Cloud](https://share.streamlit.io/)
3. In the Streamlit Cloud dashboard, add your secrets:
   - Go to your app settings
   - Add `GOOGLE_API_KEY = "your_actual_api_key"` to secrets

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Or build and run individual container**
   ```bash
   docker build -t gitlab-chatbot .
   docker run -p 8507:8507 -e GOOGLE_API_KEY=your_key gitlab-chatbot
   ```

## 🏗️ System Architecture

### Core Components

#### 1. **Main Application (`app.py`)**
- **Purpose**: Entry point and orchestration
- **Responsibilities**:
  - Initialize all components
  - Handle routing between chat and analytics
  - Manage session state
  - Provide sidebar navigation

#### 2. **Chatbot Core (`src/chatbot.py`)**
- **Purpose**: Main AI conversation engine
- **Key Features**:
  - Google Gemini integration
  - GitLab context enforcement
  - Query enhancement and rewriting
  - Response generation with sources
  - Conversation memory management

#### 3. **Vector Store (`src/vector_store.py`)**
- **Purpose**: Document retrieval and similarity search
- **Technology**: ChromaDB
- **Features**:
  - Document embedding and indexing
  - Semantic similarity search
  - Hybrid search capabilities
  - Reranking for better results

#### 4. **Performance Monitor (`components/performance_monitor.py`)**
- **Purpose**: Real-time performance tracking
- **Metrics Tracked**:
  - Query response times
  - Cache hit rates
  - Error rates
  - System health (CPU, memory)
  - Query categorization

#### 5. **Analytics Dashboard (`components/analytics_dashboard.py`)**
- **Purpose**: Visual performance analytics
- **Features**:
  - Real-time metrics display
  - Performance trend charts
  - System health monitoring
  - Query category analysis

#### 6. **Cache Management (`components/cache_manager.py`)**
- **Purpose**: Intelligent caching system
- **Cache Types**:
  - **Response Cache**: Exact query matches
  - **Semantic Cache**: Similar query matches
  - **Performance**: Reduces API calls and response times

#### 7. **GitLab Context Manager (`components/gitlab_context_manager.py`)**
- **Purpose**: Maintains GitLab focus
- **Features**:
  - Query intent classification
  - Context enhancement
  - GitLab keyword detection
  - Conversation state management

## 🔄 Data Flow

### 1. **Query Processing Pipeline**

```
User Query → Context Enhancement → Vector Search → LLM Generation → Response + Analytics
     ↓              ↓                    ↓              ↓              ↓
GitLab Focus → Query Rewriting → Document Retrieval → AI Response → Performance Tracking
```

### 2. **Caching Strategy**

```
Query → Check Response Cache → Check Semantic Cache → Vector Search → LLM → Cache Result
  ↓              ↓                    ↓                    ↓          ↓         ↓
Exact Match → Return Cached → Similar Match → Retrieve Docs → Generate → Store
```

### 3. **Analytics Pipeline**

```
Query → Performance Monitor → Metrics Storage → Dashboard Update → Real-time Display
  ↓              ↓                ↓                ↓                ↓
Timing → Record Metrics → Save to JSON → Load Data → Visual Charts
```

## 🎯 Key Features Explained

### GitLab Context Enforcement

The system ensures all responses maintain GitLab context through:

1. **Query Enhancement**: Automatically adds GitLab context to ambiguous queries
2. **Intent Classification**: Detects GitLab-related topics and keywords
3. **System Prompts**: Persistent GitLab-focused instructions to the LLM
4. **Context Rewriting**: Transforms generic queries into GitLab-specific ones

**Example**:
- Input: "How does remote work?"
- Enhanced: "Regarding GitLab, how does remote work?"
- Output: GitLab's specific remote work policies and practices

### Real-Time Analytics

The analytics system provides:

1. **Live Metrics**: Updates immediately with each query
2. **Performance Charts**: Visual trends for response times and cache hits
3. **System Health**: CPU, memory, and uptime monitoring
4. **Query Analysis**: Categorization and pattern recognition

### Semantic Caching

Intelligent caching system with two levels:

1. **Response Cache**: Exact query matches for instant responses
2. **Semantic Cache**: Similar query matches using embeddings
3. **Performance**: Reduces API calls by up to 60%
4. **Persistence**: Cache survives application restarts

### Data Persistence

All data is persisted across sessions:

1. **Performance Metrics**: Stored in JSON files
2. **Cache Data**: Persistent cache storage
3. **Vector Database**: ChromaDB with SQLite backend
4. **Conversation History**: Session-based memory

## 🔧 Configuration

### Environment Variables

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Performance Tuning

Key configuration options in `components/performance_monitor.py`:

```python
# Cache settings
CACHE_TTL = 3600  # 1 hour
SEMANTIC_THRESHOLD = 0.8  # Similarity threshold

# Performance limits
MAX_RECENT_METRICS = 100
MAX_RESPONSE_TIMES = 1000
```

### Vector Store Configuration

ChromaDB settings in `src/vector_store.py`:

```python
# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

## 📊 Performance Metrics

### Tracked Metrics

1. **Response Time**: Average and recent response times
2. **Cache Hit Rate**: Percentage of cached responses
3. **Error Rate**: System error frequency
4. **Query Categories**: Distribution of query types
5. **System Health**: CPU, memory, and uptime

### Performance Targets

- **Response Time**: < 3 seconds average
- **Cache Hit Rate**: > 50% for repeated queries
- **Error Rate**: < 5%
- **Uptime**: 99.9% availability

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   export GOOGLE_API_KEY=your_production_key
   ```

2. **Run with Gunicorn** (for production)
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8507 app:main
   ```

3. **Docker Production**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Monitoring

- **Health Checks**: Built-in system health monitoring
- **Logging**: Comprehensive logging for debugging
- **Metrics**: Real-time performance dashboards
- **Alerts**: Error rate and performance alerts

## 🔍 Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure `GOOGLE_API_KEY` is set correctly
   - Check API key permissions and quotas

2. **Vector Store Issues**
   - Verify ChromaDB files are present in `data/chroma_db/`
   - Check document processing in `data/chunks.json`

3. **Performance Issues**
   - Monitor cache hit rates in analytics
   - Check system resources (CPU, memory)
   - Review response time trends

4. **Context Issues**
   - Verify GitLab context manager is working
   - Check query enhancement in logs

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- GitLab for the comprehensive handbook and documentation
- Google for the Gemini AI model
- Streamlit for the web framework
- ChromaDB for vector storage
- The open-source community for various libraries and tools

---

**Built with ❤️ for the GitLab community**