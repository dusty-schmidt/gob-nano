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
from typing import Optional

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
        print("")
        print("=" * 70)
        print(" 🚀 GOB-01 Complete Installation & Setup")
        print("=" * 70)
        print()
        print(f" 📍 Project Directory: {self.project_root.absolute()}")
        print()

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
            print(f"❌ Python 3.9+ required (found {version[0]}.{version[1]})")
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
        
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            self.print_colored("✓ Virtual environment created", "\033[0;32m")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create venv: {e}")
            return False

    def install_dependencies(self) -> bool:
        """Install all required Python packages"""
        print("Installing Python dependencies...")
        
        venv_python = str(self.venv_path / "bin" / "python") if sys.platform != "win32" else str(self.venv_path / "Scripts" / "python.exe")
        
        try:
            subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True, capture_output=True)
            subprocess.run([venv_python, "-m", "pip", "install", "-e", "."], cwd=str(self.project_root), check=True, capture_output=True)
            self.print_colored("✓ All dependencies installed", "\033[0;32m")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

    def create_env_file(self):
        """Create .env file with template"""
        if self.env_path.exists():
            self.print_colored("✓ .env file exists", "\033[0;32m")
        else:
            print("Creating .env file...")
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
        print(f"\n{self.section_break}")
        print(" 🔑 Step 1: OpenRouter API Key (REQUIRED)")
        print(f"{self.section_break}\n")
        
        # Check if key is provided in environment (non-interactive mode)
        env_key = os.environ.get("GOB_OPENROUTER_API_KEY")
        if env_key:
            print("Found OpenRouter API key in environment.")
            self.update_env_file("OPENROUTER_API_KEY", env_key)
            print(f"{self.colored('✓ API key configured from environment', self.GREEN)}")
            return

        print("GOB needs an LLM to work. Get your free key at:")
        print("https://openrouter.ai/keys\n")
        print("Paste your OpenRouter API key below (or press Enter to skip):")
        
        # Check if running interactively
        if sys.stdin.isatty():
            key = input("> ").strip()
        else:
            # Non-interactive mode (piped input) - read from stdin
            key = sys.stdin.readline().strip()
            
        if key:
            self.update_env_file("OPENROUTER_API_KEY", key)
            print(f"{self.colored('✓ API key configured', self.GREEN)}")
        else:
            print(f"{self.colored('⚠️  No API key provided', self.YELLOW)}")

    def prompt_discord_token(self):
        """Prompt for Discord Bot Token"""
        print(f"\n{self.section_break}")
        print(" 🎮 Step 2: Discord Bot Token (OPTIONAL)")
        print(f"{self.section_break}\n")
        
        print("Set up Discord bot for 24/7 availability\n")
        
        # Check if token is provided in environment
        env_token = os.environ.get("DISCORD_BOT_TOKEN")
        if env_token:
            print("Found Discord bot token in environment.")
            self.update_env_file("DISCORD_BOT_TOKEN", env_token)
            print(f"{self.colored('✓ Discord token configured from environment', self.GREEN)}")
            return
            
        print("Set up Discord bot now? (y/n): ", end="")
        
        # Check if running interactively
        if sys.stdin.isatty():
            choice = input().strip().lower()
        else:
            # Non-interactive mode (piped input) - default to n
            choice = "n"
            
        if choice == 'y':
            print("\nEnter your Discord bot token:")
            token = input("> ").strip()
            if token:
                self.update_env_file("DISCORD_BOT_TOKEN", token)
                print(f"{self.colored('✓ Discord token configured', self.GREEN)}")
            else:
                print(f"{self.colored('⚠️  No token provided', self.YELLOW)}")
        else:
            print(f"{self.colored('⚠️  Discord setup skipped', self.YELLOW)}")

    def validate_installation(self) -> bool:
        """Validate that installation works"""
        print(f"\n{self.section_break}")
        print(" 🔍 Step 3: Validate Installation")
        print(f"{self.section_break}\n")
        
        checks = [
            ("Python environment configured", self.venv_path.exists()),
            ("Config file exists", self.config_path.exists()),
        ]
        
        all_passed = True
        for desc, check in checks:
            if check:
                print(f"✓ {desc}")
            else:
                print(f"❌ {desc}")
                all_passed = False
                
        # Check LLM config
        try:
            import sys
            sys.path.append(str(self.project_root))
            from src.gob.core.config_loader import load_config
            config = load_config()
            llm_config = config.get("llm", {})
            if llm_config.get("api_key"):
                print(f"✓ LLM client configured (key found)")
            else:
                print(f"⚠️  OpenRouter API key not found - agent needs key to run")
        except Exception as e:
            print(f"❌ Config validation failed: {e}")
            all_passed = False
        """Print completion message"""
        print(f"\n{self.GREEN}═══════════════════════════════════════{self.NC}")
        print(f"{self.GREEN} 🎉 SETUP COMPLETE!{self.NC}")
        print(f"{self.GREEN}═══════════════════════════════════════{self.NC}")
        print()
        print(f"{self.BLUE} 📍 Project: {self.project_root.absolute()}{self.NC}")
        print()
        print(f"{self.BLUE} ▶  Start GOB:{self.NC}")
        print(f"   bash scripts/gob.sh            # TUI chat")
        print(f"   bash scripts/gob.sh --discord  # Discord bot")
        print()

    def run(self):
        """Run complete setup"""
        self.print_header()
        
        # Step 1: System Checks
        print("─" * 70)
        print(" ✅ Step 1: System Checks")
        print("─" * 70)
        
        if not self.check_python_version():
            return False
        if not self.check_prerequisites():
            return False
        print()
        
        # Step 2: Create environment
        print("─" * 70)
        print(" ✅ Step 2: Create Python Environment")
        print("─" * 70)
        
        if not self.create_venv():
            return False
        if not self.install_dependencies():
            return False
        self.create_env_file()
        print()
        
        # Step 3: Configure credentials
        print("─" * 70)
        print(" ✅ Step 3: Configure Credentials")
        print("─" * 70)
        
        self.prompt_api_key()
        print()
        self.prompt_discord_token()
        
        # Step 4: Validate
        print()
        if not self.validate_installation():
            print("\n❌ Validation failed")
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
