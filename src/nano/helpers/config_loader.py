"""Configuration loader for NANO"""
import yaml
from pathlib import Path

def load_config():
    """Load the main config.yaml file from the config directory"""
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
