# GOB-01

AI agent that uses Discord as the bridge for collaboration between agents and humans.

## Install
```bash
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-01/main/scripts/install.sh | bash
```

## Usage
```bash
gob            # TUI chat
gob --discord  # Discord bot
```

## Features
- TUI chat
- Discord bot
- Semantic memory
- Multi-LLM routing
- Local embeddings

## Config
- `~/.gob/.env` - API keys
- `~/.gob/config/config.yaml` - Models, tools, behavior

## Docs
See docs/ for configuration, tools, FAQ, and development.