"""
LLM Client layer for GOB
Provides chat and embedding clients via OpenRouter + local sentence-transformers
"""

import os
import aiohttp
import logging
import time
from typing import Dict, List, Optional
import numpy as np
import warnings

# Suppress noisy library warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub.file_download").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


class LLMClient:
    """Chat model client - talks to OpenRouter (or any OpenAI-compatible API)"""

    def __init__(self, model: str = None, api_key: str = None, base_url: str = None):
        self.model = model or os.getenv("CHAT_MODEL", "openai/gpt-3.5-turbo")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self.timeout = 60

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages to the LLM and return the response text"""
        start_time = time.time()
        logger.info(f"LLM request: model={self.model}, messages={len(messages)}")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/dusty-schmidt/gob-01",
            "X-Title": "GOB Agent"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.7
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url, json=payload, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    elapsed = time.time() - start_time

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        raise RuntimeError(f"API error {response.status}: {error_text}")

                    result = await response.json()

                    # Extract content
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"]
                    elif "message" in result:
                        content = result["message"]["content"]
                    else:
                        raise RuntimeError(f"Unexpected API response: {result}")

                    logger.info(f"LLM responded in {elapsed:.1f}s")
                    return content

            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"LLM call failed after {elapsed:.1f}s: {e}")
                raise RuntimeError(f"LLM call failed: {str(e)}")


class EmbeddingClient:
    """Local embedding model using sentence-transformers"""

    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model_name = model
        self._model = None
        logger.info(f"EmbeddingClient initialized (model: {self.model_name})")

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.debug(f"Loading embedding model: {self.model_name}")
                load_start = time.time()
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Embedding model loaded in {time.time() - load_start:.1f}s")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Failed to load embedding model: {str(e)}")

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding vector"""
        self._load_model()
        return self._model.encode(text)


class MultiLLM:
    """Multi-model LLM manager - the single interface orchestrator talks to"""

    def __init__(self, config: dict = None):
        config = config or {}

        # Chat model
        chat_model = config.get("chat_model", os.getenv("CHAT_MODEL", "openai/gpt-3.5-turbo"))
        api_key = config.get("api_key", os.getenv("OPENROUTER_API_KEY"))
        base_url = config.get("endpoint", "https://openrouter.ai/api/v1")

        # Embedding model (local, no API cost)
        embedding_model = config.get("embedding_model", "all-MiniLM-L6-v2")

        logger.info(f"MultiLLM: chat={chat_model}, embeddings={embedding_model}")

        self.chat_client = LLMClient(model=chat_model, api_key=api_key, base_url=base_url)
        self.embedding = EmbeddingClient(model=embedding_model)
        self.chat_model = chat_model

    async def chat_complete(self, messages: List[Dict[str, str]]) -> str:
        """Chat completion"""
        return await self.chat_client.chat(messages)

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embeddings"""
        return self.embedding.embed(text)
