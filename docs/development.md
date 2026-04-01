# Development Guide

## Prerequisites

- Python 3.9+
- An OpenRouter API key ([get one free](https://openrouter.ai/keys))
- Git

## Setup

```bash
git clone https://github.com/dusty-schmidt/gob.git
cd gob
echo 'OPENROUTER_API_KEY=sk-or-your-key-here' > .env
pip install -e .
```

## Run

```bash
python -m gob.run_gob --tui
```

Or with Docker:
```bash
docker compose -f docker/docker-compose.yml up --build
```

## Project Layout

```
gob/
├── config/                 # Configuration files
│   ├── config.yaml         # System config (model, provider, tools)
│   └── agents/
│       └── default.yaml    # Agent personality and behavior
├── docker/                 # Docker configuration
├── docs/                   # Documentation (you are here)
├── src/gob/                # Source code
│   ├── run_gob.py          # Entry point
│   ├── core/               # Core logic
│   ├── ux/                 # User interfaces
│   └── tools/              # Agent tools
├── tests/                  # Test suite
├── .env                    # API keys (not committed)
├── pyproject.toml          # Python package config
└── VERSION                 # Current version
```

## Git Workflow

Solo dev workflow — simple and honest:

```bash
# Start a fix or feature
git checkout -b fix/description-of-change

# Make your changes, then:
git add -A
git commit -m "fix: what you changed"
git checkout main
git merge fix/description-of-change
git branch -d fix/description-of-change
git push origin main
```

**Versioning:** Commit freely, tag releases only when you hit a milestone.
```bash
# When you've reached a meaningful release:
git tag v1.1.0
git push origin v1.1.0
```

## Changing the Model

Edit `config/config.yaml`:
```yaml
llm:
  chat_model: qwen/qwen3.6-plus-preview:free   # change this
```

Browse available models at [openrouter.ai/models](https://openrouter.ai/models). Free models have `:free` suffix.

## Adding a New Tool

1. Create `src/gob/tools/your_tool.py` with an `execute()` function
2. Add the tool name to `config/config.yaml` under `tools.enabled`
3. Add the tool name to `config/agents/default.yaml` under `tools`
4. The orchestrator will auto-load it

## Useful Make Commands

```bash
make help     # Show available commands
make clean    # Remove __pycache__ and build artifacts
make test     # Run test suite
make status   # Git status check
```