#!/usr/bin/env python3
"""Event Kit Agent (renamed from simplified-event-agent)
Usage:
  # Manifest-based recommendations
  python agent.py recommend --interests "ai safety, agents" --top 3 --profile-save user1
  python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"
  
  # Graph API recommendations (requires Graph credentials in .env)
  python agent.py recommend --source graph --user-id user@example.com --interests "ai safety" --top 3
  python agent.py recommend --source graph --interests "agents" --top 3  # Uses default user
"""

from __future__ import annotations
import json, argparse, pathlib, urllib.parse, time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List, Dict, Any, Optional

MANIFEST_PATH = pathlib.Path(__file__).parent / "agent.json"
try:
    from telemetry import get_telemetry  # local module
except Exception:  # pragma: no cover
    get_telemetry = lambda manifest: None  # type: ignore

try:
    from settings import Settings  # Graph settings
    from graph_auth import GraphAuthClient, GraphAuthError
    from graph_service import GraphEventService, GraphServiceError
    from core import recommend_from_graph
    GRAPH_AVAILABLE = True
except Exception:  # pragma: no cover
    GRAPH_AVAILABLE = False  # Graph dependencies not available


class SecurityValidator:
    """Input validation for security hardening."""
    
    MAX_INTERESTS_LENGTH = 500
    MAX_USER_ID_LENGTH = 255
    MAX_TITLE_LENGTH = 200
    VALID_INTERESTS_PATTERN = r'^[a-zA-Z0-9\s,\-]+$'
    VALID_EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    VALID_TITLE_PATTERN = r'^[a-zA-Z0-9\s,\-:?!\(\)\'\.]+$'
    
    @staticmethod
    def validate_interests(interests: str) -> tuple[bool, str]:
        """Validate interests string."""
        import re
        
        if not interests or not interests.strip():
            return False, "Interests cannot be empty"
        
        if len(interests) > SecurityValidator.MAX_INTERESTS_LENGTH:
            return False, f"Interests too long (max {SecurityValidator.MAX_INTERESTS_LENGTH} chars)"
        
        if not re.match(SecurityValidator.VALID_INTERESTS_PATTERN, interests):
            return False, "Interests contain invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_user_id(user_id: str) -> tuple[bool, str]:
        """Validate user ID (email format)."""
        import re
        
        if not user_id or not user_id.strip():
            return False, "User ID cannot be empty"
        
        if len(user_id) > SecurityValidator.MAX_USER_ID_LENGTH:
            return False, f"User ID too long (max {SecurityValidator.MAX_USER_ID_LENGTH} chars)"
        
        if not re.match(SecurityValidator.VALID_EMAIL_PATTERN, user_id):
            return False, "User ID must be a valid email address"
        
        return True, ""
    
    @staticmethod
    def validate_session_title(title: str) -> tuple[bool, str]:
        """Validate session title."""
        import re
        
        if not title or not title.strip():
            return False, "Session title cannot be empty"
        
        if len(title) > SecurityValidator.MAX_TITLE_LENGTH:
            return False, f"Session title too long (max {SecurityValidator.MAX_TITLE_LENGTH} chars)"
        
        if not re.match(SecurityValidator.VALID_TITLE_PATTERN, title):
            return False, "Session title contains invalid characters"
        
        return True, ""


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 100, window_seconds: int = 60):
        """Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
            window_seconds: Time window for rate limiting in seconds
        """
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.request_log: Dict[str, List[float]] = {}
    
    def is_allowed(self, ip: str) -> bool:
        """Check if request from IP is allowed."""
        now = time.time()
        
        # Initialize IP log if needed
        if ip not in self.request_log:
            self.request_log[ip] = []
        
        # Remove old requests outside the window
        self.request_log[ip] = [
            ts for ts in self.request_log[ip]
            if now - ts < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.request_log[ip]) < self.requests_per_minute:
            self.request_log[ip].append(now)
            return True
        
        return False
    
    def cleanup_old_entries(self) -> None:
        """Remove IPs with no recent requests."""
        now = time.time()
        self.request_log = {
            ip: timestamps
            for ip, timestamps in self.request_log.items()
            if any(now - ts < self.window_seconds for ts in timestamps)
        }


