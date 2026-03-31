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
        self.model = model or os.getenv("CHAT_MODEL", "qwen/qwen3.5-flash-02-23")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or "https://openrouter.ai/api/v1"
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
                    total_time = time.time() - start_time
                    logger.info(f"LLM chat completed successfully in {total_time:.3f}s")
                    return result["choices"][0]["message"]["content"]
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
            embedding = self._model.encode([text])
            total_time = time.time() - start_time
            logger.info(f"Embedding generated in {total_time:.3f}s")
            return np.array(embedding[0])
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Embedding generation failed after {total_time:.3f}s: {e}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}")
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate batch embeddings using local model with timing"""
        start_time = time.time()
        logger.debug(f"Generating batch embeddings for {len(texts)} texts")
        
        self._load_model()
        try:
            embeddings = self._model.encode(texts)
            total_time = time.time() - start_time
            logger.info(f"Batch embeddings generated in {total_time:.3f}s")
            return np.array(embeddings)
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Batch embedding generation failed after {total_time:.3f}s: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {str(e)}")


class MultiLLM:
    """Multi-model LLM orchestrator"""
    
    def __init__(self, config: dict):
        self.config = config
        self.chat_model = config.get("chat_model", "qwen/qwen3.5-flash-02-23")
        self.utility_model = config.get("utility_model", "qwen/qwen3.5-flash-02-23")
        self.embedding_model = config.get("embedding_model", "all-MiniLM-L6-v2")
        
        # Initialize clients
        api_key = config.get("api_key")
        self.chat_client = LLMClient(self.chat_model, api_key)
        self.utility_client = UtilityLLMClient(self.utility_model, api_key)
        self.embedding_client = EmbeddingClient(self.embedding_model)
        
        logger.info(f"MultiLLM initialized with chat: {self.chat_model}, utility: {self.utility_model}, embedding: {self.embedding_model}")
    
    async def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> str:
        """Chat completion using primary model"""
        return await self.chat_client.chat(messages, tools)
    
    async def chat_complete(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> str:
        """Chat completion using primary model (alias for chat)"""
        return await self.chat(messages, tools)
    
    async def generate(self, messages: List[Dict], max_tokens: int = 512) -> str:
        """Generate text using utility model"""
        return await self.utility_client.generate(messages, max_tokens)
    
    async def generate_query(self, context: str, purpose: str) -> str:
        """Generate a search query for memory retrieval"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates concise search queries based on context."},
            {"role": "user", "content": f"Given this context: {context}\n\nGenerate a concise search query for: {purpose}"}
        ]
        return await self.utility_client.generate(messages, max_tokens=64)
    
    def embed(self, text: str) -> np.ndarray:
        """Generate embedding vector using local model"""
        return self.embedding_client.embed(text)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate batch embeddings using local model"""
        return self.embedding_client.embed_batch(texts)
    
    def get_model_info(self) -> dict:
        """Get information about current models"""
        return {
            "chat_model": self.chat_model,
            "utility_model": self.utility_model,
            "embedding_model": self.embedding_model,
            "embedding_dimension": 384  # Fixed dimension for all-MiniLM-L6-v2
        }

                        result = await response.json()
                        total_time = time.time() - start_time
                        logger.info(f"Utility LLM generation completed in {total_time:.3f}s")
                        return result["choices"][0]["message"]["content"]

            except Exception as e:
                logger.error(f"API request failed: {str(e)}")
                if self.rate_limiter.should_retry(500, str(e)):
                    self.rate_limiter.increment_retry()
                    delay = self.rate_limiter.get_retry_delay()
                    logger.warning(f"API request failed, retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise RuntimeError(f"API call failed: {str(e)}")

        raise RuntimeError(f"Max retries ({self.rate_limiter.max_retries}) exceeded for API")


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
            embedding = self._model.encode([text])
            total_time = time.time() - start_time
            logger.info(f"Embedding generated in {total_time:.3f}s")
            return np.array(embedding[0])
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Embedding generation failed after {total_time:.3f}s: {e}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}")

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate batch embeddings using local model with timing"""
        start_time = time.time()
        logger.debug(f"Generating batch embeddings for {len(texts)} texts")

        self._load_model()
        try:
            embeddings = self._model.encode(texts)
            total_time = time.time() - start_time
            logger.info(f"Batch embeddings generated in {total_time:.3f}s")
            return np.array(embeddings)
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Batch embedding generation failed after {total_time:.3f}s: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {str(e)}")


