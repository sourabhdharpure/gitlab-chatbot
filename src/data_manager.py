"""
Data source manager for handling multiple knowledge bases.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging
from pathlib import Path

try:
    from .data_processor import WebDataProcessor
    from .vector_store import VectorStore, build_vector_store_from_data
except ImportError:
    from data_processor import WebDataProcessor
    from vector_store import VectorStore, build_vector_store_from_data

logger = logging.getLogger(__name__)

class DataSourceManager:
    """Manages multiple data sources and their vector stores."""
    
    def __init__(self, base_data_dir: str = "data"):
        self.base_data_dir = Path(base_data_dir)
        self.base_data_dir.mkdir(exist_ok=True)
        
        # Metadata file to track all data sources
        self.metadata_file = self.base_data_dir / "sources_metadata.json"
        self.metadata = self.load_metadata()
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load metadata about all data sources."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
        
        return {"sources": {}, "current_source": None}
    
    def save_metadata(self):
        """Save metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def generate_source_id(self, urls: List[str], name: str = None) -> str:
        """Generate a unique ID for a data source."""
        if name:
            # Use provided name, sanitized
            base_id = "".join(c for c in name.lower() if c.isalnum() or c in '-_')
        else:
            # Generate from URLs
            url_hash = hashlib.md5('|'.join(sorted(urls)).encode()).hexdigest()[:8]
            base_id = f"source_{url_hash}"
        
        # Ensure uniqueness
        counter = 1
        source_id = base_id
        while source_id in self.metadata["sources"]:
            source_id = f"{base_id}_{counter}"
            counter += 1
        
        return source_id
    
    def create_data_source(self, urls: List[str], name: str = None, 
                          description: str = None, max_pages: int = 50) -> Dict[str, Any]:
        """Create a new data source from URLs."""
        source_id = self.generate_source_id(urls, name)
        
        # Create directory for this source
        source_dir = self.base_data_dir / source_id
        source_dir.mkdir(exist_ok=True)
        
        # Source metadata
        source_info = {
            "id": source_id,
            "name": name or f"Source {source_id}",
            "description": description or f"Data from {len(urls)} URLs",
            "urls": urls,
            "created_at": datetime.now().isoformat(),
            "last_updated": None,
            "status": "creating",
            "document_count": 0,
            "chunk_count": 0,
            "directory": str(source_dir),
            "vector_store_path": str(source_dir / "chroma_db")
        }
        
        # Add to metadata
        self.metadata["sources"][source_id] = source_info
        self.save_metadata()
        
        return source_info
    
    def process_data_source(self, source_id: str, max_pages: int = 50) -> Dict[str, Any]:
        """Process a data source by scraping and creating vector store."""
        if source_id not in self.metadata["sources"]:
            raise ValueError(f"Data source {source_id} not found")
        
        source_info = self.metadata["sources"][source_id]
        source_dir = Path(source_info["directory"])
        
        try:
            # Update status
            source_info["status"] = "processing"
            self.save_metadata()
            
            # Initialize data processor
            processor = WebDataProcessor(source_info["urls"], max_pages=max_pages)
            
            # Process documents
            documents = processor.process_all_pages()
            
            # Save processed data
            documents_file = source_dir / "documents.json"
            chunks_file = source_dir / "chunks.json"
            
            with open(documents_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, ensure_ascii=False)
            
            # Create chunks
            chunks = processor.chunk_documents()
            with open(chunks_file, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            # Create vector store
            vector_store = VectorStore(persist_directory=source_info["vector_store_path"])
            vector_store.add_documents(chunks)
            
            # Update metadata
            source_info.update({
                "status": "completed",
                "last_updated": datetime.now().isoformat(),
                "document_count": len(documents),
                "chunk_count": len(chunks),
                "documents_file": str(documents_file),
                "chunks_file": str(chunks_file)
            })
            
            self.save_metadata()
            
            return source_info
            
        except Exception as e:
            # Update status on error
            source_info["status"] = "error"
            source_info["error"] = str(e)
            self.save_metadata()
            raise e
    
    def get_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """Get all data sources."""
        return self.metadata["sources"]
    
    def get_data_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific data source."""
        return self.metadata["sources"].get(source_id)
    
    def set_current_source(self, source_id: str):
        """Set the current active data source."""
        if source_id in self.metadata["sources"]:
            self.metadata["current_source"] = source_id
            self.save_metadata()
        else:
            raise ValueError(f"Data source {source_id} not found")
    
    def get_current_source(self) -> Optional[Dict[str, Any]]:
        """Get the current active data source."""
        current_id = self.metadata.get("current_source")
        if current_id and current_id in self.metadata["sources"]:
            return self.metadata["sources"][current_id]
        return None
    
    def delete_data_source(self, source_id: str):
        """Delete a data source and its files."""
        if source_id not in self.metadata["sources"]:
            raise ValueError(f"Data source {source_id} not found")
        
        source_info = self.metadata["sources"][source_id]
        source_dir = Path(source_info["directory"])
        
        # Remove files
        try:
            import shutil
            if source_dir.exists():
                shutil.rmtree(source_dir)
        except Exception as e:
            logger.error(f"Error deleting source directory: {e}")
        
        # Remove from metadata
        del self.metadata["sources"][source_id]
        
        # Clear current source if it was this one
        if self.metadata.get("current_source") == source_id:
            self.metadata["current_source"] = None
        
        self.save_metadata()
    
    def get_vector_store(self, source_id: str = None) -> Optional[VectorStore]:
        """Get vector store for a data source."""
        if source_id is None:
            source_info = self.get_current_source()
        else:
            source_info = self.get_data_source(source_id)
        
        if not source_info or source_info["status"] != "completed":
            return None
        
        try:
            return VectorStore(persist_directory=source_info["vector_store_path"])
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return None
    
    def refresh_data_source(self, source_id: str, max_pages: int = 50) -> Dict[str, Any]:
        """Refresh/update an existing data source."""
        if source_id not in self.metadata["sources"]:
            raise ValueError(f"Data source {source_id} not found")
        
        # Mark as processing and re-process
        source_info = self.metadata["sources"][source_id]
        source_info["status"] = "refreshing"
        self.save_metadata()
        
        return self.process_data_source(source_id, max_pages)
    
    def get_source_stats(self) -> Dict[str, Any]:
        """Get statistics about all data sources."""
        sources = self.metadata["sources"]
        stats = {
            "total_sources": len(sources),
            "completed_sources": len([s for s in sources.values() if s["status"] == "completed"]),
            "processing_sources": len([s for s in sources.values() if s["status"] in ["creating", "processing", "refreshing"]]),
            "error_sources": len([s for s in sources.values() if s["status"] == "error"]),
            "total_documents": sum(s.get("document_count", 0) for s in sources.values()),
            "total_chunks": sum(s.get("chunk_count", 0) for s in sources.values()),
            "current_source": self.metadata.get("current_source")
        }
        return stats

# URL validation and preprocessing utilities
def validate_and_clean_urls(urls: List[str]) -> List[str]:
    """Validate and clean a list of URLs."""
    import re
    from urllib.parse import urlparse
    
    clean_urls = []
    for url in urls:
        url = url.strip()
        if not url:
            continue
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                continue
            clean_urls.append(url)
        except Exception:
            continue
    
    return clean_urls

def extract_domain_from_urls(urls: List[str]) -> str:
    """Extract primary domain from URLs for naming."""
    from urllib.parse import urlparse
    
    domains = []
    for url in urls:
        try:
            domain = urlparse(url).netloc
            if domain:
                domains.append(domain)
        except Exception:
            continue
    
    if domains:
        # Get most common domain
        from collections import Counter
        most_common = Counter(domains).most_common(1)[0][0]
        return most_common.replace('www.', '').replace('.com', '')
    
    return "unknown"