def load_manifest(path: pathlib.Path = MANIFEST_PATH) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _load_external_sessions(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    feat = manifest.get("features", {}).get("externalSessions", {})
    if not feat.get("enabled"):
        return []
    file = feat.get("file", "sessions_external.json")
    p = pathlib.Path(file)
    if not p.exists() and not p.is_absolute():
        script_dir = pathlib.Path(__file__).parent
        alt = script_dir / file
        if alt.exists():
            p = alt
        else:
            manifest_dir = MANIFEST_PATH.parent
            alt2 = manifest_dir / file
            if alt2.exists():
                p = alt2
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
        if isinstance(data, list):
            return [d for d in data if isinstance(d, dict)]
    except Exception:
        return []
    return []


def get_sessions(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    external = _load_external_sessions(manifest)
    return external if external else manifest.get("sessions", [])


def _normalize_interests(raw: str) -> List[str]:
    norm = raw.replace(";", ",").lower()
    return [t.strip() for t in norm.split(",") if t.strip()]


def load_profile(file: str, key: str) -> List[str]:
    p = pathlib.Path(file).expanduser()
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
        val = data.get(key)
        if isinstance(val, list):
            return [str(v).lower() for v in val]
    except Exception:
        return []
    return []


def save_profile(file: str, key: str, interests: List[str]) -> None:
    p = pathlib.Path(file).expanduser()
    data: Dict[str, Any] = {}
    if p.exists():
        try:
            data = json.loads(p.read_text())
        except Exception:
            data = {}
    data[key] = interests
    p.write_text(json.dumps(data, indent=2))


def score_session(
    session: Dict[str, Any], interests: List[str], w: Dict[str, float]
) -> Dict[str, Any]:
    tags = [t.lower() for t in session.get("tags", [])]
    interest_hits = sum(1 for t in tags if t in interests)
    diversity_component = len(set(interests)) * 0.01 * w["diversity"]
    contributions = {
        "interest_match": interest_hits * w["interest"],
        "popularity": session.get("popularity", 0) * w["popularity"],
        "diversity": diversity_component,
    }
    total = sum(contributions.values())
    return {"session": session, "score": total, "contributions": contributions}


def recommend(
    manifest: Dict[str, Any], interests: List[str], top_n: int
) -> Dict[str, Any]:
    w = manifest["weights"]
    sessions = get_sessions(manifest)
    scored = [score_session(s, interests, w) for s in sessions]
    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)[:top_n]
    conflicts = _count_conflicts([r["session"] for r in ranked])
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
    }


def explain(
    manifest: Dict[str, Any], title: str, interests: List[str]
) -> Dict[str, Any]:
    w = manifest["weights"]
    sessions = get_sessions(manifest)
    session = next((s for s in sessions if s["title"].lower() == title.lower()), None)
    if not session:
        return {"error": "session not found", "title": title}
    detail = score_session(session, interests, w)
    return {
        "title": session["title"],
        "score": detail["score"],
        "contributions": detail["contributions"],
        "matched_tags": [t for t in session.get("tags", []) if t.lower() in interests],
    }


def _count_conflicts(sessions: List[Dict[str, Any]]) -> int:
    slots = {}
    for s in sessions:
        slot = (s.get("start"), s.get("end"))
        slots.setdefault(slot, 0)
        slots[slot] += 1
    return sum(1 for v in slots.values() if v > 1)


