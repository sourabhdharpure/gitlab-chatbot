"""
Utility functions for the GitLab chatbot application.
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class Config:
    """Configuration management for the application."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            "app": {
                "title": "GitLab AI Assistant",
                "max_tokens": 2048,
                "temperature": 0.7,
                "max_conversation_history": 10
            },
            "data": {
                "max_pages": 50,
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "data_dir": "data",
                "vector_store_dir": "data/chroma_db"
            },
            "urls": {
                "gitlab_handbook": "https://about.gitlab.com/handbook/",
                "gitlab_direction": "https://about.gitlab.com/direction/"
            },
            "models": {
                "embedding_model": "all-MiniLM-L6-v2",
                "default_llm": "gemini"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Error loading config file: {e}, using defaults")
        
        return default_config
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'app.title')."""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value):
        """Set configuration value using dot notation."""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value

class TextProcessor:
    """Text processing utilities."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove extra newlines
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction (can be improved with NLP libraries)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Filter common words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy',
            'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'
        }
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency
        keyword_counts = {}
        for keyword in keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:max_keywords]]
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
        """Truncate text to specified length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r'[.!?]+', text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

class URLValidator:
    """URL validation and processing utilities."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def is_gitlab_url(url: str) -> bool:
        """Check if URL is from GitLab domain."""
        try:
            parsed = urlparse(url)
            return 'gitlab.com' in parsed.netloc.lower()
        except:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL by removing fragments and query parameters."""
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except:
            return url

class FileManager:
    """File management utilities."""
    
    @staticmethod
    def ensure_directory(directory: str):
        """Ensure directory exists, create if not."""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def save_json(data: Any, filepath: str, indent: int = 2):
        """Save data as JSON file."""
        directory = os.path.dirname(filepath)
        if directory:
            FileManager.ensure_directory(directory)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def load_json(filepath: str) -> Any:
        """Load data from JSON file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def get_file_hash(filepath: str) -> str:
        """Get MD5 hash of file."""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

class Timer:
    """Simple timer utility."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        return self
    
    def stop(self):
        """Stop the timer."""
        self.end_time = time.time()
        return self
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, *args):
        self.stop()

class PerformanceMonitor:
    """Monitor application performance."""
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, name: str, value: float, timestamp: Optional[datetime] = None):
        """Record a performance metric."""
        if timestamp is None:
            timestamp = datetime.now()
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'value': value,
            'timestamp': timestamp.isoformat()
        })
    
    def get_average(self, name: str, last_n: Optional[int] = None) -> float:
        """Get average value for a metric."""
        if name not in self.metrics:
            return 0.0
        
        values = self.metrics[name]
        if last_n:
            values = values[-last_n:]
        
        if not values:
            return 0.0
        
        return sum(item['value'] for item in values) / len(values)
    
    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics for all metrics."""
        summary = {}
        for name, values in self.metrics.items():
            if values:
                value_list = [item['value'] for item in values]
                summary[name] = {
                    'count': len(value_list),
                    'average': sum(value_list) / len(value_list),
                    'min': min(value_list),
                    'max': max(value_list),
                    'latest': value_list[-1]
                }
        return summary

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    level = getattr(logging, log_level.upper())
    
    # Configure basic logging
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

# Global instances
config = Config()
performance_monitor = PerformanceMonitor()
