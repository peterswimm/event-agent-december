# Event Kit

**Minimal declarative event recommendation agent** for Vibe Kit. Demonstrates core agent patterns with one manifest (`agent.json`) and one script (`agent.py`).

---

## Overview

Event Kit is a lightweight innovation kit showcasing:

- **Declarative manifest**: Sessions, weights, and feature flags in JSON
- **CLI + HTTP server**: Recommend, explain, export endpoints
- **Adaptive Cards**: Interactive UI for Copilot experiences
- **Telemetry**: Structured JSONL logging for observability
- **Profile persistence**: Save/load user preferences
- **External data override**: Swap in real event feeds
- **Microsoft Graph integration**: Live calendar events with MSAL auth (NEW)

---

## How This Fits in Vibe Kit

Vibe Kit is a repository of innovation kits designed to accelerate AI agent prototyping. Event Kit serves as:

1. **Foundational example**: Minimal agent architecture (manifest + logic)
2. **Starter for real integrations**: Easily extend to Microsoft Graph, SharePoint, or Agent SDK hosting
3. **Pattern library**: Demonstrates scoring, conflict detection, adaptive cards, telemetry

For production-ready Graph/SharePoint integration, see [`innovation-kit-repository/event-agent/`](../innovation-kit-repository/event-agent/) which includes:

- Microsoft 365 Agents SDK hosting scaffold
- Graph Calendar fetching with MSAL auth
- SharePoint page publishing
- Pydantic configuration with feature flags
- Full setup guide in `MVP_GUIDE.md`

---

## Quick Start

### 1. Run Locally (No Setup)

```bash
cd eventkit

# Recommend sessions
python agent.py recommend --interests "agents, ai safety" --top 3

# Explain a session
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"

# Export itinerary
python agent.py export --interests "agents, privacy" --output my_itinerary.md

# Start HTTP server
python agent.py serve --port 8010 --card
```

Test endpoints:

```bash
curl http://localhost:8010/health
curl "http://localhost:8010/recommend?interests=agents,ai+safety&top=3&card=1"
curl "http://localhost:8010/explain?session=Generative+Agents+in+Production&interests=agents,gen+ai"
```

### 2. Profile Persistence

```bash
# Save interests for later
python agent.py recommend --interests "agents, telemetry" --profile-save demo

# Load saved profile
python agent.py recommend --profile-load demo --top 5
```

Profiles stored in `~/.event_agent_profiles.json`.

### 3. Run Tests

```bash
python -m pytest eventkit/tests -q
```

All 7 tests should pass (recommend, explain, export, profile, server, telemetry, external sessions).

---

## Setup Dev Environment in VS Code

### Prerequisites

- Python 3.11+
- VS Code with Python extension

### Steps

1. **Clone the Vibe Kit repo** (if not already):

   ```bash
   git clone https://github.com/peterswimm/vibe-kit.git
   cd vibe-kit
   ```

2. **Open eventkit in VS Code**:

   ```bash
   code eventkit
   ```

   Or open the workspace folder in VS Code and navigate to `eventkit/`.

3. **Create a virtual environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dev dependencies** (optional, for testing):

   ```bash
   pip install pytest
   ```

   The agent itself has **zero dependencies** — runs with Python stdlib only.

5. **Configure VS Code**:

   - Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
   - Select `Python: Select Interpreter`
   - Choose `.venv/bin/python`

6. **Run the agent**:

   Open integrated terminal in VS Code (`Ctrl+` `/`Cmd+` `) and:

   ```bash
   python agent.py recommend --interests "agents, ai safety" --top 3
   ```

7. **Run tests** (in VS Code terminal):

   ```bash
   python -m pytest tests -v
   ```

   Or use VS Code's Testing sidebar (flask icon) to discover and run tests interactively.

8. **Debug**:

   Set breakpoints in `agent.py`, then press `F5` (Run > Start Debugging). VS Code will prompt to create a `launch.json` — select "Python File" for CLI debugging or "Python: Current File" for general use.

---

## Extending with Agent SDK

To integrate with Microsoft 365 Agents SDK (Teams/Copilot Studio hosting):

1. **See the full Agent SDK starter** in [`innovation-kit-repository/event-agent/starter-code/agents_sdk_integration/`](../innovation-kit-repository/event-agent/starter-code/agents_sdk_integration/)
2. **Follow MVP_GUIDE.md** for Graph authentication, SharePoint publish, and SDK hosting setup
3. **Compare patterns**: Event Kit (`eventkit/agent.py`) shows minimal logic; Agent SDK starter adds authentication, caching, and enterprise features

### Key Differences

