#!/bin/bash
#
# GOB Automatic Version Bump Script
# Prompts user for version bump level and applies the bump
#

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get current version
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "0.0.0")
echo -e "${BLUE}Current version: $CURRENT_VERSION${NC}"

# Parse version components
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Prompt user for bump level
echo ""
echo -e "${YELLOW}Select version bump level:${NC}"
echo "1) Major (MAJOR.minor.patch) - Breaking changes"
echo "2) Minor (major.MINOR.patch) - New features"
echo "3) Patch (major.minor.PATCH) - Bug fixes (default)"
echo ""
read -p "Enter choice (1-3, default: 3): " choice

# Default to patch if no input
if [ -z "$choice" ]; then
    choice=3
fi

# Apply the appropriate version bump
case $choice in
    1)
        # Major version bump
        NEW_MAJOR=$((MAJOR + 1))
        NEW_VERSION="$NEW_MAJOR.0.0"
        echo -e "${GREEN}Major version bump selected${NC}"
        ;;
    2)
        # Minor version bump
        NEW_MINOR=$((MINOR + 1))
        NEW_VERSION="$MAJOR.$NEW_MINOR.0"
        echo -e "${GREEN}Minor version bump selected${NC}"
        ;;
    3|"")
        # Patch version bump (default)
        NEW_PATCH=$((PATCH + 1))
        NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
        echo -e "${GREEN}Patch version bump selected${NC}"
        ;;
    *)
        echo "Invalid choice. Defaulting to patch version bump."
        NEW_PATCH=$((PATCH + 1))
        NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
        ;;
esac

echo -e "${BLUE}Bumping to version: $NEW_VERSION${NC}"

# Use version manager to set new version
./scripts/version_manager.sh set "$NEW_VERSION"

# Commit and tag
git add VERSION src/gob/version.py pyproject.toml 2>/dev/null || true
git commit -m "release: Bump version to $NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"

echo ""
echo -e "${GREEN}✅ Version automatically bumped to $NEW_VERSION${NC}"
echo ""
echo "Next steps:"
echo "1. Review: git show HEAD"
echo "2. Push: git push origin main v$NEW_VERSION"
