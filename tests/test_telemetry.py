import json, subprocess, sys, pathlib, time

AGENT = pathlib.Path(__file__).resolve().parents[1] / "agent.py"
MANIFEST = pathlib.Path(__file__).resolve().parents[1] / "agent.json"


def telemetry_file():
    data = json.loads(MANIFEST.read_text())
    feat = data.get("features", {}).get("telemetry", {})
    return pathlib.Path(feat.get("file", "telemetry.jsonl"))


def run(cmd):
    result = subprocess.run(
        [sys.executable, str(AGENT)] + cmd, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_telemetry_line_written():
    tf = telemetry_file()
    if tf.exists():
        tf.unlink()
    out = run(["recommend", "--interests", "agents, ai safety", "--top", "2"])
    assert "sessions" in out
    for _ in range(10):
        if tf.exists() and tf.stat().st_size > 0:
            break
        time.sleep(0.05)
    assert tf.exists(), "telemetry file not created"
    lines = tf.read_text().strip().splitlines()
    assert lines, "no telemetry lines"
    rec = json.loads(lines[-1])
    assert rec.get("action") == "recommend"
    assert rec.get("success") is True
