# Microsoft Graph API Setup

Complete guide for setting up Microsoft Graph integration to use your calendar events for recommendations.

## Overview

Event Kit supports Microsoft Graph API for fetching calendar events from Exchange Online, enabling:

- **Real calendar integration**: Use actual calendar events instead of sample data
- **User-specific recommendations**: Filter events by user interests
- **Dynamic event scoring**: Score based on real popularity and attendee counts
- **Dual-mode support**: Switch between manifest and Graph modes

## Prerequisites

### Required Azure Resources

- Azure subscription
- Azure Active Directory access
- Permissions to register applications

### Required Packages

Already included in `requirements.txt`:

- `msal` (1.25.0+) — Microsoft Authentication Library
- `msgraph-core` (1.0.0+) — Microsoft Graph API client
- `pydantic-settings` (2.0.0+) — Configuration management
- `azure-identity` (1.14.0+) — Azure authentication

Install with:

```bash
pip install -r requirements.txt msal msgraph-core azure-identity
```

## Azure AD Application Setup

### Step 1: Register Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **+ New registration**
4. Configure:
   - **Name**: "Event Agent"
   - **Supported account types**: "Accounts in this organizational directory only"
   - **Redirect URI**: Leave blank
5. Click **Register**

### Step 2: Create Client Secret

