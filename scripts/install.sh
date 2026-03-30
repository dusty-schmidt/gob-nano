#!/bin/bash
# GOB-Nano One-Liner Installer
# Usage: bash <(curl -s https://raw.githubusercontent.com/dusty-schmidt/gob-nano/main/scripts/install.sh)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║       GOB-Nano Installation           ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found. Please install git first.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}\n"

# Determine install location
INSTALL_DIR="${1:-.}/gob-nano"
echo -e "${BLUE}📁 Installation directory: $INSTALL_DIR${NC}\n"

# Clone repository if not present
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${BLUE}Cloning GOB-Nano repository...${NC}"
    git clone https://github.com/dusty-schmidt/gob-nano.git "$INSTALL_DIR"
else
    echo -e "${YELLOW}Directory $INSTALL_DIR already exists${NC}"
fi

cd "$INSTALL_DIR"

# Run setup
if [ -f "scripts/setup-complete.sh" ]; then
    bash scripts/setup-complete.sh
else
    echo -e "${RED}❌ Setup script not found${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 Installation complete!${NC}"
echo -e "${BLUE}Start with: cd $INSTALL_DIR && source venv/bin/activate && python -m gob.main${NC}"
