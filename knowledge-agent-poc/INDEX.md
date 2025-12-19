# Knowledge Agent - Complete Integration Suite

**Status**: ✅ Production Ready
**Last Updated**: December 18, 2025
**Version**: 2.0 (Full Enterprise Edition)

---

## 🎯 Quick Navigation

### 📖 Documentation
- **[README.md](README.md)** - Project overview
- **[OPTIONAL_INTEGRATIONS.md](OPTIONAL_INTEGRATIONS.md)** - Architecture & concepts
- **[BUILD_COMPLETE.md](BUILD_COMPLETE.md)** - Full build summary ⭐ START HERE

### 🏢 Tier-by-Tier Guides
- **[BOT_INTEGRATION.md](BOT_INTEGRATION.md)** - Bot Framework setup
- **[M365_QUICKSTART.md](M365_QUICKSTART.md)** - SharePoint/OneDrive guide
- **[M365_BUILD_COMPLETE.md](M365_BUILD_COMPLETE.md)** - M365 implementation
- **[TIER3_TIER4_COMPLETE.md](TIER3_TIER4_COMPLETE.md)** - Foundry & Power Platform ⭐
- **[TIER3_TIER4_SUMMARY.md](TIER3_TIER4_SUMMARY.md)** - Quick reference

### 💻 Code Examples
- **[tier3_tier4_examples.py](tier3_tier4_examples.py)** - 12 working examples ⭐
- **[m365_examples.py](m365_examples.py)** - M365 integration examples
- **[examples.py](examples.py)** - Basic extraction examples

### 🔍 Verification & Testing
- **[verify_tier3_tier4.py](verify_tier3_tier4.py)** - Tier 3/4 validation ⭐
- **[test_extraction.py](tests/test_extraction.py)** - Unit tests

---

