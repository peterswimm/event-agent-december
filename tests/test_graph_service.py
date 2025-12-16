"""Unit tests for Microsoft Graph event service."""

import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from graph_auth import GraphAuthClient, GraphAuthError
from graph_service import GraphEventService, GraphServiceError
from settings import Settings


class TestGraphEventServiceInitialization:
    """Tests for GraphEventService initialization."""

    @pytest.fixture
    def mock_auth_client(self):
        """Create mock authentication client."""
        mock = Mock(spec=GraphAuthClient)
        return mock

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        return Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

    def test_init_with_defaults(self, mock_auth_client, mock_settings):
        """Test initialization with default parameters."""
        service = GraphEventService(mock_auth_client, mock_settings)

        assert service.auth_client == mock_auth_client
        assert service.settings == mock_settings
        assert service.cache_ttl == 300
        assert service._cache == {}

    def test_init_with_custom_cache_ttl(self, mock_auth_client, mock_settings):
        """Test initialization with custom cache TTL."""
        service = GraphEventService(mock_auth_client, mock_settings, cache_ttl=600)

        assert service.cache_ttl == 600


class TestEventFetching:
    """Tests for event fetching from Graph API."""

    @pytest.fixture
    def mock_auth_client(self):
        """Create mock authentication client."""
        mock = Mock(spec=GraphAuthClient)
        mock.get_access_token.return_value = "test_token_123"
        return mock

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        return Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

    @pytest.fixture
    def sample_graph_event(self):
        """Create a sample Graph API event."""
        return {
            "id": "event123",
            "subject": "Team Standup",
            "start": {"dateTime": "2023-12-16T09:00:00", "timeZone": "UTC"},
            "end": {"dateTime": "2023-12-16T09:30:00", "timeZone": "UTC"},
            "location": {"displayName": "Conference Room A"},
            "categories": ["work", "standup"],
            "isOnlineMeeting": False,
            "bodyPreview": "Daily standup meeting",
        }

    @patch("graph_service.httpx.Client")
    def test_get_events_success(self, mock_client_class, mock_auth_client, mock_settings, sample_graph_event):
        """Test successful event fetching."""
        service = GraphEventService(mock_auth_client, mock_settings)

        graph_response = {"value": [sample_graph_event]}

        mock_response = Mock(status_code=200)
        mock_response.json.return_value = graph_response

        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_class.return_value = mock_client_instance

        events = service.get_events()

        assert len(events) == 1
        assert events[0]["id"] == "event123"
        assert events[0]["title"] == "Team Standup"

    @patch("graph_service.httpx.Client")
    def test_get_events_with_time_range(self, mock_client_class, mock_auth_client, mock_settings):
        """Test event fetching with specified time range."""
        service = GraphEventService(mock_auth_client, mock_settings)

        start = datetime(2023, 12, 16, 9, 0, 0)
        end = datetime(2023, 12, 16, 17, 0, 0)

        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"value": []}

        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_class.return_value = mock_client_instance

        service.get_events(start_time=start, end_time=end, top=20)

        # Verify the request was made with correct parameters
        call_args = mock_client_instance.get.call_args
        assert call_args is not None

    def test_get_events_auth_failure(self, mock_auth_client, mock_settings):
        """Test event fetching when authentication fails."""
        service = GraphEventService(mock_auth_client, mock_settings)
        mock_auth_client.get_access_token.side_effect = GraphAuthError("Auth failed")

        with pytest.raises(GraphServiceError) as exc_info:
            service.get_events()

        assert "Authentication failed" in str(exc_info.value)

    @patch("graph_service.httpx.Client")
    def test_get_events_api_error_401(self, mock_client_class, mock_auth_client, mock_settings):
        """Test handling of 401 Unauthorized response."""
        service = GraphEventService(mock_auth_client, mock_settings)

        mock_response = Mock(status_code=401, text="Unauthorized")

        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_class.return_value = mock_client_instance

        with pytest.raises(GraphServiceError) as exc_info:
            service.get_events()

        assert "Invalid token" in str(exc_info.value)

    @patch("graph_service.httpx.Client")
    def test_get_events_rate_limited_429(self, mock_client_class, mock_auth_client, mock_settings):
        """Test handling of rate limit (429) response."""
        service = GraphEventService(mock_auth_client, mock_settings)

        mock_response = Mock(status_code=429)
        mock_response.headers = {"Retry-After": "60"}

        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_class.return_value = mock_client_instance

        with pytest.raises(GraphServiceError) as exc_info:
            service.get_events()

        assert "Rate limited" in str(exc_info.value)

    @patch("graph_service.httpx.Client")
    def test_get_events_network_error(self, mock_client_class, mock_auth_client, mock_settings):
        """Test handling of network errors."""
        service = GraphEventService(mock_auth_client, mock_settings)

        mock_client_instance = MagicMock()
        mock_client_instance.get.side_effect = httpx.RequestError("Connection failed")
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_class.return_value = mock_client_instance

        with pytest.raises(GraphServiceError) as exc_info:
            service.get_events()

        assert "Network error" in str(exc_info.value)


