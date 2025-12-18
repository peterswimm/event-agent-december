"""
Azure AI Projects SDK Adapter for Event Kit Agent

This module provides integration with the Azure AI Projects SDK, enabling
the Event Kit agent to be hosted in Teams, Copilot Studio, and other
Microsoft 365 environments.

Usage:
    from agents_sdk_adapter import EventKitAgent
    
    agent = EventKitAgent()
    result = agent.handle_tool_call("recommend_sessions", {
        "interests": "agents, ai safety",
        "top": 3
    })
"""

import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

# Import core Event Kit functionality
try:
    from core import recommend, explain, recommend_from_graph
    from settings import Settings
    from errors import InvalidInputError, EventKitError
except ImportError as e:
    logging.warning(f"Failed to import Event Kit modules: {e}")
    recommend = None
    explain = None
    recommend_from_graph = None
    Settings = None  # type: ignore
    InvalidInputError = Exception  # type: ignore
    EventKitError = Exception  # type: ignore

# Import telemetry separately (it may not be available)
try:
    from telemetry import TelemetryClient
except ImportError:
    TelemetryClient = None  # type: ignore
    logging.info("TelemetryClient not available")

# Try to import Azure AI Projects SDK (optional dependency)
try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    HAS_AZURE_AI_SDK = True
except ImportError:
    HAS_AZURE_AI_SDK = False
    logging.info("Azure AI Projects SDK not installed. Agent will run in standalone mode.")


logger = logging.getLogger(__name__)


