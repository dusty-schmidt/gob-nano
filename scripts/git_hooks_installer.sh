#!/bin/bash
#
# GOB Git Hooks Installer
# Installs git hooks for automated version management and conflict prevention
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

echo -e "${BLUE}Installing GOB Git Hooks...${NC}"

# Pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
#
# GOB Pre-commit Hook
# Validates version consistency and branch naming
#

set -e

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
VERSION_FILE="$PROJECT_ROOT/VERSION"
VERSION_PY="$PROJECT_ROOT/src/gob/version.py"
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Validate branch naming convention
if [[ ! "$BRANCH_NAME" =~ ^(main|master|develop|feature/|bugfix/|hotfix/|micro-task-|release/) ]]; then
    echo -e "${RED}Error: Branch name '$BRANCH_NAME' does not follow naming convention${NC}"
    echo "Valid patterns:"
    echo "  - main/master/develop"
    echo "  - feature/*"
    echo "  - bugfix/*"
    echo "  - hotfix/*"
    echo "  - micro-task-*"
    echo "  - release/*"
    exit 1
fi

# Validate version consistency
if [ -f "$VERSION_FILE" ] && [ -f "$VERSION_PY" ]; then
    VERSION_FROM_FILE=$(cat "$VERSION_FILE")
    VERSION_FROM_PY=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT/src'); from gob.version import get_version; print(get_version())" 2>/dev/null || echo "")
    
    if [ "$VERSION_FROM_FILE" != "$VERSION_FROM_PY" ] && [ -n "$VERSION_FROM_PY" ]; then
        echo -e "${RED}Error: Version mismatch detected!${NC}"
        echo "VERSION file: $VERSION_FROM_FILE"
        echo "version.py:   $VERSION_FROM_PY"
        echo ""
        echo "Run: ./scripts/version_manager.sh sync"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Pre-commit checks passed${NC}"
EOF

chmod +x "$HOOKS_DIR/pre-commit"

# Post-merge hook
cat > "$HOOKS_DIR/post-merge" << 'EOF'
#!/bin/bash
#
# GOB Post-merge Hook
# Automatically handles version bumps after merges to main
#

set -e

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# Only auto-bump on main/master branch merges
if [ "$BRANCH_NAME" = "main" ] || [ "$BRANCH_NAME" = "master" ]; then
    echo "Auto-bumping version after merge to $BRANCH_NAME..."
    cd "$PROJECT_ROOT"
    ./scripts/auto_version_bump_auto.sh patch "$BRANCH_NAME"
fi
EOF

chmod +x "$HOOKS_DIR/post-merge"

# Pre-push hook
cat > "$HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash
#
# GOB Pre-push Hook
# Prevents version conflicts before pushing
#

set -e

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
REMOTE="$1"
URL="$2"

# Check for version lock
if [ -d "$PROJECT_ROOT/.version_lock" ]; then
    echo "Warning: Version lock detected. Another process may be updating versions."
    echo "Waiting for lock to be released..."
    
    # Wait up to 30 seconds for lock to be released
    for i in {1..30}; do
        if [ ! -d "$PROJECT_ROOT/.version_lock" ]; then
            break
        fi
        sleep 1
    done
    
    if [ -d "$PROJECT_ROOT/.version_lock" ]; then
        echo "Error: Version lock still held after 30 seconds."
        echo "Please check for stale lock and remove manually if needed."
        exit 1
    fi
fi

echo "Pre-push checks completed successfully."
EOF

chmod +x "$HOOKS_DIR/pre-push"

# Post-commit hook
cat > "$HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
#
# GOB Post-commit Hook
# Shows current version after successful commit
#

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
VERSION_FILE="$PROJECT_ROOT/VERSION"

if [ -f "$VERSION_FILE" ]; then
    VERSION=$(cat "$VERSION_FILE")
    echo "Current version: $VERSION"
fi
EOF

chmod +x "$HOOKS_DIR/post-commit"

echo -e "${GREEN}✅ Git hooks installed successfully!${NC}"
echo ""
echo "Installed hooks:"
echo "  - pre-commit: Validates version consistency and branch naming"
echo "  - post-merge: Auto-bumps version on main branch merges"
echo "  - pre-push: Prevents version conflicts"
echo "  - post-commit: Shows current version after commits"
echo ""
echo "To disable hooks temporarily, use:"
echo "  git commit --no-verify"
echo "  git push --no-verify"
echo ""
echo "To remove all hooks: rm -rf $HOOKS_DIR"