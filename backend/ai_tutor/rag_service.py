"""RAG (Retrieval Augmented Generation) service for knowledge retrieval"""
from typing import List, Dict, Any, Optional
import logging
from .models import KnowledgeDocument, DocumentChunk
from .embedding_service import embedding_service
import re

logger = logging.getLogger(__name__)

class RAGService:
    """Service for retrieving relevant context from knowledge base"""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return chunks
    
    @staticmethod
    def process_document(document: KnowledgeDocument) -> int:
        """Process a document: chunk and generate embeddings"""
        try:
            logger.info(f"Processing document: {document.title}")
            
            # Delete existing chunks
            document.chunks.all().delete()
            
            # Chunk the document
            chunks = RAGService.chunk_text(document.content)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Generate embeddings
            embeddings = embedding_service.generate_embeddings(chunks)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Create chunk objects
            chunk_objects = []
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_obj = DocumentChunk(
                    document=document,
                    chunk_text=chunk_text,
                    chunk_index=idx,
                    embedding=embedding.tolist(),
                    metadata={
                        'length': len(chunk_text),
                        'document_type': document.document_type,
                    }
                )
                chunk_objects.append(chunk_obj)
            
            # Bulk create
            DocumentChunk.objects.bulk_create(chunk_objects)
            logger.info(f"Successfully processed document: {document.title}")
            
            return len(chunks)
        
        except Exception as e:
            logger.error(f"Failed to process document {document.title}: {e}")
            raise
    
    @staticmethod
    def search_knowledge_base(query: str, top_k: int = 5, 
                            document_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant chunks"""
        try:
            logger.info(f"Searching knowledge base for: {query}")
            
            # Generate query embedding
            query_embedding = embedding_service.generate_embedding(query)
            
            # Get all chunks (with optional filtering)
            chunks_query = DocumentChunk.objects.select_related('document')
            
            if document_types:
                chunks_query = chunks_query.filter(document__document_type__in=document_types)
            
            chunks_query = chunks_query.filter(document__is_active=True)
            
            # Load chunks with embeddings
            chunks_data = []
            for chunk in chunks_query:
                chunk_embedding = chunk.get_embedding()
                chunks_data.append((str(chunk.id), chunk_embedding, chunk))
            
            if not chunks_data:
                logger.warning("No chunks found in knowledge base")
                return []
            
            logger.info(f"Searching through {len(chunks_data)} chunks")
            
            # Calculate similarities
            similarities = []
            for chunk_id, chunk_embedding, chunk_obj in chunks_data:
                similarity = embedding_service.cosine_similarity(
                    query_embedding, chunk_embedding
                )
                similarities.append((chunk_id, similarity, chunk_obj))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top-k results
            results = []
            for chunk_id, similarity, chunk_obj in similarities[:top_k]:
                results.append({
                    'chunk_id': chunk_id,
                    'similarity': float(similarity),
                    'text': chunk_obj.chunk_text,
                    'document_title': chunk_obj.document.title,
                    'document_type': chunk_obj.document.document_type,
                    'metadata': chunk_obj.metadata,
                })
            
            logger.info(f"Found {len(results)} relevant chunks")
            return results
        
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
            return []
    
    @staticmethod
    def build_context_from_results(results: List[Dict[str, Any]], 
                                   max_tokens: int = 2000) -> str:
        """Build context string from search results"""
        if not results:
            return ""
        
        context_parts = []
        current_length = 0
        
        for result in results:
            text = result['text']
            source = f"[Source: {result['document_title']}]"
            chunk_text = f"{source}\n{text}\n"
            
            # Rough token estimation (1 token ≈ 4 characters)
            estimated_tokens = len(chunk_text) // 4
            
            if current_length + estimated_tokens > max_tokens:
                break
            
            context_parts.append(chunk_text)
            current_length += estimated_tokens
        
        return "\n---\n".join(context_parts)

# Global instance
rag_service = RAGService()