class EventKitAgent:
    """
    Azure AI Projects SDK adapter for Event Kit Agent.
    
    This class wraps the Event Kit recommendation engine and exposes it
    as tool calls compatible with the Azure AI Projects SDK.
    
    Attributes:
        settings: Application settings (Graph credentials, etc.)
        telemetry: Telemetry client for logging
        manifest: Loaded session manifest data
    """
    
    def __init__(
        self,
        settings: Optional[Any] = None,
        telemetry: Optional[Any] = None,
        manifest_path: str = "agent.json"
    ):
        """
        Initialize the Event Kit Agent adapter.
        
        Args:
            settings: Application settings. If None, loads from environment.
            telemetry: Telemetry client. If None, creates new instance.
            manifest_path: Path to agent.json manifest file.
        """
        self.settings = settings or (Settings() if Settings else None)
        self.telemetry = telemetry or (TelemetryClient() if TelemetryClient else None)
        self.manifest_path = Path(manifest_path)
        
        # Load manifest
        self.manifest = self._load_manifest()
        
        # Tool call handlers
        self.tool_handlers = {
            "recommend_sessions": self._handle_recommend,
            "explain_session": self._handle_explain,
            "export_itinerary": self._handle_export,
        }
        
        logger.info("EventKitAgent initialized")
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load the session manifest from agent.json."""
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            logger.info(f"Loaded manifest with {len(manifest.get('sessions', []))} sessions")
            return manifest
        except FileNotFoundError:
            logger.error(f"Manifest file not found: {self.manifest_path}")
            return {"sessions": []}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse manifest: {e}")
            return {"sessions": []}
    
    def handle_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool call from the Azure AI Projects SDK.
        
        Args:
            tool_name: Name of the tool to invoke (e.g., "recommend_sessions")
            parameters: Tool parameters as a dictionary
            
        Returns:
            Dictionary containing the tool result
            
        Raises:
            InvalidInputError: If tool name is unknown or parameters are invalid
            EventKitError: If tool execution fails
        """
        correlation_id = parameters.pop("correlation_id", None)
        
        if correlation_id:
            logger.info(f"Processing tool call: {tool_name} (correlation_id={correlation_id})")
        else:
            logger.info(f"Processing tool call: {tool_name}")
        
        # Get handler
        handler = self.tool_handlers.get(tool_name)
        if not handler:
            raise InvalidInputError(f"Unknown tool: {tool_name}")
        
        try:
            # Execute handler
            result = handler(parameters)
            
            # Log to telemetry
            if self.telemetry and correlation_id:
                self.telemetry.log(
                    action=f"agent_tool_call_{tool_name}",
                    correlation_id=correlation_id,
                    interests=parameters.get("interests", ""),
                    duration_ms=0,  # Actual duration would be measured in production
                    sessions_returned=len(result.get("sessions", []))
                )
            
            return result
            
        except EventKitError as e:
            logger.error(f"Tool call failed: {tool_name} - {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in tool call: {tool_name}")
            raise EventKitError(f"Tool execution failed: {e}")
    
    def _handle_recommend(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle recommend_sessions tool call.
        
        Args:
            parameters: Tool parameters containing:
                - interests (str): Comma-separated interests
                - top (int, optional): Max sessions to return (default: 5)
                - use_graph (bool, optional): Use Graph API (default: False)
                
        Returns:
            Dictionary with sessions, scoring, and conflicts
        """
        interests = parameters.get("interests", "")
        top = parameters.get("top", 5)
        use_graph = parameters.get("use_graph", False)
        
        if not interests:
            raise InvalidInputError("'interests' parameter is required")
        
        # Parse interests
        interests_list = [i.strip() for i in interests.split(",") if i.strip()]
        
        if not interests_list:
            raise InvalidInputError("At least one interest is required")
        
        # Choose recommendation source
        if use_graph and self.settings.graph_enabled:
            # Use Graph-based recommendations
            if recommend_from_graph is None:
                raise EventKitError("Graph recommendations not available")
            
            result = recommend_from_graph(
                interests=interests_list,
                top=top,
                settings=self.settings
            )
        else:
            # Use manifest-based recommendations
            if recommend is None:
                raise EventKitError("Recommend function not available")
            
            result = recommend(
                manifest=self.manifest,
                interests=interests_list,
                top=top
            )
        
        # Format for Teams/Copilot
        formatted_result = self._format_recommendation_result(result)
        
        return formatted_result
    
    def _handle_explain(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle explain_session tool call.
        
        Args:
            parameters: Tool parameters containing:
                - session_title (str): Session to explain
                - interests (str): Comma-separated interests
                
        Returns:
            Dictionary with explanation, matched keywords, and relevance score
        """
        session_title = parameters.get("session_title", "")
        interests = parameters.get("interests", "")
        
        if not session_title:
            raise InvalidInputError("'session_title' parameter is required")
        
        if not interests:
            raise InvalidInputError("'interests' parameter is required")
        
        # Parse interests
        interests_list = [i.strip() for i in interests.split(",") if i.strip()]
        
        if explain is None:
            raise EventKitError("Explain function not available")
        
        # Get explanation
        result = explain(
            manifest=self.manifest,
            session_title=session_title,
            interests=interests_list
        )
        
        # Format for Teams/Copilot
        formatted_result = {
            "session": session_title,
            "explanation": result.get("explanation", ""),
            "matched_keywords": result.get("matched_keywords", []),
            "relevance_score": result.get("relevance_score", 0.0),
            "markdown": self._format_explanation_markdown(result)
        }
        
        return formatted_result
    
    def _handle_export(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle export_itinerary tool call.
        
        Args:
            parameters: Tool parameters containing:
                - interests (str): Comma-separated interests
                - profile_name (str, optional): Profile name to save
                
        Returns:
            Dictionary with markdown content and save status
        """
        interests = parameters.get("interests", "")
        profile_name = parameters.get("profile_name")
        
        if not interests:
            raise InvalidInputError("'interests' parameter is required")
        
        # Parse interests
        interests_list = [i.strip() for i in interests.split(",") if i.strip()]
        
        # Get recommendations for export
        if recommend is None:
            raise EventKitError("Recommend function not available")
        
        recommendations = recommend(
            manifest=self.manifest,
            interests=interests_list,
            top=10  # Export more sessions
        )
        
        # Generate markdown
        markdown = self._generate_itinerary_markdown(recommendations, interests_list)
        
        # Save profile if requested
        saved = False
        if profile_name:
            saved = self._save_profile(profile_name, interests_list)
        
        return {
            "markdown": markdown,
            "profile_saved": saved,
            "profile_name": profile_name if saved else None,
            "sessions_count": len(recommendations.get("sessions", []))
        }
    
    def _format_recommendation_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format recommendation result for Teams/Copilot display."""
        sessions = result.get("sessions", [])
        scoring = result.get("scoring", [])
        
        # Format sessions with enhanced metadata
        formatted_sessions = []
        for i, session in enumerate(sessions):
            score_info = scoring[i] if i < len(scoring) else {}
            
            formatted_session = {
                "id": session.get("id", f"session-{i}"),
                "title": session.get("title", "Untitled"),
                "category": session.get("category", "General"),
                "description": session.get("description", ""),
                "keywords": session.get("keywords", []),
                "popularity": session.get("popularity", 0),
                "score": score_info.get("score", 0),
                "matched_interests": score_info.get("matched_interests", []),
                "confidence": score_info.get("confidence_level", 0)
            }
            formatted_sessions.append(formatted_session)
        
        return {
            "sessions": formatted_sessions,
            "total_count": len(formatted_sessions),
            "conflicts": result.get("conflicts", 0),
            "markdown": self._format_recommendations_markdown(formatted_sessions)
        }
    
    def _format_recommendations_markdown(self, sessions: List[Dict[str, Any]]) -> str:
        """Generate markdown representation of recommendations."""
        lines = ["# Recommended Sessions\n"]
        
        for i, session in enumerate(sessions, 1):
            lines.append(f"## {i}. {session['title']}")
            lines.append(f"**Category**: {session['category']}")
            lines.append(f"**Score**: {session['score']:.2f}")
            
            if session.get('matched_interests'):
                lines.append(f"**Matched Interests**: {', '.join(session['matched_interests'])}")
            
            if session.get('description'):
                lines.append(f"\n{session['description']}")
            
            lines.append("")  # Empty line between sessions
        
        return "\n".join(lines)
    
    def _format_explanation_markdown(self, result: Dict[str, Any]) -> str:
        """Generate markdown representation of explanation."""
        lines = [
            f"# Session Explanation: {result.get('session', 'Unknown')}",
            "",
            result.get("explanation", ""),
            "",
            "## Matched Keywords",
        ]
        
        keywords = result.get("matched_keywords", [])
        if keywords:
            for kw in keywords:
                lines.append(f"- {kw}")
        else:
            lines.append("- None")
        
        lines.append("")
        lines.append(f"**Relevance Score**: {result.get('relevance_score', 0):.2f}")
        
        return "\n".join(lines)
    
    def _generate_itinerary_markdown(
        self, 
        recommendations: Dict[str, Any], 
        interests: List[str]
    ) -> str:
        """Generate complete itinerary in Markdown format."""
        lines = [
            "# My Personalized Event Itinerary",
            "",
            f"**Interests**: {', '.join(interests)}",
            f"**Generated**: {self._get_timestamp()}",
            "",
            "---",
            ""
        ]
        
        sessions = recommendations.get("sessions", [])
        scoring = recommendations.get("scoring", [])
        
        for i, session in enumerate(sessions):
            score_info = scoring[i] if i < len(scoring) else {}
            
            lines.append(f"## {i+1}. {session.get('title', 'Untitled')}")
            lines.append(f"**Category**: {session.get('category', 'General')}")
            lines.append(f"**Relevance Score**: {score_info.get('score', 0):.2f}")
            
            if session.get('description'):
                lines.append("")
                lines.append(session['description'])
            
            matched = score_info.get('matched_interests', [])
            if matched:
                lines.append("")
                lines.append(f"**Why this session**: Matches your interests in {', '.join(matched)}")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        conflicts = recommendations.get("conflicts", 0)
        if conflicts > 0:
            lines.append(f"⚠️ **Note**: {conflicts} scheduling conflicts detected")
        
        return "\n".join(lines)
    
    def _save_profile(self, profile_name: str, interests: List[str]) -> bool:
        """Save user profile for future use."""
        try:
            profile_file = Path.home() / ".event_agent_profiles.json"
            
            # Load existing profiles
            profiles = {}
            if profile_file.exists():
                with open(profile_file, 'r') as f:
                    profiles = json.load(f)
            
            # Save profile
            profiles[profile_name] = {
                "interests": interests,
                "updated": self._get_timestamp()
            }
            
            with open(profile_file, 'w') as f:
                json.dump(profiles, f, indent=2)
            
            logger.info(f"Saved profile: {profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get list of agent capabilities.
        
        Returns:
            List of capability definitions
        """
        return [
            {
                "name": "recommend_sessions",
                "description": "Get personalized session recommendations",
                "parameters": ["interests", "top", "use_graph"]
            },
            {
                "name": "explain_session",
                "description": "Explain why a session matches interests",
                "parameters": ["session_title", "interests"]
            },
            {
                "name": "export_itinerary",
                "description": "Export personalized itinerary",
                "parameters": ["interests", "profile_name"]
            }
        ]


# Convenience function for standalone usage
def create_agent(
    manifest_path: str = "agent.json",
    settings: Optional[Any] = None
) -> EventKitAgent:
    """
    Create and return an EventKitAgent instance.
    
    Args:
        manifest_path: Path to agent.json manifest
        settings: Application settings (optional)
        
    Returns:
        Initialized EventKitAgent
    """
    return EventKitAgent(
        settings=settings,
        manifest_path=manifest_path
    )


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create agent
    agent = create_agent()
    
    # Example tool calls
    print("=== Example: Recommend Sessions ===")
    result = agent.handle_tool_call("recommend_sessions", {
        "interests": "agents, ai safety",
        "top": 3
    })
    print(f"Recommended {len(result['sessions'])} sessions")
    print(result['markdown'])
    
    print("\n=== Example: Explain Session ===")
    if result['sessions']:
        first_session = result['sessions'][0]['title']
        explanation = agent.handle_tool_call("explain_session", {
            "session_title": first_session,
            "interests": "agents, ai safety"
        })
        print(explanation['markdown'])
    
    print("\n=== Example: Export Itinerary ===")
    export_result = agent.handle_tool_call("export_itinerary", {
        "interests": "agents, ai safety, machine learning",
        "profile_name": "demo_profile"
    })
    print(f"Exported {export_result['sessions_count']} sessions")
    print(f"Profile saved: {export_result['profile_saved']}")
