"""NANO Lint Script - Code quality checks"""
import subprocess
from .utils import get_project_root, print_success, print_info

def run_linting():
    print_info("Running code quality checks...\n")
    project_root = get_project_root()
    src_dir = project_root / "src"
    
    tools = [
        ("isort", ["isort", str(src_dir)]),
        ("black", ["black", str(src_dir)]),
        ("flake8", ["flake8", str(src_dir)]),
    ]
    
    for tool_name, cmd in tools:
        print_info(f"Running {tool_name}...")
        try:
            subprocess.run(cmd, check=False)
        except FileNotFoundError:
            print(f"⚠️  {tool_name} not found")
    
    print_success("Code quality checks complete!")

if __name__ == "__main__":
    run_linting()
