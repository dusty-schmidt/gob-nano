#!/usr/bin/env python3
"""
GOB - Ultra-minimal AI agent framework
Entry point
"""

import sys
import os
import argparse
from pathlib import Path

from gob.core.config_loader import load_config
from gob.core.llm_client import MultiLLM
from gob.core.logger import setup_logger, log_to_chat
from gob.core.memory.memory import MemoryManager

logger = setup_logger()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='GOB - Ultra-minimal AI agent')
    parser.add_argument('--tui', action='store_true', help='Launch TUI chat interface (default)')
    parser.add_argument('--version', action='version', version='GOB 1.0.0')
    return parser.parse_args()


def setup_environment():
    """Set up environment variables and paths"""
    gob_home = Path.home() / '.gob'
    os.makedirs(gob_home, exist_ok=True)
    os.environ['GOB_HOME'] = str(gob_home)
    return gob_home


def check_api_key(config):
    """Check if API key is available. Returns True if found, False otherwise."""
    api_key = config.get("llm", {}).get("api_key") or os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("\n❌ OpenRouter API key not found.\n")
        print("To set up your API key:")
        print("  1. Get a key from https://openrouter.ai/keys")
        print("  2. Create a .env file in the project root:")
        print("     echo 'OPENROUTER_API_KEY=sk-or-...' > .env")
        print()
        return False

    return True


def main_entry():
    """Main entry point - parses args and launches TUI"""
    args = parse_args()

    # Set up environment
    gob_home = setup_environment()

    # Load configuration
    config = load_config()

    # Check API key
    if not check_api_key(config):
        sys.exit(1)

    # Initialize memory (SQLite only, lightweight)
    memory = MemoryManager()
    logger.info("Memory initialized")

    # Initialize LLM client
    llm_config = config.get("llm", {})
    llm_client = MultiLLM(llm_config)
    logger.info(f"LLM client initialized (model: {llm_client.chat_model})")

    # Load agent config
    from gob.core.agent_loader import load_agent
    agent_config = load_agent(config.get("agent", {}).get("profile", "default"))

    # Initialize orchestrator
    from gob.core.orchestrator import AgentOrchestrator
    tools_config = config.get("tools", {})
    orchestrator = AgentOrchestrator(llm_client, memory, agent_config, tools_config)
    logger.info("Orchestrator initialized")

    # Launch TUI
    from gob.ux.tui_chat import TUIChat
    logger.info("Launching TUI chat interface...")
    chat = TUIChat(orchestrator, memory)
    chat.run()


if __name__ == "__main__":
    main_entry()