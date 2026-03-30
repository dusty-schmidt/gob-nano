# Gradient Observation Bridge (GOB-01)

A minimal, production-ready AI agent that treats Discord as the bridge for collaboration between agents and humans.

---

## Get Started

```bash
git clone https://github.com/dusty-schmidt/gob-01.git
cd gob-01
bash scripts/gob.sh
```

That's it. The wizard handles everything:
- Creates Python virtual environment
- Installs all dependencies
- Prompts for your [OpenRouter API key](https://openrouter.ai/keys) (free)
- Optionally sets up Discord bot
- Validates the installation

**Total time:** ~2 minutes

---

## Usage

```bash
bash scripts/gob.sh            # TUI chat (default)
bash scripts/gob.sh --tui      # TUI chat (explicit)
bash scripts/gob.sh --discord  # Discord bot
bash scripts/gob.sh setup      # Re-run setup wizard
```

---

## Prerequisites

- Python 3.9+
- Git
- [OpenRouter API key](https://openrouter.ai/keys) (free)
- *(Optional)* Discord bot token for Discord mode

---

## What You Get

- **TUI Chat** – Terminal chat, works instantly after setup
- **Discord Bot** – 24/7 availability via @mention or DM
- **Semantic Memory** – Remembers context across sessions (FAISS)
- **Built-in Tools** – Web search, code execution, file editing, document reading
- **Multi-LLM** – Routes tasks to cheap/expensive models to control cost
- **Local Embeddings** – Offline vector search, no extra API cost

---

## Configuration

All config lives in two files:

| File | Purpose |
|------|---------|
| `.env` | API keys and secrets |
| `config/config.yaml` | Models, tools, agent behavior |

See [docs/configuration.md](docs/configuration.md) for details.

---

## Troubleshooting

**`Permission denied` on gob.sh**
```bash
chmod +x scripts/gob.sh
```

**`python3` not found**
```bash
sudo apt install python3 python3-venv python3-pip   # Debian/Ubuntu
```

**API key missing after setup**
```bash
bash scripts/gob.sh setup   # Re-run wizard
```

---

## Documentation

- [Configuration](docs/configuration.md)
- [Tools](docs/tools.md)
- [FAQ](docs/faq.md)
- [Development](docs/development.md)

---

Created by Dusty Schmidt
