"""
Microsoft Foundry (Azure AI) Adapter

Unified adapter for:
- Azure AI Projects SDK
- Microsoft Agent Framework
- Prompt Flow integration
"""

from typing import Any, Dict, Optional
import logging

from adapters.base_adapter import UnifiedAdapter, AdapterType, ToolDefinition
from settings import Settings

try:
    from agent_framework_azure_ai import AzureAIAgent
    from agent_framework import Agent, Tool, RunContext
    from azure.identity import DefaultAzureCredential
    HAS_AGENT_FRAMEWORK = True
except ImportError:
    HAS_AGENT_FRAMEWORK = False
    logging.info("Microsoft Agent Framework not available. Install with: pip install agent-framework-azure-ai --pre")


class FoundryAdapter(UnifiedAdapter):
    """
    Microsoft Foundry adapter for EventKit.

    Supports:
    - Azure AI Projects SDK
    - Microsoft Agent Framework
    - Prompt Flow deployments
    """

    def __init__(
        self,
        project_endpoint: Optional[str] = None,
        credential: Optional[Any] = None,
        model_deployment: str = "gpt-4o",
        settings: Optional[Settings] = None,
        **kwargs
    ):
        """
        Initialize Foundry adapter.

        Args:
            project_endpoint: Microsoft Foundry project endpoint URL
            credential: Azure credential (DefaultAzureCredential recommended)
            model_deployment: Model deployment name in Foundry
            settings: Application settings
            **kwargs: Additional base adapter arguments
        """
        # Initialize base adapter first
        super().__init__(AdapterType.FOUNDRY, settings=settings, **kwargs)

        if not HAS_AGENT_FRAMEWORK:
            self.logger.warning(
                "Microsoft Agent Framework not installed. "
                "Install with: pip install agent-framework-azure-ai --pre"
            )
            self.agent = None
        else:
            self.project_endpoint = project_endpoint or self.settings.foundry_project_endpoint
            self.credential = credential or DefaultAzureCredential()
            self.model_deployment = model_deployment

            # Initialize Agent Framework
            self.agent = self._create_agent()
            self.logger.info(f"Agent Framework initialized with model: {model_deployment}")

    def _create_agent(self) -> Optional[Agent]:
        """Create Agent Framework agent with EventKit tools."""
        if not HAS_AGENT_FRAMEWORK:
            return None

        tools = [
            Tool(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters,
                handler=lambda params, ctx, t=tool: self.handle_tool_call(
                    t.name, params, ctx
                )
            )
            for tool in self.tools.values()
        ]

        return AzureAIAgent(
            project_endpoint=self.project_endpoint,
            credential=self.credential,
            model_deployment=self.model_deployment,
            tools=tools
        )

    def _validate_parameters(
        self,
        tool: ToolDefinition,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate parameters for Foundry (Agent Framework format)."""
        # Agent Framework provides validated params
        # Just ensure required fields are present
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
        """Transform response for Agent Framework."""
        # Agent Framework expects structured response
        return {
            "content": result.get("result", {}),
            "status": result.get("status", "success"),
            "metadata": {
                "timestamp": result.get("timestamp"),
                "adapter": "foundry",
                "sessions_count": result.get("sessions_count")
            }
        }

    async def run(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run agent with message (Agent Framework API).

        Args:
            message: User message
            context: Optional context dictionary

        Returns:
            Agent response
        """
        if not self.agent:
            raise RuntimeError(
                "Agent Framework not available. "
                "Install with: pip install agent-framework-azure-ai --pre"
            )

        run_context = RunContext(
            message=message,
            context=context or {}
        )

        response = await self.agent.run(run_context)
        return response
