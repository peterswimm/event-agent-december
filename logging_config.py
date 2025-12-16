"""Logging configuration for Event Agent.

This module sets up structured logging for the application with support for:
- File-based logging
- Console logging
- Graph-specific event logging
- Integration with telemetry
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """Configure application-wide logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, only console logging.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(levelname)s: %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (simple format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File gets detailed logs
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific loggers
    logging.getLogger('graph_auth').setLevel(level)
    logging.getLogger('graph_service').setLevel(level)
    logging.getLogger('core').setLevel(level)


def get_graph_logger(module_name: str = None) -> logging.Logger:
    """Get a logger configured for Graph-related operations.
    
    Args:
        module_name: Name of the module requesting logger (e.g., __name__)
        
    Returns:
        Configured logger instance
    """
    if module_name:
        return logging.getLogger(module_name)
    return logging.getLogger('graph_events')


class GraphEventLogger:
    """Helper class for structured Graph event logging."""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or get_graph_logger()
    
    def log_auth_start(self, tenant_id: str) -> None:
        """Log the start of authentication."""
        self.logger.debug(f"Starting Graph authentication for tenant: {tenant_id}")
    
    def log_auth_success(self, token_ttl: int = None) -> None:
        """Log successful authentication."""
        msg = "Graph authentication successful"
        if token_ttl:
            msg += f" (token TTL: {token_ttl}s)"
        self.logger.info(msg)
    
    def log_auth_error(self, error: str) -> None:
        """Log authentication error."""
        self.logger.error(f"Graph authentication failed: {error}")
    
    def log_event_fetch_start(self, interests: list, top_n: int) -> None:
        """Log the start of event fetching."""
        self.logger.info(
            f"Fetching Graph events for interests: {', '.join(interests)} (top {top_n})"
        )
    
    def log_event_fetch_complete(self, count: int) -> None:
        """Log completion of event fetching."""
        self.logger.info(f"Fetched {count} events from Microsoft Graph")
    
    def log_event_fetch_error(self, error: str) -> None:
        """Log event fetch error."""
        self.logger.error(f"Failed to fetch Graph events: {error}")
    
    def log_recommendation_start(self, interests: list, top_n: int) -> None:
        """Log start of recommendation process."""
        self.logger.info(
            f"Starting Graph-based recommendation for {', '.join(interests)} (top {top_n})"
        )
    
    def log_recommendation_complete(self, count: int, conflicts: int = 0) -> None:
        """Log recommendation completion."""
        msg = f"Graph recommendation completed: {count} sessions"
        if conflicts > 0:
            msg += f" ({conflicts} time conflicts detected)"
        self.logger.info(msg)
    
    def log_rate_limit(self, retry_after: int) -> None:
        """Log rate limit encountered."""
        self.logger.warning(
            f"Graph API rate limited - will retry after {retry_after}s"
        )
    
    def log_cache_hit(self, cache_key: str) -> None:
        """Log cache hit."""
        self.logger.debug(f"Graph event cache hit: {cache_key}")
    
    def log_cache_miss(self, cache_key: str) -> None:
        """Log cache miss."""
        self.logger.debug(f"Graph event cache miss: {cache_key}")


# Initialize logging when module is imported
_log_level = os.getenv('LOG_LEVEL', 'INFO')
_log_file = os.getenv('LOG_FILE', None)
setup_logging(log_level=_log_level, log_file=_log_file)
