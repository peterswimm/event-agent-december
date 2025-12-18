"""
Tests for Bot Framework Activity Handler

Tests Teams bot command parsing, message handling, and adaptive card generation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Skip all tests if bot framework not available
pytest.importorskip("botbuilder.core", reason="Bot Framework SDK not installed")

from bot_handler import EventKitBotHandler, create_bot_handler


@pytest.mark.bot
class TestBotHandlerInitialization:
    """Test bot handler initialization."""
    
    def test_bot_handler_creates_with_defaults(self):
        """Test that bot handler initializes with default values."""
        handler = EventKitBotHandler()
        
        assert handler.conversation_state is None
        assert handler.user_state is None
        assert handler.agent is not None
    
    def test_bot_handler_with_custom_agent(self):
        """Test bot handler with custom agent."""
        mock_agent = Mock()
        handler = EventKitBotHandler(agent=mock_agent)
        
        assert handler.agent is mock_agent
    
    def test_create_bot_handler_factory(self):
        """Test factory function creates handler."""
        handler = create_bot_handler()
        
        assert isinstance(handler, EventKitBotHandler)


@pytest.mark.bot
class TestCommandParsing:
    """Test command parsing logic."""
    
    def test_parse_recommend_command(self):
        """Test parsing recommend command."""
        handler = EventKitBotHandler()
        command, params = handler._parse_message("@bot recommend agents, ai safety --top 5")
        
        assert command == "recommend"
        assert params["interests"] == "agents, ai safety"
        assert params["top"] == "5"
    
    def test_parse_explain_command(self):
        """Test parsing explain command."""
        handler = EventKitBotHandler()
        command, params = handler._parse_message('@bot explain "AI Safety" --interests safety')
        
        assert command == "explain"
        assert params["session"] == "AI Safety"
        assert params["interests"] == "safety"
    
    def test_parse_export_command(self):
        """Test parsing export command."""
        handler = EventKitBotHandler()
        command, params = handler._parse_message("@bot export agents --profile my_profile")
        
        assert command == "export"
        assert params["interests"] == "agents"
        assert params["profile"] == "my_profile"
    
    def test_parse_help_command(self):
        """Test parsing help command."""
        handler = EventKitBotHandler()
        command, params = handler._parse_message("@bot help")
        
        assert command == "help"
        assert params == {}
    
    def test_parse_command_without_bot_mention(self):
        """Test parsing command without @bot prefix."""
        handler = EventKitBotHandler()
        command, params = handler._parse_message("recommend agents --top 3")
        
        # Should still parse if bot mention not required
        assert command in ["recommend", "unknown"]


@pytest.mark.bot
@pytest.mark.asyncio
class TestMessageHandling:
    """Test message activity handling."""
    
    async def test_on_message_activity_with_help(self, mock_turn_context):
        """Test help command handling."""
        mock_turn_context.activity.text = "@bot help"
        handler = EventKitBotHandler()
        
        await handler.on_message_activity(mock_turn_context)
        
        # Verify response sent
        assert mock_turn_context.send_activity.called
    
    async def test_on_message_activity_with_recommend(self, mock_turn_context):
        """Test recommend command handling."""
        mock_turn_context.activity.text = "@bot recommend agents --top 3"
        handler = EventKitBotHandler()
        
        # Mock agent response
        handler.agent.handle_tool_call = Mock(return_value={
            "sessions": [
                {"id": "1", "title": "Test Session", "score": 0.9}
            ],
            "markdown": "# Results"
        })
        
        await handler.on_message_activity(mock_turn_context)
        
        # Verify agent called
        assert handler.agent.handle_tool_call.called
        assert mock_turn_context.send_activity.called
    
    async def test_on_message_activity_handles_errors(self, mock_turn_context):
        """Test error handling in message processing."""
        mock_turn_context.activity.text = "@bot recommend agents"
        handler = EventKitBotHandler()
        
        # Mock agent to raise error
        handler.agent.handle_tool_call = Mock(side_effect=Exception("Test error"))
        
        await handler.on_message_activity(mock_turn_context)
        
        # Should send error message
        assert mock_turn_context.send_activity.called


@pytest.mark.bot
class TestAdaptiveCardGeneration:
    """Test adaptive card creation."""
    
    def test_create_recommendations_card(self):
        """Test recommendations card generation."""
        handler = EventKitBotHandler()
        
        result = {
            "sessions": [
                {
                    "id": "1",
                    "title": "AI Agents",
                    "category": "AI",
                    "description": "Learn about agents",
                    "score": 0.95
                }
            ],
            "total_count": 1
        }
        
        card = handler._create_recommendations_card(result)
        
        # Verify card structure
        assert card is not None
    
    def test_create_empty_recommendations_card(self):
        """Test card generation with no results."""
        handler = EventKitBotHandler()
        
        result = {"sessions": [], "total_count": 0}
        
        card = handler._create_recommendations_card(result)
        
        assert card is not None


@pytest.mark.bot
@pytest.mark.asyncio
class TestReactionHandling:
    """Test message reaction handling."""
    
    async def test_on_message_reaction_activity(self, mock_turn_context):
        """Test reaction activity handling."""
        mock_turn_context.activity.reaction = {"type": "like"}
        handler = EventKitBotHandler()
        
        await handler.on_message_reaction_activity(mock_turn_context)
        
        # Should handle without error
        assert True


@pytest.mark.bot
@pytest.mark.asyncio
class TestMemberHandling:
    """Test member add/remove handling."""
    
    async def test_on_members_added(self, mock_turn_context):
        """Test member added greeting."""
        handler = EventKitBotHandler()
        members = [MagicMock(name="Test User", id="user-123")]
        
        await handler.on_members_added_activity(members, mock_turn_context)
        
        # Should send greeting
        assert mock_turn_context.send_activity.called
    
    async def test_on_members_removed(self, mock_turn_context):
        """Test member removed handling."""
        handler = EventKitBotHandler()
        members = [MagicMock(name="Test User", id="user-123")]
        
        await handler.on_members_removed_activity(members, mock_turn_context)
        
        # Should handle without error
        assert True


@pytest.mark.bot
class TestNaturalLanguageProcessing:
    """Test natural language query handling."""
    
    def test_extract_interests_from_message(self):
        """Test extracting interests from natural language."""
        handler = EventKitBotHandler()
        
        message = "I'm interested in AI agents and machine learning"
        interests = handler._extract_interests(message)
        
        # Should extract relevant keywords
        assert interests is not None
        assert len(interests) > 0
