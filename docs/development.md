# Development

Extend and maintain Gob.

## Architecture Overview

```
gob/
├── src/gob/           # Core application
│   ├── main.py        # Entry point, CLI handling
│   ├── orchestrator.py # Task routing, tool coordination
│   ├── tools/         # Tool implementations
│   ├── helpers/       # Config, memory, LLM clients
│   ├── interfaces/    # TUI, Discord bot
│   └── data/          # Runtime data storage
├── config/            # YAML configuration
│   ├── agents/        # Agent profiles
│   └── config.yaml    # System settings
├── tests/             # Unit tests
├── scripts/           # Build & setup utilities
└── docker/            # Container configs
```

## Project Structure

### src/gob/

#### **main.py**
Entry point that:
- Parses CLI arguments
- Loads configuration
- Validates setup
- Initializes memory and LLM
- Routes to appropriate interface

#### **orchestrator.py**
Central task handler:
- Receives user input
- Selects appropriate tool
- Executes tool
- Formats response

#### **tools/**
Core capabilities:
- `response` - Base text generation
- `search_engine` - Web search
- `code_execution` - Linux/Python execution
- `text_editor` - File manipulation
- `document_query` - PDF/docs/HTML parsing

#### **helpers/**
Supporting services:
- `config_loader.py` - YAML config parsing
- `agent_loader.py` - Agent profile loading
- `memory/memory.py` - JSONL persistence
- `llm_client.py` - OpenRouter API integration
- `tool_loader.py` - Runtime tool discovery

## Getting Started

### Development Setup

```bash
# Clone repository
git clone https://github.com/dusty-schmidt/gob.git
cd gob

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/gob --cov-report=html

# Run specific test file
pytest tests/test_config.py -v
```

All 22 tests should pass:
- Config loading (5 tests)
- Memory operations (4 tests)
- Tool loading (2 tests)
- Agent loading (2 tests)
- Tool existence (5 tests)
All 22 tests should pass:
- Config loading (5 tests)
- Memory operations (4 tests)
- Tool loading (2 tests)
- Agent loading (2 tests)
- Tool existence (5 tests)
- Main integration (4 tests)

## Git Workflow

### Branch Strategy: GitHub Flow (Simple)

```
main ──────────────────────────────────── (always deployable)
     └── task/feature-name              (your work)
```

- `main` is the only permanent branch
- Task branches branch from `main`, merge back to `main`
- One task = one branch = one merge to main

### Workflow Steps

#### 1. STARTING A NEW TASK

```bash
git checkout main
git pull origin main
git checkout -b task/short-description
```

#### 2. WHILE WORKING

Commit early and often:

```bash
git add .
git commit -m "Brief description of changes"
```

#### 3. BEFORE MERGING

**ALWAYS run tests AND lint, fix any issues:**

```bash
# Run the test suite
python -m scripts.lint

# Run lint check
python scripts/test.py

# If tests fail or lint finds issues, fix them before proceeding
```

**Lint issues must be fixed - do not skip or ignore warnings.**

#### 4. MERGING TO MAIN

```bash
git checkout main
git pull origin main
git merge task/your-branch-name
git push origin main
git branch -d task/your-branch-name
```

### Rules

1. **ALWAYS** branch from `main`
2. **ALWAYS** run `python scripts/test.py` before merging
3. **ALWAYS** run `python -m scripts.lint` and fix all issues before merging
4. **ALWAYS** pull `main` before creating a new branch
5. **ALWAYS** delete task branches after merging
6. **NEVER** push directly to `main` (always use a task branch)
7. **NEVER** skip or ignore lint warnings

### Quick Reference

| Situation | Command |
|----------|---------|
| Start new task | `git checkout -b task/name` |
| Save work | `git add . && git commit -m "message"` |
| Run tests | `python scripts/test.py` |
| Run lint | `python -m scripts.lint` |
| See status | `git status` |
| See history | `git log --oneline` |
| Switch branch | `git checkout branch-name` |
| Update from main | `git pull origin main` |
| Merge to main | `git checkout main && git merge branch-name && git push` |
| Delete branch | `git branch -d branch-name` |

### Branch Naming

Use `task/` prefix with a short description:

| Good | Bad |
|------|-----|
| `task/add-yaml-configs` | `my-work` |
| `task/fix-memory-bug` | `branch1` |
| `task/update-dockerfile` | `latest` |

