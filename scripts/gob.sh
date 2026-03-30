#!/bin/bash
# GOB Agent - Unified setup and launcher
# Single command for everything: setup + TUI + Discord

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Set PYTHONPATH to include the src directory
export PYTHONPATH="$DIR/src:$PYTHONPATH"

# Check if config is incomplete - run setup wizard if needed
if [ -z "$OPENROUTER_API_KEY" ] || [ ! -f ".env" ] || grep -q '\${OPENROUTER}' .env 2>/dev/null; then
    echo ""
    echo "🚀 GOB Agent - Initial Setup"
    echo "═══════════════════════════════════════════════"
    echo ""
    echo "Setting up your GOB agent..."
    echo ""
    
    # Prompt for OpenRouter API key
    echo "🔑 Step 1: OpenRouter API Key"
    echo "─────────────────────────────────────────────────────"
    echo "GOB needs an LLM to work. Get your free key at:"
    echo "https://openrouter.ai/keys"
    echo ""
    read -r -s -p "Paste your OpenRouter API key (or press Enter to skip): " API_KEY
    echo ""
    
    if [ -n "$API_KEY" ]; then
        export OPENROUTER_API_KEY="$API_KEY"
        echo "✓ API key configured" >> /tmp/gob_setup.log 2>/dev/null || true
    else
        echo "⚠️  No API key provided. You'll need one to chat."
    fi
    
    # Prompt for Discord token (optional but recommended)
    echo ""
    echo "🎮 Step 2: Discord Bot (Optional)"
    echo "─────────────────────────────────────────────────────"
    read -r -p "Set up Discord bot for 24/7 availability? (y/n): " SETUP_DISCORD
    
    if [ "$SETUP_DISCORD" = "y" ] || [ "$SETUP_DISCORD" = "Y" ]; then
        echo ""
        echo "Go to: https://discord.com/developers/applications"
        echo "1. Create new application → 'GOB Agent'"
        echo "2. Bot tab → Add Bot"
        echo "3. Copy bot TOKEN"
        echo "4. OAuth2 → URL Generator → scopes: bot"
        echo "5. Permissions: Send Messages, Read History, Manage Channels, Manage Guild"
        echo ""
        read -r -s -p "Paste your Discord bot token: " DISCORD_TOKEN
        echo ""
        
        if [ -n "$DISCORD_TOKEN" ]; then
            export DISCORD_BOT_TOKEN="$DISCORD_TOKEN"
            echo "✓ Discord token configured" >> /tmp/gob_setup.log 2>/dev/null || true
        else
            echo "⚠️  No Discord token provided."
        fi
    else
        echo "⚠️  Skipped Discord setup. Run './gob.sh --discord' to configure later."
    fi
    
    echo ""
    echo "═══════════════════════════════════════════════"
    echo "✓ Setup complete!"
    echo ""
fi

# Use the OpenRouter API key from environment or secrets
if [ -z "$OPENROUTER_API_KEY" ]; then
    OPENROUTER_API_KEY="§§secret(OPENROUTER_API_KEY)"
fi

# Run main.py - mode determined by args
python src/gob/main.py "$@"
