# Graph API Architecture

How Microsoft Graph integration works in Event Kit.

## Overview

Event Kit integrates with Microsoft Graph API to fetch calendar events as an alternative to static manifest sessions. This enables recommendations based on actual user calendars.

## Architecture Diagram

```
User Request
    ↓
CLI / HTTP API
    ↓
core.py (recommend_from_graph)
    ↓
GraphEventService
    ↓
GraphAuthClient (MSAL)
    ↓
Microsoft Graph API
    ↓
Calendar Events
    ↓
Transform to Agent Schema
    ↓
Scoring & Recommendations
    ↓
Return Results
```

## Components

### 1. GraphAuthClient (`graph_auth.py`)

Handles Microsoft authentication using MSAL (Microsoft Authentication Library).

**Key features:**

- Token acquisition with client credentials flow
- Token caching to `~/.event_agent_token_cache.json`
- Automatic token refresh (5-minute buffer before expiration)
- Error handling for authentication failures

**Flow:**

1. Load cached token (if exists and valid)
2. If no token or expired, request new token from Azure AD
3. Cache token for reuse
4. Return access token for Graph API calls

**Code example:**

```python
from graph_auth import GraphAuthClient
from settings import Settings

settings = Settings()
auth_client = GraphAuthClient(settings)
token = auth_client.get_access_token()  # Returns cached or new token
```

### 2. GraphEventService (`graph_service.py`)

Fetches and transforms calendar events from Microsoft Graph.

**Key features:**

- Fetch calendar events for date range
- Transform Graph events to agent schema
- Event caching (5-minute TTL)
- Rate limit handling with exponential backoff
- Error handling for API failures

**Event transformation:**

Graph API returns events in Microsoft schema. We transform to agent schema:

```python
# Microsoft Graph event
{
  "subject": "AI Safety Workshop",
  "start": {"dateTime": "2024-01-15T09:00:00Z"},
  "end": {"dateTime": "2024-01-15T10:00:00Z"},
  "location": {"displayName": "Building 5"},
  "attendees": [...]
}

# Transformed to agent schema
{
  "id": "event-hash",
  "title": "AI Safety Workshop",
  "start": "09:00",
  "end": "10:00",
  "location": "Building 5",
  "tags": ["ai", "safety", "workshop"],
  "popularity": 0.85
}
```

**Code example:**

```python
from graph_service import GraphEventService

service = GraphEventService(auth_client, settings)
events = service.get_calendar_events(
    start_date="2024-01-15",
    end_date="2024-01-16"
)
```

### 3. Settings (`settings.py`)

Configuration management using pydantic-settings.

**Key features:**

- Load from environment variables
- Validation of required fields
- Type coercion
- Default values

**Configuration:**

```python
from settings import Settings

settings = Settings()

# Check if Graph is configured
if settings.validate_graph_ready():
    # Use Graph API
    pass
else:
    errors = settings.get_validation_errors()
    print(f"Graph not ready: {errors}")
```

### 4. Core Logic (`core.py`)

Recommendation engine with Graph integration.

**Key functions:**

- `recommend_from_graph()` — Get recommendations from Graph events
- Scoring algorithm (same as manifest mode)
- Conflict detection
- Telemetry logging

**Flow:**

1. Fetch events from Graph
2. Extract tags from event titles/descriptions
3. Score events based on interests
4. Detect scheduling conflicts
5. Return top N recommendations

**Code example:**

```python
from core import recommend_from_graph

result = recommend_from_graph(
    graph_service,
    interests=["ai", "safety"],
    top=3
)

# Returns:
# {
#   "source": "graph",
#   "sessions": [...],
#   "conflicts": 0,
#   "scoring": {...}
# }
```

## Data Flow

### Manifest Mode (Default)

```
agent.json → recommend() → scoring → results
```

### Graph Mode

```
Graph API → get_calendar_events() → transform → recommend_from_graph() → scoring → results
```

## Dual-Mode Support

Event Kit supports both modes simultaneously:

**Manifest mode:**

```bash
python agent.py recommend --interests "ai" --top 3
# Uses agent.json sessions
```

**Graph mode:**

```bash
python agent.py recommend --source graph --interests "ai" --top 3
# Uses Microsoft Graph calendar events
```

Both modes use the same scoring algorithm and return the same schema.

## Scoring Algorithm

Same algorithm for both modes:

```python
score = (interest_match * W_interest) + 
        (popularity * W_popularity) + 
        (diversity * W_diversity)
```

**Weights (from agent.json):**

