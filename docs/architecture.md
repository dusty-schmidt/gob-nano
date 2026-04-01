# Architecture

## Overview

gob is a loop: **User → Orchestrator → LLM → (optional: Tool) → User**

```
┌─────────────┐     ┌──────────────────┐     ┌───────────────┐
│  TUI Chat   │────▶│  Orchestrator    │────▶│  OpenRouter   │
│  (gob/ux/)  │◀────│  (gob/core/)     │◀────│  LLM API      │
└─────────────┘     └────────┬─────────┘     └───────────────┘
                             │
                    ┌────────┼─────────┐
                    ▼        ▼         ▼
               ┌────────┐ ┌────────┐ ┌────────┐
               │ Tools  │ │ Memory │ │ Config │
               │ (exec, │ │(SQLite)│ │ (YAML) │
               │ search)│ │        │ │        │
               └────────┘ └────────┘ └────────┘
```

## Safety

GOB is built with a self-protecting architecture. It prevents the agent from damaging its own environment by enforcing four pillars:

1. **Isolation** — Code execution runs inside a resource-capped Docker container (`512MB RAM`, `1 CPU`). Infinite loops or memory leaks cannot brick the host.
2. **Validation** — Every tool is contract-checked (docstrings, signatures) before loading. Merges require syntax and test gates.
3. **Autopsy** — Failures produce structured reports (`Exit Code → Classification → Suggested Recovery`) which are injected back into the agent's context, forcing adaptation.
4. **Automated Merge** — Code is never written directly to `main`. Changes land on feature branches, pass validation inside the sandbox, and merge only on success.

---

## Directory Structure

```
src/gob/
├── run_gob.py              # Entry point — parses args, wires components
├── core/
│   ├── orchestrator.py     # The agent loop — sends messages, handles tools
│   ├── llm_client.py       # LLM API client (OpenRouter) + local embeddings
│   ├── memory/
│   │   └── memory.py       # SQLite storage + failure context + lazy FAISS
│   ├── config_loader.py    # Loads config/config.yaml with env var resolution
│   ├── agent_loader.py     # Loads agent profiles from config/agents/
│   ├── tool_loader.py      # Dynamic tool import with contract validation
│   ├── autopsy.py          # Failure analysis and recovery suggestions
│   └── logger.py           # Logging setup
├── ux/
│   └── tui_chat.py         # Terminal chat interface
└── tools/
    ├── response.py         # Return text to user
    ├── code_execution.py   # Run Python or bash inside the G.O.B. sandbox
    ├── search_engine.py    # Web search via DuckDuckGo
    ├── text_editor.py      # Read/write/edit files
    └── document_query.py   # Parse and query documents
```

## How a Message Flows

1. **User types** in TUI → `tui_chat.py` captures input
2. **TUI calls** `orchestrator.process_message(text, session_id)`
3. **Orchestrator builds** the message list (system prompt + conversation history + relevant memories)
4. **Orchestrator sends** messages to LLM via `llm_client.chat_complete()`
5. **LLM responds** with either:
   - **Plain text** → returned directly to user
   - **JSON tool call** → orchestrator loads tool (validating contract), executes in sandbox, feeds result back
6. **On failure**, the `autopsy` module classifies the crash and stores the report in `failure_context`. The agent sees why it failed and adjusts.
7. **TUI displays** the response and **saves** both messages to SQLite

## Memory

- **In-session**: The orchestrator keeps `self.messages` growing through the conversation
- **Cross-session**: `load_session_history()` reads the last 20 messages from SQLite
- **Failure context**: Failed executions are stored in a dedicated `failure_context` table for adaptive learning
- **Vector search** (optional): FAISS index is lazy-loaded only when requested

## Configuration

Two config files, clear responsibilities:

| File | Controls | Example |
|------|----------|---------|
| `config/config.yaml` | System settings — LLM provider, model, API endpoint | `chat_model: qwen/qwen3.6-plus-preview:free` |
| `config/agents/default.yaml` | Agent personality — system prompt, tools, behavior | `description: "Minimal AI assistant"` |
| `.env` | Secrets — API keys | `OPENROUTER_API_KEY=sk-or-...` |

## Future: v2.0.0 Dual Model Architecture

The current architecture uses a single LLM for everything. v2.0.0 will introduce:
- **Chat model** — handles user conversation (synchronous)
- **Utility model** — handles memory summarization, embeddings, background tasks (async)

This separation means the chat never stalls waiting for memory operations.
