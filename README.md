# Gradient Observation Bridge (GOB)

A minimal AI agent that treats Discord as its native operating system.

## Why GOB Exists

Every AI framework makes trade-offs. Some are too heavy. Some are missing collaboration features. Some require building custom infrastructure on top. Most waste resources on problems that are already solved elsewhere.

GOB starts with a different assumption: **Discord already solved the interface, organization, and collaboration problems. Use that instead of rebuilding it.**

This frees resources for what actually matters: agent intelligence and capability.

## What GOB Does

GOB runs as an agent in Discord. It can:

- Create and manage Discord servers for teams
- Execute tools and integrate with external services
- Maintain memory across conversations
- Work from your phone (mobile variant)
- Run in a container or on your laptop
- Coordinate with other agents
- Access web, search, documents, and code execution

Humans and agents interact through Discord. No custom UI. No separate interface. Just Discord.

## Quick Start

### Option 1: TUI (Terminal) - Fastest

```bash
git clone https://github.com/dusty-schmidt/gob-nano.git
cd gob-nano
./gob.sh
```

Choose "TUI Chat" and start talking to GOB immediately.

### Option 2: Discord Bot - For Teams

```bash
./gob.sh
```

Choose "Discord Setup" on first run. The wizard handles:
- Creating your Discord app
- Generating bot tokens
- Setting up the bot in your server
- Configuring API keys

Then invite the bot to your Discord server and start using it.

### Option 3: Docker Container - For Deployment

```bash
docker-compose up
```

GOB runs 24/7 as a Discord bot. Works on any machine with Docker.

## How It Works

### The Architecture

```
Your Discord Server
  ├── Create channels for organization
  ├── Ask @GOB questions
  ├── Post tasks
  └── See results automatically
    ↓
  GOB Agent
    ├── Reads Discord messages
    ├── Uses tools as needed
    ├── Maintains conversation context
    └── Posts results back to Discord
    ↓
  Tools Available
    ├── search_engine (web queries)
    ├── text_editor (file operations)
    ├── document_query (PDFs, docs)
    ├── code_execution (run code)
    └── response (LLM reasoning)
```

### The Discord Integration

GOB isn't a bot that posts to Discord. It *is* a Discord user:

- **Channels** = workflow organization
- **Reactions** = status tracking (👀 working, ✅ complete)
- **Threads** = task breakdowns
- **Files** = results and artifacts
- **Mentions** = notifications

Your team already knows Discord. No learning curve.

## Configuration

Edit `config/config.yaml` to set:

```yaml
llm:
  provider: openrouter  # or local
  model: qwen/qwen3.5-flash-02-23
  api_key: your_key_here

discord:
  token: your_bot_token

memory:
  type: jsonl  # lightweight default
```

Edit `config/agents/default.yaml` to customize agent behavior.

## Mobile Version

Want GOB on your phone?

```bash
# Install Termux on Android
# Then in Termux:
pkg install python3
git clone https://github.com/dusty-schmidt/gob-nano.git
cd gob-nano
python -m gob.main --mode discord
```

GOB runs on your phone, connected to the same Discord server. Works on mobile data (no WiFi required).

## Documentation

- **[Quick Start](docs/quick-start.md)** - Detailed setup instructions
- **[Configuration](docs/configuration.md)** - All settings explained
- **[Tools](docs/tools.md)** - What each tool does
- **[Development](docs/development.md)** - How to extend GOB
- **[FAQ](docs/faq.md)** - Common questions

## Requirements

- Python 3.10+
- 4GB RAM (8GB ideal)
- Docker (optional, for container deployment)
- OpenRouter API key (for LLM access) or local LLM
- Discord server (for bot mode)

## What Makes GOB Different

| Feature | GOB | Other Frameworks |
|---------|-----|------------------|
| UI/UX | Discord (built-in) | Custom dashboards (you build) |
| Team collaboration | Native | Add-on feature |
| Mobile support | Yes (via Discord app) | Usually no |
| Setup time | Minutes | Hours/days |
| Dependencies | Minimal | Many |
| Learning curve | None (already know Discord) | Steep |
| Scalability | Teams/orgs | Single user focus |

## Use Cases

- **Team Workspace** - Agents and humans working together in Discord
- **Personal Assistant** - Agent on your phone, always available
- **Remote Coordination** - Distributed teams, async work
- **Agent Training** - Multiple agents learning in shared workspace
- **Workflow Automation** - Tasks triggered through Discord
- **Research/Analysis** - Agent handles research, posts results

## Architecture Notes

GOB prioritizes:

1. **Simplicity** - Minimal codebase, easy to understand
2. **Efficiency** - Lightweight, runs on constrained hardware
3. **Collaboration** - Human-agent teams as first-class citizens
4. **Extensibility** - Add new agents or tools easily
5. **Portability** - Container, desktop, or phone

## Getting Help

- Check [FAQ](docs/faq.md)
- See [Configuration](docs/configuration.md) for settings
- Read [Development](docs/development.md) to extend GOB
- Open an issue on GitHub

## License

MIT

## Contributing

Contributions welcome. See [Development](docs/development.md) for guidelines.

---

**Start with**: `./gob.sh` and choose your interface.

Then join the Discord community to see what others are building.