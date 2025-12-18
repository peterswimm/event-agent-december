# Application Patterns

## Profiles-First Recommendation

Store multiple profiles (e.g., `privacy`, `observability`) and run batch recommendations to produce comparative itineraries.

Pattern:

```bash
python agent.py recommend --interests "privacy, ai safety" --profile-save privacy
python agent.py recommend --interests "telemetry, agents" --profile-save observability
```

## External Data Refresh

Pull latest session data from an upstream source (CSV/API), transform to list of dicts, write `sessions_external.json`, rerun recommend without modifying code.

## Governance-Aware Export

Run export feature and attach telemetry summary for auditing:

```bash
python agent.py export --interests "agents, governance"
python scripts/summarize_telemetry.py > exports/telemetry_summary.json
```

## Adaptive Card Delivery

Serve recommendations with `--card` so downstream clients (Teams/Outlook) can render actionable explain buttons.

## Daily Rotation

Rotate telemetry file and external sessions each day to maintain clean state and time-bounded analytics.
