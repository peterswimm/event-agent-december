ov# Event Kit Agent

**AI-powered event recommendation agent** with multi-channel deployment support. Demonstrates production-ready agent patterns for Teams, Copilot, HTTP APIs, and CLI.

[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com/peterswimm/event-agent-december)
[![Tests: 147 Passing](https://img.shields.io/badge/Tests-147%20Passing-success)](./tests)
[![Documentation: Complete](https://img.shields.io/badge/Docs-Complete-blue)](./docs)

---

## 🌟 Overview

Event Kit is a comprehensive AI agent showcasing enterprise-ready patterns:

### Core Features
- ✅ **Declarative manifest**: Sessions, weights, and feature flags in JSON
- ✅ **Multi-channel deployment**: CLI, HTTP API, Teams, Copilot Studio
- ✅ **Bot Framework integration**: Full Teams/Outlook bot with adaptive cards
- ✅ **Microsoft Graph integration**: Live calendar events with MSAL auth
- ✅ **Adaptive Cards**: Interactive UI for rich experiences
- ✅ **Profile persistence**: Save/load user preferences
- ✅ **Structured telemetry**: Application Insights + JSONL logging
- ✅ **Security hardening**: Input validation, rate limiting, CORS
- ✅ **Production infrastructure**: Docker, Bicep, CI/CD pipelines

### Deployment Modes

| Mode | Use Case | Entry Point | Documentation |
|------|----------|-------------|---------------|
| **CLI** | Local testing, scripts | `agent.py` | [Quick Start](#quick-start) |
| **HTTP API** | REST endpoints | `agent.py serve` | [API Docs](docs/api-guide.md) |
| **Teams Bot** | Microsoft Teams | `bot_server.py` | [Teams Setup](docs/agents-sdk-setup.md) · [MS Learn: Bot Framework](https://learn.microsoft.com/azure/bot-service/) |
| **Copilot Plugin** | Copilot Studio | `copilot-plugin.json` | [Copilot Guide](docs/agents-sdk-setup.md#copilot-integration) · [MS Learn: Copilot Studio](https://learn.microsoft.com/microsoft-copilot-studio/) |
| **Docker** | Containerized deployment | `deploy/Dockerfile` | [Deployment Guide](docs/deployment-guide.md) · [MS Learn: Container Apps](https://learn.microsoft.com/azure/container-apps/) |

---

## How This Fits in Vibe Kit

Vibe Kit is a repository of innovation kits designed to accelerate AI agent prototyping. Event Kit serves as:

1. **Foundational example**: Minimal agent architecture (manifest + logic)
2. **Starter for real integrations**: Easily extend to Microsoft Graph, SharePoint, or Agent SDK hosting
3. **Pattern library**: Demonstrates scoring, conflict detection, adaptive cards, telemetry

For production-ready Graph/SharePoint integration, see [`innovation-kit-repository/event-agent/`](../innovation-kit-repository/event-agent/) which includes:

- Microsoft 365 Agents SDK hosting scaffold
- Graph Calendar fetching with MSAL auth
- SharePoint page publishing
- Pydantic configuration with feature flags
- Full setup guide in `MVP_GUIDE.md`

---

## � Quick Start

Choose your testing environment:

### 1️⃣ CLI Mode (30 seconds)

```bash
# Install dependencies
pip install -r requirements.txt

# Recommend sessions
python agent.py recommend --interests "agents, ai safety" --top 3

# Explain a session
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"

# Export itinerary
python agent.py export --interests "agents, privacy" --output my_itinerary.md
```

### 2️⃣ HTTP API Mode (1 minute)

```bash
# Start server
python agent.py serve --port 8010 --card

# Test endpoints
curl http://localhost:8010/health
curl "http://localhost:8010/recommend?interests=agents,ai+safety&top=3"
curl "http://localhost:8010/explain?session=Generative+Agents&interests=agents"
```

### 3️⃣ Teams Bot Mode (5 minutes)

```bash
# Start bot server
python bot_server.py

# Download Bot Framework Emulator v4.14.1+
# https://github.com/microsoft/BotFramework-Emulator/releases/latest

# Connect to: http://localhost:3978/api/messages
# Send: @bot recommend agents, machine learning
```

**Complete guide**: [LOCAL_TESTING.md](LOCAL_TESTING.md)

### 4️⃣ Docker Mode (2 minutes)

```bash
# Build and run
docker build -t eventkit:latest -f deploy/Dockerfile .
docker run -p 8010:8010 eventkit:latest

# Or use Docker Compose
cd deploy
docker compose up
```

### 5️⃣ Microsoft Foundry Mode (15 minutes)

```bash
# Deploy infrastructure with Foundry
az deployment group create \
  --resource-group eventkit-rg \
  --template-file infra/main.bicep \
  --parameters deployFoundry=true

# Install Agent Framework SDK (--pre flag required)
pip install agent-framework-azure-ai --pre

# Configure environment
export FOUNDRY_ENABLED=true
export FOUNDRY_PROJECT_ENDPOINT="https://eastus.api.azureml.ms"

# Run with Agent Framework
python agent_framework_adapter.py
```

**Complete guide**: [docs/foundry-deployment.md](docs/foundry-deployment.md)

**Microsoft Learn**:
- [Azure AI Foundry Overview](https://learn.microsoft.com/azure/ai-studio/what-is-ai-studio)
- [Agent Service](https://learn.microsoft.com/azure/ai-services/agents/overview)
- [Prompt Flow](https://learn.microsoft.com/azure/machine-learning/prompt-flow/overview-what-is-prompt-flow)

---

## 📚 Documentation

### Quick Start

- 🚀 **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- 🎯 **[docs/DECISION_GUIDE.md](docs/DECISION_GUIDE.md)** - Choose the right integration pattern & platform ⭐
- 💻 **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup & workflow
- 🧪 **[LOCAL_TESTING.md](LOCAL_TESTING.md)** - Multi-channel testing guide

### Architecture

- ⭐ **[docs/UNIFIED_ADAPTER_ARCHITECTURE.md](docs/UNIFIED_ADAPTER_ARCHITECTURE.md)** - Unified adapter pattern (Azure AI Foundry, Power Platform, Bot Framework)
- 🔧 **[docs/EXTENSIBILITY_GUIDE.md](docs/EXTENSIBILITY_GUIDE.md)** - Extending with Power Platform, Azure Functions, declarative agents

### Integration & Deployment

- 🤖 **[docs/agents-sdk-setup.md](docs/agents-sdk-setup.md)** - Teams/Copilot integration · [MS Learn](https://learn.microsoft.com/azure/bot-service/bot-builder-basics)
- 🏭 **[docs/foundry-deployment.md](docs/foundry-deployment.md)** - Azure AI Foundry deployment · [MS Learn](https://learn.microsoft.com/azure/ai-studio/)
- 🚀 **[docs/deployment-guide.md](docs/deployment-guide.md)** - Production deployment · [MS Learn](https://learn.microsoft.com/azure/app-service/)

### API & Testing

- 🔧 **[docs/api-guide.md](docs/api-guide.md)** - HTTP API reference
- 📝 **[docs/api-examples.md](docs/api-examples.md)** - API usage examples
- ✅ **[docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Comprehensive testing guide (190+ tests)
- 🐛 **[docs/troubleshooting.md](docs/troubleshooting.md)** - Troubleshooting & common issues

---

## 🧪 Multi-Channel Testing Environments

### Environment 1: Local CLI
**Purpose**: Quick testing, scripting, debugging

```bash
# Test recommendation logic
python agent.py recommend --interests "agents" --top 3

# Test with profile persistence
python agent.py recommend --interests "agents, telemetry" --profile-save demo
python agent.py recommend --profile-load demo --top 5
```

**Best for**: Algorithm testing, data validation, automation

---

### Environment 2: HTTP API Server
**Purpose**: REST API testing, integration testing

```bash
# Start server with adaptive cards
python agent.py serve --port 8010 --card
```

**Test with curl**:
```bash
# Health check
curl http://localhost:8010/health

# Recommendations
curl "http://localhost:8010/recommend?interests=agents,ai+safety&top=5"

# With adaptive cards
curl "http://localhost:8010/recommend?interests=agents&top=3&card=1"

# Explain session
curl "http://localhost:8010/explain?session=AI+Safety+Foundations&interests=ai+safety"

# Export itinerary
curl "http://localhost:8010/export?interests=agents,privacy&format=markdown"
```

**Best for**: API integration, performance testing, HTTP client development

---

### Environment 3: Bot Framework Emulator
**Purpose**: Teams bot testing, conversation flow testing

**Setup**:
1. Start bot server: `python bot_server.py`
2. Download [Bot Framework Emulator v4.14.1+](https://github.com/microsoft/BotFramework-Emulator/releases/latest)
3. Open emulator, connect to `http://localhost:3978/api/messages`
4. Leave App ID and Password empty for local testing

**Test commands**:
```
recommend agents, machine learning --top 5
explain "Generative Agents in Production" --interests agents
export agents, ai safety --profile my_profile
help
```

**Features to test**:
- ✅ Command parsing
- ✅ Adaptive cards rendering
- ✅ Natural language queries
- ✅ Error handling
- ✅ Typing indicators
- ✅ Profile persistence

**Best for**: Bot UX testing, conversation design, Teams preparation

**Complete guide**: [LOCAL_TESTING.md](LOCAL_TESTING.md)

---

### Environment 4: Microsoft Teams (Local Tunnel)
**Purpose**: Real Teams environment testing

**Setup with ngrok**:
```bash
# Start bot server
python bot_server.py

# In another terminal, start ngrok
ngrok http 3978

# Copy ngrok URL (e.g., https://abc-123-def.ngrok.io)
# Update bot endpoint in Azure Portal or Bot Framework registration
# Upload teams-app.json to Teams Developer Portal
```

**Test in Teams**:
```
@EventKit Agent recommend agents, machine learning
@EventKit Agent explain "Session Title" --interests agents
@EventKit Agent export agents --profile tech_days
@EventKit Agent help
```

**Best for**: End-to-end Teams testing, user acceptance testing

---

### Environment 5: Docker Container
**Purpose**: Production-like environment, deployment validation

```bash
# Build image
docker build -t eventkit:test -f deploy/Dockerfile .

# Run with environment variables
docker run -p 8010:8010 \
  -e BOT_ID="your-bot-id" \
  -e BOT_PASSWORD="your-password" \
  eventkit:test

# Or use Docker Compose
cd deploy
docker compose up
```

**Test**:
```bash
curl http://localhost:8010/health
curl "http://localhost:8010/recommend?interests=agents&top=3"
```

**Best for**: Deployment validation, container testing, CI/CD pipeline testing

---

### Environment 6: Copilot Studio
**Purpose**: Copilot integration testing

**Setup**:
1. Go to [Copilot Studio](https://copilotstudio.microsoft.com)
2. Create new copilot
3. Import `copilot-plugin.json`
4. Configure actions with bot endpoint

**Test scenarios**:
- "Find sessions about agents and AI"
- "Explain why this session matches my interests"
- "Export my personalized agenda"

**Best for**: Copilot UX testing, AI orchestration validation

---

### Environment 7: Azure Production
**Purpose**: Production deployment, monitoring

**Deploy**:
```bash
# Using Bicep templates
az deployment group create \
  --resource-group eventkit-prod-rg \
  --template-file infra/main.bicep \
  --parameters infra/prod.bicepparam
```

**Monitor**:
- Application Insights for telemetry
- Log Analytics for centralized logs
- Azure Monitor for alerts

**Best for**: Production validation, load testing, performance monitoring

**Complete guide**: [docs/deployment-guide.md](docs/deployment-guide.md)

---

### Environment 8: Microsoft Foundry
**Purpose**: AI Hub orchestration, Prompt Flow evaluation, model management

**Setup**:
```bash
# Deploy Foundry infrastructure
az deployment group create \
  --resource-group eventkit-foundry-rg \
  --template-file infra/main.bicep \
  --parameters deployFoundry=true

# Install Agent Framework SDK (--pre flag required)
pip install agent-framework-azure-ai --pre

# Configure environment
export FOUNDRY_ENABLED=true
export FOUNDRY_PROJECT_ENDPOINT="https://eastus.api.azureml.ms"
export FOUNDRY_PROJECT_NAME="eventkit-prod-project"
```

**Test**:
```python
from agent_framework_adapter import EventKitAgentFramework
agent = EventKitAgentFramework()
response = await agent.run("recommend sessions about AI agents")
```

**Features**:
- ✅ AI Hub & Project for resource management
- ✅ GPT-4o and GPT-3.5-turbo deployments
- ✅ Prompt Flow orchestration (4-node workflow)
- ✅ Evaluation framework (precision, recall, F1, relevance)
- ✅ Managed compute and auto-scaling
- ✅ Enterprise security (RBAC, Key Vault)

**Best for**: Production AI orchestration, model evaluation, multi-agent systems, prompt engineering

**Complete guide**: [docs/foundry-deployment.md](docs/foundry-deployment.md)

---

## ⚖️ Choosing the Right Platform

**Microsoft Foundry or Copilot Studio?** Here's how to decide:

### Decision Framework

```
┌─────────────────────────────────────────────────────────────┐
│                  WHO IS BUILDING?                            │
└─────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
   ┌──────▼──────┐                   ┌─────▼─────┐
   │ Line-of-    │                   │ Software  │
   │ Business    │                   │ Developers│
   │ Users + IT  │                   │ with      │
   │ Admins      │                   │ DevOps    │
   └──────┬──────┘                   └─────┬─────┘
          │                                 │
   ┌──────▼──────────────┐          ┌──────▼──────────────┐
   │ COPILOT STUDIO      │          │ MICROSOFT FOUNDRY   │
   │                     │          │                     │
   │ ✅ Low-code UI      │          │ ✅ Full Python/C#   │
   │ ✅ Managed platform │          │ ✅ Custom code      │
   │ ✅ Quick iteration  │          │ ✅ DevOps pipelines │
   │ ✅ Built-in actions │          │ ✅ Own resources    │
   │ ✅ No infra mgmt    │          │ ✅ Deep integration │
   └─────────────────────┘          └─────────────────────┘
```

### When to Use Copilot Studio

**✅ Choose Copilot Studio when**:
- **Team composition**: Line-of-business users, IT admins, professional makers
- **Development style**: Low-code, visual design, managed environment
- **Speed**: Need to move from experimentation to execution quickly
- **Complexity**: Moderate workflows with built-in connectors
- **Governance**: Want managed security, compliance out-of-the-box

**Example scenarios**:
- HR building an employee onboarding agent
- IT help desk creating a ticket routing bot
- Marketing automating customer engagement
- Rapid prototyping with business stakeholders

**EventKit in Copilot Studio**:
- Use `copilot-plugin.json` manifest
- Deploy via [docs/agents-sdk-setup.md](docs/agents-sdk-setup.md#copilot-integration)
- Leverage built-in Teams integration
- No infrastructure management required

**Learn more**:
- [Microsoft Copilot Studio documentation](https://learn.microsoft.com/microsoft-copilot-studio/)
- [Create your first copilot](https://learn.microsoft.com/microsoft-copilot-studio/fundamentals-get-started)
- [Add custom actions](https://learn.microsoft.com/microsoft-copilot-studio/advanced-plugin-actions)

---

### When to Use Microsoft Foundry

**✅ Choose Microsoft Foundry when**:
- **Team composition**: Software developers, ML engineers, DevOps teams
- **Development style**: Pro-code, Python/C#/.NET, custom frameworks
- **Control**: Need deep customization, custom models, fine-tuning
- **Integration**: Complex enterprise systems, custom APIs
- **DevOps**: CI/CD pipelines, infrastructure as code, version control

**Example scenarios**:
- Building multi-agent orchestration systems
- Custom model deployment and evaluation
- Complex RAG (Retrieval-Augmented Generation) pipelines
- Production ML workflows with advanced monitoring
- Integration with legacy enterprise systems

**EventKit in Microsoft Foundry**:
- Use `agent_framework_adapter.py` for Agent Framework
- Deploy with `flow.dag.yaml` for Prompt Flow orchestration
- Full guide: [docs/foundry-deployment.md](docs/foundry-deployment.md)
- Bicep infrastructure: `infra/main.bicep` with `deployFoundry=true`

**Learn more**:
- [Azure AI Foundry documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Develop AI agents](https://learn.microsoft.com/azure/ai-services/agents/quickstart)
- [Prompt Flow development](https://learn.microsoft.com/azure/machine-learning/prompt-flow/get-started-prompt-flow)
- [Deploy generative AI](https://learn.microsoft.com/azure/machine-learning/prompt-flow/how-to-deploy-for-real-time-inference)

---

### Fusion Teams: Use Both

**Many organizations need both platforms** - this is expected and supported:

**Collaboration patterns**:
- **Copilot Studio agents** for business users
- **Foundry agents** for backend processing, ML models
- **Communication**: Multi-agent workflows using MCP, A2A, Activity Protocol

**Microsoft Agent Pre-Purchase Plan (P3)**:
- Single pool of funds for both platforms
- Choose the right tool at build time, not purchase time
- Flexibility as team composition changes

**EventKit supports both**:
- Bot Framework for Copilot Studio integration
- Agent Framework for Foundry orchestration
- Shared core logic (`core.py`) works across platforms

---

### Feature Parity Reference

| Feature | Copilot Studio | Microsoft Foundry | EventKit Support |
|---------|----------------|-------------------|------------------|
| **Multi-agent workflows** | ✅ | ✅ | ✅ Both |
| **Tools/Plugins** | ✅ Built-in | ✅ Custom | ✅ Both |
| **Orchestration** | ✅ Visual | ✅ Code-first | ✅ Both |
| **Enterprise governance** | ✅ Managed | ✅ Custom RBAC | ✅ Both |
| **Low-code design** | ✅ Yes | ❌ Pro-code only | ⚠️ Copilot only |
| **Custom models** | ⚠️ Limited | ✅ Full control | ✅ Foundry |
| **DevOps integration** | ⚠️ Basic | ✅ Advanced | ✅ Foundry |
| **Infrastructure control** | ❌ Managed | ✅ Full control | ✅ Foundry |

### Decision Checklist

**Choose Copilot Studio if you answer YES to 3+ questions**:
- [ ] Do you have non-developer business users building agents?
- [ ] Do you prefer visual/low-code tools?
- [ ] Is speed to market more important than deep customization?
- [ ] Do you want Microsoft to manage infrastructure?
- [ ] Are built-in connectors sufficient for your needs?

**Choose Microsoft Foundry if you answer YES to 3+ questions**:
- [ ] Do you have professional software developers on the team?
- [ ] Do you need custom model deployment or fine-tuning?
- [ ] Do you require advanced DevOps (CI/CD, IaC, testing)?
- [ ] Do you need deep integration with custom enterprise systems?
- [ ] Do you want full control over infrastructure and resources?

**Need help deciding?** Contact: Mads Bolaris, Shawn Henry, Anjli Chaudhry

**Official Resources**:
- [Microsoft Agent Service documentation](https://learn.microsoft.com/azure/ai-services/agents/)
- [Build your first agent](https://learn.microsoft.com/azure/ai-services/agents/quickstart)
- [Azure AI platform decision guide](https://learn.microsoft.com/azure/architecture/data-guide/technology-choices/data-science-and-machine-learning)

---

## 🎯 API Overview

### HTTP Endpoints

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/health` | GET | Health check | `curl http://localhost:8010/health` |
| `/recommend` | GET | Get personalized recommendations | `curl "http://localhost:8010/recommend?interests=agents&top=3"` |
| `/explain` | GET | Understand why a session matches | `curl "http://localhost:8010/explain?session=Title&interests=agents"` |
| `/export` | GET | Export itinerary to Markdown | `curl "http://localhost:8010/export?interests=agents&format=markdown"` |
| `/recommend-graph` | GET | Calendar-based recommendations | `curl "http://localhost:8010/recommend-graph?interests=agents&top=5"` |

**Full documentation**: [docs/api-guide.md](docs/api-guide.md) (100+ examples)

### Bot Commands (Teams/Emulator)

| Command | Format | Example |
|---------|--------|---------|
| Recommend | `@bot recommend <interests> --top <n>` | `@bot recommend agents, ai safety --top 5` |
| Explain | `@bot explain "<title>" --interests <list>` | `@bot explain "Session Title" --interests agents` |
| Export | `@bot export <interests> --profile <name>` | `@bot export agents --profile my_profile` |
| Help | `@bot help` | `@bot help` |

**Full reference**: [TEAMS_QUICK_REFERENCE.md](TEAMS_QUICK_REFERENCE.md)

---

## 🏗️ Architecture & Components

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                          │
│  Teams | Outlook | Copilot Studio | HTTP API | CLI          │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                  Integration Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Bot Handler  │  │ SDK Adapter  │  │ HTTP Server  │      │
│  │ (Teams)      │  │ (Copilot)    │  │ (REST API)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    Core Engine                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ recommend()  │  │ explain()    │  │ export()     │      │
│  │ scoring      │  │ matching     │  │ itinerary    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Graph API    │  │ Telemetry    │  │ Profiles     │      │
│  │ Integration  │  │ Logging      │  │ Storage      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | File | Purpose | Lines |
|-----------|------|---------|-------|
| **Core Logic** | `core.py` | Recommendation engine | ~400 |
| **Agent CLI** | `agent.py` | Command-line interface | ~800 |
| **Bot Handler** | `bot_handler.py` | Teams message processing | 455 |
| **Bot Server** | `bot_server.py` | aiohttp HTTP server | 223 |
| **Unified Adapters** | `adapters/base_adapter.py` | Base adapter framework | 450 |
| **Foundry Adapter** | `adapters/foundry_adapter.py` | Azure AI Foundry | 150 |
| **Power Adapter** | `adapters/power_adapter.py` | Power Platform | 120 |
| **Bot Adapter** | `adapters/bot_adapter.py` | Bot Framework | 150 |
| **Graph Service** | `graph_service.py` | Microsoft Graph API | ~300 |
| **Telemetry** | `telemetry.py` | Application Insights | ~200 |
| **Settings** | `settings.py` | Configuration management | ~150 |

**Architecture**: EventKit uses a **unified adapter pattern** to integrate with Azure AI Foundry, Power Platform, and Bot Framework. See [docs/UNIFIED_ADAPTER_ARCHITECTURE.md](docs/UNIFIED_ADAPTER_ARCHITECTURE.md) for details.

### Feature Matrix

| Feature | CLI | HTTP API | Bot Emulator | Teams | Foundry | Copilot | Production |
|---------|-----|----------|--------------|-------|---------|---------|------------|
| **Recommendations** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Explanations** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Export Itinerary** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Adaptive Cards** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Graph Integration** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Profile Persistence** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Natural Language** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Rate Limiting** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Telemetry** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Authentication** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Monitoring** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |

---

## Quick Start

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/recommend` | GET | Get personalized recommendations |
| `/explain` | GET | Understand why a session matches |
| `/export` | GET | Export itinerary to Markdown |
| `/recommend-graph` | GET | Calendar-based recommendations |

**Example**: `curl "http://localhost:8010/recommend?interests=agents&top=3"`

**Full documentation with 100+ code examples**: [docs/api-guide.md](docs/api-guide.md)

---

## Quick Start

### 1. Run Locally (No Setup)

```bash
cd event-agent-example

# Install dependencies
pip install -r requirements.txt

# Recommend sessions
python agent.py recommend --interests "agents, ai safety" --top 3

# Explain a session
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"

# Export itinerary
python agent.py export --interests "agents, privacy" --output my_itinerary.md

# Start HTTP server
python agent.py serve --port 8010 --card
```

Test endpoints:

```bash
curl http://localhost:8010/health
curl "http://localhost:8010/recommend?interests=agents,ai+safety&top=3&card=1"
curl "http://localhost:8010/explain?session=Generative+Agents+in+Production&interests=agents,gen+ai"
```

### 2. Profile Persistence

```bash
# Save interests for later
python agent.py recommend --interests "agents, telemetry" --profile-save demo

# Load saved profile
python agent.py recommend --profile-load demo --top 5
```

Profiles stored in `~/.event_agent_profiles.json`.

### 3. Run Tests

```bash
python -m pytest eventkit/tests -q
```

All 147 tests should pass (126 original + 21 security tests).

---

## Development Workflow

### Quick Commands

**One-command setup**:

```bash
bash setup.sh
```

**Make commands**:

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev           # Install dev dependencies + pre-commit hooks
make test          # Run tests with coverage
make lint          # Check code quality
make format        # Auto-format code
make run           # Start the server locally
make docker-run    # Run in Docker
make deploy-dev    # Deploy to Azure (dev environment)
```

**See [DEVELOPMENT.md](DEVELOPMENT.md) for complete guide.**

### GitHub Actions CI/CD

Automated workflows run on every push and PR:

- **Tests** (`test.yml`): Pytest with coverage on PR/push
- **Linting** (`lint.yml`): Black, isort, pylint checks
- **Security** (`security.yml`): Weekly Bandit + Safety scans
- **Deploy** (`deploy.yml`): Auto-deploy to Azure on merge to main

**Configuration**: See [.github/workflows/README.md](.github/workflows/README.md)

### Pre-commit Hooks

Automatically run code quality checks before commits:

```bash
pre-commit install
pre-commit run --all-files
```

**Checks**: Black, isort, pylint, bandit, pytest

---

## Docker & Azure Deployment

**Microsoft Learn**: [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/) · [Deploy containers](https://learn.microsoft.com/azure/container-apps/quickstart-portal)

**Local Docker**:

```bash
make docker-build
make docker-run
make docker-logs
```

**Deploy to Azure**:

```bash
make deploy-dev      # Development
make deploy-prod     # Production
```

Includes:

- Multi-stage Docker build (optimized size)
- Azure App Service with managed identity
- Key Vault for secrets
- Application Insights for monitoring
- Log Analytics for centralized logging

**Infrastructure**: [infra/README.md](infra/README.md)

---

## Setup Dev Environment in VS Code

### Prerequisites

- Python 3.11+
- VS Code with Python extension

### Steps

1. **Clone the Vibe Kit repo** (if not already):

   ```bash
   git clone https://github.com/peterswimm/vibe-kit.git
   cd vibe-kit
   ```

2. **Open eventkit in VS Code**:

   ```bash
   code eventkit
   ```

   Or open the workspace folder in VS Code and navigate to `eventkit/`.

3. **Create a virtual environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dev dependencies** (optional, for testing):

   ```bash
   pip install pytest
   ```

   The agent itself has **zero dependencies** — runs with Python stdlib only.

5. **Configure VS Code**:

   - Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
   - Select `Python: Select Interpreter`
   - Choose `.venv/bin/python`

6. **Run the agent**:

   Open integrated terminal in VS Code (`Ctrl+` `/`Cmd+` `) and:

   ```bash
   python agent.py recommend --interests "agents, ai safety" --top 3
   ```

7. **Run tests** (in VS Code terminal):

   ```bash
   python -m pytest tests -v
   ```

   Or use VS Code's Testing sidebar (flask icon) to discover and run tests interactively.

8. **Debug**:

   Set breakpoints in `agent.py`, then press `F5` (Run > Start Debugging). VS Code will prompt to create a `launch.json` — select "Python File" for CLI debugging or "Python: Current File" for general use.

---

## Extending with Agent SDK

To integrate with Microsoft 365 Agents SDK (Teams/Copilot Studio hosting):

1. **See the full Agent SDK starter** in [`innovation-kit-repository/event-agent/starter-code/agents_sdk_integration/`](../innovation-kit-repository/event-agent/starter-code/agents_sdk_integration/)
2. **Follow MVP_GUIDE.md** for Graph authentication, SharePoint publish, and SDK hosting setup
3. **Compare patterns**: Event Kit (`eventkit/agent.py`) shows minimal logic; Agent SDK starter adds authentication, caching, and enterprise features

### Key Differences

| Feature          | Event Kit (`eventkit/`)      | Agent SDK Starter (`innovation-kit-repository/event-agent/`) |
| ---------------- | ---------------------------- | ------------------------------------------------------------ |
| **Auth**         | None (mock data)             | MSAL (Graph + SharePoint)                                    |
| **Data Source**  | Static JSON or external file | Microsoft Graph Calendar                                     |
| **Publishing**   | Markdown export              | SharePoint page creation                                     |
| **Hosting**      | CLI + HTTP server            | Microsoft 365 Agents SDK (Teams/Copilot Studio)              |
| **Config**       | JSON manifest                | Pydantic settings + `.env`                                   |
| **Dependencies** | None                         | `pydantic`, `msal`, `requests`, `botbuilder-core`            |

**When to use Event Kit**: Prototyping agent logic, testing scoring algorithms, local demos

**When to use Agent SDK Starter**: Production deployment, Graph integration, Teams/Copilot experiences

---

## 📁 Project Structure

```
event-agent-example/
├── 🎯 Core Engine
│   ├── agent.py                      # CLI interface + command handlers
│   ├── core.py                       # Core recommendation logic
│   ├── agent.json                    # Event sessions catalog + scoring config
│   ├── agent-declaration.json        # Agents SDK manifest
│   └── agent.schema.json             # JSON schema validation
│
├── 🔌 Unified Adapters (NEW)
│   ├── adapters/
│   │   ├── __init__.py               # Package initialization
│   │   ├── base_adapter.py           # Base adapter framework (450 lines)
│   │   ├── foundry_adapter.py        # Azure AI Foundry (150 lines)
│   │   ├── power_adapter.py          # Power Platform (120 lines)
│   │   ├── bot_adapter.py            # Bot Framework (150 lines)
│   │   ├── directline_bot.py         # Direct Line bridge
│   │   └── requirements-directline.txt
│   ├── agent_framework_adapter.py    # Backward compat wrapper
│   └── agents_sdk_adapter.py         # Legacy adapter (539 lines)
│
├── 🤖 Bot Framework Integration
│   ├── bot_handler.py                # Teams activity handler (455 lines)
│   ├── bot_server.py                 # aiohttp HTTP server (223 lines)
│   ├── teams-app.json                # Teams app manifest
│   └── copilot-plugin.json           # Copilot Studio plugin manifest
│
├── 🌐 Microsoft Graph Integration
│   ├── graph_service.py              # Calendar API client
│   ├── graph_auth.py                 # MSAL authentication
│   └── runner.py                     # Multi-mode runner
│
├── ⚙️ Configuration & Utilities
│   ├── settings.py                   # Pydantic settings + environment config
│   ├── telemetry.py                  # Application Insights integration
│   ├── logging_config.py             # Structured logging
│   └── errors.py                     # Custom exceptions
│
├── 🧪 Tests (190+ tests passing)
│   ├── test_unified_adapters.py      # Unified adapter tests (NEW)
│   ├── test_agents_sdk.py            # SDK adapter tests
│   ├── test_graph_service.py         # Graph API tests
│   ├── test_core_graph.py            # Core logic tests
│   ├── test_bot_handler.py           # Bot Framework tests
│   └── ... (20 test files)
│
├── 📚 Documentation
│   ├── README.md                     # This file
│   ├── QUICKSTART.md                 # Quick start guide
│   ├── DEVELOPMENT.md                # Development guide
│   ├── LOCAL_TESTING.md              # Multi-channel testing guide
│   ├── docs/
│   │   ├── UNIFIED_ADAPTER_ARCHITECTURE.md  # Unified adapters (NEW)
│   │   ├── EXTENSIBILITY_GUIDE.md    # Power Platform integration
│   │   ├── TESTING_GUIDE.md          # Comprehensive testing
│   │   ├── agents-sdk-setup.md       # Teams/Copilot integration
│   │   ├── foundry-deployment.md     # Azure AI Foundry deployment
│   │   ├── deployment-guide.md       # Production deployment
│   │   ├── api-guide.md              # HTTP API reference
│   │   ├── api-examples.md           # API usage examples
│   │   └── troubleshooting.md        # Common issues
│
├── 🏗️ Infrastructure
│   ├── infra/
│   │   ├── main.bicep                # Azure resources (App Service, Key Vault, etc.)
│   │   ├── dev.bicepparam            # Development environment
│   │   └── prod.bicepparam           # Production environment
│   ├── deploy/
│   │   ├── Dockerfile                # Multi-stage build
│   │   ├── docker-compose.yml        # Local dev containers
│   │   └── nginx.conf                # Reverse proxy
│   └── .devcontainer/
│       └── devcontainer.json         # VS Code dev containers
│
├── 🔄 CI/CD & Automation
│   ├── .github/workflows/
│   │   ├── test.yml                  # Pytest on every PR
│   │   ├── lint.yml                  # Code quality checks
│   │   ├── security.yml              # Security scans
│   │   └── deploy.yml                # Azure deployment
│   ├── Makefile                      # Development commands
│   ├── setup.sh                      # One-command setup
│   └── .pre-commit-config.yaml       # Git hooks
│
├── 📦 Dependencies
│   ├── requirements.txt              # Production dependencies
│   ├── requirements-dev.txt          # Development dependencies
│   └── pyproject.toml                # Project metadata
│
└── 📊 Data & Assets
    ├── assets/
    │   ├── sample_itinerary.md       # Sample export output
    │   └── sessions_external.json    # External event data
    └── exports/                      # Generated itineraries
└── README.md                # This file
```

  ```bash
  # Requires: MICROSOFT_APP_ID, MICROSOFT_APP_PASSWORD; optional AGENT_API_BASE
  eventkit-runner --mode directline-adapter --port 3979
  ```

  ```bash
  # Optional interests; add --publish to push pages
  eventkit-runner --mode sharepoint-agent --interests "AI;agents" --max-sessions 3 --publish
  ```

Mode boundaries:

- MCP/tools only in `custom-chat`
- Graph/SharePoint integrations only in `m365-agent` / `sharepoint-agent`

Deployment playbooks:

- `m365-agent`: Azure App Service/Container Apps, Bot Framework channel
- `sharepoint-agent`: Azure Function/Container job
- `custom-chat`: Containerized web service + optional MCP servers

### Config via Environment

You can set `RUN_MODE` and related variables in `.env` and run the runner without `--mode`:

```bash
cd eventkit
cp .env.example .env
# Edit .env, then export for the shell
export $(grep -v '^#' .env | xargs)

# RUN_MODE controls the behavior; falls back to CLI --mode if provided
eventkit-runner  # uses RUN_MODE
```

`.env.example` keys:

- `RUN_MODE`: `custom-chat` | `m365-agent` | `sharepoint-agent`
- `PORT`: Port for server modes (`custom-chat`, `m365-agent`)
- `INCLUDE_CARD`: `true|false` Adaptive Card in responses (custom-chat)
- `GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`: Required for `m365-agent`; required for `sharepoint-agent` when publishing
- `INTERESTS`, `MAX_SESSIONS`, `PUBLISH`: Defaults for `sharepoint-agent`

### Observability

- `custom-chat`: JSONL telemetry via `telemetry.jsonl`, health check at `/health`
- `m365-agent`: Integrate Azure Application Insights in the SDK host; expose liveness/readiness on the hosting platform
- `sharepoint-agent`: Log publish actions to JSONL and consider Azure Function logs or Container logs; add a simple CLI exit code for automation

### MCP/Tooling Separation

- MCP servers and tooling are intended for `custom-chat` mode only.
- Avoid enabling MCP in `m365-agent` and `sharepoint-agent` paths unless a specific enterprise need is identified.
- Keep boundaries clear: SDK-hosted experiences should rely on Graph/SharePoint integrations and platform observability.

### Deployment Playbooks

- `m365-agent` (Teams/Copilot Studio host):

  - Package the SDK host as a container and deploy to Azure App Service or Azure Container Apps.
  - Configure Bot Framework channel and required Graph credentials via app settings.
  - Add Application Insights for tracing and dashboards.

- `sharepoint-agent` (publisher service):

  - Implement as an Azure Function (timer/HTTP) or a scheduled container job.
  - Provide Graph credentials via Key Vault/App Settings; log publish results to JSONL and platform logs.
  - Keep no-chat boundary: this service publishes itineraries only.

- `custom-chat` (local/minimal web):
  - Containerize the HTTP server for portability; optionally run MCP servers alongside.
  - Expose `/health` and write local JSONL telemetry; consider lightweight reverse proxy for production demos.

### Minimize Open Ports

To reduce security review scope, prefer a single externally exposed port:

- Use NGINX reverse proxy to expose only `8010` and proxy to internal services.
- Bind internal services to `127.0.0.1` and non-exposed ports (`8011` for agent, `5174` for frontend when needed).

Quick container example (exposes only 8010):

```bash
cd eventkit/deploy
docker build -t eventkit-proxy .
docker run --rm -p 8010:8010 eventkit-proxy
```

Or use Docker Compose:

```bash
cd eventkit/deploy
docker compose up -d
```

This runs `agent.py serve` on `8011` internally and fronts it with NGINX at `8010`. The optional frontend can be proxied under `/app` without opening `5174` publicly.

Devcontainer now forwards only `8010`, consolidating all services behind the NGINX proxy.

### Direct Line / Web Chat (Adaptive Cards)

Use the Bot Framework adapter shim in `eventkit/adapters/directline_bot.py`:

```bash
cd eventkit
python -m pip install -r adapters/requirements-directline.txt
MICROSOFT_APP_ID="<bot app id>" \
MICROSOFT_APP_PASSWORD="<bot app password>" \
AGENT_API_BASE="http://localhost:8010" \
python -m eventkit.adapters.directline_bot --port 3979
```

- Exposes `/api/messages` for Direct Line / Bot Framework Web Chat.
- Forwards user text to the Event Kit `/recommend` endpoint and returns an Adaptive Card attachment.
- Deploy this container to Azure App Service/Container Apps, enable the Direct Line channel, and point Web Chat to the Direct Line token.

## Feature Flags

Adjust behavior in `agent.json > features`:

- **`telemetry.enabled`**: Log actions to `telemetry.jsonl`
- **`export.enabled`**: Save markdown to `exports/` directory
- **`externalSessions.enabled`**: Override sessions with `sessions_external.json`

---

## Next Steps

1. **Customize sessions**: Edit `agent.json` to add your event data
2. **Adjust scoring weights**: Tweak `weights` (interest, popularity, diversity)
3. **Connect real data**: Enable `externalSessions` and provide JSON feed
4. **Add authentication**: See Agent SDK starter for Graph/MSAL patterns
5. **Deploy as service**: Use systemd or containerize (see `QUICKSTART.md`)
6. **Integrate with Teams**: Follow `innovation-kit-repository/event-agent/MVP_GUIDE.md`

---

## Resources & Dependencies

**Core Dependencies**:
- **[Bot Framework SDK](https://learn.microsoft.com/azure/bot-service/)** - Teams/Outlook bot integration
- **[Microsoft Graph](https://learn.microsoft.com/graph/)** - Calendar and M365 data access
- **[Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)** - Telemetry and monitoring
- **[Azure Bicep](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)** - Infrastructure as Code
- **[pytest](https://docs.pytest.org/)** - Testing framework
- **[VS Code](https://code.visualstudio.com/docs/languages/python)** - Python development environment

---

## 📚 Additional Resources

### EventKit Documentation

**Getting Started**:
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide (5 minutes)
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development guide
- **[LOCAL_TESTING.md](LOCAL_TESTING.md)** - Multi-channel testing guide

**Architecture & Integration**:
- **[docs/UNIFIED_ADAPTER_ARCHITECTURE.md](docs/UNIFIED_ADAPTER_ARCHITECTURE.md)** ⭐ - Unified adapter pattern (Azure AI Foundry, Power Platform, Bot Framework)
- **[docs/EXTENSIBILITY_GUIDE.md](docs/EXTENSIBILITY_GUIDE.md)** - Power Platform, Azure Functions, declarative agents
- **[docs/agents-sdk-setup.md](docs/agents-sdk-setup.md)** - Teams/Copilot integration
- **[docs/foundry-deployment.md](docs/foundry-deployment.md)** - Azure AI Foundry deployment
- **[docs/deployment-guide.md](docs/deployment-guide.md)** - Production deployment

**Testing & Quality**:
- **[docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Comprehensive testing guide (20 test files, 190+ tests)
- **[pytest.ini](pytest.ini)** - Test configuration

**Complete Documentation**: **[docs/](docs/)** - Full documentation library

### Microsoft Learn Resources

**AI & Agents**:
- [Azure AI Services overview](https://learn.microsoft.com/azure/ai-services/)
- [Build AI agents](https://learn.microsoft.com/azure/ai-services/agents/overview)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Responsible AI principles](https://learn.microsoft.com/azure/machine-learning/concept-responsible-ai)

**Bot Framework & Teams**:
- [Bot Framework documentation](https://learn.microsoft.com/azure/bot-service/)
- [Teams bot development](https://learn.microsoft.com/microsoftteams/platform/bots/what-are-bots)
- [Teams Platform overview](https://learn.microsoft.com/microsoftteams/platform/overview)
- [Teams JavaScript SDK](https://learn.microsoft.com/microsoftteams/platform/tabs/how-to/using-teams-client-sdk)
- [Adaptive Cards](https://learn.microsoft.com/adaptive-cards/)
- [Bot Framework SDK (Python)](https://learn.microsoft.com/azure/bot-service/python/bot-builder-python-quickstart)

**Microsoft Graph & SharePoint**:
- [Microsoft Graph overview](https://learn.microsoft.com/graph/overview)
- [Graph Python SDK](https://learn.microsoft.com/graph/sdks/sdks-overview)
- [Calendar API reference](https://learn.microsoft.com/graph/api/resources/calendar)
- [SharePoint REST API](https://learn.microsoft.com/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service)
- [SharePoint Framework (SPFx)](https://learn.microsoft.com/sharepoint/dev/spfx/sharepoint-framework-overview)
- [Files & Lists via Graph](https://learn.microsoft.com/graph/api/resources/sharepoint)
- [Authentication with MSAL](https://learn.microsoft.com/azure/active-directory/develop/msal-overview)

**Office Add-ins & Extensibility**:
- [Office Add-ins platform](https://learn.microsoft.com/office/dev/add-ins/overview/office-add-ins)
- [Office JavaScript API](https://learn.microsoft.com/office/dev/add-ins/reference/javascript-api-for-office)
- [Outlook Add-ins](https://learn.microsoft.com/office/dev/add-ins/outlook/outlook-add-ins-overview)
- [Microsoft 365 Copilot extensibility](https://learn.microsoft.com/microsoft-365-copilot/extensibility/)

**Azure Deployment & Functions**:
- [Azure App Service](https://learn.microsoft.com/azure/app-service/)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)
- [Azure Functions](https://learn.microsoft.com/azure/azure-functions/)
- [Azure Functions Python](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Bicep documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure CLI reference](https://learn.microsoft.com/cli/azure/)

**Power Platform & Connectors**:
- [Power Platform overview](https://learn.microsoft.com/power-platform/)
- [Custom Connectors](https://learn.microsoft.com/connectors/custom-connectors/)
- [Power Automate](https://learn.microsoft.com/power-automate/)
- [Power Apps](https://learn.microsoft.com/power-apps/)
- [Dataverse](https://learn.microsoft.com/power-apps/developer/data-platform/)

**Adaptive Cards & WebChat**:
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
- [Adaptive Cards SDK](https://learn.microsoft.com/adaptive-cards/sdk/)
- [Bot Framework WebChat](https://learn.microsoft.com/azure/bot-service/bot-service-channel-connect-webchat)
- [Direct Line API](https://learn.microsoft.com/azure/bot-service/rest-api/bot-framework-rest-direct-line-3-0-concepts)

**Declarative Agents & Skills**:
- [Declarative agents](https://learn.microsoft.com/microsoft-365-copilot/extensibility/declarative-agent-manifest)
- [Agent builder](https://learn.microsoft.com/microsoft-365-copilot/extensibility/build-declarative-agents)
- [API plugins](https://learn.microsoft.com/microsoft-365-copilot/extensibility/api-plugin-overview)
- [Copilot connectors](https://learn.microsoft.com/microsoft-365-copilot/extensibility/overview-business-applications)

**Microsoft 365 Knowledge & Search**:
- [Microsoft Search API](https://learn.microsoft.com/graph/search-concept-overview)
- [Knowledge connectors](https://learn.microsoft.com/microsoftsearch/connectors-overview)
- [Graph Connectors](https://learn.microsoft.com/graph/connecting-external-content-connectors-overview)
- [Search external content](https://learn.microsoft.com/graph/search-concept-custom-types)

**Monitoring & Security**:
- [Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Azure Key Vault](https://learn.microsoft.com/azure/key-vault/)
- [Azure RBAC](https://learn.microsoft.com/azure/role-based-access-control/)
- [Azure security baseline](https://learn.microsoft.com/security/benchmark/azure/)

---

## License

MIT — See [LICENSE](../LICENSE) in repository root.
