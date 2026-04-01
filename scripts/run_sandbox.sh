#!/bin/bash
# run_sandbox.sh — Execute a command inside the sandbox container
# Usage: ./scripts/run_sandbox.sh "command to run"
#
# Resource limits are enforced by docker-compose (512MB RAM, 1 CPU).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SANDBOX_DIR="$PROJECT_ROOT/docker"

cd "$SANDBOX_DIR"

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"command to execute\""
    echo "Example: $0 \"python -c 'print(\\\"hello\\\")'\""
    exit 1
fi

echo "[SANDBOX] Building image if needed..."
docker compose -f docker-compose.sandbox.yml build --quiet 2>&1 || true

echo "[SANDBOX] Running: $*"
docker compose -f docker-compose.sandbox.yml run --rm sandbox $*
EXIT_CODE=$?

echo "[SANDBOX] Exit code: $EXIT_CODE"
exit $EXIT_CODE