| Feature          | Event Kit (`eventkit/`)      | Agent SDK Starter (`innovation-kit-repository/event-agent/`) |
| ---------------- | ---------------------------- | ------------------------------------------------------------ |
| **Auth**         | None (mock data)             | MSAL (Graph + SharePoint)                                    |
| **Data Source**  | Static JSON or external file | Microsoft Graph Calendar                                     |
| **Publishing**   | Markdown export              | SharePoint page creation                                     |
| **Hosting**      | CLI + HTTP server            | Microsoft 365 Agents SDK (Teams/Copilot Studio)              |
| **Config**       | JSON manifest                | Pydantic settings + `.env`                                   |
| **Dependencies** | None                         | `pydantic`, `msal`, `requests`, `botbuilder-core`            |

**When to use Event Kit**: Prototyping agent logic, testing scoring algorithms, local demos

**When to use Agent SDK Starter**: Production deployment, Graph integration, Teams/Copilot experiences

---

## Project Structure

```
eventkit/
├── agent.py                 # Core logic (recommend, explain, export, serve)
├── agent.json               # Manifest (sessions, weights, features)
├── telemetry.py             # JSONL logging module
├── pyproject.toml           # Packaging (console script: "eventkit")
├── EVENT_KIT.md             # Quick start overview
├── QUICKSTART.md            # Detailed CLI/server usage
├── runner.py                # Unified runner for mutually exclusive modes
├── core.py                  # Importable core functions (recommend, explain, recommend_from_graph)
├── settings.py              # Pydantic settings (includes Graph credentials)
├── agent.schema.json        # JSON Schema for manifest validation
│
├── # Microsoft Graph Integration (NEW)
├── graph_auth.py            # MSAL authentication and token caching
├── graph_service.py         # Graph API wrapper, event transformation, caching
├── logging_config.py        # Structured logging with GraphEventLogger
│
├── docs/
│   ├── graph-setup.md       # Complete Graph setup and configuration guide
│   ├── technical-guide.md   # Architecture and design patterns
│   └── ...
│
├── tests/
│   ├── test_recommend.py
│   ├── test_explain.py
│   ├── test_export.py
│   ├── test_profile.py
│   ├── test_server.py
│   ├── test_telemetry.py
│   ├── test_graph_auth.py           # Graph auth module tests
│   ├── test_graph_service.py        # Graph API service tests
│   ├── test_core_graph.py           # Graph recommendations tests
│   ├── test_graph_server.py         # /recommend-graph endpoint tests
│   ├── test_graph_integration.py    # End-to-end integration tests
│   └── test_logging_config.py       # Logging configuration tests
├── .env                     # Configuration file (not committed)
```
│   └── test_external_sessions.py
├── docs/                    # Technical guides
│   ├── technical-guide.md
│   ├── performance-guide.md
│   ├── troubleshooting.md
│   ├── application-patterns.md
│   ├── data-integration.md
│   ├── evaluation.md
│   ├── governance.md
│   └── openapi-snippet.yaml
├── scripts/                 # Utilities
│   ├── evaluate_profiles.py
│   ├── export_itinerary.py
│   ├── generate_sessions_template.py
│   └── summarize_telemetry.py
└── assets/                  # Sample data
    ├── sample_itinerary.md
    └── sessions_external.json
```

---

## Run Modes (Mutually Exclusive)

Use the unified runner to select the mode:

- `custom-chat`: Minimal HTTP server with optional MCP tools

  ```bash
  eventkit-runner --mode custom-chat --port 8010 --card
  ```

- `m365-agent`: Microsoft 365 Agents SDK host (Teams/Copilot Studio)

  ```bash
  # Required env: GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET
  eventkit-runner --mode m365-agent --port 3978
  ```

- `sharepoint-agent`: Publish itineraries to SharePoint (no chat hosting)

- `directline-adapter`: Bot Framework Direct Line/Web Chat adapter

  ```bash
  # Requires: MICROSOFT_APP_ID, MICROSOFT_APP_PASSWORD; optional AGENT_API_BASE
  eventkit-runner --mode directline-adapter --port 3979
  ```

  ```bash
  # Optional interests; add --publish to push pages
  eventkit-runner --mode sharepoint-agent --interests "AI;agents" --max-sessions 3 --publish
  ```

Mode boundaries:

- MCP/tools only in `custom-chat`
- Graph/SharePoint integrations only in `m365-agent` / `sharepoint-agent`

Deployment playbooks:

- `m365-agent`: Azure App Service/Container Apps, Bot Framework channel
- `sharepoint-agent`: Azure Function/Container job
- `custom-chat`: Containerized web service + optional MCP servers

### Config via Environment

You can set `RUN_MODE` and related variables in `.env` and run the runner without `--mode`:

```bash
cd eventkit
cp .env.example .env
# Edit .env, then export for the shell
export $(grep -v '^#' .env | xargs)

