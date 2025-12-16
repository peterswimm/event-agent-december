# HTTP API Guide

Event Kit exposes a lightweight HTTP API for recommendations, explanations, exports, and health checks.

## Start the Server

```bash
python agent.py serve --port 8080 --card
```

- `--port`: Port to listen on (default: 8080)
- `--card`: Include Adaptive Card in responses

## Authentication (Optional)

If `API_TOKEN` is set in the environment, all requests must include:

```http
Authorization: Bearer <API_TOKEN>
```

Without the correct token, the server returns `401 {"error":"unauthorized"}`.

## Endpoints

### GET /health

Health check for the server.

- Response: `200 {"status":"ok"}`

Example:
```bash
curl http://localhost:8080/health
```

### GET /recommend

Get recommendations using the manifest sessions.

**Query parameters:**
- `interests` (string, required): Comma-separated interests (e.g., `agents,ai+safety`)
- `top` (int, optional): Number of recommendations (default: `manifest["recommend"]["max_sessions_default"]`)
- `profileLoad` (string, optional): Profile name to load interests from
- `card` (1 or 0, optional): Include Adaptive Card in response

**Response:**
```json
{
  "sessions": [
    {
      "title": "Generative Agents in Production",
      "score": 0.87,
      "topics": ["agents", "gen ai"]
    }
  ],
  "adaptiveCard": { /* present if card=1 or server started with --card */ }
}
```

Example:
```bash
curl "http://localhost:8080/recommend?interests=agents,ai&top=3&card=1"
```

### GET /explain

Explain why a session was recommended.

**Query parameters:**
- `session` (string, required): Session title
- `interests` (string, required): Your interests
- `profileLoad` (string, optional): Load interests from profile

**Response:**
```json
{
  "session": "Generative Agents in Production",
  "interests": ["agents", "gen ai"],
  "weights": { "interests": 0.5, "topics": 0.3, "recency": 0.2 },
  "score": 0.87,
  "explanation": "Matched topics: agents, gen ai"
}
```

Example:
```bash
curl "http://localhost:8080/explain?session=Generative+Agents+in+Production&interests=agents,gen+ai"
```

### GET /recommend-graph

Get recommendations using Microsoft Graph calendar events.

Requires Graph credentials. See [Graph API Setup](../03-GRAPH-API/setup.md).

**Query parameters:**
- `interests` (string, required): Comma-separated interests
- `top` (int, optional): Number of recommendations (default: manifest value)
- `userId` (string, optional): Email address for Graph queries (can be omitted if set in `.env`)
- `card` (1 or 0, optional): Include Adaptive Card

**Response:**
```json
{
  "sessions": [
    { "title": "Meeting with Agents Team", "score": 0.92 }
  ],
  "userId": "user@company.com", // present if provided
  "adaptiveCard": { /* present if enabled */ }
}
```

Example:
```bash
curl "http://localhost:8080/recommend-graph?interests=ai+safety&top=3&userId=user@company.com"
```

### GET /export

Export recommended sessions as Markdown.

**Query parameters:**
- `interests` (string, required): Comma-separated interests
- `profileLoad` (string, optional): Load interests from profile

**Response:**
```json
{
  "markdown": "# Itinerary...",
  "sessionCount": 3,
  "saved": "exports/itinerary_agents_ai.md" // present if feature flag enabled
}
```

Example:
```bash
curl "http://localhost:8080/export?interests=agents,privacy"
```

## Errors

- `400 {"error":"no interests provided"}` — Missing interests
- `400 {"error":"session required"}` — Missing session for `/explain`
- `401 {"error":"unauthorized"}` — Missing or invalid `Authorization` header when `API_TOKEN` is set
- `502 {"error":"Graph API error: ..."}` — Graph API failed
- `503 {"error":"Graph API support not available"}` — Graph libraries not installed
- `404 {"error":"not found"}` — Unknown path

## Notes

- Use `card=1` or `--card` server flag to include Adaptive Cards for Copilot experiences.
- Default `top` is controlled by `agent.json` → `recommend.max_sessions_default`.
- Profiles are stored in `~/.event_agent_profiles.json` and loaded via `profileLoad`.
