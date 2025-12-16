# Agent ADK Dev Environment - Scaffolding Analysis

## Current State

### ✅ What's Already Built
1. **Core Agent Logic** (`agent.py`, `core.py`)
   - Session recommendation with scoring (interest, popularity, diversity)
   - Session explanation with matched tags
   - HTTP server with Adaptive Card support
   - CLI interface for all operations

2. **Configuration & Manifest**
   - `agent.json` manifest (sessions, weights, feature flags)
   - `settings.py` with Pydantic BaseSettings (partially configured)
   - `.env.example` with Graph credential placeholders

3. **Observability**
   - Telemetry system (`telemetry.py`) with JSONL logging
   - Structured event logging for all actions
   - Profile persistence (`~/.event_agent_profiles.json`)

4. **Testing**
   - Unit tests for recommend, explain, export, profile
   - Server integration tests
   - Test coverage for telemetry

5. **Runtime Modes**
   - `custom-chat`: Standalone HTTP server
   - `m365-agent`: Agents SDK integration (partial - references external path)
   - `sharepoint-agent`: Publishing to SharePoint (scaffolding only)

---

## ❌ Missing for Full ADK Dev Environment with MSL/Graph Auth

### **Priority 1: Critical Authentication & Authorization**

#### 1. **MSAL Authentication Layer**
- **Status**: Placeholder in `.env.example`
- **Missing**:
  - MSAL Python package (`msal`)
  - `graph_auth.py` module with MSAL client initialization
  - Token cache management (file-based or in-memory)
  - Client credentials flow for service accounts
  - Interactive login flow for user context
  - Token refresh/retry logic

#### 2. **Microsoft Graph API Integration**
- **Status**: Not implemented
- **Missing**:
  - Graph API client wrapper module (`graph_service.py`)
  - Calendar endpoint integration (fetch user/tenant events)
  - People search / user lookup endpoints
  - Event metadata transformation (Graph format → agent.json format)
  - Rate limiting & retry strategies
  - Error handling for Graph API failures

#### 3. **Credential Management**
- **Status**: Environment variables defined but not used
- **Missing**:
  - Environment variable validation at startup
  - Secure credential storage (KeyVault integration or encrypted local storage)
  - Tenant ID / Client ID / Client Secret handling
  - Multi-tenant support (if needed)

---

### **Priority 2: Agent ADK Integration**

#### 1. **Microsoft 365 Agents SDK Setup**
- **Status**: References external path (`innovation-kit-repository/event-agent/...`)
- **Missing**:
  - Agents SDK package dependency in `pyproject.toml`
  - Agent declaration file (JSON schema for Agents SDK)
  - Request/response adapter for Agents SDK message format
  - Activity handler integration
  - Turn context handling
  - State management (conversation state, user state)

#### 2. **Declarative Agent Configuration**
- **Status**: `agent.json` exists but not in Agents SDK format
- **Missing**:
  - Agents SDK manifest schema (actions, capabilities, instructions)
  - Plugin registration for recommendation/explanation
  - Tool definitions for Graph integration
  - System prompt definition
  - Instructions for context-awareness

#### 3. **Teams/Copilot Hosting**
- **Status**: Incomplete in `runner.py`
- **Missing**:
  - Bot Framework adapter setup
  - Teams activity handler
  - Copilot plugin manifest (`copilot-manifest.json`)
  - OAuth connection setup for Teams

---

### **Priority 3: Enterprise Features**

#### 1. **Logging & Monitoring**
- **Status**: Basic telemetry exists
- **Missing**:
  - Application Insights integration (structured logging)
  - Distributed tracing support
  - Log levels (DEBUG, INFO, WARN, ERROR)
  - Correlation IDs for request tracking
  - Performance metrics (latency percentiles)

#### 2. **Configuration Management**
- **Status**: `settings.py` uses Pydantic but incomplete
- **Missing**:
  - Full environment variable mapping
  - Configuration validation at startup
  - Feature flags in settings (currently only in agent.json)
  - Secrets management integration
  - Multi-environment configs (dev, staging, prod)

