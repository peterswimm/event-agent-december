"""Tests for security features: input validation and rate limiting."""

import pytest
import time
from agent import SecurityValidator, RateLimiter


class TestSecurityValidator:
    """Tests for input validation."""

    def test_validate_interests_valid(self):
        """Test valid interests string."""
        is_valid, error = SecurityValidator.validate_interests("ai, machine learning, agents")
        assert is_valid
        assert error == ""

    def test_validate_interests_empty(self):
        """Test empty interests string."""
        is_valid, error = SecurityValidator.validate_interests("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_validate_interests_too_long(self):
        """Test interests string exceeding max length."""
        long_string = "a" * (SecurityValidator.MAX_INTERESTS_LENGTH + 1)
        is_valid, error = SecurityValidator.validate_interests(long_string)
        assert not is_valid
        assert "too long" in error.lower()

    def test_validate_interests_invalid_characters(self):
        """Test interests with invalid characters."""
        is_valid, error = SecurityValidator.validate_interests("ai; drop table sessions;")
        assert not is_valid
        assert "invalid characters" in error.lower()

    def test_validate_interests_with_hyphens(self):
        """Test interests with hyphens (valid)."""
        is_valid, error = SecurityValidator.validate_interests("machine-learning, ai-safety")
        assert is_valid
        assert error == ""

    def test_validate_user_id_valid(self):
        """Test valid email format."""
        is_valid, error = SecurityValidator.validate_user_id("user@example.com")
        assert is_valid
        assert error == ""

    def test_validate_user_id_empty(self):
        """Test empty user ID."""
        is_valid, error = SecurityValidator.validate_user_id("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_validate_user_id_invalid_format(self):
        """Test invalid email format."""
        is_valid, error = SecurityValidator.validate_user_id("not-an-email")
        assert not is_valid
        assert "valid email" in error.lower()

    def test_validate_user_id_too_long(self):
        """Test user ID exceeding max length."""
        long_email = "a" * 250 + "@example.com"
        is_valid, error = SecurityValidator.validate_user_id(long_email)
        assert not is_valid
        assert "too long" in error.lower()

    def test_validate_session_title_valid(self):
        """Test valid session title."""
        is_valid, error = SecurityValidator.validate_session_title("AI Safety: Best Practices")
        assert is_valid
        assert error == ""

    def test_validate_session_title_empty(self):
        """Test empty session title."""
        is_valid, error = SecurityValidator.validate_session_title("")
        assert not is_valid
        assert "empty" in error.lower()

    def test_validate_session_title_too_long(self):
        """Test session title exceeding max length."""
        long_title = "a" * (SecurityValidator.MAX_TITLE_LENGTH + 1)
        is_valid, error = SecurityValidator.validate_session_title(long_title)
        assert not is_valid
        assert "too long" in error.lower()

    def test_validate_session_title_invalid_characters(self):
        """Test session title with invalid characters."""
        is_valid, error = SecurityValidator.validate_session_title("Session <script>alert('xss')</script>")
        assert not is_valid
        assert "invalid characters" in error.lower()

    def test_validate_session_title_with_punctuation(self):
        """Test session title with common punctuation (valid)."""
        is_valid, error = SecurityValidator.validate_session_title("AI Agents: What's Next? (Part 1)")
        assert is_valid
        assert error == ""


class TestRateLimiter:
    """Tests for rate limiting."""

    def test_rate_limiter_allows_first_request(self):
        """Test that first request from IP is allowed."""
        limiter = RateLimiter(requests_per_minute=10, window_seconds=60)
        assert limiter.is_allowed("192.168.1.1")

    def test_rate_limiter_allows_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(requests_per_minute=5, window_seconds=60)
        ip = "192.168.1.2"
        
        for i in range(5):
            assert limiter.is_allowed(ip), f"Request {i+1} should be allowed"

    def test_rate_limiter_blocks_over_limit(self):
        """Test that requests exceeding limit are blocked."""
        limiter = RateLimiter(requests_per_minute=3, window_seconds=60)
        ip = "192.168.1.3"
        
        # First 3 requests should pass
        for i in range(3):
            assert limiter.is_allowed(ip), f"Request {i+1} should be allowed"
        
        # 4th request should be blocked
        assert not limiter.is_allowed(ip), "Request 4 should be blocked"

    def test_rate_limiter_different_ips(self):
        """Test that different IPs have independent limits."""
        limiter = RateLimiter(requests_per_minute=2, window_seconds=60)
        
        # IP1 makes 2 requests
        assert limiter.is_allowed("192.168.1.4")
        assert limiter.is_allowed("192.168.1.4")
        assert not limiter.is_allowed("192.168.1.4")  # Blocked
        
        # IP2 should still be allowed
        assert limiter.is_allowed("192.168.1.5")
        assert limiter.is_allowed("192.168.1.5")

    def test_rate_limiter_window_expiry(self):
        """Test that requests are allowed again after window expires."""
        limiter = RateLimiter(requests_per_minute=2, window_seconds=1)  # 1 second window
        ip = "192.168.1.6"
        
        # Fill the quota
        assert limiter.is_allowed(ip)
        assert limiter.is_allowed(ip)
        assert not limiter.is_allowed(ip)  # Blocked
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.is_allowed(ip)

    def test_rate_limiter_cleanup(self):
        """Test cleanup of old IP entries."""
        limiter = RateLimiter(requests_per_minute=5, window_seconds=1)
        
        # Make requests from multiple IPs
        for i in range(10):
            limiter.is_allowed(f"192.168.1.{i}")
        
        # Verify entries exist
        assert len(limiter.request_log) == 10
        
        # Wait for window to expire
        time.sleep(2.5)
        
        # Cleanup should remove old entries
        limiter.cleanup_old_entries()
        assert len(limiter.request_log) == 0

    def test_rate_limiter_partial_window(self):
        """Test that old requests don't count toward current limit."""
        limiter = RateLimiter(requests_per_minute=3, window_seconds=2)
        ip = "192.168.1.7"
        
        # Make 2 requests
        assert limiter.is_allowed(ip)
        assert limiter.is_allowed(ip)
        
        # Wait 2.1 seconds (outside window)
        time.sleep(2.1)
        
        # Should be able to make 3 more requests
        assert limiter.is_allowed(ip)
        assert limiter.is_allowed(ip)
        assert limiter.is_allowed(ip)
        assert not limiter.is_allowed(ip)  # 4th should be blocked