1. In your app, go to **Certificates & secrets**
2. Click **+ New client secret**
3. Add description (e.g., "Event Agent Secret") and expiration
4. Click **Add**
5. **⚠️ Copy the secret value immediately** (won't be shown again)

### Step 3: Grant API Permissions

1. Go to **API permissions**
2. Click **+ Add a permission** → **Microsoft Graph**
3. Choose **Application permissions** (not Delegated)
4. Add these permissions:
   - `Calendars.Read` — Read calendar events
   - `User.Read` — Read basic user info
5. Click **Add permissions**
6. **⚠️ Click "Grant admin consent for [Org Name]"** (requires admin)

### Step 4: Collect Credentials

From the app overview page, copy:

- **Tenant ID**: "Directory (tenant) ID"
- **Client ID**: "Application (client) ID"
- **Client Secret**: From Step 2

## Configuration

### Create .env File

Create `.env` in the project root:

```bash
# Microsoft Graph Credentials
GRAPH_TENANT_ID=your-tenant-id-here
GRAPH_CLIENT_ID=your-client-id-here
GRAPH_CLIENT_SECRET=your-client-secret-here

# Optional: Default user for Graph queries
# GRAPH_USER_ID=user@company.com

# Optional: Logging
# LOG_LEVEL=INFO
# LOG_FILE=~/.event_agent.log
```

**Security:** Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
echo "~/.event_agent_token_cache.json" >> .gitignore
```

### Verify Configuration

Test your setup:

```bash
# Check if Graph is ready
python -c "from settings import Settings; print('Graph ready:', Settings().validate_graph_ready())"

# If False, see validation errors:
python -c "from settings import Settings; print(Settings().get_validation_errors())"
```

Expected output:

```
Graph ready: True
```

## Usage

### CLI Commands

#### Graph Recommendations

```bash
# Get recommendations from your calendar
python agent.py recommend --source graph --interests "ai, agents" --top 3

# With user tracking
python agent.py recommend --source graph --user-id user@company.com --interests "ai" --top 5

# Save profile
python agent.py recommend --source graph --interests "ai, safety" --profile-save my_profile

# Load profile
python agent.py recommend --source graph --profile-load my_profile --top 3
```

#### Explain Graph Events

```bash
# Explain why a calendar event was recommended
python agent.py explain --source graph --session "Meeting Title" --interests "ai"
```

#### Export from Graph

```bash
# Export Graph recommendations to file
python agent.py export --source graph --interests "ai, agents" --output my_calendar.md
```

### HTTP API

Start the server:

```bash
python agent.py serve --port 8000 --card
```

#### GET /recommend-graph

Get recommendations from Microsoft Graph.

**Query parameters:**

- `interests` (required): Comma-separated interests
- `top` (optional): Number of results
- `userId` (optional): User email for tracking
- `card` (optional): `1` for Adaptive Card format

**Example:**

```bash
curl "http://localhost:8000/recommend-graph?interests=ai+safety&top=3&userId=user@company.com"
```

**Response:**

```json
{
  "source": "graph",
  "sessions": [
    {
      "title": "AI Safety Workshop",
      "start": "09:00",
      "end": "10:00",
      "location": "Building 5",
      "tags": ["ai", "safety"],
      "popularity": 0.85,
      "score": 4.23
    }
  ],
  "userId": "user@company.com"
}
```

## Troubleshooting

See [Troubleshooting Guide](troubleshooting.md) for detailed solutions.

### Configuration Issues

**Problem:** "Graph credentials not configured"

**Solution:**

```bash
# Verify .env exists
cat .env

# Check variables are set
python -c "from settings import Settings; print(Settings().get_validation_errors())"
```

### Authentication Failures

**Problem:** "AADSTS700016: Application not found"

**Solution:**

- Verify Tenant ID is correct
- Ensure app registered in same Azure tenant
- Check Client ID matches

**Problem:** "AADSTS530007: Client secret expired"

**Solution:**

- Generate new client secret in Azure Portal
- Update `.env` with new secret
- Restart application

### No Events Returned

**Problem:** Empty recommendations from Graph

**Solution:**

- Check user has calendar events
- Verify `Calendars.Read` permission granted
- Check admin consent was granted
- Review logs: `cat ~/.event_agent.log`

### Rate Limiting

**Problem:** "Rate limited - will retry"

**Solution:**

- Normal for high-frequency requests
- Automatic retry with exponential backoff
- Graph API limit: 10,000 requests per 10 minutes

## Security Best Practices

### Credential Management

1. ✅ Use environment variables (never hardcode)
2. ✅ Add `.env` to `.gitignore`
3. ✅ Rotate secrets regularly in Azure Portal
4. ✅ Use Azure Key Vault for production
5. ✅ Grant minimum required permissions

### Token Security

- Tokens cached in `~/.event_agent_token_cache.json`
- Auto-refresh before expiration (5-minute buffer)
- Tokens never logged
- Cache file permissions: user-readable only

### Production Deployment

- Use HTTPS only
- Add authentication: set `API_TOKEN` env var
- Enable rate limiting
- Restrict CORS origins
- Monitor API usage

## Advanced Configuration

### Custom Event Transformation

Edit `graph_service.py` to customize how Graph events are transformed:

```python
def _transform_event(self, event_data: dict) -> dict:
    # Your custom transformation logic
    pass
```

### Custom Scoring Weights

Modify `core.py` to adjust recommendation scoring:

```python
weights = {
    "interest": 2.5,      # Interest match importance
    "popularity": 0.7,    # Event popularity weight
    "diversity": 0.4      # Interest diversity
}
```

### Logging

Control logging via environment:

```bash
LOG_LEVEL=DEBUG           # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=~/.event_agent.log
```

## Performance

### Caching

- Events cached for 5 minutes (default)
- Configurable: `GraphEventService(cache_ttl=300)`
- Manual cache clear available

### Rate Limiting

- Automatic retry on 429 responses
- Exponential backoff
- Logs rate limit encounters

### Batch Operations

For multiple users:

- Use background job system
- Implement batch endpoint
- Add queue-based processing

## Next Steps

- 📖 [Architecture Guide](architecture.md) — How Graph integration works
- 🆘 [Troubleshooting](troubleshooting.md) — Common issues
- 🔐 [Security Guide](../05-PRODUCTION/security.md) — Production security
- 📊 [Performance Guide](../05-PRODUCTION/performance.md) — Optimization tips

## Support

For issues:

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Review logs: `tail -f ~/.event_agent.log`
3. Enable debug: `LOG_LEVEL=DEBUG python agent.py ...`
4. Check [Graph API Status](https://docs.microsoft.com/graph/api/overview)
