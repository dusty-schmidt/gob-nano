"""Common utilities for scripts"""
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

def get_project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent

def get_config_dir():
    """Get config directory"""
    return get_project_root() / "config"

def get_data_dir():
    """Get data directory"""
    return get_project_root() / "src" / "nano" / "data"

def load_yaml(path):
    """Load YAML file"""
    if not yaml:
        raise ImportError("PyYAML not installed")
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def save_yaml(path, data):
    """Save YAML file"""
    if not yaml:
        raise ImportError("PyYAML not installed")
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")
    sys.exit(1)

def print_info(msg):
    print(f"ℹ️  {msg}")
