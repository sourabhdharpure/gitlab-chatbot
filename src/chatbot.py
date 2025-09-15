"""
Core chatbot implementation with LLM integration and conversation management.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import google.generativeai as genai
from dataclasses import dataclass
import re

try:
    from .vector_store import VectorStore, AdvancedRetriever
except ImportError:
    from vector_store import VectorStore, AdvancedRetriever

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    sources: Optional[List[Dict]] = None

class ConversationMemory:
    """Manages conversation history and context."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.messages: List[ChatMessage] = []
        self.context_summary = ""
    
    def add_message(self, role: str, content: str, sources: Optional[List[Dict]] = None):
        """Add a message to conversation history."""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            sources=sources
        )
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_context(self) -> str:
        """Get formatted conversation context."""
        if not self.messages:
            return ""
        
        context_parts = []
        for message in self.messages[-5:]:  # Last 5 messages
            context_parts.append(f"{message.role.title()}: {message.content}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear conversation history."""
        self.messages = []
        self.context_summary = ""

class GitLabChatbot:
    """Main chatbot class with LLM integration."""
    
    def __init__(self, vector_store: VectorStore, api_key: str, model_type: str = "gemini", cache_manager=None):
        """
        Initialize the chatbot.
        
        Args:
            vector_store: Vector store for document retrieval
            api_key: API key for the LLM
            model_type: Type of model ('gemini' or 'openai')
            cache_manager: Cache manager for response caching
        """
        self.vector_store = vector_store
        self.retriever = AdvancedRetriever(vector_store)
        self.memory = ConversationMemory()
        self.model_type = model_type
        self.cache_manager = cache_manager
        
        # Production settings
        self.max_query_length = 500
        self.request_count = 0
        self.last_request_time = 0
        
        # Response templates for common questions (reduces API calls)
        self.response_templates = {
            "gitlab_overview": "GitLab is a complete DevOps platform that provides a single application for the entire software development lifecycle. We're a fully remote company with team members in over 65 countries. GitLab offers source code management, CI/CD, security scanning, project management, and more - all in one platform. Our core values are Results, Efficiency, Diversity, Iteration, and Transparency.",
            "gitlab_values": "GitLab's core values are Results, Efficiency, Diversity, Iteration, and Transparency. These values guide everything we do, from how we work remotely to how we develop software. We believe in results over hours worked, efficiency through automation, diversity in all forms, iteration over perfection, and transparency in everything we do.",
            "remote_work": "GitLab is a fully remote company with team members in over 65 countries. We believe in asynchronous communication, transparency, and results-oriented work. Our remote work culture emphasizes trust, clear documentation, and making work visible to everyone. We use GitLab itself for most of our work processes.",
            "ci_cd_basics": "GitLab CI/CD is our built-in continuous integration and deployment tool. It uses YAML configuration files (.gitlab-ci.yml) to define pipelines that automatically build, test, and deploy your code. Pipelines run in stages (build, test, deploy) and can be triggered by commits, merge requests, or schedules.",
            "hiring_process": "GitLab's hiring process is designed to be transparent and efficient. We use structured interviews, work samples, and cultural fit assessments. The process typically includes a phone screen, technical interview, and final interview with the hiring manager. We value diversity and inclusion in all our hiring decisions.",
            "company_culture": "GitLab's culture is built on our values and our all-remote work model. We emphasize transparency, iteration, and results. Our handbook is public, our meetings are recorded, and we share our learnings openly. We believe in working asynchronously and making work visible to everyone."
        }
        
        # Configure LLM (Gemini only) - using faster model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash', 
                                         generation_config=genai.types.GenerationConfig(
                                             max_output_tokens=256,  # Reduced from default
                                             temperature=0.7,        # Slightly more focused
                                             top_p=0.8,             # More focused responses
                                             top_k=20               # Limit vocabulary
                                         ))
        
        logger.info(f"Initialized GitLab chatbot with {model_type} model")
    
    def get_template_response(self, query: str) -> Optional[str]:
        """Check if query matches a common template to avoid API calls."""
        query_lower = query.lower().strip()
        
        # Check for basic "what is gitlab" questions FIRST (most common)
        if any(phrase in query_lower for phrase in [
            'what is gitlab', 'what is git lab', 'tell me about gitlab', 
            'explain gitlab', 'describe gitlab', 'gitlab overview',
            'what does gitlab do', 'gitlab company', 'about gitlab'
        ]):
            return self.response_templates["gitlab_overview"]
        
        # Check for values/culture questions
        elif any(word in query_lower for word in ['values', 'culture', 'principles', 'what does gitlab believe']):
            return self.response_templates["gitlab_values"]
        
        # Check for remote work questions
        elif any(word in query_lower for word in ['remote', 'work from home', 'distributed', 'async']):
            return self.response_templates["remote_work"]
        
        # Check for CI/CD questions
        elif any(word in query_lower for word in ['ci/cd', 'pipeline', 'continuous integration', 'deploy']):
            return self.response_templates["ci_cd_basics"]
        
        # Check for hiring questions
        elif any(word in query_lower for word in ['hiring', 'interview', 'recruitment', 'how to get hired']):
            return self.response_templates["hiring_process"]
        
        # Check for general culture questions
        elif any(word in query_lower for word in ['company culture', 'how does gitlab work', 'what makes gitlab different']):
            return self.response_templates["company_culture"]
        
        return None
    
    def create_prompt(self, query: str, context_docs: List[Dict], conversation_context: str = "") -> str:
        """Create a comprehensive prompt for the LLM."""
        
        # Ultra-short system prompt (30 tokens max)
        system_prompt = "You are GitLab's AI Assistant. Answer GitLab questions briefly."
        
        # Minimal context (100 chars max, 1 doc only)
        context_text = ""
        if context_docs:
            content = context_docs[0]['content'][:100]  # Only first doc, 100 chars max
            context_text = f"\nContext: {content}"
        
        # Ultra-short prompt (200 tokens total max)
        prompt = f"{system_prompt}{context_text}\nQ: {query}\nA:"

        return prompt
    
    def generate_response_gemini(self, prompt: str) -> tuple:
        """Generate response using Gemini and return response with token usage."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=512,  # Reduced from 1024 to 512
                )
            )
            
            # Extract token usage information
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0
            cost_usd = 0.0
            
            try:
                # Try to get token usage from response metadata
                if hasattr(response, 'usage_metadata'):
                    input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                    output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                    total_tokens = getattr(response.usage_metadata, 'total_token_count', 0)
                else:
                    # Estimate token usage if metadata not available
                    input_tokens = len(prompt.split()) * 1.3  # Rough estimation
                    output_tokens = len(response.text.split()) * 1.3
                    total_tokens = int(input_tokens + output_tokens)
                
                # Calculate cost based on Gemini pricing (as of 2024)
                # Input: $0.075 per 1K tokens, Output: $0.30 per 1K tokens
                cost_usd = (input_tokens * 0.000075 + output_tokens * 0.0003) / 1000
                
            except Exception as e:
                logger.warning(f"Could not extract token usage: {e}")
                # Fallback estimation
                input_tokens = len(prompt.split()) * 1.3
                output_tokens = len(response.text.split()) * 1.3
                total_tokens = int(input_tokens + output_tokens)
                cost_usd = (input_tokens * 0.000075 + output_tokens * 0.0003) / 1000
            
            return response.text, {
                'input_tokens': int(input_tokens),
                'output_tokens': int(output_tokens),
                'total_tokens': int(total_tokens),
                'cost_usd': cost_usd
            }
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again.", {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cost_usd': 0.0
            }
    
    
    def is_gitlab_related(self, query: str) -> bool:
        """Check if query is related to GitLab."""
        gitlab_keywords = [
            'gitlab', 'handbook', 'direction', 'remote', 'work',
            'code review', 'ci/cd', 'pipeline', 'merge request',
            'issue', 'epic', 'milestone', 'values', 'culture',
            'hiring', 'onboarding', 'process', 'policy', 'company',
            'public', 'stock', 'business', 'enterprise', 'organization'
        ]
        
        query_lower = query.lower()
        # Be more permissive for short queries or ones that could relate to GitLab as a company
        return any(keyword in query_lower for keyword in gitlab_keywords) or len(query.split()) <= 4
    
    def chat(self, query: str, use_context: bool = True) -> Tuple[str, List[Dict], Dict]:
        """
        Main chat function with enhanced GitLab context enforcement.
        
        Args:
            query: User query
            use_context: Whether to use conversation context
            
        Returns:
            Tuple of (response, source_documents, token_info)
        """
        logger.info(f"Processing query: {query}")
        
        # Input validation
        if not query or len(query.strip()) == 0:
            return "Please provide a valid question.", [], {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost_usd': 0.0}
        
        if len(query) > self.max_query_length:
            return f"Query too long. Please keep it under {self.max_query_length} characters.", [], {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost_usd': 0.0}
        
        # Basic rate limiting (simple implementation)
        import time
        current_time = time.time()
        if current_time - self.last_request_time < 0.1:  # 100ms between requests
            time.sleep(0.1)
        self.last_request_time = current_time
        self.request_count += 1
        
        # Check cache first (fastest path)
        if self.cache_manager:
            cached_response = self.cache_manager.get_cached_response(query)
            if cached_response:
                logger.info(f"Using cached response (type: {cached_response[3]})")
                token_info = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost_usd': 0.0}
                return cached_response[0], cached_response[1], token_info
        
        # Quick template response check for common questions (fast path)
        template_response = self.get_template_response(query)
        if template_response:
            logger.info("Using fast template response")
            # Store in cache for future use
            if self.cache_manager:
                self.cache_manager.store_response(query, template_response, [], {'type': 'template'})
            # Return immediately for speed
            token_info = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost_usd': 0.0}
            return template_response, [], token_info
        
        # Enhanced GitLab context enforcement
        # Always assume GitLab context and rewrite query if needed
        processed_query = self._enhance_query_for_gitlab_context(query)
        
        # Check if we should redirect to GitLab context
        if self._should_redirect_to_gitlab(query):
            response = self._get_gitlab_redirect_response(query)
            self.memory.add_message("user", query)
            self.memory.add_message("assistant", response)
            # Return empty token info for redirect responses
            token_info = {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cost_usd': 0.0
            }
            return response, [], token_info
        
        # Retrieve relevant documents using processed query (optimized for speed)
        try:
            context_docs = self.retriever.retrieve_with_reranking(processed_query, final_results=1)  # Only 1 doc for speed
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            context_docs = []
        
        # Get conversation context
        conversation_context = self.memory.get_context() if use_context else ""
        
        # Create prompt with enhanced GitLab context
        prompt = self.create_prompt(processed_query, context_docs, conversation_context)
        
        # Generate response using Gemini with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response, token_info = self.generate_response_gemini(prompt)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to generate response after {max_retries} attempts: {e}")
                    return "I apologize, but I'm having trouble processing your request right now. Please try again.", [], {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'cost_usd': 0.0}
                else:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(1)  # Wait before retry
        
        # Store in memory
        source_docs = [doc['metadata'] for doc in context_docs]
        self.memory.add_message("user", query)
        self.memory.add_message("assistant", response, source_docs)
        
        # Format sources for display
        formatted_sources = []
        for doc in context_docs:
            metadata = doc['metadata']
            formatted_sources.append({
                'title': metadata.get('title', 'Unknown Document'),
                'url': metadata.get('url', '#'),
                'source_url': metadata.get('url', '#')  # For compatibility
            })
        
        # Store in cache for future use
        if self.cache_manager:
            self.cache_manager.store_response(query, response, formatted_sources, {
                'type': 'ai_generated',
                'context_docs_count': len(context_docs),
                'token_info': token_info
            })
        
        logger.info(f"Generated response with {len(context_docs)} source documents")
        return response, formatted_sources, token_info
    
    def get_follow_up_suggestions(self, query: str, response: str) -> List[str]:
        """Generate follow-up question suggestions."""
        suggestions = []
        
        # General GitLab follow-ups
        general_suggestions = [
            "Can you tell me more about GitLab's remote work culture?",
            "How does GitLab handle performance reviews?",
            "What are GitLab's core values?",
            "How does the GitLab development process work?"
        ]
        
        # Query-specific suggestions
        query_lower = query.lower()
        if "remote" in query_lower or "work" in query_lower:
            suggestions.extend([
                "What tools does GitLab use for remote collaboration?",
                "How does GitLab onboard remote employees?"
            ])
        elif "code" in query_lower or "review" in query_lower:
            suggestions.extend([
                "What is GitLab's merge request process?",
                "How does GitLab ensure code quality?"
            ])
        elif "hiring" in query_lower or "interview" in query_lower:
            suggestions.extend([
                "What is GitLab's interview process like?",
                "How does GitLab evaluate candidates?"
            ])
        elif "values" in query_lower or "culture" in query_lower:
            suggestions.extend([
                "How does GitLab live its values in practice?",
                "What makes GitLab's culture unique?"
            ])
        
        # Combine and limit suggestions
        all_suggestions = suggestions + general_suggestions
        return list(set(all_suggestions))[:4]  # Remove duplicates and limit to 4
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.memory.clear()
        logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of current conversation."""
        return {
            'message_count': len(self.memory.messages),
            'last_update': self.memory.messages[-1].timestamp.isoformat() if self.memory.messages else None,
            'model_type': self.model_type
        }
    
    def _enhance_query_for_gitlab_context(self, query: str) -> str:
        """Enhance query to ensure GitLab context."""
        query_lower = query.lower().strip()
        
        # GitLab keywords that indicate clear GitLab context
        gitlab_keywords = [
            'gitlab', 'git', 'repository', 'repo', 'merge request', 'mr', 'pull request', 'pr',
            'ci', 'cd', 'pipeline', 'deploy', 'deployment', 'issue', 'bug', 'feature', 'task',
            'handbook', 'direction', 'culture', 'values', 'process', 'workflow', 'team',
            'code review', 'review', 'approval', 'branch', 'commit', 'push', 'clone',
            'fork', 'project', 'group', 'namespace', 'user', 'member', 'permission',
            'security', 'vulnerability', 'scan', 'audit', 'compliance', 'license',
            'documentation', 'wiki', 'pages', 'snippets', 'packages', 'registry',
            'container', 'docker', 'kubernetes', 'helm', 'terraform', 'monitoring',
            'observability', 'metrics', 'logging', 'alerting', 'incident', 'response',
            'sre', 'devops', 'platform', 'infrastructure', 'remote work', 'hiring',
            'interview', 'onboarding', 'performance', 'review', 'management'
        ]
        
        # Check if query already has GitLab context
        has_gitlab_context = any(keyword in query_lower for keyword in gitlab_keywords)
        
        if has_gitlab_context:
            return query
        
        # Check for ambiguous terms that could be GitLab-related
        ambiguous_terms = [
            'project management', 'team', 'workflow', 'process', 'security', 'compliance',
            'documentation', 'monitoring', 'deployment', 'pipeline', 'review', 'issue',
            'task', 'feature', 'bug', 'development', 'collaboration', 'communication',
            'remote', 'work', 'hiring', 'interview', 'onboarding', 'performance'
        ]
        
        has_ambiguous_terms = any(term in query_lower for term in ambiguous_terms)
        
        if has_ambiguous_terms:
            # Add GitLab context to ambiguous queries
            return f"Regarding GitLab, {query}"
        
        # For completely unrelated queries, add GitLab context
        return f"In the context of GitLab, {query}"
    
    def _should_redirect_to_gitlab(self, query: str) -> bool:
        """Determine if query should be redirected to GitLab context."""
        query_lower = query.lower().strip()
        
        # Very specific non-GitLab terms that should be redirected
        non_gitlab_terms = [
            'weather', 'news', 'sports', 'cooking', 'recipe', 'movie', 'music',
            'travel', 'shopping', 'finance', 'stock', 'crypto', 'bitcoin',
            'politics', 'election', 'covid', 'health', 'medical', 'fitness'
        ]
        
        # Check if query contains non-GitLab terms
        has_non_gitlab_terms = any(term in query_lower for term in non_gitlab_terms)
        
        # Check if query is very short and unclear
        is_very_short = len(query.split()) <= 2
        
        # Check if query is a greeting without context
        is_greeting = query_lower in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        
        return has_non_gitlab_terms or (is_very_short and not is_greeting)
    
    def _get_gitlab_redirect_response(self, query: str) -> str:
        """Get redirect response for non-GitLab queries."""
        return """I'm here to help with GitLab-related questions! I can assist you with:

• **GitLab's products and features** - CI/CD, project management, security, etc.
• **GitLab's culture and values** - remote work, transparency, iteration
• **GitLab's processes** - development workflow, code reviews, hiring
• **GitLab's best practices** - DevOps, security, collaboration

What would you like to know about GitLab?"""

