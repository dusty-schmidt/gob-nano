"""GOB Agent - Main entry point"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


from src.gob.helpers.agent_loader import load_agent
from src.gob.helpers.config_loader import load_config
from src.gob.helpers.llm_client import LLMClient
from src.gob.helpers.memory.memory import MemoryManager
from src.gob.helpers.setup_wizard import run_api_key_wizard, run_discord_wizard
from src.gob.orchestrator import AgentOrchestrator


def main():
    """Initialize and run the NANO agent"""
    # Parse command line arguments first
    parser = argparse.ArgumentParser(description="GOB-GOB Agent")
    parser.add_argument(
        "--mode",
        choices=["tui", "discord", "validate"],
        default="tui",
        help="Run mode: tui (interactive chat), discord (bot), validate (check config only)",
    )
    args = parser.parse_args()

    print("🚀 Starting GOB Agent...")

    # Load configuration
    try:
        config = load_config()
        logger.info("Config loaded")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        sys.exit(1)

    # Load agent profile
    try:
        agent_profile = config.get("agent", {}).get("profile", "default")
        agent = load_agent(agent_profile)
        print(f"✅ Agent profile loaded: {agent.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Failed to load agent: {e}")
        sys.exit(1)

    # Initialize memory
    try:
        memory_dir = Path(__file__).parent / "helpers" / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        memory_file = memory_dir / "memory.jsonl"
        memory = MemoryManager(memory_file)
        print(f"✅ Memory initialized: {memory_file}")
    except Exception as e:
        print(f"❌ Failed to initialize memory: {e}")
        sys.exit(1)

    # Initialize LLM client with deferred setup
    try:
        llm_config = config.get("llm", {})
        llm = LLMClient(llm_config)
        print(f"✅ LLM client initialized: {llm.model}")
    except ValueError as e:
        if "API key not configured" in str(e):
            print("\n🔑 OpenRouter API key is missing.")
            print("Starting setup wizard...\n")
            run_api_key_wizard()
            # Reload config to pick up new env var
            load_dotenv()
            try:
                llm = LLMClient(config.get("llm", {}))
                print(f"✅ LLM client initialized: {llm.model}")
            except Exception as retry_e:
                print(f"❌ Failed to initialize LLM after setup: {retry_e}")
                sys.exit(1)
        else:
            print(f"❌ Failed to initialize LLM: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        sys.exit(1)

    # Initialize orchestrator
    try:
        orchestrator = AgentOrchestrator(
            llm_client=llm,
            memory=memory,
            agent_config=agent,
            tools_config=config.get("tools", {}),
        )
        print(f"✅ Orchestrator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        sys.exit(1)

    print("")
    print("═" * 50)
    print("Agent initialized successfully!")
    print("═" * 50)
    print("")

    # Run in selected mode
    if args.mode == "validate":
        print("✅ Configuration validation complete")
        print(f"   Agent: {agent.get('name', 'Unknown')}")
        print(f"   Model: {llm.model}")
        print(f"   Tools: {', '.join(orchestrator.enabled_tools)}")
        print("")
        print("System is ready to run!")
        return

    elif args.mode == "tui":
        print("Starting TUI chat interface...")
        print("")
        from src.gob.interfaces.tui_chat import run_tui_chat

        run_tui_chat(orchestrator, memory)

        # Suggest Discord setup after successful TUI session
        print("")
        print("═" * 50)
        print("Session complete!")
        print("═" * 50)
        print("")

        # Check if Discord is configured
        discord_config = config.get("discord", {})
        discord_token = discord_config.get("token", "")

        if not discord_token or discord_token.startswith("${"):
            print("💡 Want me always available in Discord?")
            print("")
            print("  1. Get a Discord token from Discord Developer Portal")
            print("  2. Add it to .env: DISCORD_BOT_TOKEN=your_token")
            print("  3. Run: python -m gob.main --mode discord")
            print("")
            print("")

    elif args.mode == "discord":
        # Check if Discord is configured, if not, offer setup
        discord_config = config.get("discord", {})
        discord_token = discord_config.get("token", "")

        if not discord_token or discord_token.startswith("${"):
            print("\n🎮 Discord bot token is missing.")
            print("Starting setup wizard...\n")
            new_token = run_discord_wizard()
            if new_token:
                with open(".env", "a") as f:
                    f.write(f"\nDISCORD_BOT_TOKEN={new_token}\n")
                os.environ["DISCORD_BOT_TOKEN"] = new_token
                discord_config["token"] = new_token
            else:
                print("\n⚠️  Skipping Discord setup. Exiting.")
                return

        print("Starting Discord bot...")
        print("")
        from src.gob.interfaces.discord_bot import run_discord_bot

        run_discord_bot(orchestrator, memory, discord_config)


if __name__ == "__main__":
    main()
