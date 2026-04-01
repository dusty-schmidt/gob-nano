# Configuration Reference

GOB uses three configuration sources with clear separation of concerns.

## config/config.yaml — System Settings

Controls the plumbing: what LLM, what endpoint, what tools are available.

```yaml
agent:
  name: gob                    # Agent name
  profile: default             # Which agent profile to load

default_mode: tui              # Default launch mode

llm:
  api_key: ${OPENROUTER_API_KEY}           # Resolved from environment
  endpoint: https://openrouter.ai/api/v1   # API base URL
  max_tokens: 4096                         # Max response length
  temperature: 0.7                         # Creativity (0.0-1.0)
  chat_model: qwen/qwen3.6-plus-preview:free  # Model to use
  embedding_model: all-MiniLM-L6-v2        # Local embedding model

tools:
  enabled:                     # Tools available system-wide
    - response
    - search_engine
    - code_execution
    - text_editor
    - document_query
  disabled: []                 # Explicitly disabled tools
```

### Environment Variable Resolution

Config values like `${OPENROUTER_API_KEY}` are resolved from:
1. Environment variables
2. `.env` file in project root

## config/agents/default.yaml — Agent Personality

Controls who the agent IS: personality, system prompt, behavior settings.

```yaml
name: "gob"
description: "Minimal AI assistant for edge devices"

context: >-                    # This becomes the system prompt
  You are gob, a minimal AI assistant...

tools:                         # Which tools THIS agent can use
  - response
  - code_execution

settings:
  max_iterations: 20           # Max tool-use loops per message
  retry_on_error: true         # Retry on tool failures
  auto_suggest_tools: true     # LLM can suggest tools proactively

preferences:
  verbose_outputs: false       # Concise vs detailed responses
```

### Multiple Agent Profiles

Create additional profiles in `config/agents/`:
```
config/agents/
├── default.yaml          # General-purpose agent
├── coder.yaml            # Code-focused agent (future)
└── researcher.yaml       # Research-focused agent (future)
```

Switch profiles in `config.yaml`:
```yaml
agent:
  profile: coder
```

## .env — Secrets

API keys and sensitive values. Never committed to git.

```bash
OPENROUTER_API_KEY=sk-or-your-key-here
```

## Precedence

`config.yaml` defines system defaults. The agent profile can reference tools but cannot override the model — that's a system-level decision.
