# Architecture (Early Phase)

## What We're Building
AI agent that uses Discord as a bridge for human-agent collaboration.

## Critical Assumptions (If Wrong, Project Dies)
1. Users want TUI interface (not just web dashboard)
2. Discord bot won't hit rate limits with real usage
3. Docker containers won't be blocked by corporate firewalls
4. Ollama API pricing stays reasonable

## Architecture Decisions We Might Regret
- **Docker-first**: Performance might suck for quick commands
- **Discord bridge**: Single point of failure if Discord changes API
- **TUI interface**: Might be too complex for non-technical users

## What Could Break Everything
- Memory system corrupts conversations
- Docker overhead makes it unusable
- Discord rate limits kill the bot

## Next Validation Steps
1. Get 5 people to install and run TUI
2. Test Discord bot with 10+ users
3. Measure Docker overhead on slow machines