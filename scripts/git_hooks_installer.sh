#!/bin/bash
# git_hooks_installer.sh — Install pre-commit syntax validation hooks
# Usage: ./scripts/git_hooks_installer.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

mkdir -p "$HOOKS_DIR"

echo "[HOOKS] Installing pre-commit syntax check..."

cat > "$HOOKS_DIR/pre-commit" << 'HOOK_EOF'
#!/bin/bash
# Pre-commit hook: Fail if staged Python files have syntax errors

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

ERRORS=0
for file in $STAGED_FILES; do
    echo "[PRE-COMMIT] Checking syntax: $file"
    if ! python -m py_compile "$file" 2>/dev/null; then
        echo "❌ Syntax error in $file"
        python -m py_compile "$file"
        ERRORS=1
    fi
done

if [ $ERRORS -ne 0 ]; then
    echo "[PRE-COMMIT] ❌ Commit blocked due to syntax errors."
    exit 1
fi

echo "[PRE-COMMIT] ✅ All staged Python files pass syntax check."
exit 0
HOOK_EOF

chmod +x "$HOOKS_DIR/pre-commit"
echo "[HOOKS] ✅ Pre-commit hook installed at $HOOKS_DIR/pre-commit"
