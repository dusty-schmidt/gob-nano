#!/bin/bash
# GOB-01 - Single-command launcher
# Usage:
#   scripts/gob.sh          # Auto-setup if needed, then launch TUI
#   scripts/gob.sh setup    # Run setup wizard explicitly
#   scripts/gob.sh --tui    # Launch TUI mode
#   scripts/gob.sh --discord # Launch Discord bot

set -e

# Resolve project root (parent of scripts/)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
cd "$ROOT"

# Python paths
VENV_PYTHON="$ROOT/venv/bin/python"
export PYTHONPATH="$ROOT/src:$PYTHONPATH"

# ─── Helpers ────────────────────────────────────────────────────────────────

need_setup() {
    # Wizard needed if venv missing OR .env missing OR key not set
    [ ! -f "$VENV_PYTHON" ] && return 0
    [ ! -f "$ROOT/.env" ]   && return 0
    grep -q "^OPENROUTER_API_KEY=." "$ROOT/.env" 2>/dev/null || return 0
    return 1
}

run_setup() {
    echo ""
    echo "════════════════════════════════════════════════════"
    echo " 🚀 GOB-01 First-Time Setup"
    echo "════════════════════════════════════════════════════"
    echo ""
    # Use system python to bootstrap the wizard (no venv yet)
    python3 "$ROOT/src/gob/core/setup_wizard.py"
    echo ""
}

# ─── Explicit setup mode ────────────────────────────────────────────────────

if [ "$1" = "setup" ]; then
    python3 "$ROOT/src/gob/core/setup_wizard.py"
    exit 0
fi

# ─── Auto-setup when first time or incomplete ────────────────────────────────

if need_setup; then
    run_setup
fi

# ─── Ensure venv exists after setup ─────────────────────────────────────────

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Setup incomplete - venv not found at $VENV_PYTHON"
    echo "   Run: scripts/gob.sh setup"
    exit 1
fi

# ─── Parse mode ─────────────────────────────────────────────────────────────

MODE="tui"
if   [ "$1" = "--discord" ];  then MODE="discord"
elif [ "$1" = "--validate" ]; then MODE="validate"
elif [ "$1" = "--tui" ];      then MODE="tui"
fi

# ─── Launch using venv python ────────────────────────────────────────────────

exec "$VENV_PYTHON" "$ROOT/src/gob/main.py" --mode "$MODE"
