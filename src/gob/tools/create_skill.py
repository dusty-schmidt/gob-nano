import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def create_skill(skill_name: str, description: str = ""):
    """
    Create a new skill directory and SKILL.md file.
    
    Args:
        skill_name: Name of the skill (will be used as directory name)
        description: Brief description of the skill
    
    Returns:
        dict: Success status and path to created skill
    """
    try:
        # Determine skill directory path
        skills_dir = Path(__file__).parent.parent / "plugins" / skill_name
        skills_dir.mkdir(parents=True, exist_ok=True)
        
        # Create SKILL.md content
        skill_content = f"""# {skill_name}

## Description
{description or 'A custom skill for GOB agent.'}

## Usage

## Examples

"""
        
        # Write SKILL.md
        skill_file = skills_dir / "SKILL.md"
        with open(skill_file, 'w') as f:
            f.write(skill_content)
        
        logger.info(f"Created skill: {skill_name} at {skill_file}")
        
        return {
            "success": True,
            "path": str(skill_file),
            "message": f"Skill '{skill_name}' created successfully"
        }
    
    except PermissionError as e:
        logger.error(f"Permission denied when creating skill: {e}")
        return {
            "success": False,
            "error": f"Permission denied: {e}. Check directory permissions."
        }
    except OSError as e:
        logger.error(f"OS error when creating skill: {e}")
        return {
            "success": False,
            "error": f"File system error: {e}. Check disk space or path validity."
        }
    except Exception as e:
        logger.error(f"Unexpected error creating skill: {e}")
        return {
            "success": False,
            "error": f"An unexpected error occurred: {e}"
        }
