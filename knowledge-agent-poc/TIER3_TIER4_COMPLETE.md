# Tier 3 & 4 Implementation Guide

**Status**: ✅ Complete - Azure AI Foundry & Power Platform Integrations
**Date**: December 18, 2025

---

## 📦 New Files Created

### Tier 3: Azure AI Foundry

| File | Lines | Purpose |
|------|-------|---------|
| `integrations/foundry_provider.py` | ~230 | LLM provider using Foundry models |
| `integrations/foundry_integration.py` | ~400 | Tool registration, deployment, monitoring |

### Tier 4: Power Platform

| File | Lines | Purpose |
|------|-------|---------|
| `integrations/power_platform_connector.py` | ~600 | REST API for Power Automate, Apps, BI |

### Configuration

| File | Lines | Purpose |
|------|-------|---------|
| `integrations/extended_settings.py` | ~350 | Unified settings for all integrations |
| `integrations/__init__.py` | ~55 | Updated exports (now includes all 3 tiers) |

**Total New Code**: ~1,635 lines across 4 files

---

## 🎯 Tier 3: Azure AI Foundry Integration

### What It Does

**Foundry Provider** (`foundry_provider.py`):
- Seamless LLM provider integration
- Use Foundry-deployed models (gpt-4-turbo, gpt-4o, phi-3, mistral)
- Automatic model selection by artifact type
- Token caching and request optimization

**Example - Use Foundry Model**:
```python
from integrations import create_foundry_provider

# Create provider
provider = create_foundry_provider(
    project_connection_string="your-foundry-connection-string",
    artifact_type="paper"  # Auto-selects gpt-4-turbo
)

# Use in extraction
result = await provider.extract(
    system_prompt="Extract research paper metadata...",
    user_prompt="<paper content here>",
    temperature=0.3
)
```

### Foundry Integration Features

**Agent Registration** (`foundry_integration.py`):
- Register all extraction tools in Foundry project
- Create agentic apps with full capabilities
- Set up monitoring and tracing
- Configure auto-scaling deployments

**Example - Deploy to Foundry**:
```python
from integrations import FoundryAgentIntegration

integration = FoundryAgentIntegration(
    project_connection_string="your-connection-string"
)

# Register tools
tools = integration.register_extraction_tools()

# Create agent
agent_config = integration.create_foundry_agent(
    enable_monitoring=True,
    enable_tracing=True
)

# Get deployment config
deploy_config = integration.get_deployment_config(
    replicas=3,
    cpu="2",
    memory="8G"
)
```

### Quality Evaluation

**Foundry Evaluation** (`foundry_integration.py`):
- Built-in quality metrics (coherence, groundedness, relevance, accuracy)
- Single extraction evaluation
- Batch evaluation with aggregation
- Performance summaries and trends

**Example - Evaluate Extractions**:
```python
from integrations import FoundryEvaluation

evaluation = FoundryEvaluation(
    project_connection_string="your-connection-string"
)

# Evaluate one extraction
result = evaluation.evaluate_extraction(
    artifact_id="paper_123",
    extracted_content="Generated abstract...",
    source_content="Original paper...",
    metrics=["coherence", "groundedness", "relevance", "accuracy"]
)

# Evaluate batch
batch_results = evaluation.batch_evaluate(extractions=[...])

# Get performance dashboard
performance = evaluation.get_performance_summary(time_range_days=30)
```

---

## 📱 Tier 4: Power Platform Integration

### What It Does

**Power Automate** - REST API endpoints for workflow automation
**Power Apps** - Data APIs for custom applications
**Power BI** - Analytics endpoints for dashboards

### Power Automate Connector

**Main Endpoint**:
```
POST /extract
{
  "artifact_type": "paper",
  "source_location": "/path/to/file.pdf",
  "save_results": true,
  "notify_teams": true
}
```

**Response**:
```json
{
  "success": true,
  "title": "Research Paper Title",
  "confidence": 0.88,
  "overview": "Plain language summary...",
  "artifact_url": "https://storage/artifact.json",
  "extraction_time_seconds": 12.5
}
```

**SharePoint Integration**:
```python
# From Power Automate flow
POST /extract-from-sharepoint
{
  "site_id": "site-123",
  "file_path": "/Research/paper.pdf",
  "notify_teams": true,
  "team_id": "team-456",
  "channel_id": "channel-789"
}
```

**OneDrive Integration**:
```python
# From Power Automate flow
POST /extract-from-onedrive
{
  "file_path": "/Documents/talk_transcript.txt"
}
```

### Power Apps API

**List Artifacts**:
```python
GET /artifacts?limit=100&offset=0

Response:
{
  "items": [
    {
      "id": "artifact_1",
      "title": "Sample Paper",
      "overview": "Abstract...",
      "confidence": 0.89,
      "source_type": "paper",
      "extraction_date": "2025-12-18T..."
    }
  ],
  "total": 1250,
  "hasMore": true
}
```

