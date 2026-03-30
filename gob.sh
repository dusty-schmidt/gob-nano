#!/bin/bash
# Gob Agent - Quick start script
# Run ./gob.sh to get straight to chat if configured, or setup wizard if new

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Check if Python venv exists
if [ ! -d "venv" ]; then
    echo "🔧 First time setup..."
    bash scripts/install.sh
fi

# Activate venv
source venv/bin/activate

# Run main - if configured, goes straight to chat
# If not configured, shows setup wizard with Discord first
python -m gob.main --mode tui
