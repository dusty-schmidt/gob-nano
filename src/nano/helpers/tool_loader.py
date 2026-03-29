"""Tool loader for NANO"""
from importlib import import_module

def load_tool(tool_name: str):
    """Import and return a tool module from nano.tools by name"""
    module_path = f"nano.tools.{tool_name}"
    try:
        return import_module(module_path)
    except ModuleNotFoundError as e:
        raise ImportError(f"Tool '{tool_name}' not found in {module_path}") from e
