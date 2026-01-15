from openai import AzureOpenAI
from src.utils.logger import logger
from src.utils.config import config

class AzureOpenAIClient:
    """Wrapper for Azure OpenAI client with error handling"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            logger.info("Initializing Azure OpenAI client...")
            try:
                self._client = AzureOpenAI(
                    api_key=config.AZURE_OPENAI_API_KEY,
                    api_version=config.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=config.AZURE_OPENAI_ENDPOINT
                )
                logger.info("✓ Azure OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
                raise
    
    def generate_answer(
        self,
        query: str,
        context: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate RAG answer using retrieved context"""
        try:
            system_prompt = """You are a helpful assistant that answers questions based on provided context.
            
IMPORTANT RULES:
1. Answer ONLY using the provided context
2. If the answer is not in the context, say "I don't have sufficient information to answer this question"
3. Be concise and clear
4. Cite specific sections when possible"""
            
            user_prompt = f"""Context:
{context}

Question: {query}

Please provide a clear, concise answer based only on the context provided."""
            
            logger.info(f"Generating answer for query: {query[:50]}...")
            
            response = self._client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            answer = response.choices[0].message.content
            logger.info(f"✓ Answer generated ({len(answer)} chars)")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Azure OpenAI connection"""
        try:
            logger.info("Testing Azure OpenAI connection...")
            response = self._client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            logger.info("✓ Azure OpenAI connection successful")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# Singleton instance
azure_client = AzureOpenAIClient()
