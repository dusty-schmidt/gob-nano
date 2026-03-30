# Configuration

Customize gob's behavior and capabilities.

## Project Overview

Gob runs in a minimal configuration with room for expansion. The entire system is driven by YAML configuration files.

## Configuration Files

### config/config.yaml

The main configuration file controls system-wide settings:

```yaml
# NANO Configuration
# Secrets are loaded from .env file

agent:
  name: gob
  profile: default

discord:
  token: ${DISCORD_BOT_TOKEN}
  prefix: !

llm:
  provider: openrouter
  endpoint: https://openrouter.ai/api/v1
  model: qwen/qwen3.5-flash-02-23
  api_key: ${OPENROUTER_API_KEY}
  max_tokens: 4096
  temperature: 0.7

tools:
  enabled:
    - response
    - search_engine
    - code_execution
    - text_editor
    - document_query
  disabled: []
```

#### Key Settings

| Field | Default | Description |
|-------|---------|-------------|
| `agent.name` | `gob` | Display name for the bot |
| `agent.profile` | `default` | Which agent config to load |
| `llm.model` | `qwen/qwen3.5-flash-02-23` | LLM model to use |
| `llm.temperature` | `0.7` | Creativity level (0.0-2.0) |
| `llm.max_tokens` | `4096` | Maximum response tokens |
| `tools.enabled` | 5 tools | Which tools are available |

## Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys
OPENROUTER_API_KEY=your_openrouter_key_here
DISCORD_BOT_TOKEN=your_discord_token_here

# Optional settings
LLM_TEMPERATURE=0.7
MAX_TOKENS=4096
```

The system loads variables from `.env` automatically.

## Agent Configuration

Agents are defined in `config/agents/` as YAML files:

### config/agents/default.yaml

```yaml
name: "Default Agent"
description: "General purpose AI assistant"

model:
  provider: "openrouter"
  name: "qwen/qwen3.5-flash-02-23"
  max_tokens: 4096
  temperature: 0.7

context: |
  You are a helpful AI assistant.
  Execute tasks efficiently.
  Use tools when needed.
  Be concise but thorough.

tools:
  - response
  - search_engine
  - code_execution
  - text_editor
  - document_query
```

### Create Custom Agents

To create a new agent, add a YAML file to the agents directory:

**config/agents/coder.yaml**

```yaml
name: "Coder Agent"
description: "Specialized for software development"

model:
  provider: "openrouter"
  name: "qwen/qwen3.5-flash-02-23"

context: |
  You are a software development assistant.
  Write production-quality code.
  Focus on security and best practices.

settings:
  max_iterations: 30
  temperature: 0.5
```

Gob auto-discovers all YAML files at startup.

## Runtime Configuration

Run with validation to check your configuration:

```bash
python -m gob.main --mode validate
```

This verifies:
- ✅ Config loads correctly
- ✅ Agent profile loads
- ✅ Memory initializes
- ✅ LLM is configured
- ✅ All tools are available

## Customizing Behavior

### Adjust LLM Creativity

```yaml
llm:
  temperature: 0.3  # More deterministic
  # or
  temperature: 1.2  # More creative
```

### Change Output Length

```yaml
llm:
  max_tokens: 2048  # Shorter responses
  # or
  max_tokens: 8192  # Longer responses
```

### Enable/Disable Tools

Disable unused tools for faster startup:

```yaml
tools:
  enabled:
    - response
    - code_execution
  disabled:
    - search_engine
    - document_query
```

---

**Next:** See [available tools](tools.md) or [contribute to development](development.md)