## 🚀 5-Minute Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-tier3-tier4.txt  # For Tier 3 & 4
```

### 2. Configure
```bash
cp .env.example .env
# Edit with your credentials (optional for tiers 3 & 4)
```

### 3. Verify
```bash
python verify_tier3_tier4.py
# ✅ TIER 3 & 4 INTEGRATION READY FOR PRODUCTION
```

### 4. Run Examples
```bash
python tier3_tier4_examples.py
# Outputs all 12 examples
```

### 5. Start API
```bash
python -m integrations.power_platform_connector
# Listening on http://localhost:8000
# Test: curl http://localhost:8000/health
```

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│          KNOWLEDGE EXTRACTION AGENT ECOSYSTEM                │
│                  (4 Integration Tiers)                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ TIER 1: LOCAL (Always Available)                   │   │
│  │ • PaperAgent - PDF extraction                      │   │
│  │ • TalkAgent - Transcript analysis                  │   │
│  │ • RepositoryAgent - Code analysis                 │   │
│  │ Files: agents/, core/, prompts/                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                        ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ TIER 2: MICROSOFT 365 (Optional)                   │   │
│  │ • SharePoint document extraction                   │   │
│  │ • OneDrive file access                             │   │
│  │ • Teams notifications                              │   │
│  │ Files: integrations/m365_*                         │   │
│  │ Requires: M365_ENABLED=true                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                        ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ TIER 3: AZURE AI FOUNDRY (Optional)                │   │
│  │ • Foundry model support (4 models)                 │   │
│  │ • Quality evaluation (6 metrics)                   │   │
│  │ • Performance monitoring                           │   │
│  │ Files: integrations/foundry_*                      │   │
│  │ Requires: FOUNDRY_ENABLED=true                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                        ↓                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ TIER 4: POWER PLATFORM (Optional)                  │   │
│  │ • Power Automate workflows                         │   │
│  │ • Power Apps custom UI                             │   │
│  │ • Power BI analytics dashboard                     │   │
│  │ Files: integrations/power_platform_*               │   │
│  │ Requires: POWER_PLATFORM_ENABLED=true              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  All layers optionally enabled via:                         │
│  • .env configuration                                       │
│  • integrations/extended_settings.py                        │
│  • Unified interface                                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📦 Integration Modules

### Core Tier 1 (Local)
| Module | Purpose |
|--------|---------|
| `agents/` | PaperAgent, TalkAgent, RepositoryAgent |
| `core/` | Base schemas, extraction pipeline |
| `prompts/` | Prompt engineering templates |
| `knowledge_agent_bot.py` | Conversational interface |

### Tier 2 (Microsoft 365)
| Module | Purpose |
|--------|---------|
| `integrations/m365_connector.py` | SharePoint, OneDrive, Teams API |
| `integrations/m365_schemas.py` | M365 metadata structures |

### Tier 3 (Azure AI Foundry) ⭐ NEW
| Module | Purpose |
|--------|---------|
| `integrations/foundry_provider.py` | LLM provider for Foundry models |
| `integrations/foundry_integration.py` | Agent registration, evaluation, monitoring |

### Tier 4 (Power Platform) ⭐ NEW
| Module | Purpose |
|--------|---------|
| `integrations/power_platform_connector.py` | REST API for Power Automate/Apps/BI |

### Configuration (Tier 3 & 4) ⭐ NEW
| Module | Purpose |
|--------|---------|
| `integrations/extended_settings.py` | Unified configuration system |

---

## 🔧 Features by Tier

### Tier 1: Local
- ✅ Extract from PDFs, TXT, DOCX, MD
- ✅ 3 specialized extraction agents
- ✅ JSON artifact output
- ✅ CLI interface
- ✅ Local file storage

### Tier 2: M365
- ✅ Everything in Tier 1 +
- ✅ SharePoint document extraction
- ✅ OneDrive file access
- ✅ Teams channel notifications
- ✅ M365 storage integration
- ✅ OAuth 2.0 token management

### Tier 3: Foundry
- ✅ Everything in Tiers 1-2 +
- ✅ Foundry LLM model support
- ✅ 4 model options (gpt-4-turbo, gpt-4o, phi-3, mistral)
- ✅ Quality evaluation (6 metrics)
- ✅ Batch processing
- ✅ Performance monitoring & trends
- ✅ Model auto-selection

### Tier 4: Power Platform
- ✅ Everything in Tiers 1-3 +
- ✅ Power Automate workflows
- ✅ Power Apps data API
- ✅ Power BI analytics endpoints
- ✅ REST API with 12+ endpoints
- ✅ Data export (JSON/CSV)

---

## 📋 Environment Configuration

### Minimal (.env)
```bash
# Just Tier 1 - works out of the box
```

### Tier 2: M365
```bash
M365_ENABLED=true
M365_TENANT_ID=your-tenant-id
M365_CLIENT_ID=your-client-id
M365_CLIENT_SECRET=your-secret
```

### Tier 3: Foundry
```bash
FOUNDRY_ENABLED=true
FOUNDRY_CONNECTION_STRING=your-connection-string
FOUNDRY_MODEL=gpt-4-turbo
FOUNDRY_TRACING=true
LLM_PROVIDER=azure-ai-foundry
```

### Tier 4: Power Platform
```bash
POWER_PLATFORM_ENABLED=true
POWER_APPS_ENABLED=true
POWER_BI_ENABLED=true
API_PORT=8000
```

### Full Enterprise
```bash
INTEGRATION_MODE=full-enterprise
# Plus all of above
```

See `.env.example` for complete template.

---

## 🎓 Use Cases

### Use Case 1: Local Development
```bash
# Tier 1 only
python knowledge_agent_bot.py
python examples.py
```

### Use Case 2: Enterprise Teams
```bash
# Tier 1 + 2
M365_ENABLED=true python knowledge_agent_bot.py --m365
# Users upload to SharePoint → Automatic extraction → Teams notifications
```

### Use Case 3: High-Volume Production
```bash
# Tier 1 + 2 + 3
FOUNDRY_ENABLED=true INTEGRATION_MODE=full-enterprise python knowledge_agent_bot.py --m365
# Uses Foundry models, evaluates quality, tracks metrics
```

### Use Case 4: Business Intelligence
```bash
# All tiers
python -m integrations.power_platform_connector
# Plus: Power Automate workflows, Power Apps UI, Power BI dashboards
```

---

## 🚀 Deployment Options

### Option 1: Local (Development)
```bash
python knowledge_agent_bot.py
# Default: Tier 1 (local extraction)
```

### Option 2: Standalone API
```bash
python -m integrations.power_platform_connector
# Starts FastAPI on port 8000
# Enables Tier 4 capabilities
```

### Option 3: Docker Container
```bash
docker build -t knowledge-agent:latest .
docker run -p 8000:8000 -e FOUNDRY_ENABLED=true knowledge-agent:latest
```

### Option 4: Azure Container Instances
```bash
az containerapp up --name knowledge-agent \
  -e FOUNDRY_ENABLED=true \
  -e M365_ENABLED=true
