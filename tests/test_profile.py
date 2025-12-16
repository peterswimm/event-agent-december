import json, subprocess, sys, pathlib

AGENT = pathlib.Path(__file__).resolve().parents[1] / "agent.py"
PROFILE_KEY = "profile_test_user"


def run(cmd):
    result = subprocess.run(
        [sys.executable, str(AGENT)] + cmd, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_profile_round_trip():
    save_out = run(
        [
            "recommend",
            "--interests",
            "ai safety",
            "--profile-save",
            PROFILE_KEY,
        ]
    )
    assert save_out.get("profileSaved") == PROFILE_KEY
    load_out = run(
        [
            "recommend",
            "--interests",
            "edge",
            "--profile-load",
            PROFILE_KEY,
        ]
    )
    scoring_titles = [s["title"].lower() for s in load_out["sessions"]]
    assert any("ai safety foundations" in t for t in scoring_titles)
