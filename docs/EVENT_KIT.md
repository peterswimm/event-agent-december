# Event Kit (Renamed)

This directory supersedes `simplified-event-agent/`. All references should now use `eventkit/`.

## Quick Start

```bash
cd eventkit
python agent.py recommend --interests "agents, ai safety" --top 3
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"
python agent.py export --interests "agents, ai safety" --profile-save demo
python agent.py serve --port 8010 --card
```

Health:

```bash
curl http://localhost:8010/health
```

## Feature Flags

See `agent.json > features` for telemetry, export, externalSessions.

## Docs

Guides retained under `eventkit/docs/`.

## Migration Notes

- Old path references (`simplified-event-agent/`) should be updated in downstream scripts.
- Console entrypoint renamed to `eventkit` (install via `pip install .` then run `eventkit recommend ...`).
