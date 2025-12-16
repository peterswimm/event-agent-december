#!/usr/bin/env python3
"""Generate a sessions_external.json template to stdout for eventkit.
Usage:
  python scripts/generate_sessions_template.py > sessions_external.json
"""

import json

TEMPLATE = [
    {
        "id": "ext1",
        "title": "Example Session Title",
        "start": "09:00",
        "end": "09:40",
        "location": "Room A",
        "tags": ["agents", "ai safety"],
        "popularity": 0.7,
    }
]

if __name__ == "__main__":  # pragma: no cover
    print(json.dumps(TEMPLATE, indent=2))