#### 3. **Security & Validation**
- **Status**: Basic Bearer token validation in HTTP server
- **Missing**:
  - Input validation middleware
  - CORS configuration
  - Rate limiting
  - Request size limits
  - SQL injection / prompt injection protection
  - Token validation against Azure AD

---

### **Priority 4: Deployment & Infrastructure**

#### 1. **Container Support**
- **Status**: `Dockerfile` and `docker-compose.yml` exist
- **Missing**:
  - Multi-stage build optimization
  - Health check endpoint configuration
  - Environment variable injection
  - Volume mounts for logs/data
  - Network configuration

#### 2. **Azure Deployment**
- **Status**: Not present
- **Missing**:
  - Bicep/Terraform IaC templates
  - App Service / Container App deployment configs
  - Azure SQL / Cosmos DB setup (if persistence needed)
  - Key Vault integration
  - Managed Identity setup
  - CI/CD pipeline (GitHub Actions / Azure Pipelines)

#### 3. **Local Development**
- **Status**: Basic setup documented
- **Missing**:
  - VSCode dev container configuration (`.devcontainer/`)
  - Development dependency management
  - Pre-commit hooks
  - Makefile / scripts for common tasks
  - Environment setup scripts

---

### **Priority 5: Documentation & Examples**

#### 1. **Setup Documentation**
- **Status**: `QUICKSTART.md`, `README.md` exist
- **Missing**:
  - MSAL auth setup guide (step-by-step)
  - Graph API scopes & permissions explained
  - Agents SDK integration walkthrough
  - Deployment guide (local → Azure)
  - Troubleshooting common auth issues

#### 2. **API Documentation**
- **Status**: OpenAPI snippet in `docs/`
- **Missing**:
  - Complete OpenAPI/Swagger spec
  - API authentication examples
  - Request/response samples
  - Error codes reference

#### 3. **Code Examples**
- **Status**: Basic examples exist
- **Missing**:
  - Graph event fetching example
  - Token refresh example
  - Error handling patterns
  - Mock/test Graph responses

---

## 📋 Detailed Implementation Plan

### **PHASE 1: Foundation & Authentication (Tasks 1-15)**

#### **Task 1: Update Dependencies**
- [ ] Open `pyproject.toml`
- [ ] Add MSAL, msgraph-core, azure-identity, pydantic-settings
- [ ] Add dev dependencies (pytest, responses, pytest-cov)
- [ ] Run `pip install -e .` to validate

#### **Task 2: Enhance Settings Configuration**
- [ ] Update `settings.py` with:
  - `graph_tenant_id: str`
  - `graph_client_id: str`
  - `graph_client_secret: SecretStr`
  - `app_insights_connection_string: Optional[str]`
  - Validation: raise if Graph vars missing when mode=m365-agent
- [ ] Add `Config.env_file = ".env"`
- [ ] Create actual `.env` from `.env.example`

#### **Task 3: Create MSAL Authentication Module**
- [ ] Create `graph_auth.py` with:
  - `GraphAuthClient` class
    - `__init__(settings: Settings)`
    - `get_access_token() -> str` (with caching)
    - `_acquire_token_for_client() -> str` (MSAL flow)
    - `_refresh_token_if_expired()` (cache logic)
  - Token file cache: `~/.event_agent_token_cache.json`
- [ ] Add error handling for auth failures
- [ ] Add logging for token acquisition

#### **Task 4: Write Auth Unit Tests**
- [ ] Create `tests/test_graph_auth.py`
- [ ] Test token acquisition (mock MSAL)
- [ ] Test token caching
- [ ] Test token refresh
- [ ] Test missing credentials error handling

#### **Task 5: Create Graph Service Module**
- [ ] Create `graph_service.py` with:
  - `GraphEventService` class
    - `__init__(auth_client: GraphAuthClient, cache_ttl: int = 300)`
    - `fetch_user_events(user_id: str) -> List[Dict]`
    - `fetch_calendar_events(calendar_id: str) -> List[Dict]`
  - Response transformation: Graph → agent schema
    - Map `subject` → `title`
    - Map `start.dateTime` → `start`
    - Map `end.dateTime` → `end`
    - Map `location.displayName` → `location`
    - Derive `tags` from subject keywords
