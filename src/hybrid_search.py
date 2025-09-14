"""
Hybrid Search Engine for GitLab AI Chatbot
Combines semantic vector search with keyword-based search for optimal retrieval accuracy.
Implements query routing, rewriting, and reranking for production-grade performance.
"""

import os
import re
import json
import time
import logging
from typing import List, Dict, Optional, Tuple, Any, Set
from dataclasses import dataclass
from collections import Counter
import math

# NLP and search imports
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("Warning: Vector search libraries not available")

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Enhanced search result with scoring and metadata."""
    content: str
    source_url: str
    relevance_score: float
    keyword_score: float
    semantic_score: float
    combined_score: float
    chunk_id: str
    metadata: Dict[str, Any]

@dataclass
class QueryAnalysis:
    """Analysis of user query for optimization."""
    original_query: str
    cleaned_query: str
    keywords: List[str]
    entities: List[str]
    query_type: str  # 'factual', 'procedural', 'comparison', 'list'
    needs_expansion: bool
    suggested_expansions: List[str]

class KeywordSearchEngine:
    """
    Fast keyword-based search using TF-IDF and Boolean matching.
    Provides exact term matching and phrase detection.
    """
    
    def __init__(self, documents: List[Dict]):
        self.documents = documents
        self.doc_vectors = {}
        self.vocabulary = set()
        self.idf_scores = {}
        self._build_index()
    
    def _build_index(self):
        """Build TF-IDF index for keyword search."""
        try:
            # Build vocabulary and document frequency
            doc_freq = Counter()
            all_terms = []
            
            for i, doc in enumerate(self.documents):
                content = doc.get('content', '').lower()
                terms = self._extract_terms(content)
                all_terms.append(terms)
                
                # Count unique terms per document
                unique_terms = set(terms)
                for term in unique_terms:
                    doc_freq[term] += 1
                self.vocabulary.update(unique_terms)
            
            # Calculate IDF scores
            total_docs = len(self.documents)
            for term in self.vocabulary:
                self.idf_scores[term] = math.log(total_docs / (doc_freq[term] + 1))
            
            # Build TF-IDF vectors for each document
            for i, terms in enumerate(all_terms):
                self.doc_vectors[i] = self._calculate_tf_idf(terms)
                
            logger.info(f"Built keyword index with {len(self.vocabulary)} terms")
            
        except Exception as e:
            logger.error(f"Error building keyword index: {e}")
            self.doc_vectors = {}
            self.vocabulary = set()
    
    def _extract_terms(self, text: str) -> List[str]:
        """Extract searchable terms from text."""
        # Remove special characters and split
        text = re.sub(r'[^\w\s-]', ' ', text.lower())
        terms = text.split()
        
        # Filter terms (remove very short/long terms)
        terms = [term for term in terms if 2 <= len(term) <= 50]
        
        return terms
    
    def _calculate_tf_idf(self, terms: List[str]) -> Dict[str, float]:
        """Calculate TF-IDF vector for a document."""
        term_freq = Counter(terms)
        total_terms = len(terms)
        
        tf_idf = {}
        for term, freq in term_freq.items():
            tf = freq / total_terms
            idf = self.idf_scores.get(term, 0)
            tf_idf[term] = tf * idf
        
        return tf_idf
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Search using keyword matching with TF-IDF scoring.
        Returns list of (document_index, score) tuples.
        """
        try:
            query_terms = self._extract_terms(query.lower())
            if not query_terms:
                return []
            
            query_vector = self._calculate_tf_idf(query_terms)
            
            # Calculate similarity scores
            scores = []
            for doc_id, doc_vector in self.doc_vectors.items():
                score = self._cosine_similarity(query_vector, doc_vector)
                if score > 0:
                    scores.append((doc_id, score))
            
            # Sort by score and return top results
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[:top_k]
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two TF-IDF vectors."""
        intersection = set(vec1.keys()) & set(vec2.keys())
        if not intersection:
            return 0.0
        
        numerator = sum(vec1[term] * vec2[term] for term in intersection)
        
        sum1 = sum(val**2 for val in vec1.values())
        sum2 = sum(val**2 for val in vec2.values())
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        
        return numerator / denominator if denominator > 0 else 0.0

class QueryOptimizer:
    """
    Query analysis and optimization for better search results.
    Handles query rewriting, expansion, and routing.
    """
    
    def __init__(self):
        self.gitlab_terms = {
            'values': ['principles', 'ethos', 'culture', 'beliefs'],
            'collaboration': ['teamwork', 'cooperation', 'working together'],
            'transparency': ['openness', 'visibility', 'clear communication'],
            'iteration': ['improvement', 'incremental', 'agile'],
            'efficiency': ['productivity', 'performance', 'optimization'],
            'diversity': ['inclusion', 'belonging', 'equity'],
            'results': ['outcomes', 'achievements', 'deliverables']
        }
        
        self.query_patterns = {
            'definition': r'\b(what is|define|meaning|definition)\b',
            'process': r'\b(how to|process|procedure|steps|workflow)\b',
            'comparison': r'\b(compare|difference|versus|vs|better)\b',
            'list': r'\b(list|examples|types|kinds|categories)\b'
        }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze and optimize user query."""
        try:
            cleaned_query = self._clean_query(query)
            keywords = self._extract_keywords(cleaned_query)
            entities = self._extract_entities(cleaned_query)
            query_type = self._classify_query_type(cleaned_query)
            
            needs_expansion = len(keywords) < 3 or len(cleaned_query.split()) < 4
            suggested_expansions = self._generate_expansions(cleaned_query, keywords)
            
            return QueryAnalysis(
                original_query=query,
                cleaned_query=cleaned_query,
                keywords=keywords,
                entities=entities,
                query_type=query_type,
                needs_expansion=needs_expansion,
                suggested_expansions=suggested_expansions
            )
            
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return QueryAnalysis(
                original_query=query,
                cleaned_query=query,
                keywords=[query],
                entities=[],
                query_type='factual',
                needs_expansion=False,
                suggested_expansions=[]
            )
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize query text."""
        # Remove extra whitespace and normalize
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Convert to lowercase for processing (preserve original case for display)
        return query
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query."""
        # Simple keyword extraction - can be enhanced with NLP
        stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'can', 'to', 'of', 'in', 'on', 'at',
                     'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
                     'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out',
                     'off', 'over', 'under', 'again', 'further', 'then', 'once'}
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract GitLab-specific entities."""
        entities = []
        query_lower = query.lower()
        
        # Look for GitLab-specific terms
        gitlab_entities = ['gitlab', 'handbook', 'direction', 'company', 'team', 'remote',
                          'values', 'culture', 'hiring', 'onboarding', 'development']
        
        for entity in gitlab_entities:
            if entity in query_lower:
                entities.append(entity)
        
        return entities
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query for targeted processing."""
        query_lower = query.lower()
        
        for query_type, pattern in self.query_patterns.items():
            if re.search(pattern, query_lower):
                return query_type
        
        return 'factual'  # Default type
    
    def _generate_expansions(self, query: str, keywords: List[str]) -> List[str]:
        """Generate query expansions using synonyms and related terms."""
        expansions = []
        query_lower = query.lower()
        
        # Add synonym-based expansions
        for keyword in keywords:
            for main_term, synonyms in self.gitlab_terms.items():
                if keyword in synonyms or keyword == main_term:
                    # Add alternative phrasings
                    for synonym in synonyms:
                        if synonym not in query_lower:
                            expanded = query + " " + synonym
                            expansions.append(expanded)
                    break
        
        # Add context-specific expansions
        if 'gitlab' not in query_lower:
            expansions.append(f"GitLab {query}")
        
        return expansions[:3]  # Limit to top 3 expansions

