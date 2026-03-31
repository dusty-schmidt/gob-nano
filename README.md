# GOB - AI Agent

A lean AI agent with TUI chat interface.

## Quick Start

```bash
git clone https://github.com/dusty-schmidt/gob-01.git
cd gob-01
pip install -e .
python -m gob.main --tui
```

## Features

- **TUI Chat**: Terminal interface with clean help display
- **5 Core Tools**: code_execution, text_editor, response, search_engine, document_query
- **AI Orchestration**: Multi-model support via Ollama Cloud API
- **Memory System**: Semantic memory with FAISS embeddings
- **Configuration**: Ollama API with llama3.2:3b models

## Usage

```bash
# TUI mode
python -m gob.main --tui

# Version info
python -m gob.main --version

# Help
python -m gob.main --help
```

## Configuration

Configure Ollama API in `.env`:
```
OLLAMA_CLOUD_API_KEY=your_key_here
```

Configure agent behavior in `config/config.yaml`:
```yaml
agent_name: gob
profile: default
llm:
  api_key: ${OLLAMA_CLOUD_API_KEY}
  endpoint: https://api.ollama.com/v1
  chat_model: llama3.2:3b
```

## Version

Current version: 0.2.4

## License

MIT