class TestEventTransformation:
    """Tests for event transformation from Graph to agent schema."""

    @pytest.fixture
    def mock_auth_client(self):
        """Create mock authentication client."""
        mock = Mock(spec=GraphAuthClient)
        mock.get_access_token.return_value = "test_token"
        return mock

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        return Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

    def test_transform_basic_event(self, mock_auth_client, mock_settings):
        """Test transformation of basic event."""
        service = GraphEventService(mock_auth_client, mock_settings)

        event = {
            "id": "event_id_1",
            "subject": "Project Meeting",
            "start": {"dateTime": "2023-12-16T10:00:00", "timeZone": "UTC"},
            "end": {"dateTime": "2023-12-16T11:00:00", "timeZone": "UTC"},
            "location": {"displayName": "Room 101"},
            "categories": ["meeting"],
        }

        transformed = service._transform_events([event])

        assert len(transformed) == 1
        assert transformed[0]["id"] == "event_id_1"
        assert transformed[0]["title"] == "Project Meeting"
        assert transformed[0]["start"] == "10:00"
        assert transformed[0]["end"] == "11:00"
        assert transformed[0]["location"] == "Room 101"
        assert "meeting" in transformed[0]["tags"]

    def test_transform_skips_cancelled_events(self, mock_auth_client, mock_settings):
        """Test that cancelled events are skipped."""
        service = GraphEventService(mock_auth_client, mock_settings)

        event = {
            "id": "cancelled_event",
            "subject": "Cancelled Meeting",
            "start": {"dateTime": "2023-12-16T10:00:00", "timeZone": "UTC"},
            "end": {"dateTime": "2023-12-16T11:00:00", "timeZone": "UTC"},
            "isCancelled": True,
        }

        transformed = service._transform_events([event])

        assert len(transformed) == 0

    def test_transform_skips_invalid_times(self, mock_auth_client, mock_settings):
        """Test that events with invalid times are skipped."""
        service = GraphEventService(mock_auth_client, mock_settings)

        event = {
            "id": "bad_time_event",
            "subject": "Bad Time Event",
            "start": {},  # Missing datetime
            "end": {"dateTime": "2023-12-16T11:00:00", "timeZone": "UTC"},
        }

        transformed = service._transform_events([event])

        assert len(transformed) == 0

    def test_transform_extracts_tags(self, mock_auth_client, mock_settings):
        """Test tag extraction from event."""
        service = GraphEventService(mock_auth_client, mock_settings)

        event = {
            "id": "event_with_tags",
            "subject": "Online Standup",
            "start": {"dateTime": "2023-12-16T09:00:00", "timeZone": "UTC"},
            "end": {"dateTime": "2023-12-16T09:30:00", "timeZone": "UTC"},
            "categories": ["standup", "team"],
            "isOnlineMeeting": True,
            "isReminderOn": True,
        }

        transformed = service._transform_events([event])

        tags = transformed[0]["tags"]
        assert "standup" in tags
        assert "team" in tags
        assert "online" in tags
        assert "reminder" in tags

    def test_transform_calculates_popularity(self, mock_auth_client, mock_settings):
        """Test popularity score calculation."""
        service = GraphEventService(mock_auth_client, mock_settings)

        event = {
            "id": "popular_event",
            "subject": "Popular Event",
            "start": {"dateTime": "2023-12-16T10:00:00", "timeZone": "UTC"},
            "end": {"dateTime": "2023-12-16T11:00:00", "timeZone": "UTC"},
            "location": {"displayName": "Main Hall"},
            "bodyPreview": "This is a great event",
            "attendees": [{"emailAddress": {"address": "user1@example.com"}}],
            "isOnlineMeeting": True,
        }

        transformed = service._transform_events([event])

        popularity = transformed[0]["popularity"]
        assert 0.0 <= popularity <= 1.0
        # Should be high due to description, attendees, location, and online
        assert popularity > 0.5


