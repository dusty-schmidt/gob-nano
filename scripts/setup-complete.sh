#!/bin/bash
# GOB Complete Setup - One-liner installation and configuration
# This script handles:
# 1. Installing dependencies
# 2. Setting up Python environment
# 3. Configuring API key
# 4. Setting up Discord bot
# 5. Creating initial Discord server

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 GOB Complete Setup${NC}"
echo -e "${BLUE}==================${NC}\n"

# Determine script directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$DIR")"
cd "$PROJECT_DIR"

echo -e "${YELLOW}📍 Project directory: $PROJECT_DIR${NC}\n"

# Step 1: Install system dependencies
echo -e "${BLUE}[1/5] Installing system dependencies...${NC}"
echo -e "${YELLOW}⚠️  Manual step: Ensure python3, pip, and git are installed${NC}"

# Step 2: Activate virtual environment
echo -e "\n${BLUE}[2/5] Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Step 3: Configure API key
echo -e "\n${BLUE}[3/5] Configuring API key...${NC}"
echo "Please enter your OpenRouter API key:"
read -r -s API_KEY
echo ""

if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}⚠️  No API key provided. You can set it later in config/config.yaml${NC}"
else
    # Update config.yaml with API key
    python3 << 'EOF'
import os
import yaml

config_path = "config/config.yaml"
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
else:
    config = {}

# Set API key
if 'llm' not in config:
    config['llm'] = {}
config['llm']['api_key'] = os.environ.get('API_KEY')

with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
    
print("✓ API key saved to config/config.yaml")
EOF
fi

# Step 4: Discord bot setup prompt
echo -e "\n${BLUE}[4/5] Discord Bot Setup${NC}"
echo "Would you like to set up the Discord bot now? (y/n)"
read -r SETUP_DISCORD

if [ "$SETUP_DISCORD" = "y" ] || [ "$SETUP_DISCORD" = "Y" ]; then
    echo ""
    echo -e "${YELLOW}Discord Bot Setup Instructions:${NC}"
    echo "1. Go to https://discord.com/developers/applications"
    echo "2. Click 'New Application' and give it a name (e.g., 'GOB')"
    echo "3. Go to 'Bot' section and click 'Add Bot'"
    echo "4. Copy the bot TOKEN"
    echo "5. Go to OAuth2 > URL Generator"
    echo "6. Select scopes: 'bot'"
    echo "7. Select permissions: 'Send Messages', 'Read Message History', 'Manage Channels', 'Manage Guild'"
    echo "8. Copy the generated URL and open in browser to invite bot to a server"
    echo ""
    echo "Paste your Discord bot TOKEN:"
    read -r -s DISCORD_TOKEN
    echo ""
    
    if [ -z "$DISCORD_TOKEN" ]; then
        echo -e "${YELLOW}⚠️  No Discord token provided. You can set it later in config/config.yaml${NC}"
    else
        # Update config.yaml with Discord token
        python3 << 'EOF'
import os
import yaml

config_path = "config/config.yaml"
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
else:
    config = {}

# Set Discord token
if 'discord' not in config:
    config['discord'] = {}
config['discord']['token'] = os.environ.get('DISCORD_TOKEN')

with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
    
print("✓ Discord token saved to config/config.yaml")
EOF
    fi
fi

# Step 5: Create initial server
echo -e "\n${BLUE}[5/5] Creating initial Discord server${NC}"
echo "Enter project name for Discord server (or press Enter to skip):"
read -r PROJECT_NAME

if [ -n "$PROJECT_NAME" ]; then
    echo -e "${YELLOW}To create the server, run:${NC}"
    echo "python3 -m gob.main --discord-setup-project '$PROJECT_NAME'"
    echo ""
    echo -e "${YELLOW}Or start Discord mode and use the !setup_project command in Discord${NC}"
fi

# Final instructions
echo -e "\n${GREEN}==================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}==================${NC}\n"

echo -e "${BLUE}Next steps:${NC}"
echo "1. Start TUI chat: ./gob.sh"
echo "2. Or run Discord bot and use it in Discord"
echo ""
echo -e "${YELLOW}To verify everything works:${NC}"
echo "   source venv/bin/activate"
echo "   python -m gob.main --mode tui"
echo ""
echo -e "${YELLOW}For more information, see:${NC}"
echo "   docs/quick-start.md"
echo "   docs/configuration.md"
echo ""
