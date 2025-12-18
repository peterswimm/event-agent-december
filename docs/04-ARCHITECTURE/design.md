# System Architecture & Design

High-level overview of Event Kit's architecture, design patterns, and system structure.

## Architecture Overview

Event Kit follows a **declarative agent pattern** with minimal dependencies:

```text
User Request (CLI/HTTP)
    ↓
Command Parser (agent.py)
    ↓
Core Logic (core.py)
    ↓
Data Source (Manifest or Graph)
    ↓
Scoring Engine
    ↓
Results + Telemetry
```

## Core Components

### 1. Entry Point (`agent.py`)

Main application entry point handling:

- CLI command parsing (`argparse`)
- HTTP server (`HTTPServer`)
- Routing to core functions
- Adaptive Card generation
- Telemetry integration

**Key responsibilities:**

- Parse user input (interests, flags, options)
- Route to appropriate core function
- Format output (JSON, Markdown, Adaptive Cards)
- Handle HTTP requests/responses
- Log actions to telemetry

### 2. Core Logic (`core.py`)

Business logic for recommendations and scoring:

- `recommend()` — Manifest-based recommendations
- `recommend_from_graph()` — Graph API recommendations
- `explain()` — Session scoring explanation
- Session scoring algorithm
- Conflict detection
- Interest normalization

**Scoring formula:**

```python
score = (interest_match * W_interest) + 
        (popularity * W_popularity) + 
        (diversity * W_diversity)
```

### 3. Configuration (`settings.py`)

Pydantic-based configuration management:

- Environment variable loading
- Type validation
- Default values
- Graph API credentials validation

**Configuration hierarchy:**

1. Environment variables (`.env`)
2. System environment
3. Default values

### 4. Graph Integration

**GraphAuthClient** (`graph_auth.py`):

- MSAL authentication
- Token caching
- Automatic refresh

**GraphEventService** (`graph_service.py`):

- Calendar event fetching
- Event transformation
- Response caching
- Rate limit handling

### 5. Telemetry (`telemetry.py`)

Structured logging to `telemetry.jsonl`:

```json
{
  "ts": 1732540000.123,
  "action": "recommend",
  "success": true,
  "latency_ms": 12.5,
  "payload": {...}
}
```

## Data Flow

### Manifest Mode

```
user interests → normalize → load agent.json → 
score sessions → sort by score → top N → 
detect conflicts → format output → telemetry
```

### Graph Mode

```
user interests → normalize → authenticate (MSAL) → 
fetch calendar events → transform to schema → 
score events → sort by score → top N → 
detect conflicts → format output → telemetry
```

## Design Patterns

### 1. Declarative Configuration

**Pattern:** Configuration as data, not code

**Implementation:**

- `agent.json` defines sessions, weights, features
- No code changes needed to adjust recommendations
- Feature flags control behavior

**Benefits:**

- Easy to modify without deploying code
- Version control for business logic
- Non-developers can adjust weights

### 2. Dual-Mode Support

**Pattern:** Pluggable data sources

**Implementation:**

- `--source manifest` uses `agent.json`
- `--source graph` uses Microsoft Graph API
- Same scoring algorithm for both

**Benefits:**

- Start simple (manifest) → scale up (Graph)
- Test without external dependencies
- Easy A/B comparison

### 3. Telemetry First

**Pattern:** Observable by default

**Implementation:**

- Every action logged to JSONL
- Success/error tracking
- Latency measurement
- Structured format for analysis

**Benefits:**

- No instrumentation code in business logic
- Easy to aggregate and analyze
- Audit trail included

### 4. Profile Persistence

**Pattern:** User state management

**Implementation:**

- Save interests to named profiles
- Load profiles for quick reuse
- JSON file storage

**Benefits:**

- Faster repeated queries
- User preference memory
- Profile comparison workflows

### 5. Conflict Detection

**Pattern:** Time slot validation

**Implementation:**

- Track `(start, end)` pairs
- Count overlapping slots
- Report in results

**Benefits:**

- Schedule feasibility check
- User can see conflicts upfront
- Optimize for conflict-free recommendations

## Module Structure

```
event-agent-example/
├── agent.py              # CLI & HTTP server entry point
├── core.py               # Recommendation engine
├── settings.py           # Configuration management
├── telemetry.py          # Structured logging
├── graph_auth.py         # MSAL authentication
├── graph_service.py      # Graph API client
├── logging_config.py     # Logging setup
├── agent.json            # Session manifest
├── .env                  # Environment config
└── tests/                # Test suite
    ├── test_recommend.py
    ├── test_graph_*.py
    └── ...
```

## Extensibility Points

### Adding New Data Sources

To add a new data source (e.g., SharePoint):

1. Create service class: `sharepoint_service.py`
2. Implement `get_events()` returning standard schema
3. Add to `core.py` source routing
4. Update CLI `--source` options

**Example:**

```python
# sharepoint_service.py
class SharePointService:
    def get_events(self):
        # Fetch from SharePoint
        return [{"id": ..., "title": ..., "tags": ...}]

# core.py
if source == "sharepoint":
    service = SharePointService(settings)
    return recommend_from_events(service.get_events(), interests, top)
```

