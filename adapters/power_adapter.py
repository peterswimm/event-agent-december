"""
Power Platform Adapter

Unified adapter for:
- Custom Connectors (OpenAPI)
- Power Automate flows
- Logic Apps
"""

from typing import Any, Dict, Optional

from adapters.base_adapter import UnifiedAdapter, AdapterType, ToolDefinition


class PowerAdapter(UnifiedAdapter):
    """
    Power Platform adapter for EventKit.

    Supports:
    - Custom Connectors
    - Power Automate
    - Logic Apps
    """

    def __init__(self, **kwargs):
        """Initialize Power Platform adapter."""
        super().__init__(AdapterType.POWER_PLATFORM, **kwargs)

    def _validate_parameters(
        self,
        tool: ToolDefinition,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate parameters for Power Platform (OpenAPI format)."""
        # Power Platform sends parameters in OpenAPI format
        validated = {}

        schema = tool.parameters.get("properties", {})
        required = tool.parameters.get("required", [])

        for param_name, param_schema in schema.items():
            if param_name in parameters:
                validated[param_name] = parameters[param_name]
            elif "default" in param_schema:
                validated[param_name] = param_schema["default"]
            elif param_name in required:
                raise ValueError(f"Missing required parameter: {param_name}")

        return validated

    def _transform_response(
        self,
        tool: ToolDefinition,
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform response for Power Platform (OpenAPI response format)."""
        # Power Platform expects OpenAPI-compliant response
        return {
            "value": result.get("result", {}),
            "status": result.get("status", "success"),
            "@odata.context": f"$metadata#EventKit.{tool.name}",
            "@odata.type": "#EventKit.Response",
            "timestamp": result.get("timestamp")
        }

    def get_openapi_spec(self) -> Dict[str, Any]:
        """
        Generate OpenAPI specification for Power Platform.

        Returns:
            OpenAPI 3.0 specification
        """
        paths = {}

        for tool in self.tools.values():
            paths[f"/{tool.name}"] = {
                "post": {
                    "summary": tool.description,
                    "operationId": tool.name,
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": tool.parameters
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "value": {"type": "object"},
                                            "status": {"type": "string"},
                                            "@odata.context": {"type": "string"},
                                            "@odata.type": {"type": "string"},
                                            "timestamp": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Bad Request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

        return {
            "openapi": "3.0.0",
            "info": {
                "title": "EventKit API",
                "version": "1.0.0",
                "description": "EventKit session recommendation API for Power Platform integration"
            },
            "servers": [
                {"url": "https://eventkit.azurewebsites.net", "description": "Production"},
                {"url": "http://localhost:8010", "description": "Development"}
            ],
            "paths": paths,
            "components": {
                "securitySchemes": {
                    "apiKey": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                }
            },
            "security": [{"apiKey": []}]
        }
