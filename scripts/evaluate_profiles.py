#!/usr/bin/env python3
"""Evaluate multiple interest profiles against current sessions (eventkit).
Usage:
  python scripts/evaluate_profiles.py --profiles privacy="privacy, ai safety" obs="telemetry, agents" --top 3
  python scripts/evaluate_profiles.py --load demo observability --top 3
"""

import argparse, json, time, statistics, pathlib, sys
from typing import List, Dict, Any

SCRIPT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import agent  # type: ignore


def normalize(raw: str) -> List[str]:
    return [t.strip().lower() for t in raw.replace(";", ",").split(",") if t.strip()]


def relevance(sessions: List[Dict[str, Any]], interests: List[str]) -> float:
    if not sessions:
        return 0.0
    hits = sum(
        1 for s in sessions if any(t.lower() in interests for t in s.get("tags", []))
    )
    return hits / len(sessions)


def diversity(sessions: List[Dict[str, Any]], interests: List[str]) -> int:
    covered = set()
    for s in sessions:
        for t in s.get("tags", []):
            if t.lower() in interests:
                covered.add(t.lower())
    return len(covered)


def conflicts(rec: Dict[str, Any]) -> int:
    return rec.get("conflicts", 0)


def run_eval(
    manifest: Dict[str, Any], interests: List[str], top: int
) -> Dict[str, Any]:
    start = time.time()
    rec = agent.recommend(manifest, interests, top)
    latency = (time.time() - start) * 1000
    sessions = rec["sessions"]
    return {
        "interests": interests,
        "relevance": relevance(sessions, interests),
        "diversity": diversity(sessions, interests),
        "conflicts": conflicts(rec),
        "latency_ms": latency,
        "count": len(sessions),
    }


def main():  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profiles", nargs="*", help="Inline profiles key=interests,..."
    )
    parser.add_argument("--load", nargs="*", help="Profile ids to load from storage")
    parser.add_argument("--top", type=int, default=None)
    args = parser.parse_args()

    manifest = agent.load_manifest()
    top_n = args.top or manifest["recommend"]["max_sessions_default"]
    storage_file = manifest.get("profile", {}).get("storage_file")

    profile_specs: Dict[str, List[str]] = {}
    if args.profiles:
        for spec in args.profiles:
            if "=" in spec:
                name, raw = spec.split("=", 1)
                profile_specs[name] = normalize(raw)
    if args.load and storage_file:
        for pid in args.load:
            interests = agent.load_profile(storage_file, pid)
            if interests:
                profile_specs[pid] = interests

    results = [
        run_eval(manifest, ints, top_n) | {"profile": name}
        for name, ints in profile_specs.items()
    ]
    latencies = [r["latency_ms"] for r in results]
    summary = {
        "profiles": results,
        "aggregate": {
            "count": len(results),
            "median_latency_ms": statistics.median(latencies) if latencies else None,
            "max_latency_ms": max(latencies) if latencies else None,
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
