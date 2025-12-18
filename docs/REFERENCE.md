# Command & API Reference

Quick reference for Event Kit CLI commands, HTTP endpoints, and configuration options.

## CLI Commands

### recommend

Get session recommendations based on interests.

**Syntax:**

```bash
python agent.py recommend [OPTIONS]
```

**Options:**

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--interests` | `-i` | Yes* | — | Comma-separated interests |
| `--top` | `-t` | No | 3 | Number of recommendations |
| `--source` | `-s` | No | manifest | Data source: `manifest` or `graph` |
| `--user-id` | `-u` | No | — | User email (for Graph mode) |
| `--profile-save` | — | No | — | Save interests to profile name |
| `--profile-load` | — | No | — | Load interests from profile |

*Required unless `--profile-load` is used

**Examples:**

```bash
# Basic recommendation
python agent.py recommend --interests "ai, agents" --top 3

# Using Graph API
python agent.py recommend --source graph --interests "ai" --user-id user@company.com

# Save profile
python agent.py recommend --interests "ai, safety" --profile-save myprofile

# Load profile
python agent.py recommend --profile-load myprofile --top 5
```

### explain

Explain why a session was recommended.

**Syntax:**

```bash
python agent.py explain [OPTIONS]
```

**Options:**

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--session` | `-s` | Yes | — | Session title to explain |
| `--interests` | `-i` | Yes* | — | Comma-separated interests |
| `--source` | — | No | manifest | Data source: `manifest` or `graph` |
| `--user-id` | `-u` | No | — | User email (for Graph mode) |
| `--profile-load` | — | No | — | Load interests from profile |

*Required unless `--profile-load` is used

**Examples:**

```bash
# Explain a session
python agent.py explain --session "AI Safety Workshop" --interests "ai, safety"

# Using Graph
python agent.py explain --source graph --session "Meeting Title" --interests "ai"
```

### export

Export recommended sessions as Markdown itinerary.

**Syntax:**

```bash
python agent.py export [OPTIONS]
```

**Options:**

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--interests` | `-i` | Yes* | — | Comma-separated interests |
| `--output` | `-o` | No | console | Output filename |
| `--top` | `-t` | No | 3 | Number of sessions |
| `--source` | `-s` | No | manifest | Data source |
| `--user-id` | `-u` | No | — | User email (for Graph) |
| `--profile-load` | — | No | — | Load from profile |

**Examples:**

```bash
# Export to file
python agent.py export --interests "ai, agents" --output itinerary.md

# Export to console
python agent.py export --interests "ai"

# Using Graph
python agent.py export --source graph --interests "ai" --output calendar.md
```

### serve

Start HTTP server for REST API access.

**Syntax:**

```bash
python agent.py serve [OPTIONS]
```

**Options:**

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--port` | `-p` | No | 8080 | Port to listen on |
| `--card` | `-c` | No | false | Enable Adaptive Cards |

**Examples:**

```bash
# Start on default port
python agent.py serve

# Custom port with cards
python agent.py serve --port 8000 --card
```

## HTTP API Endpoints

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "ok"
}
```

**Example:**

```bash
curl http://localhost:8080/health
```

### GET /recommend

Get manifest-based recommendations.

**Query Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `interests` | Yes* | — | Comma-separated interests |
| `top` | No | 3 | Number of results |
| `profileLoad` | No | — | Profile name to load |
| `card` | No | 0 | Include Adaptive Card (1=yes) |

**Response:**

```json
{
  "sessions": [
    {
      "title": "Session Title",
      "score": 4.23,
      "topics": ["ai", "agents"]
    }
  ],
  "conflicts": 0,
  "scoring": { "weights": {...} }
}
```

**Example:**

```bash
curl "http://localhost:8080/recommend?interests=ai,agents&top=3&card=1"
```

### GET /recommend-graph

Get Graph API-based recommendations.

**Query Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `interests` | Yes | — | Comma-separated interests |
| `top` | No | 3 | Number of results |
| `userId` | No | — | User email for tracking |
| `card` | No | 0 | Include Adaptive Card (1=yes) |

**Response:**

```json
{
  "source": "graph",
  "sessions": [
    {
      "title": "Calendar Event",
      "start": "09:00",
      "end": "10:00",
      "score": 4.23
    }
  ],
  "userId": "user@company.com"
}
```

**Example:**

```bash
curl "http://localhost:8080/recommend-graph?interests=ai&top=3&userId=user@company.com"
```

### GET /explain

Explain a session recommendation.

**Query Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `session` | Yes | — | Session title |
| `interests` | Yes* | — | Comma-separated interests |
| `profileLoad` | No | — | Profile name |

**Response:**

```json
{
  "session": "AI Workshop",
  "interests": ["ai"],
  "score": 4.23,
  "explanation": "Matched topics: ai, safety"
}
```

**Example:**

```bash
curl "http://localhost:8080/explain?session=AI+Workshop&interests=ai"
```

### GET /export

Export itinerary as Markdown.

**Query Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `interests` | Yes* | — | Comma-separated interests |
| `profileLoad` | No | — | Profile name |

**Response:**

```json
{
  "markdown": "# Itinerary\n...",
  "sessionCount": 3,
  "saved": "exports/itinerary.md"
}
```

**Example:**

```bash
curl "http://localhost:8080/export?interests=ai,agents"
```

## Configuration

### Environment Variables

Set in `.env` file or system environment.

#### Graph API Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GRAPH_TENANT_ID` | Yes* | — | Azure AD tenant ID |
| `GRAPH_CLIENT_ID` | Yes* | — | App registration client ID |
| `GRAPH_CLIENT_SECRET` | Yes* | — | Client secret value |
| `GRAPH_USER_ID` | No | — | Default user email |

