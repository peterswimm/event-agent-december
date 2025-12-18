# EventKit Extensibility Guide

This guide covers extending EventKit with Microsoft 365, Power Platform, Azure Functions, and declarative agents.

---

## 📋 Table of Contents

- [Power Platform Connectors](#power-platform-connectors)
- [Azure Functions](#azure-functions)
- [Declarative Agent Skills](#declarative-agent-skills)
- [Adaptive Cards](#adaptive-cards)
- [Bot Framework WebChat](#bot-framework-webchat)
- [Microsoft 365 Knowledge Connectors](#microsoft-365-knowledge-connectors)

---

## 🔌 Power Platform Connectors

### Overview

Power Platform Custom Connectors allow EventKit to be used in Power Automate flows, Power Apps, and Logic Apps.

### Create Custom Connector

**1. Export OpenAPI Spec**

EventKit already exposes HTTP endpoints. Create OpenAPI spec:

```yaml
# openapi-connector.yaml
openapi: 3.0.0
info:
  title: EventKit Connector
  description: Get personalized conference session recommendations
  version: 1.0.0
servers:
  - url: https://eventkit.azurewebsites.net
paths:
  /recommend:
    get:
      operationId: GetRecommendations
      summary: Get session recommendations
      parameters:
        - name: interests
          in: query
          required: true
          schema:
            type: string
          description: Comma-separated interests (e.g., "ai,agents")
        - name: top
          in: query
          schema:
            type: integer
            default: 3
          description: Number of recommendations
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  sessions:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        title:
                          type: string
                        topics:
                          type: array
                          items:
                            type: string
                        score:
                          type: number
  /explain:
    get:
      operationId: ExplainSession
      summary: Explain why session matches interests
      parameters:
        - name: session
          in: query
          required: true
          schema:
            type: string
        - name: interests
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success
```

**2. Import to Power Platform**

1. Go to [Power Automate](https://make.powerautomate.com)
2. Navigate to **Data** → **Custom Connectors** → **+ New custom connector** → **Import an OpenAPI file**
3. Upload `openapi-connector.yaml`
4. Configure authentication (if needed - API Key or OAuth2)
5. Test the connector
6. Create connection

**3. Use in Power Automate**

```json
{
  "type": "ApiConnection",
  "inputs": {
    "host": {
      "connection": {
        "name": "@parameters('$connections')['eventkit']['connectionId']"
      }
    },
    "method": "get",
    "path": "/recommend",
    "queries": {
      "interests": "@{triggerBody()?['interests']}",
      "top": 3
    }
  }
}
```

**4. Use in Power Apps**

```javascript
// Add data source: EventKit Connector
// Use in app:
ClearCollect(
    Sessions,
    EventKitConnector.GetRecommendations(
        {interests: "ai,agents,production", top: 5}
    ).sessions
);

// Display in gallery
Gallery1.Items = Sessions
```

### Best Practices

- **Rate Limiting**: Add Azure API Management for throttling
- **Caching**: Cache recommendations for 5-10 minutes
- **Error Handling**: Return structured error responses
- **Authentication**: Use API keys or OAuth2 via Azure AD

---

## ⚡ Azure Functions

### Overview

Deploy EventKit as serverless Azure Functions for auto-scaling and pay-per-use.

### Setup

**1. Create Function App**

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Create function project
func init eventkit-functions --python
cd eventkit-functions

# Create HTTP trigger function
func new --name RecommendFunction --template "HTTP trigger" --authlevel "function"
```

**2. Implement Function**

Create `function_app.py`:

```python
import azure.functions as func
import json
import logging
from core import recommend, load_manifest
from settings import Settings

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="recommend")
def recommend_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Get session recommendations via Azure Function."""
    logging.info('EventKit recommend function triggered')

    try:
        # Parse request
        interests = req.params.get('interests', '')
        top = int(req.params.get('top', 3))

        if not interests:
            return func.HttpResponse(
                json.dumps({"error": "interests parameter required"}),
                mimetype="application/json",
                status_code=400
            )

        # Load manifest and recommend
        manifest = load_manifest()
        interests_list = [i.strip() for i in interests.split(',')]
        result = recommend(manifest, interests_list, top)

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error in recommend function: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="explain")
def explain_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Explain session match via Azure Function."""
    logging.info('EventKit explain function triggered')

    try:
        session_title = req.params.get('session', '')
        interests = req.params.get('interests', '')

        if not session_title or not interests:
            return func.HttpResponse(
                json.dumps({"error": "session and interests required"}),
                mimetype="application/json",
                status_code=400
            )

        manifest = load_manifest()
        interests_list = [i.strip() for i in interests.split(',')]
        result = explain(manifest, session_title, interests_list)

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error in explain function: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
```

**3. Deploy to Azure**

```bash
# Login to Azure
az login

# Create resource group
az group create --name eventkit-functions-rg --location eastus

# Create storage account
az storage account create \
    --name eventitkitstorage \
    --resource-group eventkit-functions-rg \
    --location eastus \
    --sku Standard_LRS

# Create function app
az functionapp create \
    --resource-group eventkit-functions-rg \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --name eventkit-functions \
    --storage-account eventitkitstorage \
    --os-type Linux

# Deploy
func azure functionapp publish eventkit-functions
```

**4. Test Functions**

```bash
# Get function URL
FUNCTION_URL=$(az functionapp function show \
    --name eventkit-functions \
    --resource-group eventkit-functions-rg \
    --function-name recommend \
    --query invokeUrlTemplate -o tsv)

# Test with curl
curl "${FUNCTION_URL}?interests=ai,agents&top=3"
```

### Timer-Triggered Functions

For scheduled operations (e.g., publish daily itineraries to SharePoint):

```python
import azure.functions as func
from datetime import datetime

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 8 * * *", arg_name="timer")
def daily_itinerary_publisher(timer: func.TimerRequest) -> None:
    """Publish daily itineraries at 8 AM UTC."""
    logging.info(f'Daily itinerary publisher triggered at {datetime.utcnow()}')

    # Load user profiles from storage
    profiles = load_user_profiles()

    # Generate recommendations for each user
    for profile in profiles:
        recommendations = generate_recommendations(profile)
        publish_to_sharepoint(profile['email'], recommendations)

    logging.info(f'Published itineraries for {len(profiles)} users')
```

---

## 🤖 Declarative Agent Skills

### Overview

Declarative agents in Microsoft 365 Copilot use JSON manifests to define capabilities. EventKit can be exposed as agent skills.

### Agent Manifest

Create `declarative-agent-manifest.json`:

```json
{
  "version": "1.0.0",
  "name": "EventKit Agent",
  "description": "Get personalized conference session recommendations",
  "instructions": "You are an expert at recommending conference sessions based on user interests. When users ask for session recommendations, use the recommend_sessions skill. When they want to understand why a session was recommended, use the explain_session skill.",
  "capabilities": [
    {
      "name": "web_search",
      "enabled": true
    }
  ],
  "actions": [
    {
      "id": "recommend_sessions",
      "description": "Get personalized session recommendations based on user interests",
      "capabilities": {
        "response_semantics": {
          "data_path": "$.sessions",
          "properties": {
            "title": "$.title",
            "subtitle": "$.topics",
            "url": "$.url"
          },
          "static_template": {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.5",
            "$data": "${jsonPath($data, '$.sessions')}",
            "body": [
              {
                "type": "TextBlock",
                "text": "Session Recommendations",
                "weight": "Bolder",
                "size": "Large"
              },
              {
                "type": "Container",
                "$data": "${$data}",
                "items": [
                  {
                    "type": "TextBlock",
                    "text": "${title}",
                    "weight": "Bolder",
                    "wrap": true
                  },
                  {
                    "type": "TextBlock",
                    "text": "Topics: ${join(topics, ', ')}",
                    "isSubtle": true,
                    "wrap": true
                  },
                  {
                    "type": "TextBlock",
                    "text": "Match Score: ${formatNumber(score, 0)}%",
                    "spacing": "Small"
                  }
                ]
              }
            ],
            "actions": [
              {
                "type": "Action.OpenUrl",
                "title": "View Details",
                "url": "${url}"
              }
            ]
          }
        }
      },
      "states": {
        "reasoning": {
          "description": "Analyzing your interests and matching with available sessions..."
        },
        "responding": {
          "description": "Preparing recommendations..."
        }
      }
    },
    {
      "id": "explain_session",
      "description": "Explain why a specific session matches user interests",
      "capabilities": {
        "response_semantics": {
          "data_path": "$",
          "properties": {
            "explanation": "$.explanation"
          }
        }
      }
    }
  ],
  "conversation_starters": [
    {
      "title": "Find AI sessions",
      "text": "What sessions would you recommend about AI and machine learning?"
    },
    {
      "title": "Production systems",
      "text": "Show me sessions about deploying AI in production"
    },
    {
      "title": "Agent development",
      "text": "I want to learn about building AI agents"
    }
  ]
}
```

### OpenAPI Plugin Definition

Create `openapi-plugin.yaml` for the agent:

```yaml
openapi: 3.0.0
info:
  title: EventKit Agent Skills
  version: 1.0.0
servers:
  - url: https://eventkit.azurewebsites.net
paths:
  /recommend:
    get:
      operationId: recommend_sessions
      summary: Get personalized session recommendations
      x-openai-isConsequential: false
      parameters:
        - name: interests
          in: query
          required: true
          schema:
            type: string
          description: Comma-separated interests (e.g., "ai,agents,production")
        - name: top
          in: query
          schema:
            type: integer
            default: 3
          description: Number of recommendations to return
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  sessions:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        title:
                          type: string
                        topics:
                          type: array
                        score:
                          type: number
                        url:
                          type: string
  /explain:
    get:
      operationId: explain_session
      summary: Explain why a session matches interests
      x-openai-isConsequential: false
      parameters:
        - name: session
          in: query
          required: true
          schema:
            type: string
        - name: interests
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  explanation:
                    type: string
```

### Deploy Declarative Agent

1. Package files: `declarative-agent-manifest.json` + `openapi-plugin.yaml`
2. Upload to Microsoft 365 Admin Center → Copilot → Agents
3. Publish to organization or specific users
4. Users can invoke: "Use EventKit to recommend AI sessions"

---

## 🎨 Adaptive Cards

### Overview

EventKit already generates Adaptive Cards. Here's how to extend and customize them.

### Card Templates

**Rich Recommendation Card**:

```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.5",
  "body": [
    {
      "type": "TextBlock",
      "text": "📅 Your Personalized Itinerary",
      "weight": "Bolder",
      "size": "Large",
      "color": "Accent"
    },
    {
      "type": "TextBlock",
      "text": "Based on your interests: AI, Agents, Production",
      "isSubtle": true,
      "wrap": true
    },
    {
      "type": "Container",
      "separator": true,
      "spacing": "Large",
      "items": [
        {
          "type": "ColumnSet",
          "columns": [
            {
              "type": "Column",
              "width": "auto",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "🕒",
                  "size": "Large"
                }
              ]
            },
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "Generative Agents in Production",
                  "weight": "Bolder",
                  "wrap": true
                },
                {
                  "type": "TextBlock",
                  "text": "9:00 AM - 10:30 AM • Hall A",
                  "isSubtle": true,
                  "spacing": "None"
                },
                {
                  "type": "TextBlock",
                  "text": "95% match • Topics: AI, agents, production systems",
                  "size": "Small",
                  "color": "Good",
                  "spacing": "Small"
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "Add to Calendar",
      "url": "https://calendar.eventkit.com/add?session=session-1"
    },
    {
      "type": "Action.Submit",
      "title": "Explain Match",
      "data": {
        "action": "explain",
        "sessionId": "session-1"
      }
    },
    {
      "type": "Action.ShowCard",
      "title": "Session Details",
      "card": {
        "type": "AdaptiveCard",
        "body": [
          {
            "type": "TextBlock",
            "text": "Learn how to deploy AI agents in production environments with reliability, monitoring, and observability.",
            "wrap": true
          }
        ]
      }
    }
  ]
}
```

### Card Designer Integration

Use [Adaptive Cards Designer](https://adaptivecards.io/designer/) to:

1. Design cards visually
2. Test with sample data
3. Export JSON
4. Integrate into EventKit

### Dynamic Card Generation

Extend `agent.py` with richer cards:

```python
def _build_advanced_card(sessions: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate advanced Adaptive Card with user context."""
    body = [
        {
            "type": "TextBlock",
            "text": f"📅 Itinerary for {profile.get('name', 'You')}",
            "weight": "Bolder",
            "size": "Large",
            "color": "Accent"
        },
        {
            "type": "TextBlock",
            "text": f"Based on interests: {', '.join(profile['interests'])}",
            "isSubtle": True
        }
    ]

    for session in sessions:
        body.append({
            "type": "Container",
            "separator": True,
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [{
                                "type": "Image",
                                "url": session.get('icon', 'https://via.placeholder.com/40'),
                                "size": "Small"
                            }]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": session['title'],
                                    "weight": "Bolder",
                                    "wrap": True
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"{session['start']} - {session['end']} • {session['location']}",
                                    "isSubtle": True
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"{int(session['score'] * 100)}% match",
                                    "color": "Good" if session['score'] > 0.7 else "Attention",
                                    "size": "Small"
                                }
                            ]
                        }
                    ]
                }
            ]
        })

    return {
        "type": "AdaptiveCard",
        "version": "1.5",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "body": body,
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "Export Full Itinerary",
                "url": f"https://eventkit.com/export?profile={profile['id']}"
            }
        ]
    }
```

---

## 💬 Bot Framework WebChat

### Overview

WebChat provides embedded chat for EventKit bot in websites.

### Setup WebChat

**1. Get Direct Line Token**

```python
# Add to agent.py or separate endpoint
@app.route('/api/directline/token', methods=['POST'])
def get_directline_token():
    """Generate Direct Line token for WebChat."""
    import requests

    # Get token from Bot Framework
    response = requests.post(
        'https://directline.botframework.com/v3/directline/tokens/generate',
        headers={
            'Authorization': f'Bearer {settings.directline_secret}'
        }
    )

    return jsonify(response.json())
```

**2. Create WebChat Page**

Create `webchat.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EventKit Assistant</title>
  <script crossorigin="anonymous"
    src="https://cdn.botframework.com/botframework-webchat/latest/webchat.js">
  </script>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    #webchat-container {
      max-width: 800px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      overflow: hidden;
    }

    #webchat-header {
      background: #4a5568;
      color: white;
      padding: 20px;
      text-align: center;
    }

    #webchat {
      height: 600px;
      width: 100%;
    }
  </style>
</head>
<body>
  <div id="webchat-container">
    <div id="webchat-header">
      <h1>🎯 EventKit Assistant</h1>
      <p>Get personalized session recommendations</p>
    </div>
    <div id="webchat" role="main"></div>
  </div>

  <script>
    (async function() {
      try {
        // Fetch Direct Line token
        const tokenRes = await fetch('https://eventkit.azurewebsites.net/api/directline/token', {
          method: 'POST'
        });
        const { token } = await tokenRes.json();

        // Initialize Web Chat
        const store = window.WebChat.createStore({}, ({ dispatch }) => next => action => {
          if (action.type === 'DIRECT_LINE/CONNECT_FULFILLED') {
            dispatch({
              type: 'WEB_CHAT/SEND_EVENT',
              payload: {
                name: 'webchat/join',
                value: { language: 'en-US' }
              }
            });
          }
          return next(action);
        });

        // Render Web Chat
        window.WebChat.renderWebChat(
          {
            directLine: window.WebChat.createDirectLine({ token }),
            store,
            userID: 'user-' + Date.now(),
            username: 'Conference Attendee',
            locale: 'en-US',
            styleOptions: {
              botAvatarInitials: 'EK',
              botAvatarBackgroundColor: '#667eea',
              userAvatarInitials: 'YOU',
              userAvatarBackgroundColor: '#764ba2',
              primaryFont: 'Segoe UI, sans-serif',
              bubbleBackground: '#f7fafc',
              bubbleFromUserBackground: '#667eea',
              bubbleFromUserTextColor: 'white',
              sendBoxBackground: '#f7fafc',
              sendBoxButtonColor: '#667eea',
              timestampColor: '#718096'
            },
            sendTypingIndicator: true
          },
          document.getElementById('webchat')
        );

        // Send welcome message
        store.dispatch({
          type: 'WEB_CHAT/SEND_EVENT',
          payload: {
            name: 'webchat/welcome',
            value: { message: 'Hi! I can help you find sessions.' }
          }
        });
      } catch (error) {
        console.error('Error initializing webchat:', error);
        document.getElementById('webchat').innerHTML =
          '<p style="padding: 20px; color: red;">Error loading chat. Please refresh.</p>';
      }
    })();
  </script>
</body>
</html>
```

**3. Deploy**

- Host `webchat.html` on Azure Static Web Apps, App Service, or CDN
- Configure Direct Line channel in Azure Bot Service
- Set Direct Line secret in environment variables

### Advanced WebChat Features

**Custom Activities**:

```javascript
// Handle custom events from bot
const activityMiddleware = () => next => card => {
  if (card.activity.type === 'event' && card.activity.name === 'recommendations') {
    // Custom rendering for recommendations
    return (
      <div className="recommendations-card">
        {card.activity.value.sessions.map(session => (
          <div key={session.id}>{session.title}</div>
        ))}
      </div>
    );
  }
  return next(card);
};

window.WebChat.renderWebChat({
  activityMiddleware,
  // ... other config
});
```

---

## 🔍 Microsoft 365 Knowledge Connectors

### Overview

Connect EventKit to Microsoft Search and Microsoft 365 Copilot using Graph Connectors.

### Graph Connector Setup

**1. Register Graph Connector**

```python
from msgraph import GraphServiceClient
from msgraph.generated.models.external_connection import ExternalConnection
from msgraph.generated.models.configuration import Configuration
from msgraph.generated.models.schema import Schema

async def register_eventkit_connector(graph_client: GraphServiceClient):
    """Register EventKit as Graph Connector."""

    # Create external connection
    connection = ExternalConnection(
        id="eventkitSessions",
        name="EventKit Sessions",
        description="Conference sessions with personalized recommendations",
        configuration=Configuration(
            authorization_type="delegated"
        )
    )

    await graph_client.external.connections.post(connection)

    # Define schema
    schema = Schema(
        base_type="microsoft.graph.externalItem",
        properties=[
            {
                "name": "title",
                "type": "string",
                "isSearchable": True,
                "isQueryable": True
            },
            {
                "name": "description",
                "type": "string",
                "isSearchable": True
            },
            {
                "name": "topics",
                "type": "stringCollection",
                "isSearchable": True,
                "isQueryable": True,
                "isRefinable": True
            },
            {
                "name": "sessionTime",
                "type": "dateTime",
                "isQueryable": True,
                "isRefinable": True
            },
            {
                "name": "location",
                "type": "string",
                "isQueryable": True,
                "isRefinable": True
            }
        ]
    )

    await graph_client.external.connections.by_external_connection_id(
        'eventkitSessions'
    ).schema.patch(schema)
```

**2. Ingest Session Data**

```python
from msgraph.generated.models.external_item import ExternalItem
from msgraph.generated.models.acl import Acl
from msgraph.generated.models.access_type import AccessType

async def ingest_sessions(graph_client: GraphServiceClient, sessions: List[Dict]):
    """Ingest sessions into Graph Connector."""

    for session in sessions:
        item = ExternalItem(
            id=session['id'],
            content={
                "type": "html",
                "value": f"<h1>{session['title']}</h1><p>{session['description']}</p>"
            },
            acl=[
                Acl(
                    type="everyone",
                    value="everyone",
                    access_type=AccessType.Grant
                )
            ],
            properties={
                "title": session['title'],
                "description": session['description'],
                "topics": session['topics'],
                "sessionTime": session['start'],
                "location": session['location']
            }
        )

        await graph_client.external.connections.by_external_connection_id(
            'eventkitSessions'
        ).items.by_external_item_id(session['id']).put(item)
```

**3. Search External Content**

```python
from msgraph.generated.search.query.query_post_request_body import QueryPostRequestBody
from msgraph.generated.models.search_request import SearchRequest
from msgraph.generated.models.entity_type import EntityType

async def search_eventkit_sessions(graph_client: GraphServiceClient, query: str):
    """Search EventKit sessions via Microsoft Search."""

    request_body = QueryPostRequestBody(
        requests=[
            SearchRequest(
                entity_types=[EntityType.ExternalItem],
                query=SearchQueryType(query_string=query),
                content_sources=["/external/connections/eventkitSessions"],
                from_=0,
                size=25
            )
        ]
    )

    result = await graph_client.search.query.post(request_body)

    # Extract and return results
    hits = []
    for response in result.value:
        for hit_container in response.hits_containers:
            hits.extend(hit_container.hits)

    return hits
```

### Copilot Integration

Once Graph Connector is configured, EventKit sessions appear in:

- **Microsoft Search** (Office.com, SharePoint, Bing)
- **Microsoft 365 Copilot** - "Find EventKit sessions about AI"
- **Outlook** - Search for sessions in email compose

### Scheduled Sync

Create Azure Function for daily sync:

```python
import azure.functions as func
from datetime import datetime

@app.timer_trigger(schedule="0 0 2 * * *", arg_name="timer")
async def sync_eventkit_to_graph(timer: func.TimerRequest):
    """Sync EventKit sessions to Graph Connector daily at 2 AM."""
    logging.info(f'Graph Connector sync triggered at {datetime.utcnow()}')

    # Load sessions
    manifest = load_manifest()
    sessions = manifest['sessions']

    # Ingest to Graph
    graph_client = get_graph_client()
    await ingest_sessions(graph_client, sessions)

    logging.info(f'Synced {len(sessions)} sessions to Graph Connector')
```

---

## 🚀 Quick Reference

### VS Code Snippets

Use these snippets (already in `.vscode/eventkit.code-snippets`):

- `ekadaptivecard` - Adaptive Card template
- `ekpowerconnector` - Power Platform connector OpenAPI
- `ekfunction` - Azure Function HTTP trigger
- `ekagentaction` - Declarative agent action
- `ekskill` - Agent SDK skill function
- `ekknowledge` - M365 Knowledge Connector query
- `ekwebchat` - WebChat HTML integration
- `ekpowerflow` - Power Automate flow action

### Common Tasks

| Task | Command |
|------|---------|
| Test Power Connector | `Test-PowerPlatformConnector -ConnectorId eventkit` |
| Deploy Azure Function | `func azure functionapp publish eventkit-functions` |
| Validate Adaptive Card | Visit [adaptivecards.io/designer](https://adaptivecards.io/designer/) |
| Test WebChat locally | Open `webchat.html` in browser |
| Sync Graph Connector | `python scripts/sync_graph_connector.py` |

### Additional Resources

- [Power Platform Connectors](https://learn.microsoft.com/connectors/custom-connectors/)
- [Azure Functions Python](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Declarative Agents](https://learn.microsoft.com/microsoft-365-copilot/extensibility/declarative-agent-manifest)
- [Adaptive Cards](https://adaptivecards.io/)
- [Bot Framework WebChat](https://github.com/microsoft/BotFramework-WebChat)
- [Graph Connectors](https://learn.microsoft.com/graph/connecting-external-content-connectors-overview)

---

## 🆘 Troubleshooting

**Power Platform Connector not working**:
- Verify OpenAPI spec is valid
- Check authentication configuration
- Test endpoints directly with curl
- Review connector logs in Power Platform admin

**Azure Functions cold start**:
- Use Premium plan for always-on
- Enable Application Insights for diagnostics
- Configure proper dependency management

**Adaptive Cards not rendering**:
- Validate JSON at [adaptivecards.io/designer](https://adaptivecards.io/designer/)
- Check Adaptive Card version compatibility
- Verify host application supports card features

**WebChat connection issues**:
- Verify Direct Line secret is correct
- Check CORS settings on backend
- Review Bot Framework channel configuration
- Test with Bot Framework Emulator first

**Graph Connector sync failing**:
- Verify app permissions (ExternalItem.ReadWrite.All)
- Check schema matches data structure
- Review Graph API error responses
- Use Graph Explorer for debugging

---

**Need more help?** Check [docs/troubleshooting.md](troubleshooting.md) or contact the team.