class HybridSearchEngine:
    """
    Advanced hybrid search engine combining semantic and keyword search.
    Implements reranking and query optimization for optimal results.
    """
    
    def __init__(self, vector_store, documents: List[Dict]):
        self.vector_store = vector_store
        self.documents = documents
        self.keyword_engine = KeywordSearchEngine(documents)
        self.query_optimizer = QueryOptimizer()
        
        # Search weights (can be tuned based on performance)
        self.semantic_weight = 0.7
        self.keyword_weight = 0.3
        
        # Performance tracking
        self.search_stats = {
            'total_searches': 0,
            'semantic_searches': 0,
            'keyword_searches': 0,
            'hybrid_searches': 0,
            'avg_response_time': 0.0
        }
    
    def search(self, query: str, top_k: int = 5, use_hybrid: bool = True) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic and keyword approaches.
        """
        start_time = time.time()
        self.search_stats['total_searches'] += 1
        
        try:
            # Analyze query for optimization
            query_analysis = self.query_optimizer.analyze_query(query)
            
            if use_hybrid:
                results = self._hybrid_search(query_analysis, top_k)
                self.search_stats['hybrid_searches'] += 1
            else:
                # Fallback to semantic search only
                results = self._semantic_search_only(query, top_k)
                self.search_stats['semantic_searches'] += 1
            
            # Track performance
            response_time = time.time() - start_time
            self._update_avg_response_time(response_time)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            # Fallback to basic search
            return self._semantic_search_only(query, top_k)
    
    def _hybrid_search(self, query_analysis: QueryAnalysis, top_k: int) -> List[SearchResult]:
        """Perform hybrid search with both semantic and keyword approaches."""
        try:
            # Get semantic search results
            semantic_results = self._get_semantic_results(query_analysis.cleaned_query, top_k * 2)
            
            # Get keyword search results
            keyword_results = self._get_keyword_results(query_analysis.cleaned_query, top_k * 2)
            
            # Combine and rerank results
            combined_results = self._combine_results(semantic_results, keyword_results, query_analysis)
            
            # Apply reranking
            reranked_results = self._rerank_results(combined_results, query_analysis)
            
            return reranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return self._semantic_search_only(query_analysis.cleaned_query, top_k)
    
    def _get_semantic_results(self, query: str, top_k: int) -> List[Tuple[Dict, float]]:
        """Get results from semantic vector search."""
        try:
            if hasattr(self.vector_store, 'similarity_search_with_score'):
                docs_and_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
                return [(doc.page_content, score) for doc, score in docs_and_scores]
            else:
                # Fallback method
                docs = self.vector_store.similarity_search(query, k=top_k)
                return [(doc.page_content, 0.5) for doc in docs]  # Default score
                
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _get_keyword_results(self, query: str, top_k: int) -> List[Tuple[str, float]]:
        """Get results from keyword search."""
        try:
            keyword_scores = self.keyword_engine.search(query, top_k)
            results = []
            
            for doc_idx, score in keyword_scores:
                if doc_idx < len(self.documents):
                    content = self.documents[doc_idx].get('content', '')
                    results.append((content, score))
            
            return results
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def _combine_results(self, semantic_results: List[Tuple], keyword_results: List[Tuple], 
                        query_analysis: QueryAnalysis) -> List[SearchResult]:
        """Combine semantic and keyword search results."""
        combined = {}
        
        # Process semantic results
        for content, score in semantic_results:
            content_hash = hash(content[:100])  # Use first 100 chars as identifier
            if content_hash not in combined:
                combined[content_hash] = SearchResult(
                    content=content,
                    source_url="",  # Will be filled from metadata
                    relevance_score=0.0,
                    keyword_score=0.0,
                    semantic_score=score,
                    combined_score=0.0,
                    chunk_id="",
                    metadata={}
                )
            else:
                combined[content_hash].semantic_score = max(combined[content_hash].semantic_score, score)
        
        # Process keyword results
        for content, score in keyword_results:
            content_hash = hash(content[:100])
            if content_hash not in combined:
                combined[content_hash] = SearchResult(
                    content=content,
                    source_url="",
                    relevance_score=0.0,
                    keyword_score=score,
                    semantic_score=0.0,
                    combined_score=0.0,
                    chunk_id="",
                    metadata={}
                )
            else:
                combined[content_hash].keyword_score = max(combined[content_hash].keyword_score, score)
        
        # Calculate combined scores
        for result in combined.values():
            result.combined_score = (
                self.semantic_weight * result.semantic_score +
                self.keyword_weight * result.keyword_score
            )
            result.relevance_score = result.combined_score
        
        return list(combined.values())
    
    def _rerank_results(self, results: List[SearchResult], query_analysis: QueryAnalysis) -> List[SearchResult]:
        """Apply reranking based on query analysis and content features."""
        try:
            for result in results:
                # Apply query-specific boosting
                boost_factor = 1.0
                
                # Boost results containing query keywords
                content_lower = result.content.lower()
                for keyword in query_analysis.keywords:
                    if keyword.lower() in content_lower:
                        boost_factor += 0.1
                
                # Boost results containing entities
                for entity in query_analysis.entities:
                    if entity.lower() in content_lower:
                        boost_factor += 0.15
                
                # Apply query type specific boosting
                if query_analysis.query_type == 'definition' and 'define' in content_lower:
                    boost_factor += 0.2
                elif query_analysis.query_type == 'process' and any(word in content_lower for word in ['step', 'process', 'how']):
                    boost_factor += 0.2
                
                # Apply boost
                result.combined_score *= boost_factor
                result.relevance_score = result.combined_score
            
            # Sort by final score
            results.sort(key=lambda x: x.combined_score, reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            return sorted(results, key=lambda x: x.combined_score, reverse=True)
    
    def _semantic_search_only(self, query: str, top_k: int) -> List[SearchResult]:
        """Fallback to semantic search only."""
        try:
            semantic_results = self._get_semantic_results(query, top_k)
            
            results = []
            for content, score in semantic_results:
                results.append(SearchResult(
                    content=content,
                    source_url="",
                    relevance_score=score,
                    keyword_score=0.0,
                    semantic_score=score,
                    combined_score=score,
                    chunk_id="",
                    metadata={}
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search fallback: {e}")
            return []
    
    def _update_avg_response_time(self, response_time: float):
        """Update average response time statistics."""
        current_avg = self.search_stats['avg_response_time']
        total_searches = self.search_stats['total_searches']
        
        new_avg = ((current_avg * (total_searches - 1)) + response_time) / total_searches
        self.search_stats['avg_response_time'] = new_avg
    
    def get_performance_stats(self) -> Dict:
        """Get search engine performance statistics."""
        return self.search_stats.copy()
    
    def tune_weights(self, semantic_weight: float, keyword_weight: float):
        """Tune the weights for semantic vs keyword search."""
        total = semantic_weight + keyword_weight
        self.semantic_weight = semantic_weight / total
        self.keyword_weight = keyword_weight / total
        
        logger.info(f"Updated search weights: semantic={self.semantic_weight:.2f}, keyword={self.keyword_weight:.2f}")
