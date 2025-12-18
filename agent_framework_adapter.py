"""
Microsoft Agent Framework Adapter for Event Kit

This module provides integration with Microsoft Agent Framework (preview),
enabling advanced agent orchestration, multi-agent systems, and Microsoft
Foundry (formerly Azure AI Foundry) model integration.

NOTE: This file is maintained for backward compatibility.
New code should use adapters.foundry_adapter.FoundryAdapter directly.

Installation:
    pip install agent-framework-azure-ai --pre

Usage:
    from agent_framework_adapter import EventKitAgentFramework

    agent = EventKitAgentFramework(
        project_endpoint="https://your-project.region.ai.azure.com",
        credential=DefaultAzureCredential()
    )

    result = await agent.run("recommend sessions about agents and AI")
"""

import logging
from typing import Any, Dict, List, Optional, Union
import json
from datetime import datetime

# Import unified adapter
from adapters.foundry_adapter import FoundryAdapter

logger = logging.getLogger(__name__)


class EventKitAgentFramework(FoundryAdapter):
    """
    Microsoft Agent Framework integration for Event Kit.

    Backward compatibility wrapper for FoundryAdapter.

    Provides advanced agent capabilities:
    - Model orchestration with Microsoft Foundry
    - Multi-agent coordination
    - Structured tool calling
    - Streaming responses
    - Conversation memory
    """

    def __init__(
        self,
        project_endpoint: Optional[str] = None,
        credential: Optional[Any] = None,
        model_deployment: str = "gpt-4o",
        **kwargs
    ):
        """
        Initialize Agent Framework adapter.

        Args:
            project_endpoint: Microsoft Foundry project endpoint URL
            credential: Azure credential (DefaultAzureCredential recommended)
            model_deployment: Model deployment name in Foundry
            **kwargs: Additional Agent Framework configuration
        """
        # Use unified adapter implementation
        super().__init__(
            project_endpoint=project_endpoint,
            credential=credential,
            model_deployment=model_deployment,
            **kwargs
        )

        logger.info(f"EventKit Agent Framework initialized with model: {model_deployment}")

    def _create_agent(self) -> Agent:
        """Create Agent Framework agent with EventKit tools."""

        # Define tools for the agent
        tools = [
            Tool(
                name="recommend_sessions",
                description="Get personalized event session recommendations based on interests",
                parameters={
                    "type": "object",
                    "properties": {
                        "interests": {
                            "type": "string",
                            "description": "Comma-separated list of interests (e.g., 'agents, ai safety')"
                        },
                        "top": {
                            "type": "integer",
                            "description": "Number of recommendations to return (default: 3)",
                            "default": 3
                        },
                        "use_graph": {
                            "type": "boolean",
                            "description": "Use Microsoft Graph calendar for recommendations",
                            "default": False
                        }
                    },
                    "required": ["interests"]
                },
                function=self._tool_recommend_sessions
            ),
            Tool(
                name="explain_session",
                description="Explain why a specific session matches user interests",
                parameters={
                    "type": "object",
                    "properties": {
                        "session_title": {
                            "type": "string",
                            "description": "Title of the session to explain"
                        },
                        "interests": {
                            "type": "string",
                            "description": "Comma-separated list of interests"
                        }
                    },
                    "required": ["session_title", "interests"]
                },
                function=self._tool_explain_session
            ),
            Tool(
                name="export_itinerary",
                description="Export a personalized itinerary in Markdown format",
                parameters={
                    "type": "object",
                    "properties": {
                        "interests": {
                            "type": "string",
                            "description": "Comma-separated list of interests"
                        },
                        "profile_name": {
                            "type": "string",
                            "description": "Profile name to save preferences"
                        }
                    },
                    "required": ["interests"]
                },
                function=self._tool_export_itinerary
            )
        ]

        # Create Agent Framework agent with Azure AI connection
        agent = AzureAIAgent(
            endpoint=self.project_endpoint,
            credential=self.credential,
            model=self.model_deployment,
            tools=tools,
            instructions="""You are EventKit, an AI assistant that helps users discover and
            plan conference sessions based on their interests. You have access to tools that:

            1. Recommend sessions based on interests
            2. Explain why sessions match interests
            3. Export personalized itineraries

            Be helpful, concise, and proactive in suggesting relevant sessions. When users
            express interests, use the recommend_sessions tool to find matching sessions.
            """,
            temperature=0.7,
            max_tokens=2000
        )

        return agent

    def _tool_recommend_sessions(self, interests: str, top: int = 3, use_graph: bool = False) -> Dict[str, Any]:
        """Tool function: Get session recommendations."""
        try:
            interests_list = [i.strip() for i in interests.split(",")]

            if use_graph and self.settings.validate_graph_ready():
                from graph_service import GraphService
                graph = GraphService()
                results = graph.recommend_from_calendar(
                    interests=interests_list,
                    top=top
                )
            else:
                results = recommend(
                    interests=interests_list,
                    top=top,
                    manifest_path="agent.json"
                )

            return {
                "success": True,
                "sessions": results,
                "count": len(results),
                "interests": interests_list
            }

        except Exception as e:
            logger.error(f"Error in recommend_sessions tool: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _tool_explain_session(self, session_title: str, interests: str) -> Dict[str, Any]:
        """Tool function: Explain session match."""
        try:
            interests_list = [i.strip() for i in interests.split(",")]

            explanation = explain(
                session_title=session_title,
                interests=interests_list,
                manifest_path="agent.json"
            )

            return {
                "success": True,
                "explanation": explanation,
                "session": session_title,
                "interests": interests_list
            }

        except Exception as e:
            logger.error(f"Error in explain_session tool: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _tool_export_itinerary(self, interests: str, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """Tool function: Export itinerary."""
        try:
            interests_list = [i.strip() for i in interests.split(",")]

            itinerary = export_itinerary(
                interests=interests_list,
                manifest_path="agent.json"
            )

            # Save profile if name provided
            if profile_name:
                from agent import save_profile
                save_profile(profile_name, interests_list)

            return {
                "success": True,
                "itinerary": itinerary,
                "profile_saved": profile_name is not None,
                "profile_name": profile_name
            }

        except Exception as e:
            logger.error(f"Error in export_itinerary tool: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def run(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Run the agent with a user message.

        Args:
            user_message: User's input message
            context: Optional conversation context

        Returns:
            Agent's response text
        """
        try:
            # Create run context
            run_context = RunContext(
                user_id=context.get("user_id", "default") if context else "default",
                conversation_id=context.get("conversation_id", "default") if context else "default",
                metadata=context or {}
            )

            # Run agent
            response = await self.agent.run(
                message=user_message,
                context=run_context
            )

            return response.content

        except Exception as e:
            logger.error(f"Error running Agent Framework: {e}")
            return f"Error: {str(e)}"

    async def stream(self, user_message: str, context: Optional[Dict[str, Any]] = None):
        """
        Stream agent responses for real-time display.

        Args:
            user_message: User's input message
            context: Optional conversation context

        Yields:
            Response chunks as they're generated
        """
        try:
            run_context = RunContext(
                user_id=context.get("user_id", "default") if context else "default",
                conversation_id=context.get("conversation_id", "default") if context else "default",
                metadata=context or {}
            )

            # Stream responses
            async for chunk in self.agent.stream(message=user_message, context=run_context):
                yield chunk.content

        except Exception as e:
            logger.error(f"Error streaming from Agent Framework: {e}")
            yield f"Error: {str(e)}"


# Convenience functions for backward compatibility
async def run_agent_framework(
    message: str,
    project_endpoint: Optional[str] = None,
    model: str = "gpt-4o"
) -> str:
    """
    Quick helper to run Agent Framework without manual setup.

    Example:
        response = await run_agent_framework(
            "recommend sessions about agents and AI",
            project_endpoint="https://my-project.eastus.ai.azure.com"
        )
    """
    agent = EventKitAgentFramework(
        project_endpoint=project_endpoint,
        model_deployment=model
    )
    return await agent.run(message)


if __name__ == "__main__":
    # Example usage
    import asyncio

    async def main():
        # Initialize agent
        agent = EventKitAgentFramework(
            project_endpoint="https://your-project.eastus.ai.azure.com",
            model_deployment="gpt-4o"
        )

        # Run query
        response = await agent.run("I'm interested in AI agents and safety. What sessions do you recommend?")
        print(response)

        # Stream query
        print("\nStreaming response:")
        async for chunk in agent.stream("Explain the first session to me"):
            print(chunk, end="", flush=True)

    # asyncio.run(main())
    print("Agent Framework adapter loaded. Use EventKitAgentFramework class for integration.")
