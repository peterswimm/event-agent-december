# Data Integration Guide

## External Sessions File Format

`sessions_external.json` is a JSON array of session objects matching manifest schema:

```json
[
  {
    "id": "x1",
    "title": "Custom External Session",
    "start": "09:00",
    "end": "09:30",
    "location": "Room X",
    "tags": ["agents"],
    "popularity": 0.5
  }
]
```

## Merge Strategy

Current implementation REPLACES manifest sessions entirely when the file is present & feature enabled. For a merge approach:

1. Load manifest sessions.
2. Deduplicate by `id` or `title`.
3. Append external sessions.

## Refresh Workflow

```bash
python scripts/generate_sessions_template.py > sessions_external.json
# Edit file, add real sessions
python agent.py recommend --interests "agents, ai safety"
```

## Validation Tips

- Ensure required fields: `id`, `title`, `start`, `end`, `location`, `tags`, `popularity`.
- Keep popularity in 0–1 range.
- Normalize tag casing (lowercase) for consistent matching.

## Upstream Sources

- CSV exports from conference scheduling tools
- Internal planning spreadsheets
- API endpoints returning session metadata

Transform upstream shape to the expected dict keys before writing JSON.
