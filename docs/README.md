# Early Phase Documentation

## What These Docs Are For
These docs help validate if GOB is worth building. They're honest about what we don't know yet.

## What We Need To Validate
1. **Installation friction** - Can people actually install it?
2. **TUI usability** - Does the terminal interface work?  
3. **Discord integration** - Does the bot actually connect?
4. **Performance** - Is Docker overhead acceptable?

## Known Problems (Please Confirm These)
- Memory leaks during long conversations
- TUI might freeze on Windows
- Discord bot might disconnect
- Docker might be too slow

## How To Help
1. Try installing: `pip install -e . && python -m gob.main --tui`
2. Report what breaks: [GitHub issues]
3. Answer: Would you actually use this?

## Next Steps
If enough people can install and use it without major issues, we'll build the real documentation.