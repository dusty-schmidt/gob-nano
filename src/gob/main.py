import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gob.core.config_loader import load_config
from src.gob.core.agent_loader import load_agent
from src.gob.core.llm_client import MultiLLM
from src.gob.core.memory.memory import MemoryManager
from src.gob.core.setup_wizard import run_api_key_wizard, run_discord_wizard
from src.gob.orchestrator import AgentOrchestrator
from src.gob.core.logger import setup_logger
from src.gob.core.logger import setup_logger

def main():
    # Setup logging
    logger = setup_logger()
    logger.info("Starting GOB Agent...")

    # Load config
    try:
        config = load_config()
        logger.info("Config loaded")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    # Load agent profile
    try:
        agent_profile = config.get("agent", {}).get("profile", "default")
        agent_config = load_agent(agent_profile)
        logger.info(f"Agent profile loaded: {agent_config.get('name', agent_profile)}")
    except Exception as e:
        logger.error(f"Failed to load agent profile: {e}")
        sys.exit(1)

    # Initialize memory (SQLite)
    try:
        memory = MemoryManager()
        logger.info(f"Memory initialized: {memory.db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize memory: {e}")
        sys.exit(1)

    # Initialize Multi-LLM Client
    try:
        llm_config = config.get("llm", {})
        # Pass config dict directly to MultiLLM
        llm_client = MultiLLM(config=llm_config)
        logger.info(f"MultiLLM client initialized: {llm_config.get('model')}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        sys.exit(1)

    # Initialize Orchestrator
    try:
        orchestrator = AgentOrchestrator(
            llm_client=llm_client,
            memory=memory,
            agent_config=agent_config,
            tools_config=config.get("tools", {})
        )
        logger.info("Orchestrator initialized")
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        sys.exit(1)

    # Argument parsing
# Parse arguments at entry point to support console_scripts
def main_entry():
    """CLI entry point for 'gob' command after pip install"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["tui", "discord", "validate"], default="tui")
    args = parser.parse_args()

    if args.mode == "validate":
        logger.info("Configuration validation complete")
        return

    if args.mode == "tui":
        from src.gob.io.tui_chat import TUIChat
        ui = TUIChat(orchestrator, memory)
        ui.run()
    elif args.mode == "discord":
        # Check for Discord token
        discord_token = config.get("discord", {}).get("token")
        if not discord_token:
            discord_token = run_discord_wizard()
        
        from src.gob.io.discord_bot import GobDiscordBot
        bot = GobDiscordBot(config, memory, orchestrator)
        bot.run(discord_token)

if __name__ == "__main__":
    main()

# Also register main_entry for console_scripts in pyproject.toml
if __name__ == "__console_scripts__":
    main_entry()
