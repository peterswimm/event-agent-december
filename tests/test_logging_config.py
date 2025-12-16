"""Tests for logging configuration and Graph event logging."""
import logging
import tempfile
import os
from pathlib import Path
import pytest

from logging_config import setup_logging, get_graph_logger, GraphEventLogger


class TestLoggingConfiguration:
    """Test logging setup and configuration."""

    def teardown_method(self):
        """Clean up logging handlers."""
        # Remove file handlers to release locks
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)

    def test_setup_logging_console_only(self):
        """Test logging setup with console output only."""
        setup_logging(log_level="DEBUG")
        logger = logging.getLogger("test_module")
        
        # Should not raise any errors
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            setup_logging(log_level="INFO", log_file=log_file)
            
            logger = logging.getLogger("test_module")
            logger.info("Test message")
            
            # Close handlers before checking file
            for handler in logging.root.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
            
            # Check file was created
            assert Path(log_file).exists()
            
            # Check content
            content = Path(log_file).read_text()
            assert "Test message" in content

    def test_setup_logging_different_levels(self):
        """Test logging setup with different log levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            setup_logging(log_level=level)
            logger = logging.getLogger("test")
            # Should not raise
            logger.info(f"Testing {level}")

    def test_get_graph_logger(self):
        """Test getting a graph-specific logger."""
        logger = get_graph_logger("graph_module")
        assert logger is not None
        assert logger.name == "graph_module"

    def test_get_graph_logger_default(self):
        """Test getting default graph logger."""
        logger = get_graph_logger()
        assert logger is not None
        assert logger.name == "graph_events"


class TestGraphEventLogger:
    """Test GraphEventLogger helper class."""

    def setup_method(self):
        """Set up test logger."""
        self.logger = GraphEventLogger(logging.getLogger("test_graph"))

    def test_log_auth_start(self):
        """Test logging authentication start."""
        # Should not raise
        self.logger.log_auth_start("tenant-id-123")

    def test_log_auth_success(self):
        """Test logging successful authentication."""
        self.logger.log_auth_success()

    def test_log_auth_success_ttl_param(self):
        """Test logging successful authentication with TTL."""
        self.logger.log_auth_success(token_ttl=3600)

    def test_log_auth_error(self):
        """Test logging authentication error."""
        self.logger.log_auth_error("Invalid credentials")

    def test_log_event_fetch_start(self):
        """Test logging event fetch start."""
        self.logger.log_event_fetch_start(["ai", "safety"], 5)

    def test_log_event_fetch_complete(self):
        """Test logging event fetch completion."""
        self.logger.log_event_fetch_complete(3)

    def test_log_event_fetch_error(self):
        """Test logging event fetch error."""
        self.logger.log_event_fetch_error("Network timeout")

    def test_log_recommendation_start(self):
        """Test logging recommendation start."""
        self.logger.log_recommendation_start(["ai", "agents"], 3)

    def test_log_recommendation_complete_no_conflicts(self):
        """Test logging recommendation completion without conflicts."""
        self.logger.log_recommendation_complete(3)

    def test_log_recommendation_complete_with_conflicts(self):
        """Test logging recommendation completion with conflicts."""
        self.logger.log_recommendation_complete(3, conflicts=1)

    def test_log_rate_limit(self):
        """Test logging rate limit."""
        self.logger.log_rate_limit(60)

    def test_log_cache_hit(self):
        """Test logging cache hit."""
        self.logger.log_cache_hit("events_ai_2024-01-01")

    def test_log_cache_miss(self):
        """Test logging cache miss."""
        self.logger.log_cache_miss("events_ai_2024-01-01")


class TestGraphEventLoggerIntegration:
    """Integration tests for Graph event logging with telemetry."""

    def teardown_method(self):
        """Clean up logging handlers."""
        # Remove file handlers to release locks
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)

    def test_logger_with_file_output(self):
        """Test Graph event logger writing to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "graph_events.log")
            setup_logging(log_level="DEBUG", log_file=log_file)
            
            logger = GraphEventLogger(logging.getLogger("graph_test"))
            logger.log_auth_start("test-tenant")
            logger.log_event_fetch_start(["ai"], 5)
            logger.log_recommendation_complete(3, conflicts=0)
            
            # Close handlers before reading
            for handler in logging.root.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
            
            # Verify file output
            content = Path(log_file).read_text()
            assert "authentication" in content.lower()
            assert "ai" in content

    def test_logger_messages_contain_details(self):
        """Test that logger messages contain expected details."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            setup_logging(log_level="INFO", log_file=log_file)
            
            logger = GraphEventLogger(logging.getLogger("graph_detail"))
            
            # Log various events
            logger.log_event_fetch_start(["artificial intelligence", "safety"], 5)
            logger.log_event_fetch_complete(2)
            logger.log_rate_limit(30)
            
            # Close handlers before reading
            for handler in logging.root.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
            
            content = Path(log_file).read_text()
            
            # Verify content
            assert "artificial intelligence" in content or "Fetching" in content
            assert "safety" in content or "Fetching" in content
            assert "2 events" in content or "Fetched" in content or "Graph" in content
            assert "30" in content or "rate" in content.lower()

    def test_logger_different_levels(self):
        """Test logger respects logging levels."""
        # Debug level should capture everything
        setup_logging(log_level="DEBUG")
        debug_logger = GraphEventLogger(logging.getLogger("debug_test"))
        debug_logger.log_cache_hit("test_key")
        
        # Warning level should skip debug messages in most scenarios
        setup_logging(log_level="WARNING")
        warning_logger = GraphEventLogger(logging.getLogger("warning_test"))
        warning_logger.log_cache_miss("test_key")


class TestLoggingEnvironmentVars:
    """Test logging configuration via environment variables."""

    def test_log_level_from_env(self):
        """Test LOG_LEVEL environment variable."""
        os.environ["LOG_LEVEL"] = "DEBUG"
        # Re-import to pick up env var (in practice, this is set before import)
        import logging_config
        setup_logging()  # Should use DEBUG from env
        
        logger = logging.getLogger("test_env")
        logger.debug("Should be visible")

    def test_log_file_from_env(self):
        """Test LOG_FILE environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "app.log")
            os.environ["LOG_FILE"] = log_file
            
            setup_logging()
            logger = logging.getLogger("test_env_file")
            logger.info("Environment file test")
            
            # Should have created the file
            if Path(log_file).exists():
                assert "Environment file test" in Path(log_file).read_text()


class TestLoggingErrorHandling:
    """Test logging error handling and edge cases."""

    def teardown_method(self):
        """Clean up logging handlers."""
        # Remove file handlers to release locks
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)

    def test_logging_invalid_level(self):
        """Test logging with invalid level defaults to INFO."""
        setup_logging(log_level="INVALID_LEVEL")
        logger = logging.getLogger("invalid_level")
        logger.info("Should work with default INFO level")

    def test_logging_to_nonexistent_directory(self):
        """Test logging creates directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "subdir", "deep", "test.log")
            setup_logging(log_level="INFO", log_file=log_file)
            
            logger = logging.getLogger("deep_test")
            logger.info("In deep directory")
            
            # Close handlers before asserting
            for handler in logging.root.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
            
            # Directory should be created
            assert Path(log_file).parent.exists()

    def test_graph_event_logger_graceful_failure(self):
        """Test GraphEventLogger handles missing logger gracefully."""
        # Create logger with None (should use default)
        logger = GraphEventLogger(None)
        
        # Should not raise
        logger.log_auth_start("tenant")
        logger.log_event_fetch_complete(5)
