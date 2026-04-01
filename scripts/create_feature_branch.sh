#!/bin/bash
# create_feature_branch.sh — Create and checkout a feature branch
# Usage: ./scripts/create_feature_branch.sh <number> "<description>"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <number> \"<description>\""
    echo "Example: $0 16 docker-sandbox-definition"
    exit 1
fi

TASK_NUM="$1"
DESC="$2"

BRANCH_NAME="micro-task-${TASK_NUM}-${DESC}"

cd "$PROJECT_ROOT"

if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo "[BRANCH] Branch already exists: $BRANCH_NAME"
    echo "[BRANCH] Switching to existing branch..."
    git checkout "$BRANCH_NAME"
    exit 0
fi

if git show-ref --verify --quiet refs/remotes/origin/$BRANCH_NAME; then
    echo "[BRANCH] Remote branch exists: $BRANCH_NAME"
    git checkout -b "$BRANCH_NAME" origin/"$BRANCH_NAME"
    exit 0
fi

git checkout main
git pull origin main --ff-only

git checkout -b "$BRANCH_NAME"
echo "[BRANCH] ✅ Created and checked out: $BRANCH_NAME"
