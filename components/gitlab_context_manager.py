"""
GitLab Context Manager - Enforces GitLab context and maintains conversation focus
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GitLabContextManager:
    """Manages GitLab context enforcement and conversation focus."""
    
    def __init__(self):
        self.gitlab_keywords = [
            'gitlab', 'git', 'repository', 'repo', 'merge request', 'mr', 'pull request', 'pr',
            'ci', 'cd', 'pipeline', 'deploy', 'deployment', 'issue', 'bug', 'feature', 'task',
            'handbook', 'direction', 'culture', 'values', 'process', 'workflow', 'team',
            'code review', 'review', 'approval', 'branch', 'commit', 'push', 'clone',
            'fork', 'project', 'group', 'namespace', 'user', 'member', 'permission',
            'security', 'vulnerability', 'scan', 'audit', 'compliance', 'license',
            'documentation', 'wiki', 'pages', 'snippets', 'snippets', 'packages',
            'registry', 'container', 'docker', 'kubernetes', 'helm', 'terraform',
            'monitoring', 'observability', 'metrics', 'logging', 'alerting',
            'incident', 'response', 'sre', 'devops', 'platform', 'infrastructure'
        ]
        
        self.gitlab_phrases = [
            'gitlab ci/cd', 'gitlab pipeline', 'gitlab workflow', 'gitlab process',
            'gitlab handbook', 'gitlab direction', 'gitlab culture', 'gitlab values',
            'gitlab team', 'gitlab project', 'gitlab group', 'gitlab user',
            'gitlab security', 'gitlab compliance', 'gitlab documentation'
        ]
        
        self.system_prompts = {
            'primary': """You are a GitLab AI Assistant focused exclusively on GitLab's products, culture, processes, and practices. Your expertise covers:

- GitLab Handbook, Direction, and company culture
- GitLab CI/CD pipelines, workflows, and DevOps practices  
- GitLab project management, issues, and merge requests
- GitLab security, compliance, and best practices
- GitLab platform features and capabilities
- GitLab team collaboration and communication

