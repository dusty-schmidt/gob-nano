"""
Response tool - Send response to user

This tool provides functionality to format and send responses back to the user.
It supports different output formats and ensures consistent response structure.
"""

from typing import Dict, Any


def execute(query: str, output_format: str = "text") -> Dict[str, Any]:
    """
    Return response to the user query
    
    Args:
        query: The user's query or input string
        output_format: The desired output format (default: "text")
        
    Returns:
        Dict containing the response and success status
        
    Example:
        >>> execute("Hello, how are you?")
        {"response": "Response to: Hello, how are you?", "success": True}
    """
    return {"response": f"Response to: {query}", "success": True}