- [ ] Add caching with TTL
- [ ] Add error handling for API failures
- [ ] Rate limiting: respect Retry-After headers

#### **Task 6: Write Graph Service Tests**
- [ ] Create `tests/test_graph_service.py`
- [ ] Mock Graph API responses
- [ ] Test event transformation
- [ ] Test caching behavior
- [ ] Test error handling (401, 429, 500)
- [ ] Test rate limit backoff

#### **Task 7: Update Core Module**
- [ ] Modify `core.py`:
  - Add `recommend_from_graph(user_id, interests, top_n) -> Dict`
  - Inject `GraphEventService` dependency
  - Reuse existing scoring logic
- [ ] Keep backward compatibility with manifest-based sessions

#### **Task 8: Update Agent CLI**
- [ ] Add `--source` flag to `agent.py recommend`:
  - `--source manifest` (default, current behavior)
  - `--source graph` (fetch from Graph)
- [ ] Add `--user-id` flag (required when `--source graph`)
- [ ] Example: `python agent.py recommend --source graph --user-id user@tenant.onmicrosoft.com --interests "ai, agents"`

#### **Task 9: Add Graph Endpoint to HTTP Server**
- [ ] Add `/recommend-graph?user_id=...&interests=...` endpoint
- [ ] Add `/health-graph` to test Graph connectivity
- [ ] Return 401 if credentials missing
- [ ] Telemetry for Graph calls

#### **Task 10: Create Integration Test**
- [ ] Create `tests/test_graph_integration.py`
- [ ] End-to-end: auth → fetch events → recommend
- [ ] Mock full Graph API flow
- [ ] Verify scoring works with real Graph schema

#### **Task 11: Add Logging & Observability**
- [ ] Update `telemetry.py` to track:
  - Graph API calls (user_id, latency, errors)
  - Token acquisition events
  - Cache hits/misses
- [ ] Add structured logging to `graph_auth.py`, `graph_service.py`
- [ ] Add correlation IDs for request tracing

#### **Task 12: Documentation**
- [ ] Create `docs/graph-setup.md`:
  - How to register app in Azure AD
  - Required scopes (Calendars.Read, etc.)
  - Creating service account vs interactive
  - Setting up `.env`
- [ ] Update `QUICKSTART.md` with Graph examples
- [ ] Add troubleshooting section

#### **Task 13: Local Testing**
- [ ] Copy `.env.example` → `.env`
- [ ] Populate with real Azure AD credentials
- [ ] Test `python agent.py recommend --source graph --user-id <email>`
- [ ] Verify token caching works
- [ ] Test HTTP server endpoints

#### **Task 14: Security Hardening**
- [ ] Validate all Graph credentials at startup (`settings.py`)
- [ ] Mask secrets in logs
- [ ] Add rate limiting to `/recommend-graph`
- [ ] Input validation on user_id, interests

#### **Task 15: Dependency Lock**
- [ ] Generate `requirements.txt` from `pyproject.toml`
- [ ] Test in clean venv

---

### **PHASE 2: Agents SDK Integration (Tasks 16-25)**

#### **Task 16: Add Agents SDK to Dependencies**
- [ ] Update `pyproject.toml`:
  - `azure-ai-projects>=0.1.0` (or latest Agents SDK)
  - `azure-identity>=1.14.0`
- [ ] Run `pip install -e .`

#### **Task 17: Create Agent Declaration File**
- [ ] Create `agent-declaration.json`:
  ```json
  {
    "schema_version": "1.0",
    "name": "Event Kit Agent",
    "instructions": "You recommend relevant conference sessions based on user interests.",
    "capabilities": [
      {
        "name": "recommend_sessions",
        "description": "Get session recommendations",
        "parameters": {
          "interests": "string (comma-separated)",
          "top_n": "integer"
        }
      },
      {
        "name": "explain_session",
        "description": "Explain why a session matches interests",
        "parameters": {
          "session_title": "string",
          "interests": "string"
        }
      }
    ]
  }
  ```

