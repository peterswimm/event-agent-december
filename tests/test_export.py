import json, subprocess, sys, pathlib, os

AGENT = pathlib.Path(__file__).resolve().parents[1] / "agent.py"
EXPORTS = pathlib.Path(__file__).resolve().parents[1] / "exports"


def run_json(cmd):
    result = subprocess.run(
        [sys.executable, str(AGENT)] + cmd, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_export_markdown_file_written():
    if EXPORTS.exists():
        for f in EXPORTS.glob("*.md"):
            f.unlink()
    out = run_json(
        ["export", "--interests", "agents, ai safety", "--output", "test_itinerary.md"]
    )
    path = pathlib.Path(out["saved"]) if out.get("saved") else None
    assert path and path.exists()
    content = path.read_text()
    assert "Event Itinerary" in content
    os.remove(path)
