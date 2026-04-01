"""autopsy.py — Failure analysis module.

When code execution inside the sandbox fails, this module parses the
captured stdout, stderr, and exit code to produce a human-readable
summary that the agent can use for self-correction.
"""

from typing import Final

_OOM_KILL_INDICATORS: Final = (
    "killed", "oom", "out of memory", "memory exhausted"
)
_TIMEOUT_INDICATORS: Final = (
    "timeout", "timed out", "deadline exceeded", "killed"
)
_SYNTAX_INDICATORS: Final = (
    "syntaxerror", "indentationerror", "nameerror",
    "typeerror", "importerror"
)


def _classify(exit_code: int, stderr: str) -> str:
    """Return a high-level classification string."""
    stderr_lower = stderr.lower()
    if exit_code == 137 or any(k in stderr_lower
                              for k in _OOM_KILL_INDICATORS):
        return "OOM kill (exit 137)"
    if any(k in stderr_lower for k in _TIMEOUT_INDICATORS):
        return "Timeout / Execution killed"
    if any(k in stderr_lower for k in _SYNTAX_INDICATORS):
        return "Syntax or Import Error"
    if exit_code == 1:
        return "Runtime Error"
    if exit_code >= 128:
        return f"System Signal (exit {exit_code})"
    return f"Generic Error (exit {exit_code})"


def summarize_failure(exit_code: int, stdout: str, stderr: str) -> str:
    """Return a structured human-readable failure analysis.

    Args:
        exit_code: Container process exit code.
        stdout: Captured standard output.
        stderr: Captured standard error.

    Returns:
        Human-readable string with classification, patterns, and recovery suggestions.
    """
    classification = _classify(exit_code, stderr)
    last_traceback = ""
    lines = stderr.splitlines()
    for i, line in enumerate(lines):
        if "Traceback" in line:
            last_traceback = "\n".join(lines[i:])

    recovery = "- Retry with simpler code or reduce resource usage\n"
    if "Syntax" in classification or "Import" in classification:
        recovery = "- Fix syntax/imports before retrying\n  - Run `python -m py_compile <file>` locally\n"
    elif "OOM" in classification:
        recovery = "- Reduce memory usage; process fewer items or use generators\n"
    elif "Timeout" in classification:
        recovery = "- Optimize loop or add timeout; reduce input size\n"

    report = f"""--- Autopsy Report ---
Classification: {classification}
Exit Code: {exit_code}

Error Trace:
{last_traceback.strip() if last_traceback else stderr.strip()}

Suggested Recovery:
{recovery}"""
    return report.strip()
