"""
EventKit Unified Adapters

Provides unified adapter pattern for integrating EventKit with:
- Microsoft Foundry (Azure AI)
- Power Platform Connectors
- Bot Framework (Direct Line, Teams, WebChat)
"""

from adapters.base_adapter import UnifiedAdapter, AdapterType, ToolDefinition

__all__ = [
    "UnifiedAdapter",
    "AdapterType",
    "ToolDefinition",
]

# Conditional imports for optional adapters
try:
    from adapters.foundry_adapter import FoundryAdapter
    __all__.append("FoundryAdapter")
except ImportError:
    pass

try:
    from adapters.power_adapter import PowerAdapter
    __all__.append("PowerAdapter")
except ImportError:
    pass

try:
    from adapters.bot_adapter import BotAdapter
    __all__.append("BotAdapter")
except ImportError:
    pass
