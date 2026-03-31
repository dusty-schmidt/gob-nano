#!/bin/bash
# GOB-01 One-Command Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-01/main/scripts/install.sh | bash
#
# This script is self-contained and handles everything:
# - Checks prerequisites (Python 3.9+, git)
 # - Clones repo to ~/.gob
# - Runs setup wizard (deps, venv, .env, API key)
# - Adds 'gob' command to PATH
# - Is fully idempotent (run multiple times safely)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: Preflight Checks
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗"
echo "║      GOB-01 Installation Wizard        ║"
echo -e "╚════════════════════════════════════════╝${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "   Install Python 3.9+: apt install python3 python3-venv python3-pip"
    exit 1
fi
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo -e "${GREEN}✓ Python $PY_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3.9+ required (found $PY_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PY_VERSION${NC}"

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found${NC}"
    echo "   Install: apt install git"
    exit 1
fi
echo -e "${GREEN}✓ Git${NC}"

# Check internet (try DNS lookup)
if ! timeout 2 python3 -c "import socket; socket.create_connection(('8.8.8.8', 53), timeout=2)" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Internet connectivity check failed (may still work)${NC}"
else
    echo -e "${GREEN}✓ Internet${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: Clone or Update Repository
# ─────────────────────────────────────────────────────────────────────────────

INSTALL_DIR="$HOME/.gob"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}📦 GOB-01 already installed at $INSTALL_DIR${NC}"
    
    # Check if running interactively
    if [ -t 0 ]; then
        # Interactive terminal, ask user
        read -p "Update existing installation? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Pulling latest changes..."
            cd "$INSTALL_DIR"
            git pull origin main
            echo -e "${GREEN}✓ Updated${NC}"
        else
            echo "Skipped"
            echo -e "${BLUE}To use GOB, run: gob${NC}"
            exit 0
        fi
    else
        # Non-interactive (piped), default to updating
        echo "Updating (non-interactive mode)..."
        cd "$INSTALL_DIR"
        git pull origin main
        echo -e "${GREEN}✓ Updated${NC}"
    fi
else
    echo -e "${BLUE}Cloning GOB-01...${NC}"
    git clone https://github.com/dusty-schmidt/gob-01.git "$INSTALL_DIR"
    echo -e "${GREEN}✓ Cloned to $INSTALL_DIR${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: Run Setup Wizard (handles venv, deps, .env, validation)
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}Running setup wizard...${NC}"
echo ""

# Ensure wizard dependencies are installed in system python
pip3 install -q pyyaml python-dotenv > /dev/null 2>&1

# Pass API key to wizard if provided in environment
if [ -n "$GOB_OPENROUTER_API_KEY" ]; then
    export GOB_OPENROUTER_API_KEY
fi

cd "$INSTALL_DIR"
echo 'n' | python3 src/gob/core/setup_wizard.py

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Phase 4: Shell Integration (add 'gob' command to PATH)
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}Setting up shell integration...${NC}"
echo ""

# Create launcher script
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/gob" << 'EOF'
#!/bin/bash
exec bash "$HOME/.gob/scripts/gob.sh" "$@"
EOF
chmod +x "$HOME/.local/bin/gob"
echo -e "${GREEN}✓ Created $HOME/.local/bin/gob${NC}"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    echo -e "${GREEN}✓ ~/.local/bin already in PATH${NC}"
else
    echo -e "${YELLOW}⚠️  ~/.local/bin not in PATH${NC}"
    
    # Detect shell and update rc file
    if [ -n "$ZSH_VERSION" ]; then
        RC_FILE="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        RC_FILE="$HOME/.bashrc"
    elif grep -q fish <<< "$SHELL"; then
        RC_FILE="$HOME/.config/fish/config.fish"
    else
        RC_FILE="$HOME/.bashrc"
    fi
    
    if ! grep -q '~/.local/bin' "$RC_FILE" 2>/dev/null; then
        echo '' >> "$RC_FILE"
        echo '# GOB-01 PATH' >> "$RC_FILE"
        if grep -q fish <<< "$SHELL"; then
            echo 'set -gx PATH $PATH $HOME/.local/bin' >> "$RC_FILE"
        else
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC_FILE"
        fi
        echo -e "${GREEN}✓ Updated $RC_FILE${NC}"
    fi
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Phase 5: Done Message
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 GOB-01 Installation Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📍 Install Location:${NC} $INSTALL_DIR"
echo ""
echo -e "${BLUE}▶  Usage:${NC}"
echo "   gob            # Start TUI chat"
echo "   gob --discord  # Start Discord bot"
echo "   gob --help     # See all options"
echo ""
echo -e "${BLUE}📚 Documentation:${NC} $INSTALL_DIR/README.md"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Phase 5: Done Message
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 GOB-01 Installation Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📍 Install Location:${NC} $INSTALL_DIR"
echo ""
echo -e "${BLUE}▶  Usage:${NC}"
echo "   gob            # Start TUI chat"
echo "   gob --discord  # Start Discord bot"
echo "   gob --help     # See all options"
echo ""
echo -e "${BLUE}📚 Documentation:${NC} $INSTALL_DIR/README.md"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Phase 6: Post-Install Guidance
# ─────────────────────────────────────────────────────────────────────────────

if [ -n "$GOB_OPENROUTER_API_KEY" ] || ( [ -f "$HOME/.gob/.env" ] && grep -q '^OPENROUTER_API_KEY=[^[:space:]]' "$HOME/.gob/.env" 2>/dev/null ); then
    echo -e "${BLUE}🚀 Launching GOB...${NC}"
    exec ~/.local/bin/gob --tui
else
    echo ""
    echo -e "${YELLOW}⚠️  OpenRouter API key not found${NC}"
    echo ""
    echo "To complete setup:"
    echo "  1. Get your free key from https://openrouter.ai/keys"
    echo "  2. Edit ~/.gob/.env and add:"
    echo "     OPENROUTER_API_KEY=your-key-here"
    echo "  3. Run: gob --tui"
    echo ""
    echo "Or run the setup wizard again:"
    echo "   ~/.gob/scripts/gob.sh setup"
    echo ""
fi
