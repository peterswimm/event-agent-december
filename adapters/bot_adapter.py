"""
Bot Framework Adapter

Unified adapter for:
- Direct Line / WebChat
- Microsoft Teams
- Bot Framework channels
"""

from typing import Any, Dict, Optional
import logging

from adapters.base_adapter import UnifiedAdapter, AdapterType, ToolDefinition

try:
    from botbuilder.core import ActivityHandler, TurnContext
    from botbuilder.schema import Activity, ActivityTypes, Attachment
    HAS_BOT_FRAMEWORK = True
except ImportError:
    HAS_BOT_FRAMEWORK = False
    logging.info("Bot Framework SDK not installed. Install with: pip install botbuilder-core")


class BotAdapter(UnifiedAdapter):
    """
    Bot Framework adapter for EventKit.

    Supports:
    - Direct Line
    - Microsoft Teams
    - WebChat
    - All Bot Framework channels
    """

    def __init__(self, **kwargs):
        """Initialize Bot Framework adapter."""
        super().__init__(AdapterType.BOT_FRAMEWORK, **kwargs)

        if not HAS_BOT_FRAMEWORK:
            self.logger.warning(
                "Bot Framework SDK not installed. "
                "Install with: pip install botbuilder-core botbuilder-integration-aiohttp"
            )

    def _validate_parameters(
        self,
        tool: ToolDefinition,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate parameters for Bot Framework (activity context)."""
        # Bot Framework sends text in activity
        # Extract interests from text message
        if "text" in parameters:
            text = parameters["text"].strip()
            return {
                "interests": text,
                "top": parameters.get("top", 5),
                "use_graph": parameters.get("use_graph", False)
            }

        # Standard parameter validation
        required = tool.parameters.get("required", [])
        for param_name in required:
            if param_name not in parameters:
                raise ValueError(f"Missing required parameter: {param_name}")

        return parameters

    def _transform_response(
        self,
        tool: ToolDefinition,
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform response for Bot Framework (Activity format)."""
        # Bot Framework expects Activity with optional Adaptive Card
        result_data = result.get("result", {})
        sessions = result_data.get("sessions", [])

        # Generate text summary
        if sessions:
            summary = f"Found {len(sessions)} sessions:\n\n"
            for i, session in enumerate(sessions[:3], 1):
                summary += f"{i}. **{session.get('title', 'Unknown')}**\n"
                topics = session.get('topics', [])
                if topics:
                    summary += f"   Topics: {', '.join(topics)}\n"
        else:
            summary = "No sessions found for your interests."

        response = {
            "type": "message",
            "text": summary,
            "attachments": []
        }

        # Add Adaptive Card if requested
        if context and context.get("include_card") and sessions:
            card = self._generate_adaptive_card(sessions)
            response["attachments"].append({
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card
            })

        return response

    def _generate_adaptive_card(self, sessions: list) -> Dict[str, Any]:
        """Generate Adaptive Card for sessions."""
        body = [
            {
                "type": "TextBlock",
                "text": "Session Recommendations",
                "weight": "Bolder",
                "size": "Large"
            }
        ]

        for session in sessions[:5]:
            body.append({
                "type": "Container",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": session.get("title", ""),
                        "weight": "Bolder",
                        "wrap": True
                    },
                    {
                        "type": "TextBlock",
                        "text": f"Topics: {', '.join(session.get('topics', []))}",
                        "wrap": True,
                        "isSubtle": True
                    },
                    {
                        "type": "TextBlock",
                        "text": f"Match Score: {int(session.get('score', 0) * 100)}%",
                        "color": "Good" if session.get('score', 0) > 0.7 else "Accent"
                    }
                ],
                "separator": True
            })

        return {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": body
        }

    async def handle_activity(
        self,
        turn_context: Any
    ) -> None:
        """
        Handle Bot Framework activity.

        Args:
            turn_context: Bot Framework TurnContext
        """
        if not HAS_BOT_FRAMEWORK:
            raise RuntimeError("Bot Framework SDK not installed")

        if turn_context.activity.type == ActivityTypes.message:
            text = turn_context.activity.text or ""

            # Call unified tool handler
            result = self.handle_tool_call(
                "recommend_sessions",
                {"text": text, "top": 5},
                {"include_card": True}
            )

            # Send response
            await turn_context.send_activity(
                Activity(
                    type=result["type"],
                    text=result["text"],
                    attachments=[
                        Attachment(**attach) for attach in result.get("attachments", [])
                    ]
                )
            )
