"""Unit tests for Graph API recommendation function in core module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List

from core import recommend_from_graph


class TestRecommendFromGraphInitialization:
    """Tests for recommend_from_graph function initialization and validation."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock GraphEventService."""
        mock = Mock()
        mock.get_events.return_value = []
        return mock

    def test_empty_interests_raises_error(self, mock_graph_service):
        """Test that empty interests list raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            recommend_from_graph(mock_graph_service, [], 3)

        assert "At least one interest is required" in str(exc_info.value)

    def test_zero_top_raises_error(self, mock_graph_service):
        """Test that top <= 0 raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            recommend_from_graph(mock_graph_service, ["ai"], 0)

        assert "top must be a positive integer" in str(exc_info.value)

    def test_negative_top_raises_error(self, mock_graph_service):
        """Test that negative top raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            recommend_from_graph(mock_graph_service, ["ai"], -1)

        assert "top must be a positive integer" in str(exc_info.value)


class TestRecommendFromGraphBasicFunctionality:
    """Tests for basic recommendation functionality."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock GraphEventService."""
        mock = Mock()
        return mock

    @pytest.fixture
    def sample_sessions(self) -> List[Dict[str, Any]]:
        """Create sample sessions from Graph API."""
        return [
            {
                "id": "event1",
                "title": "AI Safety Workshop",
                "start": "10:00",
                "end": "11:00",
                "location": "Room A",
                "tags": ["ai safety", "workshop"],
                "popularity": 0.8,
            },
            {
                "id": "event2",
                "title": "Agents Deep Dive",
                "start": "11:15",
                "end": "12:15",
                "location": "Room B",
                "tags": ["agents", "deep dive"],
                "popularity": 0.9,
            },
            {
                "id": "event3",
                "title": "LLM Ethics",
                "start": "13:00",
                "end": "14:00",
                "location": "Room C",
                "tags": ["ai safety", "ethics"],
                "popularity": 0.7,
            },
        ]

    def test_recommend_no_sessions_found(self, mock_graph_service):
        """Test recommendation when no sessions are found."""
        mock_graph_service.get_events.return_value = []

        result = recommend_from_graph(mock_graph_service, ["ai"], 3)

        assert result["sessions"] == []
        assert result["scoring"] == []
        assert result["source"] == "graph"
        assert "message" in result

    def test_recommend_single_session(self, mock_graph_service, sample_sessions):
        """Test recommendation with single session."""
        mock_graph_service.get_events.return_value = sample_sessions[:1]

        result = recommend_from_graph(
            mock_graph_service, ["ai safety"], 3
        )

        assert len(result["sessions"]) == 1
        assert result["sessions"][0]["title"] == "AI Safety Workshop"
        assert result["source"] == "graph"
        assert len(result["scoring"]) == 1

    def test_recommend_multiple_sessions(self, mock_graph_service, sample_sessions):
        """Test recommendation with multiple sessions."""
        mock_graph_service.get_events.return_value = sample_sessions

        result = recommend_from_graph(
            mock_graph_service, ["ai safety", "agents"], 3
        )

        assert len(result["sessions"]) <= 3
        assert all("title" in s for s in result["sessions"])
        assert len(result["scoring"]) == len(result["sessions"])

    def test_recommend_respects_top_limit(self, mock_graph_service, sample_sessions):
        """Test that top parameter limits results."""
        mock_graph_service.get_events.return_value = sample_sessions

        result = recommend_from_graph(
            mock_graph_service, ["ai"], top=2
        )

        assert len(result["sessions"]) <= 2

    def test_recommend_default_weights(self, mock_graph_service, sample_sessions):
        """Test that default weights are used when not provided."""
        mock_graph_service.get_events.return_value = sample_sessions

        result = recommend_from_graph(
            mock_graph_service, ["ai safety"], 3
        )

        # Should use default weights and score successfully
        assert len(result["scoring"]) > 0
        assert all("score" in s and "contributions" in s for s in result["scoring"])

    def test_recommend_custom_weights(self, mock_graph_service, sample_sessions):
        """Test recommendation with custom weights."""
        mock_graph_service.get_events.return_value = sample_sessions

        custom_weights = {"interest": 5.0, "popularity": 1.0, "diversity": 0.1}

        result = recommend_from_graph(
            mock_graph_service, ["ai safety"], 3, weights=custom_weights
        )

        assert len(result["scoring"]) > 0
        # With higher interest weight, interest_match should dominate
        assert result["scoring"][0]["contributions"]["interest_match"] > 0


