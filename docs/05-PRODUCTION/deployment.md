# Deployment Guide

Production deployment options for Event Kit.

## Overview

Event Kit supports multiple deployment patterns:

| Pattern | Use Case | Complexity | Scalability |
|---------|----------|------------|-------------|
| **Standalone** | Development, testing | Low | Single server |
| **Containerized** | Production, cloud | Medium | Horizontal |
| **System Service** | Always-on server | Medium | Single server |
| **Serverless** | Event-driven | High | Auto-scale |

## Prerequisites

### System Requirements

- **OS:** Linux, macOS, or Windows
- **Python:** 3.8 or higher
- **Memory:** 512MB minimum, 2GB recommended
- **Disk:** 1GB minimum (logs can grow)
- **Network:** HTTPS access for Graph API (if used)

### Dependencies

```bash
# Core dependencies
pip install pydantic-settings

# Graph API (optional)
pip install msal msgraph-core

# Testing (development only)
pip install pytest pytest-cov
```

## Deployment Pattern 1: Standalone

**Use case:** Development, testing, local deployments.

### Setup

```bash
# Clone or copy application
cd event-agent-example

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Run CLI

```bash
python agent.py recommend --interests "ai, ml" --top 5
```

### Run HTTP Server

```bash
python agent.py serve --port 8000
```

**Access:** `http://localhost:8000/health`

### Pros & Cons

✅ **Pros:**

- Simple setup
- Easy debugging
- No containerization overhead

❌ **Cons:**

- Manual start/stop
- No auto-restart on failure
- Environment-dependent

## Deployment Pattern 2: Containerized (Docker)

**Use case:** Production, cloud deployments, consistent environments.

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY agent.py core.py settings.py telemetry.py ./
COPY agent.json .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose HTTP port
EXPOSE 8000

# Run server
CMD ["python", "agent.py", "serve", "--port", "8000"]
```

### Build Image

```bash
docker build -t event-agent:latest .
```

### Run Container

```bash
docker run -d \
    --name event-agent \
    -p 8000:8000 \
    -e TENANT_ID="your-tenant-id" \
    -e CLIENT_ID="your-client-id" \
    -e CLIENT_SECRET="your-secret" \
    -e DEFAULT_USER_ID="user@example.com" \
    -v $(pwd)/telemetry.jsonl:/app/telemetry.jsonl \
    -v $(pwd)/.msal_token_cache.bin:/home/appuser/.msal_token_cache.bin \
    event-agent:latest
```

### Docker Compose

For multi-container deployments:

```yaml
version: '3.8'

services:
  event-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TENANT_ID=${TENANT_ID}
      - CLIENT_ID=${CLIENT_ID}
      - CLIENT_SECRET=${CLIENT_SECRET}
      - DEFAULT_USER_ID=${DEFAULT_USER_ID}
      - API_TOKEN=${API_TOKEN}
    volumes:
      - ./telemetry.jsonl:/app/telemetry.jsonl
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - event-agent
```

### Nginx Reverse Proxy

`nginx.conf`:

```nginx
http {
    upstream event_agent {
        server event-agent:8000;
    }

    server {
        listen 80;
        server_name events.example.com;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name events.example.com;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;

        location / {
            proxy_pass http://event_agent;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            access_log off;
            proxy_pass http://event_agent/health;
        }
    }
}
```

### Start with Compose

```bash
docker-compose up -d
```

### Pros & Cons

✅ **Pros:**

- Consistent environment
- Easy to scale horizontally
- Isolated dependencies
- Works on any platform

❌ **Cons:**

- Docker overhead (~100MB)
- Requires Docker knowledge
- Volume management needed

## Deployment Pattern 3: System Service (systemd)

**Use case:** Always-on server, Linux production deployments.

### Setup

```bash
# Install to /opt
sudo mkdir -p /opt/event-agent
sudo cp -r * /opt/event-agent/
cd /opt/event-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
sudo cp .env.example .env
sudo nano .env  # Edit with your settings
```

### Create Service Unit

`/etc/systemd/system/event-agent.service`:

```ini
[Unit]
Description=Event Kit Agent
After=network.target

[Service]
Type=simple
User=nobody
Group=nogroup
WorkingDirectory=/opt/event-agent
Environment="PATH=/opt/event-agent/venv/bin"
ExecStart=/opt/event-agent/venv/bin/python agent.py serve --port 8000
Restart=on-failure
RestartSec=10s

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/event-agent/telemetry.jsonl
ReadWritePaths=/opt/event-agent/.msal_token_cache.bin

[Install]
WantedBy=multi-user.target
```

### Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable event-agent

# Start service
sudo systemctl start event-agent

# Check status
sudo systemctl status event-agent
```

### Log Management

```bash
# View logs
sudo journalctl -u event-agent -f

# Rotate logs
sudo journalctl --vacuum-time=7d
```

### Pros & Cons

✅ **Pros:**

- Auto-start on boot
- Auto-restart on failure
- systemd logging integration
- Security hardening

❌ **Cons:**

- Linux-only
- Manual deployment steps
- Requires root access

## Deployment Pattern 4: Serverless (Azure Functions)

**Use case:** Event-driven, auto-scaling, pay-per-use.

### Setup

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Create function app
func init EventAgentApp --python
cd EventAgentApp
```

### Function Code

`function_app.py`:

```python
import azure.functions as func
import json
import logging
from agent import recommend, load_manifest

