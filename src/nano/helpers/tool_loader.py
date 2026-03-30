"""Tool loader for NANO"""
from importlib import import_module

def load_tool(tool_name: str):
    """Import and return a tool module from nano.tools by name"""
    # Try src.nano.tools first (development mode)
    module_path = f"src.nano.tools.{tool_name}"
    try:
        return import_module(module_path)
    except ModuleNotFoundError:
        # Fall back to nano.tools (installed package mode)
        module_path = f"nano.tools.{tool_name}"
        try:
            return import_module(module_path)
        except ModuleNotFoundError as e:
            raise ImportError(f"Tool '{tool_name}' not found") from e
