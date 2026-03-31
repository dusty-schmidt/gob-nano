#!/usr/bin/env python3
"""
GOB - Ultra-minimal AI agent for edge devices
Main module with TUI chat interface
"""

import sys
import os
import argparse
from pathlib import Path

from gob.core.config_loader import load_config
from gob.core.llm_client import MultiLLMClient
from gob.core.setup_wizard import GOBSetup
from gob.core.logger import log_to_chat
from gob.orchestrator import AgentOrchestrator
from gob.core.memory import MemoryManager
from gob.io.discord_bot import GobDiscordBot


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='GOB - Ultra-minimal AI agent')
    parser.add_argument('--tui', action='store_true', help='Launch TUI chat interface')
    parser.add_argument('--discord', action='store_true', help='Launch Discord bot')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    return parser.parse_args()


def setup_environment():
    """Set up environment variables and paths"""
    gob_home = Path.home() / '.gob'
    os.makedirs(gob_home, exist_ok=True)
    os.makedirs(gob_home / 'src' / 'gob' / 'core' / 'memory', exist_ok=True)
    
    # Set environment variables
    os.environ['GOB_HOME'] = str(gob_home)
    
    return gob_home


def check_and_setup_api_key():
    """Check if API key is configured and run setup wizard if needed"""
    try:
        config = load_config()
        api_key = config.get("llm", {}).get("api_key") or os.getenv("OLLAMA_CLOUD_API_KEY")
        
        if not api_key:
            log_to_chat("INFO", "🔑 Ollama API key not found. Let's set it up...")
            log_to_chat("INFO", "Get your free key at: https://ollama.com/download\n")
            
            # Run setup wizard
            setup = GOBSetup()
            setup.prompt_api_key()
            
            # Reload config after setup
            config = load_config()
            api_key = config.get("llm", {}).get("api_key") or os.getenv("OLLAMA_CLOUD_API_KEY")
            
            if api_key:
                log_to_chat("INFO", "✅ API key configured successfully!")
                return True
            else:
                log_to_chat("ERROR", "❌ API key setup failed. Please add your key to .env file manually.")
                return False
        
        return True
    except Exception as e:
        log_to_chat("ERROR", f"❌ Error during API key setup: {e}")
        return False


def main_entry():
    """Main entry point - parses args and launches appropriate mode"""
    args = parse_args()
    
    # Set up environment
    gob_home = setup_environment()
    
    # Check API key
    if not check_and_setup_api_key():
        sys.exit(1)
    
    # Load configuration
    config = load_config()
    
    # Initialize memory
    memory_path = gob_home / 'src' / 'gob' / 'core' / 'memory' / 'memory.db'
    memory = Memory(str(memory_path))
    log_to_chat("INFO", f"Memory initialized: {memory_path}")
    
    # Initialize LLM client
    llm_client = MultiLLMClient(config)
    log_to_chat("INFO", "MultiLLM client initialized")
    
    # Initialize orchestrator
    orchestrator = Orchestrator(llm_client, memory, config)
    log_to_chat("INFO", "Orchestrator initialized")
    
    # Launch appropriate mode
    if args.discord:
        log_to_chat("INFO", "Launching Discord bot...")
        bot = DiscordBot(orchestrator, config)
        bot.run()
    else:
        # Default to TUI mode
        log_to_chat("INFO", "Launching TUI chat interface...")
        chat = TUIChat(orchestrator, config)
        chat.start()


if __name__ == "__main__":
    main_entry()