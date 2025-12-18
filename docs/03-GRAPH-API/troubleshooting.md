# Troubleshooting Guide

Common issues and solutions for Event Kit, including Graph API problems.

## Configuration Issues

### "Graph credentials not configured"

**Symptom:** Error when using `--source graph`

**Cause:** Missing or invalid Graph credentials in `.env`

**Solution:**

```bash
# Check if .env exists
cat .env

# Verify all three variables are set
python -c "from settings import Settings; print(Settings().get_validation_errors())"

# Should show:
# [] (empty list = all good)
# or specific missing variables
```

Create `.env` if missing:

```bash
cp .env.example .env
# Edit with your credentials
```

### "No interests provided"

**Symptom:** `{"error": "no interests provided"}`

**Cause:** Missing `--interests` parameter or empty profile

**Solution:**

```bash
# Provide interests explicitly
python agent.py recommend --interests "ai, agents" --top 3

# Or save a profile first
python agent.py recommend --interests "ai" --profile-save myprofile
python agent.py recommend --profile-load myprofile
```

### "Session not found"

**Symptom:** `{"error": "session not found"}` when using `/explain`

**Cause:** Session title doesn't match any events

**Solution:**

```bash
# List available sessions
python agent.py recommend --interests "any" --top 10

# Use exact title (case-sensitive)
python agent.py explain --session "Exact Session Title" --interests "ai"
```

## Graph API Issues

### "AADSTS700016: Application not found in directory"

**Symptom:** Authentication fails

**Cause:** Tenant ID or Client ID incorrect

**Solution:**

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Find your app
3. Copy **Directory (tenant) ID** and **Application (client) ID**
4. Update `.env`:

```bash
GRAPH_TENANT_ID=correct-tenant-id
GRAPH_CLIENT_ID=correct-client-id
```

### "AADSTS530007: Client secret has expired or is invalid"

**Symptom:** Authentication error

**Cause:** Client secret expired or incorrect

**Solution:**

1. Go to Azure Portal → Your app → **Certificates & secrets**
2. Delete old secret
3. Create new secret
4. Copy secret value
5. Update `.env`:

```bash
GRAPH_CLIENT_SECRET=new-secret-value
```

6. Restart application

### "No events returned" from Graph

**Symptom:** Empty recommendations from `--source graph`

**Cause:** No calendar events or permissions issue

**Solution:**

**Check user has events:**

```bash
# Verify date range has events
python -c "
from graph_service import GraphEventService
from graph_auth import GraphAuthClient
from settings import Settings
s = Settings()
a = GraphAuthClient(s)
service = GraphEventService(a, s)
events = service.get_calendar_events()
print(f'Found {len(events)} events')
"
```

**Check API permissions:**

1. Azure Portal → Your app → **API permissions**
2. Verify `Calendars.Read` is present
3. Check **Status** shows "Granted for [Org]"
4. If not granted, click "Grant admin consent"

**Check logs:**

```bash
cat ~/.event_agent.log | grep -i error
```

### "Rate limited - will retry"

**Symptom:** Warning in logs about rate limiting

**Cause:** Too many requests to Graph API

**Solution:**

- **Normal behavior** — automatic retry with backoff
- Graph API limit: 10,000 requests per 10 minutes
- For bulk operations, add delays between requests
- Consider caching results

### "Failed to load token cache"

**Symptom:** Warning about token cache file

**Cause:** File permissions or corrupt cache

**Solution:**

```bash
# Delete and regenerate cache
rm ~/.event_agent_token_cache.json

# Run command again (will create new cache)
python agent.py recommend --source graph --interests "ai" --top 3
```

## HTTP Server Issues

### "Port already in use"

**Symptom:** Server fails to start

**Cause:** Another process using the port

**Solution:**

```bash
# Try different port
python agent.py serve --port 8081

# Or kill existing process (Windows)
netstat -ano | findstr :8080
taskkill /PID <process-id> /F

# Or kill existing process (Linux/macOS)
lsof -ti:8080 | xargs kill -9
```

### "unauthorized" from HTTP API

**Symptom:** `401 {"error":"unauthorized"}`

**Cause:** `API_TOKEN` is set but not provided

**Solution:**

```bash
# Include Authorization header
curl -H "Authorization: Bearer your-token-here" \
  "http://localhost:8080/recommend?interests=ai"

# Or unset API_TOKEN for development
unset API_TOKEN
python agent.py serve --port 8080
```

## Manifest Issues

### "External sessions ignored"

**Symptom:** External sessions file not loaded

**Cause:** Feature disabled or file missing

**Solution:**

1. Enable in `agent.json`:

```json
{
  "features": {
    "externalSessions": {
      "enabled": true,
      "file": "sessions_external.json"
    }
  }
}
```

2. Create valid sessions file:

```json
{
  "sessions": [
    {
      "id": "ext-1",
      "title": "Custom Event",
      "topics": ["custom"]
    }
  ]
}
```

### "Telemetry file not created"

**Symptom:** No `telemetry.jsonl` file

**Cause:** Telemetry disabled or no actions executed

**Solution:**

1. Enable in `agent.json`:

