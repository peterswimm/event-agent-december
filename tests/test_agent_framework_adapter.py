"""
Tests for Microsoft Foundry Agent Framework Adapter

Tests EventKitAgentFramework integration with Azure AI Projects,
Agent Framework SDK, and Prompt Flow.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Skip all tests if agent framework not available
pytest.importorskip("agent_framework_azure_ai", reason="Agent Framework SDK not installed")

# Import will fail if module doesn't exist - that's OK for now
try:
    from agent_framework_adapter import EventKitAgentFramework
    HAS_AGENT_FRAMEWORK = True
except ImportError:
    HAS_AGENT_FRAMEWORK = False
    pytest.skip("agent_framework_adapter module not available", allow_module_level=True)


@pytest.mark.foundry
class TestAgentFrameworkInitialization:
    """Test Agent Framework adapter initialization."""
    
    def test_agent_framework_creates_with_defaults(self, foundry_settings):
        """Test initialization with default settings."""
        with patch("agent_framework_adapter.AzureAIAgent"):
            agent = EventKitAgentFramework(settings=foundry_settings)
            
            assert agent.settings == foundry_settings
            assert agent.model_deployment == "gpt-4o"
    
    def test_agent_framework_validates_settings(self, mock_settings):
        """Test that initialization validates Foundry settings."""
        mock_settings.foundry_enabled = False
        mock_settings.validate_foundry_ready = Mock(return_value=False)
        
        with pytest.raises(ValueError):
            EventKitAgentFramework(settings=mock_settings)
    
    def test_agent_framework_with_custom_deployment(self, foundry_settings):
        """Test initialization with custom model deployment."""
        with patch("agent_framework_adapter.AzureAIAgent"):
            agent = EventKitAgentFramework(
                settings=foundry_settings,
                model_deployment="gpt-35-turbo"
            )
            
            assert agent.model_deployment == "gpt-35-turbo"


@pytest.mark.foundry
@pytest.mark.asyncio
class TestAgentFrameworkRun:
    """Test Agent Framework run method."""
    
    async def test_run_with_recommendation_query(self, foundry_settings):
        """Test running agent with recommendation query."""
        with patch("agent_framework_adapter.AzureAIAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent.run = AsyncMock(return_value="Here are your sessions...")
            mock_agent_class.return_value = mock_agent
            
            agent = EventKitAgentFramework(settings=foundry_settings)
            response = await agent.run("recommend sessions about AI agents")
            
            assert response is not None
            assert mock_agent.run.called
    
    async def test_run_with_explanation_query(self, foundry_settings):
        """Test running agent with explanation query."""
        with patch("agent_framework_adapter.AzureAIAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent.run = AsyncMock(return_value="This session matches because...")
            mock_agent_class.return_value = mock_agent
            
            agent = EventKitAgentFramework(settings=foundry_settings)
            response = await agent.run('explain session "AI Safety" for interests safety')
            
            assert response is not None
            assert mock_agent.run.called
    
    async def test_run_handles_errors(self, foundry_settings):
        """Test error handling in run method."""
        with patch("agent_framework_adapter.AzureAIAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent.run = AsyncMock(side_effect=Exception("API error"))
            mock_agent_class.return_value = mock_agent
            
            agent = EventKitAgentFramework(settings=foundry_settings)
            
            with pytest.raises(Exception):
                await agent.run("recommend sessions")


@pytest.mark.foundry
@pytest.mark.asyncio
class TestAgentFrameworkStream:
    """Test Agent Framework streaming responses."""
    
    async def test_stream_returns_chunks(self, foundry_settings):
        """Test streaming response chunks."""
        with patch("agent_framework_adapter.AzureAIAgent") as mock_agent_class:
            mock_agent = Mock()
            
            async def mock_stream(query):
                yield "Chunk 1"
                yield "Chunk 2"
                yield "Chunk 3"
            
            mock_agent.stream = mock_stream
            mock_agent_class.return_value = mock_agent
            
            agent = EventKitAgentFramework(settings=foundry_settings)
            chunks = []
            
            async for chunk in agent.stream("recommend sessions"):
                chunks.append(chunk)
            
            assert len(chunks) == 3
            assert "Chunk 1" in chunks


@pytest.mark.foundry
class TestAgentFrameworkTools:
    """Test Agent Framework tool integration."""
    
    def test_tool_recommend_sessions_defined(self, foundry_settings):
        """Test recommend_sessions tool is defined."""
        with patch("agent_framework_adapter.AzureAIAgent"):
            agent = EventKitAgentFramework(settings=foundry_settings)
            
            # Verify tool methods exist
            assert hasattr(agent, "_tool_recommend_sessions")
    
    def test_tool_explain_session_defined(self, foundry_settings):
        """Test explain_session tool is defined."""
        with patch("agent_framework_adapter.AzureAIAgent"):
            agent = EventKitAgentFramework(settings=foundry_settings)
            
            assert hasattr(agent, "_tool_explain_session")
    
    def test_tool_export_itinerary_defined(self, foundry_settings):
        """Test export_itinerary tool is defined."""
        with patch("agent_framework_adapter.AzureAIAgent"):
            agent = EventKitAgentFramework(settings=foundry_settings)
            
            assert hasattr(agent, "_tool_export_itinerary")
    
    def test_tool_recommend_calls_core_function(self, foundry_settings, sample_manifest):
        """Test that tool calls core recommend function."""
        with patch("agent_framework_adapter.AzureAIAgent"):
            with patch("agent_framework_adapter.recommend") as mock_recommend:
                mock_recommend.return_value = {
                    "sessions": [{"id": "1", "title": "Test"}],
                    "scoring": []
                }
                
                agent = EventKitAgentFramework(settings=foundry_settings)
                result = agent._tool_recommend_sessions("agents", 3)
                
                assert mock_recommend.called
                assert result is not None


@pytest.mark.foundry
class TestAgentFrameworkAzureIntegration:
    """Test Azure AI Project integration."""
    
    def test_uses_default_azure_credential(self, foundry_settings):
        """Test that agent uses DefaultAzureCredential."""
        with patch("agent_framework_adapter.DefaultAzureCredential") as mock_cred:
            with patch("agent_framework_adapter.AzureAIAgent"):
                EventKitAgentFramework(settings=foundry_settings)
                
                # Should create credential
                assert mock_cred.called
    
    def test_connects_to_foundry_endpoint(self, foundry_settings):
        """Test connection to Foundry project endpoint."""
        with patch("agent_framework_adapter.AzureAIAgent") as mock_agent_class:
            agent = EventKitAgentFramework(settings=foundry_settings)
            
            # Verify endpoint configuration
            assert agent.project_endpoint == foundry_settings.foundry_project_endpoint
