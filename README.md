# Gradient Observation Bridge (GOB)

GOB is a minimal AI agent that treats Discord as the bridge for true collaboration between agents and humans. It manages a discord server, executes tools, maintains memory, and coordinates with humans and other agents. Django already solved the hard problems—team collaboration, notifications, mobile access, persistent messaging, file sharing, permissions, organization. This allows GOB to be highly intelligent with extensive native capabilities while remaining light enough to run on an edge device. 

GOB runs in a docker container with a built in linux environment, has a dedicated workspace for full development, and can install new tools and capabilities autonomously.  It is compatible with MCP, SKILLS, and whatever comes out next month.

## One-Command Everything

**Fresh install to full setup in a single command:**

```bash
cd ~/.gob
./gob.sh
```

The unified setup detects what you need and guides you through:
1. ✅ OpenRouter API key configuration
2. ✅ Optional Discord bot setup for 24/7 availability  
3. ✅ Launch TUI chat or Discord mode based on your choice

**Quick access:**
- TUI Chat: `./gob.sh --mode tui` or just `./gob.sh`
- Discord Bot: `./gob.sh --mode discord`
- Validate: `./gob.sh --mode validate`

Created by Dusty Schmidt
