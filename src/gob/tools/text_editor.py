"""Text editor tool - Read/write/edit files"""

def read(path, line_from=1, line_to=None):
    """Read file content"""
    try:
        with open(path, 'r') as f:
            return {"content": f.read(), "success": True}
    except FileNotFoundError:
        return {"error": f"File not found: {path}", "success": False}

def write(path, content):
    """Write content to file"""
    try:
        with open(path, 'w') as f:
            f.write(content)
        return {"path": path, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

def patch(path, edits):
    """Patch file with edits"""
    return {"path": path, "edits": edits, "success": True}
