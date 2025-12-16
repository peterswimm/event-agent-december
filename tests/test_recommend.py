import json, subprocess, sys, pathlib

AGENT = pathlib.Path(__file__).resolve().parents[1] / "agent.py"


def run(cmd):
    result = subprocess.run(
        [sys.executable, str(AGENT)] + cmd, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_recommend_basic():
    out = run(["recommend", "--interests", "agents, ai safety"])
    assert "sessions" in out and len(out["sessions"]) <= 3
    titles = [s["title"].lower() for s in out["sessions"]]
    assert any("generative agents" in t for t in titles)
