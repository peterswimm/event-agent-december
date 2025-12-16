#!/usr/bin/env python3
"""Export itinerary via eventkit agent CLI wrapper.
Usage:
  python scripts/export_itinerary.py "agents, ai safety" [output.md]
"""

import subprocess, sys


def main():  # pragma: no cover
    if len(sys.argv) < 2:
        print("Usage: export_itinerary.py 'interest1, interest2' [filename]")
        sys.exit(1)
    interests = sys.argv[1]
    fname = sys.argv[2] if len(sys.argv) > 2 else None
    cmd = [sys.executable, "agent.py", "export", "--interests", interests]
    if fname:
        cmd += ["--output", fname]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
