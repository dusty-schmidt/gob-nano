#!/bin/bash
# merge_safely.sh — Validate and merge a feature branch into main
# Usage: ./scripts/merge_safely.sh <feature-branch-name>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <feature-branch-name>"
    exit 1
fi

BRANCH="$1"
echo "[MERGE] Validating branch: $BRANCH"

# Ensure branch exists locally
if ! git show-ref --verify --quiet refs/heads/$BRANCH; then
    echo "[MERGE] ❌ Branch $BRANCH does not exist locally."
    exit 1
fi

# Stash any local changes
git stash push -m "Pre-merge stash" --quiet 2>/dev/null || true

# Switch to main and update
git checkout main
git pull origin main --ff-only

# Merge branch without committing yet to allow validation
git merge --no-commit --no-ff "$BRANCH" || {
    echo "[MERGE] ❌ Merge conflicts detected. Aborting."
    git merge --abort
    git stash pop --quiet 2>/dev/null || true
    exit 1
}

echo "[MERGE] Running pre-merge validation..."

# Syntax check
ERRORS=0
STAGED_PY=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
for f in $STAGED_PY; do
    if ! python -m py_compile "$f" 2>/dev/null; then
        echo "[MERGE] ❌ Syntax error in $f"
        ERRORS=1
    fi
done

if [ $ERRORS -ne 0 ]; then
    echo "[MERGE] ❌ Syntax check failed."
    git merge --abort
    git stash pop --quiet 2>/dev/null || true
    exit 1
fi

# Commit the merge
git commit -m "chore: merge $BRANCH into main"

# Version bump
if [ -f "$PROJECT_ROOT/scripts/auto_version_bump_auto.sh" ]; then
    chmod +x "$PROJECT_ROOT/scripts/auto_version_bump_auto.sh"
    "$PROJECT_ROOT/scripts/auto_version_bump_auto.sh" patch
    echo "[MERGE] Version bumped."
else
    echo "[MERGE] ⚠️ Version bump script not found; skipping."
fi

# Push to main
if [ -n "$SKIP_PUSH" ]; then
    echo "[MERGE] ⚠️ Push skipped (SKIP_PUSH set)."
else
    git push origin main
fi

# Clean up feature branch
git branch -D "$BRANCH"
git push origin --delete "$BRANCH" 2>/dev/null || true

# Pop stash
git stash pop --quiet 2>/dev/null || true

echo "[MERGE] ✅ Successfully merged $BRANCH into main."