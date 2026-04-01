#!/bin/bash
# GOB Docker entrypoint

set -e

# Handle signals
trap 'echo "Shutting down..."; exit 0' SIGTERM SIGINT

echo "Starting GOB..."

# Load .env if present
if [ -f /app/.env ]; then
    set -a
    source /app/.env
    set +a
fi

# Run the command passed to the container
exec "$@"
