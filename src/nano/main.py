"""NANO Agent - Main entry point"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from src.nano.helpers.config_loader import load_config
from src.nano.helpers.agent_loader import load_agent
from src.nano.helpers.memory.memory import MemoryManager


def main():
    """Initialize and run the NANO agent"""
    print("🚀 Starting NANO Agent...")
    
    # Load configuration
    try:
        config = load_config()
        print(f"✅ Config loaded")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        sys.exit(1)
    
    # Load agent profile
    try:
        agent_profile = config.get('agent', {}).get('profile', 'default')
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
    
    # Verify LLM configuration
    try:
        llm_config = config.get('llm', {})
        provider = llm_config.get('provider')
        model = llm_config.get('model')
        api_key = llm_config.get('api_key')
        
        if not api_key or api_key.startswith('your_'):
            print("⚠️  LLM API key not configured. Please set it in .env")
            print(f"   Provider: {provider}")
            print(f"   Model: {model}")
            sys.exit(1)
        
        print(f"✅ LLM configured: {provider}/{model}")
    except Exception as e:
        print(f"❌ Failed to verify LLM config: {e}")
        sys.exit(1)
    
    # List available tools
    try:
        from src.nano.helpers.tool_loader import load_tool
        enabled_tools = config.get('tools', {}).get('enabled', [])
        print(f"✅ Enabled tools: {', '.join(enabled_tools)}")
        for tool_name in enabled_tools:
            try:
                load_tool(tool_name)
            except ImportError:
                print(f"   ⚠️  Tool not found: {tool_name}")
    except Exception as e:
        print(f"❌ Failed to load tools: {e}")
    
    print("")
    print("═" * 50)
    print("Agent initialized successfully!")
    print("═" * 50)
    print("")
    print("Configuration:")
    print(f"  Agent: {agent.get('name', 'Unknown')}")
    print(f"  Model: {llm_config.get('model')}")
    print(f"  Memory file: {memory_file}")
    print("")
    print("Ready for tasks. This is a placeholder entry point.")
    print("For Discord bot integration, implement bot handlers here.")
    print("For interactive mode, implement REPL here.")
    print("")


if __name__ == "__main__":
    main()
