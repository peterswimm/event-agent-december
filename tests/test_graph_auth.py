"""Unit tests for Microsoft Graph authentication module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from graph_auth import GraphAuthClient, GraphAuthError
from settings import Settings


class TestGraphAuthClientInitialization:
    """Tests for GraphAuthClient initialization."""

    def test_init_with_valid_credentials(self):
        """Test initialization with all required credentials."""
        settings = Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

        with patch("graph_auth.msal.ConfidentialClientApplication"):
            with patch.object(GraphAuthClient, "_load_token_cache"):
                client = GraphAuthClient(settings)
                assert client.settings == settings
                assert client._app is not None
                assert client._token_cache == {}

    def test_init_missing_tenant_id(self):
        """Test initialization fails without tenant_id."""
        settings = Settings(
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

        with pytest.raises(GraphAuthError) as exc_info:
            GraphAuthClient(settings)

        assert "GRAPH_TENANT_ID not set" in str(exc_info.value)

    def test_init_missing_client_id(self):
        """Test initialization fails without client_id."""
        settings = Settings(
            graph_tenant_id="tenant123",
            graph_client_secret="secret789",
        )

        with pytest.raises(GraphAuthError) as exc_info:
            GraphAuthClient(settings)

        assert "GRAPH_CLIENT_ID not set" in str(exc_info.value)

    def test_init_missing_client_secret(self):
        """Test initialization fails without client_secret."""
        settings = Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
        )

        with pytest.raises(GraphAuthError) as exc_info:
            GraphAuthClient(settings)

        assert "GRAPH_CLIENT_SECRET not set" in str(exc_info.value)

    def test_init_creates_cache_file_path(self):
        """Test that cache file path is set correctly."""
        settings = Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

        with patch("graph_auth.msal.ConfidentialClientApplication"):
            client = GraphAuthClient(settings)
            assert client.cache_file == Path.home() / ".event_agent_token_cache.json"


class TestTokenAcquisition:
    """Tests for token acquisition."""

    @pytest.fixture
    def mock_settings(self):
        """Create settings with Graph credentials."""
        return Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

    @pytest.fixture
    def mock_msal_app(self):
        """Create mock MSAL app."""
        mock = Mock()
        mock.acquire_token_for_client.return_value = {
            "access_token": "token123",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        return mock

    def test_acquire_token_for_client_success(self, mock_settings, mock_msal_app):
        """Test successful token acquisition."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            client = GraphAuthClient(mock_settings)

            result = client._acquire_token_for_client()

            assert result["access_token"] == "token123"
            assert result["expires_in"] == 3600
            mock_msal_app.acquire_token_for_client.assert_called_once_with(
                scopes=["https://graph.microsoft.com/.default"]
            )

    def test_acquire_token_for_client_error(self, mock_settings, mock_msal_app):
        """Test token acquisition failure."""
        mock_msal_app.acquire_token_for_client.return_value = {
            "error": "invalid_client",
            "error_description": "Client authentication failed",
        }

        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            client = GraphAuthClient(mock_settings)

            with pytest.raises(GraphAuthError) as exc_info:
                client._acquire_token_for_client()

            assert "invalid_client" in str(exc_info.value)

    def test_acquire_token_for_client_exception(self, mock_settings, mock_msal_app):
        """Test token acquisition exception handling."""
        mock_msal_app.acquire_token_for_client.side_effect = ConnectionError("Network error")

        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            client = GraphAuthClient(mock_settings)

            with pytest.raises(GraphAuthError) as exc_info:
                client._acquire_token_for_client()

            assert "Network error" in str(exc_info.value)


