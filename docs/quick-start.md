# Quick Start

Get gob running in 5 minutes.

## Two Paths to Success

Gob starts you with **instant value**, then can expand to:

1. **TUI Chat** (instant) - Use immediately, get value
2. **Discord Bot** (step 2) - Always available, 24/7

## Path 1: Start with TUI Chat ⚡

**The fastest way to see gob in action:**

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob/main/scripts/install.sh | bash
cd ~/.gob

# Configure API key only
nano .env
# Add: OPENROUTER_API_KEY=your_key_here

# Run chat
source venv/bin/activate
python -m gob.main --mode tui
```

**What happens:**
- ✅ Type naturally - `"Write a Python script for X"`
- ✅ GoB uses tools automatically - search, code execution, file editing
- ✅ Works instantly - no Discord needed
- ✅ Exit anytime with `Ctrl+C`

**After session ends:**
- 💡 gob will suggest: *"Want me always available in Discord?"*
- 🚀 Then upgrade to Discord bot (see Path 2)

---

## Path 2: Upgrade to Discord Bot

**After experiencing TUI, set up Discord for always-on helper:**

```bash
# 1. Get Discord token (from Discord Developer Portal)
curl -fsSL https://discord.com/developers/applications
# Create bot → Bot tab → Reset Token → Copy token

# 2. Add to .env
nano .env
# Add: DISCORD_BOT_TOKEN=your_token_here

# 3. Run Discord bot
python -m gob.main --mode discord
```

**How to use:**
- **Mention:** `@gob Hello` - responds in any channel
- **DM:** Direct messages always enabled
- **Commands:** `!help`, `!clear`, `!status`
- **Always listening:** 24/7 without terminal open

---

## Prerequisites

### Required

- Python 3.9+
- Git
- Terminal with internet access
- OpenRouter API key ([Sign up at openrouter.ai](https://openrouter.ai))

### Optional (for Discord)

- Discord account
- Discord server (or personal server)

---

## One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob/main/scripts/install.sh | bash
```

This will:
1. Clone to `~/.gob`
2. Create Python venv
3. Install all dependencies
4. Generate `.env` template

---

## Using the Bot

### TUI Mode

```
User: "What are the latest AI trends?"
→ Gob: [Searches & summarizes]

User: "Write a script to parse this CSV"
→ Gob: [Uses code_execution, creates file]

User: "What's in this config?"
→ Gob: [Uses text_editor, explains structure]
```

**Tools work automatically** - no need to request specific capabilities!

### Discord Mode

```
👤 @gob Hello
@gob: Hi! How can I help?

👤 !status
@gob: Shows model, active conversations, tools
```

---

## Why This Flow?

| Step | Benefit |
|------|---------|
| **1. TUI chat** | Instant gratification, zero setup |
| **2. Experience value** | See tools in action |
| **3. Upgrade to Discord** | Always available, multi-user |

**Low friction entry → proven value → optional expansion**

---

## Next Steps

### After TUI Success

- 💡 Accept Discord suggestion when prompts
- 📚 Read [Discord Setup](configuration.md#discord-setup) for full details
- 🛠️ Let Gob help install Discord as a task!

### Explore More

- [Configuration](configuration.md) - Customize everything
- [Tools](tools.md) - See what gob can do
- [Development](development.md) - Extend gob
- [FAQ](faq.md) - Common questions

---

**Ready?** Start with TUI: `python -m gob.main --mode tui` 🚀