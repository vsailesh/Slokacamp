"""Embedding service for generating and storing text embeddings"""
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using sentence-transformers"""
    
    def __init__(self):
        self.model = None
        self.model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    
    def _load_model(self):
        """Lazy load the embedding model"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        self._load_model()
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        self._load_model()
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [emb for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_similar_chunks(self, query_embedding: np.ndarray, 
                           chunk_embeddings: List[Tuple[str, np.ndarray]], 
                           top_k: int = 5) -> List[Tuple[str, float]]:
        """Find top-k most similar chunks to query"""
        similarities = []
        
        for chunk_id, chunk_embedding in chunk_embeddings:
            similarity = self.cosine_similarity(query_embedding, chunk_embedding)
            similarities.append((chunk_id, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]

# Global instance
embedding_service = EmbeddingService()
