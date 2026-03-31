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
from sentence_transformers import SentenceTransformer
import asyncio


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
    """Multi-LLM layer that routes tasks to appropriate models"""
    
    def __init__(
        self,
        config: dict = None,
        chat_model: str = None,
        utility_model: str = None,
        embedding_model: str = None
    ):
        if config:
            chat_model = chat_model or config.get('chat_model')
            utility_model = utility_model or config.get('utility_model')
            embedding_model = embedding_model or config.get('embedding_model')
        
        logger.info(f"MultiLLM initialized - Chat: {chat_model}, Utility: {utility_model}, Embedding: {embedding_model}")
        
        self.chat = LLMClient(model=chat_model)
        self.utility = UtilityLLMClient(model=utility_model)
        self.embedding = EmbeddingClient()  # Offline, no model needed usually
    
    async def chat_complete(self, messages: List[Dict]) -> str:
        """Expensive model for reasoning - use sparingly"""
        logger.info("MultiLLM: Starting expensive chat completion")
        return await self.chat.chat(messages)
    
    async def summarize(self, text: str, prompt: str = None) -> str:
        """Cheap model for summarization tasks"""
        start_time = time.time()
        logger.info(f"MultiLLM: Starting summarization task")
        
        if not prompt:
            prompt = f"Summarize this concisely in 2 paragraphs:\n{text}"
        
        try:
            result = await self.utility.generate([{"role": "user", "content": prompt}])
            total_time = time.time() - start_time
            logger.info(f"MultiLLM: Summarization completed in {total_time:.3f}s")
            return result
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"MultiLLM: Summarization failed after {total_time:.3f}s: {e}")
            raise
    
    async def generate_query(self, context: str, task: str) -> str:
        """Cheap model to generate search queries for memory recall"""
        start_time = time.time()
        logger.info(f"MultiLLM: Starting query generation for task: {task}")
        
        prompt = f"""You are a memory retrieval specialist. Analyze this context and generate a precise search query to find relevant stored memories.

Context: {context}

Generate a search query (1-2 sentences) that will match relevant memories."""
        
        try:
            result = await self.utility.generate([{"role": "user", "content": prompt}])
            total_time = time.time() - start_time
            logger.info(f"MultiLLM: Query generation completed in {total_time:.3f}s")
            return result
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"MultiLLM: Query generation failed after {total_time:.3f}s: {e}")
            raise
    
    def embed(self, text: str) -> np.ndarray:
        """Offline embedding - no API cost"""
        logger.debug("MultiLLM: Starting offline embedding")
        return self.embedding.embed(text)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Offline batch embedding - no API cost"""
        logger.debug(f"MultiLLM: Starting batch embedding for {len(texts)} texts")
        return self.embedding.embed_batch(texts)