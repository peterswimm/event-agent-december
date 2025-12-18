# Microsoft Graph Integration Setup Guide

This guide walks through setting up and using Microsoft Graph API integration for event recommendations in the Event Agent ADK.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Azure AD Application Setup](#azure-ad-application-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [HTTP API](#http-api)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

## Overview

The Event Agent now supports Microsoft Graph API for fetching calendar events from Exchange Online. This enables:

- **Real calendar integration**: Fetch actual calendar events instead of relying on static manifests
- **User-specific recommendations**: Filter events by user interests and availability
- **Dynamic event scoring**: Score events based on real popularity and attendee counts
- **Dual-mode support**: Run with either manifest-based or Graph-based recommendations

## Prerequisites

### Required Packages

All dependencies are included in `pyproject.toml`. Install with:

```bash
pip install -e ".[dev]"
```

Key packages:
- `msal` (1.25.0+): Microsoft Authentication Library
- `msgraph-core` (1.0.0+): Microsoft Graph API client
- `pydantic-settings` (2.0.0+): Configuration management
- `azure-identity` (1.14.0+): Azure authentication utilities

### Azure Requirements

You need:
1. An Azure subscription
2. Access to Azure Active Directory
3. Permissions to register applications

## Azure AD Application Setup

### Step 1: Register an Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **+ New registration**
4. Fill in the details:
   - **Name**: "Event Agent"
   - **Supported account types**: "Accounts in this organizational directory only"
   - **Redirect URI**: Leave blank (not needed for daemon app)
5. Click **Register**

### Step 2: Create a Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **+ New client secret**
3. Add a description and expiration
4. Click **Add**
5. **Copy the secret value** (you won't see it again)

### Step 3: Grant API Permissions

1. In your app registration, go to **API permissions**
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Choose **Application permissions** (not Delegated)
5. Search for and select:
   - `Calendars.Read`
   - `User.Read`
6. Click **Add permissions**
7. Click **Grant admin consent for [Org Name]**

### Step 4: Collect Application Information

From your app registration overview page, collect:
- **Tenant ID**: Listed as "Directory (tenant) ID"
- **Client ID**: Listed as "Application (client) ID"
- **Client Secret**: Created in Step 2

## Configuration

### Step 1: Set Environment Variables

Create or update `.env` file in the project root:

```bash
# Microsoft Graph Configuration
GRAPH_TENANT_ID=your-tenant-id
GRAPH_CLIENT_ID=your-client-id
GRAPH_CLIENT_SECRET=your-client-secret

# Optional: Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=~/.event_agent.log
```

**Security Note**: Never commit `.env` files to version control. Add to `.gitignore`:

```bash
.env
.env.local
~/.event_agent_token_cache.json
```

### Step 2: Verify Configuration

Test your configuration with:

```bash
# Check settings are loaded correctly
python -c "from settings import Settings; s = Settings(); print('Graph ready:', s.validate_graph_ready())"
```

If not ready, get validation errors:

```bash
python -c "from settings import Settings; s = Settings(); print(s.get_validation_errors())"
```

## Usage

### CLI: Manifest Mode (Default)

Existing CLI commands continue to work unchanged:

```bash
# Recommend sessions for interests
python agent.py recommend --interests "ai safety, agents" --top 3

# Explain a specific session
python agent.py explain --session "Session Title" --interests "ai safety"

# Export itinerary
python agent.py export --interests "ai safety" --output itinerary.md
```

### CLI: Graph Mode

To use Graph API instead of manifest:

```bash
# Get recommendations from Graph
python agent.py recommend --source graph --interests "ai safety, agents" --top 3

# With user tracking
python agent.py recommend --source graph --user-id user@company.com --interests "ai" --top 5

# Export from Graph results
python agent.py export --interests "ai safety" --output itinerary.md
```

### Profiles in Graph Mode

Save and load user profiles:

```bash
# Save user's interests
python agent.py recommend --source graph --interests "ai, safety, agents" \
  --profile-save john_profile --user-id john@company.com

# Load saved profile
python agent.py recommend --source graph --profile-load john_profile --top 5
```

## HTTP API

### GET /recommend-graph

Get recommendations from Microsoft Graph events.

**Query Parameters:**
- `interests` (required): Comma-separated interests (e.g., "ai safety,agents")
- `top` (optional): Number of sessions to return (default from manifest)
- `userId` (optional): User ID for tracking in telemetry
- `card` (optional): "1" to include Adaptive Card format

**Example:**

```bash
curl "http://localhost:8000/recommend-graph?interests=ai+safety&top=3&userId=user%40company.com"
```

**Response (200 OK):**

```json
{
  "source": "graph",
  "sessions": [
    {
      "title": "Event Title",
      "start": "09:00",
      "end": "09:40",
      "location": "Hall A",
      "tags": ["ai", "safety"],
      "popularity": 0.85,
      "score": 4.23,
      "contributions": {
        "interest_match": 2.0,
        "popularity": 0.425,
        "diversity": 0.805
      }
    }
  ],
  "conflicts": 0,
  "scoring": {...},
  "userId": "user@company.com"
}
```

**Error Responses:**

- `400 Bad Request`: Missing required parameters
- `502 Bad Gateway`: Graph credentials not configured or API error
- `503 Service Unavailable`: Graph API support not available

### Starting HTTP Server

```bash
# Start server with Graph support enabled
python agent.py serve --port 8000

# With Adaptive Card support
python agent.py serve --port 8000 --card
```

Server output:

```
[serve] listening on port 8000 (endpoints: /recommend /recommend-graph /explain /health /export)
```

## Troubleshooting

### Configuration Issues

**Problem**: "Graph credentials not configured"

**Solution**: Verify .env file:

```bash
# Check env file exists
cat .env

# Verify all three variables are set
echo $GRAPH_TENANT_ID
echo $GRAPH_CLIENT_ID
echo $GRAPH_CLIENT_SECRET
```

### Authentication Failures

**Problem**: "AADSTS700016: Application not found in directory"

**Solution**: 
- Verify Tenant ID is correct
- Ensure app is registered in the same Azure tenant
- Check Application ID matches

**Problem**: "AADSTS530007: Client secret has expired or is invalid"

**Solution**:
- Generate a new client secret in Azure Portal
- Update `.env` file with new secret
- Restart the application

### Event Fetching Issues

**Problem**: "No events returned" or empty recommendations

**Solution**:
- Check user has calendar events for current date range
- Verify user has shared calendar with the application
- Check API permissions in Azure Portal (Calendars.Read required)
- Review logs: `cat ~/.event_agent.log`

**Problem**: "Rate limited - will retry"

**Solution**:
- Normal for high-frequency requests
- Automatic retry after specified seconds
- Consider caching or batch requests
- Graph API standard limits: 10,000 requests per 10 minutes

### Token Caching Issues

**Problem**: "Failed to load token cache"

**Solution**:
- Token cache file: `~/.event_agent_token_cache.json`
- Check file permissions
- Delete and regenerate: `rm ~/.event_agent_token_cache.json`
- Token auto-refreshes before expiration (5-minute buffer)

## Security Considerations

### Client Secret Management

1. **Never commit secrets** to version control
2. **Use environment variables**, not hardcoded values
3. **Rotate secrets regularly** in Azure Portal
4. **Use Azure Key Vault** for production deployments
5. **Restrict secret to required scopes** (Calendar.Read only)

### API Permissions

1. **Principle of Least Privilege**: Only grant necessary permissions
2. **Use Application Permissions** (not Delegated) for daemon apps
3. **Regularly audit** granted permissions
4. **Revoke unused** permissions

### Token Security

1. **Automatic caching** with 5-minute expiration buffer
2. **Tokens never logged** (checked in debug output)
3. **Cache file permissions** set to user-readable only
4. **Automatic cleanup** on authentication errors

### Network Security

1. **HTTPS only** for production APIs
2. **Add authentication** to HTTP server: `API_TOKEN=token` env var
3. **Rate limiting** enabled by default
4. **Input validation** on all endpoints
5. **CORS headers** restricted: `Access-Control-Allow-Origin: *`

For production, replace with explicit origin list.

### Testing with Graph

```bash
# Dry run without actual Graph calls
python agent.py recommend --source graph --interests "test" --help

# Enable debug logging
LOG_LEVEL=DEBUG python agent.py recommend --source graph --interests "ai"

# Check logs
tail -f ~/.event_agent.log
```

## Performance Optimization

### Caching

- Events cached for 5 minutes by default
- Configurable via GraphEventService(cache_ttl=seconds)
- Manual cache clear available

### Rate Limiting

- Automatic retry on 429 (Rate Limited) responses
- Exponential backoff implemented
- Logs rate limit encounters for monitoring

### Batch Operations

For multiple users, consider:
- Using a background job system
- Implementing batch recommendation endpoint
- Adding queue-based processing

## Advanced Configuration

### Custom Event Transformation

Edit `graph_service.py` `_transform_event()` method to customize how Graph events are transformed to the agent schema.

### Custom Scoring Weights

Modify scoring in `core.py` `recommend_from_graph()`:

```python
weights = {
    "interest": 2.5,      # Interest match importance
    "popularity": 0.7,    # Event popularity
    "diversity": 0.4      # Interest diversity
}
result = recommend_from_graph(service, interests, top, weights=weights)
```

### Logging Configuration

Control logging via environment variables:

```bash
LOG_LEVEL=DEBUG           # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=~/.event_agent.log  # Optional file output
```

Or programmatically:

```python
from logging_config import setup_logging
setup_logging(log_level="DEBUG", log_file="app.log")
```

## Next Steps

1. [Run integration tests](../docs/technical-guide.md)
2. [Monitor with telemetry](../docs/performance-guide.md)
3. [Deploy to production](../docs/application-patterns.md)
4. [Check troubleshooting guide](../docs/troubleshooting.md)

## Support

For issues or questions:
1. Check [troubleshooting.md](troubleshooting.md)
2. Review application logs: `tail -f ~/.event_agent.log`
3. Check Graph API status: https://docs.microsoft.com/graph/api/overview
4. Enable debug logging: `LOG_LEVEL=DEBUG`
