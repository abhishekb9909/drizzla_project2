from typing import List, Dict, Any
from src.utils.logger import logger
from src.utils.config import config
from src.retrieval_service import retrieval_service
from src.utils.llm_client import azure_client

class RAGService:
    """Retrieval-Augmented Generation service"""
    
    def __init__(self):
        self.retrieval_service = retrieval_service
        self.llm_client = azure_client
    
    def generate_answer(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate RAG answer with source attribution
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            threshold: Similarity threshold
            filters: Metadata filters
        
        Returns:
            Dict with answer, references, and metadata
        """
        try:
            logger.info(f"RAG generation started for: {query[:50]}...")
            
            # Step 1: Retrieve relevant chunks
            retrieved = self.retrieval_service.retrieve(
                query=query,
                top_k=top_k,
                threshold=threshold,
                filters=filters
            )
            
            if not retrieved:
                logger.warning("No relevant chunks found")
                return {
                    "query": query,
                    "answer": "I don't have sufficient information in the indexed documents to answer this question.",
                    "references": [],
                    "retrieved_count": 0
                }
            
            # Step 2: Build context from retrieved chunks
            context = self._build_context(retrieved)
            logger.info(f"Context built from {len(retrieved)} chunks ({len(context)} chars)")
            
            # Step 3: Generate answer using LLM
            answer = self.llm_client.generate_answer(
                query=query,
                context=context,
                max_tokens=500,
                temperature=0.7
            )
            logger.info(f"Answer generated ({len(answer)} chars)")
            
            # Step 4: Build references from retrieved chunks
            references = self._build_references(retrieved)
            
            return {
                "query": query,
                "answer": answer,
                "references": references,
                "retrieved_count": len(retrieved),
                "retrieved_chunks": [
                    {
                        "chunk_id": r["chunk_id"],
                        "score": r["score"],
                        "text_snippet": r["text"][:100] + "..." if len(r["text"]) > 100 else r["text"]
                    }
                    for r in retrieved[:3]  # Only show top 3 snippets
                ]
            }
        
        except Exception as e:
            logger.error(f"RAG generation failed: {e}")
            raise
    
    def _build_context(self, retrieved: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        
        for i, chunk in enumerate(retrieved, 1):
            header = f"[Chunk {i} - Doc: {chunk.get('doc_name', 'unknown')}"
            
            if chunk.get('page_number'):
                header += f", Page: {chunk['page_number']}"
            if chunk.get('section_title'):
                header += f", Section: {chunk['section_title']}"
            
            header += f", Score: {chunk['score']:.2f}]"
            
            context_parts.append(header)
            context_parts.append(chunk['text'])
            context_parts.append("")  # Blank line between chunks
        
        return "\n".join(context_parts)
    
    def _build_references(self, retrieved: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build reference list from retrieved chunks"""
        references = []
        seen = set()
        
        for chunk in retrieved:
            # Avoid duplicate references from same location
            ref_key = (
                chunk.get('doc_name'),
                chunk.get('page_number'),
                chunk.get('section_title')
            )
            
            if ref_key in seen:
                continue
            seen.add(ref_key)
            
            ref = {
                "doc_name": chunk.get('doc_name', 'unknown'),
                "chunk_id": chunk.get('chunk_id'),
            }
            
            if chunk.get('page_number') is not None:
                ref["page_number"] = chunk['page_number']
            if chunk.get('section_title'):
                ref["section_title"] = chunk['section_title']
            if chunk.get('location'):
                ref["location"] = chunk['location']
            
            references.append(ref)
        
        return references
    
    def test_rag_pipeline(self) -> Dict[str, Any]:
        """Test RAG pipeline end-to-end"""
        try:
            logger.info("Testing RAG pipeline...")
            
            test_query = "What is AI?"
            logger.info(f"Test query: {test_query}")
            
            # Test retrieval
            retrieved = self.retrieval_service.retrieve(test_query, top_k=3)
            logger.info(f"  Retrieval: {len(retrieved)} chunks found")
            
            # Test LLM connection
            is_connected = self.llm_client.test_connection()
            if not is_connected:
                logger.error("✗ LLM connection failed")
                return {"status": "error", "message": "LLM connection failed"}
            logger.info("  LLM connection successful")
            
            # Test answer generation (if retrieval worked)
            if retrieved:
                result = self.generate_answer(test_query)
                logger.info("  Answer generation successful")
                return {
                    "status": "success",
                    "message": "RAG pipeline is functional",
                    "test_result": {
                        "query": result["query"],
                        "answer_length": len(result["answer"]),
                        "references_count": len(result["references"])
                    }
                }
            else:
                logger.warning("⚠ No chunks retrieved for test query")
                return {
                    "status": "warning",
                    "message": "RAG pipeline works but no relevant documents found for test query"
                }
        
        except Exception as e:
            logger.error(f"RAG pipeline test failed: {e}")
            return {"status": "error", "message": str(e)}

# Singleton instance
rag_service = RAGService()
