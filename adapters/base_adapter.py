"""
Unified Adapter Base for EventKit

Provides common functionality for all EventKit adapters (Foundry, Power Platform, Bot Framework).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import logging
from datetime import datetime
import json

from core import recommend, explain, export_itinerary
from settings import Settings
from errors import InvalidInputError, EventKitError

# Try to import telemetry (optional)
try:
    from telemetry import TelemetryClient
except ImportError:
    TelemetryClient = None


class AdapterType(Enum):
    """Types of adapters."""
    FOUNDRY = "foundry"
    POWER_PLATFORM = "power_platform"
    BOT_FRAMEWORK = "bot_framework"
    HTTP_API = "http_api"


class ToolDefinition:
    """Metadata for an EventKit tool."""

    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameters: Dict[str, Any],
        response_format: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.parameters = parameters
        self.response_format = response_format or "json"


class UnifiedAdapter(ABC):
    """
    Base adapter class for all EventKit integrations.

    Provides:
    - Tool registration and discovery
    - Shared error handling
    - Unified telemetry
    - Common credential management
    - Request/response transformation
    """

    def __init__(
        self,
        adapter_type: AdapterType,
        settings: Optional[Settings] = None,
        telemetry: Optional[Any] = None,
        manifest_path: str = "agent.json"
    ):
        """
        Initialize unified adapter.

        Args:
            adapter_type: Type of adapter (Foundry, Power, Bot)
            settings: Application settings
            telemetry: Telemetry client
            manifest_path: Path to agent manifest
        """
        self.adapter_type = adapter_type
        self.settings = settings or Settings()
        self.telemetry = telemetry or (TelemetryClient() if TelemetryClient else None)
        self.manifest_path = manifest_path

        # Load manifest
        self.manifest = self._load_manifest()

        # Register tools
        self.tools: Dict[str, ToolDefinition] = {}
        self._register_tools()

        self.logger = logging.getLogger(f"{__name__}.{adapter_type.value}")
        self.logger.info(f"Initialized {adapter_type.value} adapter with {len(self.tools)} tools")

    def _load_manifest(self) -> Dict[str, Any]:
        """Load agent.json manifest."""
        from pathlib import Path

        manifest_file = Path(self.manifest_path)
        if manifest_file.exists():
            with open(manifest_file) as f:
                return json.load(f)

        self.logger.warning(f"Manifest not found: {self.manifest_path}")
        return {"sessions": []}

    def _register_tools(self) -> None:
        """Register EventKit tools."""
        # Recommend sessions tool
        self.tools["recommend_sessions"] = ToolDefinition(
            name="recommend_sessions",
            description="Recommend conference sessions based on user interests",
            handler=self._handle_recommend,
            parameters={
                "type": "object",
                "properties": {
                    "interests": {
                        "type": "string",
                        "description": "Comma-separated list of interests"
                    },
                    "top": {
                        "type": "integer",
                        "description": "Number of sessions to return",
                        "default": 5
                    },
                    "use_graph": {
                        "type": "boolean",
                        "description": "Use Microsoft Graph for personalization",
                        "default": False
                    }
                },
                "required": ["interests"]
            }
        )

        # Explain session tool
        self.tools["explain_session"] = ToolDefinition(
            name="explain_session",
            description="Explain why a session matches user interests",
            handler=self._handle_explain,
            parameters={
                "type": "object",
                "properties": {
                    "session_title": {
                        "type": "string",
                        "description": "Title of the session to explain"
                    },
                    "interests": {
                        "type": "string",
                        "description": "User's interests"
                    }
                },
                "required": ["session_title", "interests"]
            }
        )

        # Export itinerary tool
        self.tools["export_itinerary"] = ToolDefinition(
            name="export_itinerary",
            description="Export personalized itinerary to markdown",
            handler=self._handle_export,
            parameters={
                "type": "object",
                "properties": {
                    "interests": {
                        "type": "string",
                        "description": "User's interests"
                    },
                    "profile_name": {
                        "type": "string",
                        "description": "Profile name for the itinerary"
                    }
                },
                "required": ["interests"]
            }
        )

    def handle_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle tool call with unified error handling and telemetry.

        Args:
            tool_name: Name of the tool to invoke
            parameters: Tool parameters
            context: Optional adapter-specific context

        Returns:
            Tool execution result

        Raises:
            InvalidInputError: If tool is unknown or parameters are invalid
            EventKitError: If tool execution fails
        """
        start_time = datetime.utcnow()
        correlation_id = parameters.pop("correlation_id", None)

        self.logger.info(
            f"Tool call: {tool_name}",
            extra={
                "tool": tool_name,
                "adapter": self.adapter_type.value,
                "correlation_id": correlation_id
            }
        )

        # Get tool definition
        tool = self.tools.get(tool_name)
        if not tool:
            error_msg = f"Unknown tool: {tool_name}"
            self.logger.error(error_msg)
            self._log_telemetry("tool_call_failed", {
                "tool": tool_name,
                "error": "unknown_tool",
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            })
            raise InvalidInputError(error_msg)

        try:
            # Validate parameters (adapter-specific)
            validated_params = self._validate_parameters(tool, parameters)

            # Execute tool handler
            result = tool.handler(validated_params, context)

            # Transform response (adapter-specific)
            response = self._transform_response(tool, result, context)

            # Log success telemetry
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._log_telemetry("tool_call_success", {
                "tool": tool_name,
                "adapter": self.adapter_type.value,
                "duration_ms": duration_ms,
                "correlation_id": correlation_id
            })

            return response

        except InvalidInputError as e:
            self.logger.error(f"Invalid parameters: {e}")
            self._log_telemetry("tool_call_failed", {
                "tool": tool_name,
                "error": "invalid_parameters",
                "details": str(e)
            })
            raise
        except Exception as e:
            self.logger.exception(f"Tool execution failed: {e}")
            self._log_telemetry("tool_call_failed", {
                "tool": tool_name,
                "error": "execution_error",
                "details": str(e)
            })
            raise EventKitError(f"Tool execution failed: {e}") from e

    def _handle_recommend(
        self,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle recommend_sessions tool call."""
        interests = parameters.get("interests", "").split(",")
        interests = [i.strip() for i in interests if i.strip()]
        top = parameters.get("top", 5)
        use_graph = parameters.get("use_graph", False)

        result = recommend(self.manifest, interests, top)

        return {
            "status": "success",
            "result": result,
            "sessions_count": len(result.get("sessions", [])),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _handle_explain(
        self,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle explain_session tool call."""
        session_title = parameters.get("session_title", "")
        interests = parameters.get("interests", "").split(",")
        interests = [i.strip() for i in interests if i.strip()]

        result = explain(self.manifest, session_title, interests)

        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _handle_export(
        self,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle export_itinerary tool call."""
        interests = parameters.get("interests", "").split(",")
        interests = [i.strip() for i in interests if i.strip()]
        profile_name = parameters.get("profile_name", "default")

        result = export_itinerary(self.manifest, interests, profile_name)

        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _log_telemetry(self, event: str, properties: Dict[str, Any]) -> None:
        """Log telemetry event."""
        if self.telemetry:
            try:
                self.telemetry.log_event(event, properties)
            except Exception as e:
                self.logger.warning(f"Failed to log telemetry: {e}")

    # Abstract methods (adapter-specific implementation)

    @abstractmethod
    def _validate_parameters(
        self,
        tool: ToolDefinition,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and normalize parameters (adapter-specific).

        Args:
            tool: Tool definition with schema
            parameters: Raw parameters from adapter

        Returns:
            Validated and normalized parameters
        """
        pass

    @abstractmethod
    def _transform_response(
        self,
        tool: ToolDefinition,
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Transform response for adapter (adapter-specific).

        Args:
            tool: Tool definition
            result: Raw result from tool handler
            context: Adapter-specific context

        Returns:
            Transformed response for adapter
        """
        pass

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in adapter-specific format.

        Returns:
            List of tool definitions
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]
