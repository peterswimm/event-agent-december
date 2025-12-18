"""
Parse user intent and extract parameters for EventKit agent.
"""

from promptflow import tool
import re
from typing import Dict, Any


@tool
def parse_intent(user_message: str) -> Dict[str, Any]:
    """
    Parse user message to determine intent and extract parameters.
    
    Returns:
        dict with keys: intent, extracted_interests, session_title
    """
    message_lower = user_message.lower()
    
    # Default values
    intent = "general"
    extracted_interests = ""
    session_title = ""
    
    # Detect recommend intent
    if any(word in message_lower for word in ["recommend", "suggest", "find", "show", "interested in", "looking for"]):
        intent = "recommend"
        # Extract interests from common patterns
        patterns = [
            r"(?:interested in|about|regarding)\s+([^\.!?]+)",
            r"(?:sessions? (?:on|about))\s+([^\.!?]+)",
            r"(?:looking for)\s+([^\.!?]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                extracted_interests = match.group(1).strip()
                break
        
        # If no pattern matched, extract comma-separated terms
        if not extracted_interests:
            # Look for technology/topic keywords
            keywords = re.findall(r'\b(?:ai|agents?|ml|machine learning|llm|nlp|gen ai|safety|privacy|security|telemetry|monitoring)\b', message_lower)
            if keywords:
                extracted_interests = ", ".join(set(keywords))
    
    # Detect explain intent
    elif any(word in message_lower for word in ["explain", "why", "tell me about", "what about"]):
        intent = "explain"
        # Extract session title in quotes
        quote_match = re.search(r'"([^"]+)"', user_message)
        if quote_match:
            session_title = quote_match.group(1)
        # Extract from "about X" or "why X"
        elif "about" in message_lower:
            about_match = re.search(r'about\s+([^\.!?]+)', message_lower)
            if about_match:
                session_title = about_match.group(1).strip()
        
        # Extract interests if mentioned
        interest_match = re.search(r'(?:interested in|interests?:?)\s+([^\.!?]+)', message_lower)
        if interest_match:
            extracted_interests = interest_match.group(1).strip()
    
    # Detect export intent
    elif any(word in message_lower for word in ["export", "itinerary", "schedule", "agenda"]):
        intent = "export"
        # Extract interests
        interest_match = re.search(r'(?:for|about|with)\s+([^\.!?]+)', message_lower)
        if interest_match:
            extracted_interests = interest_match.group(1).strip()
    
    return {
        "intent": intent,
        "extracted_interests": extracted_interests,
        "session_title": session_title
    }
