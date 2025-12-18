# Module Reference

Complete reference for all Event Kit modules.

## Overview

Event Kit is structured as a modular Python application with the following core modules:

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `agent.py` | CLI & HTTP entry point | `recommend()`, `explain()`, server |
| `core.py` | Recommendation logic | `recommend_from_graph()`, scoring |
| `settings.py` | Configuration management | `Settings` class |
| `telemetry.py` | Structured logging | `get_telemetry()`, append |
| `graph_auth.py` | MSAL authentication | `GraphAuthClient` |
| `graph_service.py` | Graph API client | `GraphEventService` |
| `logging_config.py` | Logging setup | `setup_logging()` |

## agent.py

**Purpose:** Main entry point for CLI commands and HTTP server.

### Key Functions

#### `load_manifest(path: pathlib.Path) -> Dict[str, Any]`

Loads the `agent.json` manifest file.

**Parameters:**

- `path` — Path to manifest file (default: `agent.json` in script directory)

**Returns:** Dictionary with sessions, weights, and features

**Raises:** `json.JSONDecodeError` if manifest is invalid

#### `recommend(manifest: Dict, interests: List[str], top_n: int) -> Dict`

Generates recommendations from manifest sessions.

**Parameters:**

- `manifest` — Loaded manifest dictionary
- `interests` — List of normalized interest strings
- `top_n` — Number of recommendations to return

**Returns:**

```python
{
    "sessions": [...],      # Top N recommended sessions
    "scoring": [...],       # Score breakdown for each
    "conflicts": int        # Number of time conflicts
}
```

#### `explain(manifest: Dict, title: str, interests: List[str]) -> Dict`

Explains scoring for a specific session.

**Parameters:**

- `manifest` — Loaded manifest
- `title` — Session title to explain
- `interests` — User interests for scoring

**Returns:**

```python
{
    "title": str,
    "score": float,
    "contributions": {...},  # Breakdown by factor
    "matched_tags": [...]    # Tags that matched interests
}
```

#### `score_session(session: Dict, interests: List[str], weights: Dict) -> Dict`

Scores a single session against interests.

**Parameters:**

- `session` — Session dictionary with tags, popularity
- `interests` — Normalized interest list
- `weights` — Scoring weights dict

**Returns:**

```python
{
    "session": {...},
    "score": float,
    "contributions": {
        "interest_match": float,
        "popularity": float,
        "diversity": float
    }
}
```

### HTTP Server

#### `EventAgentHandler` (BaseHTTPRequestHandler)

Handles HTTP requests for API endpoints.

**Endpoints:**

- `GET /health` — Health check
- `POST /recommend` — Manifest recommendations
- `POST /recommend-graph` — Graph API recommendations
- `POST /explain` — Explain session scoring
- `POST /export` — Export itinerary

**Request format:**

```json
{
    "interests": ["ai", "agents"],
    "top": 3,
    "userId": "user@example.com"  // Graph only
}
```

**Response format:**

```json
{
    "sessions": [...],
    "scoring": [...],
    "conflicts": 2,
    "source": "manifest"
}
```

## core.py

**Purpose:** Core recommendation logic, importable by other modules.

### Key Functions

#### `recommend(manifest: Dict, interests: List[str], top: int) -> Dict`

Delegates to `agent.recommend()` for manifest-based recommendations.

**Signature:** Same as `agent.recommend()`

#### `explain(manifest: Dict, session_title: str, interests: List[str]) -> Dict`

Delegates to `agent.explain()` for session scoring explanation.

**Signature:** Same as `agent.explain()`

#### `recommend_from_graph(graph_service, interests: List[str], top: int, weights: Dict = None) -> Dict`

Generates recommendations from Microsoft Graph calendar events.

**Parameters:**

- `graph_service` — `GraphEventService` instance
- `interests` — Interest list
- `top` — Number of recommendations
- `weights` — Optional scoring weights (default: `{interest: 2.0, popularity: 0.5, diversity: 0.3}`)

**Returns:**

```python
{
    "sessions": [...],
    "scoring": [...],
    "conflicts": int,
    "source": "graph"
}
```

**Raises:**

- `ValueError` — Empty interests or invalid top
- `GraphServiceError` — Graph API failure
- `GraphAuthError` — Authentication failure

## settings.py

**Purpose:** Configuration management using Pydantic.

### Settings Class

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TENANT_ID: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    DEFAULT_USER_ID: Optional[str] = None
    API_TOKEN: Optional[str] = None
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

**Usage:**

```python
from settings import Settings

settings = Settings()  # Loads from .env
tenant = settings.TENANT_ID
```

**Environment variables:**

- `TENANT_ID` — Azure AD tenant ID (required)
- `CLIENT_ID` — App registration client ID (required)
- `CLIENT_SECRET` — App secret (required)
- `DEFAULT_USER_ID` — Default user email (optional)
- `API_TOKEN` — HTTP API bearer token (optional)
- `PORT` — HTTP server port (default: 8000)

## telemetry.py

**Purpose:** Structured telemetry logging to JSONL.

### Key Functions

#### `get_telemetry(manifest: Dict) -> Callable`

Creates a telemetry logger function.

**Parameters:**

- `manifest` — Manifest with telemetry config

