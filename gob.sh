#!/bin/bash
# GOB Agent - Quick start script (local source)

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Set PYTHONPATH to include the src directory
export PYTHONPATH="$DIR/src:$PYTHONPATH"

# Use the OpenRouter API key from secrets
export OPENROUTER_API_KEY="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"

# Run main.py directly from local source
python src/gob/main.py "$@"
