# Gradient Observation Bridge (GOB-01)

GOB-01 is a minimal, production-ready AI agent that treats Discord as the bridge for collaboration between agents and humans.

## ⚡ ONE-Command Setup

**Fresh install to full agent running in minutes:**

```bash
git clone https://github.com/dusty-schmidt/gob-01.git
cd gob-01
./gob.sh
```

That's it. The setup wizard automatically:
1. Creates Python virtual environment
2. Installs all 12+ dependencies
3. Configures `.env` file
4. Prompts for OpenRouter API key (required)
5. Optionally sets up Discord bot
6. Validates everything works

## 🚀 What You Get

### Core Features
- ✅ **TUI Chat** - Chat in terminal, works instantly
- ✅ **Discord Bot** - 24/7 availability with @mention system
- ✅ **Memory Recall** - Remembers facts across sessions via FAISS vector search
- ✅ **12+ Built-in Tools** - Search, code execution, file editing, document query
- ✅ **Multi-LLM Support** - Cost-optimized query routing (Chat/Utility/Embedding)
- ✅ **Error Handling** - Graceful failure with recovery

### How It Works
- Type naturally: `"What are the latest AI trends?"`
- GOB uses tools automatically → searches, creates files, analyzes data
- Remembers context across sessions → intelligent conversation flow
- Exit anytime with `Ctrl+C`

## 🛠️ Quick Commands

```bash
gob.sh                    # Launch (auto-detects mode)
gob.sh --tui              # TUI chat
gob.sh --discord          # Discord bot
gob.sh --validate         # Verify installation
gob.sh setup              # Run setup wizard
```

## 📋 Prerequisites (You Only Need These)

### Required:
- **Python 3.9+**
- **Git**
- **pip** package manager
- **Internet access**
- **OpenRouter API key** (free at https://openrouter.ai/keys)

### Optional:
- **Discord server** and bot token for Discord mode

### NOT Required:
- ❌ Manual pip installs
- ❌ Manual venv creation
- ❌ Manual .env editing
- ❌ Multiple commands or steps

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [Quick Start](docs/quick-start.md) | Get running in 2 minutes |
| [Configuration](docs/configuration.md) | Detailed setup options |
| [Tools](docs/tools.md) | All available tools |
| [FAQ](docs/faq.md) | Common questions |
| [Development](docs/development.md) | Extend GOB |

## 💡 Example Usage

### TUI Chat
```
User: "What are the latest AI trends?"
→ GOB: [Searches & summarizes from web]

User: "Write a Python script to parse this CSV"
→ GOB: [Uses code_execution, creates file]

User: "What's in this config file?"
→ GOB: [Uses text_editor, explains structure]
```

### Discord Bot
```
👤 @gob Hello
@gob: Hi! How can I help?

👤 !help
@gob: Shows available commands

👤 !status
@gob: Shows model, active conversations, tools
```

## 🔧 Technical Details

- **Architecture:** Minimal, focused on core agent capabilities
- **Memory:** FAISS vector DB for semantic recall
- **Database:** SQLite for conversation history
- **LLM:** OpenRouter with multi-model routing
- **Deployment:** Docker or direct Python install
- **Extensibility:** Plugin system, custom tools, skills support

## 🎯 Compare to Other Frameworks

| Feature | GOB-01 | Agent Zero | Typical Agent |
|---------|--------|------------|---------------|
| Memory Recall | ✅ FAISS | ✅ FAISS | ❌ None |
| Multi-LLM | ✅ Chat/Utility | ✅ Chat/Utility | ❌ Single |
| Tools | ✅ 12+ | ✅ Extensive | ⚠️ Few |
| Discord | ✅ 24/7 | ✅ 24/7 | ⚠️ Optional |
| Setup Time | ⚡ 2 min | ⚡ 2 min | ⏱️ 30 min |
| Complexity | 🟢 Minimal | 🟡 Moderate | 🟡 Varies |

## 📝 Installation Verification

After setup, verify everything works:

```bash
gob.sh --validate
```

**Tests:**
- 🟢 Virtual environment configured
- 🟢 All packages installed
- 🟢 LLM client working
- 🟢 Config file loaded

## 🛠️ Troubleshooting

### "Python not found"
Install Python 3.9+: `sudo apt install python3 python3-venv python3-pip`

### "Git not found"
Install Git: `sudo apt install git`

### "Permission denied" on gob.sh
Make executable: `chmod +x scripts/gob.sh`

### "API key missing"
Run `gob.sh` again - wizard will prompt you

## 🤝 Created by Dusty Schmidt

GOB-01 focuses on simplicity: minimal code, maximum intelligence. Everything is production-ready out of the box.

**Ready to go? Start now:**
```bash
git clone https://github.com/dusty-schmidt/gob-01.git
cd gob-01
./gob.sh
```
