# EventKit Decision Guide

**Choose the right integration pattern, platform, and adapter for your use case**

---

## 🎯 Quick Decision Trees

### 1. What Are You Building?

```
START: What type of application?
│
├─ 🤖 Conversational bot (chat interface)
│   ├─ For Microsoft Teams → Use Bot Adapter + Teams Bot
│   ├─ For Outlook → Use Bot Adapter + Outlook Integration
│   ├─ For custom web chat → Use Bot Adapter + WebChat
│   └─ For multiple channels → Use Bot Adapter (supports all)
│
├─ 🔌 Business process automation
│   ├─ Power Automate workflows → Use Power Adapter (Custom Connector)
│   ├─ Power Apps integration → Use Power Adapter (Custom Connector)
│   ├─ Logic Apps → Use Power Adapter (Custom Connector)
│   └─ Azure Functions → Use HTTP API or Foundry Adapter
│
├─ 🏭 AI agent/copilot with LLM orchestration
│   ├─ Azure AI Foundry → Use Foundry Adapter (Agent Framework)
│   ├─ Prompt Flow → Use Foundry Adapter (Prompt Flow integration)
│   ├─ Microsoft Copilot Studio → Use Power Adapter
│   └─ Custom orchestration → Use HTTP API directly
│
└─ 🌐 REST API integration
    ├─ Simple HTTP calls → Use HTTP API endpoints
    ├─ SDK in Python → Import adapters directly
    ├─ SDK in other languages → Use HTTP API
    └─ GraphQL → Use HTTP API (no GraphQL support yet)
```

---

## 🏗️ Integration Pattern Selection

### Decision Matrix

| If you need... | Use this | Why |
|----------------|----------|-----|
| **Conversational UI** in Teams/Outlook | Bot Adapter | Native Microsoft Bot Framework integration with Adaptive Cards |
| **Low-code automation** in Power Platform | Power Adapter | Generates OpenAPI spec for Custom Connectors |
| **AI orchestration** with Azure AI | Foundry Adapter | Integrates with Agent Framework and Prompt Flow |
| **Direct API access** from any language | HTTP API | Language-agnostic REST endpoints |
| **Python integration** in existing code | Base Adapter | Import as Python module, customize as needed |

### When to Use Each Adapter

#### 🤖 Bot Adapter (`adapters/bot_adapter.py`)

**Use when:**
- ✅ Building conversational experiences
- ✅ Need Adaptive Card support
- ✅ Deploying to Teams, Outlook, or WebChat
- ✅ Want rich interactive UI elements

**Don't use when:**
- ❌ Building headless automation (use Power Adapter)
- ❌ Need simple REST API (use HTTP API)
- ❌ Orchestrating with Prompt Flow (use Foundry Adapter)

**Example use cases:**
- Teams bot for employee event recommendations
- Outlook add-in for calendar-aware suggestions
- Customer support chat widget on website

#### 🏭 Foundry Adapter (`adapters/foundry_adapter.py`)

**Use when:**
- ✅ Building with Azure AI Foundry
- ✅ Using Agent Framework or Prompt Flow
- ✅ Need LLM orchestration capabilities
- ✅ Want AI evaluation and monitoring

**Don't use when:**
- ❌ Building for Power Platform (use Power Adapter)
- ❌ Need conversational UI (use Bot Adapter)
- ❌ Simple API integration (use HTTP API)

**Example use cases:**
- Multi-agent system in Azure AI Foundry
- Prompt Flow with tool calling
- AI-powered recommendation engine with RAG

#### 🔌 Power Adapter (`adapters/power_adapter.py`)

**Use when:**
- ✅ Building Power Automate flows
- ✅ Creating Power Apps
- ✅ Need Custom Connector for Logic Apps
- ✅ Low-code/no-code integration

**Don't use when:**
- ❌ Need conversational interface (use Bot Adapter)
- ❌ Building with Azure AI (use Foundry Adapter)
- ❌ Want direct Python integration (use Base Adapter)

**Example use cases:**
- Automated email workflows with recommendations
- Power Apps dashboard with session data
- Logic Apps integration for event processing

#### 🌐 HTTP API (`agent.py serve`)

**Use when:**
- ✅ Need language-agnostic integration
- ✅ Building microservices architecture
- ✅ Want simple REST endpoints
- ✅ Calling from JavaScript, Java, .NET, etc.

