"""Tool loader for GOB with contract validation"""

import inspect
import logging
from importlib import import_module
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ToolValidationError(Exception):
    """Raised when tool contract validation fails."""
    pass


def validate_tool_contract(module) -> bool:
    """Validate that a tool module adheres to the expected interface.

    Args:
        module: The loaded Python module to validate.

    Returns:
        True if validation passes, False otherwise.

    Raises:
        Warning: Logged if contract mismatches are found.
    """
    if not hasattr(module, "execute") and not hasattr(module, "run"):
        logger.warning(
            f"[CONTRACT] Module {module.__name__} has no execute() or run() function"
        )
        return False

    entry_fn = getattr(module, "execute", None) or getattr(module, "run", None)
    sig = inspect.signature(entry_fn)

    # Check docstring exists
    doc = entry_fn.__doc__
    if not doc or not doc.strip():
        logger.warning(
            f"[CONTRACT] {module.__name__}:entry_fn missing docstring"
        )
        return False

    # Check that Args section exists in docstring
    if "Args:" not in doc and "args:" not in doc:
        logger.info(
            f"[CONTRACT] {module.__name__}:entry_fn docstring missing Args section"
        )

    # Validate parameters have **kwargs or match signature
    params = list(sig.parameters.values())
    has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)

    if not has_kwargs and len(params) < 1:
        logger.warning(
            f"[CONTRACT] {module.__name__}:entry_fn has no kwargs or positional args"
        )
        return False

    logger.info(f"[CONTRACT] ✅ {module.__name__} passes contract validation")
    return True


def load_tool(tool_name: str) -> Any:
    """Import and return a tool module from gob.tools by name, validating contracts.

    Args:
        tool_name: Name of the tool module (e.g., 'code_execution').

    Returns:
        The imported tool module.

    Raises:
        ImportError: If the tool module cannot be found.
    """
    module_path = f"gob.tools.{tool_name}"
    try:
        mod = import_module(module_path)
        validate_tool_contract(mod)
        return mod
    except ModuleNotFoundError as e:
        logger.error(f"Tool '{tool_name}' not found at '{module_path}': {e}")
        raise ImportError(f"Tool '{tool_name}' not found") from e
