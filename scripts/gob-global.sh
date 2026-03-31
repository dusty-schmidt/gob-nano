#!/bin/bash
# Global GOB Command - Always works, regardless of current directory

set -e

# Function to find GOB installation
check_gob_installation() {
    local gob_paths=(
        "$HOME/.gob"
        "$HOME/THE-NET/repos/gob-01"
        "$(pwd)/gob"
        "$(dirname "$(readlink -f "$0")")/.."
    )
    
    for path in "${gob_paths[@]}"; do
        if [ -f "$path/scripts/gob.sh" ]; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

# Find and use GOB installation
GOB_ROOT=$(check_gob_installation)

if [ -z "$GOB_ROOT" ]; then
    echo "Error: Could not find GOB installation"
    echo "Please install GOB using: curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-01/main/scripts/install.sh | bash"
    exit 1
fi

# Execute GOB with the found installation
exec bash "$GOB_ROOT/scripts/gob.sh" "$@"
