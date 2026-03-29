"""NANO Setup Wizard - Interactive configuration"""
import sys
from pathlib import Path
from utils import get_config_dir, get_data_dir, save_yaml, print_success, print_error, print_info

def run_setup():
    print("\n🚀 NANO Agent Setup Wizard\n")
    
    config_dir = get_config_dir()
    config_file = config_dir / "config.yaml"
    
    print_info("Welcome to NANO setup!")
    print_info(f"Config will be saved to: {config_file}\n")
    
    # Get Discord token
    discord_token = input("🤖 Enter your Discord bot token: ").strip()
    if not discord_token:
        print_error("Discord token is required")
    
    # ---------------------------------------------------------------
    # LLM provider configuration – support OpenRouter, Groq, and Ollama Cloud
    # ---------------------------------------------------------------
    # Choose provider
    providers = {
        "1": "openrouter",
        "2": "groq",
        "3": "ollama"
    }
    print_info("Select LLM provider:")
    print("  1) OpenRouter (default)")
    print("  2) Groq")
    print("  3) Ollama Cloud")
    provider_choice = input("Enter number [1-3]: ").strip() or "1"
    provider = providers.get(provider_choice, "openrouter")

    # Set defaults per provider
    if provider == "openrouter":
        endpoint = "https://openrouter.ai/api/v1"
        default_model = "openai/gpt-4o-mini"
        key_name = "OpenRouter API key"
    elif provider == "groq":
        endpoint = "https://api.groq.com/openai/v1"
        default_model = "llama3-8b-8192"
        key_name = "Groq API key"
    else:  # ollama
        endpoint = "https://api.ollama.com/v1"
        default_model = "mistral"
        key_name = "Ollama Cloud API key"

    # Allow user to override the default model if they wish
    model = input(f"Enter model to use (default: {default_model}): ").strip() or default_model

    # Get API key for the selected provider
    api_key = input(f"🔑 Enter your {key_name}: ").strip()
    if not api_key:
        print_error(f"{key_name} is required")

    # Build the LLM config block
    llm_config = {
        "provider": provider,
        "endpoint": endpoint,
        "model": model,
        "api_key": api_key,
        "max_tokens": 4096,
        "temperature": 0.7
    }

    # ---------------------------------------------------------------
    # Assemble full configuration dictionary
    # ---------------------------------------------------------------
    config = {
        "agent": {"name": agent_name, "profile": "default"},
        "discord": {"token": discord_token, "prefix": "!"},
        "llm": llm_config,
        "tools": {
            "enabled": ["response", "search_engine", "code_execution", "text_editor", "document_query"],
            "disabled": []
        }
    }
    
    # Ensure directories exist
    config_dir.mkdir(parents=True, exist_ok=True)
    get_data_dir().mkdir(parents=True, exist_ok=True)
    
    # Save config
    save_yaml(config_file, config)
    print_success(f"Configuration saved to {config_file}")
    
    # Create memory file
    memory_file = get_data_dir() / "memory.jsonl"
    memory_file.touch(exist_ok=True)
    print_success(f"Memory file created at {memory_file}")
    
    print_success("Setup complete!")
    print_info("Run: python -m nano.main")

if __name__ == "__main__":
    run_setup()
