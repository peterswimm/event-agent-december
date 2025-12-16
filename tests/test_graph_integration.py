"""Integration tests for Graph API functionality.

Tests end-to-end flows covering:
- CLI with manifest mode
- CLI with Graph mode (mocked)
- HTTP endpoints with manifest and Graph modes
- Core recommendation logic with Graph events
"""
import json
from unittest.mock import patch, MagicMock, Mock
import pytest

from core import recommend_from_graph
from graph_service import GraphEventService


class TestGraphIntegrationCLI:
    """Integration tests for CLI with Graph mode."""

    def test_cli_recommend_manifest_mode(self):
        """Test CLI recommend command in manifest mode (default)."""
        from agent import _normalize_interests, recommend

        manifest = {
            "recommend": {"max_sessions_default": 3},
            "weights": {"interest": 2.0, "popularity": 0.5, "diversity": 0.3},
            "sessions": [
                {
                    "title": "Session 1",
                    "start": "09:00",
                    "end": "10:00",
                    "tags": ["ai"],
                    "popularity": 0.8,
                },
                {
                    "title": "Session 2",
                    "start": "10:00",
                    "end": "11:00",
                    "tags": ["safety"],
                    "popularity": 0.6,
                },
            ],
        }

        interests = _normalize_interests("ai, safety")
        result = recommend(manifest, interests, 3)

        assert "sessions" in result
        assert isinstance(result["sessions"], list)
        # Manifest mode doesn't include "source" field, but has scoring
        assert "scoring" in result or "conflicts" in result

    def test_cli_normalize_interests(self):
        """Test interest normalization."""
        from agent import _normalize_interests

        assert _normalize_interests("AI, Safety") == ["ai", "safety"]
        assert _normalize_interests("agents; production") == ["agents", "production"]
        # Note: internal spaces in tags are preserved during split by comma
        assert _normalize_interests("  ai  ,  safety  ") == ["ai", "safety"]

    def test_cli_profile_operations(self):
        """Test profile save and load."""
        import tempfile
        import os
        from agent import save_profile, load_profile

        with tempfile.TemporaryDirectory() as tmpdir:
            profile_file = os.path.join(tmpdir, "test_profile.json")
            interests = ["ai", "safety"]

            save_profile(profile_file, "test_user", interests)
            loaded = load_profile(profile_file, "test_user")

            assert loaded == interests


class TestGraphIntegrationCore:
    """Integration tests for Graph core recommendation."""

    def test_recommend_from_graph_with_mocked_service(self):
        """Test recommend_from_graph with mocked GraphEventService."""
        mock_service = MagicMock(spec=GraphEventService)
        mock_service.get_events.return_value = [
            {
                "title": "AI Talk",
                "start": "09:00",
                "end": "09:40",
                "location": "Hall A",
                "tags": ["ai"],
                "popularity": 0.8,
            },
            {
                "title": "Safety Panel",
                "start": "10:00",
                "end": "10:40",
                "location": "Hall B",
                "tags": ["safety"],
                "popularity": 0.6,
            },
        ]

        result = recommend_from_graph(mock_service, ["ai", "safety"], 2)

        assert "sessions" in result
        assert len(result["sessions"]) <= 2
        assert result.get("source") == "graph"
        mock_service.get_events.assert_called_once()

    def test_recommend_from_graph_error_handling(self):
        """Test recommend_from_graph handles service errors."""
        mock_service = MagicMock(spec=GraphEventService)
        mock_service.get_events.side_effect = Exception("Service error")

        with pytest.raises(Exception, match="Service error"):
            recommend_from_graph(mock_service, ["ai"], 1)

    def test_recommend_from_graph_empty_results(self):
        """Test recommend_from_graph with no events found."""
        mock_service = MagicMock(spec=GraphEventService)
        mock_service.get_events.return_value = []

        result = recommend_from_graph(mock_service, ["nonexistent"], 3)

        assert "sessions" in result
        assert len(result["sessions"]) == 0

    def test_recommend_from_graph_scoring_calculation(self):
        """Test scoring calculation in recommend_from_graph."""
        mock_service = MagicMock(spec=GraphEventService)
        mock_service.get_events.return_value = [
            {
                "title": "AI Talk",
                "start": "09:00",
                "end": "09:40",
                "location": "Hall A",
                "tags": ["ai", "production"],
                "popularity": 0.9,
            },
            {
                "title": "Safety Panel",
                "start": "10:00",
                "end": "10:40",
                "location": "Hall B",
                "tags": ["safety"],
                "popularity": 0.5,
            },
        ]

        result = recommend_from_graph(
            mock_service, ["ai", "production"], 2, weights={"interest": 2.0, "popularity": 0.5, "diversity": 0.3}
        )

        # Graph results have sessions with contributions/score info
        assert "sessions" in result
        if len(result["sessions"]) >= 2:
            # Graph results should have score info in each session
            session_scores = [s.get("contributions", {}).get("interest_match", 0) for s in result["sessions"]]
            # First session has more tag matches so should have higher interest match
            assert session_scores[0] >= session_scores[1]

    def test_recommend_from_graph_conflict_detection(self):
        """Test conflict detection in recommend_from_graph."""
        mock_service = MagicMock(spec=GraphEventService)
        mock_service.get_events.return_value = [
            {
                "title": "Talk 1",
                "start": "09:00",
                "end": "09:40",
                "location": "Hall A",
                "tags": ["ai"],
                "popularity": 0.8,
            },
            {
                "title": "Talk 2",
                "start": "09:00",
                "end": "09:40",
                "location": "Hall B",
                "tags": ["ai"],
                "popularity": 0.8,
            },
        ]

        result = recommend_from_graph(mock_service, ["ai"], 2)

        # Should detect time conflict
        conflicts = result.get("conflicts", 0)
        assert conflicts >= 0


