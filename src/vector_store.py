"""
Vector store implementation for efficient similarity search and retrieval.
"""

# Fix SQLite version issue for ChromaDB
import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for document embeddings and similarity search."""
    
    def __init__(self, persist_directory: str = "data/chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist the vector database
            model_name: Name of the sentence transformer model
        """
        self.persist_directory = persist_directory
        self.model_name = model_name
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection_name = "gitlab_documents"
        try:
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "GitLab Handbook and Direction documents"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts."""
        logger.info(f"Creating embeddings for {len(texts)} texts")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def add_documents(self, documents: List[Dict]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        # Prepare data for ChromaDB
        ids = []
        texts = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            doc_id = f"doc_{i}_{hash(doc['url'] + str(doc.get('chunk_id', 0)))}"
            ids.append(doc_id)
            
            # Create searchable text (title + content)
            searchable_text = f"{doc['title']}\n\n{doc['content']}"
            texts.append(searchable_text)
            
            # Prepare metadata
            metadata = {
                'url': doc['url'],
                'title': doc['title'],
                'word_count': doc['word_count'],
                'chunk_id': doc.get('chunk_id', 0),
                'total_chunks': doc.get('total_chunks', 1),
                'scraped_at': doc.get('scraped_at', 0)
            }
            metadatas.append(metadata)
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"✅ Successfully added {len(documents)} documents to vector store")
    
    def search(self, query: str, n_results: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of relevant documents with similarity scores
        """
        logger.info(f"Searching for: '{query}'")
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=filter_dict
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else 0.0,
                    'similarity': 1 - (results['distances'][0][i] if 'distances' in results else 0.0)
                }
                formatted_results.append(result)
        
        logger.info(f"Found {len(formatted_results)} relevant documents")
        return formatted_results
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection."""
        count = self.collection.count()
        return {
            'name': self.collection_name,
            'document_count': count,
            'model_name': self.model_name,
            'persist_directory': self.persist_directory
        }
    
    def delete_collection(self) -> None:
        """Delete the collection (useful for reindexing)."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

class AdvancedRetriever:
    """Advanced retrieval with query enhancement and reranking."""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    def enhance_query(self, query: str) -> List[str]:
        """Generate variations of the query for better retrieval."""
        base_query = query.strip()
        enhanced_queries = [base_query]
        
        # Add GitLab-specific context with smarter matching
        if "what is" in base_query.lower():
            gitlab_contexts = [
                f"GitLab company overview",
                f"GitLab platform definition", 
                f"GitLab {base_query.replace('what is', '').strip()}",
                f"About GitLab {base_query.replace('what is', '').strip()}",
                f"GitLab introduction {base_query.replace('what is', '').strip()}"
            ]
        elif any(word in base_query.lower() for word in ["values", "value", "core"]):
            gitlab_contexts = [
                f"GitLab values",
                f"GitLab core values",
                f"GitLab company values",
                f"GitLab mission values",
                f"GitLab culture values"
            ]
        else:
            gitlab_contexts = [
                f"GitLab {base_query}",
                f"GitLab handbook {base_query}",
                f"GitLab direction {base_query}",
                f"How does GitLab {base_query}",
                f"GitLab process for {base_query}"
            ]
        
        enhanced_queries.extend(gitlab_contexts)
        return enhanced_queries[:6]  # Increased to 6 variations
    
    def retrieve_with_reranking(self, query: str, n_results: int = 10, final_results: int = 5) -> List[Dict]:
        """
        Retrieve documents with query enhancement and reranking.
        
        Args:
            query: Original query
            n_results: Number of initial results to retrieve
            final_results: Number of final results to return
            
        Returns:
            Reranked list of relevant documents
        """
        # Get enhanced queries
        enhanced_queries = self.enhance_query(query)
        
        # Retrieve results for each query variation
        all_results = {}
        for enhanced_query in enhanced_queries:
            results = self.vector_store.search(enhanced_query, n_results=n_results)
            for result in results:
                doc_id = result['id']
                if doc_id not in all_results:
                    all_results[doc_id] = result
                    all_results[doc_id]['scores'] = []
                all_results[doc_id]['scores'].append(result['similarity'])
        
        # Rerank by average similarity score
        for doc_id in all_results:
            scores = all_results[doc_id]['scores']
            all_results[doc_id]['avg_similarity'] = np.mean(scores)
            all_results[doc_id]['max_similarity'] = np.max(scores)
        
        # Sort by average similarity
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x['avg_similarity'],
            reverse=True
        )
        
        return sorted_results[:final_results]

def build_vector_store_from_data(data_file: str = "data/chunks.json", persist_directory: str = "data/chroma_db") -> VectorStore:
    """
    Build vector store from processed data file.
    
    Args:
        data_file: Path to the chunks JSON file
        persist_directory: Directory to persist the vector database
        
    Returns:
        Initialized VectorStore with documents
    """
    logger.info("Building vector store from data...")
    
    # Load documents
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    # Initialize vector store
    vector_store = VectorStore(persist_directory=persist_directory)
    
    # Check if collection is empty
    collection_info = vector_store.get_collection_info()
    if collection_info['document_count'] == 0:
        # Add documents to vector store
        vector_store.add_documents(documents)
    else:
        logger.info(f"Collection already contains {collection_info['document_count']} documents")
    
    return vector_store

def main():
    """Main function to test the vector store."""
    # Build vector store
    vector_store = build_vector_store_from_data()
    
    # Test search
    test_queries = [
        "How does GitLab handle code reviews?",
        "GitLab remote work policy",
        "CI/CD pipeline configuration",
        "GitLab values and culture"
    ]
    
    retriever = AdvancedRetriever(vector_store)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = retriever.retrieve_with_reranking(query, final_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['metadata']['title']}")
            print(f"   Similarity: {result['avg_similarity']:.3f}")
            print(f"   URL: {result['metadata']['url']}")
            print(f"   Preview: {result['content'][:150]}...")
            print()

if __name__ == "__main__":
    main()
