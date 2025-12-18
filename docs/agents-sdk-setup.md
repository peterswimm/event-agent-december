# Event Kit Agent - SDK Integration Guide

**Status**: Phase 3 - Agents SDK Integration
**Last Updated**: December 18, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Setup Steps](#setup-steps)
5. [Bot Framework Configuration](#bot-framework-configuration)
6. [Teams Deployment](#teams-deployment)
7. [Copilot Integration](#copilot-integration)
8. [Local Testing](#local-testing)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

---

## Overview

Event Kit now supports hosting via Microsoft 365 Agents SDK and Bot Framework, enabling deployment to:
- **Microsoft Teams** - Bot in channels and direct messages
- **Copilot Studio** - Custom Copilot with EventKit capabilities
- **Outlook** - Agent availability in Outlook email

### Components

| Component | File | Purpose |
|-----------|------|---------|
| Unified Adapters | `adapters/` | Flexible integration framework for multiple platforms |
| - Base Adapter | `adapters/base_adapter.py` | Abstract base with shared tool registration and error handling |
| - Foundry Adapter | `adapters/foundry_adapter.py` | Azure AI Foundry and Agent Framework integration |
| - Bot Adapter | `adapters/bot_adapter.py` | Bot Framework, Teams, and Adaptive Card generation |
| Legacy Adapter | `agent_framework_adapter.py` | Backward compatibility wrapper (uses FoundryAdapter) |
| Bot Handler | `bot_handler.py` | Teams Bot Framework activity processing |
| Manifest | `agent-declaration.json` | Agent capabilities definition |
| Teams Manifest | `teams-app.json` | Teams bot registration |

> **Note**: The unified adapter architecture (see [UNIFIED_ADAPTER_ARCHITECTURE.md](UNIFIED_ADAPTER_ARCHITECTURE.md)) provides a consistent pattern for integrating with Azure AI Foundry, Power Platform, and Bot Framework while reducing code duplication by 24%.

---

## Architecture

```mermaid
┌─────────────────────┐
│   Teams/Outlook     │
│   Copilot Studio    │
└──────────┬──────────┘
           │ HTTP
┌──────────▼──────────┐
│   Bot Framework     │
│   (bot_handler)     │
└──────────┬──────────┘
           │ Tool Calls
┌──────────▼──────────────────────┐
│   Unified Adapters Framework     │
│   (adapters/base_adapter.py)     │
│   ├─ foundry_adapter.py          │
│   ├─ bot_adapter.py               │
│   └─ power_adapter.py            │
└──────────┬──────────────────────┘
           │ Functions
┌──────────▼────────────────────────────┐
│   Event Kit Core Functions            │
│   - recommend()                        │
│   - explain()                          │
│   - Graph API integration              │
└────────────────────────────────────────┘
```

---

## Prerequisites

### Required

- **Python 3.11+** - Event Kit base requirement
- **Azure Subscription** - For Bot Service and Azure Ad registration
- **Azure CLI** - For deployment automation
- **Bot Framework SDK** - `pip install botbuilder-core botbuilder-integration-aiohttp`
- **Microsoft 365 Agents SDK** - `pip install azure-ai-projects`

### Optional

- **Bot Emulator** - Local testing of Teams bots
- **Copilot Studio** - For custom Copilot creation
- **Teams Toolkit for VS Code** - Teams development extension

### Environment Variables

Create `.env` with these required values:

```bash
# Bot Configuration
BOT_ID=your-bot-app-id-here
BOT_PASSWORD=your-bot-app-password-here
BOT_ENDPOINT=https://your-domain.azurewebsites.net/api/messages

# Azure AI Projects
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string
AZURE_AI_PROJECT_NAME=your-project-name

# Graph API (optional, for Graph-based recommendations)
GRAPH_TENANT_ID=your-tenant-id
GRAPH_CLIENT_ID=your-client-id
GRAPH_CLIENT_SECRET=your-client-secret

# Application Insights (optional)
APP_INSIGHTS_CONNECTION_STRING=your-connection-string
```

---

## Setup Steps

### Step 1: Install Dependencies

```bash
# Install SDK dependencies
pip install -r requirements.txt

# Install optional Bot Framework packages
pip install botbuilder-core botbuilder-integration-aiohttp azure-ai-projects
```

### Step 2: Register Bot Service in Azure

```bash
# Using Azure CLI
az bot create \
  --name EventKitAgent \
  --resource-group <your-rg> \
  --kind registration \
  --display-name "Event Kit Agent" \
  --endpoint https://your-domain.azurewebsites.net/api/messages
```

This generates:
- **Bot ID** (Application ID)
- **Bot Password** (save securely)

Add these to `.env`:

```bash
BOT_ID=<your-bot-id>
BOT_PASSWORD=<your-bot-password>
```

### Step 3: Register Azure AD Application

For Teams/Copilot integration, register an Azure AD app:

```bash
# Using Azure Portal or Azure CLI
az ad app create \
  --display-name "EventKit Agent" \
  --reply-urls "https://your-domain.azurewebsites.net/auth/callback"
```

### Step 4: Update Configuration Files

#### agent-declaration.json
The manifest is already configured with 3 capabilities:
- `recommend_sessions` - Get recommendations
- `explain_session` - Explain why sessions match
- `export_itinerary` - Export personalized itinerary

**No changes needed** - it's production-ready!

#### teams-app.json
Update with your bot ID and domain:

```json
{
  "id": "YOUR-BOT-ID-HERE",
  "bots": [{
    "botId": "YOUR-BOT-ID-HERE"
  }],
  "validDomains": ["your-domain.azurewebsites.net"],
  "webApplicationInfo": {
    "id": "YOUR-BOT-ID-HERE",
    "resource": "api://your-domain.azurewebsites.net/YOUR-BOT-ID-HERE"
  }
}
```

### Step 5: Create Bot Handler Server

Create `bot_server.py`:

```python
#!/usr/bin/env python3
"""
Bot Framework Server for Event Kit Agent

Hosts the bot using aiohttp and handles Teams activities.
"""

import os
import asyncio
import logging
from aiohttp import web
from botbuilder.core import (
    ConversationState,
    MemoryStorage,
    UserState,
)
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication

from bot_handler import EventKitBotHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize storage
memory = MemoryStorage()
conversation_state = ConversationState(memory)
user_state = UserState(memory)

# Initialize bot handler
bot = EventKitBotHandler(
    conversation_state=conversation_state,
    user_state=user_state
)


async def messages(req: web.Request) -> web.Response:
    """Handle incoming Bot Framework activities."""
    body = await req.json()
    auth_header = req.headers.get("Authorization", "")

    response = await adapter.process_activity(auth_header, body, bot.on_turn)

    if response:
        return web.json_response(data=response.body)
    else:
        return web.Response(status=201)


async def create_app():
    """Create and configure aiohttp application."""
    global adapter

    # Create adapter
    auth = ConfigurationBotFrameworkAuthentication()
    adapter = CloudAdapter(auth)

    app = web.Application()

    # Add error handling
    async def handle_error(request, error):
        logger.exception(f"Request failed: {error}")
        return web.json_response(
            {"error": "Internal server error"},
            status=500
        )

    app.middlewares.append(handle_error)

    # Routes
    app.router.add_post("/api/messages", messages)
    app.router.add_get("/health", lambda r: web.json_response({"status": "ok"}))

    return app


if __name__ == "__main__":
    PORT = int(os.getenv("PORT", "3978"))

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(create_app())

    web.run_app(app, host="0.0.0.0", port=PORT)
```

---

## Bot Framework Configuration

### Activity Handlers

The `bot_handler.py` implements these activity handlers:

| Handler | Event | Purpose |
|---------|-------|---------|
| `on_message_activity` | Message received | Process user queries |
| `on_message_reaction_activity` | Reaction added | Track user reactions |
| `on_members_added_activity` | Member joins | Send welcome message |
| `on_members_removed_activity` | Member leaves | Clean up state |

### Command Processing

Commands are parsed from messages:

```
Format: @bot <command> <args> --option value

Examples:
- @bot recommend agents, ai safety --top 5
- @bot explain "Session Title" --interests agents
- @bot export agents --profile my_profile
- @bot help
```

---

## Teams Deployment

### 1. Package the App

```bash
# Zip the Teams manifest
zip eventkit-teams.zip \
  teams-app.json \
  assets/outline-icon-192.png \
  assets/color-icon-192.png
```

### 2. Deploy to Azure App Service

```bash
# Build and push Docker image
docker build -t eventkit:latest .
docker tag eventkit:latest <registry>.azurecr.io/eventkit:latest
docker push <registry>.azurecr.io/eventkit:latest

# Update App Service
az webapp config container set \
  --name eventkit-agent \
  --resource-group <your-rg> \
  --docker-custom-image-name <registry>.azurecr.io/eventkit:latest \
  --docker-registry-server-url https://<registry>.azurecr.io
```

### 3. Add App to Teams

**In Teams Admin Center:**
1. Go to **Teams apps** → **Manage apps**
2. Click **Upload a custom app**
3. Select `eventkit-teams.zip`
4. Configure permissions and policies
5. Assign to users/teams

**In Teams Client:**
1. Click **...** (More) → **Find an app**
2. Search for "Event Kit Agent"
3. Click **Add** to install

### 4. Test in Teams

**Personal Chat:**
```
@Event Kit Agent recommend agents, machine learning
```

**Team Channel:**
```
@Event Kit Agent help
```

---

## Copilot Integration

### 1. Create in Copilot Studio

1. Go to [Copilot Studio](https://copilotstudio.microsoft.com)
2. Click **Create** → **New agent**
3. Select **From blank**
4. Configure:
   - **Name**: "Event Kit Copilot"
   - **Description**: "Event session recommendations"

### 2. Add Knowledge

1. Click **Knowledge**
2. Select **Upload files**
3. Upload `agent.json` (sessions manifest)

### 3. Add Actions

In **Actions**:

```yaml
Name: Get Session Recommendations
URL: https://your-domain.azurewebsites.net/api/recommend
Method: POST
Parameters:
  - interests: string (required)
  - top: integer (default: 5)
```

### 4. Test

1. Click **Test**
2. Try: "Recommend sessions about agents and AI safety"
3. Verify responses

### 5. Publish

1. Click **Publish**
2. Configure availability (Teams, Teams Chat, Web)
3. Share access link

---

## Local Testing

### Option 1: Using Bot Emulator

**Install Bot Emulator:**
```bash
# Download from https://github.com/Microsoft/BotFramework-Emulator/releases
```

**Configure:**
1. Open Bot Emulator
2. Click **Open Bot** in the welcome tab
3. Set bot URL to `http://localhost:3978/api/messages`
4. Leave App ID and Password empty for local testing

**Test:**
```
User: recommend agents, ai safety
Bot: [Recommendations response]
```

### Option 2: Direct HTTP

```bash
# Start bot server
python bot_server.py

# Test in another terminal
curl -X POST http://localhost:3978/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "text": "recommend agents",
    "from": {"id": "user1", "name": "Test User"},
    "recipient": {"id": "bot", "name": "EventKit"},
    "id": "msg1"
  }'
```

### Option 3: Using ngrok for Tunneling

```bash
# Install ngrok: https://ngrok.com/download

# Start bot server
python bot_server.py &

# Start ngrok tunnel
ngrok http 3978

# Copy ngrok URL (e.g., https://abc-123-def.ngrok.io)
# Use in Bot Service endpoint configuration
```

---

## Troubleshooting

### Bot Not Responding

**Symptoms**: No response to messages in Teams

**Diagnosis**:
```bash
# Check bot server is running
curl http://localhost:3978/health

# Check logs
tail -f logs/bot-handler.log

# Verify Bot ID and Password
echo "Bot ID: $BOT_ID"
echo "Bot Password set: $([ -n "$BOT_PASSWORD" ] && echo "YES" || echo "NO")"
```

**Solutions**:
1. Verify `BOT_ID` and `BOT_PASSWORD` in `.env`
2. Ensure bot endpoint is accessible externally
3. Check firewall rules allow Teams traffic
4. Restart bot service

### Message Parsing Errors

**Symptoms**: "Unknown command" or "Invalid parameters"

**Examples**:
```
@bot recommend  # Missing interests → Error
@bot explain session --interests  # Missing interests → Error
```

**Solutions**:
- Use format: `@bot <command> [args] --option value`
- Comma-separate interests: `agents, ai safety`
- Quote session titles: `"Session Title"`

### Graph API Integration Issues

**Symptoms**: Graph recommendations fail, but manifest recommendations work

**Solutions**:
1. Verify Graph credentials in `.env`
2. Check Azure AD app permissions:
   - Calendars.Read (delegated)
   - User.Read (delegated)
3. Ensure user has granted consent

```bash
# Test Graph connectivity
python -c "from graph_service import GraphEventService; print('OK')"
```

### Teams App Installation Issues

**Symptoms**: "This app cannot be loaded" or "App failed to load"

**Solutions**:
1. Validate `teams-app.json` schema
2. Check all bot IDs match across files
3. Verify domain is accessible
4. Ensure HTTPS (Teams requires secure connections)

```bash
# Validate manifest
az teams app validate -m teams-app.json -p eventkit-teams.zip
```

### Performance Issues

**Symptoms**: Slow recommendations, timeouts

**Diagnosis**:
```bash
# Check response times
python -c "
import time
from agents_sdk_adapter import EventKitAgent
agent = EventKitAgent()
start = time.time()
result = agent.handle_tool_call('recommend_sessions', {'interests': 'test', 'top': 3})
print(f'Response time: {time.time() - start:.2f}s')
"
```

**Solutions**:
1. Reduce session manifest size (limit to <1000 sessions)
2. Enable caching in GraphEventService
3. Increase rate limits if needed
4. Scale App Service to higher tier

---

## API Reference

### EventKitAgent Class

```python
from agents_sdk_adapter import EventKitAgent

agent = EventKitAgent()
```

#### Methods

##### `handle_tool_call(tool_name: str, parameters: dict) → dict`

Execute a tool with given parameters.

**Parameters**:
- `tool_name`: "recommend_sessions" | "explain_session" | "export_itinerary"
- `parameters`: Tool-specific parameters

**Returns**: Tool result dictionary

**Example**:
```python
result = agent.handle_tool_call("recommend_sessions", {
    "interests": "agents, ai safety",
    "top": 5,
    "correlation_id": "msg-123"
})
```

##### `get_capabilities() → list`

Get list of available agent capabilities.

**Returns**: List of capability definitions

**Example**:
```python
capabilities = agent.get_capabilities()
# [
#   {"name": "recommend_sessions", "description": "...", "parameters": [...]},
#   {"name": "explain_session", "description": "...", "parameters": [...]},
#   ...
# ]
```

---

### EventKitBotHandler Class

```python
from bot_handler import EventKitBotHandler

handler = EventKitBotHandler()
```

#### Methods

##### `async on_message_activity(turn_context) → None`

Process incoming message activity.

**Parameters**:
- `turn_context`: Bot Framework TurnContext

**Supported Commands**:
- `recommend` - Get recommendations
- `explain` - Explain a session
- `export` - Export itinerary
- `help` - Show help

---

## Integration Examples

### Example 1: Custom Recommendation Flow

```python
from agents_sdk_adapter import EventKitAgent

agent = EventKitAgent()

# Get recommendations
result = agent.handle_tool_call("recommend_sessions", {
    "interests": "agents, machine learning, responsible ai",
    "top": 5,
    "use_graph": True  # Use Graph API if available
})

# Use results
for session in result["sessions"]:
    print(f"Title: {session['title']}")
    print(f"Score: {session['score']:.2f}")
    print(f"Matched: {', '.join(session['matched_interests'])}")
    print()
```

### Example 2: Teams Message Handler

```python
from bot_handler import EventKitBotHandler

handler = EventKitBotHandler()

async def process_user_message(text):
    # Parse and handle
    command, params = handler._parse_message(text)

    if command == "recommend":
        # Get recommendations
        result = handler.agent.handle_tool_call(
            "recommend_sessions",
            params
        )
        return result["markdown"]
```

---

## Next Steps

1. **Deploy to Azure** - Use Bicep templates in `infra/`
2. **Enable Graph Integration** - Configure Graph credentials for calendar-based recommendations
3. **Add Copilot Extensions** - Extend with SharePoint, OneDrive integration
4. **Custom Actions** - Add domain-specific session sources
5. **Analytics** - Monitor usage via Application Insights

---

## Support

**Issues**: [GitHub Issues](https://github.com/peterswimm/event-agent-december/issues)
**Documentation**: [Complete Docs](https://github.com/peterswimm/event-agent-december/tree/main/docs)
**Teams Samples**: [Microsoft Teams Samples](https://github.com/OfficeDev/Microsoft-Teams-Samples)