### If Something Goes Wrong

**Accidentally worked on main:**
```bash
git stash
git checkout -b task/fix-mistake
git stash pop
```

**Need to undo last commit:**
```bash
git reset --soft HEAD~1  # keep changes staged
git reset HEAD~1         # discard changes
```

## Adding New Tools

### 1. Create Tool File

Create `src/gob/tools/my_tool.py`:

```python
"""My Custom Tool"""
import requests

def fetch_data(url: str) -> dict:
    """Fetch and parse data from URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

### 2. Register in Loader

Update `src/gob/helpers/tool_loader.py`:

```python
tools = {
    "response",
    "search_engine",
    "code_execution",
    "text_editor",
    "document_query",
    "my_tool"  # Add here
}
```

### 3. Expose in Package

Update `src/gob/tools/__init__.py`:

```python
from .response import *
from .search_engine import *
from .code_execution import *
from .text_editor import *
from .document_query import *
from .my_tool import *  # Add here
```

### 4. Enable in Config

Add to `config/config.yaml`:

```yaml
tools:
  enabled:
    - response
    - search_engine
    - code_execution
    - text_editor
    - document_query
    - my_tool  # Add here
```

## Custom Agents

Create new agent profiles in `config/agents/`:

**config/agents/researcher.yaml**

```yaml
name: "Researcher Agent"
description: "Specialized in information gathering and analysis"

model:
  provider: "openrouter"
  name: "qwen/qwen3.5-flash-02-23"
  max_tokens: 4096
  temperature: 0.6

context: |
  You are a research assistant.
  Prioritize accuracy and source verification.
  Cite sources when providing information.

tools:
  - response
  - search_engine
  - document_query

settings:
  max_iterations: 25
```

## Configuration Changes

### Environment Variables

Set in `.env`:

```bash
OPENROUTER_API_KEY=your_key_here
DISCORD_BOT_TOKEN=your_token_here
LLM_TEMPERATURE=0.7
MAX_TOKENS=4096
```

### System Settings

Edit `config/config.yaml`:

```yaml
llm:
  provider: openrouter
  model: qwen/qwen3.5-flash-02-23
  temperature: 0.7    # Adjust creativity
  max_tokens: 4096    # Adjust response length

tools:
  enabled:
    - response
    - search_engine
    - code_execution
    - text_editor
    - document_query
  disabled: []        # Remove unused tools
```

## Docker Setup

### Build Image

```bash
make build
```

### Run Container

```bash
make run
```

### Development with Docker

```bash
docker-compose up
# Edit files in mounted volume
docker-compose exec gob bash
```

## Making Changes

### 1. Make Changes Locally

```bash
# Create feature branch
git checkout -b feature/my-improvement
```

### 2. Test Changes

```bash
pytest tests/ -v
python -m gob.main --mode validate
```

### 3. Update Documentation

Keep docs in sync:
- README.md - Short intro
- docs/quick-start.md - Installation
- docs/configuration.md - Setup details
- docs/tools.md - Tool documentation

### 4. Commit Changes

```bash
git add .
git commit -m "feat: Add my-improvement"
git push origin feature/my-improvement
```

## Best Practices

### Code Style

- Use type hints
- Write docstrings
- Keep functions small (< 50 lines)
- One concern per file

### Testing

- Mock external dependencies
- Test edge cases
- Use descriptive test names
- Keep tests fast

### Documentation

- Document public APIs
- Keep examples current
- Update CHANGELOG.md for major changes
- Use clear commit messages

## Debugging

### Enable Debug Logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Validate Configuration

```bash
python -m gob.main --mode validate
```

### Test Tools Individually

```bash
# Run tool in isolation
python -c "from src.gob.tools import search_engine; print(search_engine.query('test'))"
```

## Contributing

1. **Tests must pass:** `pytest tests/ -v`
2. **Keep dependencies minimal:** Install packages on-demand
3. **Use YAML for configs:** Easy to edit, no coding required
4. **Document thoroughly:** Add docs for new features
5. **Write clear commits:** Explain "why" not just "what"

## Resources

- [Quick Start](quick-start.md) - Installation guide
- [Configuration](configuration.md) - Customization options
- [Tools](tools.md) - Available capabilities
- [FAQ](faq.md) - Common questions

---

**Ready to contribute?** Check the GitHub repo for issues and feature requests!
