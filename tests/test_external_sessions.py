import subprocess, sys, json, pathlib

AGENT = pathlib.Path(__file__).resolve().parents[1] / "agent.py"
SESS_FILE = pathlib.Path(__file__).resolve().parents[1] / "sessions_external.json"


def run_json(cmd):
    result = subprocess.run(
        [sys.executable, str(AGENT)] + cmd, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_external_sessions_override():
    sessions = [
        {
            "id": "x1",
            "title": "Custom External Session",
            "start": "09:00",
            "end": "09:30",
            "location": "Room X",
            "tags": ["agents"],
            "popularity": 0.5,
        },
        {
            "id": "x2",
            "title": "Another External Session",
            "start": "09:40",
            "end": "10:10",
            "location": "Room Y",
            "tags": ["ai safety"],
            "popularity": 0.7,
        },
    ]
    SESS_FILE.write_text(json.dumps(sessions, indent=2))
    out = run_json(["recommend", "--interests", "agents, ai safety", "--top", "2"])
    titles = {s["title"].lower() for s in out["sessions"]}
    assert "custom external session" in titles
    assert titles == {"custom external session", "another external session"}
    SESS_FILE.unlink()
