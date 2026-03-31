#!/usr/bin/env python3
"""
Fix for GOB-01 embedding issues
This script configures the system to use local embeddings instead of OpenRouter API
"""

import os
import json
from pathlib import Path

# Set environment variables to use local embeddings
os.environ['EMBEDDING_MODEL'] = 'all-MiniLM-L6-v2'
os.environ['EMBEDDING_PROVIDER'] = 'huggingface'

# Create a local embedding configuration
config_dir = Path('/a0/usr/projects/gob/.a0proj/memory')
config_dir.mkdir(parents=True, exist_ok=True)

# Update embedding configuration
embedding_config = {
    "model_provider": "huggingface",
    "model_name": "all-MiniLM-L6-v2",
    "local": True,
    "device": "cpu"
}

with open(config_dir / 'embedding.json', 'w') as f:
    json.dump(embedding_config, f, indent=2)

# Create a local model configuration
local_model_config = {
    "embedding_model": {
        "name": "all-MiniLM-L6-v2",
        "provider": "huggingface",
        "local": True,
        "device": "cpu"
    }
}

with open(config_dir / 'local_model_config.json', 'w') as f:
    json.dump(local_model_config, f, indent=2)

print("✓ Embedding configuration updated to use local models")
print("✓ Configuration files created in .a0proj/memory/")
print("✓ System will now use local sentence-transformers for embeddings")

# Test the embedding setup
print("\nTesting embedding setup...")
try:
    from gob.core.llm_client import EmbeddingClient
    embed_client = EmbeddingClient()
    test_embedding = embed_client.embed("test")
    print(f"✓ Local embedding test successful: shape={test_embedding.shape}")
except Exception as e:
    print(f"✗ Local embedding test failed: {e}")
    print("  You may need to install sentence-transformers: pip install sentence-transformers")