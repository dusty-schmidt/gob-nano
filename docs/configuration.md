# Configuration

Config files:
- `config/config.yaml` - Main settings
- `.env` - API keys
- `config/agents/*.yaml` - Agent configs

## config/config.yaml
```yaml
agent:
  name: gob
  profile: default

llm:
  provider: openrouter
  chat_model: qwen/qwen3.5-flash-02-23
  api_key: ${OPENROUTER_API_KEY}

tools:
  enabled:
    - response
    - search_engine
    - code_execution
    - text_editor
    - document_query
```

## .env
```bash
OPENROUTER_API_KEY=your_key
DISCORD_BOT_TOKEN=your_token
```

## Custom Agents
Create `config/agents/your-agent.yaml`:
```yaml
name: "Your Agent"
context: |
  You are a specialized assistant.
```

## Validate Config
```bash
python -m gob.main --mode validate
```