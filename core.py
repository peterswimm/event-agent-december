"""Core functions for Event Kit, importable by other hosts.

This module exposes stable recommend/explain call signatures by delegating to
the existing implementation in `agent.py`. Refactor the logic here over time,
keeping function signatures stable for reuse.
"""

from __future__ import annotations

from typing import Any, Dict, List

# Delegate to agent.py for the implementation for now
from .agent import recommend as _recommend_impl  # type: ignore
from .agent import explain as _explain_impl  # type: ignore


def recommend(
    manifest: Dict[str, Any], interests: List[str], top: int
) -> Dict[str, Any]:
    return _recommend_impl(manifest, interests, top)


def explain(
    manifest: Dict[str, Any], session_title: str, interests: List[str]
) -> Dict[str, Any]:
    return _explain_impl(manifest, session_title, interests)
