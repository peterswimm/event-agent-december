# Event Kit Agent - API Usage Examples

This guide provides practical examples for integrating with the Event Kit Agent API across multiple languages and tools.

## Table of Contents

- [curl (Command Line)](#curl-examples)
- [Python Requests](#python-requests)
- [PowerShell](#powershell)
- [JavaScript/Node.js](#javascriptnodejs)
- [Teams/Copilot](#teamcopilot)
- [Error Handling](#error-handling)
- [Authentication](#authentication)
- [Troubleshooting](#troubleshooting)

---

## curl Examples

### Basic Recommendation

Get session recommendations based on interests:

```bash
curl "http://localhost:8010/recommend?interests=agents,ai%20safety&top=3"
```

### With Authentication

```bash
export API_TOKEN="your-api-token-here"

curl -H "Authorization: Bearer $API_TOKEN" \
  "http://localhost:8010/recommend?interests=python,data%20science&top=5"
```

### With Correlation ID (for tracing)

```bash
curl -H "X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000" \
  "http://localhost:8010/recommend?interests=agents&top=3"
```

### Request Adaptive Card

Include rich UI for Teams/Copilot:

```bash
curl "http://localhost:8010/recommend?interests=machine%20learning&top=3&card=1"
```

### Explain a Session

```bash
curl "http://localhost:8010/explain?session=Generative%20Agents%20in%20Production&interests=agents,production"
```

### Export Itinerary

```bash
curl "http://localhost:8010/export?interests=cloud,security&profileSave=myprofile" \
  -o my_itinerary.md
```

### Health Check

```bash
curl http://localhost:8010/health
```

### Save Options

Requests and responses with JSON output:

```bash
# Get JSON recommendations
curl -s "http://localhost:8010/recommend?interests=agents&top=3" | jq .

# Count recommended sessions
curl -s "http://localhost:8010/recommend?interests=agents&top=3" | jq '.sessions | length'

# Extract session titles
curl -s "http://localhost:8010/recommend?interests=agents&top=3" | jq '.sessions[] | .title'
```

---

## Python Requests

### Installation

```bash
pip install requests
```

### Basic Example

```python
import requests
import json

# Configure
API_BASE = "http://localhost:8010"
INTERESTS = "agents, ai safety, machine learning"

# Make request
response = requests.get(
    f"{API_BASE}/recommend",
    params={
        "interests": INTERESTS,
        "top": 5,
        "card": "1"
    }
)

# Handle response
if response.status_code == 200:
    result = response.json()
    print(f"Found {len(result['sessions'])} recommendations")
    for session in result['sessions']:
        print(f"  - {session['title']} (score: {result['scoring'][0]['score']})")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### With Authentication

```python
import requests
import os

API_TOKEN = os.getenv("API_TOKEN")
headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

response = requests.get(
    "http://localhost:8010/recommend",
    params={"interests": "agents, ai"},
    headers=headers,
    timeout=10
)

result = response.json()
```

### With Correlation ID

```python
import requests
import uuid

correlation_id = str(uuid.uuid4())
headers = {
    "X-Correlation-ID": correlation_id
}

response = requests.get(
    "http://localhost:8010/recommend",
    params={"interests": "agents"},
    headers=headers
)

# Response includes same correlation ID
response_cid = response.headers.get("X-Correlation-ID")
print(f"Trace ID: {response_cid}")
```

### Batch Operations

```python
import requests
import json

class EventKitClient:
    def __init__(self, base_url="http://localhost:8010", api_token=None):
        self.base_url = base_url
        self.session = requests.Session()
        if api_token:
            self.session.headers.update({
                "Authorization": f"Bearer {api_token}"
            })
    
    def recommend(self, interests, top=5, card=False):
        """Get recommendations"""
        response = self.session.get(
            f"{self.base_url}/recommend",
            params={
                "interests": interests,
                "top": top,
                "card": "1" if card else "0"
            }
        )
        response.raise_for_status()
        return response.json()
    
    def explain(self, session, interests):
        """Explain a session"""
        response = self.session.get(
            f"{self.base_url}/explain",
            params={
                "session": session,
                "interests": interests
            }
        )
        response.raise_for_status()
        return response.json()
    
    def export(self, interests, profile_save=None):
        """Export itinerary"""
        params = {"interests": interests}
        if profile_save:
            params["profileSave"] = profile_save
        
        response = self.session.get(
            f"{self.base_url}/export",
            params=params
        )
        response.raise_for_status()
        return response.text  # Markdown content

# Usage
client = EventKitClient(api_token="your-token")

# Recommend
recommendations = client.recommend("agents, ai safety", top=3)
print(f"Recommendations: {len(recommendations['sessions'])}")

# Explain
explanation = client.explain("Generative Agents", "agents, production")
print(f"Explanation: {explanation['explanation']}")

# Export
markdown = client.export("agents, safety", profile_save="my-profile")
with open("itinerary.md", "w") as f:
    f.write(markdown)
```

### Error Handling

```python
import requests
from requests.exceptions import RequestException, Timeout

try:
    response = requests.get(
        "http://localhost:8010/recommend",
        params={"interests": "agents"},
        timeout=5
    )
    response.raise_for_status()
    result = response.json()
    
except Timeout:
    print("Request timed out")
    
except requests.HTTPError as e:
    if response.status_code == 400:
        error = response.json()
        print(f"Invalid input: {error['message']}")
    elif response.status_code == 429:
        print("Rate limit exceeded")
    else:
        print(f"HTTP Error: {e}")
        
except RequestException as e:
    print(f"Request failed: {e}")
```

---

## PowerShell

### Basic Example

```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8010/recommend" `
  -Method Get `
  -Body @{
    interests = "agents, ai safety"
    top = 5
  }

$data = $response.Content | ConvertFrom-Json
$data.sessions | Select-Object title, category | Format-Table
```

### With Authentication

```powershell
$token = $env:API_TOKEN
$headers = @{
  Authorization = "Bearer $token"
}

$response = Invoke-WebRequest -Uri "http://localhost:8010/recommend" `
  -Method Get `
  -Headers $headers `
  -Body @{
    interests = "agents"
  }

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 4
```

### Batch Processing

```powershell
function Get-EventRecommendations {
  param(
    [Parameter(Mandatory=$true)]
    [string]$Interests,
    
    [int]$Top = 5,
    
    [switch]$IncludeCard
  )
  
  $params = @{
    interests = $Interests
    top = $Top
  }
  
  if ($IncludeCard) {
    $params.card = "1"
  }
  
  $response = Invoke-WebRequest -Uri "http://localhost:8010/recommend" `
    -Method Get `
    -Body $params
  
  return $response.Content | ConvertFrom-Json
}

# Usage
$recommendations = Get-EventRecommendations -Interests "cloud, security" -Top 3

foreach ($session in $recommendations.sessions) {
  Write-Host "Title: $($session.title)"
  Write-Host "Category: $($session.category)"
  Write-Host "---"
}
```

### Export to CSV

```powershell
$recommendations = Invoke-WebRequest -Uri "http://localhost:8010/recommend" `
  -Method Get `
  -Body @{ interests = "agents" } | `
  Select-Object -ExpandProperty Content | `
  ConvertFrom-Json

$recommendations.sessions | `
  Select-Object @(
    @{Name="Title"; Expression={$_.title}},
    @{Name="Category"; Expression={$_.category}},
    @{Name="Popularity"; Expression={$_.popularity}}
  ) | `
  Export-Csv -Path "sessions.csv" -NoTypeInformation
```

---

## JavaScript/Node.js

### Installation

```bash
npm install axios
```

### Basic Example

```javascript
const axios = require('axios');

const API_BASE = 'http://localhost:8010';

async function getRecommendations(interests, top = 5) {
  try {
    const response = await axios.get(`${API_BASE}/recommend`, {
      params: {
        interests: interests,
        top: top,
        card: '1'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    throw error;
  }
}

// Usage
getRecommendations('agents, ai safety', 3)
  .then(result => {
    console.log(`Found ${result.sessions.length} recommendations`);
    result.sessions.forEach(session => {
      console.log(`- ${session.title}`);
    });
  });
```

### With Authentication

```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'http://localhost:8010',
  headers: {
    'Authorization': `Bearer ${process.env.API_TOKEN}`
  }
});

async function recommend(interests) {
  const response = await client.get('/recommend', {
    params: { interests, top: 5 }
  });
  return response.data;
}
```

### Correlation Tracking

```javascript
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

const correlationId = uuidv4();

const response = await axios.get('http://localhost:8010/recommend', {
  params: { interests: 'agents' },
  headers: {
    'X-Correlation-ID': correlationId
  }
});

console.log(`Response correlation ID: ${response.headers['x-correlation-id']}`);
```

### Streaming Example (for export)

```javascript
const axios = require('axios');
const fs = require('fs');

async function exportItinerary(interests, outputFile) {
  const response = await axios.get(
    'http://localhost:8010/export',
    {
      params: {
        interests: interests,
        profileSave: 'my-profile'
      },
      responseType: 'stream'
    }
  );
  
  response.data.pipe(fs.createWriteStream(outputFile));
  
  return new Promise((resolve, reject) => {
    response.data.on('end', () => resolve());
    response.data.on('error', reject);
  });
}

// Usage
exportItinerary('agents, security', 'itinerary.md')
  .then(() => console.log('Exported successfully'));
```

### React Component Example

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

export function RecommendationWidget({ interests }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        const response = await axios.get(
          'http://localhost:8010/recommend',
          {
            params: {
              interests: interests,
              top: 5,
              card: '1'
            }
          }
        );
        setSessions(response.data.sessions);
        setError(null);
      } catch (err) {
        setError(err.message);
        setSessions([]);
      } finally {
        setLoading(false);
      }
    };

    if (interests) {
      fetchRecommendations();
    }
  }, [interests]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="recommendations">
      {sessions.map(session => (
        <div key={session.id} className="session">
          <h3>{session.title}</h3>
          <p>{session.category}</p>
          <p>Popularity: {session.popularity}%</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Teams/Copilot

### Adaptive Card Response

When you include `card=1` in a recommendation request, the API returns an Adaptive Card:

```bash
curl "http://localhost:8010/recommend?interests=agents&top=3&card=1"
```

The response includes an `adaptiveCard` property with a complete Adaptive Card JSON that Teams and Copilot can render.

### Teams Bot Integration Example

```python
from botbuilder.core import Bot, BotFrameworkAdapterSettings, ConversationState
from botbuilder.schema import Activity, ActivityTypes
import requests

class EventKitBot(Bot):
    def on_message_activity(self, turn_context):
        # Extract interests from message
        interests = turn_context.activity.text
        
        # Call Event Kit API
        response = requests.get(
            "http://localhost:8010/recommend",
            params={
                "interests": interests,
                "card": "1",
                "top": 5
            }
        )
        
        result = response.json()
        
        # Send Adaptive Card in Teams
        message = Activity(
            type=ActivityTypes.message,
            attachments=[{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": result.get("adaptiveCard")
            }]
        )
        
        return turn_context.send_activity(message)
```

---

## Error Handling

### Common Error Scenarios

#### Missing Interests

```bash
curl "http://localhost:8010/recommend"
# Response: 400
# {
#   "error": "InvalidInputError",
#   "message": "Must provide either interests or profileLoad parameter",
#   "statusCode": 400
# }
```

#### Rate Limit Exceeded

```bash
# After 100 requests per minute from same IP
curl "http://localhost:8010/recommend?interests=agents"
# Response: 429
# {
#   "error": "RateLimitError",
#   "message": "Rate limit exceeded: 100 requests per minute",
#   "statusCode": 429
# }
```

#### Graph API Not Configured

```bash
curl "http://localhost:8010/recommend-graph?interests=agents"
# Response: 400
# {
#   "error": "GraphAuthError",
#   "message": "Graph API credentials not configured",
#   "statusCode": 400
# }
```

#### Invalid Session

```bash
curl "http://localhost:8010/explain?session=NonexistentSession&interests=agents"
# Response: 400
# {
#   "error": "InvalidInputError",
#   "message": "Session 'NonexistentSession' not found",
#   "statusCode": 400
# }
```

---

## Authentication

### Environment Setup

```bash
# Set API token
export API_TOKEN="your-secure-token-here"

# Or in .env file (Docker)
echo "API_TOKEN=your-secure-token" >> deploy/.env
```

### Token Format

The API expects bearer tokens in the Authorization header:

```bash
Authorization: Bearer <TOKEN>
```

### Token Validation

The server validates tokens by comparing against the `API_TOKEN` environment variable. If no token is configured, all requests are allowed.

---

## Rate Limiting

### Default Limits

- **100 requests per minute** per IP address
- Windowed rate limiting (sliding window)
- Returns 429 status when exceeded

### IP Resolution

The server uses:
1. `X-Forwarded-For` header (if behind proxy)
2. Direct connection IP (if direct)

### Retry Strategy

```python
import time
import requests

def retry_with_backoff(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 429:
                # Rate limited - wait and retry
                wait_time = 2 ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            
            time.sleep(2 ** attempt)
```

---

## Troubleshooting

### Server Not Responding

```bash
# Check health
curl http://localhost:8010/health

# Check logs
docker logs eventkit-agent

# Check port
netstat -an | grep 8010
```

### CORS Issues

The API supports CORS with `Access-Control-Allow-Origin: *`. If you get CORS errors:

1. Verify the API is running
2. Check browser console for exact error
3. Ensure you're using correct domain/port
4. Verify `Origin` header is being sent

### Authentication Failures

```bash
# Test with token
curl -H "Authorization: Bearer $API_TOKEN" http://localhost:8010/health

# Test without token (if auth disabled)
curl http://localhost:8010/health

# Verify token environment variable
echo $API_TOKEN
```

### Slow Responses

```bash
# Add timing
curl -w "@curl-format.txt" "http://localhost:8010/recommend?interests=agents"

# Check API logs for performance
# Look for correlation ID in logs
curl -H "X-Correlation-ID: debug-trace" "http://localhost:8010/recommend?interests=agents"
```

### Graph API Errors

```bash
# Verify Graph credentials are configured
echo $GRAPH_TENANT_ID
echo $GRAPH_CLIENT_ID

# Test Graph endpoint
curl "http://localhost:8010/recommend-graph?interests=agents"
```

---

## Best Practices

1. **Always use timeouts** (5-10 seconds)
2. **Implement exponential backoff** for retries
3. **Include correlation IDs** for tracing
4. **Handle all error responses** with proper messages
5. **Cache results** when appropriate (insights don't change frequently)
6. **Use connection pooling** for multiple requests
7. **Validate input** before sending to API
8. **Monitor rate limits** and adjust request patterns
9. **Use profiles** for saved preferences instead of repeating interests
10. **Test with `/health`** before production use
