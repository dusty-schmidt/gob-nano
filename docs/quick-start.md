# Quick Start

Get gob running in 5 minutes.

## Prerequisites

- Python 3.9+
- Git
- A terminal with internet access

## One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob/main/scripts/install.sh | bash
```

This will:
1. Clone the repository to `~/.gob`
2. Create a Python virtual environment
3. Install all dependencies
4. Generate a `.env` template

## First Run

```bash
# Navigate to the project
cd ~/.gob

# Activate the virtual environment
source venv/bin/activate

# Configure your API keys
nano .env  # Add OPENROUTER_API_KEY

# Run a validation check
python -m gob.main --mode validate

# Start the interactive chat
python -m gob.main --mode tui
```

## Using the Bot

Once running, you can:

- **Type naturally:** Ask questions, request code, analyze files
- **Use tools automatically:** Gob will detect when to use search, code execution, or file editing
- **Install packages on-demand:** When a task requires a package Gob doesn't have, it will install it via pip or apt-get

## Stopping

Press `Ctrl+C` to exit the chat.

---

**Next Steps:**

- [Configuration Guide](configuration.md) - Customize settings
- [Available Tools](tools.md) - See what Gob can do
- [Development](development.md) - Extend Gob
