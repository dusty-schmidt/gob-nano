"""Tool loader for GOB"""

from importlib import import_module
import logging

logger = logging.getLogger(__name__)


def load_tool(tool_name: str):
    """Import and return a tool module from gob.tools by name"""
    module_path = f"gob.tools.{tool_name}"
    try:
        return import_module(module_path)
    except ModuleNotFoundError as e:
        logger.error(f"Tool '{tool_name}' not found at '{module_path}': {e}")
        raise ImportError(f"Tool '{tool_name}' not found") from e
