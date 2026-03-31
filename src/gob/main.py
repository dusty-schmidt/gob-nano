import os
import sys
import logging
import argparse
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.gob.core.config_loader import load_config
from src.gob.core.agent_loader import load_agent
from src.gob.core.llm_client import MultiLLM
from src.gob.core.memory.memory import MemoryManager
from src.gob.core.logger import setup_logger
from src.gob.orchestrator import AgentOrchestrator
from src.gob.core.setup_wizard import GOBSetup

logger = setup_logger()


def bootstrap():
    """Initialize all core components and return them"""
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

    # Initialize memory
    try:
        memory = MemoryManager()
        logger.info(f"Memory initialized: {memory.db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize memory: {e}")
        sys.exit(1)

    # Initialize Multi-LLM Client
    try:
        llm_config = config.get("llm", {})
        llm_client = MultiLLM(config=llm_config)
        logger.info(f"MultiLLM client initialized")
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

    return config, memory, orchestrator


def check_and_setup_api_key():
    """Check if API key is configured and prompt if needed"""
    try:
        config = load_config()
        api_key = config.get("llm", {}).get("api_key") or os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            print("🔑 OpenRouter API key not found. Let's set it up...")
            print("Get your free key at: https://openrouter.ai/keys\n")
            
            # Run setup wizard
            setup = GOBSetup()
            setup.prompt_api_key()
            
            # Reload config after setup
            config = load_config()
            api_key = config.get("llm", {}).get("api_key") or os.getenv("OPENROUTER_API_KEY")
            
            if api_key:
                print("✅ API key configured successfully!")
                return True
            else:
                print("❌ API key setup failed. Please add your key to .env file manually.")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error during API key setup: {e}")
        return False


def main_entry():
    """Main entry point - parses args and launches appropriate mode"""
    parser = argparse.ArgumentParser(description="GOB-01 Agent")
    parser.add_argument("--mode", choices=["tui", "discord", "validate", "setup"], default="tui")
    args = parser.parse_args()

    if args.mode == "validate":
        # Quick validation - just check imports and config load
        print("")
        print("✓ GOB-01 imports OK")
        try:
            config = load_config()
            print("✓ Config loaded")
        except Exception as e:
            print(f"❌ Config error: {e}")
            sys.exit(1)
        api_key = config.get("llm", {}).get("api_key") or os.getenv("OPENROUTER_API_KEY")
        if api_key:
            print("✓ OpenRouter API key found")
        else:
            print("⚠️  No OpenRouter API key - set OPENROUTER_API_KEY in .env")
        print("✓ Validation complete")
        return

    if args.mode == "setup":
        # Run setup wizard
        print("🚀 Running GOB setup wizard...")
        setup = GOBSetup()
        setup.run()
        return

    # Check if API key is configured, prompt if needed
    if not check_and_setup_api_key():
        print("❌ Cannot continue without API key. Please set up your OpenRouter API key.")
        sys.exit(1)

    # Bootstrap all components
    config, memory, orchestrator = bootstrap()

    if args.mode == "tui":
        from src.gob.io.tui_chat import TUIChat
        ui = TUIChat(orchestrator, memory)
        ui.run()

    elif args.mode == "discord":
        discord_token = (
            config.get("discord", {}).get("token")
            or os.getenv("DISCORD_BOT_TOKEN")
        )
        if not discord_token:
            print("❌ Discord bot token not set. Add DISCORD_BOT_TOKEN to .env")
            sys.exit(1)
        from src.gob.io.discord_bot import GobDiscordBot
        bot = GobDiscordBot(config, memory, orchestrator)
        bot.run(discord_token)


if __name__ == "__main__":
    main_entry()
