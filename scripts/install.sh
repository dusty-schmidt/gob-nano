#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------------------------
# YOLO installer for the NANO Agent (idempotent)
#   - Detects if the repository is already present
#   - Sets up a Python virtual environment
#   - Installs the package (editable mode)
#   - Runs the built‑in setup wizard
# -------------------------------------------------------------------

# Repository URL (SSH) – used only if we need to clone
REPO_URL="git@github.com:dusty-schmidt/gob-family.git"

# ---------------------------------------------------------------
# Resolve the absolute path of the project root (two levels up)
# ---------------------------------------------------------------
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NANO_DIR="${PROJECT_ROOT}/nano"

# ---------------------------------------------------------------
# Step 1 – Clone the repository if it is not already present
# ---------------------------------------------------------------
if [ ! -d "${PROJECT_ROOT}/.git" ]; then
  echo "Cloning repository..."
  git clone "$REPO_URL" "$PROJECT_ROOT"
else
  echo "Repository already exists – skipping clone."
fi

# ---------------------------------------------------------------
# Step 2 – Change into the nano source directory
# ---------------------------------------------------------------
cd "$NANO_DIR"

# ---------------------------------------------------------------
# Step 3 – Create (or reuse) a virtual environment named 'venv'
# ---------------------------------------------------------------
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
else
  echo "Virtual environment already exists – reusing."
fi

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip and install build tools
pip install --quiet --upgrade pip setuptools wheel

# ---------------------------------------------------------------
# Step 4 – Install the package in editable mode
# ---------------------------------------------------------------
pip install -e .

# ---------------------------------------------------------------
# Step 5 – Run the setup wizard (creates config if missing)
# ---------------------------------------------------------------
python scripts/setup.py
python -m nano.scripts.setup

# ---------------------------------------------------------------
# Final message
# ---------------------------------------------------------------
echo "✅ NANO agent installed and initial setup completed."

echo "You can now start the agent with:"
echo "  source venv/bin/activate && python -m nano.main"
