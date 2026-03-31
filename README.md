# Gradient Observation Bridge (GOB-01)

A minimal, production-ready AI agent that treats Discord as the bridge for collaboration between agents and humans.

---

## Install in One Command

```bash
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-01/main/scripts/install.sh | bash
```

This installs GOB-01 to `~/.gob` and adds the `gob` command to your PATH.

---

## Usage

After installation, just run:

```bash
gob            # Start TUI chat
gob --discord  # Start Discord bot
gob --help     # See all options
```

---

## What You Get

- **TUI Chat** – Terminal chat, works instantly
- **Discord Bot** – 24/7 availability via @mention or DM
- **Semantic Memory** – Remembers context across sessions (FAISS)
- **Built-in Tools** – Web search, code execution, file editing, document reading
- **Multi-LLM** – Routes tasks to cheap/expensive models to control cost
- **Local Embeddings** – Offline vector search, no extra API cost

---

## Prerequisites

- Python 3.9+
- Git
- [OpenRouter API key](https://openrouter.ai/keys) (free)
- *(Optional)* Discord bot token for Discord mode

---

## Configuration

All config lives in two files:

| File | Purpose |
|------|---------|
| `~/.gob/.env` | API keys and secrets |
| `~/.gob/config/config.yaml` | Models, tools, agent behavior |

---

## Troubleshooting

**Installation failed?**
- Ensure Python 3.9+, git, and pip are installed
- Check internet connectivity

**`gob` command not found?**
- Reload your shell: `source ~/.bashrc` or `source ~/.zshrc`
- Or open a new terminal

**API key missing after setup?**
- Edit `~/.gob/.env` and add your OpenRouter key
- Or run the installer again to re-prompt

**Update GOB-01?**
```bash
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-01/main/scripts/install.sh | bash
```
→ Detects existing install and offers to pull latest changes

---

## Documentation

- [Configuration](docs/configuration.md) – Detailed setup options
- [Tools](docs/tools.md) – All available tools and usage
- [FAQ](docs/faq.md) – Common questions
- [Development](docs/development.md) – Extending GOB

---

Created by Dusty Schmidt