def _build_itinerary_markdown(interests: List[str], recommendation: Dict[str, Any]) -> str:
    """Build markdown itinerary from recommendation result."""
    lines = ["# Event Itinerary"]
    lines.append(f"\n**Recommended for:** {', '.join(interests)}\n")
    
    for session in recommendation.get("sessions", []):
        title = session.get("title", "Unknown Session")
        start = session.get("start", "?")
        end = session.get("end", "?")
        location = session.get("location", "?")
        tags = session.get("tags", [])
        
        lines.append(f"## {title}")
        lines.append(f"\nTime: {start} - {end} | Location: {location}")
        if tags:
            lines.append(f"Tags: {', '.join(tags)}\n")
        else:
            lines.append("")
    
    return "\n".join(lines)


def _build_adaptive_card(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    body = []
    actions = []
    for i, s in enumerate(sessions, start=1):
        body.append(
            {
                "type": "Container",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": f"{i}. {s['title']}",
                        "weight": "Bolder",
                    },
                    {
                        "type": "TextBlock",
                        "text": f"{s.get('start', '?')} - {s.get('end', '?')} @ {s.get('location', '?')}",
                        "isSubtle": True,
                        "spacing": "None",
                    },
                ],
            }
        )
        actions.append(
            {
                "type": "Action.Submit",
                "title": f"Explain #{i}",
                "data": {
                    "action": "explainSession",
                    "sessionTitle": s["title"],
                    "start": s.get("start"),
                    "end": s.get("end"),
                    "room": s.get("location"),
                },
            }
        )
    return {
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [
            {
                "type": "TextBlock",
                "text": "Event Recommendations",
                "weight": "Bolder",
                "size": "Medium",
            }
        ]
        + body,
        "actions": actions,
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    }


