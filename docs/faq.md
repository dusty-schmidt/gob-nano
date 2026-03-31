# FAQ

## Setup
1. Install: `curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-01/main/scripts/install.sh | bash`
2. Configure: Add `OPENROUTER_API_KEY` to `~/.gob/.env`
3. Run: `gob` or `gob --discord`

## APIs
- Required: OpenRouter API key
- Optional: Discord bot token

## Tools
Auto-detected. Install missing packages on-demand.

## Memory
JSONL persistence in `src/gob/core/memory/memory.db`

## Reset
```bash
rm src/gob/core/memory/memory.db
```