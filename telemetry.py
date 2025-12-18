from __future__ import annotations
import json
import os
import uuid
import time
from typing import Any, Dict, Optional

# Application Insights integration (optional)
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    APPINSIGHTS_AVAILABLE = True
except ImportError:
    APPINSIGHTS_AVAILABLE = False
    trace = None  # type: ignore


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
        self.app_insights_enabled = False
        self.tracer = None
        
        # Initialize Application Insights if connection string provided
        if self.app_insights_cs and APPINSIGHTS_AVAILABLE:
            try:
                configure_azure_monitor(connection_string=self.app_insights_cs)
                self.tracer = trace.get_tracer(__name__)
                self.app_insights_enabled = True
            except Exception as e:
                print(f"[telemetry] Failed to initialize Application Insights: {e}")

    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for request tracking."""
        return str(uuid.uuid4())

    def log(
        self,
        action: str,
        payload: Dict[str, Any],
        start_ts: float | None,
        success: bool,
        error: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Log telemetry event to JSONL file and optionally to Application Insights.
        
        Args:
            action: The action being logged (e.g., 'recommend', 'explain')
            payload: The payload data associated with the action
            start_ts: Start timestamp of the action
            success: Whether the action succeeded
            error: Error message if action failed
            correlation_id: Optional correlation ID for request tracing
        """
        if not self.enabled:
            return
        
        # Calculate duration
        duration_ms = None
        if start_ts is not None:
            duration_ms = int((time.time() - start_ts) * 1000)
        
        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = self.generate_correlation_id()
        
        try:
            # Log to JSONL file
            line = {
                "action": action,
                "payload": payload,
                "start": start_ts,
                "duration_ms": duration_ms,
                "success": success,
                "error": error,
                "correlation_id": correlation_id,
                "timestamp": time.time(),
            }
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(line) + "\n")
        except Exception:
            pass
        
        # Log to Application Insights if enabled
        if self.app_insights_enabled and self.tracer:
            try:
                self._log_to_app_insights(
                    action, payload, duration_ms, success, error, correlation_id
                )
            except Exception as e:
                print(f"[telemetry] Failed to log to Application Insights: {e}")

    def _log_to_app_insights(
        self,
        action: str,
        payload: Dict[str, Any],
        duration_ms: Optional[int],
        success: bool,
        error: Optional[str],
        correlation_id: str,
    ) -> None:
        """Log structured telemetry to Application Insights."""
        if not self.tracer:
            return
        
        with self.tracer.start_as_current_span(action) as span:
            # Set span attributes
            span.set_attribute("action", action)
            span.set_attribute("correlation_id", correlation_id)
            span.set_attribute("success", success)
            
            if duration_ms is not None:
                span.set_attribute("duration_ms", duration_ms)
            
            # Add custom properties from payload (sanitized)
            if "interests" in payload:
                interests = payload["interests"]
                if isinstance(interests, list):
                    span.set_attribute("interests_count", len(interests))
                    span.set_attribute("interests", ",".join(interests[:5]))  # First 5 only
            
            if "sessions" in payload:
                sessions = payload["sessions"]
                if isinstance(sessions, list):
                    span.set_attribute("sessions_returned", len(sessions))
            
            if "userId" in payload:
                # Hash or anonymize user ID for privacy
                span.set_attribute("user_id_hash", str(hash(payload["userId"]))[:8])
            
            # Set span status
            if success:
                span.set_status(Status(StatusCode.OK))
            else:
                span.set_status(Status(StatusCode.ERROR, error or "Unknown error"))
                if error:
                    span.record_exception(Exception(error))

    def log_exception(
        self,
        exception: Exception,
        action: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Log an exception to telemetry and Application Insights.
        
        Args:
            exception: The exception to log
            action: The action that caused the exception
            correlation_id: Optional correlation ID for request tracing
        """
        if not self.enabled:
            return
        
        if correlation_id is None:
            correlation_id = self.generate_correlation_id()
        
        # Log to JSONL
        try:
            line = {
                "action": action,
                "exception": str(exception),
                "exception_type": type(exception).__name__,
                "correlation_id": correlation_id,
                "timestamp": time.time(),
            }
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(line) + "\n")
        except Exception:
            pass
        
        # Log to Application Insights
        if self.app_insights_enabled and self.tracer:
            try:
                with self.tracer.start_as_current_span(f"{action}_exception") as span:
                    span.set_attribute("action", action)
                    span.set_attribute("correlation_id", correlation_id)
                    span.set_status(Status(StatusCode.ERROR, str(exception)))
                    span.record_exception(exception)
            except Exception:
                pass


def get_telemetry(manifest: Dict[str, Any]) -> Optional[Telemetry]:
    features = manifest.get("features", {}).get("telemetry", {})
    enabled = bool(features.get("enabled"))
    path = features.get("file", "telemetry.jsonl")
    app_insights_cs = os.getenv("APP_INSIGHTS_CONNECTION_STRING")
    return Telemetry(enabled, path, app_insights_cs)
