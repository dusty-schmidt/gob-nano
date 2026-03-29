#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------------------------
# NANO Installer - One command setup
# Usage: curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-nano/main/scripts/install.sh | bash
# -------------------------------------------------------------------

REPO_URL="git@github.com:dusty-schmidt/gob-nano.git"
INSTALL_DIR="${HOME}/.nano"

# ---------------------------------------------------------------
# Step 1 - Clone or update repository
# ---------------------------------------------------------------
if [ -d "${INSTALL_DIR}/.git" ]; then
    echo "📦 Updating existing installation..."
    cd "${INSTALL_DIR}"
    git pull origin main
else
    echo "📥 Cloning gob-nano to ${INSTALL_DIR}..."
    git clone "${REPO_URL}" "${INSTALL_DIR}"
    cd "${INSTALL_DIR}"
fi

# ---------------------------------------------------------------
# Step 2 - Create virtual environment
# ---------------------------------------------------------------
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
pip install --quiet --upgrade pip

# ---------------------------------------------------------------
# Step 3 - Install package
# ---------------------------------------------------------------
echo "📦 Installing package..."
pip install --quiet -e .

# ---------------------------------------------------------------
# Step 4 - Create .env from template if missing
# ---------------------------------------------------------------
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# NANO Environment Variables
OPENROUTER_API_KEY=your_openrouter_api_key_here
DISCORD_BOT_TOKEN=your_discord_bot_token_here
EOF
    echo "⚠️  Please edit .env and add your API keys!"
fi

# ---------------------------------------------------------------
# Step 5 - Create memory file
# ---------------------------------------------------------------
mkdir -p src/nano/data
touch src/nano/data/memory.jsonl

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: python -m nano.main"