# RUN_MODE controls the behavior; falls back to CLI --mode if provided
eventkit-runner  # uses RUN_MODE
```

`.env.example` keys:

- `RUN_MODE`: `custom-chat` | `m365-agent` | `sharepoint-agent`
- `PORT`: Port for server modes (`custom-chat`, `m365-agent`)
- `INCLUDE_CARD`: `true|false` Adaptive Card in responses (custom-chat)
- `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`: Required for `m365-agent`; required for `sharepoint-agent` when publishing
- `INTERESTS`, `MAX_SESSIONS`, `PUBLISH`: Defaults for `sharepoint-agent`

### Observability

- `custom-chat`: JSONL telemetry via `telemetry.jsonl`, health check at `/health`
- `m365-agent`: Integrate Azure Application Insights in the SDK host; expose liveness/readiness on the hosting platform
- `sharepoint-agent`: Log publish actions to JSONL and consider Azure Function logs or Container logs; add a simple CLI exit code for automation

### MCP/Tooling Separation

- MCP servers and tooling are intended for `custom-chat` mode only.
- Avoid enabling MCP in `m365-agent` and `sharepoint-agent` paths unless a specific enterprise need is identified.
- Keep boundaries clear: SDK-hosted experiences should rely on Graph/SharePoint integrations and platform observability.

### Deployment Playbooks

- `m365-agent` (Teams/Copilot Studio host):

  - Package the SDK host as a container and deploy to Azure App Service or Azure Container Apps.
  - Configure Bot Framework channel and required Graph credentials via app settings.
  - Add Application Insights for tracing and dashboards.

- `sharepoint-agent` (publisher service):

  - Implement as an Azure Function (timer/HTTP) or a scheduled container job.
  - Provide Graph credentials via Key Vault/App Settings; log publish results to JSONL and platform logs.
  - Keep no-chat boundary: this service publishes itineraries only.

- `custom-chat` (local/minimal web):
  - Containerize the HTTP server for portability; optionally run MCP servers alongside.
  - Expose `/health` and write local JSONL telemetry; consider lightweight reverse proxy for production demos.

### Minimize Open Ports

To reduce security review scope, prefer a single externally exposed port:

- Use NGINX reverse proxy to expose only `8010` and proxy to internal services.
- Bind internal services to `127.0.0.1` and non-exposed ports (`8011` for agent, `5174` for frontend when needed).

Quick container example (exposes only 8010):

```bash
cd eventkit/deploy
docker build -t eventkit-proxy .
docker run --rm -p 8010:8010 eventkit-proxy
```

Or use Docker Compose:

```bash
cd eventkit/deploy
docker compose up -d
```

This runs `agent.py serve` on `8011` internally and fronts it with NGINX at `8010`. The optional frontend can be proxied under `/app` without opening `5174` publicly.

Devcontainer now forwards only `8010`, consolidating all services behind the NGINX proxy.

### Direct Line / Web Chat (Adaptive Cards)

Use the Bot Framework adapter shim in `eventkit/adapters/directline_bot.py`:

```bash
cd eventkit
python -m pip install -r adapters/requirements-directline.txt
MICROSOFT_APP_ID="<bot app id>" \
MICROSOFT_APP_PASSWORD="<bot app password>" \
AGENT_API_BASE="http://localhost:8010" \
python -m eventkit.adapters.directline_bot --port 3979
```

- Exposes `/api/messages` for Direct Line / Bot Framework Web Chat.
- Forwards user text to the Event Kit `/recommend` endpoint and returns an Adaptive Card attachment.
- Deploy this container to Azure App Service/Container Apps, enable the Direct Line channel, and point Web Chat to the Direct Line token.

## Feature Flags

Adjust behavior in `agent.json > features`:

- **`telemetry.enabled`**: Log actions to `telemetry.jsonl`
- **`export.enabled`**: Save markdown to `exports/` directory
- **`externalSessions.enabled`**: Override sessions with `sessions_external.json`

---

## Next Steps

1. **Customize sessions**: Edit `agent.json` to add your event data
2. **Adjust scoring weights**: Tweak `weights` (interest, popularity, diversity)
3. **Connect real data**: Enable `externalSessions` and provide JSON feed
4. **Add authentication**: See Agent SDK starter for Graph/MSAL patterns
5. **Deploy as service**: Use systemd or containerize (see `QUICKSTART.md`)
6. **Integrate with Teams**: Follow `innovation-kit-repository/event-agent/MVP_GUIDE.md`

---

## Resources

- **Vibe Kit Repository**: <https://github.com/peterswimm/vibe-kit>
- **Agent SDK Starter**: `innovation-kit-repository/event-agent/starter-code/agents_sdk_integration/`
- **Full Setup Guide**: `innovation-kit-repository/event-agent/MVP_GUIDE.md`
- **Roadmap**: `innovation-kit-repository/event-agent/ROADMAP.md`
- **Technical Docs**: `eventkit/docs/technical-guide.md`

---

## License

MIT — See [LICENSE](../LICENSE) in repository root.
