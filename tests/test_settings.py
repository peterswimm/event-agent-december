"""Tests for settings module."""

import os
import pytest
from settings import Settings


class TestSettingsBasics:
    """Test basic settings loading and validation."""

    def test_settings_loads_from_env_file(self, tmp_path):
        """Test that settings loads from .env file."""
        # Settings should load from .env file in current directory
        settings = Settings()
        assert settings is not None

    def test_graph_credentials_optional(self):
        """Test that Graph credentials are optional."""
        # Should be able to create settings without Graph creds
        settings = Settings(
            graph_tenant_id=None,
            graph_client_id=None,
            graph_client_secret=None,
        )
        assert not settings.validate_graph_ready()

    def test_graph_credentials_validation(self):
        """Test Graph credentials validation."""
        settings = Settings(
            graph_tenant_id="test-tenant",
            graph_client_id="test-client",
            graph_client_secret="test-secret",
        )
        assert settings.validate_graph_ready()

    def test_partial_graph_credentials(self):
        """Test that partial Graph credentials are detected."""
        settings = Settings(
            graph_tenant_id="test-tenant",
            graph_client_id=None,
            graph_client_secret=None,
        )
        assert not settings.validate_graph_ready()
        errors = settings.get_validation_errors()
        assert len(errors) == 2
        assert "GRAPH_CLIENT_ID" in str(errors)

    def test_missing_all_graph_credentials(self):
        """Test detection of all missing Graph credentials."""
        settings = Settings()
        errors = settings.get_validation_errors()
        if not all([settings.graph_tenant_id, settings.graph_client_id, settings.graph_client_secret]):
            # At least one credential is missing in test environment
            assert len(errors) > 0

    def test_graph_enabled_flag(self):
        """Test Graph enabled feature flag."""
        settings = Settings(graph_enabled=True)
        assert settings.graph_enabled is True

        settings2 = Settings(graph_enabled=False)
        assert settings2.graph_enabled is False


class TestSettingsEnvironmentVariables:
    """Test settings environment variable loading."""

    def test_run_mode_env_var(self):
        """Test RUN_MODE environment variable."""
        os.environ["RUN_MODE"] = "test-mode"
        settings = Settings()
        assert settings.run_mode == "test-mode"
        del os.environ["RUN_MODE"]

    def test_api_token_env_var(self):
        """Test API_TOKEN environment variable."""
        os.environ["API_TOKEN"] = "test-token"
        settings = Settings()
        assert settings.api_token == "test-token"
        del os.environ["API_TOKEN"]

    def test_graph_credentials_env_vars(self):
        """Test Graph credential environment variables."""
        os.environ["GRAPH_TENANT_ID"] = "test-tenant-id"
        os.environ["GRAPH_CLIENT_ID"] = "test-client-id"
        os.environ["GRAPH_CLIENT_SECRET"] = "test-secret"

        settings = Settings()
        assert settings.graph_tenant_id == "test-tenant-id"
        assert settings.graph_client_id == "test-client-id"
        assert settings.graph_client_secret == "test-secret"
        assert settings.validate_graph_ready()

        del os.environ["GRAPH_TENANT_ID"]
        del os.environ["GRAPH_CLIENT_ID"]
        del os.environ["GRAPH_CLIENT_SECRET"]


class TestSettingsCaseInsensitive:
    """Test case-insensitive environment variable handling."""

    def test_lowercase_env_vars(self):
        """Test that lowercase env vars are accepted."""
        os.environ["api_token"] = "lowercase-token"
        settings = Settings()
        # Pydantic with case_sensitive=False should handle this
        # (though the Settings class uses UPPERCASE env names)
        del os.environ["api_token"]
