"""
Data Persistence Manager for GitLab AI Chatbot
Ensures all data (caches, vector store, scraped content) persists across app restarts.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import streamlit as st
from pathlib import Path

logger = logging.getLogger(__name__)

class DataPersistenceManager:
    """
    Manages persistent storage and loading of all chatbot data.
    Ensures the app starts with pre-existing caches and data.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Data file paths
        self.app_state_file = self.data_dir / "app_state.json"
        self.performance_file = self.data_dir / "performance_metrics.json"
        self.user_sessions_file = self.data_dir / "user_sessions.json"
        
        # Initialize app state
        self.app_state = self._load_app_state()
        
        logger.info(f"Data persistence manager initialized: {self.data_dir}")
    
    def _load_app_state(self) -> Dict[str, Any]:
        """Load application state from disk."""
        try:
            if self.app_state_file.exists():
                with open(self.app_state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    logger.info("Loaded app state from disk")
                    return state
        except Exception as e:
            logger.warning(f"Could not load app state: {e}")
        
        # Default state
        return {
            'app_version': '1.0.0',
            'first_startup': datetime.now().isoformat(),
            'last_startup': datetime.now().isoformat(),
            'total_sessions': 0,
            'total_queries': 0,
            'data_sources_loaded': False,
            'cache_initialized': False,
            'performance_monitoring_enabled': True
        }
    
    def save_app_state(self, updates: Dict[str, Any] = None):
        """Save application state to disk."""
        try:
            if updates:
                self.app_state.update(updates)
            
            self.app_state['last_startup'] = datetime.now().isoformat()
            
            with open(self.app_state_file, 'w', encoding='utf-8') as f:
                json.dump(self.app_state, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Could not save app state: {e}")
    
    def ensure_data_sources_exist(self) -> bool:
        """Ensure all required data sources exist."""
        required_files = [
            self.data_dir / "documents.json",
            self.data_dir / "chunks.json",
            self.data_dir / "chroma_db" / "chroma.sqlite3"
        ]
        
        missing_files = [f for f in required_files if not f.exists()]
        
        if missing_files:
            logger.warning(f"Missing data files: {[str(f) for f in missing_files]}")
            return False
        
        return True
    
    def preload_all_data(self) -> Dict[str, Any]:
        """
        Preload all persistent data for immediate app startup.
        Returns status of data loading.
        """
        start_time = time.time()
        status = {
            'data_sources': False,
            'caches': False,
            'performance_data': False,
            'load_time': 0.0,
            'errors': []
        }
        
        try:
            # Check data sources
            if self.ensure_data_sources_exist():
                status['data_sources'] = True
                logger.info("✅ Data sources verified")
            else:
                status['errors'].append("Missing core data files")
                logger.warning("❌ Some data sources missing")
            
            # Verify cache files exist
            cache_files = [
                self.data_dir / "semantic_cache.json",
                self.data_dir / "response_cache.json"
            ]
            
            cache_status = []
            for cache_file in cache_files:
                if cache_file.exists():
                    try:
                        with open(cache_file, 'r') as f:
                            cache_data = json.load(f)
                            cache_size = len(cache_data.get('cache', {}))
                            cache_status.append(f"{cache_file.name}: {cache_size} entries")
                    except:
                        cache_status.append(f"{cache_file.name}: error loading")
                else:
                    cache_status.append(f"{cache_file.name}: not found")
            
            if cache_status:
                status['caches'] = True
                logger.info(f"✅ Cache status: {', '.join(cache_status)}")
            
            # Load performance data
            if self.performance_file.exists():
                status['performance_data'] = True
                logger.info("✅ Performance data available")
            
            status['load_time'] = time.time() - start_time
            
            # Update app state
            self.save_app_state({
                'data_sources_loaded': status['data_sources'],
                'cache_initialized': status['caches'],
                'last_data_check': datetime.now().isoformat()
            })
            
            logger.info(f"Data preload completed in {status['load_time']:.2f}s")
            
        except Exception as e:
            status['errors'].append(str(e))
            logger.error(f"Error during data preload: {e}")
        
        return status
    
    def get_data_status(self) -> Dict[str, Any]:
        """Get comprehensive data status for dashboard."""
        try:
            # Check file sizes and modification times
            data_info = {}
            
            for file_pattern in ['*.json', 'chroma_db/*']:
                for file_path in self.data_dir.glob(file_pattern):
                    if file_path.is_file():
                        stat = file_path.stat()
                        data_info[file_path.name] = {
                            'size_mb': round(stat.st_size / 1024 / 1024, 2),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'exists': True
                        }
            
            # Cache statistics
            cache_stats = {}
            cache_files = ['semantic_cache.json', 'response_cache.json']
            
            for cache_file in cache_files:
                cache_path = self.data_dir / cache_file
                if cache_path.exists():
                    try:
                        with open(cache_path, 'r') as f:
                            cache_data = json.load(f)
                            cache_stats[cache_file] = {
                                'entries': len(cache_data.get('cache', {})),
                                'last_updated': cache_data.get('last_updated', 'unknown'),
                                'status': 'active'
                            }
                    except:
                        cache_stats[cache_file] = {'status': 'error'}
                else:
                    cache_stats[cache_file] = {'status': 'missing'}
            
            return {
                'app_state': self.app_state,
                'data_files': data_info,
                'cache_status': cache_stats,
                'data_directory': str(self.data_dir),
                'total_size_mb': sum(info.get('size_mb', 0) for info in data_info.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting data status: {e}")
            return {'error': str(e)}
    
    def cleanup_old_data(self, days_old: int = 30):
        """Clean up old data files and cache entries."""
        try:
            current_time = datetime.now()
            cleaned_files = []
            
            # Clean up old log files, temp files, etc.
            for file_pattern in ['*.log', '*.tmp', '*_backup_*']:
                for file_path in self.data_dir.glob(file_pattern):
                    if file_path.is_file():
                        file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if (current_time - file_age).days > days_old:
                            file_path.unlink()
                            cleaned_files.append(str(file_path))
            
            if cleaned_files:
                logger.info(f"Cleaned up {len(cleaned_files)} old files")
            
            return cleaned_files
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return []
    
    def export_data_backup(self) -> str:
        """Export all data as a backup file."""
        try:
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'app_state': self.app_state,
                'data_status': self.get_data_status()
            }
            
            backup_file = self.data_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data backup created: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return ""

# Streamlit cached singleton
@st.cache_resource
def get_persistence_manager() -> DataPersistenceManager:
    """Get singleton persistence manager instance."""
    return DataPersistenceManager()

def display_data_status_dashboard():
    """Display data status in Streamlit sidebar."""
    try:
        persistence_manager = get_persistence_manager()
        data_status = persistence_manager.get_data_status()
        
        st.sidebar.markdown("### Data Status")
        
        # Overall status
        app_state = data_status.get('app_state', {})
        
        if app_state.get('data_sources_loaded', False):
            st.sidebar.success("Data sources loaded")
        else:
            st.sidebar.warning("Data sources need verification")
        
        if app_state.get('cache_initialized', False):
            st.sidebar.success("Caches initialized")
        else:
            st.sidebar.info("Caches will be built on first use")
        
        # Data size info
        total_size = data_status.get('total_size_mb', 0)
        st.sidebar.metric("Total Data Size", f"{total_size:.1f} MB")
        
        # Cache status
        cache_status = data_status.get('cache_status', {})
        
        with st.sidebar.expander("Cache Details"):
            for cache_name, cache_info in cache_status.items():
                if cache_info.get('status') == 'active':
                    st.write(f"**{cache_name}**: {cache_info.get('entries', 0)} entries")
                else:
                    st.write(f"**{cache_name}**: {cache_info.get('status', 'unknown')}")
        
        # App statistics
        with st.sidebar.expander("App Statistics"):
            st.write(f"**Total Sessions**: {app_state.get('total_sessions', 0)}")
            st.write(f"**Total Queries**: {app_state.get('total_queries', 0)}")
            
            last_startup = app_state.get('last_startup', 'unknown')
            if last_startup != 'unknown':
                try:
                    startup_time = datetime.fromisoformat(last_startup)
                    st.write(f"**Last Startup**: {startup_time.strftime('%Y-%m-%d %H:%M')}")
                except:
                    st.write(f"**Last Startup**: {last_startup}")
        
    except Exception as e:
        st.sidebar.error(f"Error displaying data status: {e}")

def initialize_persistent_data():
    """
    Initialize all persistent data on app startup.
    Call this early in your Streamlit app.
    """
    try:
        persistence_manager = get_persistence_manager()
        
        # Show loading indicator
        with st.spinner("Loading persistent data..."):
            preload_status = persistence_manager.preload_all_data()
        
        # Update session count
        if 'session_initialized' not in st.session_state:
            current_sessions = persistence_manager.app_state.get('total_sessions', 0)
            persistence_manager.save_app_state({'total_sessions': current_sessions + 1})
            st.session_state.session_initialized = True
        
        return preload_status
        
    except Exception as e:
        logger.error(f"Error initializing persistent data: {e}")
        return {'error': str(e)}
