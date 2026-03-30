#!/bin/bash
# GOB-NANO Launcher Script
# Usage: ./gob.sh [tui|discord|validate|bash]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-tui}"

cd "$SCRIPT_DIR"

case "$MODE" in
    tui)
        echo "🚀 Starting GOB-NANO in TUI mode..."
        echo "   (Press Ctrl+C to exit)"
        echo ""
        docker-compose -f docker/docker-compose.yml run --rm gob
        ;;
    
    discord)
        echo "🤖 Starting GOB-NANO Discord bot..."
        echo "   (Press Ctrl+C to stop)"
        echo ""
        docker-compose -f docker/docker-compose.yml run --rm -e NANO_MODE=discord gob
        ;;
    
    validate)
        echo "✅ Validating GOB-NANO configuration..."
        docker-compose -f docker/docker-compose.yml run --rm gob python -m src.gob.main --mode validate
        ;;
    
    bash)
        echo "🐚 Opening bash shell in GOB-NANO container..."
        docker-compose -f docker/docker-compose.yml run --rm gob bash
        ;;
    
    *)
        echo "Usage: ./gob.sh [tui|discord|validate|bash]"
        echo ""
        echo "Commands:"
        echo "  tui       - Start interactive TUI chat (default)"
        echo "  discord   - Start Discord bot"
        echo "  validate  - Validate configuration only"
        echo "  bash      - Open container shell"
        echo ""
        echo "Examples:"
        echo "  ./gob.sh              # Start TUI mode"
        echo "  ./gob.sh tui          # Start TUI mode explicitly"
        echo "  ./gob.sh discord      # Start Discord bot"
        exit 1
        ;;
esac