class MultiLLM:
    """Multi-model LLM orchestrator"""

    def __init__(self, config: dict):
        self.config = config
        self.chat_model = config.get("chat_model", "qwen/qwen3.5-flash-02-23")
        self.utility_model = config.get("utility_model", "qwen/qwen3.5-flash-02-23")
        self.embedding_model = config.get("embedding_model", "all-MiniLM-L6-v2")

        # Initialize clients
        api_key = config.get("api_key")

        # Configure fallback models for rate limiting protection
        fallback_models = [
            "nvidia/nemotron-nano-9b-v2:free",
            "qwen/qwen3.5-flash-02-23",
            "ollama/llama3.2:3b"
        ]

        self.chat_client = LLMClient(self.chat_model, api_key, fallback_models=fallback_models)
        self.utility_client = UtilityLLMClient(self.utility_model, api_key)
        self.embedding_client = EmbeddingClient(self.embedding_model)

        logger.info(f"MultiLLM initialized with chat: {self.chat_model}, utility: {self.utility_model}, embedding: {self.embedding_model}")

    async def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> str:
        """Chat completion using primary model"""
        return await self.chat_client.chat(messages, tools)

    async def chat_complete(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> str:
        """Chat completion using primary model (alias for chat)"""
        return await self.chat(messages, tools)

    async def generate(self, messages: List[Dict], max_tokens: int = 512) -> str:
        """Generate text using utility model"""
        return await self.utility_client.generate(messages, max_tokens)

    async def generate_query(self, context: str, purpose: str) -> str:
        """Generate a search query for memory retrieval"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates concise search queries based on context."},
            {"role": "user", "content": f"Given this context: {context}\n\nGenerate a concise search query for: {purpose}"}
        ]
        return await self.utility_client.generate(messages, max_tokens=64)

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding vector using local model"""
        return self.embedding_client.embed(text)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate batch embeddings using local model"""
        return self.embedding_client.embed_batch(texts)

    def get_model_info(self) -> dict:
        """Get information about current models"""
        return {
            "chat_model": self.chat_model,
            "utility_model": self.utility_model,
            "embedding_model": self.embedding_model,
            "embedding_dimension": 384  # Fixed dimension for all-MiniLM-L6-v2
        }


                        result = await response.json()
                        total_time = time.time() - start_time
                        logger.info(f"Utility LLM generation completed in {total_time:.3f}s")
                        return result["choices"][0]["message"]["content"]

            except Exception as e:
                logger.error(f"API request failed: {str(e)}")
                if self.rate_limiter.should_retry(500, str(e)):
                    self.rate_limiter.increment_retry()
                    delay = self.rate_limiter.get_retry_delay()
                    logger.warning(f"API request failed, retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise RuntimeError(f"API call failed: {str(e)}")

        raise RuntimeError(f"Max retries ({self.rate_limiter.max_retries}) exceeded for API")


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
            embedding = self._model.encode([text])
            total_time = time.time() - start_time
            logger.info(f"Embedding generated in {total_time:.3f}s")
            return np.array(embedding[0])
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Embedding generation failed after {total_time:.3f}s: {e}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}")

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate batch embeddings using local model with timing"""
        start_time = time.time()
        logger.debug(f"Generating batch embeddings for {len(texts)} texts")

        self._load_model()
        try:
            embeddings = self._model.encode(texts)
            total_time = time.time() - start_time
            logger.info(f"Batch embeddings generated in {total_time:.3f}s")
            return np.array(embeddings)
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Batch embedding generation failed after {total_time:.3f}s: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {str(e)}")


class MultiLLM:
    """Multi-model LLM orchestrator"""

    def __init__(self, config: dict):
        self.config = config
        self.chat_model = config.get("chat_model", "qwen/qwen3.5-flash-02-23")
        self.utility_model = config.get("utility_model", "qwen/qwen3.5-flash-02-23")
        self.embedding_model = config.get("embedding_model", "all-MiniLM-L6-v2")

        # Initialize clients
        api_key = config.get("api_key")

        # Configure fallback models for rate limiting protection
        fallback_models = [
            "nvidia/nemotron-nano-9b-v2:free",
            "qwen/qwen3.5-flash-02-23",
            "ollama/llama3.2:3b"
        ]

        self.chat_client = LLMClient(self.chat_model, api_key, fallback_models=fallback_models)
        self.utility_client = UtilityLLMClient(self.utility_model, api_key)
        self.embedding_client = EmbeddingClient(self.embedding_model)

        logger.info(f"MultiLLM initialized with chat: {self.chat_model}, utility: {self.utility_model}, embedding: {self.embedding_model}")

    async def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> str:
        """Chat completion using primary model"""
        return await self.chat_client.chat(messages, tools)

    async def chat_complete(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> str:
        """Chat completion using primary model (alias for chat)"""
        return await self.chat(messages, tools)

    async def generate(self, messages: List[Dict], max_tokens: int = 512) -> str:
        """Generate text using utility model"""
        return await self.utility_client.generate(messages, max_tokens)

    async def generate_query(self, context: str, purpose: str) -> str:
        """Generate a search query for memory retrieval"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates concise search queries based on context."},
            {"role": "user", "content": f"Given this context: {context}\n\nGenerate a concise search query for: {purpose}"}
        ]
        return await self.utility_client.generate(messages, max_tokens=64)

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding vector using local model"""
        return self.embedding_client.embed(text)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate batch embeddings using local model"""
        return self.embedding_client.embed_batch(texts)

    def get_model_info(self) -> dict:
        """Get information about current models"""
        return {
            "chat_model": self.chat_model,
            "utility_model": self.utility_model,
            "embedding_model": self.embedding_model,
            "embedding_dimension": 384  # Fixed dimension for all-MiniLM-L6-v2
        }
