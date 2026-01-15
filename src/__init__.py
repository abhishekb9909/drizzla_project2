"""
Document RAG Retrieval Pipeline - Phase 2

Retrieval-Augmented Generation system with FAISS + Azure OpenAI
"""

__version__ = "1.0.0"
__author__ = "Abhishake B"
__description__ = "Document RAG Pipeline - Retrieval & Answer Generation"

# Version info
VERSION = (1, 0, 0)

# Lazy imports
def __getattr__(name):
    if name == "retrieval_service":
        from src.retrieval_service import retrieval_service
        return retrieval_service
    elif name == "rag_service":
        from src.rag_service import rag_service
        return rag_service
    elif name == "config":
        from src.utils.config import config
        return config
    elif name == "logger":
        from src.utils.logger import logger
        return logger
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["retrieval_service", "rag_service", "config", "logger"]
