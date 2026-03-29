"""Agent loader for NANO"""
from pathlib import Path
import yaml

def load_agent(profile: str = "default"):
    """Load an agent configuration YAML from config/agents"""
    # Navigate from src/nano/helpers/ up to project root
    agents_dir = Path(__file__).parent.parent.parent.parent / "config" / "agents"
    agent_file = agents_dir / f"{profile}.yaml"
    if not agent_file.is_file():
        raise FileNotFoundError(f"Agent profile not found: {agent_file}")
    with open(agent_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
