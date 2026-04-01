"""Code execution tool - executes Python code and bash commands inside the G.O.B. sandbox."""

import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

_LOG_DIR = Path(".gob/logs")
_LOG_DIR.mkdir(parents=True, exist_ok=True)


def _write_sandbox_log(stdout: str, stderr: str, exit_code: int) -> str:
    """Persist execution output to a timestamped JSON log file.

    Args:
        stdout: Captured standard output from the sandbox.
        stderr: Captured standard error from the sandbox.
        exit_code: Exit code from the sandbox process.

    Returns:
        The absolute path to the written log file.
    """
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    log_path = _LOG_DIR / f"exec_{ts}.json"
    entry = {"timestamp": ts, "exit_code": exit_code, "stdout": stdout, "stderr": stderr}
    log_path.write_text(json.dumps(entry, indent=2))
    return str(log_path)


def execute(code: str, language: str = "python") -> dict:
    """
    Execute code and return structured result with captured logs.

    Args:
        code: The code to execute
        language: "python" or "bash"

    Returns:
        Dictionary with keys:
            - stdout: Captured standard output
            - stderr: Captured standard error
            - exit_code: Process exit code
            - success: True if exit code is 0
            - log_path: Path to the sandbox log file
    """
    if language == "bash":
        return _execute_bash(code)
    else:
        return _execute_python(code)


# ---------------------------------------------------------------------------
# Sandbox-aware execution (uses Docker when available, falls back to local)
# ---------------------------------------------------------------------------

def _sandbox_enabled() -> bool:
    """Return True if Docker is available and sandbox is configured."""
    return os.getenv("GOB_NO_SANDBOX") != "1" and os.path.exists("/usr/bin/docker")


def _execute_in_sandbox(code: str, language: str = "python") -> dict:
    """Run code inside the sandbox container using docker-compose."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_parts = script_dir.split("/")
    # Walk up from tools -> gob -> src -> project root
    idx = -1
    for i, part in enumerate(project_root_parts):
        if part == "src" and i > 0 and project_root_parts[i-1] == "gob":
            idx = i - 2
            break
    project_root = "/".join(project_root_parts[:idx]) if idx >= 0 else script_dir
    sandbox_dir = os.path.join(project_root, "docker")

    if not os.path.exists(os.path.join(sandbox_dir, "docker-compose.sandbox.yml")):
        # Fallback: run locally if sandbox configuration is missing
        return _execute_python_local(code)

    cmd = ["docker", "compose", "-f", "docker-compose.sandbox.yml", "run", "--rm", "sandbox"]
    if language == "python":
        cmd += ["python", "-c", code]
    else:
        cmd += ["sh", "-c", code]

    try:
        proc = subprocess.run(
            cmd,
            cwd=sandbox_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        result = {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
            "success": proc.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        result = {"stdout": "", "stderr": "Execution timed out after 60s", "exit_code": 124, "success": False}
    except Exception as e:
        result = {"stdout": "", "stderr": str(e), "exit_code": 1, "success": False}

    result["log_path"] = _write_sandbox_log(result["stdout"], result["stderr"], result["exit_code"])
    return result


def _execute_python(code: str) -> dict:
    """Execute Python code, preferring sandbox when available."""
    if _sandbox_enabled():
        return _execute_in_sandbox(code, "python")
    return _execute_python_local(code)


def _execute_python_local(code: str) -> dict:
    """Execute Python code locally (fallback when sandbox is disabled)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        proc = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        result = {"stdout": proc.stdout, "stderr": proc.stderr, "exit_code": proc.returncode, "success": proc.returncode == 0}
    except subprocess.TimeoutExpired:
        result = {"stdout": "", "stderr": "Timed out after 30s", "exit_code": 124, "success": False}
    except Exception as e:
        result = {"stdout": "", "stderr": str(e), "exit_code": 1, "success": False}
    finally:
        os.unlink(tmp_path)

    result["log_path"] = _write_sandbox_log(result["stdout"], result["stderr"], result["exit_code"])
    return result


def _execute_bash(command: str) -> dict:
    """Execute bash command, preferring sandbox when available."""
    if _sandbox_enabled():
        return _execute_in_sandbox(command, "bash")
    return _execute_bash_local(command)


def _execute_bash_local(command: str) -> dict:
    """Execute a bash command locally (fallback)."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": result.returncode == 0,
            "log_path": _write_sandbox_log(result.stdout, result.stderr, result.returncode),
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Timed out after 30s", "exit_code": 124, "success": False}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": 1, "success": False}


def run(command: str, **kwargs) -> dict:
    """Alias for execute to match tool interface."""
    language = kwargs.get("language", "python")
    return execute(command, language)