### Adding New Scoring Factors

To add new scoring factors (e.g., recency):

1. Add weight to `agent.json`:

```json
{
  "weights": {
    "interest": 2.0,
    "popularity": 0.5,
    "recency": 0.3
  }
}
```

2. Update scoring in `core.py`:

```python
recency_score = calculate_recency(session)
total += recency_score * weights["recency"]
```

3. Add to scoring breakdown in results

### Adding New Output Formats

To add new output formats (e.g., iCal):

1. Create format function:

```python
def _build_ical(sessions):
    # Generate .ics format
    return ical_string
```

2. Add format parameter to CLI/API
3. Route to format function in `agent.py`

## Security Architecture

### Authentication

- Graph API: Application permissions (daemon app)
- HTTP API: Optional bearer token (`API_TOKEN`)
- No user authentication (single-tenant design)

### Data Protection

- Credentials in environment variables only
- Token cache encrypted at rest (OS-level)
- No PII in telemetry by default
- HTTPS required for production

### Input Validation

- Interests treated as plain text (no execution)
- Session titles sanitized
- Query parameters validated
- No SQL injection risk (no database)

### Access Control

- Feature flags control capability exposure
- Admin consent required for Graph API
- Read-only Graph permissions
- No write operations to external systems

## Performance Characteristics

### Time Complexity

- Scoring: O(N × M) where N=sessions, M=interests
- Sorting: O(N log N)
- Conflict detection: O(N²) worst case (typically O(N))

**Overall:** O(N × M + N log N)

### Space Complexity

- Sessions in memory: O(N)
- Token cache: O(1) file
- Telemetry: O(actions) append-only
- Profiles: O(profiles) in JSON

### Latency Targets

| Operation | Target | Typical |
|-----------|--------|---------|
| Recommend (manifest) | <25ms | 12-15ms |
| Recommend (Graph) | <1000ms | 500-800ms |
| Explain | <15ms | 8-10ms |
| Export | <40ms | 20-30ms |

## Scalability

### Current Limits

- Sessions: ~10,000 (manifest mode)
- Events: ~1,000 per Graph query
- Concurrent requests: 1 (single-threaded HTTP)

### Scaling Options

**Vertical:**

- Pre-index tags for O(1) lookup
- Cache recommendations (5-min TTL)
- Vectorize interests for semantic search

**Horizontal:**

- Deploy behind load balancer
- Use WSGI server (Gunicorn)
- Add Redis cache layer
- Queue-based background processing

## Error Handling Strategy

### Fail Fast

- Missing required parameters → 400 error
- Invalid configuration → startup failure
- Authentication errors → 502 error

### Graceful Degradation

- Graph API unavailable → log error, return empty
- External sessions file missing → fall back to manifest
- Token cache corrupt → regenerate

### Retry Logic

- Graph API rate limits → exponential backoff
- Network errors → 3 retries with delay
- Token refresh → automatic before expiration

## Testing Strategy

### Unit Tests

- Pure functions (scoring, normalization)
- Mock external dependencies
- Fast execution (<1s total)

### Integration Tests

- Graph API with real credentials
- HTTP server endpoints
- File I/O operations

### Coverage

- Target: >80% line coverage
- Critical paths: 100% coverage
- All error paths tested

## Monitoring & Observability

### Metrics

Collected from `telemetry.jsonl`:

- Request count by action
- Success/error rate
- P50/P95/P99 latency
- Conflict rate

### Logs

Application logs (`~/.event_agent.log`):

- Authentication events
- API calls
- Error details
- Debug information

### Alerting Hooks

- Parse telemetry for error spikes
- Monitor latency degradation
- Track Graph API rate limits
- Detect configuration issues

## Deployment Patterns

### Standalone

- Single Python process
- Local or VM deployment
- Manual start/stop
- Development/testing

### Containerized

- Docker image with dependencies
- Docker Compose for orchestration
- Environment-based configuration
- Production-ready

### Serverless

- Azure Functions / AWS Lambda
- Event-driven invocation
- Auto-scaling
- Pay-per-use

### System Service

- systemd unit file
- Auto-start on boot
- Log rotation
- Health monitoring

## Future Architecture

### Planned Enhancements

1. **Multi-tenant support** — Separate data per organization
2. **Database backend** — PostgreSQL for sessions storage
3. **Real-time updates** — WebSocket for live recommendations
4. **ML scoring** — Train models on user feedback
5. **Distributed caching** — Redis for shared state

### Migration Path

1. Add database abstraction layer
2. Implement repository pattern
3. Introduce service layer
4. Add event bus for async processing
5. Deploy microservices architecture

## Next Steps

- 📖 [Module Reference](modules.md) — Detailed module documentation
- 🎯 [Scoring Algorithm](scoring-algorithm.md) — Deep dive into scoring
- 🎨 [Application Patterns](patterns.md) — Common usage patterns
- 📊 [Performance Guide](../05-PRODUCTION/performance.md) — Optimization tips

