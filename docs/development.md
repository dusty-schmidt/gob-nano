# Development Guide

## Prerequisites

- Python 3.9+
- An OpenRouter API key ([get one free](https://openrouter.ai/keys))
- Git, Docker (for sandbox isolation)

## Setup

```bash
git clone https://github.com/dusty-schmidt/gob.git
cd gob
echo 'OPENROUTER_API_KEY=sk-or-your-key-here' > .env
pip install -e .
```

## Run

```bash
python -m gob.run_gob --tui
```

Or with Docker:
```bash
docker compose -f docker/docker-compose.yml up --build
```

## Project Layout

```
gob/
├── config/                 # Configuration files
│   ├── config.yaml         # System config (model, provider, tools)
│   └── agents/
│       └── default.yaml    # Agent personality and behavior
├── docker/                 # Sandbox and deployment Dockerfiles
├── docs/                   # Documentation (you are here)
├── src/gob/                # Source code
│   ├── run_gob.py          # Entry point
│   ├── core/               # Core logic (orchestrator, memory, autopsy)
│   ├── ux/                 # User interfaces
│   └── tools/              # Agent tools
├── scripts/                # G.O.B. safety scripts (sandbox, merge, validation)
├── tests/                  # Test suite
├── .env                    # API keys (not committed)
├── pyproject.toml          # Python package config
└── VERSION                 # Current version
```

## Git Workflow

**Safety-first development:** Never push directly to `main`. The agent protects its own codebase by enforcing branch isolation and pre-merge validation.

```bash
# 1. Configure rebase to keep linear history
git config --global pull.rebase true

# 2. Start work
git checkout main && git pull
git checkout -b fix/description

# 3. Code, then validate locally
./scripts/run_sandbox.sh "python -m py_compile src/gob/core/*.py"

# 4. Commit and push
git add -A && git commit -m "fix: what changed"
git pull origin main --rebase  # Sync before pushing
git push origin fix/description

# 5. Merge safely (run from main after review)
./scripts/merge_safely.sh fix/description
```

**Why this matters:** The `merge_safely.sh` script enforces syntax checks, test gates, and version bumping automatically. No human error, no skipped validation.

## Changing the Model

Edit `config/config.yaml`:
```yaml
llm:
  chat_model: qwen/qwen3.6-plus-preview:free   # change this
```

Browse available models at [openrouter.ai/models](https://openrouter.ai/models). Free models have `:free` suffix.

## Adding a New Tool

1. Create `src/gob/tools/your_tool.py` with an `execute(**kwargs)` function
2. Add a docstring with `Args:` section — the orchestrator contract-checks this before allowing calls
3. Enable it in `config/config.yaml` under `tools.enabled` and `config/agents/default.yaml` under `tools`

## Useful Make Commands

```bash
make help     # Show available commands
make clean    # Remove __pycache__ and build artifacts
make test     # Run test suite
make status   # Git status check
```