**Don't use when:**
- ❌ Python codebase (import adapters directly)
- ❌ Need Bot Framework features (use Bot Adapter)
- ❌ Building Custom Connectors (use Power Adapter)

**Example use cases:**
- Web application backend API
- Mobile app integration
- Third-party service integration

---

## 🚀 Platform Selection

### Hosting Decision Tree

```
START: Where will this run?
│
├─ Microsoft 365 environment only
│   ├─ Teams required → Deploy as Teams Bot (Bot Adapter)
│   ├─ Outlook required → Deploy as Outlook Bot (Bot Adapter)
│   ├─ SharePoint integration → Use Power Adapter
│   └─ Multiple M365 apps → Bot Adapter (supports all channels)
│
├─ Power Platform ecosystem
│   ├─ Power Automate → Deploy as Custom Connector (Power Adapter)
│   ├─ Power Apps → Deploy as Custom Connector (Power Adapter)
│   ├─ Copilot Studio → Deploy as Copilot action (Power Adapter)
│   └─ Dataverse → Power Adapter with Dataverse connector
│
├─ Azure AI development
│   ├─ Agent Framework → Azure AI Foundry (Foundry Adapter)
│   ├─ Prompt Flow → Azure AI Foundry (Foundry Adapter)
│   ├─ Azure OpenAI → Foundry Adapter or HTTP API
│   └─ Custom AI pipeline → HTTP API on Azure App Service
│
└─ General cloud/on-premises
    ├─ Azure → Azure App Service (HTTP API)
    ├─ AWS → Container deployment (HTTP API)
    ├─ On-premises → Docker container (HTTP API)
    └─ Kubernetes → Helm chart deployment (HTTP API)
```

### Platform Comparison

| Platform | Best For | Adapter | Deployment Complexity | Scalability |
|----------|----------|---------|----------------------|-------------|
| **Azure AI Foundry** | AI orchestration, multi-agent systems | Foundry | Medium | High (auto-scale) |
| **Power Platform** | Low-code automation, business workflows | Power | Low | Medium (platform-managed) |
| **Teams/Outlook** | Conversational experiences, M365 users | Bot | Medium | High (Bot Service) |
| **Azure App Service** | General web applications, REST APIs | HTTP API | Low | High (App Service) |
| **Docker/K8s** | Multi-cloud, on-premises, portability | HTTP API | High | Very High (manual) |

---

## 📊 Development Lifecycle Stages

### Stage 1: Prototyping & Development

**Goal**: Quickly test ideas and validate use cases

**Recommended approach:**
```
1. Start with CLI
   python agent.py recommend --interests "agents" --top 3

2. Move to HTTP API for testing
   python agent.py serve --port 8010

3. Use Bot Emulator for conversation testing
   python bot_server.py
   # Connect Bot Framework Emulator to localhost:3978
```

**Why this order:**
- CLI is fastest for logic testing
- HTTP API validates integration patterns
- Bot Emulator tests conversational flow without deployment

### Stage 2: Integration & Testing

**Goal**: Integrate with target platform and test end-to-end

**Choose integration path:**

#### Path A: Power Platform Integration
```
1. Generate OpenAPI spec (Power Adapter)
   from adapters.power_adapter import PowerAdapter
   adapter = PowerAdapter()
   spec = adapter.get_openapi_spec()

2. Create Custom Connector in Power Platform
   - Import OpenAPI spec
   - Configure authentication
   - Test actions

3. Build Power Automate flow or Power App
   - Use connector actions
   - Test with real data
```

#### Path B: Azure AI Foundry Integration
```
1. Create Foundry Adapter instance
   from adapters.foundry_adapter import FoundryAdapter
   adapter = FoundryAdapter()

2. Register as Agent Framework tool
   - Define tool manifest
   - Configure in Foundry project
   - Test with Agent Framework

3. Integrate with Prompt Flow
   - Add as custom tool
   - Build flow with orchestration
   - Evaluate with AI metrics
```

#### Path C: Teams Bot Integration
```
1. Test with Bot Emulator locally
   python bot_server.py
   # Emulator → localhost:3978/api/messages

2. Deploy to Azure and create Bot Service
   # See docs/deployment-guide.md

3. Configure Teams app and upload
   # Upload teams-app.json to Teams
   # Test in Teams client
```

