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

# Check and install Docker if needed
if ! command -v "docker" &> /dev/null; then
    log_info "Docker is not installed. Installing..."
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        log_info "Detected macOS. Installing Docker via Homebrew..."
        if ! command -v "brew" &> /dev/null; then
            log_error "Homebrew is required. Please install it first:"
            echo "  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        brew install docker docker-compose
        log_success "Docker installed via Homebrew"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux (Ubuntu/Debian)
        log_info "Detected Linux. Installing Docker..."
        sudo apt-get update
        sudo apt-get install -y docker.io docker-compose
        # Add user to docker group
        sudo usermod -aG docker "$USER"
        log_success "Docker installed. Please log out and back in, or run: newgrp docker"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        log_error "Windows detected. Please install Docker Desktop:"
        echo "  https://www.docker.com/products/docker-desktop"
        exit 1
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
else
    log_success "Docker is installed"
fi

check_command "docker-compose"
log_success "Docker Compose is installed"

# ───────────────────────────────────────────────────────────────────────────
# Step 2: Clone or Update Repository
# ───────────────────────────────────────────────────────────────────────────

log_section "Setting Up Repository"

if [ -d "${INSTALL_DIR}/.git" ]; then
    log_info "Repository exists at ${INSTALL_DIR}"
    echo
    echo "📌 Found existing installation. Choose an option:"
    echo
    echo "   1️⃣  Delete old version and install fresh (backs up first)"
    echo "   2️⃣  Install alongside (different directory name)"
    echo "   3️⃣  Overwrite existing installation (git pull)"
    echo "   4️⃣  Cancel installation"
    echo
    
    CHOICE=""
    while [ -z "${CHOICE}" ] || ! [[ "${CHOICE}" =~ ^[1-4]$ ]]; do
        read -p "👉 Enter your choice (1-4): " CHOICE
        
        if [ -z "${CHOICE}" ]; then
            echo "❌ Please enter a number between 1 and 4"
            CHOICE=""
        elif ! [[ "${CHOICE}" =~ ^[1-4]$ ]]; then
            echo "❌ Invalid choice '${CHOICE}'. Please enter 1, 2, 3, or 4."
            CHOICE=""
        fi
    done
    
    case ${CHOICE} in
        1)
            log_info "Backing up old installation..."
            BACKUP_DIR="${INSTALL_DIR}-backup-$(date +%Y%m%d-%H%M%S)"
            mv "${INSTALL_DIR}" "${BACKUP_DIR}"
            log_success "Old installation backed up to: ${BACKUP_DIR}"
            log_info "Cloning fresh gob-nano to ${INSTALL_DIR}..."
            if ! git clone "${REPO_URL}" "${INSTALL_DIR}" 2>/dev/null; then
                log_info "SSH clone failed, trying HTTPS..."
                git clone "${REPO_HTTPS}" "${INSTALL_DIR}"
            fi
            log_success "Repository cloned"
            ;;
        2)
            log_info "Installing alongside existing installation..."
            SUFFIX="-$(date +%Y%m%d-%H%M%S)"
            NEW_INSTALL_DIR="${INSTALL_DIR}${SUFFIX}"
            INSTALL_DIR="${NEW_INSTALL_DIR}"
            log_info "New installation directory: ${INSTALL_DIR}"
            log_info "Cloning gob-nano to ${INSTALL_DIR}..."
            if ! git clone "${REPO_URL}" "${INSTALL_DIR}" 2>/dev/null; then
                log_info "SSH clone failed, trying HTTPS..."
                git clone "${REPO_HTTPS}" "${INSTALL_DIR}"
            fi
            log_success "Repository cloned"
            ;;
        3)
            log_info "Overwriting existing installation..."
            cd "${INSTALL_DIR}"
            git pull origin main
            log_success "Repository updated"
            ;;
        4)
            log_error "Installation cancelled by user"
            exit 0
            ;;
    esac
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

# Check if we have interactive terminal
if [ ! -t 0 ]; then
    # Try to use /dev/tty for interactive input
    exec < /dev/tty || {
        log_error "This installer requires an interactive terminal."
        echo "Please run it directly, not piped:"
        echo "  bash <(curl -fsSL https://raw.githubusercontent.com/dusty-schmidt/gob-nano/main/scripts/install.sh)"
        exit 1
    }
fi

# OpenRouter API Key
echo "🔑 OpenRouter API Key (Required)"
echo
echo "   Step 1: Open this link in your browser:"
echo "   ➜ https://openrouter.ai/keys"
echo
echo "   Step 2: Create a new API key if you don't have one"
echo
echo "   Step 3: Copy the key and paste it below"
echo

OPENROUTER_API_KEY=""
while [ -z "${OPENROUTER_API_KEY}" ]; do
    read -p "Paste your OpenRouter API key: " OPENROUTER_API_KEY < /dev/tty
    if [ -z "${OPENROUTER_API_KEY}" ]; then
        echo "❌ API key cannot be empty."
        echo "   Please go to https://openrouter.ai/keys and get your key."
        read -p "Press Enter to try again..." < /dev/tty
    fi
done
log_success "OpenRouter API key saved"

echo

# Discord Bot Token (optional)
echo "🤖 Discord Bot Token (optional)"
echo
echo "   To set up Discord bot integration now:"
echo "   Step 1: Open https://discord.com/developers/applications"
echo "   Step 2: Create a new application and get the bot token"
echo "   Step 3: Paste it below"
echo
echo "   Or press Enter to skip (configure later in .env)"
echo

read -p "Enter Discord bot token (or press Enter to skip): " DISCORD_BOT_TOKEN < /dev/tty || DISCORD_BOT_TOKEN=""

if [ -n "${DISCORD_BOT_TOKEN}" ]; then
    log_success "Discord bot token saved"
else
    log_info "Discord bot setup skipped"
    echo "   📝 You can add it later by editing: \${INSTALL_DIR}/.env"
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