class TestTokenCaching:
    """Tests for token caching behavior."""

    @pytest.fixture
    def mock_settings(self):
        """Create settings with Graph credentials."""
        return Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

    @pytest.fixture
    def mock_msal_app(self):
        """Create mock MSAL app."""
        mock = Mock()
        mock.acquire_token_for_client.return_value = {
            "access_token": "token123",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        return mock

    def test_get_access_token_returns_cached_token(self, mock_settings, mock_msal_app):
        """Test that valid cached token is returned without new acquisition."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            with patch("graph_auth.time.time", return_value=100):
                client = GraphAuthClient(mock_settings)
                # Pre-populate cache with fresh token
                client._token_cache = {
                    "access_token": "cached_token",
                    "expires_in": 3600,
                }
                client._last_token_time = 100  # Current time

                token = client.get_access_token()

                assert token == "cached_token"
                mock_msal_app.acquire_token_for_client.assert_not_called()

    def test_get_access_token_acquires_new_on_cache_miss(self, mock_settings, mock_msal_app):
        """Test that new token is acquired when cache is empty."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            with patch.object(GraphAuthClient, "_load_token_cache"):
                client = GraphAuthClient(mock_settings)

                with patch.object(client, "_save_token_cache"):
                    token = client.get_access_token()

                assert token == "token123"
                mock_msal_app.acquire_token_for_client.assert_called_once()

    def test_get_access_token_refreshes_expired_token(self, mock_settings, mock_msal_app):
        """Test that expired token is refreshed."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            client = GraphAuthClient(mock_settings)
            # Simulate expired cache
            client._token_cache = {
                "access_token": "old_token",
                "expires_in": 3600,
            }
            client._last_token_time = -10000  # Very old timestamp

            with patch.object(client, "_save_token_cache"):
                token = client.get_access_token()

            assert token == "token123"
            assert mock_msal_app.acquire_token_for_client.call_count >= 1

    def test_is_token_valid_with_fresh_token(self, mock_settings, mock_msal_app):
        """Test token validity check for fresh token."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            with patch("graph_auth.time.time", return_value=100):
                client = GraphAuthClient(mock_settings)
                client._token_cache = {"access_token": "token", "expires_in": 3600}
                client._last_token_time = 100  # Current time

                is_valid = client._is_token_valid()

                assert is_valid

    def test_is_token_valid_with_empty_cache(self, mock_settings, mock_msal_app):
        """Test token validity check with empty cache."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            with patch.object(GraphAuthClient, "_load_token_cache"):
                client = GraphAuthClient(mock_settings)

                is_valid = client._is_token_valid()

                assert not is_valid

    def test_is_token_valid_with_expiring_token(self, mock_settings, mock_msal_app):
        """Test token validity check for token near expiration."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            client = GraphAuthClient(mock_settings)
            client._token_cache = {"access_token": "token", "expires_in": 100}
            client._last_token_time = 0  # 100+ seconds ago

            is_valid = client._is_token_valid()

            assert not is_valid  # Should be invalid (expired + buffer)


class TestTokenPersistence:
    """Tests for token cache file persistence."""

    @pytest.fixture
    def mock_settings(self):
        """Create settings with Graph credentials."""
        return Settings(
            graph_tenant_id="tenant123",
            graph_client_id="client456",
            graph_client_secret="secret789",
        )

    @pytest.fixture
    def mock_msal_app(self):
        """Create mock MSAL app."""
        mock = Mock()
        mock.acquire_token_for_client.return_value = {
            "access_token": "token123",
            "expires_in": 3600,
        }
        return mock

    def test_save_token_cache(self, mock_settings, mock_msal_app):
        """Test saving token cache to file."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            client = GraphAuthClient(mock_settings)

            # Use temporary file for testing
            with tempfile.TemporaryDirectory() as tmpdir:
                client.cache_file = Path(tmpdir) / "token_cache.json"
                client._token_cache = {"access_token": "token123", "expires_in": 3600}

                client._save_token_cache()

                assert client.cache_file.exists()
                cached = json.loads(client.cache_file.read_text())
                assert cached["access_token"] == "token123"

    def test_load_token_cache(self, mock_settings, mock_msal_app):
        """Test loading token cache from file."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            client = GraphAuthClient(mock_settings)

            with tempfile.TemporaryDirectory() as tmpdir:
                cache_file = Path(tmpdir) / "token_cache.json"
                cache_data = {"access_token": "loaded_token", "expires_in": 3600}
                cache_file.write_text(json.dumps(cache_data))

                client.cache_file = cache_file
                client._load_token_cache()

                assert client._token_cache == cache_data

    def test_load_token_cache_missing_file(self, mock_settings, mock_msal_app):
        """Test loading token cache when file doesn't exist."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            with patch.object(GraphAuthClient, "_load_token_cache"):
                client = GraphAuthClient(mock_settings)

            with tempfile.TemporaryDirectory() as tmpdir:
                client.cache_file = Path(tmpdir) / "nonexistent.json"
                client._load_token_cache()

                assert client._token_cache == {}

    def test_load_token_cache_invalid_json(self, mock_settings, mock_msal_app):
        """Test loading corrupted token cache file."""
        with patch("graph_auth.msal.ConfidentialClientApplication", return_value=mock_msal_app):
            client = GraphAuthClient(mock_settings)

            with tempfile.TemporaryDirectory() as tmpdir:
                cache_file = Path(tmpdir) / "token_cache.json"
                cache_file.write_text("invalid json {{{")

                client.cache_file = cache_file
                client._load_token_cache()

                assert client._token_cache == {}
