"""Document query tool - Read and query documents"""
import os

def read_document(path):
    """Read document content from file"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

def query(path, questions):
    """Query document content"""
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
