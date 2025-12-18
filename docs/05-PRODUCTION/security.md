# Security & Governance

Security considerations, compliance guidelines, and governance practices for Event Kit.

## Security Architecture

Event Kit follows a **defense-in-depth** approach with multiple security layers:

```text
┌─────────────────────────────────────┐
│  Network Layer (HTTPS, Firewall)   │
├─────────────────────────────────────┤
│  Authentication (MSAL, API Token)   │
├─────────────────────────────────────┤
│  Input Validation (Sanitization)    │
├─────────────────────────────────────┤
│  Data Protection (Local-only)       │
├─────────────────────────────────────┤
│  Observability (Telemetry, Logs)    │
└─────────────────────────────────────┘
```

## Authentication & Authorization

### Microsoft Graph API

**Authentication method:** Application permissions (daemon app)

**Required permissions:**

- `Calendars.Read` — Read user calendar events
- `User.Read.All` — Read user profiles (optional)

**Token flow:**

```text
1. App authenticates with client credentials
2. MSAL acquires access token (cached)
3. Token used for Graph API calls
4. Token refreshed automatically before expiration
```

**Token storage:**

- Location: `~/.msal_token_cache.bin`
- Format: Encrypted JSON (OS keychain on macOS/Windows)
- Permissions: 0600 (owner read/write only)

**Security considerations:**

- ✅ **Use application permissions** (not delegated) for daemon apps
- ✅ **Store client secret in environment variables** (never in code)
- ✅ **Rotate client secret every 90 days**
- ✅ **Monitor token cache for unauthorized access**
- ✅ **Require admin consent** for Graph API permissions

### HTTP API Authentication

**Optional bearer token authentication:**

```bash
# Set API_TOKEN in .env
API_TOKEN="your-secret-token-here"
```

**Request format:**

```bash
curl -H "Authorization: Bearer your-secret-token-here" \
    http://localhost:8000/recommend \
    -d '{"interests": ["ai"], "top": 5}'
```

**Token validation:**

```python
# agent.py
def validate_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    expected = os.getenv('API_TOKEN')
    
    if not expected:
        return True  # No token required
    
    return token == expected
```

**Security considerations:**

- ✅ **Use strong random tokens** (32+ characters)
- ✅ **Rotate tokens regularly** (every 90 days)
- ✅ **Require HTTPS in production** (prevent token interception)
- ✅ **Log authentication failures** to telemetry
- ✅ **Implement rate limiting** to prevent brute force

## Input Validation & Sanitization

### Interest Strings

**Threat:** Injection attacks via user-supplied interests.

**Mitigation:**

```python
def _normalize_interests(raw: str) -> List[str]:
    # Treat as plain text only (no execution)
    norm = raw.replace(";", ",").lower()
    interests = [t.strip() for t in norm.split(",") if t.strip()]
    
    # Limit length to prevent DOS
    interests = interests[:20]  # Max 20 interests
    
    # Validate characters (alphanumeric + spaces)
    validated = []
    for interest in interests:
        if len(interest) <= 100 and interest.replace(" ", "").isalnum():
            validated.append(interest)
    
    return validated
```

**Security considerations:**

- ✅ **No code execution** — Interests treated as plain text
- ✅ **Length limits** — Prevent memory exhaustion
- ✅ **Character validation** — Allow only alphanumeric + spaces
- ✅ **No SQL injection risk** — No database (JSON file storage)

### Session Titles & Tags

**Threat:** XSS or injection via session metadata.

**Mitigation:**

```python
def sanitize_session(session: Dict) -> Dict:
    """Sanitize session metadata for safe display."""
    import html
    
    return {
        "id": session.get("id", ""),
        "title": html.escape(session.get("title", "")),
        "tags": [html.escape(t) for t in session.get("tags", [])],
        # ... other fields
    }
```

**Security considerations:**

- ✅ **Escape HTML entities** before rendering
- ✅ **No script tags** in titles or tags
- ✅ **Validate data types** (strings, not objects)
- ✅ **Strip dangerous characters** (`<`, `>`, `"`, `'`)

### Query Parameters

**Threat:** Parameter tampering or DOS via large values.

**Mitigation:**

```python
def validate_request(body: Dict) -> Dict:
    """Validate and sanitize request parameters."""
    
    # Validate interests
    interests = body.get("interests", [])
    if not isinstance(interests, list):
        raise ValueError("interests must be a list")
    if len(interests) > 20:
        raise ValueError("Max 20 interests allowed")
    
    # Validate top
    top = body.get("top", 5)
    if not isinstance(top, int):
        raise ValueError("top must be an integer")
    if top < 1 or top > 50:
        raise ValueError("top must be between 1 and 50")
    
    return {"interests": interests, "top": top}
```

## Data Protection

### Data Boundaries