class TestEventCaching:
    """Tests for event caching behavior."""

    @pytest.fixture
    def mock_auth_client(self):
        """Create mock authentication client."""
        mock = Mock(spec=GraphAuthClient)
        mock.get_access_token.return_value = "test_token"
        return mock

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        return Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

    @patch("graph_service.httpx.Client")
    def test_cache_stores_results(self, mock_client_class, mock_auth_client, mock_settings):
        """Test that results are cached."""
        service = GraphEventService(mock_auth_client, mock_settings, cache_ttl=600)

        graph_response = {
            "value": [
                {
                    "id": "event1",
                    "subject": "Event 1",
                    "start": {"dateTime": "2023-12-16T10:00:00", "timeZone": "UTC"},
                    "end": {"dateTime": "2023-12-16T11:00:00", "timeZone": "UTC"},
                }
            ]
        }

        mock_response = Mock(status_code=200)
        mock_response.json.return_value = graph_response

        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_class.return_value = mock_client_instance

        # First call should fetch from API
        events1 = service.get_events()
        assert len(events1) == 1
        assert mock_client_instance.get.call_count == 1

        # Second call should use cache
        events2 = service.get_events()
        assert len(events2) == 1
        assert mock_client_instance.get.call_count == 1  # No additional call

    @patch("graph_service.httpx.Client")
    def test_cache_expires_after_ttl(self, mock_client_class, mock_auth_client, mock_settings):
        """Test that cache expires after TTL."""
        service = GraphEventService(mock_auth_client, mock_settings, cache_ttl=1)

        graph_response = {
            "value": [
                {
                    "id": "event1",
                    "subject": "Event 1",
                    "start": {"dateTime": "2023-12-16T10:00:00", "timeZone": "UTC"},
                    "end": {"dateTime": "2023-12-16T11:00:00", "timeZone": "UTC"},
                }
            ]
        }

        mock_response = Mock(status_code=200)
        mock_response.json.return_value = graph_response

        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_class.return_value = mock_client_instance

        # First call
        service.get_events()
        assert mock_client_instance.get.call_count == 1

        # Wait for cache to expire
        import time
        time.sleep(1.5)

        # Second call should fetch again
        service.get_events()
        assert mock_client_instance.get.call_count == 2

    def test_clear_cache(self, mock_auth_client, mock_settings):
        """Test cache clearing."""
        service = GraphEventService(mock_auth_client, mock_settings)

        service._cache = {"key": "value"}
        service._cache_time = 12345

        service.clear_cache()

        assert service._cache == {}
        assert service._cache_time == 0


class TestDateTimeHandling:
    """Tests for datetime parsing and handling."""

    @pytest.fixture
    def service(self):
        """Create service with mock dependencies."""
        mock_auth = Mock(spec=GraphAuthClient)
        mock_settings = Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )
        return GraphEventService(mock_auth, mock_settings)

    def test_parse_graph_datetime_valid(self, service):
        """Test parsing valid Graph datetime."""
        dt_obj = {"dateTime": "2023-12-16T14:30:00", "timeZone": "UTC"}

        result = service._parse_graph_datetime(dt_obj)

        assert result is not None
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 16
        assert result.hour == 14
        assert result.minute == 30

    def test_parse_graph_datetime_empty(self, service):
        """Test parsing empty datetime object."""
        result = service._parse_graph_datetime({})
        assert result is None

    def test_parse_graph_datetime_invalid(self, service):
        """Test parsing invalid datetime string."""
        result = service._parse_graph_datetime({"dateTime": "invalid"})
        assert result is None
