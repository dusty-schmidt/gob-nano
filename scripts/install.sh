#!/usr/bin/env bash
set -euo pipefail

# ───────────────────────────────────────────────────────────────────────────
# GOB-NANO One-Command Installer
# ───────────────────────────────────────────────────────────────────────────
# Usage: curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-nano/main/scripts/install.sh | bash
#
# Features:
# - Clones repo
# - Builds Docker container
# - Prompts for API keys
# - Configures Discord bot
# - Validates setup
# - Ready to run
# ───────────────────────────────────────────────────────────────────────────

set +e
echo
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║              GOB-NANO Agent - One-Command Setup                    ║"
echo "║          Ultra-minimal AI agent for edge devices                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo
set -e

# ───────────────────────────────────────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────────────────────────────────────
REPO_URL="git@github.com:dusty-schmidt/gob-nano.git"
REPO_HTTPS="https://github.com/dusty-schmidt/gob-nano.git"
INSTALL_DIR="${HOME}/.nano"
IMAGE_NAME="gob-nano"
CONTAINER_NAME="gob-nano"

# ───────────────────────────────────────────────────────────────────────────
# Helper Functions
# ───────────────────────────────────────────────────────────────────────────

log_info() {
    echo "ℹ️  $1"
}

log_success() {
    echo "✅ $1"
}

log_error() {
    echo "❌ $1" >&2
}

log_section() {
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

# ───────────────────────────────────────────────────────────────────────────
# Step 1: Check Prerequisites
# ───────────────────────────────────────────────────────────────────────────

log_section "Checking Prerequisites"

check_command "git"
log_success "Git is installed"

check_command "docker"
log_success "Docker is installed"

check_command "docker-compose"
log_success "Docker Compose is installed"

# ───────────────────────────────────────────────────────────────────────────
# Step 2: Clone or Update Repository
# ───────────────────────────────────────────────────────────────────────────

log_section "Setting Up Repository"

if [ -d "${INSTALL_DIR}/.git" ]; then
    log_info "Repository exists at ${INSTALL_DIR}"
    read -p "📌 Update to latest version? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Updating repository..."
        cd "${INSTALL_DIR}"
        git pull origin main
        log_success "Repository updated"
    fi
else
    log_info "Cloning gob-nano to ${INSTALL_DIR}..."
    
    # Try SSH first, fall back to HTTPS
    if ! git clone "${REPO_URL}" "${INSTALL_DIR}" 2>/dev/null; then
        log_info "SSH clone failed, trying HTTPS..."
        git clone "${REPO_HTTPS}" "${INSTALL_DIR}"
    fi
    log_success "Repository cloned"
fi

cd "${INSTALL_DIR}"

# ───────────────────────────────────────────────────────────────────────────
# Step 3: Collect Configuration
# ───────────────────────────────────────────────────────────────────────────

log_section "Configuration Setup"

# OpenRouter API Key
echo "🔑 OpenRouter API Key"
echo "   Get one at: https://openrouter.ai/keys"
echo
read -p "Enter your OpenRouter API key: " OPENROUTER_API_KEY

if [ -z "${OPENROUTER_API_KEY}" ]; then
    log_error "OpenRouter API key is required"
    exit 1
fi
log_success "OpenRouter API key saved"

echo

# Discord Bot Token (optional)
echo "🤖 Discord Bot Token (optional)"
echo "   Skip to configure later, or enter token now."
echo "   Get one at: https://discord.com/developers/applications"
echo
read -p "Enter Discord bot token (or press Enter to skip): " DISCORD_BOT_TOKEN || DISCORD_BOT_TOKEN=""

if [ -n "${DISCORD_BOT_TOKEN}" ]; then
    log_success "Discord bot token saved"
else
    log_info "Discord bot setup skipped (can configure later)"
fi

echo

# Save .env file
log_section "Creating Configuration Files"

cat > "${INSTALL_DIR}/.env" << EOF
# OpenRouter Configuration
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}

# Discord Bot Configuration
DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN:-your_discord_bot_token_here}
EOF

log_success ".env file created"

if [ -z "${DISCORD_BOT_TOKEN}" ]; then
    echo "   📝 To add Discord bot later, edit: ${INSTALL_DIR}/.env"
fi

echo

# ───────────────────────────────────────────────────────────────────────────
# Step 4: Build Docker Image
# ───────────────────────────────────────────────────────────────────────────

log_section "Building Docker Image"

log_info "Building ${IMAGE_NAME}:latest..."
log_info "This may take a minute on first build..."
echo

docker-compose build --no-cache

log_success "Docker image built successfully"

echo

# ───────────────────────────────────────────────────────────────────────────
# Step 5: Validate Installation
# ───────────────────────────────────────────────────────────────────────────

log_section "Validating Installation"

log_info "Running validation tests..."
echo

docker-compose run --rm nano pytest tests/ -q

log_success "All tests passed!"

echo

# ───────────────────────────────────────────────────────────────────────────
# Step 6: Discord Bot Setup (if token provided)
# ───────────────────────────────────────────────────────────────────────────

if [ -n "${DISCORD_BOT_TOKEN}" ]; then
    log_section "Discord Bot Configuration"
    
    echo "✅ Discord bot token is configured."
    echo
    echo "📌 Next steps:"
    echo "   1. Invite the bot to your server:"
    echo "      https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot"
    echo
    echo "   2. Replace YOUR_CLIENT_ID with your bot's Client ID from Discord Developer Portal"
    echo
    echo "   3. The bot will be ready once you start the container:"
    echo "      docker-compose up"
    echo
fi

# ───────────────────────────────────────────────────────────────────────────
# Step 7: Final Instructions
# ───────────────────────────────────────────────────────────────────────────

log_section "Installation Complete! 🎉"

echo "✨ GOB-NANO is ready to use!"
echo
echo "📂 Installation directory: ${INSTALL_DIR}"
echo
echo "🚀 To start the agent:"
echo "   cd ${INSTALL_DIR}"
echo "   docker-compose up"
echo
echo "🧪 To run tests:"
echo "   docker-compose run --rm nano pytest tests/ -v"
echo
echo "📝 To edit configuration:"
echo "   nano ${INSTALL_DIR}/.env"
echo "   nano ${INSTALL_DIR}/config/config.yaml"
echo
echo "📖 For more info:"
echo "   cat ${INSTALL_DIR}/README.md"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Status: Ready ✅"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
