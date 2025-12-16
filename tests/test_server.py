import subprocess, sys, time, urllib.request, json, pathlib, socket

AGENT = pathlib.Path(__file__).resolve().parents[1] / "agent.py"
PORT = 8093  # avoid collision with any existing server


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


def test_server_recommend_and_explain():
    proc = subprocess.Popen(
        [sys.executable, str(AGENT), "serve", "--port", str(PORT), "--card"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert wait_port(PORT), "server did not start"
        rec_url = (
            f"http://127.0.0.1:{PORT}/recommend?interests=agents,ai+safety&top=3&card=1"
        )
        with urllib.request.urlopen(rec_url) as r:
            data = json.loads(r.read().decode())
        assert "sessions" in data and "adaptiveCard" in data
        assert data["adaptiveCard"]["actions"][0]["title"].startswith("Explain")
        explain_url = f"http://127.0.0.1:{PORT}/explain?session=Generative+Agents+in+Production&interests=agents,gen+ai"
        with urllib.request.urlopen(explain_url) as r:
            exp = json.loads(r.read().decode())
        assert exp["title"] == "Generative Agents in Production"
        assert exp["score"] > 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
