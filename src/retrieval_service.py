import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import faiss
import numpy as np
from src.utils.logger import logger
from src.utils.config import config
from src.utils.embeddings import embeddings_manager

class RetrievalService:
    """FAISS-based vector retrieval with metadata filtering"""
    
    def __init__(self):
        self.index = None
        self.metadata = None
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index and metadata from disk"""
        try:
            logger.info(f"Loading FAISS index from {config.FAISS_INDEX_PATH}")
            
            if not Path(config.FAISS_INDEX_PATH).exists():
                raise FileNotFoundError(f"Index not found: {config.FAISS_INDEX_PATH}")
            
            self.index = faiss.read_index(config.FAISS_INDEX_PATH)
            logger.info(f"  Index loaded with {self.index.ntotal} vectors")
            
            # Load metadata
            logger.info(f"Loading metadata from {config.METADATA_PATH}")
            with open(config.METADATA_PATH, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            logger.info(f"  Metadata loaded for {len(self.metadata)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-K similar chunks for a query
        
        Args:
            query: User query string
            top_k: Number of results (default from config)
            threshold: Similarity threshold (default from config)
            filters: Metadata filters (e.g., {"doc_name": "spec.pdf"})
        
        Returns:
            List of retrieval results with metadata
        """
        top_k = top_k or config.RETRIEVAL_TOP_K
        threshold = threshold or config.SIMILARITY_THRESHOLD
        
        try:
            logger.info(f"Retrieving for query: {query[:50]}... (top_k={top_k})")
            
            # Embed query
            query_embedding = np.array([embeddings_manager.embed(query)]).astype('float32')
            
            # Search FAISS
            distances, indices = self.index.search(query_embedding, min(top_k * 2, self.index.ntotal))
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                
                # Convert FAISS distance to similarity (L2 → cosine-like)
                similarity = 1 / (1 + distance)
                
                if similarity < threshold:
                    logger.debug(f"Skipping result {i}: similarity {similarity:.4f} < {threshold}")
                    continue
                
                chunk_meta = self.metadata[idx]
                
                # Apply filters
                if filters:
                    if not self._match_filters(chunk_meta, filters):
                        continue
                
                result = {
                    "chunk_id": chunk_meta.get("id", f"chunk-{idx}"),
                    "text": chunk_meta.get("text", ""),
                    "score": float(similarity),
                    "doc_name": chunk_meta.get("source", "unknown"),
                    "page_number": chunk_meta.get("page", None),
                    "section_title": chunk_meta.get("section", None),
                    "location": chunk_meta.get("location", None)
                }
                results.append(result)
                
                if len(results) >= top_k:
                    break
            
            logger.info(f"  Retrieved {len(results)} relevant chunks")
            return results
        
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise
    
    def _match_filters(self, chunk_meta: Dict, filters: Dict) -> bool:
        """Check if chunk metadata matches filters"""
        for key, value in filters.items():
            if key not in chunk_meta:
                return False
            if isinstance(value, str):
                if value.lower() not in str(chunk_meta[key]).lower():
                    return False
            elif chunk_meta[key] != value:
                return False
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "total_chunks": self.index.ntotal,
            "embedding_dimension": self.index.d,
            "metadata_count": len(self.metadata),
            "unique_docs": len(set(m.get("source", "") for m in self.metadata))
        }

# Singleton instance
retrieval_service = RetrievalService()