def create_chatbot_from_config(config_path: str = "config.json", cache_manager=None) -> GitLabChatbot:
    """Create chatbot from configuration file."""
    # Default configuration
    default_config = {
        "model_type": "gemini",
        "vector_store_path": "data/chroma_db",
        "max_conversation_history": 10
    }
    
    # Load configuration if exists
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = default_config
    
    # Get API key from environment
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    # Initialize vector store
    vector_store = VectorStore(persist_directory=config['vector_store_path'])
    
    # Create chatbot with cache manager
    chatbot = GitLabChatbot(
        vector_store=vector_store,
        api_key=api_key,
        model_type=config['model_type'],
        cache_manager=cache_manager
    )
    
    return chatbot

def main():
    """Main function to test the chatbot."""
    # Test the chatbot
    try:
        chatbot = create_chatbot_from_config()
        
        test_queries = [
            "What are GitLab's core values?",
            "How does GitLab handle remote work?",
            "What is the code review process at GitLab?",
            "How does GitLab hire new employees?"
        ]
        
        for query in test_queries:
            print(f"\n🤖 User: {query}")
            response, sources, token_info = chatbot.chat(query)
            print(f"🤖 Assistant: {response}")
            
            if sources:
                print("\n📚 Sources:")
                for source in sources:
                    print(f"  - {source['metadata']['title']}")
            
            # Show follow-up suggestions
            suggestions = chatbot.get_follow_up_suggestions(query, response)
            if suggestions:
                print("\n💡 Suggested follow-up questions:")
                for suggestion in suggestions[:2]:
                    print(f"  - {suggestion}")
            
            print("-" * 80)
    
    except Exception as e:
        print(f"Error testing chatbot: {e}")
        print("Please ensure you have set up the vector store and API keys correctly.")

if __name__ == "__main__":
    main()
