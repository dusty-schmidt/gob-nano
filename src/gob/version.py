"""
GOB Version Information

This module contains version information for the GOB project.
Follows semantic versioning (MAJOR.MINOR.PATCH)

Version 0.2.2 - 2026-03-31
"""

__version__ = "0.2.2"
__version_info__ = (0, 2, 2)

# Version history
VERSION_HISTORY = {
    "0.2.2": {
        "date": "2026-03-31",
        "description": "Auto-bumped to 0.2.2",
        "features": ["Automatic version bump"]
    }
}

def get_version():
    """Get the current version string"""
    return __version__

def get_version_info():
    """Get the version as a tuple"""
    return __version_info__

def get_version_history():
    """Get the complete version history"""
    return VERSION_HISTORY