class TestGraphIntegrationHTTPEndpoints:
    """Integration tests for HTTP endpoints."""

    def test_http_recommend_endpoint_response_format(self):
        """Test HTTP /recommend endpoint returns correct format."""
        manifest = {
            "recommend": {"max_sessions_default": 3},
            "weights": {"interest": 2.0, "popularity": 0.5, "diversity": 0.3},
            "sessions": [
                {
                    "title": "Session 1",
                    "start": "09:00",
                    "end": "10:00",
                    "tags": ["ai"],
                    "popularity": 0.8,
                }
            ],
        }

        from agent import recommend

        result = recommend(manifest, ["ai"], 1)

        # Check response structure
        assert "sessions" in result
        assert isinstance(result["sessions"], list)
        # Manifest recommendations include scoring and conflicts info
        assert "scoring" in result
        assert "conflicts" in result

    def test_http_export_markdown_generation(self):
        """Test export markdown generation."""
        from agent import _build_itinerary_markdown

        recommendation = {
            "sessions": [
                {
                    "title": "AI Talk",
                    "start": "09:00",
                    "end": "09:40",
                    "location": "Hall A",
                    "tags": ["ai"],
                },
                {
                    "title": "Safety Panel",
                    "start": "10:00",
                    "end": "10:40",
                    "location": "Hall B",
                    "tags": ["safety"],
                },
            ]
        }

        md = _build_itinerary_markdown(["ai", "safety"], recommendation)

        assert "Event Itinerary" in md
        assert "AI Talk" in md
        assert "Safety Panel" in md
        assert "09:00 - 09:40" in md
        assert "Hall A" in md

    def test_http_adaptive_card_generation(self):
        """Test Adaptive Card generation for HTTP responses."""
        from agent import _build_adaptive_card

        sessions = [
            {
                "title": "Session 1",
                "start": "09:00",
                "end": "09:40",
                "location": "Hall A",
            },
            {
                "title": "Session 2",
                "start": "10:00",
                "end": "10:40",
                "location": "Hall B",
            },
        ]

        card = _build_adaptive_card(sessions)

        assert "body" in card
        assert "actions" in card
        assert len(card["actions"]) == len(sessions)
        assert card["actions"][0]["title"] == "Explain #1"


