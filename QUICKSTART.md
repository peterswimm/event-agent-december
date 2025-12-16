# Event Kit Quick Start

Minimal declarative agent: one manifest (`agent.json`) + one script (`agent.py`).

## Quick Start: Manifest Mode (Default)

```bash
python agent.py recommend --interests "ai safety, agents" --top 3
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"
```

## Quick Start: Microsoft Graph Mode (New)

**Setup** (one-time, 5 minutes):
```bash
# Set Graph credentials
export GRAPH_TENANT_ID=your-tenant-id
export GRAPH_CLIENT_ID=your-client-id
export GRAPH_CLIENT_SECRET=your-client-secret

# Verify
python -c "from settings import Settings; print('Ready:', Settings().validate_graph_ready())"
```

**Use**:
```bash
python agent.py recommend --source graph --interests "ai safety" --top 3 --user-id user@company.com
python agent.py recommend --source graph --interests "agents" --top 5
```

Full setup guide: [docs/graph-setup.md](docs/graph-setup.md)

## HTTP Server Mode

```bash
# Start server (supports both manifest and Graph modes)
python agent.py serve --port 8080 --card

# Manifest recommendations (existing)
curl "http://localhost:8080/recommend?interests=agents,ai+safety&top=3"

# Graph recommendations (new - requires credentials)
curl "http://localhost:8080/recommend-graph?interests=ai+safety&top=3&userId=user@company.com"

# Explain session
curl "http://localhost:8080/explain?session=Generative+Agents+in+Production&interests=agents,gen+ai"

# Export itinerary
curl "http://localhost:8080/export?interests=agents,ai+safety"

# Health check
curl "http://localhost:8080/health"
```

Endpoints: `/health`, `/recommend`, `/recommend-graph`, `/explain`, `/export`.
- Add `card=1` for Adaptive Card format
- Use `--card` flag when starting server for default Adaptive Cards

## Profiles

```bash
python agent.py recommend --interests "agents" --profile-save user1
python agent.py recommend --interests "edge" --profile-load user1
```

Stored at `~/.event_agent_profiles.json`.

## Manifest Editing

Adjust weights or sessions in `agent.json`, then rerun (no code change).

## Feature Flags

See `features` block for telemetry, export, externalSessions.

## systemd Service (Optional)

```ini
[Unit]
Description=Event Kit Agent
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/eventkit
ExecStart=/usr/bin/python3 agent.py serve --port 8080 --card
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl enable --now eventkit.service
```

## Tests

```bash
python -m pytest eventkit/tests -q
```

## Extensibility Notes

- External data override: drop `sessions_external.json` and enable feature.
- Telemetry: JSONL lines for recommend/explain/export.
- Card actions: adapt `Action.Submit` payloads to call `/explain`.
- Export itinerary: use `export` CLI or `/export` endpoint.
