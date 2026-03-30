# Gradient Observation Bridge (GOB)

GOB is a minimal AI agent that treats Discord as its native operating system. It runs as a user in your Discord server, executes tools, maintains memory, and coordinates with humans and other agents. No custom UI. No separate interface. Just Discord.

Every AI framework makes trade-offs. Most waste resources rebuilding problems already solved—custom interfaces, collaboration systems, team management. GOB starts with a different assumption: **Discord already solved these problems. Use that infrastructure instead of rebuilding it.** This frees resources for what actually matters: agent intelligence and capability. GOB runs in a container, on your laptop, or on your phone (no WiFi required). It scales from personal assistant to team workspace.

Start with: `./gob.sh` and choose your interface (TUI for instant testing, Discord for teams, Docker for deployment). See [Quick Start](docs/quick-start.md) for detailed instructions. For configuration, architecture, tools, and troubleshooting, check the [docs directory](docs/).

---

## What's Different

| | GOB | Other Frameworks |
|---|-----|------------------|
| **UI** | Discord (built-in) | Custom dashboards (you build) |
| **Collaboration** | Native | Add-on feature |
| **Setup Time** | Minutes | Hours/days |
| **Learning Curve** | None (already know Discord) | Steep |
| **Mobile** | Yes (via Discord app) | Usually no |
| **Dependencies** | Minimal | Many |

## Documentation

- [Quick Start](docs/quick-start.md) — Setup and first steps
- [Configuration](docs/configuration.md) — All settings explained
- [Tools](docs/tools.md) — What each tool does
- [Development](docs/development.md) — Extending GOB
- [FAQ](docs/faq.md) — Common questions

## Requirements

- Python 3.10+
- 4GB RAM minimum
- OpenRouter API key (for LLM) or local LLM
- Discord server (for bot mode)
- Docker (optional, for container)

## License

MIT