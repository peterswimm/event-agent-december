# Graph API Integration - Quick Reference

## Setup (5 minutes)

```bash
# 1. Set environment variables
export GRAPH_TENANT_ID=your-tenant-id
export GRAPH_CLIENT_ID=your-client-id  
export GRAPH_CLIENT_SECRET=your-client-secret

# 2. Verify configuration
python -c "from settings import Settings; print('Ready:', Settings().validate_graph_ready())"

# 3. Test CLI
python agent.py recommend --source graph --interests ai --top 3

# 4. Start server
python agent.py serve --port 8000
```

## CLI Usage

```bash
# Graph recommendations (vs manifest default)
python agent.py recommend --source graph --interests "ai safety" --top 3 --user-id user@company.com

# Manifest recommendations (default)
python agent.py recommend --interests "ai safety" --top 3

# Explain a session
python agent.py explain --session "Title" --interests "ai"

# Save/load profiles
python agent.py recommend --source graph --interests "ai" --profile-save myprofile
python agent.py recommend --source graph --profile-load myprofile
```

## HTTP Endpoints

```bash
# Manifest recommendations (existing)
curl "http://localhost:8000/recommend?interests=ai+safety&top=3"

# Graph recommendations (new)
curl "http://localhost:8000/recommend-graph?interests=ai+safety&top=3&userId=user@company.com"

# Both support Adaptive Card format
curl "http://localhost:8000/recommend-graph?interests=ai&card=1"

# Health check
curl "http://localhost:8000/health"

# Explain session
curl "http://localhost:8000/explain?session=Title&interests=ai"

# Export (manifest-based)
curl "http://localhost:8000/export?interests=ai+safety" > itinerary.md
```

## Environment Variables

```bash
# Required for Graph mode
GRAPH_TENANT_ID         # Azure AD tenant ID
GRAPH_CLIENT_ID         # Application (client) ID
GRAPH_CLIENT_SECRET     # Client secret value

# Optional
LOG_LEVEL              # DEBUG|INFO|WARNING|ERROR (default: INFO)
LOG_FILE               # Path to log file (default: none)
API_TOKEN              # For HTTP endpoint authentication
RUN_MODE              # test|dev|prod (default: dev)
```

## File Structure

```
event-agent-example/
├── graph_auth.py              # MSAL authentication
├── graph_service.py           # Graph API wrapper
├── core.py                    # Scoring and recommendations
├── agent.py                   # CLI and HTTP server
├── settings.py                # Configuration
├── logging_config.py          # Logging setup
├── .env                       # Configuration file (not committed)
├── docs/
│   └── graph-setup.md        # Full setup guide
├── tests/
│   ├── test_graph_auth.py    # Auth tests
│   ├── test_graph_service.py # Service tests
│   ├── test_core_graph.py    # Recommendation tests
│   ├── test_graph_integration.py  # Integration tests
│   └── test_graph_server.py  # HTTP endpoint tests
└── agent.json               # Manifest (can be used with --source manifest)
```

## Features

| Feature | Manifest | Graph |
|---------|----------|-------|
| Static events | ✅ | ❌ |
| Calendar integration | ❌ | ✅ |
| Real popularity scores | ❌ | ✅ |
| User filtering | ❌ | ✅ |
| Event transformation | Manual | Automatic |
| Token caching | N/A | ✅ |
| Rate limiting | N/A | ✅ |

## Common Issues

| Issue | Solution |
|-------|----------|
| "Graph credentials not configured" | Set all three env vars: TENANT_ID, CLIENT_ID, CLIENT_SECRET |
| "AADSTS700016" | Verify tenant ID and client ID match Azure portal |
| "Client secret expired" | Generate new secret in Azure portal, update .env |
| "No events returned" | Check user has calendar events, verify Calendars.Read permission |
| "Rate limited" | Automatic retry, normal for high-frequency requests |
| "Failed to load token cache" | Delete `~/.event_agent_token_cache.json` and retry |

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run Graph-specific tests
python -m pytest tests/test_graph_*.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Integration test
python -m pytest tests/test_graph_integration.py::TestGraphIntegrationEndToEnd -v
```

## Performance

- **Token caching**: 5-minute TTL, auto-refresh
- **Event caching**: 300-second TTL
- **Rate limiting**: 10,000 requests/10 minutes (Graph default)
- **Automatic retry**: 429 responses with Retry-After backoff

## Security

- ✅ Credentials in environment variables (not hardcoded)
- ✅ Client secret never logged
- ✅ Token auto-expires with 5-minute buffer
- ✅ Application permissions (not delegated)
- ✅ MSAL cache protected with file permissions
- ⚠️ CORS: Set explicit origins in production (currently *)

## Logging

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python agent.py recommend --source graph --interests ai

# Write to file
LOG_FILE=~/.event_agent.log python agent.py recommend --source graph --interests ai

# View logs
tail -f ~/.event_agent.log

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Deployment

### Local Testing
```bash
python agent.py recommend --source graph --interests "test" --top 1
```

### Server Mode
```bash
LOG_LEVEL=INFO python agent.py serve --port 8000 &
```

### Docker
Add to Dockerfile:
```dockerfile
ENV GRAPH_TENANT_ID=${GRAPH_TENANT_ID}
ENV GRAPH_CLIENT_ID=${GRAPH_CLIENT_ID}
ENV GRAPH_CLIENT_SECRET=${GRAPH_CLIENT_SECRET}
```

## Azure AD Setup (One-time)

1. Register app in Azure portal
2. Add client secret
3. Grant "Calendars.Read" permission
4. Grant admin consent
5. Copy Tenant ID, Client ID, Client Secret
6. Set environment variables
7. Done!

See [docs/graph-setup.md](graph-setup.md) for detailed steps.
