"""LLM Client for OpenRouter API"""

import json
import time
import logging
import requests
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, endpoint: str, api_key: str, model: str, timeout: int = 30):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Synchronous chat call to OpenRouter"""
        url = f"{self.endpoint}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/dusty-schmidt/gob",
            "X-Title": "GOB-GOB Agent",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
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