```

### Option 5: Kubernetes
```bash
kubectl apply -f k8s-deployment.yaml
# 3 replicas, auto-scaling, health checks included
```

---

## ✅ Validation & Testing

### Quick Validation (30 seconds)
```bash
python verify_tier3_tier4.py
# ✅ Checks all files, imports, configuration
```

### Full Examples (2 minutes)
```bash
python tier3_tier4_examples.py
# Runs all 12 integration examples
```

### Unit Tests
```bash
python -m pytest tests/
# Or: python test_extraction.py
```

---

## 🔗 API Documentation

### Power Platform REST Endpoints

**Extract**:
```
POST /extract
  artifact_type: 'paper' | 'talk' | 'repository'
  source_location: string
  save_results: bool
  notify_teams: bool
Response: { success, title, confidence, overview, artifact_url }
```

**Data Access**:
```
GET  /artifacts?limit=100&offset=0
GET  /artifacts/{id}
GET  /search?query=...&limit=20
POST /artifacts/{id}/feedback
```

**Analytics**:
```
GET /analytics/summary
GET /analytics/quality
GET /analytics/export?format=json
```

**Status**:
```
GET /health
GET /schema
```

Complete API docs: [TIER3_TIER4_COMPLETE.md](TIER3_TIER4_COMPLETE.md#power-platform-connector)

---

## 📚 Learning Resources

| Resource | Level | Time | Purpose |
|----------|-------|------|---------|
| [BUILD_COMPLETE.md](BUILD_COMPLETE.md) | Quick | 5 min | Overview |
| [tier3_tier4_examples.py](tier3_tier4_examples.py) | Beginner | 10 min | Working code |
| [OPTIONAL_INTEGRATIONS.md](OPTIONAL_INTEGRATIONS.md) | Intermediate | 20 min | Architecture |
| [TIER3_TIER4_COMPLETE.md](TIER3_TIER4_COMPLETE.md) | Advanced | 40 min | Full guide |

---

## 🆘 Troubleshooting

### Import Errors
```bash
# Install optional dependencies
pip install azure-ai-projects azure-identity fastapi uvicorn
```

### Configuration Issues
```python
from integrations import get_settings
settings = get_settings()
settings.print_summary()  # Shows current config
settings.validate_all()   # Checks everything
```

### Foundry Connection
```python
from integrations import create_foundry_provider
p = create_foundry_provider(os.getenv("FOUNDRY_CONNECTION_STRING"))
print(p.get_model_info())  # Should work if configured
```

### Power Platform API
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

See [TIER3_TIER4_COMPLETE.md#troubleshooting](TIER3_TIER4_COMPLETE.md) for more.

---

## 📞 Support

- 📖 **Documentation**: All `.md` files in this directory
- 💻 **Code Examples**: `tier3_tier4_examples.py`
- ✔️ **Verification**: `python verify_tier3_tier4.py`
- 🔧 **Configuration**: `.env.example` and `extended_settings.py`

---

## 🎉 What You Have

✅ **Complete extraction platform** (Tiers 1-4)
✅ **Optional integrations** (each tier independent)
✅ **Production-ready code** (error handling, logging, validation)
✅ **Flexible deployment** (local to Kubernetes)
✅ **Comprehensive documentation** (1,100+ lines)
✅ **Working examples** (12 complete samples)
✅ **Validation tools** (automated verification)

---

## 🏆 Status

| Component | Status |
|-----------|--------|
| Tier 1: Local | ✅ Complete |
| Tier 2: M365 | ✅ Complete |
| Tier 3: Foundry | ✅ Complete ⭐ NEW |
| Tier 4: Power Platform | ✅ Complete ⭐ NEW |
| Documentation | ✅ Complete |
| Examples | ✅ Complete |
| Verification | ✅ Complete |
| **Overall** | 🟢 **PRODUCTION READY** |

---

**Start here**: Read [BUILD_COMPLETE.md](BUILD_COMPLETE.md)
**Then try**: `python verify_tier3_tier4.py`
**Then explore**: `python tier3_tier4_examples.py`
**Then deploy**: Follow [TIER3_TIER4_COMPLETE.md](TIER3_TIER4_COMPLETE.md)

**Ready to go! 🚀**
