"""
GOB Version Information

This module contains version information for the GOB project.
Follows semantic versioning (MAJOR.MINOR.PATCH)

Version 0.1.0 - Initial release with rate limiting protection
- Enhanced LLM client with comprehensive error handling
- Automatic API key detection and prompting
- Rate limiting protection with exponential backoff
- Fallback model support
"""

__version__ = "0.1.0"
__version_info__ = (0, 1, 0)

# Version history
VERSION_HISTORY = {
    "0.1.0": {
        "date": "2026-03-31",
        "description": "Initial release with rate limiting protection",
        "features": [
            "Enhanced LLM client with comprehensive error handling",
            "Automatic API key detection and prompting",
            "Rate limiting protection with exponential backoff",
            "Fallback model support",
            "Enhanced gob.sh script with backup/restore capabilities"
        ]
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