class TestRecommendFromGraphScoring:
    """Tests for scoring and ranking logic."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock GraphEventService."""
        mock = Mock()
        return mock

    def test_scoring_includes_contributions(self, mock_graph_service):
        """Test that scoring includes detailed contributions."""
        sessions = [
            {
                "id": "e1",
                "title": "AI Session",
                "tags": ["ai"],
                "popularity": 0.8,
            }
        ]
        mock_graph_service.get_events.return_value = sessions

        result = recommend_from_graph(mock_graph_service, ["ai"], 1)

        assert len(result["scoring"]) == 1
        scoring = result["scoring"][0]
        assert "title" in scoring
        assert "score" in scoring
        assert "contributions" in scoring
        assert "interest_match" in scoring["contributions"]
        assert "popularity" in scoring["contributions"]
        assert "diversity" in scoring["contributions"]

    def test_higher_popularity_increases_score(self, mock_graph_service):
        """Test that higher popularity sessions score higher."""
        sessions = [
            {
                "id": "e1",
                "title": "Popular Session",
                "tags": ["ai"],
                "popularity": 0.9,
            },
            {
                "id": "e2",
                "title": "Less Popular Session",
                "tags": ["ai"],
                "popularity": 0.1,
            },
        ]
        mock_graph_service.get_events.return_value = sessions

        result = recommend_from_graph(mock_graph_service, ["ai"], 2)

        assert len(result["scoring"]) == 2
        # First session should have higher score due to higher popularity
        assert result["scoring"][0]["score"] >= result["scoring"][1]["score"]

    def test_interest_match_prioritized(self, mock_graph_service):
        """Test that interest matching is prioritized in default weights."""
        sessions = [
            {
                "id": "e1",
                "title": "Exact Match",
                "tags": ["ai safety", "workshop"],
                "popularity": 0.3,
            },
            {
                "id": "e2",
                "title": "No Match",
                "tags": ["other"],
                "popularity": 0.9,
            },
        ]
        mock_graph_service.get_events.return_value = sessions

        result = recommend_from_graph(mock_graph_service, ["ai safety"], 2)

        # Despite lower popularity, exact match should score higher with default weights
        assert result["scoring"][0]["title"] == "Exact Match"


class TestRecommendFromGraphConflicts:
    """Tests for time slot conflict detection."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock GraphEventService."""
        mock = Mock()
        return mock

    def test_no_conflicts_counted(self, mock_graph_service):
        """Test that no conflicts are reported for non-overlapping sessions."""
        sessions = [
            {
                "id": "e1",
                "title": "Session 1",
                "tags": ["ai"],
                "popularity": 0.8,
                "start": "09:00",
                "end": "10:00",
            },
            {
                "id": "e2",
                "title": "Session 2",
                "tags": ["ai"],
                "popularity": 0.8,
                "start": "10:15",
                "end": "11:15",
            },
        ]
        mock_graph_service.get_events.return_value = sessions

        result = recommend_from_graph(mock_graph_service, ["ai"], 2)

        assert result["conflicts"] == 0

    def test_conflicts_detected(self, mock_graph_service):
        """Test that time slot conflicts are detected."""
        sessions = [
            {
                "id": "e1",
                "title": "Session 1",
                "tags": ["ai"],
                "popularity": 0.8,
                "start": "09:00",
                "end": "10:00",
            },
            {
                "id": "e2",
                "title": "Session 2",
                "tags": ["ai"],
                "popularity": 0.8,
                "start": "09:00",  # Same time slot as session 1
                "end": "10:00",
            },
        ]
        mock_graph_service.get_events.return_value = sessions

        result = recommend_from_graph(mock_graph_service, ["ai"], 2)

        # Should detect conflict in the same time slot
        assert result["conflicts"] > 0


