# gob

**Ultra-minimal AI agent for edge devices (4-8GB RAM)**

Agent Zero's stripped-down cousin. All capability, minimal bloat.

---

## Quick Start ⚡

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob/main/scripts/install.sh | bash

# Configure
cd ~/.gob && source venv/bin/activate && nano .env

# Run
python -m gob.main
```

## What is gob?

A minimal AI assistant that:

✅ **Runs on old machines** - ~100MB RAM, ~15s startup  
✅ **Auto-discovers tools** - Add YAML configs, no coding needed  
✅ **Installs packages on-demand** - pip/apt-get available  
✅ **Full terminal access** - Any Linux tool, anytime  
✅ **YAML-based** - Edit configs, not code  

---

## Features

| Feature | Description |
|---------|-------------|
| **Core Tools** | 5 built-in: search, code execution, file editing, document parsing, responses |
| **Runtime Expandable** | Install any package when needed |
| **Custom Agents** | Create specialized profiles in YAML |
| **Lightweight** | No vector DB, no bloat |
| **Discord Ready** | Optional bot mode |

## Documentation

| Doc | Description |
|-----|-------------|
| [Quick Start](docs/quick-start.md) | Installation & first run |
| [Configuration](docs/configuration.md) | Custom settings & agents |
| [Tools](docs/tools.md) | Available capabilities |
| [Development](docs/development.md) | Extend & maintain gob |
| [FAQ](docs/faq.md) | Common questions |

---

## Examples

### Code Generation
```
You: "Write a Python script that parses CSV files"
→ Gob: [Generates complete script]
```

### File Analysis
```
You: "What's in this config file?"
→ Gob: [Reads file and explains structure]
```

### Web Research
```
You: "What are the latest AI trends?"
→ Gob: [Searches and summarizes findings]
```

---

## Why gob?

| Traditional AI Agents | gob |
|----------------------|-----|
| 500MB+ base image | 150MB base |
| Pre-bundled dependencies | Install on-demand |
| Complex configs | YAML editing |
| Slow startup (60+ sec) | Fast startup (~15s) |
| Fixed capabilities | Unlimited expansion |

---

## License

MIT (same as Agent Zero)

**GitHub:** [dusty-schmidt/gob](https://github.com/dusty-schmidt/gob)

---

**Status:** Production-ready • **Tests:** 22/22 passing • **Version:** 0.1.0