app = func.FunctionApp()

@app.route(route="recommend", auth_level=func.AuthLevel.FUNCTION)
def recommend_handler(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Recommend function triggered')

    try:
        # Parse request
        body = req.get_json()
        interests = body.get('interests', [])
        top = body.get('top', 5)

        # Load manifest
        manifest = load_manifest()

        # Generate recommendations
        result = recommend(manifest, interests, top)

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
```

### Deploy

```bash
# Login to Azure
az login

# Create resource group
az group create --name EventAgentRG --location eastus

# Create storage account
az storage account create \
    --name eventagentstorage \
    --resource-group EventAgentRG \
    --location eastus \
    --sku Standard_LRS

# Create function app
az functionapp create \
    --resource-group EventAgentRG \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --name event-agent-app \
    --storage-account eventagentstorage

# Deploy function
func azure functionapp publish event-agent-app
```

### Configure Environment

```bash
# Set environment variables
az functionapp config appsettings set \
    --name event-agent-app \
    --resource-group EventAgentRG \
    --settings \
        TENANT_ID="your-tenant-id" \
        CLIENT_ID="your-client-id" \
        CLIENT_SECRET="your-secret" \
        DEFAULT_USER_ID="user@example.com"
```

### Pros & Cons

✅ **Pros:**

- Auto-scaling
- Pay-per-use
- Managed infrastructure
- Azure integration

❌ **Cons:**

- Cold start latency (~1-2s)
- Azure-specific
- More complex setup
- Limited customization

## Production Hardening

### HTTPS / TLS

**Nginx with Let's Encrypt:**

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d events.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### API Authentication

Enable bearer token authentication:

```bash
# Set API_TOKEN in .env
API_TOKEN="your-secret-token-here"
```

**Request with auth:**

```bash
curl -H "Authorization: Bearer your-secret-token-here" \
    http://localhost:8000/recommend \
    -d '{"interests": ["ai"], "top": 5}'
```

### Rate Limiting

Use nginx rate limiting:

```nginx
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://event_agent;
        }
    }
}
```

### Monitoring

**Health check endpoint:**

```bash
# Check service health
curl http://localhost:8000/health
```

**Response:**

```json
{
    "status": "healthy",
    "timestamp": "2024-03-15T08:30:00Z"
}
```

**Uptime monitoring:**

```bash
# Add to cron
*/5 * * * * curl -f http://localhost:8000/health || echo "Service down" | mail admin@example.com
```

### Backup

**Backup telemetry and profiles:**

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/event-agent"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup telemetry
cp telemetry.jsonl $BACKUP_DIR/telemetry_$DATE.jsonl

# Backup profiles
cp ~/.event_agent_profiles.json $BACKUP_DIR/profiles_$DATE.json

# Backup manifest
cp agent.json $BACKUP_DIR/agent_$DATE.json

# Compress old backups
find $BACKUP_DIR -name "*.jsonl" -mtime +7 -exec gzip {} \;

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

**Schedule backup:**

```cron
0 2 * * * /path/to/backup.sh
```

## Scaling Strategies

### Horizontal Scaling

**Load balancer + multiple instances:**

```text
                   ┌──> Instance 1 (8001)
Load Balancer ────┼──> Instance 2 (8002)
                   └──> Instance 3 (8003)
```

**Docker Compose with replicas:**

```yaml
services:
  event-agent:
    build: .
    deploy:
      replicas: 3
    ports:
      - "8001-8003:8000"
```

**Nginx load balancer:**

```nginx
upstream event_agent_cluster {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    location / {
        proxy_pass http://event_agent_cluster;
    }
}
```

### Vertical Scaling

**Increase server resources:**

- CPU: 2+ cores for concurrent requests
- Memory: 2-4GB for large session sets
- Disk: SSD for faster I/O

### Caching

**Add Redis cache layer:**

```python
import redis
import json
import hashlib

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

def recommend_cached(manifest, interests, top):
    # Generate cache key
    key = hashlib.md5(
        f"{interests}:{top}".encode()
    ).hexdigest()
    
    # Check cache
    cached = cache.get(key)
    if cached:
        return json.loads(cached)
    
    # Compute result
    result = recommend(manifest, interests, top)
    
    # Cache for 5 minutes
    cache.setex(key, 300, json.dumps(result))
    
    return result
```

## Troubleshooting

### Service Won't Start

**Check logs:**

```bash
# systemd
sudo journalctl -u event-agent -n 50

# Docker
docker logs event-agent
```

**Common issues:**

- Missing `.env` file
- Invalid credentials
- Port already in use
- File permissions

### High Memory Usage

**Check process memory:**

```bash
ps aux | grep python
```

**Solutions:**

- Reduce session count
- Enable external sessions with file-based storage
- Increase swap space
- Upgrade server RAM

### Slow Responses

**Check latency:**

```bash
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/recommend
```

**Solutions:**

- Enable caching
- Optimize scoring (pre-indexing)
- Add more CPU cores
- Use WSGI server (Gunicorn)

## Next Steps

- 📊 [Performance Guide](performance.md) — Optimization strategies
- 🔒 [Security Guide](security.md) — Security best practices
- 📈 [Monitoring Guide](monitoring.md) — Observability setup
- 🏗️ [Architecture](../04-ARCHITECTURE/design.md) — System design
