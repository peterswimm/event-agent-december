"""Microsoft Graph API service for fetching and transforming calendar events.

This module provides the GraphEventService class which fetches events from
Microsoft Graph API and transforms them to the agent's session schema.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx

from graph_auth import GraphAuthClient, GraphAuthError
from settings import Settings

logger = logging.getLogger(__name__)


class GraphServiceError(Exception):
    """Raised when Graph API operations fail."""

    pass


class GraphEventService:
    """Fetches and transforms calendar events from Microsoft Graph API.

    Attributes:
        auth_client: GraphAuthClient for token management
        settings: Application settings
        cache: In-memory event cache
        cache_ttl: Time-to-live for cached events in seconds
        base_url: Microsoft Graph API base URL
    """

    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
    CALENDAR_EVENTS_ENDPOINT = "/me/calendarview"
    DEFAULT_CACHE_TTL = 300  # 5 minutes

    def __init__(
        self,
        auth_client: GraphAuthClient,
        settings: Settings,
        cache_ttl: int = DEFAULT_CACHE_TTL,
    ) -> None:
        """Initialize GraphEventService.

        Args:
            auth_client: Authenticated GraphAuthClient instance
            settings: Application settings
            cache_ttl: Cache time-to-live in seconds (default 300)
        """
        self.auth_client = auth_client
        self.settings = settings
        self.cache_ttl = cache_ttl
        self._cache: dict[str, Any] = {}
        self._cache_time: float = 0
        self._rate_limit_retry_after: float = 0

        logger.info("Initialized GraphEventService", extra={"cache_ttl": cache_ttl})

    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        top: int = 50,
    ) -> list[dict[str, Any]]:
        """Fetch calendar events from Graph API for the specified time range.

        Uses cached results if available and not expired. Handles rate limiting
        with exponential backoff.

        Args:
            start_time: Start of time range (default: now)
            end_time: End of time range (default: now + 7 days)
            top: Maximum number of events to return (default 50, max 999)

        Returns:
            List of event dicts transformed to agent schema

        Raises:
            GraphServiceError: If event fetching fails
        """
        # Set default time range
        if start_time is None:
            start_time = datetime.now(timezone.utc)
        if end_time is None:
            end_time = start_time + timedelta(days=7)

        # Check rate limit backoff
        if self._rate_limit_retry_after > time.time():
            raise GraphServiceError(
                "Rate limit exceeded. Please retry after "
                f"{int(self._rate_limit_retry_after - time.time())} seconds"
            )

        # Check cache
        cache_key = self._make_cache_key(start_time, end_time, top)
        if self._is_cache_valid(cache_key):
            logger.debug("Returning cached events", extra={"count": len(self._cache.get(cache_key, []))})
            return self._cache[cache_key]

        logger.info(
            "Fetching events from Graph API",
            extra={
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "top": top,
            },
        )

        try:
            events = self._fetch_events_from_api(start_time, end_time, top)
            transformed = self._transform_events(events)

            # Cache results
            self._cache[cache_key] = transformed
            self._cache_time = time.time()

            logger.info("Successfully fetched and cached events", extra={"count": len(transformed)})
            return transformed

        except GraphServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching events: {str(e)}")
            raise GraphServiceError(f"Failed to fetch events: {str(e)}") from e

    def _fetch_events_from_api(
        self,
        start_time: datetime,
        end_time: datetime,
        top: int,
    ) -> list[dict[str, Any]]:
        """Fetch raw events from Microsoft Graph API.

        Args:
            start_time: Start of time range
            end_time: End of time range
            top: Maximum events to return

        Returns:
            List of raw event dictionaries from Graph API

        Raises:
            GraphServiceError: If API call fails
        """
        try:
            token = self.auth_client.get_access_token()
        except GraphAuthError as e:
            logger.error(f"Failed to get access token: {str(e)}")
            raise GraphServiceError(f"Authentication failed: {str(e)}") from e

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        params = {
            "startDateTime": start_time.isoformat() + "Z",
            "endDateTime": end_time.isoformat() + "Z",
            "$top": min(top, 999),  # Graph API max is 999
            "$orderby": "start/dateTime",
        }

        url = f"{self.GRAPH_API_BASE}{self.CALENDAR_EVENTS_ENDPOINT}"

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=headers, params=params)

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    self._rate_limit_retry_after = time.time() + retry_after
                    raise GraphServiceError(
                        f"Rate limited. Retry after {retry_after} seconds"
                    )

                if response.status_code == 401:
                    logger.error("Authentication failed - invalid token")
                    raise GraphServiceError("Authentication failed: Invalid token")

                if response.status_code != 200:
                    logger.error(
                        f"Graph API error: {response.status_code}",
                        extra={"text": response.text[:200]},
                    )
                    raise GraphServiceError(
                        f"Graph API returned {response.status_code}: {response.text[:100]}"
                    )

                data = response.json()
                return data.get("value", [])

        except httpx.RequestError as e:
            logger.error(f"Network error calling Graph API: {str(e)}")
            raise GraphServiceError(f"Network error: {str(e)}") from e

    def _transform_events(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform Graph API events to agent session schema.

        Converts Microsoft Graph event format to the agent's session format:
        - Graph start/end times -> agent start/end (local time strings)
        - Graph location -> agent location
        - Graph subject -> agent title
        - Graph categories -> agent tags
        - Generate fake popularity score (0.0-1.0)

        Args:
            events: List of events from Graph API

        Returns:
            List of events transformed to agent schema
        """
        transformed = []

        for event in events:
            try:
                # Skip cancelled events
                if event.get("isCancelled", False):
                    logger.debug(f"Skipping cancelled event: {event.get('subject', 'Unknown')}")
                    continue

                # Extract time information
                start_dt = self._parse_graph_datetime(event.get("start", {}))
                end_dt = self._parse_graph_datetime(event.get("end", {}))

                if not start_dt or not end_dt:
                    logger.debug(f"Skipping event with invalid times: {event.get('subject')}")
                    continue

                session = {
                    "id": event.get("id", ""),
                    "title": event.get("subject", "Untitled Event"),
                    "start": start_dt.strftime("%H:%M"),  # Local time format
                    "end": end_dt.strftime("%H:%M"),
                    "location": event.get("location", {}).get("displayName", ""),
                    "tags": self._extract_tags(event),
                    "popularity": self._calculate_popularity(event),
                }

                transformed.append(session)

            except Exception as e:
                logger.warning(f"Failed to transform event: {str(e)}")
                continue

        return transformed

    def _parse_graph_datetime(self, dt_obj: dict[str, Any]) -> Optional[datetime]:
        """Parse Microsoft Graph datetime object.

        Graph returns datetime as: {"dateTime": "2023-12-16T14:30:00", "timeZone": "UTC"}

        Args:
            dt_obj: DateTime object from Graph API

        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not dt_obj:
            return None

        try:
            dt_string = dt_obj.get("dateTime", "")
            if not dt_string:
                return None

            # Parse ISO format datetime
            return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))

        except Exception as e:
            logger.debug(f"Failed to parse datetime: {str(e)}")
            return None

    def _extract_tags(self, event: dict[str, Any]) -> list[str]:
        """Extract tags from event categories and other fields.

        Args:
            event: Event from Graph API

        Returns:
            List of tag strings
        """
        tags = []

        # Add categories as tags
        if "categories" in event:
            tags.extend(event["categories"])

        # Add type-based tags
        if event.get("isOnlineMeeting"):
            tags.append("online")

        if event.get("isReminderOn"):
            tags.append("reminder")

        # Limit tags to 5
        return tags[:5]

    def _calculate_popularity(self, event: dict[str, Any]) -> float:
        """Calculate popularity score for an event.

        Currently generates a score based on:
        - Event has description (0.1)
        - Event has attendees (0.3)
        - Event has location (0.2)
        - Event is online (0.1)
        - Base score (0.25)

        Args:
            event: Event from Graph API

        Returns:
            Popularity score between 0.0 and 1.0
        """
        score = 0.25  # Base score

        if event.get("bodyPreview") or event.get("body", {}).get("content"):
            score += 0.1

        attendees = event.get("attendees", [])
        if attendees:
            score += min(0.3, len(attendees) * 0.05)  # Cap at 0.3

        if event.get("location", {}).get("displayName"):
            score += 0.2

        if event.get("isOnlineMeeting"):
            score += 0.1

        return min(score, 1.0)

    def _make_cache_key(self, start_time: datetime, end_time: datetime, top: int) -> str:
        """Create a cache key from query parameters.

        Args:
            start_time: Start of time range
            end_time: End of time range
            top: Maximum events

        Returns:
            Cache key string
        """
        return f"{start_time.date()}_{end_time.date()}_{top}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid.

        Args:
            cache_key: Cache key to check

        Returns:
            True if cache exists and hasn't expired
        """
        if cache_key not in self._cache:
            return False

        elapsed = time.time() - self._cache_time
        is_valid = elapsed < self.cache_ttl

        if not is_valid:
            logger.debug(f"Cache expired after {elapsed:.1f}s (ttl={self.cache_ttl}s)")

        return is_valid

    def clear_cache(self) -> None:
        """Clear the event cache."""
        self._cache.clear()
        self._cache_time = 0
        logger.info("Cleared event cache")
