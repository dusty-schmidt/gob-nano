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
        Dict containing file content and metadata
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Handle line range
        if line_from < 1:
            line_from = 1
        if line_to is None or line_to > len(lines):
            line_to = len(lines)
        
        content_lines = lines[line_from-1:line_to]
        content = ''.join(content_lines)
        
        return {
            'content': content,
            'path': path,
            'line_from': line_from,
            'line_to': line_to,
            'total_lines': len(lines)
        }
    except FileNotFoundError:
        return {'error': f'File not found: {path}'}
    except Exception as e:
        return {'error': f'Error reading file: {str(e)}'}

def write(path: str, content: str) -> Dict[str, Any]:
    """
    Write content to file
    
    Args:
        path: Path to the file to write
        content: Text content to write to the file
        
    Returns:
        Dict containing the file path and success status
    """
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {
            'path': path,
            'success': True,
            'message': f'File written successfully: {path}'
        }
    except Exception as e:
        return {
            'error': f'Error writing file: {str(e)}'
        }

        
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
    """Patch file with edits"""