*Required for Graph mode

#### Server Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | 8080 | HTTP server port |
| `INCLUDE_CARD` | No | false | Enable Adaptive Cards |
| `API_TOKEN` | No | — | Bearer token for auth |

#### Logging Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_LEVEL` | No | INFO | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `LOG_FILE` | No | — | Log file path (e.g., `~/.event_agent.log`) |

#### Feature Flags

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EXTERNAL_SESSIONS_FILE` | No | — | Path to external sessions JSON |

### Manifest Configuration (agent.json)

#### Weights

```json
{
  "weights": {
    "interests": 0.5,
    "topics": 0.3,
    "recency": 0.2
  }
}
```

| Weight | Range | Default | Description |
|--------|-------|---------|-------------|
| `interests` | 0.0-1.0 | 0.5 | Interest match importance |
| `topics` | 0.0-1.0 | 0.3 | Topic similarity weight |
| `recency` | 0.0-1.0 | 0.2 | Event recency bonus |

#### Feature Flags

```json
{
  "features": {
    "telemetry": {
      "enabled": true,
      "file": "telemetry.jsonl"
    },
    "export": {
      "enabled": true,
      "output_dir": "exports"
    },
    "externalSessions": {
      "enabled": false,
      "file": "sessions_external.json"
    }
  }
}
```

| Feature | Default | Description |
|---------|---------|-------------|
| `telemetry.enabled` | true | Log actions to JSONL |
| `export.enabled` | true | Save exports to file |
| `externalSessions.enabled` | false | Load sessions from file |

#### Recommend Settings

```json
{
  "recommend": {
    "max_sessions_default": 3,
    "min_score": 0.0
  }
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `max_sessions_default` | 3 | Default top N |
| `min_score` | 0.0 | Minimum score threshold |

## Profile Storage

Profiles stored at `~/.event_agent_profiles.json`:

```json
{
  "myprofile": {
    "interests": ["ai", "agents", "safety"],
    "created": "2024-01-15T10:00:00Z"
  }
}
```

**Management:**

```bash
# View all profiles
cat ~/.event_agent_profiles.json

# Delete a profile (edit file manually)
nano ~/.event_agent_profiles.json
```

## Error Codes

### HTTP Status Codes

| Code | Meaning | Cause |
|------|---------|-------|
| 200 | Success | Request completed |
| 400 | Bad Request | Missing required parameter |
| 401 | Unauthorized | Invalid or missing API_TOKEN |
| 404 | Not Found | Unknown endpoint |
| 502 | Bad Gateway | Graph API error |
| 503 | Service Unavailable | Graph support not installed |

### Error Response Format

```json
{
  "error": "error message",
  "details": "additional context"
}
```

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| Configuration | `.env` | Environment variables |
| Profiles | `~/.event_agent_profiles.json` | Saved user profiles |
| Token cache | `~/.event_agent_token_cache.json` | Graph API tokens |
| Telemetry | `telemetry.jsonl` | Action logs |
| Application log | `~/.event_agent.log` | Debug logs |
| Exports | `exports/` | Exported itineraries |
| Manifest | `agent.json` | Session definitions |

## Performance Tuning

### Token Caching

- Tokens cached for 1 hour
- Auto-refresh 5 minutes before expiration
- File: `~/.event_agent_token_cache.json`

### Event Caching

- In-memory cache, 5-minute TTL
- Configurable: `GraphEventService(cache_ttl=300)`
- Clears on application restart

### Rate Limiting

- Graph API: 10,000 requests per 10 minutes
- Automatic retry with exponential backoff
- Monitor in logs for "rate limited" warnings

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Tests

```bash
# Graph tests only
pytest tests/ -k graph -v

# Single test file
pytest tests/test_recommend.py -v

# Single test
pytest tests/test_recommend.py::test_basic_recommend -v
```

### Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html
# Open: htmlcov/index.html
```

## Quick Examples

### Complete Workflow

```bash
# 1. Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with credentials

# 2. Test configuration
python -c "from settings import Settings; print(Settings().validate_graph_ready())"

# 3. Get recommendations
python agent.py recommend --interests "ai, agents" --top 3

# 4. Using Graph
python agent.py recommend --source graph --interests "ai" --top 5

# 5. Start server
python agent.py serve --port 8080 --card

# 6. Test API
curl "http://localhost:8080/recommend?interests=ai&top=3"
```

### Common Tasks

```bash
# Save and reuse profile
python agent.py recommend --interests "ai, safety, ethics" --profile-save research
python agent.py recommend --profile-load research --top 10

# Export itinerary
python agent.py export --interests "ai" --output my-schedule.md
cat my-schedule.md

# Check Graph events
python agent.py recommend --source graph --interests "test" --top 1

# View telemetry
tail -f telemetry.jsonl

# Debug mode
LOG_LEVEL=DEBUG python agent.py recommend --interests "ai"
```

## See Also

- [Getting Started](01-GETTING-STARTED/quick-start.md) — First-time setup
- [CLI Usage Guide](02-USER-GUIDES/cli-usage.md) — Detailed CLI documentation
- [HTTP API Guide](02-USER-GUIDES/http-api.md) — Detailed API documentation
- [Graph Setup](03-GRAPH-API/setup.md) — Graph API configuration
- [Troubleshooting](03-GRAPH-API/troubleshooting.md) — Common issues
