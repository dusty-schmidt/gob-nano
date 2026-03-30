"""
Multi-model LLM client layer for GOB-01
Provides chat, utility, and embedding clients
"""
import os
import aiohttp
from typing import Dict, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import asyncio


class LLMClient:
    """Primary chat model client"""
    
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None):
        self.model = model or os.getenv("CHAT_MODEL", "openrouter/qwen/qwen3.5-flash-02-23")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self.timeout = 60
        
        # Validation
        if not self.api_key and "openrouter" in self.model:
            # We allow initialization without key, but warn/fail on usage
            pass
    
    async def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> str:
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
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise RuntimeError(f"API error: {response.status} - {error_text}")
                    
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
            except Exception as e:
                raise RuntimeError(f"LLM call failed: {str(e)}")


class UtilityLLMClient:
    """Cheap utility model for memory tasks"""
    
    def __init__(self, model: str = None, api_key: str = None):
        # Local Ollama model (free, fast for utility tasks)
        self.model = model or os.getenv("UTILITY_MODEL", "ollama/llama3.2:1b")
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.api_key = api_key
        
    async def generate(self, messages: List[Dict], max_tokens: int = 512) -> str:
        if "ollama" in self.model:
            # Ollama API call
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.model.replace("ollama/", ""),
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": max_tokens}
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()
                    return result["message"]["content"]
        else:
            # Fallback to standard OpenAI-like API (assuming generic utility model)
            url = f"{self.base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]


class EmbeddingClient:
    """Local embedding model using sentence-transformers"""
    
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model = model
        self._model = None
    
    def _load_model(self):
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model)
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Failed to load embedding model: {str(e)}")
    
    def embed(self, text: str) -> np.ndarray:
        """Generate embedding vector using local model"""
        self._load_model()
        try:
            embedding = self._model.encode([text])
            return np.array(embedding[0])
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}")
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate batch embeddings using local model"""
        self._load_model()
        try:
            embeddings = self._model.encode(texts)
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
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
        
        self.chat = LLMClient(model=chat_model)
        self.utility = UtilityLLMClient(model=utility_model)
        self.embedding = EmbeddingClient()  # Offline, no model needed usually
    
    async def chat_complete(self, messages: List[Dict]) -> str:
        """Expensive model for reasoning - use sparingly"""
        return await self.chat.chat(messages)
    
    async def summarize(self, text: str, prompt: str = None) -> str:
        """Cheap model for summarization tasks"""
        if not prompt:
            prompt = f"Summarize this concisely in 2 paragraphs:\n{text}"
        
        return await self.utility.generate([{"role": "user", "content": prompt}])
    
    async def generate_query(self, context: str, task: str) -> str:
        """Cheap model to generate search queries for memory recall"""
        prompt = f"""You are a memory retrieval specialist. Analyze this context and generate a precise search query to find relevant stored memories.

Context: {context}

Generate a search query (1-2 sentences) that will match relevant memories."""
        
        return await self.utility.generate([{"role": "user", "content": prompt}])
    
    def embed(self, text: str) -> np.ndarray:
        """Offline embedding - no API cost"""
        return self.embedding.embed(text)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        return self.embedding.embed_batch(texts)