#### **Task 18: Create Agents SDK Adapter**
- [ ] Create `agents_sdk_adapter.py`:
  - `EventKitAgent` class (inherits from SDK base)
  - `handle_recommend_tool_call(interests, top_n) -> str`
  - `handle_explain_tool_call(title, interests) -> str`
  - Message formatting for Teams/Copilot
- [ ] Integrate with existing `core.py` logic
- [ ] Handle errors gracefully

#### **Task 19: Update Runner for SDK Mode**
- [ ] Modify `runner.py`:
  - Implement `run_m365_agent(port)` fully
  - Initialize Agents SDK client
  - Load agent declaration
  - Start server on port
- [ ] Validate credentials before starting
- [ ] Add startup logging

#### **Task 20: Create Teams Activity Handler**
- [ ] Create `teams_activity_handler.py`:
  - Handle incoming activity messages
  - Route to agent via SDK
  - Format responses for Teams
  - Error handling

#### **Task 21: Generate Teams Bot Manifest**
- [ ] Create `teams-manifest.json`:
  - Bot ID (from Azure AD app)
  - Scopes, commands
  - Messaging endpoints
- [ ] Document how to upload to Teams

#### **Task 22: Write SDK Integration Tests**
- [ ] Create `tests/test_agents_sdk.py`
- [ ] Test adapter tool calling
- [ ] Test message formatting
- [ ] Test error scenarios

#### **Task 23: Create Copilot Plugin Manifest** (Optional)
- [ ] Create `copilot-manifest.json` if targeting Copilot
- [ ] Define plugin capabilities
- [ ] Setup OAuth2 flow if needed

#### **Task 24: SDK Documentation**
- [ ] Create `docs/agents-sdk-setup.md`:
  - SDK installation & setup
  - Agent declaration format
  - Tool implementation patterns
  - Teams deployment steps
  - Troubleshooting

#### **Task 25: End-to-End SDK Test**
- [ ] Test locally with Teams Bot Emulator
- [ ] Verify recommend/explain tools work
- [ ] Test Graph integration path

---

### **PHASE 3: Enterprise & Deployment (Tasks 26-35)**

#### **Task 26: Application Insights Setup**
- [ ] Update `telemetry.py`:
  - Initialize App Insights client if connection string set
  - Send telemetry events to App Insights
  - Structured logging with custom properties
  - Exception tracking
- [ ] Update `settings.py` with `app_insights_connection_string`

#### **Task 27: Distributed Tracing**
- [ ] Add correlation ID generation
- [ ] Propagate across requests
- [ ] Log in structured format (W3C trace context)
- [ ] Track in App Insights

#### **Task 28: Security Middleware**
- [ ] Add input validation:
  - Interests: alphanumeric + common separators only
  - User IDs: email format validation
  - Session titles: length limits
- [ ] Add rate limiting (e.g., 100 req/min per IP)
- [ ] Add request size limits
- [ ] CORS configuration

#### **Task 29: Enhanced Error Handling**
- [ ] Create `errors.py` with custom exceptions:
  - `GraphAuthError`
  - `GraphAPIError`
  - `InvalidInput`
- [ ] Consistent error response format
- [ ] User-friendly error messages

#### **Task 30: Create Bicep Templates**
- [ ] Create `infra/main.bicep`:
  - Azure App Service or Container App
  - Azure SQL for profile persistence (optional)
  - Key Vault for secrets
  - Application Insights
  - Storage for logs
- [ ] Create parameter files: `dev.bicepparam`, `prod.bicepparam`
- [ ] Document resource naming conventions

#### **Task 31: Docker Optimization**
- [ ] Update `Dockerfile`:
  - Multi-stage build
  - Python slim base image
  - Health check command
  - Environment variables
- [ ] Update `docker-compose.yml` for local dev
- [ ] Test image build & run

#### **Task 32: Dev Container Setup**
- [ ] Create `.devcontainer/devcontainer.json`:
  - Python 3.11 base
  - VSCode extensions (Pylance, Python, REST Client)
  - Mount workspace
  - Preinstall dependencies
- [ ] Add `.devcontainer/Dockerfile` if needed
- [ ] Document opening in Dev Container

