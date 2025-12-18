# API Documentation Guide

This guide helps you find and use the Event Kit Agent API documentation.

## Quick Links

- **OpenAPI Specification**: [openapi-spec.yaml](openapi-spec.yaml) - Complete machine-readable API definition
- **API Examples**: [api-examples.md](api-examples.md) - Practical code examples across languages
- **This Guide**: [api-guide.md](api-guide.md) - How to use the documentation

## Overview

The Event Kit Agent API provides three main capabilities:

1. **Recommend**: Get personalized session recommendations
2. **Explain**: Understand why a session matches your interests
3. **Export**: Save your itinerary as Markdown

Plus Graph integration for calendar-based recommendations.

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/recommend` | GET | Get recommendations |
| `/recommend-graph` | GET | Graph-based recommendations |
| `/explain` | GET | Explain a session |
| `/export` | GET | Export itinerary |

## Getting Started

### 1. Local Development

```bash
# Start the server
python agent.py serve --port 8010

# Health check
curl http://localhost:8010/health

# Get recommendations
curl "http://localhost:8010/recommend?interests=agents&top=3"
```

### 2. Docker Deployment

```bash
# Start with Docker Compose
docker-compose -f deploy/docker-compose.yml up

# Test
curl http://localhost:8010/health
```

### 3. Production Deployment

```bash
# Deploy to Azure
make deploy-prod

# Test
curl https://YOUR-APP-NAME.azurewebsites.net/health
```

## Using the OpenAPI Spec

The `openapi-spec.yaml` file is a complete, machine-readable API definition that can be:

- **Viewed in Swagger UI**: Paste into https://editor.swagger.io
- **Generated as documentation**: Use tools like ReDoc or Redoc
- **Code generation**: Generate SDKs for various languages
- **Validation**: Validate requests/responses

### Generate Documentation

```bash
# Using ReDoc (static HTML)
docker run -p 8080:80 \
  -e SPEC_URL=https://raw.githubusercontent.com/peterswimm/event-agent-example/main/docs/openapi-spec.yaml \
  redocly/redoc

# Open http://localhost:8080
```

### Generate Python SDK

```bash
# Using openapi-generator
openapi-generator generate \
  -i docs/openapi-spec.yaml \
  -g python \
  -o python-sdk

# Use generated client
from openapi_client import RecommendApi
api = RecommendApi()
```

## Common Use Cases

### Use Case 1: Simple Recommendation

Get the top 3 sessions for your interests.

```bash
curl "http://localhost:8010/recommend?interests=agents,machine%20learning&top=3"
```

See: [api-examples.md - Basic Recommendation](api-examples.md#basic-recommendation)

### Use Case 2: Explain a Session

Understand why a specific session is recommended.

```bash
curl "http://localhost:8010/explain?session=Generative%20Agents&interests=agents,ai"
```

See: [api-examples.md - Explain a Session](api-examples.md#explain-a-session)

### Use Case 3: Export Your Itinerary

Save recommendations as a Markdown file.

```bash
curl "http://localhost:8010/export?interests=agents&profileSave=my-profile" -o itinerary.md
```

See: [api-examples.md - Export Itinerary](api-examples.md#export-itinerary)

### Use Case 4: Integrate with Teams

Display recommendations in Microsoft Teams using Adaptive Cards.

```bash
curl "http://localhost:8010/recommend?interests=agents&card=1"
```

See: [api-examples.md - Teams/Copilot](api-examples.md#teamcopilot)

### Use Case 5: Batch Processing

Process multiple interest sets and export results.

```bash
# See: [api-examples.md - Python Requests - Batch Operations](api-examples.md#batch-operations)
```

## Authentication

### API Token

The API supports bearer token authentication:

```bash
export API_TOKEN="your-token"
curl -H "Authorization: Bearer $API_TOKEN" http://localhost:8010/recommend?interests=agents
```

### No Authentication

If `API_TOKEN` is not set, the API is open (useful for development).

## Request Tracing

Use correlation IDs to trace requests through logs:

```bash
curl -H "X-Correlation-ID: my-trace-id" http://localhost:8010/recommend?interests=agents
```

The response includes the same correlation ID in the `X-Correlation-ID` header.

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "InvalidInputError",
  "message": "Must provide either interests or profileLoad parameter",
  "statusCode": 400,
  "correlationId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Error Types

- `InvalidInputError` - Bad request parameters
- `RateLimitError` - Rate limit exceeded
- `GraphAuthError` - Graph API authentication failed
- `GraphAPIError` - Graph API returned an error
- `EventKitError` - Other errors

See: [api-examples.md - Error Handling](api-examples.md#error-handling)

## Response Formats

### Recommendation Response

```json
{
  "sessions": [...],
  "scoring": [...],
  "conflicts": 0,
  "correlationId": "..."
}
```

### Explanation Response

```json
{
  "session": "Session Title",
  "explanation": "...",
  "matchedKeywords": [...],
  "relevanceScore": 0.92
}
```

### Export Response

Plain text Markdown content.

## Rate Limiting

- **Limit**: 100 requests per minute per IP
- **Status**: 429 Too Many Requests when exceeded
- **Retry**: Use exponential backoff

See: [api-examples.md - Rate Limiting](api-examples.md#rate-limiting)

## Code Examples by Language

### curl
```bash
curl "http://localhost:8010/recommend?interests=agents"
```

### Python
```python
import requests
response = requests.get("http://localhost:8010/recommend", params={"interests": "agents"})
```

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8010/recommend" -Method Get
```

