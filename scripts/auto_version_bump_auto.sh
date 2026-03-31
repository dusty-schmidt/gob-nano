#!/bin/bash
#
# GOB Automated Version Bump Script
# Non-interactive version for CI/CD and automated workflows
# Prevents conflicts with multiple workers
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
LOCK_FILE=".version_lock"
LOCK_TIMEOUT=300  # 5 minutes
MAX_RETRIES=5
RETRY_DELAY=2

# Get current version
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "0.0.0")
echo -e "${BLUE}Current version: $CURRENT_VERSION${NC}"

# Parse version components
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Parse bump type from arguments
BUMP_TYPE="${1:-patch}"  # Default to patch if no argument
BRANCH_NAME="${2:-$(git rev-parse --abbrev-ref HEAD)}"  # Current branch if not specified

# Validate bump type
case "$BUMP_TYPE" in
    "major"|"minor"|"patch")
        echo -e "${YELLOW}Applying $BUMP_TYPE version bump${NC}"
        ;;
    *)
        echo -e "${RED}Error: Invalid bump type '$BUMP_TYPE'. Use major, minor, or patch.${NC}"
        exit 1
        ;;
esac

# Lock mechanism to prevent concurrent version bumps
acquire_lock() {
    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if mkdir "$LOCK_FILE" 2>/dev/null; then
            echo $$ > "$LOCK_FILE/pid"
            return 0
        fi
        
        # Check if lock is stale
        if [ -f "$LOCK_FILE/pid" ]; then
            local lock_pid=$(cat "$LOCK_FILE/pid")
            if ! kill -0 "$lock_pid" 2>/dev/null; then
                echo -e "${YELLOW}Removing stale lock from PID $lock_pid${NC}"
                rm -rf "$LOCK_FILE"
                continue
            fi
        fi
        
        retries=$((retries + 1))
        echo -e "${YELLOW}Lock held by another process, retrying in $RETRY_DELAY seconds... ($retries/$MAX_RETRIES)${NC}"
        sleep $RETRY_DELAY
    done
    
    echo -e "${RED}Error: Could not acquire version lock after $MAX_RETRIES attempts${NC}"
    exit 1
}

release_lock() {
    if [ -f "$LOCK_FILE/pid" ] && [ "$(cat "$LOCK_FILE/pid")" = "$$" ]; then
        rm -rf "$LOCK_FILE"
    fi
}

# Cleanup function
cleanup() {
    release_lock
}
trap cleanup EXIT

# Acquire lock
echo -e "${YELLOW}Acquiring version lock...${NC}"
acquire_lock

# Apply the version bump based on type
case "$BUMP_TYPE" in
    "major")
        NEW_MAJOR=$((MAJOR + 1))
        NEW_VERSION="$NEW_MAJOR.0.0"
        ;;
    "minor")
        NEW_MINOR=$((MINOR + 1))
        NEW_VERSION="$MAJOR.$NEW_MINOR.0"
        ;;
    "patch")
        NEW_PATCH=$((PATCH + 1))
        NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
        ;;
esac

echo -e "${BLUE}Bumping to version: $NEW_VERSION${NC}"

# Check if this version already exists in git tags
if git tag | grep -q "^v$NEW_VERSION$"; then
    echo -e "${RED}Error: Version v$NEW_VERSION already exists as a git tag${NC}"
    exit 1
fi

# Use version manager to set new version
./scripts/version_manager.sh set "$NEW_VERSION"

# Create branch-specific version tag if not on main
if [ "$BRANCH_NAME" != "main" ] && [ "$BRANCH_NAME" != "master" ]; then
    BRANCH_TAG="v${NEW_VERSION}-${BRANCH_NAME//[^a-zA-Z0-9]/-}"
    echo -e "${YELLOW}Creating branch-specific tag: $BRANCH_TAG${NC}"
    git tag -a "$BRANCH_TAG" -m "Branch $BRANCH_NAME version $NEW_VERSION"
else
    # Create main version tag
    git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
fi

# Create version commit
git add VERSION src/gob/version.py pyproject.toml 2>/dev/null || true
git commit -m "release: Auto-bump version to $NEW_VERSION on branch $BRANCH_NAME"

echo ""
echo -e "${GREEN}✅ Version automatically bumped to $NEW_VERSION${NC}"
echo ""
echo "Next steps:"
echo "1. Review: git show HEAD"
echo "2. Push: git push origin $BRANCH_NAME"
if [ "$BRANCH_NAME" = "main" ] || [ "$BRANCH_NAME" = "master" ]; then
    echo "3. Push tags: git push origin v$NEW_VERSION"
else
    echo "3. Push tags: git push origin $BRANCH_TAG"
fi

# Release lock before exit
release_lock