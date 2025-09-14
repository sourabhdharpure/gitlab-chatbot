"""
Core chatbot implementation with LLM integration and conversation management.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import google.generativeai as genai
import openai
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
    
    def __init__(self, vector_store: VectorStore, api_key: str, model_type: str = "gemini"):
        """
        Initialize the chatbot.
        
        Args:
            vector_store: Vector store for document retrieval
            api_key: API key for the LLM
            model_type: Type of model ('gemini' or 'openai')
        """
        self.vector_store = vector_store
        self.retriever = AdvancedRetriever(vector_store)
        self.memory = ConversationMemory()
        self.model_type = model_type
        
        # Configure LLM
        if model_type == "gemini":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        elif model_type == "openai":
            openai.api_key = api_key
            self.model_name = "gpt-3.5-turbo"
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        logger.info(f"Initialized GitLab chatbot with {model_type} model")
    
    def create_prompt(self, query: str, context_docs: List[Dict], conversation_context: str = "") -> str:
        """Create a comprehensive prompt for the LLM."""
        
        # Enhanced system prompt with persistent GitLab context
        system_prompt = """You are GitLab's AI Assistant, an expert on GitLab's company culture, practices, policies, and procedures. 

CRITICAL: Always assume the user is asking about GitLab unless explicitly stated otherwise. Treat all queries as GitLab-related and provide GitLab-specific context in your responses.

Guidelines:
1. Answer questions directly and naturally, as if you're a knowledgeable GitLab team member
2. Give confident, complete answers about GitLab without mentioning sources or documentation
3. Never reference "handbook," "documentation," "pages," "sources," or "provided information"
4. Don't mention where information comes from - just state facts about GitLab
5. Focus on what GitLab does, believes, and practices in a conversational way
6. Use specific GitLab examples and practices naturally in your explanations
7. For ambiguous queries, interpret them in the context of GitLab's products, culture, or processes
8. Present information as your knowledge about GitLab, not as sourced material
9. Always maintain GitLab context - if a question could relate to GitLab, answer it as such

Your role: Share knowledge about GitLab in a natural, conversational way, always maintaining GitLab context."""

        # Format context documents (hidden from user)
        context_text = ""
        if context_docs:
            context_text = "\n\nGitLab Information:\n"
            for i, doc in enumerate(context_docs, 1):
                content = doc['content'][:800]  # Limit content length
                context_text += f"\n{content}...\n"
        
        # Include conversation context
        conversation_part = ""
        if conversation_context:
            conversation_part = f"\n\nPrevious conversation:\n{conversation_context}\n"
        
        # Final prompt
        prompt = f"""{system_prompt}
{context_text}
{conversation_part}

User Question: {query}

Answer naturally and conversationally about GitLab. Don't mention any sources, documentation, or where information comes from. Just share your knowledge about GitLab as if you're explaining to a colleague."""

        return prompt
    
    def generate_response_gemini(self, prompt: str) -> str:
        """Generate response using Gemini."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def generate_response_openai(self, prompt: str) -> str:
        """Generate response using OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
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
    
    def chat(self, query: str, use_context: bool = True) -> Tuple[str, List[Dict]]:
        """
        Main chat function with enhanced GitLab context enforcement.
        
        Args:
            query: User query
            use_context: Whether to use conversation context
            
        Returns:
            Tuple of (response, source_documents)
        """
        logger.info(f"Processing query: {query}")
        
        # Enhanced GitLab context enforcement
        # Always assume GitLab context and rewrite query if needed
        processed_query = self._enhance_query_for_gitlab_context(query)
        
        # Check if we should redirect to GitLab context
        if self._should_redirect_to_gitlab(query):
            response = self._get_gitlab_redirect_response(query)
            self.memory.add_message("user", query)
            self.memory.add_message("assistant", response)
            return response, []
        
        # Retrieve relevant documents using processed query
        try:
            context_docs = self.retriever.retrieve_with_reranking(processed_query, final_results=3)
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            context_docs = []
        
        # Get conversation context
        conversation_context = self.memory.get_context() if use_context else ""
        
        # Create prompt with enhanced GitLab context
        prompt = self.create_prompt(processed_query, context_docs, conversation_context)
        
        # Generate response
        if self.model_type == "gemini":
            response = self.generate_response_gemini(prompt)
        else:
            response = self.generate_response_openai(prompt)
        
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
        
        logger.info(f"Generated response with {len(context_docs)} source documents")
        return response, formatted_sources
    
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

def create_chatbot_from_config(config_path: str = "config.json") -> GitLabChatbot:
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
    if config['model_type'] == "gemini":
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
    else:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Initialize vector store
    vector_store = VectorStore(persist_directory=config['vector_store_path'])
    
    # Create chatbot
    chatbot = GitLabChatbot(
        vector_store=vector_store,
        api_key=api_key,
        model_type=config['model_type']
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
            response, sources = chatbot.chat(query)
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
