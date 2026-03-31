#!/bin/bash

# GOB-01 Launcher - Enhanced with automatic API key handling
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHONPATH="$PROJECT_ROOT/src"
VENV_PATH="$PROJECT_ROOT/venv"
MAIN_PY="$PROJECT_ROOT/src/gob/main.py"

# Function to check if API key is configured
check_api_key() {
    local config_file="$PROJECT_ROOT/config/config.yaml"
    local env_file="$PROJECT_ROOT/.env"
    
    # Check in config.yaml
    if [ -f "$config_file" ]; then
        local api_key=$(grep -E "api_key:" "$config_file" | cut -d: -f2 | tr -d ' ' | tr -d '"')
        if [ -n "$api_key" ] && [ "$api_key" != "your-api-key-here" ]; then
            return 0
        fi
    fi
    
    # Check in environment
    local env_key=$(grep "OPENROUTER_API_KEY" "$env_file" 2>/dev/null | cut -d= -f2 | tr -d ' ')
    if [ -n "$env_key" ]; then
        return 0
    fi
    
    # Check environment variable
    if [ -n "$OPENROUTER_API_KEY" ]; then
        return 0
    fi
    
    return 1
}

# Function to prompt for API key
prompt_api_key() {
    echo -e "${BLUE}🔑 OpenRouter API Key Setup${NC}"
    echo -e "Get your free key at: https://openrouter.ai/keys"
    echo -e ""
    echo -e "Enter your OpenRouter API key (or press Enter to skip):"
    read -r api_key
    
    if [ -n "$api_key" ]; then
        # Update .env file
        if [ -f "$PROJECT_ROOT/.env" ]; then
            sed -i "s/OPENROUTER_API_KEY=.*/OPENROUTER_API_KEY=$api_key/" "$PROJECT_ROOT/.env"
        else
            echo "OPENROUTER_API_KEY=$api_key" >> "$PROJECT_ROOT/.env"
        fi
        echo -e "${GREEN}✅ API key saved to .env${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  No API key provided. GOB will run in limited mode.${NC}"
        return 1
    fi
}

# Function to setup Python environment
setup_python_env() {
    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv "$VENV_PATH"
    fi
    
    source "$VENV_PATH/bin/activate"
    
    # Install dependencies if needed
    if [ ! -f "$VENV_PATH/.installed" ]; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        pip install -e "$PROJECT_ROOT" > /dev/null 2>&1
        touch "$VENV_PATH/.installed"
    fi
}

# Function to launch GOB
launch_gob() {
    local mode="$1"
    
    # Set up Python environment
    setup_python_env
    
    # Set PYTHONPATH
    export PYTHONPATH="$PYTHONPATH"
    
    # Launch GOB
    python3 "$MAIN_PY" --mode "$mode"
}

# Main function
main() {
    echo -e "${BLUE}🚀 GOB-01 Agent Launcher${NC}"
    
    # Parse arguments
    local mode="tui"
    local setup_only=false
    local validate_only=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --discord)
                mode="discord"
                shift
                ;;
            --tui)
                mode="tui"
                shift
                ;;
            --validate)
                validate_only=true
                shift
                ;;
            --setup)
                setup_only=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --tui        Launch TUI mode (default)"
                echo "  --discord    Launch Discord bot mode"
                echo "  --setup      Run setup wizard only"
                echo "  --validate   Validate installation only"
                echo "  --help       Show this help"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Handle different modes
    if [ "$validate_only" = true ]; then
        echo -e "${BLUE}🔍 Validating installation...${NC}"
        launch_gob "validate"
        exit 0
    fi
    
    if [ "$setup_only" = true ]; then
        echo -e "${BLUE}⚙️  Running setup wizard...${NC}"
        launch_gob "setup"
        exit 0
    fi
    
    # Check if API key is configured
    if ! check_api_key; then
        echo -e "${YELLOW}⚠️  OpenRouter API key not found.${NC}"
        echo -e "${BLUE}🔑 Setting up API key...${NC}"
        
        if ! prompt_api_key; then
            echo -e "${YELLOW}⚠️  Continuing without API key. Some features may be limited.${NC}"
        fi
    fi
    
    # Launch GOB in the specified mode
    echo -e "${BLUE}🚀 Launching GOB in $mode mode...${NC}"
    launch_gob "$mode"
}

# Run main function
main "$@"
