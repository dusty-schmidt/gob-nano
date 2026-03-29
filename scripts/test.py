"""NANO Test Script - Run tests"""
import subprocess
from .utils import get_project_root, print_success, print_error, print_info

def run_tests():
    print_info("Running tests...\n")
    project_root = get_project_root()
    cmd = ["pytest", "-v", "--cov=src/nano", str(project_root / "tests")]
    try:
        subprocess.run(cmd, cwd=str(project_root), check=True)
        print_success("All tests passed!")
    except subprocess.CalledProcessError:
        print_error("Tests failed")
    except FileNotFoundError:
        print_error("pytest not found. Install: pip install pytest pytest-cov")

if __name__ == "__main__":
    run_tests()