class TestRecommendFromGraphErrorHandling:
    """Tests for error handling and edge cases."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock GraphEventService."""
        mock = Mock()
        return mock

    def test_graph_service_error_propagates(self, mock_graph_service):
        """Test that Graph service errors are propagated."""
        mock_graph_service.get_events.side_effect = Exception("Graph API error")

        with pytest.raises(Exception) as exc_info:
            recommend_from_graph(mock_graph_service, ["ai"], 3)

        assert "Graph API error" in str(exc_info.value)

    def test_case_insensitive_interest_matching(self, mock_graph_service):
        """Test that interest matching is case-insensitive."""
        sessions = [
            {
                "id": "e1",
                "title": "Session",
                "tags": ["AI Safety", "Workshop"],
                "popularity": 0.8,
            }
        ]
        mock_graph_service.get_events.return_value = sessions

        result = recommend_from_graph(mock_graph_service, ["ai safety"], 1)

        assert len(result["sessions"]) == 1
        assert result["scoring"][0]["contributions"]["interest_match"] > 0

    def test_whitespace_handling_in_interests(self, mock_graph_service):
        """Test that whitespace in interests is handled."""
        sessions = [
            {
                "id": "e1",
                "title": "Session",
                "tags": ["ai safety"],
                "popularity": 0.8,
            }
        ]
        mock_graph_service.get_events.return_value = sessions

        result = recommend_from_graph(
            mock_graph_service, ["  ai safety  ", "other"], 1
        )

        assert len(result["sessions"]) == 1

    def test_fetches_extra_sessions_for_filtering(self, mock_graph_service):
        """Test that function fetches extra sessions to account for filtering."""
        mock_graph_service.get_events.return_value = []

        recommend_from_graph(mock_graph_service, ["ai"], top=3)

        # Should fetch top * 2 sessions to have enough after filtering
        mock_graph_service.get_events.assert_called_once_with(top=6)

    def test_result_has_graph_source(self, mock_graph_service):
        """Test that result includes source='graph' identifier."""
        mock_graph_service.get_events.return_value = [
            {
                "id": "e1",
                "title": "Session",
                "tags": ["ai"],
                "popularity": 0.8,
            }
        ]

        result = recommend_from_graph(mock_graph_service, ["ai"], 1)

        assert result["source"] == "graph"


class TestRecommendFromGraphIntegration:
    """Integration tests for recommend_from_graph with realistic scenarios."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock GraphEventService."""
        mock = Mock()
        return mock

    def test_full_recommendation_flow(self, mock_graph_service):
        """Test complete recommendation flow with multiple sessions."""
        sessions = [
            {
                "id": "e1",
                "title": "AI Safety 101",
                "start": "09:00",
                "end": "10:00",
                "location": "Hall A",
                "tags": ["ai safety", "intro"],
                "popularity": 0.8,
            },
            {
                "id": "e2",
                "title": "Advanced Agents",
                "start": "10:15",
                "end": "11:15",
                "location": "Hall B",
                "tags": ["agents", "advanced"],
                "popularity": 0.9,
            },
            {
                "id": "e3",
                "title": "LLM Benchmarks",
                "start": "11:30",
                "end": "12:30",
                "location": "Hall C",
                "tags": ["llm", "benchmarks"],
                "popularity": 0.7,
            },
            {
                "id": "e4",
                "title": "Ethics Roundtable",
                "start": "13:00",
                "end": "14:00",
                "location": "Hall A",
                "tags": ["ai safety", "ethics"],
                "popularity": 0.6,
            },
        ]
        mock_graph_service.get_events.return_value = sessions

        result = recommend_from_graph(
            mock_graph_service, ["ai safety", "agents"], top=3
        )

        # Should return 3 sessions, ranked by score
        assert len(result["sessions"]) == 3
        assert len(result["scoring"]) == 3
        assert "conflicts" in result
        assert result["source"] == "graph"

        # Sessions should be ranked
        scores = [s["score"] for s in result["scoring"]]
        assert scores == sorted(scores, reverse=True)

    def test_recommendation_with_multiple_interests(self, mock_graph_service):
        """Test recommendation with multiple user interests."""
        sessions = [
            {
                "id": "e1",
                "title": "Session 1",
                "tags": ["ai", "safety"],
                "popularity": 0.5,
            },
            {
                "id": "e2",
                "title": "Session 2",
                "tags": ["agents", "llm"],
                "popularity": 0.5,
            },
            {
                "id": "e3",
                "title": "Session 3",
                "tags": ["ai", "agents"],
                "popularity": 0.5,
            },
        ]
        mock_graph_service.get_events.return_value = sessions

        result = recommend_from_graph(
            mock_graph_service, ["ai", "agents", "llm"], top=3
        )

        assert len(result["sessions"]) == 3
        # Verify sessions are ranked by score (with equal popularity, interest match dominates)
        # Session 3 matches 2 interests, Session 2 matches 1 interest + llm, Session 1 matches 1 interest
        # So Session 3 or Session 2 should be first (both match 2 interests)
        assert result["sessions"][0]["title"] in ["Session 2", "Session 3"]
