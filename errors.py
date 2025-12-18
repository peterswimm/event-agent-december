"""Custom exceptions and error helpers for the Event Kit agent."""

from typing import Optional, Dict, Any


class EventKitError(Exception):
    """Base class for Event Kit exceptions."""


class InvalidInputError(EventKitError):
    """Raised when user input fails validation."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field

    def to_response(self) -> Dict[str, Any]:
        payload = {"error": "invalid_input", "message": str(self)}
        if self.field:
            payload["field"] = self.field
        return payload


class RateLimitError(EventKitError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message)

    def to_response(self) -> Dict[str, Any]:
        return {"error": "rate_limit", "message": str(self)}


class GraphAuthError(EventKitError):
    """Authentication error when acquiring Graph tokens."""

    def __init__(self, message: str):
        super().__init__(message)

    def to_response(self) -> Dict[str, Any]:
        return {"error": "graph_auth", "message": str(self)}


class GraphAPIError(EventKitError):
    """Graph API error when calling endpoints."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

    def to_response(self) -> Dict[str, Any]:
        payload = {"error": "graph_api", "message": str(self)}
        if self.status_code is not None:
            payload["statusCode"] = self.status_code
        return payload


def error_response(code: int, message: str, details: Optional[str] = None) -> Dict[str, Any]:
    """Create a standard error response payload."""
    payload: Dict[str, Any] = {"error": message}
    if details:
        payload["details"] = details
    return payload
