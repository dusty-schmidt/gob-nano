#!/bin/bash
# GOB-01 - Complete Single-Command Setup and Launcher
# Usage: ./gob.sh                          # Launch (auto-setup if needed)
#        ./gob.sh setup                   # Run setup wizard
#        ./gob.sh --tui                   # Launch TUI mode
#        ./gob.sh --discord               # Launch Discord bot

set -e

# Get script directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Set PYTHONPATH to include src directory
export PYTHONPATH="$DIR/src:$PYTHONPATH"

# Auto-run setup wizard if needed
run_auto_setup() {
    # Check if already configured
    if [ -f ".env" ] && grep -q "^OPENROUTER_API_KEY=" .env 2>/dev/null; then
        return 0
    fi
    
    echo ""
    echo "════════════════════════════════════════════════════"
    echo " 🚀 GOB-01 Initial Setup Wizard Required"
    echo "════════════════════════════════════════════════════"
    echo ""
    echo " Running complete installation and configuration..."
    echo ""
    
    # Run Python setup wizard
    if [ -f "$DIR/src/gob/core/setup_wizard.py" ]; then
        python3 "$DIR/src/gob/core/setup_wizard.py"
        echo ""
    fi
}

# Setup mode - run wizard explicitly
if [ "$1" = "setup" ]; then
    if [ -f "$DIR/src/gob/core/setup_wizard.py" ]; then
        python3 "$DIR/src/gob/core/setup_wizard.py"
    else
        echo "❌ Setup wizard not found at $DIR/src/gob/core/setup_wizard.py"
        exit 1
    fi
    exit 0
fi

# Run auto-setup if needed
run_auto_setup

# Parse arguments
MODE="tui"
if [ "$1" = "--tui" ]; then
    MODE="tui"
elif [ "$1" = "--discord" ]; then
    MODE="discord"
elif [ "$1" = "--validate" ]; then
    MODE="validate"
fi

# Run GOB agent
exec python3 src/gob/main.py --mode "$MODE"