#### **Task 33: CI/CD Pipeline**
- [ ] Create `.github/workflows/`:
  - `test.yml`: Run tests on PR
  - `lint.yml`: Pylint, black, isort
  - `deploy.yml`: Deploy to Azure on merge
- [ ] Or Azure Pipelines if preferred
- [ ] Secrets: AZURE_CREDENTIALS, etc.

#### **Task 34: Deployment Documentation**
- [ ] Create `docs/deployment.md`:
  - Local dev setup
  - Docker local run
  - Azure deployment (Bicep)
  - Environment configuration
  - Health checks
  - Monitoring setup

#### **Task 35: Testing & Validation**
- [ ] Run full test suite: `pytest tests/ -v --cov`
- [ ] Integration test against real Azure AD (in separate env)
- [ ] Load testing (optional): 100 concurrent requests
- [ ] Security checklist

---

### **PHASE 4: Polish & Documentation (Tasks 36-40)**

#### **Task 36: Update README**
- [ ] Add Architecture diagram (Graph → Agent → Teams)
- [ ] Link to setup guides
- [ ] Quick start sections for each mode
- [ ] Support & troubleshooting

#### **Task 37: Create Architecture Document**
- [ ] `docs/architecture.md`:
  - Component diagram
  - Data flow (manifest vs Graph)
  - Auth flow (MSAL)
  - Agents SDK hosting
  - Deployment architecture

#### **Task 38: Create Operations Guide**
- [ ] `docs/operations.md`:
  - Monitoring checklist
  - Common issues & fixes
  - Scaling considerations
  - Backup/recovery

#### **Task 39: Sample Graph Events**
- [ ] Create `assets/sample_graph_events.json`:
  - Real Graph API responses
  - For testing & documentation

#### **Task 40: Final QA**
- [ ] Walk through all scenarios:
  - Local manifest mode
  - Local Graph mode
  - Teams/Copilot via SDK
  - Azure deployment
- [ ] Verify all docs are accurate
- [ ] Update CHANGELOG.md
- [ ] Tag release v1.0.0

---

## 🔧 Quick Start Checklist for Manual Setup

If implementing manually (without scaffolding tools):

### **Authentication**
- [ ] Install `msal` package
- [ ] Create `.env` with real credentials
- [ ] Implement MSAL token flow
- [ ] Test token acquisition

### **Graph API**
- [ ] Register application in Azure AD
- [ ] Grant Calendar.Read, Calendars.Read scopes
- [ ] Fetch sample calendar events
- [ ] Verify transformation to agent schema

### **Agents SDK**
- [ ] Install Agents SDK package
- [ ] Create agent manifest (JSON)
- [ ] Build activity handler
- [ ] Test with Teams emulator

### **Deployment**
- [ ] Create `.devcontainer/` config
- [ ] Write Bicep templates
- [ ] Setup Azure resources
- [ ] Test end-to-end locally & in Azure

---

## 📦 Dependency Additions Required

```toml
# Current
requires-python = ">=3.11"
dependencies = []

# Needed for full ADK environment
dependencies = [
    "msal>=1.25.0",           # MSAL authentication
    "msgraph-core>=1.0.0",    # Microsoft Graph SDK
    "pydantic>=2.0",          # Settings validation (partially there)
    "pydantic-settings>=2.0", # Env var handling
    "azure-identity>=1.14.0", # Azure auth utilities
    "azure-monitor-opentelemetry>=1.0.0",  # App Insights
]

# Dev dependencies
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0",
    "responses>=0.23.0",  # Mock HTTP responses
]
```

---

## Summary

**Current Gap**: This is a solid **local demo agent** with observability. To make it production-ready with Microsoft Graph and Agents SDK hosting:

| Component | Status | Effort |
|-----------|--------|--------|
| MSAL Auth | 10% | Medium |
| Graph API Integration | 0% | Medium |
| Agents SDK Hosting | 20% | High |
| Enterprise Logging | 20% | Low |
| Azure Deployment | 0% | High |
| Documentation | 40% | Low |

**Total scaffolding needed**: ~3-4 weeks for a full enterprise-ready implementation.
