"""Agent loader for NANO"""

from pathlib import Path

import yaml


def load_agent(profile: str = "default"):
    """Load an agent configuration YAML from config/agents"""
    # Navigate from src/gob/helpers/ up to project root
    agents_dir = Path(__file__).parent.parent.parent.parent / "config" / "agents"
    agent_file = agents_dir / f"{profile}.yaml"

    if not agent_file.is_file():
        raise FileNotFoundError(f"Agent profile not found: {agent_file}")

    with open(agent_file, "r", encoding="utf-8") as f:
        agent_config = yaml.safe_load(f)

    # Normalize agent config structure
    # Merge model settings from agent config into a standardized format
    if "model" in agent_config and isinstance(agent_config["model"], dict):
        model_config = agent_config["model"]
        # Ensure model name is accessible
        if "name" in model_config:
            agent_config["model_name"] = model_config["name"]
        if "provider" in model_config:
            agent_config["model_provider"] = model_config["provider"]

    # Set agent name if not present
    if "name" not in agent_config:
        agent_config["name"] = profile

    return agent_config
