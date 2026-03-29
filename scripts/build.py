"""NANO Build Script - Build and run Docker image"""
import subprocess
import sys
from .utils import get_project_root, print_success, print_error, print_info

def build_docker():
    print_info("Building NANO Docker image...\n")
    project_root = get_project_root()
    docker_dir = project_root / "docker"
    cmd = ["docker", "build", "-t", "nano-agent:latest", "-f", str(docker_dir / "Dockerfile"), str(project_root)]
    try:
        subprocess.run(cmd, check=True, cwd=str(project_root))
        print_success("Docker image built!")
        print_info("Run: python -m scripts.build run")
    except subprocess.CalledProcessError as e:
        print_error(f"Build failed: {e}")
    except FileNotFoundError:
        print_error("Docker not found")

def run_docker():
    print_info("Starting NANO Docker container...\n")
    project_root = get_project_root()
    docker_dir = project_root / "docker"
    cmd = ["docker-compose", "-f", str(docker_dir / "docker-compose.yml"), "up", "-d"]
    try:
        subprocess.run(cmd, check=True, cwd=str(project_root))
        print_success("Docker container started!")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed: {e}")
    except FileNotFoundError:
        print_error("docker-compose not found")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run_docker()
    else:
        build_docker()