- `W_interest` — How well event matches interests
- `W_popularity` — Event popularity (attendee count in Graph mode)
- `W_diversity` — Interest diversity bonus

**Graph-specific scoring:**

- `popularity` calculated from attendee count: `min(attendees / 100, 1.0)`
- Tags extracted from event subject/body using NLP patterns
- Time conflicts detected from calendar overlap

## Caching Strategy

### Token Caching

- Location: `~/.event_agent_token_cache.json`
- TTL: 1 hour (from Azure AD)
- Auto-refresh: 5 minutes before expiration
- Invalidation: On authentication errors

### Event Caching

- TTL: 5 minutes (configurable)
- Key: Date range hash
- Invalidation: On TTL expiration or manual clear
- In-memory only (not persisted)

## Error Handling

### Authentication Errors

- `GraphAuthError` — Token acquisition failed
- Automatic retry with new token
- Logs error details
- Returns 502 to client

### API Errors

- `GraphServiceError` — API call failed
- Rate limit: Automatic retry with backoff
- Network errors: Return 502
- Invalid response: Log and return empty results

### Validation Errors

- Missing credentials: Return 502 with details
- Invalid dates: Return 400
- Malformed events: Skip and log warning

## Security Considerations

### Authentication

- Client credentials flow (daemon app)
- Application permissions (not delegated)
- Token never logged or exposed
- Cached with user-only permissions

### API Access

- Read-only permissions (`Calendars.Read`)
- No write or delete permissions
- Admin consent required
- Audit logs in Azure AD

### Data Handling

- Events fetched on-demand (not stored)
- Token cache file encrypted at rest (OS-level)
- No PII logged
- HTTPS only for API calls

## Performance

### Token Acquisition

- First call: ~500-1000ms (network + Azure AD)
- Cached calls: <1ms (file read)
- Refresh: ~500ms (network)

### Event Fetching

- API latency: ~200-500ms
- Transform: ~5-10ms per event
- Total: ~500-1000ms for 50 events

### Recommendation Scoring

- Same as manifest mode: ~5-20ms
- Linear with event count
- Optimized with numpy/pandas (future)

## Monitoring

### Telemetry

All Graph operations logged to `telemetry.jsonl`:

```json
{
  "action": "recommend_graph",
  "timestamp": "2024-01-15T10:00:00Z",
  "duration_ms": 523,
  "success": true,
  "events_fetched": 47,
  "recommendations": 3
}
```

### Logging

Application logs to `~/.event_agent.log`:

```
[INFO] Token acquired successfully
[INFO] Fetched 47 events from Graph API
[DEBUG] Event transformed: AI Safety Workshop
[WARNING] Rate limited, retrying in 5s
```

## Testing

### Unit Tests

- `tests/test_graph_auth.py` — Authentication tests
- `tests/test_graph_service.py` — Event service tests
- `tests/test_core.py` — Recommendation tests (Graph mode)

### Integration Tests

- `tests/test_external_sessions.py` — End-to-end Graph tests
- Requires valid credentials in `.env.test`
- Mocked Graph responses for CI/CD

### Manual Testing

```bash
# Test authentication
python -c "from graph_auth import GraphAuthClient; from settings import Settings; print(GraphAuthClient(Settings()).get_access_token())"

# Test event fetching
python -c "from graph_service import GraphEventService; from graph_auth import GraphAuthClient; from settings import Settings; s = Settings(); a = GraphAuthClient(s); service = GraphEventService(a, s); print(len(service.get_calendar_events()))"

# Test recommendations
python agent.py recommend --source graph --interests "ai" --top 3
```

## Extending

### Custom Event Sources

To add custom event sources (SharePoint, Outlook, etc.):

1. Create new service class (e.g., `SharePointEventService`)
2. Implement `get_events()` method returning agent schema
3. Add to `core.py` source routing
4. Update CLI to accept new `--source` value

### Custom Transformations

To customize event transformation:

1. Edit `graph_service.py` → `_transform_event()`
2. Add custom tag extraction logic
3. Adjust popularity calculation
4. Update tests

### Custom Scoring

To add Graph-specific scoring:

1. Edit `core.py` → `recommend_from_graph()`
2. Add new scoring factors (e.g., recency, organizer)
3. Update weights in `agent.json`
4. Test with various inputs

## Next Steps

- 🚀 [Setup Guide](setup.md) — Configure Graph API
- 🆘 [Troubleshooting](troubleshooting.md) — Common issues
- 📚 [Development Guide](../06-DEVELOPMENT/contributing.md) — Contribute changes
