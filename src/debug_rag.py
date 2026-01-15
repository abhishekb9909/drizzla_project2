
import sys
import os
import traceback

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import logger
from src.utils.config import config
from src.rag_service import rag_service

def debug_rag():
    print("--------------------------------------------------")
    print("DEBUGGING RAG GENERATION")
    print("--------------------------------------------------")
    
    print(f"API Endpoint: {config.AZURE_OPENAI_ENDPOINT}")
    print(f"API Version: {config.AZURE_OPENAI_API_VERSION}")
    print(f"Deployment: {config.AZURE_OPENAI_DEPLOYMENT}")
    # Mask key for safety
    masked_key = config.AZURE_OPENAI_API_KEY[:4] + "***" + config.AZURE_OPENAI_API_KEY[-4:] if config.AZURE_OPENAI_API_KEY else "NOT SET"
    print(f"API Key: {masked_key}")
    
    print("\n[Test 1] Testing Connection")
    try:
        from src.utils.llm_client import azure_client
        if azure_client.test_connection():
            print("  Connection Successful")
        else:
            print(" Connection Failed (check logs)")
    except Exception as e:
        print(f" Connection Error: {e}")
        traceback.print_exc()

    print("\n[Test 2] Testing Generation")
    try:
        query = "What was the session about?"
        print(f"Query: {query}")
        result = rag_service.generate_answer(query)
        print(f"  Answer Generated: {result['answer']}")
    except Exception as e:
        print(f" Generation Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_rag()
