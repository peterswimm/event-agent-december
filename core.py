"""Core functions for Event Kit, importable by other hosts.

This module exposes stable recommend/explain call signatures by delegating to
the existing implementation in `agent.py`. Also provides Graph API integration
for fetching events from Microsoft Graph and making recommendations.

Refactor the logic here over time, keeping function signatures stable for reuse.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import from agent module
try:
    from agent import recommend as _recommend_impl  # type: ignore
    from agent import explain as _explain_impl  # type: ignore
    from agent import score_session, _count_conflicts  # type: ignore
except ImportError:
    # Fallback for package imports
    from .agent import recommend as _recommend_impl  # type: ignore
    from .agent import explain as _explain_impl  # type: ignore
    from .agent import score_session, _count_conflicts  # type: ignore

logger = logging.getLogger(__name__)


def recommend(
    manifest: Dict[str, Any], interests: List[str], top: int
) -> Dict[str, Any]:
    return _recommend_impl(manifest, interests, top)


def explain(
    manifest: Dict[str, Any], session_title: str, interests: List[str]
) -> Dict[str, Any]:
    return _explain_impl(manifest, session_title, interests)


def recommend_from_graph(
    graph_service: Any,
    interests: List[str],
    top: int,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Recommend sessions from Microsoft Graph calendar events.

    Fetches events from the user's calendar using GraphEventService,
    scores them against user interests, and returns top recommendations.

    Args:
        graph_service: GraphEventService instance with authenticated client
        interests: List of interest strings to match against event tags
        top: Number of top recommendations to return
        weights: Scoring weights for interest/popularity/diversity (optional)
                If not provided, defaults to: interest=2.0, popularity=0.5, diversity=0.3

    Returns:
        Dictionary with format:
        {
            "sessions": [list of recommended session dicts],
            "scoring": [score details for each recommendation],
            "conflicts": number of time slot conflicts,
            "source": "graph"
        }

    Raises:
        ValueError: If interests list is empty or top <= 0
        Exception: If Graph service fetch fails (GraphServiceError, GraphAuthError)
    """
    if not interests:
        raise ValueError("At least one interest is required")
    if top <= 0:
        raise ValueError("top must be a positive integer")

    # Use default weights if not provided
    if weights is None:
        weights = {"interest": 2.0, "popularity": 0.5, "diversity": 0.3}

    # Normalize interests to lowercase
    normalized_interests = [i.lower().strip() for i in interests if i.strip()]

    logger.info(
        "Fetching recommendations from Graph API",
        extra={
            "interests": normalized_interests,
            "top": top,
            "weights": weights,
        },
    )

    try:
        # Fetch events from Graph API
        sessions = graph_service.get_events(top=top * 2)  # Fetch extra to account for filtering

        if not sessions:
            logger.warning("No sessions returned from Graph API")
            return {
                "sessions": [],
                "scoring": [],
                "conflicts": 0,
                "source": "graph",
                "message": "No events found in calendar",
            }

        logger.info(f"Fetched {len(sessions)} sessions from Graph API")

        # Score all sessions
        scored = [score_session(s, normalized_interests, weights) for s in sessions]

        # Sort by score and take top N
        ranked = sorted(scored, key=lambda x: x["score"], reverse=True)[:top]

        # Count time slot conflicts
        conflicts = _count_conflicts([r["session"] for r in ranked])

        logger.info(
            "Scored and ranked sessions",
            extra={
                "total_scored": len(scored),
                "returned": len(ranked),
                "conflicts": conflicts,
            },
        )

        return {
            "sessions": [r["session"] for r in ranked],
            "scoring": [
                {
                    "title": r["session"]["title"],
                    "score": r["score"],
                    "contributions": r["contributions"],
                }
                for r in ranked
            ],
            "conflicts": conflicts,
            "source": "graph",
        }

    except Exception as e:
        logger.error(f"Failed to fetch recommendations from Graph: {str(e)}")
        raise
