# gob

Minimal AI agent framework. A template you build from in any direction.

## Philosophy

- **Computer as THE tool** — runs in a Linux container with full system access
- **Minimalism as THE template** — no framework lock-in, grows to suit your needs
- **No two gobs end up the same** — it evolves with you

## Quick Start

```bash
git clone https://github.com/dusty-schmidt/gob.git
cd gob
```

Create your `.env` file with your OpenRouter API key:

```bash
echo 'OPENROUTER_API_KEY=sk-or-your-key-here' > .env
```

Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys)

### Run with Docker (recommended)

```bash
docker compose -f docker/docker-compose.yml up --build
```

### Run locally (for tinkering)

```bash
pip install -e .
python -m gob.run_gob --tui
```

## Structure

```
src/gob/
├── run_gob.py          # Entry point
├── core/
│   ├── config_loader   # YAML config
│   ├── llm_client      # LLM API (OpenRouter)
│   ├── memory/         # SQLite + optional vector search
│   ├── orchestrator    # Agent loop: prompt → LLM → tool → repeat
│   └── tool_loader     # Dynamic tool import
├── ux/
│   └── tui_chat        # Terminal chat interface
└── tools/
    ├── response        # Send text to user
    ├── code_execution  # Run Python/bash
    ├── search_engine   # Web search (DuckDuckGo)
    ├── text_editor     # Read/write files
    └── document_query  # Parse documents
```

## Configuration

- `config/config.yaml` — System settings (LLM provider, model, API endpoint)
- `config/agents/default.yaml` — Agent personality (system prompt, behavior)
- `.env` — Secrets (API keys)

## Version

1.0.0

## License

MIT
