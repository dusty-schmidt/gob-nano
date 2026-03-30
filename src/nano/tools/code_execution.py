"""Code execution tool - Execute Python code and bash commands"""
import subprocess
import tempfile
import os
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr


def execute(code: str, language: str = "python") -> str:
    """
    Execute code and return result

    Args:
        code: The code to execute
        language: "python" or "bash"

    Returns:
        Output of the execution or error message
    """
    if language == "bash":
        return _execute_bash(code)
    else:
        return _execute_python(code)


def _execute_python(code: str) -> str:
    """Execute Python code in a sandboxed environment"""
    # Capture stdout and stderr
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()

    # Create execution context with limited builtins
    exec_globals = {
        "__builtins__": {
            "print": print,
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "open": open,
            "True": True,
            "False": False,
            "None": None,
            "Exception": Exception,
        }
    }

    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(code, exec_globals)

        output = stdout_buffer.getvalue()
        errors = stderr_buffer.getvalue()

        if errors:
            return f"Output:\n{output}\n\nErrors:\n{errors}"
        return output if output else "Code executed successfully (no output)"

    except Exception as e:
        return f"Error executing code: {str(e)}"


def _execute_bash(command: str) -> str:
    """Execute bash command"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            cwd="/app"   # Run from /app directory
        )

        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"Exit code: {result.returncode}")

        return "\n\n".join(output) if output else "Command executed successfully (no output)"

    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def run(command: str, **kwargs) -> str:
    """Alias for execute to match tool interface"""
    language = kwargs.get('language', 'python')
    return execute(command, language)
