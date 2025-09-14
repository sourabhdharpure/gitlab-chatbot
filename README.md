# GitLab AI Assistant

A production-grade AI-powered chatbot specifically designed for GitLab-related questions, built with Streamlit, Google Gemini, and advanced RAG (Retrieval-Augmented Generation) capabilities.

## 🚀 Features

- **GitLab-Focused AI**: Specialized for GitLab's culture, processes, and best practices
- **Real-Time Analytics**: Live performance monitoring and metrics dashboard
- **Semantic Caching**: Intelligent caching for faster responses
- **Persistent Memory**: Conversation history and data persistence
- **Production-Ready**: Clean, professional UI with error handling
- **Context Enforcement**: Always maintains GitLab context in responses

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
   # Edit .env and add your GOOGLE_API_KEY
   ```

4. **Run the application**
   ```bash
   streamlit run app.py --server.port 8507
   ```

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