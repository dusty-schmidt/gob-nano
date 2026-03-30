"""
Multi-model LLM client layer for GOB-01
Provides chat, utility, and embedding clients
"""
import os
import json
import logging
import aiohttp
import requests
from typing import Dict, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import asyncio

logger = logging.getLogger(__name__)


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

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logger.error(f"LLM request failed: {e}")
                return {
                    "error": str(e),
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": f"I encountered an error while communicating with the LLM: {e}"
                        }
                    }]
                }

    async def chat_stream(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None):
        """Streaming chat call (placeholder implementation)"""
        response = await self.chat(messages, tools)
        if "error" in response:
            yield response["error"]
        else:
            yield response["choices"][0]["message"].get("content", "")

    def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate embeddings via Ollama or OpenRouter.
        If using Ollama locally, endpoint would change to localhost:11434
        """
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model or "nomic-embed-text",
            "input": text,
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
