#!/bin/bash
#
# GOB Automatic Version Bump Script
# Manually trigger version bump for any branch
#

# Get current version
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "0.0.0")
echo "Current version: $CURRENT_VERSION"

# Parse version components
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Increment patch version
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"

echo "Bumping to version: $NEW_VERSION"

# Use version manager to set new version
./scripts/version_manager.sh set "$NEW_VERSION"

# Commit and tag
git add VERSION src/gob/version.py pyproject.toml 2>/dev/null || true
git commit -m "release: Bump version to $NEW_VERSION"
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"

echo ""
echo "✅ Version automatically bumped to $NEW_VERSION"
echo ""
echo "Next steps:"
echo "1. Review: git show HEAD"
echo "2. Push: git push origin main v$NEW_VERSION"
