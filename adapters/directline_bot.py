"""Bot Framework adapter for Event Kit to support Direct Line / Web Chat.

NOTE: This module now uses the unified BotAdapter from adapters.bot_adapter.
Maintained for backward compatibility.

Run with:
  AGENT_API_BASE=http://localhost:8010 python -m eventkit.adapters.directline_bot --port 3979 --app-id <APP_ID> --app-password <APP_PASSWORD>

This creates a Bot Framework endpoint at /api/messages that uses the unified
Bot Framework adapter with Adaptive Card support.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import web
from botbuilder.core import (
    ActivityHandler,
    BotFrameworkAdapterSettings,
    BotFrameworkAdapter,
    TurnContext,
)
from botbuilder.schema import Activity, ActivityTypes, Attachment

# Import unified bot adapter
try:
    import sys
    from pathlib import Path
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from adapters.bot_adapter import BotAdapter
    HAS_UNIFIED_ADAPTER = True
except ImportError:
    HAS_UNIFIED_ADAPTER = False


class AgentBridgeBot(ActivityHandler):
    """
    Bot Framework bridge for EventKit.

    Now uses unified BotAdapter when available.
    """

    def __init__(self, agent_base: str) -> None:
        super().__init__()
        self.agent_base = agent_base.rstrip("/")

        # Try to use unified adapter
        if HAS_UNIFIED_ADAPTER:
            try:
                self.unified_adapter = BotAdapter()
            except Exception as e:
                print(f"Warning: Could not initialize unified adapter: {e}")
                self.unified_adapter = None
        else:
            self.unified_adapter = None

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle message activity using unified adapter if available."""
        # Use unified adapter if available
        if self.unified_adapter:
            try:
                await self.unified_adapter.handle_activity(turn_context)
                return
            except Exception as e:
                print(f"Warning: Unified adapter failed, falling back to HTTP: {e}")

        # Fallback to HTTP-based approach
        user_text = (turn_context.activity.text or "").strip()
        if not user_text:
            await turn_context.send_activity(
                "Please provide interests (e.g., agents, ai safety)"
            )
            return

        card, summary = await self._fetch_recommendations(user_text)
        if card:
            await turn_context.send_activity(
                Activity(
                    type=ActivityTypes.message,
                    text=summary,
                    attachments=[
                        Attachment(
                            content_type="application/vnd.microsoft.card.adaptive",
                            content=card,
                        )
                    ],
                )
            )
        else:
            await turn_context.send_activity(summary or "No results")

    async def _fetch_recommendations(
        self, interests: str
    ) -> tuple[Optional[Dict[str, Any]], str]:
        """Fetch recommendations from HTTP API (fallback)."""
        url = f"{self.agent_base}/recommend?interests={aiohttp.helpers.quote(interests)}&top=3&card=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None, f"Error from agent API: HTTP {resp.status}"
                data = await resp.json()
        sessions: List[Dict[str, Any]] = (
            data.get("sessions", []) if isinstance(data, dict) else []
        )
        card = data.get("adaptiveCard") if isinstance(data, dict) else None
        if not sessions:
            return card, "No sessions found for your interests."
        titles = ", ".join(s.get("title", "") for s in sessions[:3])
        return card, f"Top sessions: {titles}"


async def init_app(
    adapter: BotFrameworkAdapter, bot: AgentBridgeBot
) -> web.Application:
    app = web.Application()

    async def messages(req: web.Request) -> web.Response:
        body = await req.json()
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        try:
            response = await adapter.process_activity(
                activity, auth_header, bot.on_turn
            )
            if response:
                return web.json_response(
                    data=response.body if hasattr(response, "body") else {}
                )
            return web.Response(status=201)
        except Exception as exc:  # pragma: no cover - telemetry would normally capture
            return web.Response(status=500, text=str(exc))

    app.router.add_post("/api/messages", messages)
    return app


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser("eventkit directline bot")
    p.add_argument("--port", type=int, default=3979)
    p.add_argument("--app-id", type=str, default=os.getenv("MICROSOFT_APP_ID", ""))
    p.add_argument(
        "--app-password", type=str, default=os.getenv("MICROSOFT_APP_PASSWORD", "")
    )
    p.add_argument(
        "--agent-api-base",
        type=str,
        default=os.getenv("AGENT_API_BASE", "http://localhost:8010"),
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    settings = BotFrameworkAdapterSettings(args.app_id, args.app_password)
    adapter = BotFrameworkAdapter(settings)
    bot = AgentBridgeBot(args.agent_api_base)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app(adapter, bot))
    web.run_app(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
