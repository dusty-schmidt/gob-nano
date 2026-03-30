# GOB-NANO

**Ultra-minimal AI agent framework for edge devices (4-8GB RAM)**

Agent Zero's stripped-down cousin. All capability, minimal bloat. Runs on old laptops and embedded systems.

## Quick Start

### One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-nano/main/scripts/install.sh | bash
```

This will:
- Clone to `~/.nano`
- Create a Python venv
- Install the package
- Create a `.env` template

### First Run

```bash
# Activate venv
source ~/.nano/venv/bin/activate

# Edit .env with your API keys
nano ~/.nano/.env

# Run the agent
python -m nano.main
```

## Architecture

### Four-Layer Stack

```
┌──────────────┐
│     USER     │  Discord / Telegram / CLI
├──────────────┤
│ ORCHESTRATOR │  Routes tasks, manages flow
├──────────────┤
│      LLM     │  OpenRouter (qwen3.5-flash)
├──────────────┤
│     TOOLS    │  5 core + runtime expandable
└──────────────┘
```

### Core Components

| Component | Purpose | Details |
|-----------|---------|----------|
| **main.py** | Entry point | Validates config, loads agent, initializes memory |
| **config.yaml** | System settings | LLM provider, tools, agent profile |
| **.env** | Secrets | API keys (never in git) |
| **agents/** | Agent profiles | YAML-based agent definitions |
| **memory.jsonl** | Persistent memory | Lightweight JSONL, no vector DB |
| **tools/** | Core capabilities | response, search_engine, code_execution, text_editor, document_query |

## Features

✅ **Minimal Dependencies** (~12 core packages)  
✅ **Fast Startup** (~15 seconds)  
✅ **Low RAM Usage** (~100MB idle)  
✅ **YAML Agent Configs** (runtime discoverable)  
✅ **JSONL Memory** (no FAISS overhead)  
✅ **Runtime Expandable** (install packages on-demand)  
✅ **Full Terminal Access** (curl, pip, apt-get available)  
✅ **Comprehensive Tests** (22 tests, 100% passing)  

## Configuration

### config.yaml

```yaml
agent:
  name: nano_agent
  profile: default          # Which agent to load

llm:
  provider: openrouter
  model: qwen/qwen3.5-flash-02-23
  api_key: ${OPENROUTER_API_KEY}  # Loaded from .env

tools:
  enabled:
    - response
    - search_engine
    - code_execution
    - text_editor
    - document_query
```

### .env

```bash
OPENROUTER_API_KEY=your_api_key_here
DISCORD_BOT_TOKEN=your_token_here
```

### Agents (config/agents/)

Create custom agents by adding YAML files:

```yaml
# agents/my_agent.yaml
name: My Custom Agent
description: Specialized for XYZ tasks
model: qwen/qwen3.5-flash-02-23
context: |
  You are specialized in XYZ...
tools:
  - response
  - code_execution
```

The agent auto-discovers YAML files at startup.

## Project Structure

```
gob-nano/
├── src/nano/
│   ├── main.py              # Entry point
│   ├── tools/               # 5 core tools
│   ├── helpers/             # Config, agent, memory loaders
│   └── data/                # Runtime data (memory.jsonl)
├── config/
│   ├── config.yaml          # Main settings
│   └── agents/              # Agent profiles
├── tests/                   # 22 unit tests
├── scripts/                 # Build, setup, test
├── docker/                  # Container setup
├── .env                     # Secrets (git-ignored)
└── pyproject.toml           # Python package config
```

## Development

### Install for Development

```bash
git clone git@github.com:dusty-schmidt/gob-nano.git
cd gob-nano
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Run Tests

```bash
pytest tests/ -v
```

All 22 tests should pass:
- 5 config loading tests
- 4 memory tests
- 2 tool loader tests
- 2 agent loader tests
- 5 tool existence tests
- 4 main.py integration tests

### Make Commands

