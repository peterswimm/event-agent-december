"""
Calculate evaluation metrics for session recommendations.
"""

from promptflow import tool
from typing import Dict, Any, List


@tool
def calculate_metrics(expected_sessions: List[Dict], actual_sessions: List[Dict]) -> Dict[str, float]:
    """
    Calculate precision, recall, and F1 score.
    
    Args:
        expected_sessions: Ground truth sessions
        actual_sessions: Predicted sessions
        
    Returns:
        dict with precision, recall, f1_score
    """
    # Extract session titles
    expected_titles = {s.get("title", "").lower() for s in expected_sessions}
    actual_titles = {s.get("title", "").lower() for s in actual_sessions}
    
    # Calculate metrics
    if not actual_titles:
        return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0}
    
    true_positives = len(expected_titles & actual_titles)
    false_positives = len(actual_titles - expected_titles)
    false_negatives = len(expected_titles - actual_titles)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1_score, 3)
    }
