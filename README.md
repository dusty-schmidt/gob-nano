# gob

**Ultra-minimal AI agent for edge devices (4-8GB RAM)**

Agent Zero's stripped-down cousin. All capability, minimal bloat.

**Primary Interface:** Discord Bot
**Secondary Interface:** CLI Chat

---

## Quick Start ⚡

### Discord Bot (Recommended)

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob/main/scripts/install.sh | bash
cd ~/.gob

# Enable Discord bot in .env
nano .env
# Add: DISCORD_BOT_TOKEN=your_token_here

# Run bot mode
source venv/bin/activate && python -m gob.main --mode discord
```

**How to use Discord:**
- **Mention:** `@gob Hello` - responds in channel
- **DM:** Direct messages always enabled
- **Commands:** `!help`, `!clear`, `!status`

### CLI Chat (Development)

```bash
python -m gob.main --mode tui
```

---

## What is gob?

**Always-on Discord assistant** that:

✅ **Always listening** - Responds on mention in any channel  
✅ **Persistent conversations** - Remembers context per channel  
✅ **Auto-discovers tools** - Add YAML configs, no coding needed  
✅ **Installs packages on-demand** - pip/apt-get available  
✅ **Full terminal access** - Any Linux tool, anytime  
✅ **YAML-based** - Edit configs, not code  

## Core Features

### Discord Bot

| Feature | Action |
|---------|--------|
| **Always Available** | 24/7 listening in Discord servers |
| **Channel Context** | Separate conversations per channel |
| **