```bash
make install    # Install in editable mode
make test       # Run pytest
make lint       # Code quality checks
make clean      # Remove build artifacts
make build      # Build Docker image
make run        # Start Docker container
```

## Running the Agent

### Validation Mode (current)

```bash
python -m nano.main
```

Validates:
- ✅ Config loads
- ✅ Agent profile loads
- ✅ Memory initializes
- ✅ LLM is configured
- ✅ All tools are available

### Discord Bot (coming soon)

Implement Discord handlers in `main.py` to run as a bot service.

### Interactive REPL (coming soon)

Implement REPL interface for direct terminal interaction.

## Philosophy

### Minimalism is a Feature

- **12 core files** (vs 50+ in Agent Zero)
- **~500MB container** (vs 1GB+ in Agent Zero)
- **5 core tools** initially (agent adds more as needed)
- **JSONL memory** (saves 100MB+ on startup)

### The Computer IS Your Tool

The agent runs in a **full Linux container** with:
- `apt-get` access
- `pip` access
- Full terminal commands
- Access to all Arch/Debian repositories

**What this means:** You DON'T need to bundle everything. The agent installs packages at runtime when tasks require them.

```python
# Example: Agent needs to parse PDFs
# Instead of bundling pypdf, the agent detects it needs it and runs:
# apt-get install -y python3-pypdf  OR  pip install pypdf
```

### YAML Configs Over Code

Agents are **YAML files**, not directories of Python:
- ✅ User-editable (no coding required)
- ✅ Runtime auto-discovery (drop a YAML file, agent appears)
- ✅ Simple and human-readable
- ✅ Easy to version control

## Expanding Capabilities

The agent can install additional tools at runtime:

```bash
# Install PDF parsing
pip install pypdf
apt-get install -y poppler-utils

# Install browser automation
pip install playwright
playwright install chromium

# Install database drivers
pip install sqlite3 psycopg2
```

Memory can note what's been installed for future reference.

## Design Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|----------|
| YAML agents | Runtime discovery, user-editable | Less flexible than code |
| JSONL memory | Simple, tiny footprint | No semantic search (yet) |
| OpenRouter API | External LLM, no local setup | Requires internet/API key |
| Minimal tools | Fast startup, low RAM | Install more on-demand |
| No FAISS | Saves 100MB+ RAM | Slower memory search |

## Testing

**22 comprehensive tests** with zero external dependencies:

```bash
pytest tests/ -v
# Configuration loading (5 tests)
# Memory operations (4 tests)
# Tool loading (2 tests)
# Agent loading (2 tests)
# Tool existence (5 tests)
# Main.py integration (4 tests)
```

All tests mock external dependencies — no LLM calls, no external APIs.

## Troubleshooting

### "Config file not found"

```bash
# Ensure you're in the project root
cd ~/.nano
python -m nano.main
```

### "API key not configured"

```bash
# Edit .env
nano .env
# Add your OPENROUTER_API_KEY
```

### "Tool not found"

Install at runtime:
```bash
source venv/bin/activate
pip install <package-name>
```

## Contributing

1. Tests must pass: `pytest tests/ -v`
2. Root directory must stay clean (no .py or .sh scripts)
3. Keep dependencies minimal
4. Use YAML for agent definitions
5. Document why you're NOT bundling something

## License

MIT (same as Agent Zero)

## Resources

- **GitHub:** https://github.com/dusty-schmidt/gob-nano
- **Agent Zero:** https://github.com/A2-ai/agent-zero
- **OpenRouter:** https://openrouter.ai

## Quick Reference

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-nano/main/scripts/install.sh | bash

# Setup
cd ~/.nano
source venv/bin/activate
nano .env          # Add API key

# Run
python -m nano.main

# Test
pytest tests/ -v

# Develop
git clone git@github.com:dusty-schmidt/gob-nano.git
cd gob-nano
pip install -e .
pytest tests/ -v
```

---

**Status:** Production-ready • **Tests:** 22/22 passing • **Last updated:** 2026-03-29
### Test commit by Gob agent - 2026-03-29
