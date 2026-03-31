"""
GOB Version Information

This module contains version information for the GOB project.
Follows semantic versioning (MAJOR.MINOR.PATCH)

Version 0.2.0 - 2026-03-31
"""

__version__ = "0.2.0"
__version_info__ = (0, 2, 0)

# Version history
VERSION_HISTORY = {
    "0.2.0": {
        "date": "2026-03-31",
        "description": "Enhanced version display and automatic version bumping",
        "features": ["Enhanced version display", "Automatic version bumping", "Git hooks integration"]
    },
    "0.1.0": {
        "date": "2026-03-31",
        "description": "Initial release with rate limiting protection",
        "features": ["Rate limiting protection", "Automatic API key setup", "Professional versioning"]
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
