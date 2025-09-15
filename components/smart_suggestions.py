"""
Smart Suggestions Component - Proactive engagement and context-aware recommendations
"""

import streamlit as st
import json
import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SmartSuggestions:
    """Handles proactive engagement and smart suggestions with clean UI."""
    
    def __init__(self):
        self.user_patterns = {}
        self.suggestion_history = []
        self.context_keywords = {
            'ci_cd': ['pipeline', 'deploy', 'ci/cd', 'continuous integration', 'continuous deployment'],
            'code_review': ['review', 'merge request', 'mr', 'pull request', 'pr', 'code review'],
            'remote_work': ['remote', 'work from home', 'distributed', 'async', 'collaboration'],
            'hiring': ['hiring', 'interview', 'recruitment', 'onboarding', 'candidate'],
            'security': ['security', 'vulnerability', 'scan', 'audit', 'compliance', 'sast', 'dast'],
            'devops': ['devops', 'infrastructure', 'monitoring', 'observability', 'sre'],
            'culture': ['values', 'culture', 'transparency', 'iteration', 'diversity', 'inclusion']
        }
        
        # GitLab-specific recommendations (shortened to 1-2 liners)
        self.recommendations = {
            'ci_cd': [
                "CI/CD best practices",
                "Pipeline optimization",
                "Deployment strategies",
                "CI/CD security"
            ],
            'code_review': [
                "Merge request guidelines",
                "Code review tips",
                "Reviewer strategies",
                "Quality checks"
            ],
            'remote_work': [
                "Remote work handbook",
                "Async communication",
                "Team collaboration",
                "Work-life balance"
            ],
            'hiring': [
                "Hiring process",
                "Interview tips",
                "Candidate evaluation",
                "Onboarding practices"
            ],
            'security': [
                "Security scanning",
                "Vulnerability management",
                "Compliance guidelines",
                "Secure coding"
            ],
            'devops': [
                "DevOps platform",
                "Infrastructure as Code",
                "Monitoring setup",
                "SRE practices"
            ],
            'culture': [
                "Core values",
                "Transparency principles",
                "Diversity initiatives",
                "Company culture"
            ]
        }
        
        # No CSS needed - handled by main app
    
    def _setup_suggestion_css(self):
        """CSS handled by main app - no setup needed."""
        pass
    
    def analyze_user_pattern(self, query: str, response: str) -> None:
        """Analyze user query patterns for predictive assistance."""
        if 'user_patterns' not in st.session_state:
            st.session_state.user_patterns = {}
        
        # Extract keywords from query
        query_lower = query.lower()
        detected_categories = []
        
        for category, keywords in self.context_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_categories.append(category)
        
        # Update user patterns
        for category in detected_categories:
            if category not in st.session_state.user_patterns:
                st.session_state.user_patterns[category] = {
                    'count': 0,
                    'last_accessed': None,
                    'related_queries': []
                }
            
            st.session_state.user_patterns[category]['count'] += 1
            st.session_state.user_patterns[category]['last_accessed'] = datetime.now().isoformat()
            st.session_state.user_patterns[category]['related_queries'].append(query)
    
    def get_context_aware_suggestions(self, query: str) -> List[str]:
        """Generate context-aware recommendations based on current query."""
        query_lower = query.lower()
        suggestions = []
        
        # Analyze current query context
        for category, keywords in self.context_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                suggestions.extend(self.recommendations[category][:2])  # Top 2 from each category
        
        # Add general GitLab suggestions
        general_suggestions = [
            "GitLab features",
            "Pricing plans",
            "Security features",
            "Integration capabilities"
        ]
        
        suggestions.extend(random.sample(general_suggestions, 2))
        
        # Remove duplicates and limit
        return list(set(suggestions))[:4]
    
    def get_predictive_assistance(self) -> List[str]:
        """Generate predictive assistance based on user patterns."""
        if 'user_patterns' not in st.session_state or not st.session_state.user_patterns:
            return []
            
        
        # Find most frequently accessed categories
        sorted_categories = sorted(
            st.session_state.user_patterns.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        suggestions = []
        for category, data in sorted_categories[:2]:  # Top 2 categories
            if data['count'] >= 2:  # Only suggest if user has shown interest
                suggestions.append(f"Since you're interested in {category.replace('_', ' ').title()}, you might want to explore:")
                suggestions.extend(self.recommendations[category][:2])
        
        return suggestions
    
    def get_smart_follow_ups(self, query: str, response: str) -> List[str]:
        """Generate smart follow-up questions using pure rule-based approach (no AI)."""
        # Use only rule-based suggestions for maximum performance
        return self._generate_enhanced_suggestions(query, response)
    
    # AI suggestions removed for maximum performance - using only rule-based approach
    
    def _generate_enhanced_suggestions(self, query: str, response: str) -> List[str]:
        """Fast rule-based suggestions with optimized context analysis."""
        query_lower = query.lower()
        follow_ups = []
        
        # Simplified and faster context matching
        if any(word in query_lower for word in ['ci', 'cd', 'pipeline', 'deploy', 'build', 'test']):
            follow_ups = [
                "How to optimize CI/CD performance?",
                "What security scanning features are available?",
                "How to set up automated deployments?"
            ]
        elif any(word in query_lower for word in ['review', 'merge', 'mr', 'pr', 'approval']):
            follow_ups = [
                "Code review best practices?",
                "How to automate quality checks?",
                "Merge request approval workflow?"
            ]
        elif any(word in query_lower for word in ['remote', 'work', 'team', 'collaboration', 'async']):
            follow_ups = [
                "GitLab's remote work policies?",
                "Async communication best practices?",
                "Team collaboration tools?"
            ]
        elif any(word in query_lower for word in ['hiring', 'interview', 'candidate', 'recruitment']):
            follow_ups = [
                "GitLab's interview process?",
                "Candidate evaluation methods?",
                "Onboarding best practices?"
            ]
        elif any(word in query_lower for word in ['security', 'vulnerability', 'scan', 'audit']):
            follow_ups = [
                "Security scanning capabilities?",
                "Vulnerability management process?",
                "Compliance requirements?"
            ]
        elif any(word in query_lower for word in ['devops', 'infrastructure', 'monitoring', 'sre']):
            follow_ups = [
                "DevOps platform features?",
                "Infrastructure as Code tools?",
                "Monitoring and observability?"
            ]
        elif any(word in query_lower for word in ['values', 'culture', 'transparency', 'diversity']):
            follow_ups = [
                "GitLab's core values?",
                "Transparency principles?",
                "Diversity and inclusion initiatives?"
            ]
        else:
            # General suggestions
            follow_ups = [
                "What makes GitLab different?",
                "Getting started with GitLab?",
                "GitLab's key features?"
            ]
        
        # Return 3 suggestions (already limited)
        return follow_ups[:3]
    
    def render_suggestions_sidebar(self) -> None:
        """Render smart suggestions in the sidebar."""
        with st.sidebar:
            st.markdown("### Smart Suggestions")
            
            # Context-aware suggestions
            if st.session_state.get('last_query'):
                st.markdown("**Based on your query:**")
                suggestions = self.get_context_aware_suggestions(st.session_state.last_query)
                for suggestion in suggestions:
                    if st.button(suggestion, key=f"context_{suggestion[:20]}"):
                        # Set the suggestion to be processed
                        st.session_state.suggestion_clicked = suggestion
                        st.rerun()
            else:
                # General suggestions when no last query
                st.markdown("**Try asking about:**")
                general_suggestions = [
                    "GitLab features",
                    "CI/CD best practices", 
                    "Remote work culture",
                    "Security features"
                ]
                for suggestion in general_suggestions:
                    if st.button(suggestion, key=f"general_{suggestion[:20]}"):
                        # Set the suggestion to be processed
                        st.session_state.suggestion_clicked = suggestion
                        st.rerun()
            
            # Predictive assistance
            predictive = self.get_predictive_assistance()
            if predictive:
                st.markdown("**You might also like:**")
                for suggestion in predictive:
                    st.info(suggestion)
    
    def render_follow_up_suggestions(self, query: str, response: str) -> None:
        """Render smart follow-up suggestions after a response."""
        # Cache suggestions to avoid regenerating them
        cache_key = f"suggestions_{hash(query)}_{hash(response[:100])}"
        
        if cache_key not in st.session_state:
            st.session_state[cache_key] = self.get_smart_follow_ups(query, response)
        
        follow_ups = st.session_state[cache_key]
        
        if follow_ups:
            st.markdown("**You might also ask:**")
            
            # Create responsive columns for follow-ups
            cols = st.columns(len(follow_ups))
            
            for i, follow_up in enumerate(follow_ups):
                with cols[i]:
                    # Create unique key using response content hash and timestamp to avoid duplicates
                    response_hash = hash(str(response)[:50])
                    timestamp = hash(str(datetime.now())) if 'datetime' in globals() else hash(str(i))
                    unique_key = f"followup_{response_hash}_{i}_{timestamp}"
                    
                    if st.button(follow_up, key=unique_key, use_container_width=True):
                        # Set the follow-up to be processed
                        st.session_state.suggestion_clicked = follow_up
                        # Force rerun to process the suggestion
                        st.rerun()
    
    def track_interaction(self, query: str, response: str, response_time: float) -> None:
        """Track user interactions for analytics."""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response_length': len(response),
            'response_time': response_time,
            'categories': []
        }
        
        # Categorize the interaction
        query_lower = query.lower()
        for category, keywords in self.context_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                interaction['categories'].append(category)
        
        # Store in session state
        if 'interaction_history' not in st.session_state:
            st.session_state.interaction_history = []
        
        st.session_state.interaction_history.append(interaction)
        
        # Keep only last 50 interactions
        if len(st.session_state.interaction_history) > 50:
            st.session_state.interaction_history = st.session_state.interaction_history[-50:]
        
        # Update patterns
        self.analyze_user_pattern(query, response)
    
    def get_user_insights(self) -> Dict:
        """Get insights about user behavior patterns."""
        if 'interaction_history' not in st.session_state:
            return {}
        
        history = st.session_state.interaction_history
        if not history:
            return {}
        
        # Calculate insights
        total_queries = len(history)
        avg_response_time = sum(h['response_time'] for h in history) / total_queries
        
        # Most common categories
        category_counts = {}
        for interaction in history:
            for category in interaction['categories']:
                category_counts[category] = category_counts.get(category, 0) + 1
        
        most_common_category = max(category_counts.items(), key=lambda x: x[1]) if category_counts else None
        
        return {
            'total_queries': total_queries,
            'avg_response_time': round(avg_response_time, 2),
            'most_common_category': most_common_category,
            'categories_used': list(category_counts.keys()),
            'recent_activity': history[-5:] if len(history) >= 5 else history
        }
