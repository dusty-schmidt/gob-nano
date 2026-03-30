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
    # Check if API key configured, if not run setup wizard
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("\n🚀 Welcome to Gob Agent!\n")
        print("Let's get you set up...\n")

        # Discord setup first (optional)
        discord_token = run_discord_wizard()
        if discord_token:
            with open(".env", "a") as f:
                f.write(f"\nDISCORD_BOT_TOKEN={discord_token}\n")
            os.environ["DISCORD_BOT_TOKEN"] = discord_token

        # API key (required)
        print()
        run_api_key_wizard()
        print("\n✅ Setup complete! Starting Gob...\n")

    # Parse command line arguments
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
        print(f"✅ Config loaded")
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
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        memory_file = data_dir / "memory.jsonl"
        memory = MemoryManager(memory_file)
        print(f"✅ Memory initialized: {memory_file}")
    except Exception as e:
        print(f"❌ Failed to initialize memory: {e}")
        sys.exit(1)

    # Initialize LLM client
    try:
        llm_config = config.get("llm", {})
        llm = LLMClient(llm_config)
        print(f"✅ LLM client initialized: {llm.model}")
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        sys.exit(1)

    # List available tools
    try:
        from src.gob.helpers.tool_loader import load_tool

        enabled_tools = config.get("tools", {}).get("enabled", [])
        print(f"✅ Enabled tools: {', '.join(enabled_tools)}")
        for tool_name in enabled_tools:
            try:
                load_tool(tool_name)
            except ImportError:
                print(f"   ⚠️  Tool not found: {tool_name}")
    except Exception as e:
        print(f"❌ Failed to load tools: {e}")

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
        print(f"   Tools: {', '.join(enabled_tools)}")
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
        print("Starting Discord bot...")
        print("")
        from src.gob.interfaces.discord_bot import run_discord_bot

        discord_config = config.get("discord", {})
        run_discord_bot(orchestrator, memory, discord_config)


if __name__ == "__main__":
    main()
