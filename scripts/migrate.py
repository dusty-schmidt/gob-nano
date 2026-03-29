"""NANO Migration Script - Data and config migration"""
from pathlib import Path
from .utils import get_project_root, get_data_dir, get_config_dir, print_success, print_info

def migrate_memory():
    print_info("Migrating memory files...\n")
    old_memory = get_project_root() / "helpers" / "memory" / "memory.jsonl"
    new_memory = get_data_dir() / "memory.jsonl"
    
    if old_memory.exists():
        get_data_dir().mkdir(parents=True, exist_ok=True)
        with open(old_memory, 'r') as src:
            with open(new_memory, 'w') as dst:
                dst.write(src.read())
        print_success(f"Migrated memory to {new_memory}")
    else:
        print_info("No old memory files to migrate")

def migrate_config():
    print_info("Migrating config files...\n")
    old_config = get_project_root() / "config.yaml"
    new_config = get_config_dir() / "config.yaml"
    
    if old_config.exists():
        get_config_dir().mkdir(parents=True, exist_ok=True)
        with open(old_config, 'r') as src:
            with open(new_config, 'w') as dst:
                dst.write(src.read())
        print_success(f"Migrated config to {new_config}")
    else:
        print_info("No old config files to migrate")

def run_migration():
    print_info("Starting migration...\n")
    migrate_memory()
    migrate_config()
    print_success("Migration complete!")

if __name__ == "__main__":
    run_migration()