### Stage 3: Production Deployment

**Goal**: Deploy reliably with monitoring and security

**Deployment checklist:**

✅ **Security**
- [ ] API authentication configured (tokens, OAuth)
- [ ] Secrets in Azure Key Vault (not environment variables)
- [ ] HTTPS enforced
- [ ] Input validation enabled

✅ **Monitoring**
- [ ] Application Insights connected
- [ ] Telemetry enabled
- [ ] Error alerting configured
- [ ] Performance metrics tracked

✅ **Scalability**
- [ ] Auto-scaling configured (if cloud)
- [ ] Resource limits set
- [ ] Load testing completed
- [ ] Caching strategy implemented

✅ **Reliability**
- [ ] Health check endpoint configured
- [ ] Graceful shutdown implemented
- [ ] Retry logic added
- [ ] Circuit breakers for external APIs

**Production platforms ranked by effort:**

| Platform | Setup Effort | Ongoing Maintenance | Best For |
|----------|-------------|---------------------|----------|
| Power Platform | Low | Low | Business users, automation |
| Azure AI Foundry | Medium | Low | AI developers, agent systems |
| Azure App Service | Low | Medium | General applications |
| Azure Bot Service | Medium | Medium | Conversational experiences |
| Kubernetes | High | High | Large-scale, multi-cloud |

---

## 🔀 Migration Paths

### From Prototype to Production

#### Scenario 1: CLI → Power Platform
```
1. Currently: python agent.py recommend --interests "agents"
2. Add Power Adapter:
   from adapters.power_adapter import PowerAdapter
   adapter = PowerAdapter()
3. Generate OpenAPI and create Custom Connector
4. Build Power Automate flow using connector
5. Deploy EventKit as Azure App Service for connector to call
```

#### Scenario 2: HTTP API → Teams Bot
```
1. Currently: Calling HTTP endpoints
2. Add Bot Adapter:
   from adapters.bot_adapter import BotAdapter
   adapter = BotAdapter()
3. Create bot_server.py using BotAdapter
4. Deploy to Azure Bot Service
5. Configure Teams app manifest and upload
```

#### Scenario 3: Custom Code → Azure AI Foundry
```
1. Currently: Custom Python integration
2. Refactor to use Foundry Adapter:
   from adapters.foundry_adapter import FoundryAdapter
   adapter = FoundryAdapter()
3. Register tools with Agent Framework
4. Create Foundry project and deploy
5. Build Prompt Flow or multi-agent system
```

### Adding Capabilities

#### Add Conversational UI to Existing API
```
Before: HTTP API only
After: HTTP API + Teams Bot

Steps:
1. Keep existing HTTP server running
2. Add BotAdapter for conversational interface
3. Deploy bot_server.py alongside API
4. Both can share same core logic
```

#### Add Low-Code Access to Existing Bot
```
Before: Teams Bot only
After: Teams Bot + Power Platform

Steps:
1. Add PowerAdapter alongside BotAdapter
2. Generate OpenAPI spec
3. Create Custom Connector
4. Now accessible from both Teams AND Power Platform
```

---

## 🎓 Skill Level Recommendations

### For Citizen Developers (Low-Code/No-Code)

**Recommended path:**
1. Use deployed HTTP API or Power Adapter
2. Create Custom Connector in Power Platform
3. Build flows/apps with visual designer
4. No coding required

**Documentation:**
- [docs/EXTENSIBILITY_GUIDE.md](EXTENSIBILITY_GUIDE.md) - Power Platform section
- [docs/api-guide.md](api-guide.md) - API reference for connector

### For Python Developers

**Recommended path:**
1. Import adapters directly in code
2. Use Base Adapter or specialized adapters
3. Customize and extend as needed
4. Deploy as Python application

**Documentation:**
- [docs/UNIFIED_ADAPTER_ARCHITECTURE.md](UNIFIED_ADAPTER_ARCHITECTURE.md) - Adapter patterns
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Development setup

### For Bot/Conversational AI Developers

**Recommended path:**
1. Use Bot Adapter
2. Deploy to Azure Bot Service
3. Integrate with Teams, Outlook, WebChat
4. Leverage Adaptive Cards

