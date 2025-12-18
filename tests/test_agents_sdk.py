"""
Tests for Azure AI Projects SDK Adapter

Tests the EventKitAgent adapter for tool call handling,
Teams/Copilot integration, and error handling.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from agents_sdk_adapter import EventKitAgent, create_agent
from errors import InvalidInputError, EventKitError
from settings import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = Mock(spec=Settings)
    settings.graph_enabled = False
    return settings


@pytest.fixture
def mock_telemetry():
    """Create mock telemetry client."""
    telemetry = Mock()
    telemetry.log = Mock()
    return telemetry


@pytest.fixture
def agent(mock_settings, mock_telemetry, tmp_path):
    """Create EventKitAgent instance with test manifest."""
    manifest_path = tmp_path / "test_agent.json"
    
    # Create test manifest with required fields
    manifest = {
        "sessions": [
            {
                "id": "session1",
                "title": "Building AI Agents",
                "category": "AI/ML",
                "description": "Learn to build intelligent agents",
                "keywords": ["agents", "ai", "automation"],
                "popularity": 100
            },
            {
                "id": "session2",
                "title": "AI Safety Fundamentals",
                "category": "Safety",
                "description": "Understanding AI safety principles",
                "keywords": ["safety", "ethics", "alignment"],
                "popularity": 80
            },
            {
                "id": "session3",
                "title": "Machine Learning at Scale",
                "category": "ML",
                "description": "Scaling ML systems",
                "keywords": ["machine learning", "scalability", "systems"],
                "popularity": 90
            }
        ],
        "weights": {
            "interest": 2.0,
            "popularity": 0.5,
            "diversity": 0.3
        }
    }
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f)
    
    return EventKitAgent(
        settings=mock_settings,
        telemetry=mock_telemetry,
        manifest_path=str(manifest_path)
    )


class TestEventKitAgentInitialization:
    """Test agent initialization and setup."""
    
    def test_agent_loads_manifest(self, agent):
        """Test that agent loads manifest successfully."""
        assert len(agent.manifest["sessions"]) == 3
        assert agent.manifest["sessions"][0]["title"] == "Building AI Agents"
    
    def test_agent_registers_tool_handlers(self, agent):
        """Test that agent registers all tool handlers."""
        assert "recommend_sessions" in agent.tool_handlers
        assert "explain_session" in agent.tool_handlers
        assert "export_itinerary" in agent.tool_handlers
    
    def test_agent_missing_manifest_returns_empty(self, mock_settings, mock_telemetry):
        """Test that missing manifest returns empty sessions."""
        agent = EventKitAgent(
            settings=mock_settings,
            telemetry=mock_telemetry,
            manifest_path="nonexistent.json"
        )
        assert agent.manifest["sessions"] == []
    
    def test_create_agent_convenience_function(self, tmp_path):
        """Test convenience function for creating agent."""
        manifest_path = tmp_path / "agent.json"
        manifest_path.write_text('{"sessions": []}')
        
        agent = create_agent(manifest_path=str(manifest_path))
        assert isinstance(agent, EventKitAgent)
        assert agent.manifest["sessions"] == []


class TestRecommendSessionsTool:
    """Test recommend_sessions tool call handling."""
    
    def test_recommend_basic(self, agent):
        """Test basic recommendation request."""
        result = agent.handle_tool_call("recommend_sessions", {
            "interests": "agents, ai",
            "top": 2
        })
        
        assert "sessions" in result
        assert len(result["sessions"]) <= 2
        assert "markdown" in result
        assert "total_count" in result
        
        # Check first session has expected fields
        session = result["sessions"][0]
        assert "title" in session
        assert "score" in session
        assert "matched_interests" in session
    
    def test_recommend_single_interest(self, agent):
        """Test recommendation with single interest."""
        result = agent.handle_tool_call("recommend_sessions", {
            "interests": "safety"
        })
        
        assert len(result["sessions"]) > 0
        # "AI Safety Fundamentals" should rank highly
        titles = [s["title"] for s in result["sessions"]]
        assert "AI Safety Fundamentals" in titles
    
    def test_recommend_default_top(self, agent):
        """Test recommendation with default top parameter."""
        result = agent.handle_tool_call("recommend_sessions", {
            "interests": "ai, machine learning"
        })
        
        assert len(result["sessions"]) <= 5  # default top=5
    
    def test_recommend_missing_interests_raises_error(self, agent):
        """Test that missing interests raises InvalidInputError."""
        with pytest.raises(InvalidInputError, match="interests"):
            agent.handle_tool_call("recommend_sessions", {})
    
    def test_recommend_empty_interests_raises_error(self, agent):
        """Test that empty interests raises InvalidInputError."""
        with pytest.raises(InvalidInputError, match="interests"):
            agent.handle_tool_call("recommend_sessions", {
                "interests": ""
            })
    
    def test_recommend_whitespace_only_interests_raises_error(self, agent):
        """Test that whitespace-only interests raises error."""
        with pytest.raises(InvalidInputError, match="At least one interest"):
            agent.handle_tool_call("recommend_sessions", {
                "interests": "  ,  ,  "
            })
    
    def test_recommend_with_correlation_id(self, agent, mock_telemetry):
        """Test recommendation with correlation ID logging."""
        result = agent.handle_tool_call("recommend_sessions", {
            "interests": "agents",
            "correlation_id": "test-123"
        })
        
        assert len(result["sessions"]) > 0
        # Telemetry should be logged with correlation ID
        mock_telemetry.log.assert_called_once()
        call_args = mock_telemetry.log.call_args[1]
        assert call_args["correlation_id"] == "test-123"
    
    def test_recommend_markdown_format(self, agent):
        """Test that recommendation markdown is properly formatted."""
        result = agent.handle_tool_call("recommend_sessions", {
            "interests": "agents",
            "top": 1
        })
        
        markdown = result["markdown"]
        assert "# Recommended Sessions" in markdown
        assert "Building AI Agents" in markdown
        assert "**Category**" in markdown
        assert "**Score**" in markdown


class TestExplainSessionTool:
    """Test explain_session tool call handling."""
    
    def test_explain_basic(self, agent):
        """Test basic explanation request."""
        result = agent.handle_tool_call("explain_session", {
            "session_title": "Building AI Agents",
            "interests": "agents, automation"
        })
        
        assert "session" in result
        assert result["session"] == "Building AI Agents"
        assert "explanation" in result
        assert "matched_keywords" in result
        assert "relevance_score" in result
        assert "markdown" in result
    
    def test_explain_missing_session_title(self, agent):
        """Test that missing session_title raises error."""
        with pytest.raises(InvalidInputError, match="session_title"):
            agent.handle_tool_call("explain_session", {
                "interests": "agents"
            })
    
    def test_explain_missing_interests(self, agent):
        """Test that missing interests raises error."""
        with pytest.raises(InvalidInputError, match="interests"):
            agent.handle_tool_call("explain_session", {
                "session_title": "Building AI Agents"
            })
    
    def test_explain_markdown_format(self, agent):
        """Test that explanation markdown is properly formatted."""
        result = agent.handle_tool_call("explain_session", {
            "session_title": "AI Safety Fundamentals",
            "interests": "safety, ethics"
        })
        
        markdown = result["markdown"]
        assert "# Session Explanation" in markdown
        assert "AI Safety Fundamentals" in markdown
        assert "## Matched Keywords" in markdown
        assert "**Relevance Score**" in markdown


class TestExportItineraryTool:
    """Test export_itinerary tool call handling."""
    
    def test_export_basic(self, agent):
        """Test basic itinerary export."""
        result = agent.handle_tool_call("export_itinerary", {
            "interests": "agents, ai, safety"
        })
        
        assert "markdown" in result
        assert "sessions_count" in result
        assert result["sessions_count"] > 0
        assert "profile_saved" in result
        assert result["profile_saved"] is False  # No profile_name provided
    
    def test_export_with_profile_name(self, agent, tmp_path):
        """Test export with profile saving."""
        # Mock home directory to tmp_path
        with patch("pathlib.Path.home", return_value=tmp_path):
            result = agent.handle_tool_call("export_itinerary", {
                "interests": "agents, ai",
                "profile_name": "my_profile"
            })
            
            assert result["profile_saved"] is True
            assert result["profile_name"] == "my_profile"
            
            # Verify profile file was created
            profile_file = tmp_path / ".event_agent_profiles.json"
            assert profile_file.exists()
            
            # Verify profile content
            with open(profile_file, 'r') as f:
                profiles = json.load(f)
            
            assert "my_profile" in profiles
            assert profiles["my_profile"]["interests"] == ["agents", "ai"]
    
    def test_export_missing_interests(self, agent):
        """Test that missing interests raises error."""
        with pytest.raises(InvalidInputError, match="interests"):
            agent.handle_tool_call("export_itinerary", {})
    
    def test_export_markdown_format(self, agent):
        """Test that itinerary markdown is properly formatted."""
        result = agent.handle_tool_call("export_itinerary", {
            "interests": "agents, safety"
        })
        
        markdown = result["markdown"]
        assert "# My Personalized Event Itinerary" in markdown
        assert "**Interests**:" in markdown
        assert "agents, safety" in markdown
        assert "**Generated**:" in markdown
        assert "---" in markdown  # Section dividers


class TestToolCallRouting:
    """Test tool call routing and error handling."""
    
    def test_unknown_tool_raises_error(self, agent):
        """Test that unknown tool name raises InvalidInputError."""
        with pytest.raises(InvalidInputError, match="Unknown tool"):
            agent.handle_tool_call("nonexistent_tool", {})
    
    def test_tool_execution_error_wraps_exception(self, agent):
        """Test that tool execution errors are wrapped in EventKitError."""
        # Patch recommend to raise an exception
        with patch("agents_sdk_adapter.recommend", side_effect=ValueError("Test error")):
            with pytest.raises(EventKitError, match="Tool execution failed"):
                agent.handle_tool_call("recommend_sessions", {
                    "interests": "agents"
                })


class TestAgentCapabilities:
    """Test agent capability introspection."""
    
    def test_get_capabilities_returns_list(self, agent):
        """Test that get_capabilities returns capability list."""
        capabilities = agent.get_capabilities()
        
        assert len(capabilities) == 3
        assert any(c["name"] == "recommend_sessions" for c in capabilities)
        assert any(c["name"] == "explain_session" for c in capabilities)
        assert any(c["name"] == "export_itinerary" for c in capabilities)
    
    def test_capabilities_have_required_fields(self, agent):
        """Test that capabilities have name, description, and parameters."""
        capabilities = agent.get_capabilities()
        
        for cap in capabilities:
            assert "name" in cap
            assert "description" in cap
            assert "parameters" in cap
            assert isinstance(cap["parameters"], list)


class TestMarkdownFormatting:
    """Test markdown output formatting."""
    
    def test_recommendations_markdown_structure(self, agent):
        """Test recommendations markdown has proper structure."""
        sessions = [
            {
                "title": "Test Session 1",
                "category": "Testing",
                "score": 0.95,
                "matched_interests": ["test", "demo"],
                "description": "A test session"
            },
            {
                "title": "Test Session 2",
                "category": "Testing",
                "score": 0.85,
                "matched_interests": ["demo"]
            }
        ]
        
        markdown = agent._format_recommendations_markdown(sessions)
        
        assert "# Recommended Sessions" in markdown
        assert "## 1. Test Session 1" in markdown
        assert "## 2. Test Session 2" in markdown
        assert "**Score**: 0.95" in markdown
        assert "**Matched Interests**: test, demo" in markdown
    
    def test_explanation_markdown_structure(self, agent):
        """Test explanation markdown has proper structure."""
        result = {
            "session": "Test Session",
            "explanation": "This session matches your interests because...",
            "matched_keywords": ["test", "demo", "example"],
            "relevance_score": 0.88
        }
        
        markdown = agent._format_explanation_markdown(result)
        
        assert "# Session Explanation: Test Session" in markdown
        assert "This session matches your interests" in markdown
        assert "## Matched Keywords" in markdown
        assert "- test" in markdown
        assert "- demo" in markdown
        assert "**Relevance Score**: 0.88" in markdown
    
    def test_itinerary_markdown_structure(self, agent):
        """Test itinerary markdown has proper structure."""
        recommendations = {
            "sessions": [
                {
                    "title": "Session 1",
                    "category": "Cat1",
                    "description": "Description 1"
                }
            ],
            "scoring": [
                {
                    "score": 0.9,
                    "matched_interests": ["interest1"]
                }
            ],
            "conflicts": 2
        }
        
        markdown = agent._generate_itinerary_markdown(
            recommendations,
            ["interest1", "interest2"]
        )
        
        assert "# My Personalized Event Itinerary" in markdown
        assert "**Interests**: interest1, interest2" in markdown
        assert "## 1. Session 1" in markdown
        assert "**Relevance Score**: 0.90" in markdown
        assert "⚠️ **Note**: 2 scheduling conflicts" in markdown


class TestProfileManagement:
    """Test profile saving and loading."""
    
    def test_save_profile_creates_file(self, agent, tmp_path):
        """Test that save_profile creates profile file."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            success = agent._save_profile("test_profile", ["interest1", "interest2"])
            
            assert success is True
            
            profile_file = tmp_path / ".event_agent_profiles.json"
            assert profile_file.exists()
    
    def test_save_profile_preserves_existing_profiles(self, agent, tmp_path):
        """Test that saving a profile preserves existing profiles."""
        profile_file = tmp_path / ".event_agent_profiles.json"
        
        # Create existing profile
        existing = {
            "existing_profile": {
                "interests": ["existing"],
                "updated": "2024-01-01T00:00:00"
            }
        }
        with open(profile_file, 'w') as f:
            json.dump(existing, f)
        
        # Save new profile
        with patch("pathlib.Path.home", return_value=tmp_path):
            success = agent._save_profile("new_profile", ["new"])
            
            assert success is True
            
            # Verify both profiles exist
            with open(profile_file, 'r') as f:
                profiles = json.load(f)
            
            assert "existing_profile" in profiles
            assert "new_profile" in profiles
            assert profiles["existing_profile"]["interests"] == ["existing"]
            assert profiles["new_profile"]["interests"] == ["new"]
    
    def test_save_profile_updates_existing_profile(self, agent, tmp_path):
        """Test that saving updates existing profile."""
        profile_file = tmp_path / ".event_agent_profiles.json"
        
        # Create initial profile
        with patch("pathlib.Path.home", return_value=tmp_path):
            agent._save_profile("test", ["old_interest"])
            agent._save_profile("test", ["new_interest"])
            
            # Verify profile was updated
            with open(profile_file, 'r') as f:
                profiles = json.load(f)
            
            assert profiles["test"]["interests"] == ["new_interest"]
    
    def test_save_profile_handles_errors_gracefully(self, agent):
        """Test that save_profile handles errors and returns False."""
        # Try to save to invalid path
        with patch("pathlib.Path.home", side_effect=PermissionError("No access")):
            success = agent._save_profile("test", ["interest"])
            
            assert success is False