def _get_graph_recommendation(
    interests: List[str], top_n: int, user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get recommendations from Microsoft Graph API.
    
    Args:
        interests: List of interest strings
        top_n: Number of recommendations to return
        user_id: Optional user ID (for future use with delegated auth)
        
    Returns:
        Recommendation dict with sessions, scoring, and conflicts
        
    Raises:
        ValueError: If Graph is not available or credentials are missing
        GraphAuthError: If authentication fails
        GraphServiceError: If Graph API fails
    """
    if not GRAPH_AVAILABLE:
        raise ValueError("Graph API support not available. Install required packages.")
    
    try:
        settings = Settings()
        if not settings.validate_graph_ready():
            errors = settings.get_validation_errors()
            raise ValueError(f"Graph credentials not configured: {', '.join(errors)}")
        
        # Initialize auth and service
        auth_client = GraphAuthClient(settings)
        graph_service = GraphEventService(auth_client, settings)
        
        # Get recommendations from Graph
        result = recommend_from_graph(graph_service, interests, top_n)
        
        # Add user_id if provided (for tracking/logging)
        if user_id:
            result["user_id"] = user_id
        
        return result
        
    except (GraphAuthError, GraphServiceError) as e:
        raise ValueError(f"Graph API error: {str(e)}") from e


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("eventkit agent")
    sub = p.add_subparsers(dest="command")
    r = sub.add_parser("recommend")
    r.add_argument("--source", type=str, default="manifest", choices=["manifest", "graph"], 
                   help="Event source: 'manifest' (default) or 'graph' (Microsoft Graph API)")
    r.add_argument("--user-id", type=str, default=None, 
                   help="User ID for Graph API (optional, uses service account if not provided)")
    r.add_argument("--interests", type=str, default="")
    r.add_argument("--top", type=int, default=None)
    r.add_argument("--profile-save", type=str, default=None)
    r.add_argument("--profile-load", type=str, default=None)
    e = sub.add_parser("explain")
    e.add_argument("--session", required=True)
    e.add_argument("--interests", type=str, default="")
    x = sub.add_parser("export")
    x.add_argument("--interests", type=str, default="")
    x.add_argument("--output", type=str, default=None)
    x.add_argument("--profile-save", type=str, default=None)
    x.add_argument("--profile-load", type=str, default=None)
    s = sub.add_parser("serve")
    s.add_argument("--port", type=int, default=8010)
    s.add_argument("--card", action="store_true")
    return p


def main() -> None:
    manifest = load_manifest()
    telemetry = get_telemetry(manifest)
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    start_ts = time.time()
    storage_file = manifest.get("profile", {}).get("storage_file")
    if args.command == "recommend":
        interests: List[str] = []
        if args.profile_load and storage_file:
            interests = load_profile(storage_file, args.profile_load)
        if not interests and args.interests:
            interests = _normalize_interests(args.interests)
        if not interests:
            err = {"error": "no interests provided"}
            print(json.dumps(err))
            if telemetry:
                telemetry.log(
                    "recommend", err, start_ts, success=False, error="empty_interests"
                )
            return
        top_n = args.top if args.top else manifest["recommend"]["max_sessions_default"]
        
        # Handle Graph mode
        source = getattr(args, "source", "manifest")
        if source == "graph":
            try:
                user_id = getattr(args, "user_id", None)
                result = _get_graph_recommendation(interests, top_n, user_id)
                if args.profile_save and storage_file:
                    save_profile(storage_file, args.profile_save, interests)
                    result["profileSaved"] = args.profile_save
                print(json.dumps(result, indent=2))
                if telemetry:
                    telemetry.log("recommend_graph", result, start_ts, success=True)
            except ValueError as e:
                err = {"error": str(e), "source": "graph"}
                print(json.dumps(err))
                if telemetry:
                    telemetry.log("recommend_graph", err, start_ts, success=False, error=str(e))
            return
        
        # Default manifest mode
        result = recommend(manifest, interests, top_n)
        if args.profile_save and storage_file:
            save_profile(storage_file, args.profile_save, interests)
            result["profileSaved"] = args.profile_save
        print(json.dumps(result, indent=2))
        if telemetry:
            telemetry.log("recommend", result, start_ts, success=True)
        return
    if args.command == "explain":
        interests: List[str] = []
        if args.interests:
            interests = _normalize_interests(args.interests)
        result = explain(manifest, args.session, interests)
        print(json.dumps(result, indent=2))
        if telemetry:
            telemetry.log(
                "explain",
                result,
                start_ts,
                success="error" not in result,
                error=result.get("error"),
            )
        return
    if args.command == "export":
        interests: List[str] = []
        if args.profile_load and storage_file:
            interests = load_profile(storage_file, args.profile_load)
        if not interests and args.interests:
            interests = _normalize_interests(args.interests)
        if not interests:
            err = {"error": "no interests provided"}
            print(json.dumps(err))
            if telemetry:
                telemetry.log(
                    "export", err, start_ts, success=False, error="empty_interests"
                )
            return
        top_n = manifest["recommend"]["max_sessions_default"]
        rec = recommend(manifest, interests, top_n)
        md = _build_itinerary_markdown(interests, rec)
        feat_export = manifest.get("features", {}).get("export", {})
        if feat_export.get("enabled"):
            out_dir = pathlib.Path(feat_export.get("output_dir", "exports"))
            out_dir.mkdir(parents=True, exist_ok=True)
            fname = args.output or f"itinerary_{'_'.join(interests[:3])}.md"
            path = out_dir / fname
            path.write_text(md)
            export_payload = {"saved": str(path), "sessionCount": len(rec["sessions"])}
        else:
            export_payload = {"markdown": md, "sessionCount": len(rec["sessions"])}
        if args.profile_save and storage_file:
            save_profile(storage_file, args.profile_save, interests)
            export_payload["profileSaved"] = args.profile_save
        print(json.dumps(export_payload, indent=2))
        if telemetry:
            telemetry.log(
                "export", {"sessions": rec["sessions"]}, start_ts, success=True
            )
        return
    if args.command == "serve":
        t = telemetry

        def _serve_with_telemetry(
            manifest: Dict[str, Any], port: int, default_card: bool
        ):
            storage_file = manifest.get("profile", {}).get("storage_file")

            class Handler(BaseHTTPRequestHandler):
                def _get_correlation_id(self) -> str:
                    """Extract or generate a correlation ID for the current request."""
                    # W3C traceparent: 00-<trace-id>-<span-id>-<flags>
                    traceparent = self.headers.get("traceparent")
                    if traceparent:
                        try:
                            parts = traceparent.split("-")
                            if len(parts) >= 2 and parts[1]:
                                return parts[1]
                        except Exception:
                            pass
                    cid = self.headers.get("X-Correlation-ID")
                    if cid:
                        return cid
                    if t:
                        try:
                            return t.generate_correlation_id()  # type: ignore[attr-defined]
                        except Exception:
                            pass
                    import uuid
                    return str(uuid.uuid4())

                def _send(
                    self,
                    code: int,
                    payload: Dict[str, Any],
                    start_ts: float | None = None,
                    action: str | None = None,
                    correlation_id: Optional[str] = None,
                ):
                    if correlation_id is None:
                        correlation_id = self._get_correlation_id()
                    body = json.dumps(payload).encode()
                    self.send_response(code)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    # CORS for webchat
                    self.send_header("Access-Control-Allow-Origin", "*")
                    # Expose correlation header to browser clients
                    self.send_header("Access-Control-Expose-Headers", "X-Correlation-ID")
                    # Include correlation ID in responses
                    self.send_header("X-Correlation-ID", correlation_id)
                    self.end_headers()
                    self.wfile.write(body)
                    if t and action:
                        t.log(
                            action,
                            payload,
                            start_ts,
                            success=(code == 200 and "error" not in payload),
                            error=payload.get("error"),
                            correlation_id=correlation_id,
                        )

                def do_GET(self):  # noqa: N802
                    correlation_id = self._get_correlation_id()
                    parsed = urllib.parse.urlparse(self.path)
                    qs = urllib.parse.parse_qs(parsed.query)
                    path = parsed.path
                    # Optional auth token
                    token_required = bool(os.getenv("API_TOKEN"))
                    if token_required:
                        auth_header = self.headers.get("Authorization", "")
                        expected = f"Bearer {os.getenv('API_TOKEN')}"
                        if auth_header != expected:
                            self._send(
                                401,
                                {"error": "unauthorized"},
                                time.time(),
                                "unauthorized",
                                correlation_id,
                            )
                            return
                    if path == "/health":
                        self._send(200, {"status": "ok"}, time.time(), "health", correlation_id)
                        return
                    if path == "/recommend":
                        start = time.time()
                        interests_raw = qs.get("interests", [""])[0]
                        profile_load = qs.get("profileLoad", [None])[0]
                        top = qs.get("top", [None])[0]
                        card_flag = qs.get("card", [None])[0]
                        interests: List[str] = []
                        if profile_load and storage_file:
                            interests = load_profile(storage_file, profile_load)
                        if not interests and interests_raw:
                            interests = _normalize_interests(interests_raw)
                        if not interests:
                            self._send(
                                400,
                                {"error": "no interests provided"},
                                start,
                                "recommend",
                                correlation_id,
                            )
                            return
                        top_n = (
                            int(top)
                            if top
                            else manifest["recommend"]["max_sessions_default"]
                        )
                        result = recommend(manifest, interests, top_n)
                        if default_card or card_flag == "1":
                            result["adaptiveCard"] = _build_adaptive_card(
                                result["sessions"]
                            )
                        self._send(200, result, start, "recommend", correlation_id)
                        return
                    if path == "/explain":
                        start = time.time()
                        session_title = qs.get("session", [""])[0]
                        interests_raw = qs.get("interests", [""])[0]
                        profile_load = qs.get("profileLoad", [None])[0]
                        interests: List[str] = []
                        if profile_load and storage_file:
                            interests = load_profile(storage_file, profile_load)
                        if not interests and interests_raw:
                            interests = _normalize_interests(interests_raw)
                        if not session_title:
                            self._send(
                                400, {"error": "session required"}, start, "explain"
                            )
                            return
                        result = explain(manifest, session_title, interests)
                        self._send(200, result, start, "explain", correlation_id)
                        return
                    if path == "/recommend-graph":
                        if not GRAPH_AVAILABLE:
                            self._send(
                                503,
                                {"error": "Graph API support not available"},
                                time.time(),
                                "recommend_graph",
                                correlation_id,
                            )
                            return
                        start = time.time()
                        interests_raw = qs.get("interests", [""])[0]
                        user_id = qs.get("userId", [None])[0]
                        top = qs.get("top", [None])[0]
                        card_flag = qs.get("card", [None])[0]
                        interests: List[str] = []
                        if interests_raw:
                            interests = _normalize_interests(interests_raw)
                        if not interests:
                            self._send(
                                400,
                                {"error": "no interests provided"},
                                start,
                                "recommend_graph",
                                correlation_id,
                            )
                            return
                        try:
                            settings = Settings()
                            if not settings.validate_graph_ready():
                                errors = settings.get_validation_errors()
                                self._send(
                                    502,
                                    {
                                        "error": "Graph credentials not configured",
                                        "details": ", ".join(errors),
                                    },
                                    start,
                                    "recommend_graph",
                                    correlation_id,
                                )
                                return
                            auth_client = GraphAuthClient(settings)
                            graph_service = GraphEventService(auth_client, settings)
                            top_n = (
                                int(top)
                                if top
                                else manifest["recommend"]["max_sessions_default"]
                            )
                            result = recommend_from_graph(
                                graph_service, interests, top_n
                            )
                            if user_id:
                                result["userId"] = user_id
                            if default_card or card_flag == "1":
                                result["adaptiveCard"] = _build_adaptive_card(
                                    result["sessions"]
                                )
                            self._send(200, result, start, "recommend_graph", correlation_id)
                            return
                        except (GraphAuthError, GraphServiceError) as e:
                            self._send(
                                502,
                                {"error": f"Graph API error: {str(e)}"},
                                start,
                                "recommend_graph",
                                correlation_id,
                            )
                            return
                        except ValueError as e:
                            self._send(
                                400,
                                {"error": str(e)},
                                start,
                                "recommend_graph",
                                correlation_id,
                            )
                            return
                    if path == "/export":
                        start = time.time()
                        interests_raw = qs.get("interests", [""])[0]
                        profile_load = qs.get("profileLoad", [None])[0]
                        interests: List[str] = []
                        if profile_load and storage_file:
                            interests = load_profile(storage_file, profile_load)
                        if not interests and interests_raw:
                            interests = _normalize_interests(interests_raw)
                        if not interests:
                            self._send(
                                400, {"error": "no interests provided"}, start, "export"
                            )
                            return
                        top_n = manifest["recommend"]["max_sessions_default"]
                        rec = recommend(manifest, interests, top_n)
                        md = _build_itinerary_markdown(interests, rec)
                        response = {
                            "markdown": md,
                            "sessionCount": len(rec["sessions"]),
                        }
                        feat_export = manifest.get("features", {}).get("export", {})
                        if feat_export.get("enabled"):
                            out_dir = pathlib.Path(
                                feat_export.get("output_dir", "exports")
                            )
                            out_dir.mkdir(parents=True, exist_ok=True)
                            path = out_dir / f"itinerary_{'_'.join(interests[:3])}.md"
                            path.write_text(md)
                            response["saved"] = str(path)
                        self._send(200, response, start, "export", correlation_id)
                        return
                    self._send(404, {"error": "not found"}, time.time(), "unknown", correlation_id)

                def log_message(self, fmt, *a):
                    return

            server = HTTPServer(("0.0.0.0", port), Handler)
            print(
                f"[serve] listening on port {port} (endpoints: /recommend /recommend-graph /explain /health /export)"
            )
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                print("[serve] shutting down")
                server.server_close()

        _serve_with_telemetry(manifest, args.port, getattr(args, "card", False))
        return
    build_parser().print_help()


if __name__ == "__main__":
    main()
