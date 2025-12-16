#!/usr/bin/env python3
"""Summarize telemetry.jsonl file for eventkit.
Outputs JSON summary with counts, success rate, and latency stats.
Usage:
  python scripts/summarize_telemetry.py [telemetry.jsonl]
"""

import sys, json, statistics, pathlib


def load_lines(path: pathlib.Path):
    if not path.exists():
        return []
    lines = []
    for raw in path.read_text().splitlines():
        try:
            lines.append(json.loads(raw))
        except Exception:
            continue
    return lines


def summarize(entries):
    if not entries:
        return {"count": 0}
    latencies = [
        e.get("latency_ms", 0)
        for e in entries
        if isinstance(e.get("latency_ms"), (int, float))
    ]
    actions = {}
    success = 0
    for e in entries:
        actions.setdefault(e.get("action"), 0)
        actions[e.get("action")] += 1
        if e.get("success"):
            success += 1
    return {
        "count": len(entries),
        "actions": actions,
        "success_rate": success / len(entries),
        "latency": {
            "median": statistics.median(latencies) if latencies else None,
            "p95": statistics.quantiles(latencies, n=100)[94]
            if len(latencies) >= 100
            else None,
            "max": max(latencies) if latencies else None,
        },
    }


def main():  # pragma: no cover
    file = sys.argv[1] if len(sys.argv) > 1 else "telemetry.jsonl"
    path = pathlib.Path(file)
    entries = load_lines(path)
    print(json.dumps(summarize(entries), indent=2))


if __name__ == "__main__":
    main()
