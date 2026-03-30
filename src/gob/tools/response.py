"""Response tool - Send response to user"""


def execute(query, output_format="text"):
    """Return response to the user query"""
    return {"response": f"Response to: {query}", "success": True}