**Get Single Artifact**:
```python
GET /artifacts/{artifact_id}

Response:
{
  "id": "artifact_123",
  "title": "Full Title",
  "overview": "...",
  "methods": ["Method 1", "Method 2"],
  "impact": "...",
  "confidence": 0.88,
  "source": { ... },
  "extraction_metadata": { ... }
}
```

**Search**:
```python
GET /search?query=machine+learning&limit=20

Response:
{
  "query": "machine learning",
  "total_results": 45,
  "results": [
    {
      "id": "result_1",
      "title": "Result Title",
      "snippet": "Matching text...",
      "confidence": 0.92,
      "relevance_score": 0.88
    }
  ]
}
```

**Submit Feedback**:
```python
POST /artifacts/{artifact_id}/feedback
{
  "rating": 4,
  "comment": "Good extraction but missing key methods",
  "suggested_improvements": ["Include methodology section", "Add future work"]
}
```

### Power BI Analytics

**Summary Metrics**:
```python
GET /analytics/summary

Response:
{
  "total_extractions": 1250,
  "successful_extractions": 1198,
  "success_rate": 0.958,
  "average_confidence": 0.87,
  "by_type": {
    "paper": { "count": 450, "success_rate": 0.96, "avg_confidence": 0.89 },
    "talk": { "count": 550, "success_rate": 0.95, "avg_confidence": 0.85 },
    "repository": { "count": 250, "success_rate": 0.97, "avg_confidence": 0.86 }
  }
}
```

**Quality Metrics**:
```python
GET /analytics/quality

Response:
{
  "metrics": {
    "coherence": 0.87,
    "groundedness": 0.92,
    "relevance": 0.89,
    "accuracy": 0.91,
    "completeness": 0.84
  },
  "by_model": {
    "gpt-4-turbo": { "score": 0.92, "count": 800 },
    "gpt-4o": { "score": 0.89, "count": 300 }
  }
}
```

**Export Data**:
```python
GET /analytics/export?format=json
# or
GET /analytics/export?format=csv
```

---

## ⚙️ Configuration

### Extended Settings

**New `extended_settings.py`** provides unified configuration:

```python
from integrations import get_settings

settings = get_settings()

# Check what's enabled
print(settings.get_active_providers())
# Output: ['foundry', 'foundry-evaluation', 'm365', 'power-automate', 'power-apps', 'power-bi']

print(settings.get_integration_tier())
# Output: 'full-enterprise'

print(settings.get_capability_summary())
# Output: {
#   'extraction': {'local': True, 'sharepoint': True, ...},
#   'llm': {'provider': 'azure-ai-foundry', ...},
#   ...
# }

# Validate all configs
settings.validate_all()

# Print summary
settings.print_summary()
```

### Environment Variables

**Tier 3: Azure AI Foundry**
```bash
FOUNDRY_ENABLED=true
FOUNDRY_CONNECTION_STRING=your-connection-string
FOUNDRY_MODEL=gpt-4-turbo
FOUNDRY_TRACING=true
FOUNDRY_MONITORING=true
FOUNDRY_EVALUATION=true
LLM_PROVIDER=azure-ai-foundry
```

**Tier 4: Power Platform**
```bash
POWER_PLATFORM_ENABLED=true
POWER_AUTOMATE_ENDPOINT=https://your-endpoint
POWER_APPS_ENABLED=true
POWER_BI_ENABLED=true
```

**Deployment**
```bash
INTEGRATION_MODE=full-enterprise
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=false
LOG_LEVEL=INFO
```

### .env Template

```bash
# ===== LLM Configuration =====
LLM_PROVIDER=azure-ai-foundry
LLM_MODEL=gpt-4-turbo
LLM_TEMPERATURE=0.3

# ===== Azure AI Foundry =====
FOUNDRY_ENABLED=true
FOUNDRY_CONNECTION_STRING=your-foundry-connection-string
FOUNDRY_MODEL=gpt-4-turbo
FOUNDRY_TRACING=true
FOUNDRY_MONITORING=true
FOUNDRY_EVALUATION=true

# ===== Power Platform =====
POWER_PLATFORM_ENABLED=true
POWER_AUTOMATE_ENDPOINT=https://your-region.logic.azure.com/workflows/
POWER_APPS_ENABLED=true
POWER_BI_ENABLED=true

# ===== Microsoft 365 =====
M365_ENABLED=true
M365_TENANT_ID=your-tenant-id
M365_CLIENT_ID=your-client-id
M365_CLIENT_SECRET=your-client-secret

# ===== Deployment =====
INTEGRATION_MODE=full-enterprise
API_PORT=8000
API_HOST=0.0.0.0
OUTPUT_DIR=./outputs
DEBUG=false
```

---

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install azure-ai-projects azure-identity fastapi uvicorn

# Set environment
cp .env.example .env
# Edit .env with your credentials

# Run with all features
python knowledge_agent_bot.py --m365 --foundry