```json
{
  "features": {
    "telemetry": {
      "enabled": true
    }
  }
}
```

2. Run some commands:

```bash
python agent.py recommend --interests "ai" --top 3
cat telemetry.jsonl
```

## Performance Issues

### "High latency spikes"

**Symptom:** Slow recommendations

**Cause:** Large session list or external data

**Solution:**

```bash
# Profile to find bottleneck
python -m cProfile -o profile.stats agent.py recommend --interests "ai" --top 3

# Analyze results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumtime'); p.print_stats(10)"

# Reduce session count for testing
# Edit agent.json to include fewer sessions
```

### "Export not saving file"

**Symptom:** Export doesn't create file

**Cause:** Export feature disabled or no write permissions

**Solution:**

1. Enable in `agent.json`:

```json
{
  "features": {
    "export": {
      "enabled": true,
      "output_dir": "exports"
    }
  }
}
```

2. Check directory permissions:

```bash
# Create directory
mkdir -p exports

# Check permissions (Linux/macOS)
ls -la exports

# On Windows, ensure you have write access
```

## Testing Issues

### "Tests failing" after changes

**Symptom:** pytest reports failures

**Solution:**

```bash
# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_recommend.py::test_basic_recommend -v

# Show print statements
pytest tests/ -v -s

# Show full traceback
pytest tests/ -v --tb=long
```

### "Import errors" in tests

**Symptom:** `ModuleNotFoundError` or `ImportError`

**Solution:**

```bash
# Install in development mode
pip install -e .

# Or install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import agent; import core; import settings"
```

## Logging & Debugging

### Enable Debug Logging

```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Or in .env
echo "LOG_LEVEL=DEBUG" >> .env

# Run command
python agent.py recommend --source graph --interests "ai" --top 3

# Check logs
tail -f ~/.event_agent.log
```

### View Telemetry

```bash
# View recent actions
tail -n 20 telemetry.jsonl

# Count actions
wc -l telemetry.jsonl

# Summarize (if script exists)
python scripts/summarize_telemetry.py
```

### Check Configuration

```bash
# Verify settings loaded correctly
python -c "
from settings import Settings
s = Settings()
print('Graph ready:', s.validate_graph_ready())
print('Tenant:', s.graph_tenant_id)
print('Client:', s.graph_client_id)
print('Secret set:', bool(s.graph_client_secret))
"
```

## Common Workflow Issues

### Profile not saving

**Symptom:** Profile not found when loading

**Cause:** Profile file doesn't exist or wrong name

**Solution:**

```bash
# Check profile file
cat ~/.event_agent_profiles.json

# Should show profiles like:
# {
#   "myprofile": {
#     "interests": ["ai", "agents"],
#     "created": "2024-01-15T10:00:00"
#   }
# }

# Use exact profile name when loading
python agent.py recommend --profile-load myprofile
```

### Adaptive Cards not appearing

**Symptom:** No `adaptiveCard` in HTTP response

**Cause:** Card flag not set

**Solution:**

```bash
# Start server with --card flag
python agent.py serve --port 8080 --card

# Or request card in query parameter
curl "http://localhost:8080/recommend?interests=ai&card=1"
```

## Getting Help

### Collect Diagnostics

```bash
# System info
python --version
pip list | grep -E "msal|msgraph|pydantic"

# Configuration check
python -c "from settings import Settings; print(Settings().get_validation_errors())"

# Recent logs
tail -n 50 ~/.event_agent.log

# Recent telemetry
tail -n 20 telemetry.jsonl
```

### Check Documentation

- [Setup Guide](setup.md) — Initial configuration
- [Architecture Guide](architecture.md) — How it works
- [CLI Usage](../02-USER-GUIDES/cli-usage.md) — Command reference
- [HTTP API](../02-USER-GUIDES/http-api.md) — API documentation

### Check External Resources

- [Microsoft Graph API Status](https://docs.microsoft.com/graph/api/overview)
- [Azure AD Documentation](https://docs.microsoft.com/azure/active-directory/)
- [MSAL Python Docs](https://github.com/AzureAD/microsoft-authentication-library-for-python)

## FAQ

### Q: Do I need admin consent for Graph API?

**A:** Yes, for application permissions (`Calendars.Read`). A global admin must grant consent in Azure Portal.

### Q: How long do tokens last?

**A:** Tokens are valid for 1 hour. They auto-refresh 5 minutes before expiration.

### Q: Can I use delegated permissions instead?

**A:** Not recommended. Event Kit is a daemon app designed for application permissions.

### Q: How do I rotate secrets?

**A:**

1. Create new secret in Azure Portal
2. Update `.env` with new secret
3. Restart application
4. Delete old secret after verification

### Q: Why are my calendar events not showing?

**A:** Check:

1. Admin consent granted for `Calendars.Read`
2. User has calendar events in date range
3. Credentials are correct in `.env`
4. No network/firewall issues

### Q: Can I use with multiple tenants?

**A:** Yes, but you need separate app registrations per tenant, or use multi-tenant app registration.

### Q: How do I clear the cache?

**A:**

```bash
# Token cache
rm ~/.event_agent_token_cache.json

# Event cache (in-memory only, clears on restart)
# Just restart the application
```
