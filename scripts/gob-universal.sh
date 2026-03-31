#!/bin/bash
# GOB Universal Launcher - Works from anywhere
# Automatically detects GOB installation and uses it

set -e

# Function to find GOB installation
check_gob_installation() {
    local gob_paths=(
        "$HOME/.gob"
        "$HOME/THE-NET/repos/gob-01"
        "$(pwd)/gob"
        "$(dirname "$0")/.."
    )
    
    for path in "${gob_paths[@]}"; do
        if [ -f "$path/scripts/gob.sh" ]; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

# Find GOB installation
GOB_ROOT=$(check_gob_installation)

if [ -z "$GOB_ROOT" ]; then
    echo "Error: Could not find GOB installation"
    echo "Please install GOB or ensure it's in one of these locations:"
    echo "  - ~/.gob"
    echo "  - ~/THE-NET/repos/gob-01"
    echo "  - Current directory/gob"
    exit 1
fi

# Use the found GOB installation
echo "Using GOB installation at: $GOB_ROOT"
exec bash "$GOB_ROOT/scripts/gob.sh" "$@"
