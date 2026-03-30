"""OpenRouter LLM Client for NANO"""
import os
import json
import requests
from typing import List, Dict, Any, Optional, Generator


class LLMClient:
    """Client for OpenRouter API"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.endpoint = config.get('endpoint', 'https://openrouter.ai/api/v1')
        self.model = config.get('model', 'qwen/qwen3.5-flash-02-23')
        self.api_key = config.get('api_key') or os.getenv('OPENROUTER_API_KEY')
        self.max_tokens = config.get('max_tokens', 4096)
        self.temperature = config.get('temperature', 0.7)

        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send chat completion request to OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/dusty-schmidt/gob-nano",
            "X-Title": "GOB-NANO Agent"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            response = requests.post(
                f"{self.endpoint}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise RuntimeError("LLM request timed out after 120 seconds")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"LLM request failed: {e}")

    def chat_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Stream chat completion from OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/dusty-schmidt/gob-nano",
            "X-Title": "GOB-NANO Agent"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": True
        }

        try:
            response = requests.post(
                f"{self.endpoint}/chat/completions",
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                        except (json.JSONDecodeError, KeyError):
                            continue
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"LLM stream failed: {e}")
