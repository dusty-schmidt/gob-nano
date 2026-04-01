# Tools Reference

gob tools are Python modules that the agent can invoke during conversation. The LLM decides when to use them by responding with a JSON tool call.

All tools are **contract-validated** on load: they must have an `execute()` function with a docstring containing an `Args:` section. Tools return structured results — never raw strings.

## How Tools Work

When the LLM needs a tool, it responds with:
```json
{"tool": "code_execution", "params": {"code": "print('hello')", "language": "python"}}
```

The orchestrator loads the module, validates its contract, executes it, and feeds the result back to the LLM.

## Available Tools

### response
**Purpose:** Return a text response to the user.

```json
{"tool": "response", "params": {"text": "Here is your answer..."}}
```

### code_execution
**Purpose:** Execute Python code or bash commands.

```json
{"tool": "code_execution", "params": {"code": "ls -la /tmp", "language": "bash"}}
{"tool": "code_execution", "params": {"code": "print(2 + 2)", "language": "python"}}
```

### text_editor
**Purpose:** Read, write, or edit files.

```json
{"tool": "text_editor", "params": {"action": "read", "path": "/tmp/example.txt"}}
{"tool": "text_editor", "params": {"action": "write", "path": "/tmp/out.txt", "content": "hello"}}
```

### search_engine
**Purpose:** Search the web using DuckDuckGo.

```json
{"tool": "search_engine", "params": {"query": "python async tutorial"}}
```

Requires: `pip install 'gob[search]'` (installs `duckduckgo-search`)

### document_query
**Purpose:** Read and parse document contents.

```json
{"tool": "document_query", "params": {"path": "/tmp/document.txt", "query": "summarize this"}}
```

## Creating a New Tool

1. Create a new file in `src/gob/tools/`:

```python
# src/gob/tools/my_tool.py

def execute(**kwargs):
    """Your tool's entry point. Orchestrator calls this."""
    param1 = kwargs.get("param1", "default")
    
    # Do your thing
    result = f"Processed: {param1}"
    
    return {"status": "success", "result": result}
```

2. Enable it in `config/config.yaml`:
```yaml
tools:
  enabled:
    - my_tool
```

3. Add it to `config/agents/default.yaml`:
```yaml
tools:
  - my_tool
```

4. Restart GOB — the tool is now available to the agent.

## Tool Configuration

Tools are enabled in two places:
- `config/config.yaml` → `tools.enabled` (system-level availability)
- `config/agents/default.yaml` → `tools` (agent-level access)

A tool must appear in both to be usable by the agent.