Always maintain GitLab context in your responses. If a question is ambiguous or off-topic, gently guide users back to GitLab-related topics.""",
            
            'context_reminder': """Given we are discussing GitLab, please answer the following question in the context of GitLab's products, processes, and culture:""",
            
            'clarification': """I'm here to assist you with GitLab-related questions. Could you please specify how I can help regarding GitLab's products, processes, or culture?""",
            
            'fallback': """Could you please specify your question about GitLab's procedures, features, or culture? I'm here to help with GitLab-related topics."""
        }
        
        self.conversation_context = {
            'is_gitlab_focused': True,
            'last_gitlab_topic': None,
            'conversation_history': [],
            'context_confidence': 1.0
        }
    
    def detect_gitlab_intent(self, query: str) -> Tuple[bool, float, str]:
        """
        Detect if a query is GitLab-related and determine confidence level.
        
        Returns:
            Tuple[is_gitlab_related, confidence_score, detected_topic]
        """
        query_lower = query.lower().strip()
        
        # Check for explicit GitLab mentions
        if 'gitlab' in query_lower:
            return True, 1.0, 'explicit_gitlab'
        
        # Check for GitLab-specific phrases
        for phrase in self.gitlab_phrases:
            if phrase in query_lower:
                return True, 0.9, 'gitlab_phrase'
        
        # Check for GitLab-related keywords
        keyword_matches = 0
        matched_keywords = []
        for keyword in self.gitlab_keywords:
            if keyword in query_lower:
                keyword_matches += 1
                matched_keywords.append(keyword)
        
        if keyword_matches >= 2:
            return True, 0.8, f'keywords: {", ".join(matched_keywords[:3])}'
        elif keyword_matches == 1:
            return True, 0.6, f'keyword: {matched_keywords[0]}'
        
        # Check conversation context
        if self.conversation_context['is_gitlab_focused']:
            return True, 0.5, 'conversation_context'
        
        # Check for ambiguous technical terms that could be GitLab-related
        ambiguous_terms = [
            'pipeline', 'deploy', 'repository', 'merge', 'review', 'issue',
            'project', 'team', 'workflow', 'process', 'security', 'compliance'
        ]
        
        ambiguous_matches = sum(1 for term in ambiguous_terms if term in query_lower)
        if ambiguous_matches >= 1:
            return True, 0.4, f'ambiguous_technical: {ambiguous_matches} terms'
        
        return False, 0.0, 'not_gitlab_related'
    
    def rewrite_query_for_gitlab_context(self, query: str) -> str:
        """Rewrite query to inject GitLab context when missing."""
        is_gitlab, confidence, topic = self.detect_gitlab_intent(query)
        
        if confidence >= 0.6:
            # Query already has good GitLab context
            return query
        
        if confidence >= 0.4:
            # Query has some GitLab context, enhance it
            return f"{self.system_prompts['context_reminder']}\n\n{query}"
        
        # Query lacks GitLab context, rewrite it
        if self.conversation_context['last_gitlab_topic']:
            return f"Regarding GitLab {self.conversation_context['last_gitlab_topic']}, {query}"
        else:
            return f"In the context of GitLab, {query}"
    
    def get_system_prompt(self, query: str) -> str:
        """Get appropriate system prompt based on query context."""
        is_gitlab, confidence, topic = self.detect_gitlab_intent(query)
        
        if confidence >= 0.6:
            return self.system_prompts['primary']
        elif confidence >= 0.4:
            return f"{self.system_prompts['primary']}\n\n{self.system_prompts['context_reminder']}"
        else:
            return f"{self.system_prompts['primary']}\n\n{self.system_prompts['clarification']}"
    
    def get_fallback_response(self, query: str) -> str:
        """Get fallback response for non-GitLab queries."""
        is_gitlab, confidence, topic = self.detect_gitlab_intent(query)
        
        if confidence >= 0.4:
            return f"I'd be happy to help with that in the context of GitLab. {self.system_prompts['context_reminder']}\n\n{query}"
        else:
            return self.system_prompts['fallback']
    
    def update_conversation_context(self, query: str, response: str):
        """Update conversation context based on query and response."""
        is_gitlab, confidence, topic = self.detect_gitlab_intent(query)
        
        # Update context confidence
        self.conversation_context['context_confidence'] = confidence
        
        # Update GitLab focus status
        if confidence >= 0.4:
            self.conversation_context['is_gitlab_focused'] = True
            if topic != 'conversation_context':
                self.conversation_context['last_gitlab_topic'] = topic
        else:
            self.conversation_context['is_gitlab_focused'] = False
        
        # Add to conversation history
        self.conversation_context['conversation_history'].append({
            'query': query,
            'response': response,
            'is_gitlab': is_gitlab,
            'confidence': confidence,
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 conversations
        if len(self.conversation_context['conversation_history']) > 10:
            self.conversation_context['conversation_history'] = self.conversation_context['conversation_history'][-10:]
    
    def get_context_summary(self) -> Dict:
        """Get current conversation context summary."""
        return {
            'is_gitlab_focused': self.conversation_context['is_gitlab_focused'],
            'context_confidence': self.conversation_context['context_confidence'],
            'last_topic': self.conversation_context['last_gitlab_topic'],
            'conversation_count': len(self.conversation_context['conversation_history']),
            'recent_topics': [conv['topic'] for conv in self.conversation_context['conversation_history'][-3:]]
        }
    
    def should_redirect_to_gitlab(self, query: str) -> bool:
        """Determine if query should be redirected to GitLab context."""
        is_gitlab, confidence, topic = self.detect_gitlab_intent(query)
        return confidence < 0.3 and not self.conversation_context['is_gitlab_focused']
    
    def get_redirect_prompt(self, query: str) -> str:
        """Get redirect prompt for non-GitLab queries."""
        if self.conversation_context['last_gitlab_topic']:
            return f"I notice you're asking about something outside of GitLab context. Since we've been discussing GitLab {self.conversation_context['last_gitlab_topic']}, would you like to ask about that instead? Or if you have a GitLab-related question, I'd be happy to help!"
        else:
            return self.system_prompts['clarification']