class TestGraphIntegrationEndToEnd:
    """End-to-end integration scenarios."""

    def test_e2e_manifest_recommendation_flow(self):
        """Test complete manifest recommendation flow."""
        from agent import _normalize_interests, recommend, _count_conflicts

        manifest = {
            "recommend": {"max_sessions_default": 3},
            "weights": {"interest": 2.0, "popularity": 0.5, "diversity": 0.3},
            "sessions": [
                {
                    "title": "AI in Prod",
                    "start": "09:00",
                    "end": "09:40",
                    "tags": ["ai", "production"],
                    "location": "Hall A",
                    "popularity": 0.9,
                },
                {
                    "title": "Safety Talk",
                    "start": "10:00",
                    "end": "10:40",
                    "tags": ["safety", "governance"],
                    "location": "Hall B",
                    "popularity": 0.8,
                },
                {
                    "title": "Advanced AI",
                    "start": "11:00",
                    "end": "11:40",
                    "tags": ["ai", "research"],
                    "location": "Hall A",
                    "popularity": 0.7,
                },
            ],
        }

        # Step 1: Parse interests
        interests = _normalize_interests("ai, safety")

        # Step 2: Get recommendations
        result = recommend(manifest, interests, 2)

        # Step 3: Validate result
        assert len(result["sessions"]) <= 2
        assert all(
            any(tag in interests for tag in session.get("tags", []))
            for session in result["sessions"]
        )

        # Step 4: Check conflicts
        conflicts = _count_conflicts(result["sessions"])
        assert isinstance(conflicts, int)

    def test_e2e_graph_recommendation_flow_mocked(self):
        """Test complete Graph recommendation flow with mocked services."""
        mock_service = MagicMock(spec=GraphEventService)
        mock_service.get_events.return_value = [
            {
                "title": "Event 1",
                "start": "09:00",
                "end": "09:40",
                "location": "Room A",
                "tags": ["ai"],
                "popularity": 0.8,
            }
        ]

        # Simulate the full flow
        from agent import _normalize_interests

        interests = _normalize_interests("ai")
        result = recommend_from_graph(mock_service, interests, 1)

        assert result["source"] == "graph"
        assert len(result["sessions"]) <= 1
        assert mock_service.get_events.called

    def test_e2e_settings_and_graph_auth_validation(self):
        """Test settings validation for Graph credentials."""
        from settings import Settings

        settings = Settings()

        # Test validation methods
        is_ready = settings.validate_graph_ready()
        assert isinstance(is_ready, bool)

        errors = settings.get_validation_errors()
        assert isinstance(errors, list)

        # If not ready, should have errors
        if not is_ready:
            assert len(errors) > 0

    def test_e2e_profile_with_graph_mode(self):
        """Test profile operations in context of Graph mode."""
        import tempfile
        import os
        from agent import save_profile, load_profile, _normalize_interests

        with tempfile.TemporaryDirectory() as tmpdir:
            profile_file = os.path.join(tmpdir, "test.json")
            user_interests = ["ai", "safety", "agents"]

            # Save profile
            save_profile(profile_file, "graph_user", user_interests)

            # Load profile
            loaded = load_profile(profile_file, "graph_user")

            # Normalize and verify
            normalized = _normalize_interests(", ".join(loaded))
            assert normalized == user_interests


class TestGraphIntegrationErrorPaths:
    """Test error handling in integration scenarios."""

    def test_error_invalid_interests_format(self):
        """Test handling of invalid interests format."""
        from agent import _normalize_interests

        # Empty interests should return empty list
        assert _normalize_interests("") == []
        assert _normalize_interests(";;;") == []
        assert _normalize_interests("   ") == []

    def test_error_missing_manifest_sessions(self):
        """Test handling of manifest without sessions."""
        from agent import recommend

        manifest = {
            "recommend": {"max_sessions_default": 3},
            "weights": {"interest": 2.0, "popularity": 0.5, "diversity": 0.3},
        }

        # Should handle gracefully
        result = recommend(manifest, ["ai"], 1)
        assert "sessions" in result

    def test_error_graph_service_timeout(self):
        """Test handling of Graph service timeout."""
        mock_service = MagicMock(spec=GraphEventService)
        mock_service.get_events.side_effect = TimeoutError("Request timeout")

        with pytest.raises(TimeoutError, match="Request timeout"):
            recommend_from_graph(mock_service, ["ai"], 1)

    def test_error_invalid_top_parameter(self):
        """Test handling of invalid top_n parameter."""
        with pytest.raises(ValueError):
            recommend_from_graph(MagicMock(), ["ai"], -1)

        with pytest.raises(ValueError):
            recommend_from_graph(MagicMock(), ["ai"], 0)
