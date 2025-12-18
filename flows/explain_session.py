"""
Explain why a session matches user interests.
"""

from promptflow import tool
from typing import Dict, Any


@tool
def explain_session(session_title: str, interests: str) -> Dict[str, Any]:
    """
    Explain why a specific session matches interests.
    
    Args:
        session_title: Title of session to explain
        interests: User interests
        
    Returns:
        dict with explanation
    """
    try:
        # Import EventKit core
        from core import explain
        
        if not session_title:
            return {
                "success": False,
                "error": "No session title provided",
                "explanation": ""
            }
        
        # Parse interests
        interests_list = [i.strip() for i in interests.split(",")] if interests else []
        
        # Get explanation
        explanation_text = explain(
            session_title=session_title,
            interests=interests_list,
            manifest_path="agent.json"
        )
        
        return {
            "success": True,
            "explanation": explanation_text,
            "session": session_title
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "explanation": ""
        }
