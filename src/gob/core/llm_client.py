"""
Multi-model LLM client layer for GOB-01
Provides chat, utility, and embedding clients
"""
import os
import aiohttp
import logging
import time
from typing import Dict, List, Optional
import numpy as np
import asyncio
import warnings
from sentence_transformers import SentenceTransformer

# Comprehensive warning suppression for embedding models
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Suppress Hugging Face Hub warnings
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

# Suppress transformers and sentence-transformers logging
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)
logging.getLogger("transformers.tokenization_utils_base").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub.file_download").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


class LLMClient:
    """Primary chat model client"""
    
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None):
        self.model = model or os.getenv("CHAT_MODEL", "llama3.2:3b")
        self.api_key = api_key or os.getenv("OLLAMA_CLOUD_API_KEY")
        self.base_url = base_url or "https://api.ollama.com/v1"
        self.timeout = 60
        
        # Validation
        if not self.api_key and "openrouter" in self.model:
            # We allow initialization without key, but warn/fail on usage
            pass
    
    async def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> str:
        """Chat completion with comprehensive logging and timing"""
        start_time = time.time()
        logger.info(f"Starting LLM chat request for model: {self.model}")
        logger.debug(f"Messages count: {len(messages)}")
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/dusty-schmidt/gob-01",
            "X-Title": "GOB-01 Agent"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.7
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        logger.debug(f"Request payload: {payload}")
        
        async with aiohttp.ClientSession() as session:
            try:
                logger.debug(f"Making API call to: {url}")
                api_start = time.time()
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    api_time = time.time() - api_start
                    logger.info(f"API response received in {api_time:.3f}s, status: {response.status}")
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        raise RuntimeError(f"API error: {response.status} - {error_text}")
                    
                    result = await response.json()
                    logger.debug(f"Full API response: {result}")
                    
                    # Safely extract content from response
                    try:
                        if "choices" in result and len(result["choices"]) > 0:
                            content = result["choices"][0]["message"]["content"]
                            logger.info(f"Successfully extracted content from choices")
                        elif "message" in result:
                            # Handle direct message response
                            content = result["message"]["content"]
                            logger.info(f"Successfully extracted content from direct message")
                        else:
                            # Fallback: try to extract any text field
                            content = str(result)
                            logger.warning(f"Could not extract proper message content, using raw response: {content[:100]}...")
                        
                        total_time = time.time() - start_time
                        logger.info(f"LLM chat completed successfully in {total_time:.3f}s")
                        return content
                    except (KeyError, IndexError) as e:
                        logger.error(f"Failed to extract content from API response: {e}")
                        logger.error(f"Response structure: {result}")
                        raise RuntimeError(f"Invalid API response structure: {str(e)}")
            except Exception as e:
                total_time = time.time() - start_time
                logger.error(f"LLM call failed after {total_time:.3f}s: {e}")
                raise RuntimeError(f"LLM call failed: {str(e)}")


class UtilityLLMClient:
    """Cheap utility model for memory tasks (can be local or API-based)"""
    
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None):
        self.model = model or os.getenv("UTILITY_MODEL", "qwen/qwen3.5-flash-02-23")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        # Determine base_url based on model type
        if "ollama" in self.model:
            self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        else:
            # Assume OpenRouter or other OpenAI-compatible API
            self.base_url = base_url or "https://openrouter.ai/api/v1"
    
    async def generate(self, messages: List[Dict], max_tokens: int = 512) -> str:
        """Generate text with comprehensive logging and timing"""
        start_time = time.time()
        logger.info(f"Starting utility LLM generation for model: {self.model}")
        logger.debug(f"Messages: {messages}")
        
        if "ollama" in self.model:
            # Ollama API call
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.model.replace("ollama/", ""),
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": max_tokens}
            }
            logger.debug(f"Ollama payload: {payload}")
            
            try:
                logger.debug(f"Making Ollama API call to: {url}")
                api_start = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        api_time = time.time() - api_start
                        logger.info(f"Ollama response received in {api_time:.3f}s")
                        result = await response.json()
                        total_time = time.time() - start_time
                        logger.info(f"Utility LLM generation completed in {total_time:.3f}s")
                        return result["message"]["content"]
            except Exception as e:
                total_time = time.time() - start_time
                logger.error(f"Ollama call failed after {total_time:.3f}s: {e}")
                raise RuntimeError(f"Ollama call failed: {str(e)}")
        else:
            # OpenRouter or other OpenAI-compatible API
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/dusty-schmidt/gob-01",
                "X-Title": "GOB-01 Agent"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.0
            }
            logger.debug(f"OpenRouter payload: {payload}")
            
            try:
                logger.debug(f"Making OpenRouter API call to: {url}")
                api_start = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, headers=headers) as response:
                        api_time = time.time() - api_start
                        logger.info(f"OpenRouter response received in {api_time:.3f}s, status: {response.status}")
                        result = await response.json()
                        total_time = time.time() - start_time
                        logger.info(f"Utility LLM generation completed in {total_time:.3f}s")
                        return result["choices"][0]["message"]["content"]
            except Exception as e:
                total_time = time.time() - start_time
                logger.error(f"API call failed after {total_time:.3f}s: {e}")
                raise RuntimeError(f"API call failed: {str(e)}")


