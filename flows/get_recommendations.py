"""
Get session recommendations based on interests.
"""

from promptflow import tool
from typing import Dict, Any, List


@tool
def get_recommendations(interests: str, user_interests: str = "") -> Dict[str, Any]:
    """
    Get session recommendations using EventKit core logic.
    
    Args:
        interests: Extracted interests from user message
        user_interests: User-provided interests parameter
        
    Returns:
        dict with recommendations
    """
    try:
        # Import EventKit core
        from core import recommend
        
        # Combine interests
        combined_interests = interests or user_interests
        if not combined_interests:
            return {
                "success": False,
                "error": "No interests provided",
                "recommendations": []
            }
        
        # Parse interests into list
        interests_list = [i.strip() for i in combined_interests.split(",")]
        
        # Get recommendations
        results = recommend(
            interests=interests_list,
            top=5,
            manifest_path="agent.json"
        )
        
        return {
            "success": True,
            "recommendations": results,
            "count": len(results),
            "interests": interests_list
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "recommendations": []
        }
