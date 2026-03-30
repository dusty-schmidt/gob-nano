"""Search engine tool - Web search via DuckDuckGo"""

import subprocess
import sys


def search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 5)

    Returns:
        Formatted search results or error message
    """
    # Try to use duckduckgo-search if available
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "No results found."

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
            "Or ask NANO to install it for you!"
        )

    except Exception as e:
        return f"Search error: {str(e)}"


def execute(query: str, max_results: int = 5) -> str:
    """Execute search (alias for search function)"""
    return search(query, max_results)


def install_ddg() -> str:
    """Install duckduckgo-search package"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "duckduckgo-search", "-q"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return "duckduckgo-search installed successfully! Search is now available."
        else:
            return f"Installation failed: {result.stderr}"
    except Exception as e:
        return f"Installation error: {str(e)}"
