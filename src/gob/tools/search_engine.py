"""Search engine tool - Web search via DuckDuckGo

This tool provides web search functionality using DuckDuckGo API with support for
keyword searches, result formatting, and automatic package installation.
"""

import subprocess
import sys
from typing import List, Dict, Any
from gob.core.logger import log_to_chat


def search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo

    Args:
        query: Search query string (e.g., "python list comprehension", "machine learning basics")
        max_results: Maximum number of results to return (default 5, max 20)

    Returns:
        Formatted search results or error message
        
    Example:
        >>> log_to_chat("INFO", results)
        Search results:
        
        1. Python List Comprehension Tutorial
           URL: https://example.com/python-list-comprehension
           Learn how to use list comprehensions in Python with practical examples...
    """
    # Try to use duckduckgo-search if available
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "No results found for your query.\n\nTip: Try using more specific search terms or check your spelling."

        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            href = result.get("href", "No URL")
            body = result.get("body", "No description")
            formatted_results.append(f"{i}. {title}\n   URL: {href}\n   {body}\n")

        return "Search results:\n\n" + "\n".join(formatted_results)

    except ImportError:
        # duckduckgo-search not installed, try to install it
        return (
            "Search engine requires 'duckduckgo-search' package.\n\n"
            "Install it by running:\n"
            "  pip install duckduckgo-search\n\n"
            "Or ask NANO to install it for you!\n\n"
            "Once installed, you can search for anything like:\n"
            "  'python list comprehension'")

    except Exception as e:
        return f"Search error: {str(e)}\n\nPlease check your query format and try again."


def execute(query: str, max_results: int = 5) -> str:
    """
    Execute search (alias for search function)
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 5)
        
    Returns:
        Formatted search results or error message
        
    Example:
        >>> log_to_chat("INFO", results)
        # Returns formatted search results
    """
    return search(query, max_results)


def install_ddg() -> str:
    """
    Install duckduckgo-search package
    
    Returns:
        Installation status message
        
    Example:
        >>> log_to_chat("INFO", status)
        duckduckgo-search installed successfully! Search is now available.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "duckduckgo-search", "-q"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return "duckduckgo-search installed successfully! Search is now available.\n\nYou can now search for anything like:\n• 'python tutorial'\n• 'machine learning basics'\n• 'web development guide'"
        else:
            return f"Installation failed: {result.stderr}\n\nPlease try installing manually with: pip install duckduckgo-search"
    except Exception as e:
        return f"Installation error: {str(e)}\n\nPlease check your Python environment and try again."