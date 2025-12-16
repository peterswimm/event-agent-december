# Event Kit Quick Start

Minimal declarative agent: one manifest (`agent.json`) + one script (`agent.py`).

## CLI Usage

```bash
python agent.py recommend --interests "ai safety, agents" --top 3
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"
```

## HTTP Server Mode

```bash
python agent.py serve --port 8080 --card
curl "http://localhost:8080/recommend?interests=agents,ai+safety&top=3"
curl "http://localhost:8080/explain?session=Generative+Agents+in+Production&interests=agents,gen+ai"
curl "http://localhost:8080/recommend?interests=agents,ai+safety&top=3&card=1" | jq '.adaptiveCard.actions[0]'
```

Endpoints: `/health`, `/recommend`, `/explain`, `/export`. Add `card=1` or start with `--card` for Adaptive Card.

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
