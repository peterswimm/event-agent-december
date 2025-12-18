"""
Tests for Prompt Flow Integration

Tests flow components: parse_intent, get_recommendations, explain_session,
and evaluation metrics.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

# These modules may not exist yet - handle gracefully
try:
    from flows.parse_intent import parse_intent
    HAS_PARSE_INTENT = True
except ImportError:
    HAS_PARSE_INTENT = False

try:
    from flows.get_recommendations import get_recommendations
    HAS_GET_RECOMMENDATIONS = True
except ImportError:
    HAS_GET_RECOMMENDATIONS = False

try:
    from flows.explain_session import explain_session
    HAS_EXPLAIN_SESSION = True
except ImportError:
    HAS_EXPLAIN_SESSION = False

try:
    from flows.evaluation.calculate_metrics import calculate_metrics
    HAS_METRICS = True
except ImportError:
    HAS_METRICS = False


@pytest.mark.foundry
@pytest.mark.skipif(not HAS_PARSE_INTENT, reason="parse_intent module not available")
class TestParseIntent:
    """Test intent parsing logic."""
    
    def test_parse_recommend_intent(self):
        """Test parsing recommendation intent."""
        user_message = "recommend sessions about AI agents"
        result = parse_intent(user_message)
        
        assert result["intent"] == "recommend"
        assert "agents" in result.get("extracted_interests", "").lower()
    
    def test_parse_explain_intent(self):
        """Test parsing explanation intent."""
        user_message = 'explain session "AI Safety Fundamentals"'
        result = parse_intent(user_message)
        
        assert result["intent"] == "explain"
        assert result.get("session_title") == "AI Safety Fundamentals"
    
    def test_parse_export_intent(self):
        """Test parsing export intent."""
        user_message = "export my itinerary for agents and ML"
        result = parse_intent(user_message)
        
        assert result["intent"] == "export"
    
    def test_parse_unknown_intent(self):
        """Test handling unknown intent."""
        user_message = "what is the weather?"
        result = parse_intent(user_message)
        
        assert result["intent"] in ["general", "unknown"]


@pytest.mark.foundry
@pytest.mark.skipif(not HAS_GET_RECOMMENDATIONS, reason="get_recommendations module not available")
class TestGetRecommendations:
    """Test recommendations flow node."""
    
    def test_get_recommendations_with_interests(self):
        """Test getting recommendations with interests."""
        with patch("flows.get_recommendations.recommend") as mock_recommend:
            mock_recommend.return_value = {
                "sessions": [{"id": "1", "title": "Test"}],
                "scoring": []
            }
            
            result = get_recommendations("agents, AI", 3)
            
            assert result is not None
            assert mock_recommend.called
    
    def test_get_recommendations_empty_interests(self):
        """Test handling empty interests."""
        with pytest.raises(ValueError):
            get_recommendations("", 3)


@pytest.mark.foundry
@pytest.mark.skipif(not HAS_EXPLAIN_SESSION, reason="explain_session module not available")
class TestExplainSession:
    """Test explanation flow node."""
    
    def test_explain_session_with_title(self):
        """Test explaining a session."""
        with patch("flows.explain_session.explain") as mock_explain:
            mock_explain.return_value = {
                "explanation": "This session matches...",
                "matched_keywords": ["agents", "ai"],
                "relevance_score": 0.85
            }
            
            result = explain_session("AI Agents", "agents")
            
            assert result is not None
            assert mock_explain.called
    
    def test_explain_session_missing_title(self):
        """Test handling missing session title."""
        with pytest.raises(ValueError):
            explain_session("", "agents")


@pytest.mark.foundry
@pytest.mark.skipif(not HAS_METRICS, reason="calculate_metrics module not available")
class TestEvaluationMetrics:
    """Test evaluation metrics calculation."""
    
    def test_calculate_precision_recall_f1(self):
        """Test precision, recall, F1 calculation."""
        expected_sessions = ["Session A", "Session B", "Session C"]
        actual_sessions = ["Session A", "Session B", "Session D"]
        
        metrics = calculate_metrics(expected_sessions, actual_sessions)
        
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert 0 <= metrics["precision"] <= 1
        assert 0 <= metrics["recall"] <= 1
        assert 0 <= metrics["f1_score"] <= 1
    
    def test_calculate_perfect_metrics(self):
        """Test metrics with perfect match."""
        sessions = ["Session A", "Session B"]
        
        metrics = calculate_metrics(sessions, sessions)
        
        assert metrics["precision"] == 1.0
        assert metrics["recall"] == 1.0
        assert metrics["f1_score"] == 1.0
    
    def test_calculate_no_matches(self):
        """Test metrics with no matches."""
        expected = ["Session A", "Session B"]
        actual = ["Session C", "Session D"]
        
        metrics = calculate_metrics(expected, actual)
        
        assert metrics["precision"] == 0.0
        assert metrics["recall"] == 0.0
        assert metrics["f1_score"] == 0.0
    
    def test_calculate_empty_lists(self):
        """Test handling empty input."""
        metrics = calculate_metrics([], [])
        
        # Should handle gracefully
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics


@pytest.mark.foundry
@pytest.mark.integration
class TestFlowDAGIntegration:
    """Test Prompt Flow DAG configuration."""
    
    def test_flow_dag_file_exists(self):
        """Test that flow.dag.yaml exists."""
        flow_path = Path("flow.dag.yaml")
        assert flow_path.exists(), "flow.dag.yaml not found"
    
    def test_evaluation_flow_exists(self):
        """Test that evaluation flow exists."""
        eval_flow_path = Path("flows/evaluation/flow.dag.yaml")
        assert eval_flow_path.exists(), "Evaluation flow not found"