class EmbeddingClient:
    """Local embedding model using sentence-transformers"""
    
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model = model
        self._model = None
        logger.info(f"EmbeddingClient initialized with model: {self.model}")
    
    def _load_model(self):
        if self._model is None:
            try:
                logger.debug(f"Loading embedding model: {self.model}")
                load_start = time.time()
                self._model = SentenceTransformer(self.model)
                load_time = time.time() - load_start
                logger.info(f"Embedding model loaded in {load_time:.3f}s")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Failed to load embedding model: {str(e)}")
    
    def embed(self, text: str) -> np.ndarray:
        """Generate embedding vector using local model with timing"""
        start_time = time.time()
        logger.debug(f"Generating embedding for text: {text[:50]}...")
        
        self._load_model()
        
        try:
            embedding = self._model.encode(text)
            total_time = time.time() - start_time
            logger.info(f"Embedding generated in {total_time:.3f}s, shape: {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}")


class MultiLLM:
    """Multi-model LLM manager that coordinates chat, utility, and embedding clients"""
    
    def __init__(self, config: dict = None):
        """Initialize MultiLLM with configuration"""
        config = config or {}
        
        # Chat model configuration
        chat_model = config.get("chat_model", os.getenv("CHAT_MODEL", "qwen/qwen3.5-flash-02-23"))
        chat_key = config.get("api_key", os.getenv("OPENROUTER_API_KEY"))
        chat_base = config.get("base_url")
        
        # Utility model configuration (for memory tasks)
        utility_model = config.get("utility_model", os.getenv("UTILITY_MODEL", "qwen/qwen3.5-flash-02-23"))
        utility_key = config.get("utility_key", chat_key)  # Use same key by default
        utility_base = config.get("utility_base_url", chat_base)
        
        # Embedding model configuration
        embedding_model = config.get("embedding_model", "all-MiniLM-L6-v2")
        
        logger.info(f"Initializing MultiLLM with chat_model: {chat_model}, utility_model: {utility_model}, embedding_model: {embedding_model}")
        
        # Initialize clients
        self.chat = LLMClient(model=chat_model, api_key=chat_key, base_url=chat_base)
        self.utility = UtilityLLMClient(model=utility_model, api_key=utility_key, base_url=utility_base)
        self.embedding = EmbeddingClient(model=embedding_model)
        
        # Expose chat model name for convenience
        self.chat_model = chat_model
        
        logger.info("MultiLLM initialization completed successfully")
    
    async def chat_complete(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> str:
        """Async chat completion wrapper"""
        logger.info(f"MultiLLM chat_complete called with {len(messages)} messages")
        chat_start = time.time()
        
        try:
            result = await self.chat.chat(messages, tools)
            total_time = time.time() - chat_start
            logger.info(f"MultiLLM chat_complete completed in {total_time:.3f}s")
            return result
        except Exception as e:
            total_time = time.time() - chat_start
            logger.error(f"MultiLLM chat_complete failed after {total_time:.3f}s: {e}")
            raise
    
    async def generate_query(self, context: str, task: str) -> str:
        """Generate a semantic search query from context"""
        logger.info(f"Generating query for task: {task}")
        query_start = time.time()
        
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that generates concise search queries for memory retrieval."},
                {"role": "user", "content": f"Based on this context: '{context}', generate a concise search query for finding relevant information about: {task}"}
            ]
            
            query = await self.utility.generate(messages, max_tokens=50)
            total_time = time.time() - query_start
            logger.info(f"Query generated in {total_time:.3f}s: {query[:50]}...")
            return query
        except Exception as e:
            total_time = time.time() - query_start
            logger.error(f"Query generation failed after {total_time:.3f}s: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embeddings for text"""
        logger.info(f"Embedding text of length: {len(text)}")
        embed_start = time.time()
        
        try:
            result = self.embedding.embed(text)
            total_time = time.time() - embed_start
            logger.info(f"Text embedded in {total_time:.3f}s")
            return result
        except Exception as e:
            total_time = time.time() - embed_start
            logger.error(f"Embedding failed after {total_time:.3f}s: {e}")
    
    def embed(self, text: str) -> np.ndarray:
        """Generate embeddings for text"""
        start_time = time.time()
        logger.info(f"Generating embeddings for text of length {len(text)}")
        
        try:
            embedding = self.model.encode(text)
            total_time = time.time() - start_time
            logger.info(f"Embeddings generated in {total_time:.3f}s, shape: {embedding.shape}")
            return embedding
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Embedding failed after {total_time:.3f}s: {e}")
            raise RuntimeError(f"Embedding failed: {str(e)}")


class MultiLLMClient:
    """Multi-model LLM client manager"""
    
    def __init__(self):
        self.chat = LLMClient()
        self.utility = UtilityLLMClient()
        self.embeddings = EmbeddingClient()
    
    def get_chat_model(self):
        """Get the current chat model name"""
        return self.chat.model
