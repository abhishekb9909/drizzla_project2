
"""
Debug Tools for RAG System
Run with: python src/debug_tools.py --help
"""

import sys
import os

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
from pathlib import Path
from src.utils.logger import logger
from src.utils.config import config
from src.retrieval_service import retrieval_service
from src.utils.embeddings import embeddings_manager
from src.utils.llm_client import azure_client

def inspect_index():
    """Inspect FAISS index structure and statistics"""
    print("\n" + "="*60)
    print("FAISS INDEX INSPECTION")
    print("="*60)
    
    try:
        stats = retrieval_service.get_stats()
        
        print(f"\n  Index Path: {config.FAISS_INDEX_PATH}")
        print(f"  - Total Chunks: {stats['total_chunks']}")
        print(f"  - Embedding Dimension: {stats['embedding_dimension']}")
        print(f"  - Unique Documents: {stats['unique_docs']}")
        
        # Sample metadata
        print(f"\n  Metadata (Sample of first 3 chunks):")
        for i, chunk in enumerate(retrieval_service.metadata[:3], 1):
            print(f"\n  Chunk {i}:")
            print(f"    - ID: {chunk.get('id', 'N/A')}")
            print(f"    - Source: {chunk.get('source', 'N/A')}")
            print(f"    - Page: {chunk.get('page', 'N/A')}")
            print(f"    - Section: {chunk.get('section', 'N/A')}")
            print(f"    - Text Length: {len(chunk.get('text', ''))} chars")
            print(f"    - Text Preview: {chunk.get('text', '')[:80]}...")
        
        print("\n" + "="*60)
    
    except Exception as e:
        logger.error(f"Index inspection failed: {e}")
        print(f" Error: {e}")

def test_embedding():
    """Test embedding generation"""
    print("\n" + "="*60)
    print("EMBEDDING MODEL TEST")
    print("="*60)
    
    try:
        print(f"\n  Model: {config.EMBEDDINGS_MODEL}")
        print(f"  Embedding Dimension: {embeddings_manager.get_dimension()}")
        
        test_text = "What is document chunking?"
        print(f"\n  Test Text: '{test_text}'")
        
        embedding = embeddings_manager.embed(test_text)
        print(f"    Embedding generated: {len(embedding)} dimensions")
        print(f"  Sample values: {embedding[:5]}")
        
        print("\n" + "="*60)
    
    except Exception as e:
        logger.error(f"Embedding test failed: {e}")
        print(f" Error: {e}")

def test_azure_connection():
    """Test Azure OpenAI connection"""
    print("\n" + "="*60)
    print("AZURE OPENAI CONNECTION TEST")
    print("="*60)
    
    try:
        print(f"\n  Endpoint: {config.AZURE_OPENAI_ENDPOINT}")
        print(f"  Deployment: {config.AZURE_OPENAI_DEPLOYMENT}")
        print(f"  API Version: {config.AZURE_OPENAI_API_VERSION}")
        
        is_connected = azure_client.test_connection()
        
        if is_connected:
            print(f"\n  Connection Successful!")
            print("  You can now generate RAG answers.")
        else:
            print(f"\n Connection Failed!")
            print("  Check your Azure credentials in .env file")
        
        print("\n" + "="*60)
    
    except Exception as e:
        logger.error(f"Azure connection test failed: {e}")
        print(f" Error: {e}")

def test_query(query: str = None):
    """Test query embedding and retrieval"""
    if query is None:
        query = input("Enter test query: ").strip()
    
    if not query:
        print(" Query cannot be empty")
        return
    
    print("\n" + "="*60)
    print(f"QUERY TEST: '{query}'")
    print("="*60)
    
    try:
        print(f"\n1. Embedding query...")
        embedding = embeddings_manager.embed(query)
        print(f"     Query embedding: {len(embedding)} dimensions")
        
        print(f"\n2. Searching FAISS index...")
        results = retrieval_service.retrieve(query, top_k=5)
        print(f"     Found {len(results)} relevant chunks")
        
        print(f"\n3. Top Results:")
        for i, result in enumerate(results[:5], 1):
            print(f"\n   Result {i}:")
            print(f"     Score: {result['score']:.4f}")
            print(f"     Document: {result['doc_name']}")
            if result.get('page_number'):
                print(f"     Page: {result['page_number']}")
            if result.get('section_title'):
                print(f"     Section: {result['section_title']}")
            print(f"     Text: {result['text'][:100]}...")
        
        print("\n" + "="*60)
    
    except Exception as e:
        logger.error(f"Query test failed: {e}")
        print(f" Error: {e}")

def validate_config():
    """Validate configuration"""
    print("\n" + "="*60)
    print("CONFIGURATION VALIDATION")
    print("="*60)
    
    checks = [
        ("AZURE OpenAI API Key", config.AZURE_OPENAI_API_KEY),
        ("AZURE OpenAI Endpoint", config.AZURE_OPENAI_ENDPOINT),
        ("FAISS Index File", Path(config.FAISS_INDEX_PATH).exists()),
        ("Metadata File", Path(config.METADATA_PATH).exists()),
    ]
    
    all_valid = True
    for check_name, value in checks:
        is_valid = bool(value)
        status = " " if is_valid else "❌"
        print(f"\n{status} {check_name}")
        if not is_valid:
            all_valid = False
            if check_name.startswith("AZURE"):
                print(f"   → Set in .env file")
            else:
                print(f"   → Path: {value if isinstance(value, str) else config.METADATA_PATH}")
    
    print("\n" + "="*60)
    if all_valid:
        print(" All configuration checks passed!")
    else:
        print(" Some configuration checks failed!")
    print("="*60)

def main():
    """Main debug CLI"""
    parser = argparse.ArgumentParser(description="RAG System Debug Tools")
    
    parser.add_argument(
        "--inspect-index",
        action="store_true",
        help="Inspect FAISS index and metadata"
    )
    parser.add_argument(
        "--test-embedding",
        action="store_true",
        help="Test embedding generation"
    )
    parser.add_argument(
        "--test-azure-connection",
        action="store_true",
        help="Test Azure OpenAI connection"
    )
    parser.add_argument(
        "--test-query",
        type=str,
        nargs="?",
        const="What is RAG?",
        help="Test query retrieval"
    )
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration"
    )
    
    args = parser.parse_args()
    
    # If no arguments, run all tests
    if not any(vars(args).values()):
        validate_config()
        inspect_index()
        test_embedding()
        test_azure_connection()
        test_query()
    else:
        if args.inspect_index:
            inspect_index()
        if args.test_embedding:
            test_embedding()
        if args.test_azure_connection:
            test_azure_connection()
        if args.test_query:
            test_query(args.test_query)
        if args.validate_config:
            validate_config()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Interrupted by user\n")
    except Exception as e:
        logger.error(f"Debug tool error: {e}")
        print(f" Error: {e}")
