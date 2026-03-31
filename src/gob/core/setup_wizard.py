#!/usr/bin/env python3
"""
GOB-01 Single-Command Setup Wizard
Handles: dependencies, venv, config, API keys, Discord setup, validation
Usage: gob-setup or python setup_wizard.py or ./gob.sh setup
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from gob.core.logger import log_to_chat

class GOBSetup:
    """Complete setup wizard for GOB-01"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parent.parent.parent.parent
        self.venv_path = self.project_root / "venv"
        self.env_path = self.project_root / ".env"
        self.config_path = self.project_root / "config" / "config.yaml"
        self.section_break = "─" * 70
        self.GREEN = "\033[0;32m"
        self.YELLOW = "\033[1;33m"
        self.RED = "\033[0;31m"
        self.BLUE = "\033[0;34m"
        self.NC = "\033[0m"

    def print_header(self):
        """Print colored header"""
        log_to_chat("INFO", "")
        log_to_chat("INFO", "=" * 70)
        log_to_chat("INFO", " 🚀 GOB-01 Complete Installation & Setup")
        log_to_chat("INFO", "=" * 70)
        log_to_chat("INFO", "")
        log_to_chat("INFO", f" 📍 Project Directory: {self.project_root.absolute()}")
        log_to_chat("INFO", "")

    def print_colored(self, text: str, color: str = "\033[0;32m"):
        """Print colored text"""
        end_color = "\033[0m"
        print(f"{color}{text}{end_color}")

    def colored(self, text: str, color: str = "\033[0;32m"):
        """Return colored text"""
        end_color = "\033[0m"
        return f"{color}{text}{end_color}"

    def check_python_version(self) -> bool:
        """Check Python 3.9+ requirement"""
        version = (sys.version_info.major, sys.version_info.minor)
        if version >= (3, 9):
            self.print_colored(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} found", "\033[0;32m")
            return True
        else:
            log_to_chat("ERROR", f"❌ Python 3.9+ required (found {version[0]}.{version[1]})")
            return False

    def check_prerequisites(self) -> bool:
        """Check git and pip"""
        checks = [
            ("git", "Git command"),
            ("pip3", "pip package manager"),
        ]
        for cmd, desc in checks:
            if not shutil.which(cmd):
                print(f"❌ {desc} not found - please install")
                return False
        return True

    def update_env_file(self, key: str, value: str):
        """Update or add a key-value pair in .env file"""
        env_lines = []
        if self.env_path.exists():
            with open(self.env_path, "r") as f:
                env_lines = f.readlines()
        
        updated = False
        for i, line in enumerate(env_lines):
            if line.strip().startswith(f"{key}="):
                env_lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        if not updated:
            env_lines.append(f"{key}={value}\n")
        
        with open(self.env_path, "w") as f:
            f.writelines(env_lines)

    def create_venv(self) -> bool:
        """Create Python virtual environment"""
        if self.venv_path.exists():
            self.print_colored(f"✓ Virtual environment exists", "\033[0;32m")
            return True
        
        log_to_chat("INFO", "Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            self.print_colored("✓ Virtual environment created", "\033[0;32m")
            return True
        except subprocess.CalledProcessError as e:
            log_to_chat("ERROR", f"❌ Failed to create venv: {e}")
            return False

    def install_dependencies(self) -> bool:
        """Install all required Python packages with progress feedback"""
        log_to_chat("INFO", "Installing Python dependencies...")
        
        venv_python = str(self.venv_path / "bin" / "python") if sys.platform != "win32" else str(self.venv_path / "Scripts" / "python.exe")
        
        try:
            # Upgrade pip with progress
            log_to_chat("INFO", "  → Upgrading pip...")
            subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
            
            # Install package with verbose output
            log_to_chat("INFO", "  → Installing GOB package...")
            result = subprocess.run([venv_python, "-m", "pip", "install", "-e", "."], 
                                    cwd=str(self.project_root), 
                                    capture_output=True, 
                                    text=True)
            
            if result.returncode != 0:
                log_to_chat("ERROR", f"❌ Installation failed: {result.stderr}")
                return False
                
            self.print_colored("✓ All dependencies installed", "\033[0;32m")
            return True
        except subprocess.CalledProcessError as e:
            log_to_chat("ERROR", f"❌ Failed to install dependencies: {e}")
            return False

    def create_env_file(self):
        """Create .env file with template"""
        if self.env_path.exists():
            self.print_colored("✓ .env file exists", "\033[0;32m")
        else:
            log_to_chat("INFO", "Creating .env file...")
            env_template = """# GOB-01 Configuration Environment Variables

# OpenRouter API Key (required for LLM)
# Get your free key at: https://openrouter.ai/keys
OPENROUTER_API_KEY=

# Discord Bot Token (optional)
# Get your bot token from https://discord.com/developers/applications
DISCORD_BOT_TOKEN=
"""
            with open(self.env_path, "w") as f:
                f.write(env_template)
            self.print_colored("✓ .env file created", "\033[0;32m")

    def prompt_api_key(self):
        """Prompt for OpenRouter API key"""
        log_to_chat("INFO", f"\n{self.section_break}")
        log_to_chat("INFO", " 🔑 Step 1: OpenRouter API Key (REQUIRED)")
        log_to_chat("INFO", f"{self.section_break}\n")
        
        # Check if key is provided in environment (non-interactive mode)
        env_key = os.environ.get("GOB_OPENROUTER_API_KEY")
        if env_key:
            log_to_chat("INFO", "Found OpenRouter API key in environment.")
            self.update_env_file("OPENROUTER_API_KEY", env_key)
            log_to_chat("INFO", f"{self.colored('✓ API key configured from environment', self.GREEN)}")
            return

        log_to_chat("INFO", "GOB needs an LLM to work. Get your free key at:")
        log_to_chat("INFO", "https://openrouter.ai/keys\n")
        log_to_chat("INFO", "Paste your OpenRouter API key below (or press Enter to skip):")
        
        # Check if running interactively
        if sys.stdin.isatty():
            key = input("> ").strip()
        else:
            # Non-interactive mode (piped input) - read from stdin
            # If env var is set, use it. Otherwise, read from stdin.
            if env_key:
                key = env_key
            else:
                key = sys.stdin.readline().strip()
        
        if key:
            self.update_env_file("OPENROUTER_API_KEY", key)
            log_to_chat("INFO", f"{self.colored('✓ API key configured', self.GREEN)}")
        else:
            log_to_chat("WARNING", f"{self.colored('⚠️  No API key provided', self.YELLOW)}")

    def prompt_discord_token(self):
        """Prompt for Discord Bot Token"""
        log_to_chat("INFO", f"\n{self.section_break}")
        log_to_chat("INFO", " 🎮 Step 2: Discord Bot Token (OPTIONAL)")
        log_to_chat("INFO", f"{self.section_break}\n")
        
        log_to_chat("INFO", "Set up Discord bot for 24/7 availability\n")
        
        # Check if token is provided in environment
        env_token = os.environ.get("DISCORD_BOT_TOKEN")
        if env_token:
            log_to_chat("INFO", "Found Discord bot token in environment.")
            log_to_chat("INFO", f"{self.colored('✓ Discord token configured from environment', self.GREEN)}")
            return
            
        log_to_chat("INFO", "Set up Discord bot now? (y/n): ", end="")
        
        # Check if running interactively
        if sys.stdin.isatty():
            choice = input().strip().lower()
        else:
            # Non-interactive mode (piped input) - default to n
            choice = "n"
            
        if choice == 'y':
            log_to_chat("INFO", "\nEnter your Discord bot token:")
            token = input("> ").strip()
            if token:
                self.update_env_file("DISCORD_BOT_TOKEN", token)
                log_to_chat("INFO", f"{self.colored('✓ Discord token configured', self.GREEN)}")
            else:
                log_to_chat("WARNING", f"{self.colored('⚠️  No token provided', self.YELLOW)}")
        else:
            log_to_chat("WARNING", f"{self.colored('⚠️  Discord setup skipped', self.YELLOW)}")

    def validate_installation(self) -> bool:
        """Validate that installation works"""
        log_to_chat("INFO", f"\n{self.section_break}")
        log_to_chat("INFO", " 🔍 Step 3: Validate Installation")
        log_to_chat("INFO", f"{self.section_break}\n")
        
        checks = [
            ("Python environment configured", self.venv_path.exists()),
            ("Config file exists", self.config_path.exists()),
        ]
        
        all_passed = True
        for desc, check in checks:
            if check:
                log_to_chat("INFO", f"✓ {desc}")
            else:
                log_to_chat("ERROR", f"❌ {desc}")
                all_passed = False
                
        # Check LLM config
        try:
            import sys
            sys.path.append(str(self.project_root))
            from src.gob.core.config_loader import load_config
            config = load_config()
            llm_config = config.get("llm", {})
            if llm_config.get("api_key"):
                log_to_chat("INFO", f"✓ LLM client configured (key found)")
            else:
                log_to_chat("WARNING", f"⚠️  OpenRouter API key not found - agent needs key to run")
                log_to_chat("WARNING", f"  → Add your API key to {self.env_path.absolute()}")
                log_to_chat("WARNING", f"  → Get a free key at: https://openrouter.ai/keys")
        except ImportError as e:
            log_to_chat("WARNING", f"⚠️  Config validation skipped - dependencies not installed yet")
            return True
        except Exception as e:
            log_to_chat("ERROR", f"❌ Config validation failed: {e}")
            all_passed = False
        
        return all_passed

    def print_complete_message(self):
        """Print completion message"""
        log_to_chat("INFO", f"\n{self.GREEN}═══════════════════════════════════════{self.NC}")
        log_to_chat("INFO", f"{self.GREEN} 🎉 SETUP COMPLETE!{self.NC}")
        log_to_chat("INFO", f"{self.GREEN}═══════════════════════════════════════{self.NC}")
        log_to_chat("INFO", "")
        log_to_chat("INFO", f"{self.BLUE} 📍 Project: {self.project_root.absolute()}{self.NC}")
        log_to_chat("INFO", "")
        log_to_chat("INFO", f"{self.BLUE} ▶  Start GOB:{self.NC}")
        log_to_chat("INFO", f"   bash scripts/gob.sh            # TUI chat")
        log_to_chat("INFO", f"   bash scripts/gob.sh --discord  # Discord bot")
        log_to_chat("INFO", "")

    def run(self):
        """Run complete setup"""
        self.print_header()
        
        # Step 1: System Checks
        log_to_chat("INFO", "─" * 70)
        log_to_chat("INFO", " ✅ Step 1: System Checks")
        log_to_chat("INFO", "─" * 70)
        
        if not self.check_python_version():
            return False
        if not self.check_prerequisites():
            return False
        log_to_chat("INFO", "")
        
        # Step 2: Create environment
        log_to_chat("INFO", "─" * 70)
        log_to_chat("INFO", " ✅ Step 2: Create Python Environment")
        log_to_chat("INFO", "─" * 70)
        
        if not self.create_venv():
            return False
        if not self.install_dependencies():
            return False
        self.create_env_file()
        log_to_chat("INFO", "")
        
        # Step 3: Configure credentials
        log_to_chat("INFO", "─" * 70)
        log_to_chat("INFO", " ✅ Step 3: Configure Credentials")
        log_to_chat("INFO", "─" * 70)
        
        self.prompt_api_key()
        log_to_chat("INFO", "")
        self.prompt_discord_token()
        
        # Step 4: Validate
        log_to_chat("INFO", "")
        if not self.validate_installation():
            log_to_chat("ERROR", "\n❌ Validation failed")
            return False
        
        self.print_complete_message()
        return True


def setup_command():
    """Command-line entry point"""
    wizard = GOBSetup()
    success = wizard.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(setup_command())