**Documentation:**
- [docs/agents-sdk-setup.md](agents-sdk-setup.md) - Teams/Copilot integration
- [LOCAL_TESTING.md](../LOCAL_TESTING.md) - Bot testing guide

### For AI/ML Engineers

**Recommended path:**
1. Use Foundry Adapter
2. Deploy to Azure AI Foundry
3. Integrate with Agent Framework or Prompt Flow
4. Add AI evaluation metrics

**Documentation:**
- [docs/foundry-deployment.md](foundry-deployment.md) - Azure AI Foundry guide
- [docs/UNIFIED_ADAPTER_ARCHITECTURE.md](UNIFIED_ADAPTER_ARCHITECTURE.md) - Foundry Adapter section

---

## 💡 Common Scenarios

### Scenario: Internal Employee Tool

**Requirements:**
- Used by employees in Microsoft 365
- Need conversational interface
- Should work in Teams and Outlook

**Recommended solution:**
- **Adapter**: Bot Adapter
- **Platform**: Azure Bot Service + Teams
- **Why**: Native M365 integration, employees already use Teams

### Scenario: Business Process Automation

**Requirements:**
- Automate workflows based on events
- Non-technical users should manage
- Integration with existing Power Platform

**Recommended solution:**
- **Adapter**: Power Adapter
- **Platform**: Power Automate + Custom Connector
- **Why**: Low-code, business users can build flows

### Scenario: AI Research Platform

**Requirements:**
- Experiment with multi-agent systems
- Need LLM orchestration
- Evaluate and improve AI performance

**Recommended solution:**
- **Adapter**: Foundry Adapter
- **Platform**: Azure AI Foundry
- **Why**: Built for AI development, evaluation tools

### Scenario: Public API for Partners

**Requirements:**
- External partners need API access
- Language-agnostic integration
- Need authentication and rate limiting

**Recommended solution:**
- **Adapter**: HTTP API
- **Platform**: Azure App Service + API Management
- **Why**: REST API, authentication, governance

### Scenario: Multi-Channel Customer Service

**Requirements:**
- Support web chat, Teams, Outlook
- Consistent experience across channels
- Rich interactive UI

**Recommended solution:**
- **Adapter**: Bot Adapter
- **Platform**: Azure Bot Service
- **Why**: Multi-channel support, Adaptive Cards

---

## 🔍 Quick Reference Checklist

### Choose Bot Adapter if:
- [ ] Building conversational interface
- [ ] Need Adaptive Cards
- [ ] Deploying to Teams, Outlook, or WebChat
- [ ] Want multi-channel support

### Choose Foundry Adapter if:
- [ ] Using Azure AI Foundry
- [ ] Need Agent Framework or Prompt Flow
- [ ] Building AI orchestration
- [ ] Want AI evaluation tools

### Choose Power Adapter if:
- [ ] Building in Power Platform
- [ ] Need Custom Connector
- [ ] Low-code/no-code requirement
- [ ] Business process automation

### Choose HTTP API if:
- [ ] Language-agnostic integration
- [ ] Simple REST endpoints
- [ ] Microservices architecture
- [ ] Public API for partners

---

## 📖 Next Steps

After making your decision:

1. **Read the integration guide**:
   - Bot Adapter: [docs/agents-sdk-setup.md](agents-sdk-setup.md)
   - Foundry Adapter: [docs/foundry-deployment.md](foundry-deployment.md)
   - Power Adapter: [docs/EXTENSIBILITY_GUIDE.md](EXTENSIBILITY_GUIDE.md)
   - HTTP API: [docs/api-guide.md](api-guide.md)

2. **Review architecture**:
   - [docs/UNIFIED_ADAPTER_ARCHITECTURE.md](UNIFIED_ADAPTER_ARCHITECTURE.md)

3. **Set up development environment**:
   - [QUICKSTART.md](../QUICKSTART.md)
   - [DEVELOPMENT.md](../DEVELOPMENT.md)

4. **Test locally**:
   - [LOCAL_TESTING.md](../LOCAL_TESTING.md)

5. **Deploy to production**:
   - [docs/deployment-guide.md](deployment-guide.md)

---

**Still not sure?** Check [docs/troubleshooting.md](troubleshooting.md) or open an issue on GitHub.