# Run Power Platform connector
python -m integrations.power_platform_connector
```

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements*.txt ./
RUN pip install -r requirements.txt
RUN pip install azure-ai-projects azure-identity fastapi uvicorn

COPY . .

ENV INTEGRATION_MODE=full-enterprise
EXPOSE 8000

CMD ["python", "-m", "integrations.power_platform_connector"]
```

```bash
# Build and run
docker build -t knowledge-agent:latest .
docker run -p 8000:8000 \
  -e FOUNDRY_CONNECTION_STRING=$FOUNDRY_CONNECTION_STRING \
  -e M365_TENANT_ID=$M365_TENANT_ID \
  knowledge-agent:latest
```

### Azure Container Instances

```bash
az containerapp up \
  --name knowledge-agent \
  --resource-group my-rg \
  --environment my-env \
  --image knowledge-agent:latest \
  --env-vars \
    FOUNDRY_ENABLED=true \
    FOUNDRY_CONNECTION_STRING=$FOUNDRY_CONNECTION_STRING \
    POWER_PLATFORM_ENABLED=true \
    M365_ENABLED=true \
  --target-port 8000 \
  --ingress external
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: knowledge-agent
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: knowledge-agent
  template:
    metadata:
      labels:
        app: knowledge-agent
    spec:
      containers:
      - name: agent
        image: your-registry/knowledge-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: FOUNDRY_ENABLED
          value: "true"
        - name: FOUNDRY_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: foundry-connection
        - name: POWER_PLATFORM_ENABLED
          value: "true"
        - name: M365_ENABLED
          value: "true"
        - name: M365_TENANT_ID
          valueFrom:
            secretKeyRef:
              name: m365-secrets
              key: tenant-id
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

---

## 💡 Integration Patterns

### Pattern 1: Local → Foundry (Model Upgrade)

```python
from integrations import get_settings, create_foundry_provider

settings = get_settings()

# Switch to Foundry for high-volume production
if settings.foundry_enabled:
    llm_provider = create_foundry_provider(
        project_connection_string=settings.foundry_connection_string,
        artifact_type="paper"
    )
else:
    # Fall back to default
    llm_provider = get_default_provider()

# Rest of code uses same interface
result = agent.extract_with_provider(llm_provider, content)
```

### Pattern 2: Trigger Power Automate from SharePoint

```
SharePoint Library
  ↓ (file uploaded)
  ↓ (trigger)
Power Automate Flow
  ↓ (call)
  ↓ POST /extract-from-sharepoint
Power Platform Connector
  ↓ (extract)
  ↓ (save)
Knowledge Artifacts Library (SharePoint)
  ↓ (notify)
  ↓
Teams Channel
```

### Pattern 3: Analytics Pipeline

```
Extraction → Evaluation (Foundry)
  ↓
Quality Scores → Power BI Dataset
  ↓
Live Dashboard
  ↓
Feedback from Power Apps
  ↓
Continuous Improvement Loop
```

---

## ✅ Validation Checklist

- [ ] Install dependencies: `pip install azure-ai-projects fastapi uvicorn`
- [ ] Set environment variables in .env
- [ ] Validate Foundry connection: `settings.validate_foundry_config()`
- [ ] Validate M365 config: `settings.validate_m365_config()`
- [ ] Test Foundry provider: `create_foundry_provider(...)`
- [ ] Test Power Platform connector: `uvicorn integrations.power_platform_connector:app`
- [ ] Check /health endpoint: `curl http://localhost:8000/health`
- [ ] Check /schema endpoint: `curl http://localhost:8000/schema`

---

## 🔗 Integration Tiers Summary

| Tier | Features | Use Case | Files |
|------|----------|----------|-------|
| **1: Local** | Extract from local files | Development | Core agents |
| **2: M365** | + SharePoint, OneDrive, Teams | Teams enterprise | m365_* files |
| **3: Foundry** | + Foundry models, monitoring, evaluation | Production scale | foundry_* files |
| **4: Power** | + Power Automate, Apps, BI | Full enterprise | power_* files |

All tiers are **optional and coexist**! 🎯

---

## 📚 Next Steps

1. **Test Foundry Model**:
   ```bash
   python -c "from integrations import create_foundry_provider; p = create_foundry_provider('your-conn-str'); print(p.get_model_info())"
   ```

2. **Launch Power Platform Connector**:
   ```bash
   python -m integrations.power_platform_connector
   ```

3. **Create Power Automate Flow**:
   - Go to power.microsoft.com
   - Create Cloud Flow → Instant Cloud Flow
   - Add action "HTTP" → POST to your connector

4. **Build Power Apps UI**:
   - Create Canvas App
   - Connect to `/artifacts` endpoint
   - Build gallery of artifacts

5. **Set up Power BI Dashboard**:
   - Import data from `/analytics/export`
   - Create visualizations
   - Pin to dashboard

---

**Build Status**: ✅ Complete
**Files Created**: 4 new, 1 updated
**Total Lines**: ~1,635 new code
**Dependencies Added**: azure-ai-projects, fastapi, uvicorn
**Next Milestone**: Testing & Production Deployment