Event Kit enforces **local-only data storage**:

| Data Type | Storage | Network Access |
|-----------|---------|----------------|
| Sessions (manifest) | Local JSON file | ❌ No |
| External sessions | Local JSON file | ❌ No |
| Profiles | Local JSON file | ❌ No |
| Telemetry | Local JSONL file | ❌ No |
| Token cache | Local encrypted file | ❌ No |

**Security considerations:**

- ✅ **No database** — Eliminates SQL injection risk
- ✅ **No remote storage** — Data stays on server
- ✅ **No external network calls** (except Graph API)
- ✅ **File permissions** — Owner read/write only (0600)

### Secrets Management

**Never embed secrets in:**

- ❌ Source code
- ❌ Session titles or tags
- ❌ Telemetry payload
- ❌ Log files
- ❌ Version control (Git)

**Use environment variables:**

```bash
# .env (never commit to Git)
TENANT_ID="your-tenant-id"
CLIENT_ID="your-client-id"
CLIENT_SECRET="your-client-secret"
API_TOKEN="your-api-token"
```

**Add to `.gitignore`:**

```gitignore
.env
.env.*
*.secret
*_secret.*
.msal_token_cache.bin
```

**Use secret management services:**

- **Azure Key Vault** — For Azure deployments
- **AWS Secrets Manager** — For AWS deployments
- **HashiCorp Vault** — For on-premises

**Example with Azure Key Vault:**

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net", credential=credential)

# Retrieve secrets
tenant_id = client.get_secret("TENANT-ID").value
client_id = client.get_secret("CLIENT-ID").value
client_secret = client.get_secret("CLIENT-SECRET").value
```

### PII Handling

**PII in Event Kit:**

- User email addresses (Graph API user ID)
- Session attendee names (if included in titles/tags)
- Calendar event details

**Mitigation:**

1. **Exclude PII from telemetry:**

```python
def log_telemetry(action, payload):
    # Remove PII before logging
    safe_payload = {
        "interests_count": len(payload.get("interests", [])),
        "top": payload.get("top", 0),
        # Don't log: user_id, session titles, tags
    }
    telemetry.log(action, safe_payload)
```

2. **Anonymize exports:**

```python
def anonymize_session(session):
    return {
        "id": hashlib.sha256(session["id"].encode()).hexdigest()[:8],
        "title": "[REDACTED]",
        "tags": ["[REDACTED]"],
        # Keep only structural data
        "start": session["start"],
        "end": session["end"]
    }
```

3. **Access controls:**

```bash
# Restrict telemetry file access
chmod 600 telemetry.jsonl
chown appuser:appuser telemetry.jsonl
```

## Compliance & Governance

### Policy Surface

**Feature flags control capability exposure:**

```json
{
    "features": {
        "externalSessions": {
            "enabled": false,  // Disable external data ingestion
            "file": "sessions_external.json"
        },
        "export": {
            "enabled": true,   // Enable itinerary export
            "formats": ["markdown", "json"]
        },
        "graphApi": {
            "enabled": false   // Disable Graph API integration
        }
    }
}
```

**Governance use cases:**

- **Data residency:** Disable external sessions to keep data local
- **Compliance:** Disable export for internal-only use
- **Security:** Disable Graph API in air-gapped environments

### Audit Trail

**Telemetry provides complete audit trail:**

```json
{
    "ts": 1732540000.123,
    "action": "recommend",
    "success": true,
    "latency_ms": 12.5,
    "payload": {
        "interests_count": 3,
        "top": 5,
        "source": "manifest"
    }
}
```

**Audit queries:**

```bash
# Who accessed the system?
jq 'select(.action == "recommend") | .payload.user_id' telemetry.jsonl | sort | uniq

# What was recommended?
jq 'select(.action == "recommend") | .payload.interests_count' telemetry.jsonl | stats

# When were errors encountered?
jq 'select(.success == false)' telemetry.jsonl
```

### Compliance Hooks

**Export review workflow:**

```bash
#!/bin/bash
# export_with_review.sh

# Generate export
python agent.py export --interests "ai, ml" --top 5 --output draft.md

# Attach telemetry summary
python scripts/summarize_telemetry.py >> draft.md

# Send for review
cat draft.md | mail -s "Export for Review" compliance@example.com

# Wait for approval
echo "Waiting for approval..."
read -p "Approved? (y/n): " approved

if [ "$approved" = "y" ]; then
    # Distribute
    cp draft.md final.md
    echo "Export approved and distributed"
else
    echo "Export rejected"
    rm draft.md
fi
```

### Data Retention

**Telemetry retention policy:**

```bash
#!/bin/bash
# retention_policy.sh

# Compress logs older than 7 days
find . -name "telemetry.*.jsonl" -mtime +7 -exec gzip {} \;

