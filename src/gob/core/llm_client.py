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

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM request failed: {e}")
            # Return a structured error response instead of crashing
            return {
                "error": str(e),
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": f"I encountered a network error while communicating with the LLM: {e}"
                    }
                }]
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {
                "error": str(e),
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "I received an invalid response from the LLM service."
                    }
                }]
            }

    def chat_stream(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None):
        """Streaming chat call (placeholder implementation)"""
        # For now, falls back to standard chat, can be implemented with requests stream=True
        response = self.chat(messages, tools)
        if "error" in response:
            yield response["error"]
        else:
            yield response["choices"][0]["message"].get("content", "")

    def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate embeddings via Ollama or OpenRouter.
        If using Ollama locally, endpoint would change to localhost:11434
        """
        url = f"{self.endpoint}/embeddings"
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
