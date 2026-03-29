"""Configuration loader for NANO"""
import os
import re
import yaml
from pathlib import Path

def resolve_env_vars(value):
    """Resolve ${VAR_NAME} environment variable placeholders in a string."""
    if not isinstance(value, str):
        return value
    pattern = r'\$\{([^}]+)\}'
    matches = re.findall(pattern, value)
    for var_name in matches:
        env_value = os.environ.get(var_name, '')
        value = value.replace(f'${{{var_name}}}', env_value)
    return value

def resolve_config_env_vars(config):
    """Recursively resolve environment variables in config dict values."""
    if isinstance(config, dict):
        return {k: resolve_config_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [resolve_config_env_vars(item) for item in config]
    else:
        return resolve_env_vars(config)

def load_config():
    """Load the main config.yaml file from the config directory"""
    # Navigate from src/nano/helpers/ up to project root
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "config.yaml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # Resolve environment variables
    return resolve_config_env_vars(config)
