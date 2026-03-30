#!/bin/bash
# NANO Agent Docker entrypoint

set -e

# Handle signals
trap 'echo "Shutting down..."; exit 0' SIGTERM SIGINT

echo "🚀 Starting NANO Agent..."

# Run setup if config doesn't exist
if [ ! -f "/app/config/config.yaml" ]; then
    echo "ℹ️  Configuration not found, running setup wizard..."
    python -m scripts.setup
fi

# Determine run mode from environment variable (default to TUI)
RUN_MODE="${NANO_MODE:-tui}"

echo "ℹ️  Starting agent in ${RUN_MODE} mode..."

if [ "$RUN_MODE" = "discord" ]; then
    python -m gob.main --mode discord
else
    # Default to TUI mode
    python -m gob.main --mode tui
fi
