from typing import List, Optional
from sentence_transformers import SentenceTransformer
from src.utils.logger import logger
from src.utils.config import config

class EmbeddingsManager:
    """Manages embedding generation using SentenceTransformer"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            logger.info(f"Loading embedding model: {config.EMBEDDINGS_MODEL}")
            try:
                self._model = SentenceTransformer(config.EMBEDDINGS_MODEL)
                logger.info(f"✓ Model loaded. Dimension: {self._model.get_sentence_embedding_dimension()}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
    
    def embed(self, text: str) -> List[float]:
        """Embed a single text string"""
        try:
            embedding = self._model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding failed for text: {e}")
            raise
    
    def embed_batch(self, texts: List[str], show_progress_bar: bool = False) -> List[List[float]]:
        """Embed multiple texts efficiently"""
        try:
            embeddings = self._model.encode(
                texts,
                convert_to_tensor=False,
                show_progress_bar=show_progress_bar
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self._model.get_sentence_embedding_dimension()

# Singleton instance
embeddings_manager = EmbeddingsManager()
