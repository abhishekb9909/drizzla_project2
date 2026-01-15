"""
FastAPI Server for RAG System
Run with: python src/api_server.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import logger
from src.utils.config import config
from src.rag_service import rag_service
from src.retrieval_service import retrieval_service

# Initialize FastAPI app
app = FastAPI(
    title="Document RAG Pipeline API",
    description="Retrieve and generate answers from indexed documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models

class RetrieveRequest(BaseModel):
    """Request model for document retrieval"""
    query: str
    top_k: Optional[int] = None
    threshold: Optional[float] = None

class RetrieveResponse(BaseModel):
    """Response model for retrieval"""
    query: str
    results: List[Dict[str, Any]]
    count: int

class RAGRequest(BaseModel):
    """Request model for RAG answer generation"""
    query: str
    top_k: Optional[int] = None
    threshold: Optional[float] = None

class RAGResponse(BaseModel):
    """Response model for RAG"""
    query: str
    answer: str
    references: List[Dict[str, Any]]
    retrieved_count: int

# Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Document RAG Pipeline",
        "version": "1.0.0"
    }

@app.post("/api/retrieve", response_model=RetrieveResponse)
async def retrieve_documents(request: RetrieveRequest):
    """
    Retrieve relevant document chunks
    
    -  query : User search query
    -  top_k : Number of results (default: 10)
    -  threshold : Similarity threshold (default: 0.5)
    """
    try:
        logger.info(f"API: Retrieve request - {request.query[:50]}")
        
        results = retrieval_service.retrieve(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        return RetrieveResponse(
            query=request.query,
            results=results,
            count=len(results)
        )
    
    except Exception as e:
        logger.error(f"Retrieval API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag", response_model=RAGResponse)
async def generate_rag_answer(request: RAGRequest):
    """
    Generate RAG answer with source citations
    
    -  query : User question
    -  top_k : Number of chunks to retrieve (default: 10)
    -  threshold : Similarity threshold (default: 0.5)
    """
    try:
        logger.info(f"API: RAG request - {request.query[:50]}")
        
        result = rag_service.generate_answer(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        return RAGResponse(
            query=result['query'],
            answer=result['answer'],
            references=result['references'],
            retrieved_count=result['retrieved_count']
        )
    
    except Exception as e:
        logger.error(f"RAG API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_statistics():
    """Get index statistics"""
    try:
        stats = retrieval_service.get_stats()
        return {
            "status": "success",
            "statistics": stats
        }
    
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test_pipeline():
    """Test RAG pipeline connectivity"""
    try:
        logger.info("API: Pipeline test request")
        result = rag_service.test_rag_pipeline()
        return result
    
    except Exception as e:
        logger.error(f"Test API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

 # Startup/Shutdown Events
 
@app.on_event("startup")
async def startup_event():
    """Startup operations"""
    logger.info("API Server starting...")
    logger.info(f"Config: {config.FAISS_INDEX_PATH}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown operations"""
    logger.info("API Server shutting down...")

 # Main
 
if __name__ == "__main__":
    logger.info(f"Starting API server on {config.API_HOST}:{config.API_PORT}")
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower()
    )
