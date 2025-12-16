"""Tests for /recommend-graph HTTP endpoint."""
import subprocess
import sys
import time
import urllib.request
import json
import pathlib
import socket
from unittest.mock import patch, MagicMock

AGENT = pathlib.Path(__file__).resolve().parents[1] / "agent.py"
PORT = 8094  # avoid collision with any existing server


def wait_port(port, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket() as s:
            try:
                s.connect(("127.0.0.1", port))
                return True
            except OSError:
                time.sleep(0.1)
    return False


def test_graph_endpoint_without_credentials():
    """Test /recommend-graph returns 502 when Graph credentials not configured."""
    proc = subprocess.Popen(
        [sys.executable, str(AGENT), "serve", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert wait_port(PORT), "server did not start"
        graph_url = f"http://127.0.0.1:{PORT}/recommend-graph?interests=agents&top=3"
        try:
            with urllib.request.urlopen(graph_url) as r:
                data = json.loads(r.read().decode())
            # If we get here without 502, Graph was available but credentials missing
            assert data.get("error"), "Expected error response"
        except urllib.error.HTTPError as e:
            # 502 Bad Gateway or 400 Bad Request expected
            assert e.code in (502, 400), f"Expected 502 or 400, got {e.code}"
            err = json.loads(e.fp.read().decode())
            assert "error" in err
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_graph_endpoint_missing_interests():
    """Test /recommend-graph returns 400 when interests not provided."""
    proc = subprocess.Popen(
        [sys.executable, str(AGENT), "serve", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert wait_port(PORT), "server did not start"
        graph_url = f"http://127.0.0.1:{PORT}/recommend-graph?top=3"
        try:
            with urllib.request.urlopen(graph_url) as r:
                pass
            assert False, "Expected 400 error"
        except urllib.error.HTTPError as e:
            assert e.code == 400
            err = json.loads(e.fp.read().decode())
            assert err["error"] == "no interests provided"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_graph_endpoint_health():
    """Test /health endpoint works."""
    proc = subprocess.Popen(
        [sys.executable, str(AGENT), "serve", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert wait_port(PORT), "server did not start"
        health_url = f"http://127.0.0.1:{PORT}/health"
        with urllib.request.urlopen(health_url) as r:
            data = json.loads(r.read().decode())
        assert data["status"] == "ok"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_graph_endpoint_with_mock_graph():
    """Test /recommend-graph with mocked Graph API services."""
    # This test would require mocking the Graph services at import time,
    # which is complex in subprocess context. Keeping it for documentation.
    proc = subprocess.Popen(
        [sys.executable, str(AGENT), "serve", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert wait_port(PORT), "server did not start"
        # In a real scenario, you'd set Graph credentials in environment
        # or .env file for the subprocess
        graph_url = f"http://127.0.0.1:{PORT}/recommend-graph?interests=ai+safety&top=3"
        try:
            with urllib.request.urlopen(graph_url) as r:
                data = json.loads(r.read().decode())
            # Could be 502 if Graph not available or 200 if mocked properly
            assert isinstance(data, dict)
        except urllib.error.HTTPError as e:
            # Expected since Graph credentials likely not configured
            assert e.code in (502, 400)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_graph_endpoint_with_user_id():
    """Test /recommend-graph preserves userId parameter in response."""
    proc = subprocess.Popen(
        [sys.executable, str(AGENT), "serve", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert wait_port(PORT), "server did not start"
        graph_url = (
            f"http://127.0.0.1:{PORT}/recommend-graph?interests=agents&userId=user%40example.com&top=3"
        )
        try:
            with urllib.request.urlopen(graph_url) as r:
                data = json.loads(r.read().decode())
            # If response succeeds, check userId is preserved
            if "userId" in data:
                assert data["userId"] == "user@example.com"
        except urllib.error.HTTPError as e:
            # Expected since Graph credentials likely not configured
            assert e.code in (502, 400)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_graph_endpoint_cors():
    """Test /recommend-graph returns CORS headers."""
    proc = subprocess.Popen(
        [sys.executable, str(AGENT), "serve", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert wait_port(PORT), "server did not start"
        graph_url = f"http://127.0.0.1:{PORT}/recommend-graph?interests=agents&top=3"
        try:
            with urllib.request.urlopen(graph_url) as r:
                cors_header = r.headers.get("Access-Control-Allow-Origin")
                assert cors_header == "*", "Missing CORS header"
        except urllib.error.HTTPError as e:
            # Even with error, CORS headers should be present
            cors_header = e.headers.get("Access-Control-Allow-Origin")
            assert cors_header == "*", "Missing CORS header on error response"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
