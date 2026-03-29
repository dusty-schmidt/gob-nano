# Mini-Agent-Zero Nano

Ultra-minimal agent for edge devices (4-8GB RAM)

## Quick Start

```bash
# Build container
docker-compose build

# Run agent
docker-compose up
```

## Structure

```
nano/
├── Dockerfile           # Container setup
├── docker-compose.yml   # Container orchestration
├── requirements.txt     # 11 dependencies
├── config.yaml          # System configuration
├── agents/              # Agent YAML configs
│   └── default.yaml
├── tools/               # Essential tools
│   ├── response.py
│   └── search_engine.py
├── helpers/              # Helper modules
└── main.py              # Entry point
```

## Features

- Minimal dependencies (~150MB)
- Fast startup (~15s)
- Terminal access via Docker exec
- YAML-based agent configs
- JSON memory (no FAISS)

## Terminal Access

```bash
# Enter container shell
docker exec -it mini-agent-zero /bin/bash

# Install additional packages
pip install <package-name>
apt-get install <package-name>
```

## Configuration

Edit `config.yaml` to customize:

- LLM provider and model
- Enabled tools
- Agent settings
- Memory options

## Creating Custom Agents

1. Create new YAML in `agents/`:

```yaml
name: "Custom Agent"
description: "My custom agent"
model:
  provider: "openrouter"
  name: "qwen/qwen3.5-flash-02-23"
tools:
  - response
  - search_engine
  - code_execution
context: |
  Your system prompt here.
```

2. Update `config.yaml`:

```yaml
agent:
  default_profile: "custom"  # matches filename
```

3. Restart container

## Requirements

- Docker
- 4-8GB RAM
- Linux/x86_64
