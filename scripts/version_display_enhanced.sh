#!/bin/bash

# GOB Enhanced Version Display - Clean and Minimal
# Shows version prominently in the top menu

# Colors (clean and minimal)
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Get version
get_version() {
    if [ -f "VERSION" ]; then
        cat VERSION
    else
        echo "0.1.0"
    fi
}

# Clean display for top menu
version=$(get_version)
echo -e "${BOLD}${BLUE}GOB v${version}${NC}"
