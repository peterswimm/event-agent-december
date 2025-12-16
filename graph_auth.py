"""Microsoft Graph authentication using MSAL.

This module handles token acquisition and caching for Microsoft Graph API access
using the Microsoft Authentication Library (MSAL).
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import msal

from settings import Settings

logger = logging.getLogger(__name__)


class GraphAuthError(Exception):
    """Raised when authentication fails."""

    pass


class GraphAuthClient:
    """Manages MSAL authentication and token caching for Microsoft Graph API.

    Attributes:
        settings: Application settings with Graph credentials
        cache_file: Path to token cache file (~/.event_agent_token_cache.json)
        _app: MSAL ConfidentialClientApplication instance
        _token_cache: In-memory token cache
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize GraphAuthClient.

        Args:
            settings: Settings instance with Graph credentials (tenant_id, client_id, client_secret)

        Raises:
            GraphAuthError: If any required credentials are missing
        """
        self.settings = settings
        self.cache_file = Path.home() / ".event_agent_token_cache.json"
        self._token_cache: dict = {}
        self._last_token_time: float = 0

        # Validate credentials
        if not settings.validate_graph_ready():
            errors = settings.get_validation_errors()
            raise GraphAuthError(f"Missing Graph credentials: {', '.join(errors)}")

        logger.info(
            "Initializing Graph auth client",
            extra={"tenant": settings.graph_tenant_id[:8] + "..."},
        )

        # Initialize MSAL app
        self._app = msal.ConfidentialClientApplication(
            client_id=settings.graph_client_id,
            client_credential=settings.graph_client_secret,
            authority=f"https://login.microsoftonline.com/{settings.graph_tenant_id}",
        )

        # Load cached token if available
        self._load_token_cache()

    def get_access_token(self) -> str:
        """Get a valid access token for Microsoft Graph API.

        Uses cached token if available and not expired. Otherwise acquires a new token.

        Returns:
            Valid access token string

        Raises:
            GraphAuthError: If token acquisition fails
        """
        # Check if cached token is still valid
        if self._token_cache and self._is_token_valid():
            logger.debug("Using cached access token")
            return self._token_cache.get("access_token", "")

        logger.info("Acquiring new access token from MSAL")
        token = self._acquire_token_for_client()
        self._token_cache = token
        self._last_token_time = time.time()
        self._save_token_cache()

        return token.get("access_token", "")

    def _acquire_token_for_client(self) -> dict:
        """Acquire token using client credentials flow (service account).

        Returns:
            Token response dict with 'access_token' and 'expires_in'

        Raises:
            GraphAuthError: If token acquisition fails
        """
        scopes = ["https://graph.microsoft.com/.default"]

        try:
            result = self._app.acquire_token_for_client(scopes=scopes)

            if "access_token" in result:
                logger.info(
                    "Successfully acquired access token",
                    extra={"expires_in_seconds": result.get("expires_in", 0)},
                )
                return result

            error = result.get("error", "Unknown error")
            error_desc = result.get("error_description", "No description")
            logger.error(f"Token acquisition failed: {error} - {error_desc}")
            raise GraphAuthError(f"Failed to acquire token: {error}")

        except Exception as e:
            logger.error(f"Exception during token acquisition: {str(e)}")
            raise GraphAuthError(f"Token acquisition exception: {str(e)}") from e

    def _is_token_valid(self) -> bool:
        """Check if cached token is still valid.

        Token is considered valid if:
        - Cached token exists
        - Less than 80% of expiration time has passed (5 min buffer)

        Returns:
            True if token is valid, False otherwise
        """
        if not self._token_cache:
            return False

        expires_in = self._token_cache.get("expires_in", 0)
        elapsed = time.time() - self._last_token_time
        buffer_seconds = 300  # 5 minute buffer

        is_valid = elapsed < (expires_in - buffer_seconds)
        if not is_valid:
            logger.debug(
                "Cached token expired or expiring soon",
                extra={"elapsed": elapsed, "expires_in": expires_in},
            )
        return is_valid

    def _save_token_cache(self) -> None:
        """Save token cache to disk.

        Saves the current token to ~/.event_agent_token_cache.json for persistence.
        """
        try:
            self.cache_file.write_text(json.dumps(self._token_cache, indent=2))
            logger.debug(f"Saved token cache to {self.cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save token cache: {str(e)}")

    def _load_token_cache(self) -> None:
        """Load token cache from disk.

        Attempts to load cached token from ~/.event_agent_token_cache.json.
        If file doesn't exist or is invalid, starts with empty cache.
        """
        if not self.cache_file.exists():
            logger.debug("No cached token found")
            return

        try:
            cache_content = self.cache_file.read_text()
            self._token_cache = json.loads(cache_content)
            self._last_token_time = time.time()
            logger.debug("Loaded token cache from disk")
        except Exception as e:
            logger.warning(f"Failed to load token cache: {str(e)}")
            self._token_cache = {}
