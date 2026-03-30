# Quick Start - GOB-01

Get GOB running in **one command**. No manual steps required.

---

## 🚀 ONE-Command Setup

```bash
git clone https://github.com/dusty-schmidt/gob-01.git
cd gob-01
./gob.sh
```

**What happens:**
1. ✅ Virtual environment created
2. ✅ All dependencies installed
3. ✅ `.env` configuration file created
4. ✅ **You configure OpenRouter API key** (interactive prompt)
5. ✅ **Optional Discord bot setup** (interactive prompt)
6. ✅ Everything validated and tested
7. ✅ GOB ready to run

**Total time:** ~60 seconds with API key ready

---

## 📋 Prerequisites (You Only Need These)

### Required:
- **Python 3.9+** - The agent needs Python
- **Git** - For cloning the repository
- **pip** - Package manager
- **Internet access** - For installing dependencies and calling LLM
- **OpenRouter API key** - Free key from https://openrouter.ai/keys

### Optional:
- **Discord server** - For Discord bot mode
- **Discord bot token** - From Discord Developer Portal

### NOT required:
- ❌ Manual pip installs
- ❌ Manual venv creation
- ❌ Manual .env editing
- ❌ Manual dependency installation

**Everything is automated in `./gob.sh`**.

---

## 🎯 Two Usage Paths (Both Work After Setup)

### Path 1: TUI Chat (Terminal)

The fastest way to see GOB work:

```bash
gob.sh                    # Auto-detects mode
# or:
python -m gob.main --mode tui
```

**What happens:**
- ✅ Chat in terminal
- ✅ Agent uses tools automatically
- ✅ Works instantly
- ✅ Exit with `Ctrl+C`

**Example conversation:**
```
User: "What are the latest AI trends?"
→ GOB: [Searches & summarizes]

User: "Write a Python script to parse this CSV"
→ GOB: [Uses code_execution, creates file]

User: "What's in this config file?"
→ GOB: [Uses text_editor, explains structure]
```

### Path 2: Discord Bot (24/7)

```bash
gob.sh --discord
# or:
python -m gob.main --mode discord
```

**How to use:**
- **Mention:** `@gob Hello` - responds in any channel
- **DM:** Direct messages always enabled
- **Commands:** `!help`, `!clear`, `!status`
- **Always listening:** 24/7 without terminal open

**Setup required:** During `./gob.sh` wizard, select `y` for Discord setup and paste your bot token.

---

## 🔑 API Key Configuration

During `./gob.sh` setup:

1. **OpenRouter API Key** (REQUIRED)
   - Get free key: https://openrouter.ai/keys
   - Paste during setup wizard
   - Stored in `.env` file

2. **Discord Bot Token** (OPTIONAL)
   - Get from Discord Developer Portal
   - Paste during setup wizard (if you want Discord mode)
   - Stored in `.env` file

**You can also set env vars manually:**
```bash
openrouter_api_key=your_key ./gob.sh
# or
export OPENROUTER_API_KEY=your_key && ./gob.sh
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [Quick Start](quick-start.md) | **This file** - Get running now |
| [Configuration](configuration.md) | Detailed setup options |
| [Tools](tools.md) | All available tools and usage |
| [FAQ](faq.md) | Common questions |
| [Development](development.md) | Extend GOB |

---

## ✅ Verification

After setup, verify everything works:

```bash
gob.sh --validate
```

**Tests:**
- 🟢 Virtual environment configured
- 🟢 All packages installed
- 🟢 LLM client working
- 🟢 Config file loaded

---

## 🎯 What You Get

### Immediately After Setup:
- ✅ **TUI Chat** - Chat in terminal, 0 setup
- ✅ **Memory Recall** - Remembers facts across sessions via FAISS
- ✅ **12+ Built-in Tools** - Search, code exec, file edit, etc.
- ✅ **Multi-LLM Support** - Cost-optimized query routing
- ✅ **Error Handling** - Graceful failure with recovery

### After Discord Setup:
- ✅ **24/7 Bot** - Always available
- ✅ **Mention System** - @gob Hello to engage
- ✅ **Commands** - !help, !clear, !status
- ✅ **DM Support** - Works in direct messages

---

## 🛠️ Troubleshooting

### "Python not found"
Install Python 3.9+: `sudo apt install python3 python3-venv python3-pip`

### "Git not found"
Install Git: `sudo apt install git`

### "Permission denied" on gob.sh
Make it executable: `chmod +x scripts/gob.sh`

### "API key missing"
Run `gob.sh` again - wizard will prompt you

### "Discord token invalid"
Check Discord Developer Portal → Bot tab → Reset Token

---

## Next Steps

**Try these commands after setup:**

1. **TUI Chat:**
   ```bash
   gob.sh --mode tui
   ```

2. **Test Discord:**
   ```bash
   gob.sh --discord
   ```

3. **Validate Installation:**
   ```bash
   gob.sh --validate
   ```

4. **View Tools Available:**
   ```bash
   cat docs/tools.md
   ```

**That's it. You're ready to go! 🚀**
