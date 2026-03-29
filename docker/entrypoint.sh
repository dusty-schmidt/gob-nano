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

# Run the agent
echo "ℹ️  Starting agent..."
python -m nano.main
