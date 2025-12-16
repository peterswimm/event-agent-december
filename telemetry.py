from __future__ import annotations
import json
import os
from typing import Any, Dict, Optional


class Telemetry:
    def __init__(
        self,
        enabled: bool,
        path: str = "telemetry.jsonl",
        app_insights_cs: Optional[str] = None,
    ) -> None:
        self.enabled = enabled
        self.path = path
        self.app_insights_cs = app_insights_cs

    def log(
        self,
        action: str,
        payload: Dict[str, Any],
        start_ts: float | None,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        if not self.enabled:
            return
        try:
            line = {
                "action": action,
                "payload": payload,
                "start": start_ts,
                "success": success,
                "error": error,
            }
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(line) + "\n")
        except Exception:
            pass
        # Optional: App Insights hook (placeholder)
        if self.app_insights_cs:
            # In a full implementation, send structured telemetry to Application Insights
            # using the connection string.
            pass


def get_telemetry(manifest: Dict[str, Any]) -> Optional[Telemetry]:
    features = manifest.get("features", {}).get("telemetry", {})
    enabled = bool(features.get("enabled"))
    path = features.get("file", "telemetry.jsonl")
    app_insights_cs = os.getenv("APP_INSIGHTS_CONNECTION_STRING")
    return Telemetry(enabled, path, app_insights_cs)
