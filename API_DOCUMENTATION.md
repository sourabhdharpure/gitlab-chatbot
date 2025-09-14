# GitLab AI Assistant - API Documentation

## Overview

The GitLab AI Assistant provides a RESTful API for programmatic access to GitLab-related AI capabilities. This document describes the API endpoints, request/response formats, and authentication methods.

## Base URL

```
http://localhost:8507
```

## Authentication

Currently, the API uses API key authentication via environment variables. Future versions will support JWT tokens and OAuth2.

### Headers

```http
X-API-Key: your-api-key-here
Content-Type: application/json
```

## Endpoints

### 1. Health Check

Check the health status of the application.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-14T16:30:00Z",
  "version": "1.0.0",
  "uptime": 3600,
  "components": {
    "vector_store": "healthy",
    "cache": "healthy",
    "llm": "healthy",
    "performance_monitor": "healthy"
  }
}
```

### 2. Chat Query

Send a query to the GitLab AI Assistant.

**Endpoint**: `POST /api/chat`

**Request Body**:
```json
{
  "query": "How does GitLab handle remote work?",
  "use_context": true,
  "session_id": "optional-session-id"
}
```

**Response**:
```json
{
  "response": "GitLab is a fully remote company that has been operating remotely since 2014...",
  "sources": [
    {
      "title": "GitLab Handbook - Remote Work",
      "url": "https://about.gitlab.com/handbook/people-group/remote-work/",
      "relevance_score": 0.95
    }
  ],
  "metadata": {
    "response_time": 1.23,
    "cache_hit": false,
    "confidence_score": 0.89,
    "query_id": "q_123456789"
  }
}
```

### 3. Analytics Dashboard

Get performance analytics and metrics.

**Endpoint**: `GET /api/analytics`

**Response**:
```json
{
  "metrics": {
    "total_queries": 150,
    "cache_hit_rate": 45.2,
    "avg_response_time": 1.45,
    "error_rate": 2.1
  },
  "recent_performance": [
    {
      "timestamp": "2025-09-14T16:25:00Z",
      "response_time": 1.2,
      "cache_hit": true
    }
  ],
  "query_categories": {
    "remote_work": 25,
    "development_process": 30,
    "company_culture": 20
  }
}
```

### 4. Performance Metrics

Get detailed performance metrics.

**Endpoint**: `GET /api/metrics`

**Query Parameters**:
- `timeframe`: `hour`, `day`, `week`, `month` (default: `day`)
- `limit`: Number of records to return (default: 100)

**Response**:
```json
{
  "timeframe": "day",
  "metrics": {
    "response_times": {
      "p50": 1.2,
      "p90": 2.1,
      "p95": 2.8,
      "p99": 4.5
    },
    "cache_performance": {
      "response_cache_hits": 45,
      "semantic_cache_hits": 23,
      "total_hits": 68,
      "hit_rate": 0.45
    },
    "error_rates": {
      "total_errors": 3,
      "error_rate": 0.02,
      "error_types": {
        "api_error": 2,
        "timeout": 1
      }
    }
  }
}
```

### 5. Cache Management

Manage the caching system.

#### Get Cache Statistics

**Endpoint**: `GET /api/cache/stats`

**Response**:
```json
{
  "response_cache": {
    "size": 150,
    "hit_rate": 0.35,
    "ttl": 3600
  },
  "semantic_cache": {
    "size": 75,
    "hit_rate": 0.25,
    "similarity_threshold": 0.8
  },
  "total_size": 225,
  "total_hit_rate": 0.6
}
```

#### Clear Cache

**Endpoint**: `POST /api/cache/clear`

**Request Body**:
```json
{
  "cache_type": "all",  // "response", "semantic", "all"
  "confirm": true
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Cache cleared successfully",
  "cleared_items": 225
}
```

### 6. System Information

Get system information and configuration.

**Endpoint**: `GET /api/system/info`

**Response**:
```json
{
  "version": "1.0.0",
  "environment": "production",
  "python_version": "3.11.0",
  "dependencies": {
    "streamlit": "1.28.0",
    "chromadb": "0.4.0",
    "google-generativeai": "0.3.0"
  },
  "configuration": {
    "max_conversation_history": 10,
    "cache_ttl": 3600,
    "semantic_threshold": 0.8
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request parameters",
    "details": "The 'query' field is required",
    "timestamp": "2025-09-14T16:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Chat Queries**: 100 requests per minute per IP
- **Analytics**: 60 requests per minute per IP
- **Cache Management**: 10 requests per minute per IP

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## WebSocket Support

For real-time chat functionality, WebSocket connections are supported:

**Endpoint**: `ws://localhost:8507/ws/chat`

### WebSocket Message Format

**Client to Server**:
```json
{
  "type": "chat",
  "data": {
    "query": "How does GitLab handle code reviews?",
    "session_id": "session_123"
  }
}
```

**Server to Client**:
```json
{
  "type": "response",
  "data": {
    "response": "GitLab uses merge requests for code reviews...",
    "sources": [...],
    "metadata": {...}
  }
}
```

## SDK Examples

### Python SDK

```python
import requests
import json

class GitLabAIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def chat(self, query, use_context=True, session_id=None):
        response = requests.post(
            f"{self.base_url}/api/chat",
            headers=self.headers,
            json={
                'query': query,
                'use_context': use_context,
                'session_id': session_id
            }
        )
        return response.json()
    
    def get_analytics(self):
        response = requests.get(
            f"{self.base_url}/api/analytics",
            headers=self.headers
        )
        return response.json()

# Usage
client = GitLabAIClient("http://localhost:8507", "your-api-key")
result = client.chat("What is GitLab's remote work policy?")
print(result['response'])
```

### JavaScript SDK

```javascript
class GitLabAIClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        };
    }
    
    async chat(query, useContext = true, sessionId = null) {
        const response = await fetch(`${this.baseUrl}/api/chat`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                query,
                use_context: useContext,
                session_id: sessionId
            })
        });
        return await response.json();
    }
    
    async getAnalytics() {
        const response = await fetch(`${this.baseUrl}/api/analytics`, {
            headers: this.headers
        });
        return await response.json();
    }
}

// Usage
const client = new GitLabAIClient('http://localhost:8507', 'your-api-key');
const result = await client.chat('How does GitLab handle code reviews?');
console.log(result.response);
```

## Testing

### Test Endpoints

**Health Check Test**:
```bash
curl -X GET http://localhost:8507/health
```

**Chat Query Test**:
```bash
curl -X POST http://localhost:8507/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"query": "What is GitLab?", "use_context": true}'
```

**Analytics Test**:
```bash
curl -X GET http://localhost:8507/api/analytics \
  -H "X-API-Key: your-api-key"
```

## Changelog

### Version 1.0.0 (2025-09-14)
- Initial API release
- Chat query endpoint
- Analytics dashboard endpoint
- Performance metrics endpoint
- Cache management endpoints
- Health check endpoint
- WebSocket support for real-time chat

## Support

For API support and questions:
- Documentation: [Technical Documentation](./TECHNICAL_DOCUMENTATION.md)
- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Email: support@gitlab-ai-assistant.com

---

This API documentation is automatically generated and updated with each release. For the most current information, please refer to the latest version.
