"""
Interactive CLI for RAG System
Run with: python src/main_app.py
"""

import json
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import logger
from src.utils.config import config
from src.rag_service import rag_service
from src.retrieval_service import retrieval_service

def print_banner():
    """Print welcome banner"""
    print("\n" + "="*60)
    print(" "*15 + " RAG System - Interactive CLI")
    print("="*60 + "\n")

def show_menu():
    """Display main menu"""
    print("\n" + "-"*60)
    print("Main Menu:")
    print("-"*60)
    print("1.  Search Documents (Retrieval Only)")
    print("2.  Generate RAG Answer")
    print("3.  View Index Statistics")
    print("4.  Test RAG Pipeline")
    print("5.  Exit")
    print("-"*60)

def search_documents():
    """Retrieve relevant documents"""
    print("\n[Search Documents]")
    query = input("Enter search query: ").strip()
    
    if not query:
        print("  Query cannot be empty")
        return
    
    try:
        top_k = input("Number of results (default 5): ").strip()
        top_k = int(top_k) if top_k else 5
        
        results = retrieval_service.retrieve(query, top_k=top_k)
        
        if not results:
            print("\n  No relevant documents found")
            return
        
        print(f"\n  Found {len(results)} relevant chunks:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['score']:.2%} match]")
            print(f"   Document: {result['doc_name']}")
            if result.get('page_number'):
                print(f"   Page: {result['page_number']}")
            if result.get('section_title'):
                print(f"   Section: {result['section_title']}")
            print(f"   Text: {result['text'][:100]}...")
            print()
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        print(f"  Error: {e}")

def generate_rag_answer():
    """Generate RAG answer"""
    print("\n[RAG Answer Generation]")
    query = input("Enter your question: ").strip()
    
    if not query:
        print("  Query cannot be empty")
        return
    
    try:
        print("\n Generating answer...")
        result = rag_service.generate_answer(query)
        
        print("\n" + "="*60)
        print("ANSWER:")
        print("="*60)
        print(result['answer'])
        
        if result['references']:
            print("\n" + "-"*60)
            print("SOURCES:")
            print("-"*60)
            for i, ref in enumerate(result['references'], 1):
                print(f"{i}. {ref['doc_name']}", end="")
                if 'page_number' in ref:
                    print(f" (Page {ref['page_number']})", end="")
                if 'section_title' in ref:
                    print(f" - {ref['section_title']}", end="")
                print()
        
        print("\n" + "-"*60)
        print(f"Retrieved {result['retrieved_count']} relevant chunks")
        print("="*60)
    
    except Exception as e:
        logger.error(f"RAG generation failed: {e}")
        print(f"  Error: {e}")

def show_statistics():
    """Display index statistics"""
    try:
        stats = retrieval_service.get_stats()
        
        print("\n" + "="*60)
        print("INDEX STATISTICS:")
        print("="*60)
        print(f"Total Chunks: {stats['total_chunks']}")
        print(f"Embedding Dimension: {stats['embedding_dimension']}")
        print(f"Unique Documents: {stats['unique_docs']}")
        print(f"Metadata Entries: {stats['metadata_count']}")
        print("="*60)
    
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        print(f"  Error: {e}")

def test_pipeline():
    """Test RAG pipeline"""
    print("\n Testing RAG pipeline...")
    result = rag_service.test_rag_pipeline()
    
    print("\n" + "="*60)
    print("TEST RESULTS:")
    print("="*60)
    print(f"Status: {result['status'].upper()}")
    print(f"Message: {result['message']}")
    
    if 'test_result' in result:
        print("\nDetails:")
        for key, value in result['test_result'].items():
            print(f"  - {key}: {value}")
    
    print("="*60)

def main():
    """Main CLI loop"""
    print_banner()
    
    # Validate configuration
    if not config.validate():
        print("  Configuration validation failed. Please check .env file.")
        sys.exit(1)
    
    print(" Configuration validated")
    print(f" FAISS Index: {config.FAISS_INDEX_PATH}")
    print(f" Metadata: {config.METADATA_PATH}\n")
    
    while True:
        show_menu()
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == "1":
            search_documents()
        elif choice == "2":
            generate_rag_answer()
        elif choice == "3":
            show_statistics()
        elif choice == "4":
            test_pipeline()
        elif choice == "5":
            print("\n Bye byeeeeee\n")
            break
        else:
            print("  Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Interrupted by user\n")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"  Fatal error poffffff : {e}")
        sys.exit(1)