class TestIntegrationScenarios:
    """Test complete integration scenarios."""
    
    def test_complete_workflow_recommend_explain_export(self, agent, tmp_path):
        """Test complete workflow: recommend -> explain -> export."""
        # 1. Get recommendations
        recommend_result = agent.handle_tool_call("recommend_sessions", {
            "interests": "agents, ai safety",
            "top": 3
        })
        
        assert len(recommend_result["sessions"]) > 0
        
        # 2. Explain first recommendation
        first_session = recommend_result["sessions"][0]["title"]
        explain_result = agent.handle_tool_call("explain_session", {
            "session_title": first_session,
            "interests": "agents, ai safety"
        })
        
        assert explain_result["session"] == first_session
        assert len(explain_result["matched_keywords"]) > 0
        
        # 3. Export itinerary with profile
        with patch("pathlib.Path.home", return_value=tmp_path):
            export_result = agent.handle_tool_call("export_itinerary", {
                "interests": "agents, ai safety",
                "profile_name": "integration_test"
            })
        
        assert export_result["sessions_count"] > 0
        assert export_result["profile_saved"] is True
        
        # Verify profile was saved
        profile_file = tmp_path / ".event_agent_profiles.json"
        assert profile_file.exists()
    
    def test_agent_handles_multiple_requests(self, agent):
        """Test that agent can handle multiple sequential requests."""
        for i in range(5):
            result = agent.handle_tool_call("recommend_sessions", {
                "interests": f"interest{i}",
                "top": 2
            })
            assert "sessions" in result
    
    def test_agent_maintains_state_across_calls(self, agent):
        """Test that agent maintains manifest state across calls."""
        result1 = agent.handle_tool_call("recommend_sessions", {
            "interests": "agents"
        })
        
        result2 = agent.handle_tool_call("recommend_sessions", {
            "interests": "agents"
        })
        
        # Both results should use same manifest
        assert len(result1["sessions"]) == len(result2["sessions"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
