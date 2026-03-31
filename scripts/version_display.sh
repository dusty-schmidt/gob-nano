#!/bin/bash

# GOB Version Display - Lean and Mean
# Displays version info and basic status

# Colors (minimal set)
BLUE='\033[0;34m'
NC='\033[0m'

# Get version
get_version() {
    if [ -f "VERSION" ]; then
        cat VERSION
    else
        echo "0.1.0"
    fi
}

# Main display
version=$(get_version)
echo -e "${BLUE}GOB v${version}${NC}"
