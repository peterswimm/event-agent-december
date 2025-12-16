# Technical Guide

## Scoring Model

Each session is scored as the sum of weighted contributions:

```text
total = (interest_hits * w_interest) + (popularity * w_popularity) + (diversity_factor * w_diversity)
```

- interest_hits: count of session tags that match normalized user interests
- popularity: numeric popularity (0–1) from manifest
- diversity_factor: `len(unique_interests) * 0.01`

Weights live in `agent.json > weights`:

```json
{ "interest": 2.0, "popularity": 0.5, "diversity": 0.3 }
```

## Telemetry Schema

Telemetry lines are JSON objects written to `telemetry.jsonl` (one per action):

```json
{
  "ts": 1732540000.123,
  "action": "recommend",
  "success": true,
  "error": null,
  "latency_ms": 12.5,
  "payload": { "sessions": [] }
}
```

Fields:

- ts: epoch timestamp (float)
- action: `recommend` | `explain` | `export` | `health`
- success: boolean outcome
- error: error string or null
- latency_ms: measured duration
- payload: minimal result subset (sessions array or scoring detail)

## Profiles Storage

User interest profiles persist to `~/.event_agent_profiles.json` keyed by profile id. Example:

```json
{
  "demo": ["agents", "ai safety"],
  "observability": ["telemetry", "agents"]
}
```

## External Sessions Override

When `features.externalSessions.enabled` is true and `sessions_external.json` exists, recommendation & explanation functions load sessions from that file instead of the manifest. File is a list of session objects with the same shape as `agent.json > sessions`.

## Error Handling

- Empty interests → returns error `{ "error": "no interests provided" }`
- Missing session in explain → `{ "error": "session not found" }`
- Invalid external sessions file → silently ignored (falls back to manifest sessions)

## Adaptive Card Generation

If `--card` flag (CLI serve) or `card=1` query param is set, an Adaptive Card (`version: 1.5`) with numbered session entries and explain buttons is attached to the recommendation response.

## Conflict Counting

Conflicts metric counts time slot overlaps. Each unique `(start, end)` pair with more than one session increments conflict count.

## Extensibility Points

- Add new contribution: extend `score_session` with new metric (e.g., recency) and manifest weight.
- Swap telemetry backend: replace `get_telemetry` implementation to push to external sink.
- Additional output formats: extend export feature to produce JSON itinerary or ICS calendar.
