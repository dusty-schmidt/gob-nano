# Development Guide (Early Phase)

## Quick Start
```bash
pip install -e .
python -m gob.main --tui
```

## Does It Work?
Run these commands and see what breaks:
```bash
# Test TUI interface
python -m gob.main --tui
# Type: /help

# Test Discord bot
python -m gob.main --discord
# Invite bot to your server
```

## What We Need To Know
1. Can you install it without errors?
2. Does the TUI actually start?
3. Does Discord bot connect?
4. What error messages do you get?

## Known Broken Stuff
- Memory might leak during long conversations
- TUI might freeze on Windows terminals  
- Discord bot might disconnect after 24 hours

## If It Breaks
1. Check GitHub issues for similar problems
2. Create new issue with error message
3. Try without Docker: `python src/gob/main.py --tui`

## Questions We Need Answered
- Is Docker installation too much friction?
- Does the TUI work on your system?
- Would you actually use this for AI agent work?