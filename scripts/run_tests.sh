#!/bin/bash
# run_tests.sh — Execute pytest inside the sandbox container
# Usage: ./scripts/run_tests.sh [--cov]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SANDBOX_DIR="$PROJECT_ROOT/docker"

cd "$SANDBOX_DIR"

echo "[TEST] Installing test dependencies inside sandbox..."
docker compose -f docker-compose.sandbox.yml build --quiet 2>/dev/null || true

CMD="python -m pytest tests/ -v"
if [ "$1" == "--cov" ]; then
    CMD="python -m pytest tests/ -v --cov=src/gob --cov-report=term-missing"
fi

echo "[TEST] Running: $CMD"
docker compose -f docker-compose.sandbox.yml run --rm --entrypoint sh sandbox -c "$CMD"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[TEST] ✅ All tests passed."
else
    echo "[TEST] ❌ Tests failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
