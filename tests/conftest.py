"""Shared pytest fixtures and configuration for EventKit tests."""

import json
import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock

# Import EventKit components (with optional import handling)
try:
    from settings import Settings
except ImportError:
    Settings = None

try:
    from telemetry import TelemetryClient
except ImportError:
    TelemetryClient = None

try:
    from agents_sdk_adapter import EventKitAgent
except ImportError:
    EventKitAgent = None

try:
    from bot_handler import EventKitBotHandler
except ImportError:
    EventKitBotHandler = None


# ============================================================================
# Shared Fixtures
# ============================================================================

@pytest.fixture
def sample_manifest() -> Dict[str, Any]:
    """Sample session manifest for testing."""
    return {
        "sessions": [
            {
                "id": "session1",
                "title": "Building AI Agents",
                "category": "AI/ML",
                "description": "Learn to build intelligent agents with LLMs",
                "keywords": ["agents", "ai", "automation", "llm"],
                "popularity": 100
            },
            {
                "id": "session2",
                "title": "AI Safety Fundamentals",
                "category": "Safety",
                "description": "Understanding AI safety principles and alignment",
                "keywords": ["safety", "ethics", "alignment", "ai"],
                "popularity": 80
            },
            {
                "id": "session3",
                "title": "Machine Learning at Scale",
                "category": "ML",
                "description": "Scaling ML systems in production",
                "keywords": ["machine learning", "scalability", "systems", "mlops"],
                "popularity": 90
            },
            {
                "id": "session4",
                "title": "Prompt Engineering Best Practices",
                "category": "AI/ML",
                "description": "Techniques for effective prompt engineering",
                "keywords": ["prompts", "engineering", "llm", "gpt"],
                "popularity": 95
            },
            {
                "id": "session5",
                "title": "Graph API Integration",
                "category": "Integration",
                "description": "Integrating Microsoft Graph with your apps",
                "keywords": ["graph", "api", "microsoft", "integration"],
                "popularity": 70
            }
        ],
        "weights": {
            "interest": 2.0,
            "popularity": 0.5,
            "diversity": 0.3
        }
    }


@pytest.fixture
def manifest_file(tmp_path, sample_manifest) -> Path:
    """Create temporary manifest file for testing."""
    manifest_path = tmp_path / "test_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(sample_manifest, f)
    return manifest_path


@pytest.fixture
def mock_settings():
    """Mock Settings instance."""
    if Settings is None:
        return MagicMock()
    
    settings = Mock(spec=Settings)
    settings.graph_enabled = False
    settings.graph_tenant_id = None
    settings.graph_client_id = None
    settings.graph_client_secret = None
    settings.foundry_enabled = False
    settings.foundry_project_endpoint = None
    settings.foundry_subscription_id = None
    settings.foundry_resource_group = None
    settings.foundry_project_name = None
    settings.foundry_model_deployment = "gpt-4o"
    settings.run_mode = "cli"
    settings.api_token = None
    settings.validate_graph_ready = Mock(return_value=False)
    settings.validate_foundry_ready = Mock(return_value=False)
    return settings


@pytest.fixture
def mock_telemetry():
    """Mock TelemetryClient instance."""
    if TelemetryClient is None:
        return MagicMock()
    
    telemetry = Mock(spec=TelemetryClient)
    telemetry.log = Mock()
    telemetry.track_event = Mock()
    telemetry.track_error = Mock()
    return telemetry


@pytest.fixture
def mock_graph_service():
    """Mock GraphEventService."""
    mock = Mock()
    mock.get_events = Mock(return_value=[])
    mock.user_id = "test-user@example.com"
    return mock


# ============================================================================
# Agent Fixtures
# ============================================================================

@pytest.fixture
def eventkit_agent(mock_settings, mock_telemetry, manifest_file):
    """Create EventKitAgent instance for testing."""
    if EventKitAgent is None:
        pytest.skip("EventKitAgent not available")
    
    return EventKitAgent(
        settings=mock_settings,
        telemetry=mock_telemetry,
        manifest_path=str(manifest_file)
    )


# ============================================================================
# Bot Framework Fixtures
# ============================================================================

@pytest.fixture
def mock_turn_context():
    """Mock Bot Framework TurnContext."""
    context = MagicMock()
    context.activity = MagicMock()
    context.activity.text = "@bot help"
    context.activity.id = "test-activity-123"
    context.activity.from_property = MagicMock()
    context.activity.from_property.id = "user-123"
    context.activity.from_property.name = "Test User"
    context.send_activity = Mock()
    return context


@pytest.fixture
def bot_handler(mock_settings):
    """Create EventKitBotHandler for testing."""
    if EventKitBotHandler is None:
        pytest.skip("EventKitBotHandler not available")
    
    return EventKitBotHandler(
        conversation_state=None,
        user_state=None,
        agent=None
    )


# ============================================================================
# Foundry Fixtures
# ============================================================================

@pytest.fixture
def mock_azure_credential():
    """Mock Azure DefaultAzureCredential."""
    credential = MagicMock()
    credential.get_token = Mock(return_value=MagicMock(token="mock-token"))
    return credential


@pytest.fixture
def mock_ai_project_client():
    """Mock Azure AI Project Client."""
    client = MagicMock()
    client.agents = MagicMock()
    client.agents.create_agent = Mock()
    client.agents.create_thread = Mock()
    client.agents.create_message = Mock()
    client.agents.create_run = Mock()
    return client


@pytest.fixture
def foundry_settings(mock_settings):
    """Settings configured for Foundry."""
    mock_settings.foundry_enabled = True
    mock_settings.foundry_project_endpoint = "https://eastus.api.azureml.ms"
    mock_settings.foundry_subscription_id = "00000000-0000-0000-0000-000000000000"
    mock_settings.foundry_resource_group = "test-rg"
    mock_settings.foundry_project_name = "test-project"
    mock_settings.foundry_model_deployment = "gpt-4o"
    mock_settings.validate_foundry_ready = Mock(return_value=True)
    return mock_settings


# ============================================================================
# Pytest Configuration Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may call Graph API, etc.)"
    )
    config.addinivalue_line(
        "markers", "bot: Bot Framework tests (Teams, adaptive cards)"
    )
    config.addinivalue_line(
        "markers", "foundry: Microsoft Foundry tests (Agent Framework, Prompt Flow)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (>1 second)"
    )
    config.addinivalue_line(
        "markers", "smoke: Smoke tests (basic functionality)"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Auto-mark integration tests
        if "integration" in item.nodeid or "graph" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Auto-mark bot tests
        if "bot" in item.nodeid.lower():
            item.add_marker(pytest.mark.bot)
        
        # Auto-mark foundry tests
        if "foundry" in item.nodeid.lower() or "agent_framework" in item.nodeid.lower():
            item.add_marker(pytest.mark.foundry)
        
        # Auto-mark unit tests (default)
        if not any(marker.name in ["integration", "bot", "foundry", "slow"] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
