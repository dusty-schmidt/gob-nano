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
            ("pip", "pip package manager"),
        ]
        
        for cmd, desc in checks:
            try:
                subprocess.run([cmd, "--version"], capture_output=True, check=True)
                self.print_colored(f"✓ {desc} found", "\033[0;32m")
            except subprocess.CalledProcessError:
                print(f"❌ {desc} not found - please install")
                return False
        return True

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
        
        # Activate venv
        venv_python = str(self.venv_path / "bin" / "python") if sys.platform != "win32" else str(self.venv_path / "Scripts" / "python.exe")
        
        try:
            # Upgrade pip first
            subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True, capture_output=True)
            
            # Install pyproject.toml dependencies
            subprocess.run([venv_python, "-m", "pip", "install", "-e", "."], 
                          cwd=str(self.project_root), check=True, capture_output=True)
            
            self.print_colored("✓ All dependencies installed", "\033[0;32m")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            if e.stdout:
                print(e.stdout.decode()[:500])
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

    def prompt_api_key(self) -> Optional[str]:
        """Prompt for OpenRouter API key"""
        print()
        print("─" * 70)
        print(" 🔑 Step 1: OpenRouter API Key (REQUIRED)")
        print("─" * 70)
        print()
        print(" GOB needs an LLM to work. Get your free key at:")
        print(" https://openrouter.ai/keys")
        print()
        
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
                
        print()
        print("─" * 70)
        print(" 🎮 Step 2: Discord Bot Token (OPTIONAL)")
        print("─" * 70)
        print()
        print(" Set up Discord bot for 24/7 availability")
        print()
        
        response = input(" Set up Discord bot now? (y/n): ").strip().lower()
        
        if response != "y" and response != "Y":
            print("⚠️  Discord setup skipped")
            return None
        
        print()
        print(" Discord Bot Setup Instructions:")
        print(" 1. Go to https://discord.com/developers/applications")
        print(" 2. Create new application → 'GOB Agent'")
        print(" 3. Bot tab → Add Bot → Reset Token → Copy token")
        print(" 4. OAuth2 → URL Generator → scopes: bot")
        print(" 5. Permissions: Send Messages, Read History, Manage Channels, Manage Guild")
        print()
        
        print("Paste your Discord bot token below:")
        token = input().strip()
        
        if token:
            self._save_env_var("DISCORD_BOT_TOKEN", token)
            print("✓ Discord token configured")
            return token
        
        print("⚠️  No Discord token provided")
        return None

    def _save_env_var(self, key: str, value: str):
        """Save environment variable to .env file"""
        # Read existing .env
        env_vars = {}
        if self.env_path.exists():
            with open(self.env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        env_vars[k.strip()] = v.strip()
        
        # Update and write back
        env_vars[key] = value
        with open(self.env_path, "w") as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")

    def validate_installation(self) -> bool:
        """Validate that installation works"""
        print()
        print("─" * 70)
        print(" 🔍 Step 3: Validate Installation")
        print("─" * 70)
        print()
        
        # Check Python in venv
        venv_python = str(self.venv_path / "bin" / "python") if sys.platform != "win32" else str(self.venv_path / "Scripts" / "python.exe")
        
        try:
            result = subprocess.run([venv_python, "-c", "import sys; print(sys.version)"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.print_colored("✓ Python environment configured", "\033[0;32m")
            else:
                print("❌ Python not working")
                return False
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False
        
        # Check dependencies
        try:
            result = subprocess.run([venv_python, "-c", 
                "import discord, yaml, requests, httpx, faiss, sentence_transformers, numpy; print('OK')"], 
                capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.print_colored("✓ All required packages installed", "\033[0;32m")
            else:
                print("❌ Some packages missing")
                return False
        except Exception as e:
            print(f"❌ Package validation failed: {e}")
            return False
        
        # Check config
        if self.config_path.exists():
            self.print_colored("✓ Config file exists", "\033[0;32m")
        else:
            print("⚠️  Config file missing (will be created on first run)")
        
        # Test LLM connection
        api_key = self._get_env_var("OPENROUTER_API_KEY")
        if api_key:
            try:
                from src.gob.core.llm_client import LLMClient
                client = LLMClient()
                self.print_colored("✓ LLM client configured (key found)", "\033[0;32m")
            except Exception as e:
                print(f"⚠️  LLM client: {e}")
        else:
            print("⚠️  OpenRouter API key not found - agent needs key to run")
        
        print()
        self.print_colored("═══════════════════════════════════════════════", "\033[0;32m")
        print(" ✓ VALIDATION COMPLETE")
        print("═══════════════════════════════════════════════")
        return True
    
    def _get_env_var(self, key: str) -> Optional[str]:
        """Get environment variable from .env file"""
        if self.env_path.exists():
            with open(self.env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}="):
                        return line.split("=", 1)[1].strip()
        return None

    def print_complete_message(self):
        """Print setup complete instructions"""
        print()
        print("=" * 70)
        print(" 🎉 SETUP COMPLETE!")
        print("=" * 70)
        print()
        print(f" 📍 Project: {self.project_root}")
        print()
        print(" ▶  Start GOB:")
        print("   bash scripts/gob.sh            # TUI chat")
        print("   bash scripts/gob.sh --discord  # Discord bot")
        print()
        print(" 📚 Documentation: README.md")
        print()

    def run(self):
        """Run complete setup"""
        self.print_header()
        
        # Step 1: Check prerequisites
        print("─" * 70)
        print(" ✅ Step 1: System Checks")
        print("─" * 70)
        
        if not self.check_python_version():
            print("\n❌ Setup failed - Python 3.9+ required")
            return False
        
        if not self.check_prerequisites():
            print("\n❌ Setup failed - missing prerequisites")
            return False
        
        print()
        
        # Step 2: Create environment
        print("─" * 70)
        print(" ✅ Step 2: Create Python Environment")
        print("─" * 70)
        
        if not self.create_venv():
            print("\n❌ Setup failed - venv creation")
            return False
        
        if not self.install_dependencies():
            print("\n❌ Setup failed - dependency installation")
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