**Returns:** Function to log telemetry entries

**Usage:**

```python
log = get_telemetry(manifest)
log("recommend", success=True, latency_ms=12.5, payload={...})
```

**Output format:**

```json
{
    "ts": 1732540000.123,
    "action": "recommend",
    "success": true,
    "latency_ms": 12.5,
    "payload": {...},
    "error": null
}
```

**Configuration:**

```json
{
    "telemetry": {
        "enabled": true,
        "file": "telemetry.jsonl",
        "maxSizeBytes": 52428800
    }
}
```

## graph_auth.py

**Purpose:** Microsoft Graph authentication using MSAL.

### GraphAuthClient

```python
class GraphAuthClient:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """Initialize MSAL authentication client."""
        
    def get_token(self) -> str:
        """Acquire access token for Graph API."""
        
    def clear_cache(self) -> None:
        """Clear cached tokens."""
```

**Token caching:**

- Location: `~/.msal_token_cache.bin`
- Format: Encrypted JSON
- Auto-refresh: Before expiration

**Scopes:**

- `https://graph.microsoft.com/.default`

**Error handling:**

```python
from graph_auth import GraphAuthError

try:
    token = client.get_token()
except GraphAuthError as e:
    print(f"Auth failed: {e}")
```

## graph_service.py

**Purpose:** Microsoft Graph calendar API client.

### GraphEventService

```python
class GraphEventService:
    def __init__(self, auth_client: GraphAuthClient, user_id: str):
        """Initialize Graph service with authenticated client."""
        
    def get_events(self, top: int = 10) -> List[Dict[str, Any]]:
        """Fetch calendar events for user."""
```

**Event transformation:**

Graph calendar event → Event Kit session format:

```python
{
    "id": event["id"],
    "title": event["subject"],
    "start": event["start"]["dateTime"],
    "end": event["end"]["dateTime"],
    "location": event["location"]["displayName"],
    "tags": event.get("categories", []),
    "popularity": 0  # Default
}
```

**Caching:**

- Cache duration: 5 minutes
- Key: `user_id`
- Eviction: LRU

**Rate limiting:**

- Retry on 429 status
- Exponential backoff (1s, 2s, 4s)
- Max retries: 3

## logging_config.py

**Purpose:** Application-wide logging configuration.

### Functions

#### `setup_logging(level: str = "INFO") -> None`

Configures root logger with file and console handlers.

**Parameters:**

- `level` — Log level (DEBUG, INFO, WARNING, ERROR)

**Output:**

- File: `~/.event_agent.log`
- Console: Colored output (if terminal)
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

**Usage:**

```python
from logging_config import setup_logging
import logging

setup_logging("DEBUG")
logger = logging.getLogger(__name__)
logger.info("Application started")
```

## Data Schemas

### Session Schema

```python
{
    "id": str,              # Unique session ID
    "title": str,           # Session title
    "start": str,           # ISO timestamp or time string
    "end": str,             # ISO timestamp or time string
    "location": str,        # Room or location
    "tags": List[str],      # Tags for matching
    "popularity": int       # Popularity score (0-10)
}
```

### Manifest Schema

```python
{
    "weights": {
        "interest": float,
        "popularity": float,
        "diversity": float
    },
    "sessions": List[Session],
    "telemetry": {
        "enabled": bool,
        "file": str,
        "maxSizeBytes": int
    },
    "features": {
        "externalSessions": {
            "enabled": bool,
            "file": str
        }
    }
}
```

### Telemetry Entry Schema

```json
{
    "ts": float,            // Unix timestamp
    "action": str,          // Action name
    "success": bool,        // Success flag
    "latency_ms": float,    // Latency in milliseconds
    "payload": object,      // Action-specific data
    "error": str | null     // Error message if failed
}
```

## Error Handling

### Exception Hierarchy

```text
Exception
├── GraphAuthError (graph_auth.py)
│   ├── Token acquisition failure
│   └── Invalid credentials
└── GraphServiceError (graph_service.py)
    ├── API request failure
    ├── Rate limiting
    └── Invalid response
```

### Error Responses

HTTP API errors:

```python
{
    "error": str,           # Error message
    "details": str,         # Additional context
    "code": int             # HTTP status code
}
```

## Testing Utilities

### Mock Data

```python
# tests/test_fixtures.py
MOCK_MANIFEST = {
    "weights": {"interest": 2.0, "popularity": 0.5, "diversity": 0.3},
    "sessions": [...]
}

MOCK_SESSIONS = [
    {
        "id": "session-1",
        "title": "AI Safety Workshop",
        "tags": ["ai", "safety"],
        "popularity": 5
    }
]
```

### Test Helpers

```python
from tests.test_helpers import create_test_manifest, create_mock_graph_service

manifest = create_test_manifest(sessions=MOCK_SESSIONS)
service = create_mock_graph_service(events=[...])
```

## Next Steps

- 🎯 [Scoring Algorithm](scoring-algorithm.md) — Deep dive into scoring
- 🏗️ [System Design](design.md) — Architecture overview
- 🎨 [Application Patterns](patterns.md) — Common usage patterns
- 🧪 [Testing Guide](../06-DEVELOPMENT/testing.md) — Test suite reference
