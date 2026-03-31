"""Text editor tool - Read/write/edit files

This tool provides functionality to read, write, and edit text files with support for
line-based operations and patch-based modifications.
"""

from typing import Dict, Any, List, Optional


def read(path: str, line_from: int = 1, line_to: Optional[int] = None) -> Dict[str, Any]:
    """
    Read file content with optional line range specification
    
    Args:
        path: Path to the file to read
        line_from: Starting line number (1-based, default: 1)
        line_to: Ending line number (1-based, default: None = read to end)
        
    Returns:
        Dict containing the file content and success status
        
    Example:
        >>> result = read("/path/to/file.txt", line_from=1, line_to=10)
        >>> if result["success"]:
        ...     content = result["content"]
        ...     print(f"Read {len(content.splitlines())} lines")
    """
    try:
        with open(path, "r") as f:
            lines = f.readlines()
            if line_to is None:
                line_to = len(lines)
            content = "".join(lines[line_from-1:line_to])
            return {"content": content, "success": True}
    except FileNotFoundError:
        return {"error": f"File not found: {path}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def write(path: str, content: str) -> Dict[str, Any]:
    """
    Write content to file
    
    Args:
        path: Path to the file to write
        content: Text content to write to the file
        
    Returns:
        Dict containing the file path and success status
        
    Example:
        >>> result = write("/path/to/file.txt", "Hello, World!")
        >>> if result["success"]:
        ...     print(f"File written to: {result['path']}")
    """
    try:
        with open(path, "w") as f:
            f.write(content)
        return {"path": path, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


def patch(path: str, edits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Patch file with line-based edits
    
    Args:
        path: Path to the file to patch
        edits: List of edit dictionaries with 'from', 'to', and 'content' keys
        
    Returns:
        Dict containing success status and any error messages
        
    Example:
        >>> edits = [{"from": 5, "to": 5, "content": "new line 5\\n"}]
        >>> result = patch("/path/to/file.txt", edits)
    """
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        
        # Apply edits in reverse order to maintain line numbers
        sorted_edits = sorted(edits, key=lambda x: x.get('from', 0), reverse=True)
        
        for edit in sorted_edits:
            from_line = edit.get('from', 1) - 1  # Convert to 0-indexed
            to_line = edit.get('to', edit.get('from', 1))  # Default to single line if 'to' not specified
            content = edit.get('content', '')
            
            # Ensure we don't go out of bounds
            if from_line < 0:
                from_line = 0
            if to_line > len(lines):
                to_line = len(lines)
            
            # Replace the specified range with new content
            lines[from_line:to_line] = [content]
        
        with open(path, "w") as f:
            f.writelines(lines)
            
        return {"success": True}
    except Exception as e:
        return {"error": str(e), "success": False}
