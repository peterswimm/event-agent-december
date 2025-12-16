# Configuration Guide

Event Kit is configured via environment variables and the `agent.json` manifest. This guide covers both.

## Quick Config (0 Configuration)

Event Kit works **out of the box** with sample data. No configuration needed to get started!

```bash
python agent.py recommend --interests "agents" --top 3
```

## Environment Configuration

For advanced features (Graph API, custom ports, Adaptive Cards), create a `.env` file:

### 1. Create `.env` File

```bash
# Copy the template
cp .env.example .env

# Edit with your values
nano .env  # or your favorite editor
```

### 2. Configuration Options

#### Manifest Mode (Default)

```env
# Listening port for HTTP server
PORT=8080

# Enable Adaptive Cards in HTTP responses
INCLUDE_CARD=true

# Feature flags
# (See agent.json "features" section for more)
```

#### Graph API Mode (Optional)

To use your actual calendar events:

```env
# Azure AD credentials (get from Azure Portal)
GRAPH_TENANT_ID=your-tenant-id
GRAPH_CLIENT_ID=your-client-id
GRAPH_CLIENT_SECRET=your-client-secret

# Optional: User ID for Graph queries (can override with --user-id flag)
# GRAPH_USER_ID=user@company.com
```

#### SharePoint Mode (Optional)

To publish itineraries to SharePoint:

```env
# Requires Graph credentials (above) plus:
INTERESTS=AI;agents
MAX_SESSIONS=3
PUBLISH=true
```

### 3. Load Configuration

#### Option A: Set Environment Variables (Temporary)

```bash
# Windows (Command Prompt)
set GRAPH_TENANT_ID=your-tenant-id
set GRAPH_CLIENT_ID=your-client-id
set GRAPH_CLIENT_SECRET=your-client-secret

# macOS/Linux (Bash)
export GRAPH_TENANT_ID=your-tenant-id
export GRAPH_CLIENT_ID=your-client-id
export GRAPH_CLIENT_SECRET=your-client-secret
```

#### Option B: Load from .env File (Persistent)

```bash
# Load all .env variables
# On macOS/Linux:
export $(grep -v '^#' .env | xargs)

# On Windows (PowerShell):
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}
```

#### Option C: Use python-dotenv (Automatic)

Event Kit automatically loads `.env` using `python-dotenv`. Just create the file and run:

```bash
python agent.py recommend --interests "agents" --top 3
```

## Manifest Configuration

The `agent.json` file defines sessions, weights, and features:

```json
{
  "name": "Event Kit",
  "description": "Minimal event recommendation agent",
  "sessions": [
    {
      "id": "session-1",
      "title": "Generative Agents in Production",
      "topics": ["agents", "gen ai", "production"]
    }
  ],
  "weights": {
    "interests": 0.5,
    "topics": 0.3,
    "recency": 0.2
  },
  "features": {
    "telemetry": true,
    "export": true,
    "externalSessions": true
  }
}
```

### Adjusting Weights

Edit the `weights` section to change recommendation scoring:

```json
"weights": {
  "interests": 0.6,   // Higher = prioritize user interests
  "topics": 0.3,      // Medium = consider session topics
  "recency": 0.1      // Lower = ignore event recency
}
```

Then rerun — no code changes needed!

### Feature Flags

Enable/disable features in the `features` section:

| Flag | Purpose | Default |
|------|---------|---------|
| `telemetry` | Log recommendations to `telemetry.jsonl` | `true` |
| `export` | Enable `/export` endpoint | `true` |
| `externalSessions` | Load sessions from external file | `false` |

## Advanced: External Sessions

Load session data from an external JSON file:

### 1. Create Sessions File

Create `sessions_external.json`:

```json
{
  "sessions": [
    {
      "id": "external-1",
      "title": "Custom Event",
      "topics": ["custom", "topics"]
    }
  ]
}
```

### 2. Enable in .env

```env
EXTERNAL_SESSIONS_FILE=sessions_external.json
```

Or enable feature flag in `agent.json`:

```json
"features": {
  "externalSessions": true
}
```

### 3. Use Custom Sessions

```bash
python agent.py recommend --interests "custom" --top 3
```

## Profiles

User profiles are stored locally in `~/.event_agent_profiles.json`:

```bash
# Save profile
python agent.py recommend --interests "agents" --profile-save user1

# Load profile
python agent.py recommend --profile-load user1

# List profiles (view ~/.event_agent_profiles.json)
cat ~/.event_agent_profiles.json
```

## Troubleshooting Configuration

### "Configuration error: GRAPH_TENANT_ID not found"

Ensure your `.env` file exists and contains:
```env
GRAPH_TENANT_ID=your-value
GRAPH_CLIENT_ID=your-value
GRAPH_CLIENT_SECRET=your-value
```

### "PORT already in use"

Change the port:
```env
PORT=8081
```

Or specify via CLI:
```bash
python agent.py serve --port 8081
```

### ".env not loading"

Manually load it:
```bash
# Bash/zsh:
source .env

# Or Python:
python -m dotenv
```

### "validate_graph_ready() = False"

This is OK! It means Graph credentials aren't set. For sample data, this is normal. To enable Graph, see [Graph API Setup](../03-GRAPH-API/setup.md).

## Next Steps

- 🚀 Ready to run? See [Quick Start](quick-start.md)
- 📅 Want to use your calendar? See [Graph API Setup](../03-GRAPH-API/setup.md)
- ⚙️ Need more options? See [Command Reference](../REFERENCE.md)
- 🔧 Stuck? See [Troubleshooting](../03-GRAPH-API/troubleshooting.md)
