#!/usr/bin/env python3
"""Event Kit unified runner with mutually exclusive modes.

Modes:
- m365-agent: Host via Microsoft 365 Agents SDK (Teams/Copilot)
- sharepoint-agent: Publish itineraries to SharePoint (no chat)
- custom-chat: Minimal HTTP chat server (eventkit/agent.py)

Usage:
  python -m eventkit.runner --mode custom-chat --port 8010
  python -m eventkit.runner --mode m365-agent --port 3978
  python -m eventkit.runner --mode sharepoint-agent --interests "AI;agents" --publish
"""

from __future__ import annotations
import argparse, os, sys, subprocess
from typing import Optional


def run_custom_chat(port: int, card: bool) -> int:
    cmd = [sys.executable, "agent.py", "serve", "--port", str(port)]
    if card:
        cmd.append("--card")
    return subprocess.call(cmd)


def run_m365_agent(port: int) -> int:
    runner = os.path.join(
        os.path.dirname(__file__),
        "..",
        "innovation-kit-repository",
        "event-agent",
        "starter-code",
        "agents_sdk_integration",
        "run_agent.py",
    )
    runner = os.path.abspath(runner)
    if not os.path.exists(runner):
        print(
            "Missing Agents SDK starter at innovation-kit-repository/event-agent/starter-code/agents_sdk_integration/run_agent.py",
            file=sys.stderr,
        )
        return 2
    env_required = ["GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "GRAPH_CLIENT_SECRET"]
    missing = [k for k in env_required if not os.getenv(k)]
    if missing:
        print(
            f"Missing required environment variables for m365-agent: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 3
    cmd = [sys.executable, runner, "sdk", "--port", str(port)]
    return subprocess.call(cmd)


def run_sharepoint_agent(
    interests: Optional[str], max_sessions: Optional[int], publish: bool
) -> int:
    runner = os.path.join(
        os.path.dirname(__file__),
        "..",
        "innovation-kit-repository",
        "event-agent",
        "starter-code",
        "agents_sdk_integration",
        "run_agent.py",
    )
    runner = os.path.abspath(runner)
    if not os.path.exists(runner):
        print(
            "Missing Agents SDK starter at innovation-kit-repository/event-agent/starter-code/agents_sdk_integration/run_agent.py",
            file=sys.stderr,
        )
        return 2
    # Require Graph creds for SharePoint publish path
    env_required = ["GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "GRAPH_CLIENT_SECRET"]
    missing = [k for k in env_required if not os.getenv(k)]
    if publish and missing:
        print(
            f"Missing required environment variables for sharepoint-agent publish: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 3
    cmd = [sys.executable, runner, "recommend"]
    if interests:
        cmd += ["--interests", interests]
    if max_sessions:
        cmd += ["--max-sessions", str(max_sessions)]
    if publish:
        cmd += ["--publish"]
    return subprocess.call(cmd)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("eventkit runner")
    p.add_argument(
        "--mode",
        required=False,
        choices=["custom-chat", "m365-agent", "sharepoint-agent", "directline-adapter"],
        help="Select run mode (or set RUN_MODE env)",
    )
    p.add_argument("--port", type=int, default=None, help="Port for server modes")
    p.add_argument(
        "--card",
        action="store_true",
        help="Include Adaptive Card in custom-chat responses",
    )
    p.add_argument(
        "--interests",
        type=str,
        default=None,
        help="Interests for sharepoint-agent recommend",
    )
    p.add_argument(
        "--max-sessions",
        type=int,
        default=None,
        help="Max sessions for sharepoint-agent recommend",
    )
    p.add_argument(
        "--publish",
        action="store_true",
        help="Publish itinerary to SharePoint (requires creds)",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    mode = args.mode or os.getenv("RUN_MODE")
    if not mode:
        print(
            "No mode provided. Use --mode or set RUN_MODE env to one of: custom-chat, m365-agent, sharepoint-agent",
            file=sys.stderr,
        )
        raise SystemExit(1)
    if mode == "custom-chat":
        port = args.port or 8010
        raise SystemExit(run_custom_chat(port, args.card))
    if mode == "m365-agent":
        port = args.port or 3978
        raise SystemExit(run_m365_agent(port))
    if mode == "sharepoint-agent":
        raise SystemExit(
            run_sharepoint_agent(args.interests, args.max_sessions, args.publish)
        )
    if mode == "directline-adapter":
        # Launch the Direct Line adapter shim
        cmd = [
            sys.executable,
            "-m",
            "eventkit.adapters.directline_bot",
        ]
        if args.port:
            cmd += ["--port", str(args.port)]
        return_code = subprocess.call(cmd)
        raise SystemExit(return_code)
    print("Unknown mode", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