# Delete compressed logs older than 90 days
find . -name "telemetry.*.jsonl.gz" -mtime +90 -delete

# Archive to secure storage
aws s3 cp telemetry.*.jsonl.gz s3://audit-logs/event-agent/
```

### Change Management

**Track configuration changes in version control:**

```bash
# Track manifest changes
git add agent.json
git commit -m "Adjust popularity weight from 0.5 to 0.8"

# Track feature flag changes
git add agent.json
git commit -m "Disable external sessions for compliance"

# Maintain CHANGELOG.md
echo "## 2024-03-15\n- Adjusted weights for better diversity\n- Disabled external sessions\n" >> CHANGELOG.md
git add CHANGELOG.md
git commit -m "Update changelog"
```

**Review process:**

1. Propose change via PR
2. Review by security/compliance team
3. Test in staging environment
4. Deploy to production with rollback plan
5. Monitor telemetry for anomalies

## Security Best Practices

### Network Security

- ✅ **Use HTTPS in production** — Encrypt traffic with TLS
- ✅ **Firewall rules** — Allow only necessary ports (443, not 8000)
- ✅ **Reverse proxy** — Use nginx/Apache as frontend
- ✅ **Rate limiting** — Prevent DOS attacks
- ✅ **IP whitelisting** — Restrict access to known IPs (if applicable)

**nginx security headers:**

```nginx
server {
    # ... TLS config ...
    
    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header Content-Security-Policy "default-src 'self'" always;
    
    # Hide server version
    server_tokens off;
}
```

### Application Security

- ✅ **No code execution** — Interests are plain text only
- ✅ **Input validation** — Validate all user inputs
- ✅ **Output encoding** — Escape HTML in responses
- ✅ **Error handling** — Don't leak stack traces to users
- ✅ **Logging** — Log security events (auth failures, etc.)

**Error handling:**

```python
try:
    result = recommend(manifest, interests, top)
    return {"success": True, "data": result}
except Exception as e:
    # Log error with details (internal)
    logger.error(f"Recommendation failed: {e}", exc_info=True)
    
    # Return generic error (external)
    return {"success": False, "error": "Internal server error"}
```

### Dependency Security

**Scan for vulnerabilities:**

```bash
# Install safety
pip install safety

# Scan dependencies
safety check --json
```

**Update dependencies regularly:**

```bash
# Update to latest secure versions
pip list --outdated
pip install --upgrade <package>
```

**Pin versions in requirements.txt:**

```txt
pydantic-settings==2.1.0
msal==1.26.0
msgraph-core==1.0.0
pytest==7.4.3
```

### Container Security

**Non-root user:**

```dockerfile
# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

**Minimal base image:**

```dockerfile
# Use slim Python image
FROM python:3.11-slim

# Install only required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

**Scan for vulnerabilities:**

```bash
# Scan with Trivy
trivy image event-agent:latest

# Scan with Snyk
snyk container test event-agent:latest
```

## Incident Response

### Security Incident Workflow

```text
1. Detect — Monitor logs/telemetry for anomalies
2. Contain — Disable affected features/endpoints
3. Investigate — Analyze logs, identify root cause
4. Remediate — Patch vulnerability, rotate secrets
5. Review — Post-mortem, improve defenses
```

### Monitoring for Threats

**Failed authentication attempts:**

```bash
# Count failed auth attempts
jq 'select(.action == "auth" and .success == false)' telemetry.jsonl | wc -l
```

**Unusual activity:**

```bash
# Detect spikes in requests
jq -r '.ts' telemetry.jsonl | \
    xargs -I{} date -d @{} +%Y-%m-%d_%H | \
    sort | uniq -c | \
    awk '$1 > 1000 {print "Spike detected: " $0}'
```

**Large parameter values:**

```bash
# Detect DOS attempts
jq 'select(.payload.top > 50)' telemetry.jsonl
```

### Secrets Rotation

**Rotate Graph API client secret:**

1. Create new secret in Azure Portal
2. Update `.env` with new secret
3. Restart service
4. Verify authentication works
5. Delete old secret from Azure Portal

**Rotate API token:**

```bash
# Generate new token
NEW_TOKEN=$(openssl rand -base64 32)

# Update .env
echo "API_TOKEN=$NEW_TOKEN" >> .env

# Restart service
sudo systemctl restart event-agent

# Notify API consumers
echo "API token rotated on $(date)" | mail -s "Action Required" api-users@example.com
```

## Next Steps

- 🚀 [Deployment Guide](deployment.md) — Production deployment patterns
- 📊 [Performance Guide](performance.md) — Optimization strategies
- 📈 [Monitoring Guide](monitoring.md) — Observability setup
- 🏗️ [Architecture](../04-ARCHITECTURE/design.md) — System design overview
