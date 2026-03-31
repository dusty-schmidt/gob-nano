#!/bin/bash

# GOB Version Manager
# Manages versioning for the GOB project

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$PROJECT_ROOT/VERSION"
VERSION_PY="$PROJECT_ROOT/src/gob/version.py"

# Get current version
get_version() {
    if [ -f "$VERSION_FILE" ]; then
        cat "$VERSION_FILE"
    else
        echo "0.0.0"
    fi
}

# Set new version
set_version() {
    local new_version="$1"
    
    # Validate version format (semantic versioning)
    if [[ ! "$new_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}Error: Version must follow semantic versioning (MAJOR.MINOR.PATCH)${NC}"
        exit 1
    fi
    
    # Update VERSION file
    echo "$new_version" > "$VERSION_FILE"
    
    # Update version.py
    cat > "$VERSION_PY" << PYTHON_EOF
"""
GOB Version Information

This module contains version information for the GOB project.
Follows semantic versioning (MAJOR.MINOR.PATCH)

Version $new_version - $(date +%Y-%m-%d)
"""

__version__ = "$new_version"
__version_info__ = ($(echo "$new_version" | tr '.' ' '))

# Version history
VERSION_HISTORY = {
    "$new_version": {
        "date": "$(date +%Y-%m-%d)",
        "description": "Version $new_version release",
        "features": []
    }
}

def get_version():
    """Get the current version string"""
    return __version__

def get_version_info():
    """Get the version as a tuple"""
    return __version_info__

def get_version_history():
    """Get the complete version history"""
    return VERSION_HISTORY
PYTHON_EOF

    # Update pyproject.toml if it exists
    if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
        sed -i "s/^version.*/version = \"$new_version\"/' "$PROJECT_ROOT/pyproject.toml"
    fi
    
    echo -e "${GREEN}✅ Version updated to $new_version${NC}"
}

# Create git tag
create_tag() {
    local version="$1"
    local message="$2"
    
    if [ -z "$message" ]; then
        message="Release version $version"
    fi
    
    # Create annotated tag
    git tag -a "v$version" -m "$message"
    echo -e "${GREEN}✅ Git tag 'v$version' created${NC}"
}

# Sync version files
sync_version_files() {
    local version=$(get_version)
    set_version "$version"
    echo -e "${GREEN}✅ Version files synchronized${NC}"
}

# Show version history
show_version_history() {
    echo -e "${BLUE}=== GOB Version History ===${NC}"
    echo -e "Current version: $(get_version)"
    echo ""
    
    if [ -f "$VERSION_PY" ]; then
        python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/src')
try:
    from gob.version import get_version_history
    history = get_version_history()
    for version, info in history.items():
        print(f'{version} ({info[\\\"date\\\"]}): {info[\\\"description\\\"]}')
except ImportError:
    print('Version history not available')
"
    fi
}

# Main function
main() {
    local command="$1"
    
    case "$command" in
        "get")
            get_version
            ;;
        "set")
            if [ -z "$2" ]; then
                echo -e "${RED}Error: Version required${NC}"
                echo "Usage: $0 set <version>"
                exit 1
            fi
            set_version "$2"
            ;;
        "tag")
            local version="$(get_version)"
            local message="$2"
            create_tag "$version" "$message"
            ;;
        "bump")
            local current_version=$(get_version)
            IFS='.' read -ra VERSION_PARTS <<< "$current_version"
            MAJOR=${VERSION_PARTS[0]}
            MINOR=${VERSION_PARTS[1]}
            PATCH=${VERSION_PARTS[2]}
            NEW_PATCH=$((PATCH + 1))
            NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
            set_version "$NEW_VERSION"
            ;;
        "history")
            show_version_history
            ;;
        "sync")
            sync_version_files
            ;;
        "help"|"-h"|"--help")
            echo "GOB Version Manager"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  get          - Get current version"
            echo "  set <version> - Set new version (e.g., 0.2.0)"
            echo "  bump         - Increment patch version automatically"
            echo "  tag [message] - Create git tag for current version"
            echo "  history      - Show version history"
            echo "  sync         - Sync VERSION file with version.py"
            echo "  help         - Show this help"
            ;;
        *)
            echo -e "${RED}Error: Unknown command '$command'${NC}"
            echo "Use 'help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"