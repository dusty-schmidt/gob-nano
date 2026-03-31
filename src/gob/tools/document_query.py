"""Document query tool - Read and query documents"""
import os
from typing import Dict, Any, List


def read_document(path: str) -> Dict[str, Any]:
    """
    Read document content from file
    
    Args:
        path: Path to the document file
        
    Returns:
        Dict containing the document content and success status
        
    Example:
        >>> result = read_document("/path/to/file.txt")
        >>> if result["success"]:
        ...     content = result["content"]
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


def query(path: str, questions: List[str]) -> Dict[str, Any]:
    """
    Query document content
    
    Args:
        path: Path to the document file
        questions: List of questions to search for in the document
        
    Returns:
        Dict containing answers to questions and success status
        
    Example:
        >>> result = query("/path/to/file.txt", ["what is python?"])
        >>> if result["success"]:
        ...     for question, answer in result["answers"].items():
        ...         print(f"{question}: {answer}")
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple keyword matching for now (can be enhanced with NLP)
        answers = {}
        for q in questions:
            if q.lower() in content.lower():
                answers[q] = "Found relevant information in document."
            else:
                answers[q] = "No relevant information found."
        
        return {"answers": answers, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}