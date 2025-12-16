import json, subprocess, sys, pathlib

AGENT = pathlib.Path(__file__).resolve().parents[1] / "agent.py"


def run(cmd):
    result = subprocess.run(
        [sys.executable, str(AGENT)] + cmd, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_explain_session():
    out = run(
        [
            "explain",
            "--session",
            "Generative Agents in Production",
            "--interests",
            "agents, gen ai",
        ]
    )
    assert out["title"] == "Generative Agents in Production"
    assert out["score"] > 0
    assert "interest_match" in out["contributions"]
