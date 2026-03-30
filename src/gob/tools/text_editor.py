"""Text editor tool - Read/write/edit files"""


def read(path, line_from=1, line_to=None):
    """Read file content"""
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


def write(path, content):
    """Write content to file"""
    try:
        with open(path, "w") as f:
            f.write(content)
        return {"path": path, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


def patch(path, edits):
    """Patch file with edits"""
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        
        # Sort edits by line number descending to avoid index shifting
        # edits = sorted(edits, key=lambda x: x.get('from', 0), reverse=True)
        # Wait, if we process from bottom up, we need to handle inserts correctly.
        # If we process from top down, indices shift.
        # Best approach: Read all lines, build new lines list.
        
        # We will create a map of line_number -> content for replacement/insertion
        # Since edits might overlap or be adjacent, we need to be careful.
        
        # Let's process edits in order, but adjust indices as we go.
        # Actually, it's safer to parse all edits, determine which lines are affected,
        # and construct the new file content.
        
        # Strategy: 
        # 1. Group edits by target line number.
        # 2. Iterate through original lines and apply changes.
        
        # However, `edits` format is: [{"from": N, "to": M, "content": "..."}] or {"from": N, "content": "..."}
        
        # Let's implement a robust line-based patcher.
        
        new_lines = []
        current_line_idx = 0 # 0-based index in original lines
        edit_idx = 0
        
        # Sort edits by 'from' ascending
        edits.sort(key=lambda x: x.get('from', 0))
        
        for edit in edits:
            start = edit.get('from', 0) - 1 # Convert 1-based to 0-based
            end = edit.get('to', edit.get('from', 0)) - 1
            content = edit.get('content', '')
            
            # Handle invalid indices
            if start < 0: start = 0
            
            # Copy lines from current_line_idx up to start
            while current_line_idx < start and current_line_idx < len(lines):
                new_lines.append(lines[current_line_idx])
                current_line_idx += 1
            
            # Apply the edit content
            if 'content' in edit:
                new_lines.append(content)
            
            # Skip the lines being replaced (if 'to' is specified)
            # Note: 'from' to 'to' inclusive means we skip (end - start + 1) lines
            # If only 'from' is present, we insert before that line (handled above) or replace that single line?
            # Standard 'patch' behavior: {from: N, to: M} replaces lines N to M.
            # If 'to' is missing, it implies replacing just line N? Or inserting?
            # The orchestrator comment says: {from:2 to:2 content:"x\n"} replace line
            # {from:2 content:"x\n"} insert before
            
            if 'to' in edit:
                # Skip the lines in the range
                lines_to_skip = (end - start) + 1
                current_line_idx += lines_to_skip
            # If 'to' is missing, we don't skip any lines (insertion behavior)
            
        # Copy remaining lines
        while current_line_idx < len(lines):
            new_lines.append(lines[current_line_idx])
            current_line_idx += 1
            
        with open(path, "w") as f:
            f.writelines(new_lines)
            
        return {"path": path, "edits": edits, "success": True}
    
    except Exception as e:
        return {"error": str(e), "success": False}