### JavaScript
```javascript
const response = await fetch("http://localhost:8010/recommend?interests=agents");
```

See: [api-examples.md](api-examples.md) for complete examples in each language.

## Testing the API

### Manual Testing

```bash
# Health check
curl http://localhost:8010/health

# Recommend
curl "http://localhost:8010/recommend?interests=agents&top=3"

# Explain
curl "http://localhost:8010/explain?session=Session%20Title&interests=agents"

# Export
curl "http://localhost:8010/export?interests=agents" -o itinerary.md
```

### Automated Testing

```bash
# Using pytest
pytest tests/test_server.py -v

# Using curl with jq
curl -s "http://localhost:8010/recommend?interests=agents" | jq '.sessions | length'
```

## Swagger UI / OpenAPI Explorer

You can view the full API documentation interactively:

1. Go to https://editor.swagger.io
2. Select "File" → "Import URL"
3. Enter your OpenAPI spec URL or paste the YAML

### Local Swagger UI

```bash
# Using Docker
docker run -p 8080:80 \
  -e URL=/docs/openapi-spec.yaml \
  -v $(pwd)/docs:/usr/share/nginx/html/docs \
  nginx

# Open http://localhost:8080
```

## Integration Guides

### Microsoft Teams

See: [Adaptive Card Integration](./application-patterns.md#teams-adaptive-cards)

### Copilot Extensions

See: [Copilot Integration](./application-patterns.md#copilot-integration)

### Power Automate / Logic Apps

See: [Azure Integration](./data-integration.md#azure-automation)

## Performance Considerations

- **Caching**: Results are relatively stable; consider caching
- **Pagination**: Not yet implemented; `top` parameter limits results
- **Timeouts**: Use 5-10 second timeouts
- **Batch Size**: Limit batch operations to 10-20 concurrent requests

See: [Performance Guide](./performance-guide.md)

## Troubleshooting

### API Not Responding

1. Check server is running: `curl http://localhost:8010/health`
2. Check logs: `docker logs eventkit-agent` or check console
3. Verify port: `netstat -an | grep 8010`

### Authentication Fails

1. Verify `API_TOKEN` environment variable is set
2. Check token is included in `Authorization` header
3. Verify format: `Bearer YOUR_TOKEN`

### Rate Limit Errors

1. Reduce request rate
2. Implement exponential backoff retry logic
3. Consider caching recommendations

### Graph API Errors

1. Verify Graph credentials are configured
2. Check credentials in Key Vault (production)
3. Verify user calendars are accessible

See: [api-examples.md - Troubleshooting](api-examples.md#troubleshooting)

## API Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01 | Initial release with /recommend, /explain, /export, /recommend-graph endpoints |

## Support

For issues or questions:

1. Check [api-examples.md](api-examples.md) for examples
2. Review [Troubleshooting](./troubleshooting.md)
3. Check correlation IDs in logs
4. File an issue on GitHub

## Additional Resources

- [Technical Guide](./technical-guide.md) - Architecture and internals
- [Performance Guide](./performance-guide.md) - Optimization tips
- [Application Patterns](./application-patterns.md) - Design patterns
- [Data Integration](./data-integration.md) - External data sources
- [Troubleshooting](./troubleshooting.md) - Common issues
