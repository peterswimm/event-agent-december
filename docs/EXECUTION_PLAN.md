# Execution Plan - Agent ADK Development

## Overview

This plan breaks down the scaffolding work into 40 actionable tasks across 4 phases:
- **Phase 1**: Authentication & Graph API (15 tasks, ~2 weeks)
- **Phase 2**: Agents SDK Integration (10 tasks, ~1.5 weeks)
- **Phase 3**: Enterprise & Deployment (10 tasks, ~1.5 weeks)
- **Phase 4**: Polish & Documentation (5 tasks, ~1 week)

**Total: ~6 weeks of development**

---

## How to Execute

### Daily Workflow
1. Pick 2-3 tasks from current phase
2. Create a new branch: `git checkout -b feature/task-X-description`
3. Complete task checklist items
4. Run tests: `pytest tests/ -v`
5. Commit & push
6. Mark task complete here

### Progress Tracking
- [ ] = Not started
- [x] = Complete
- [~] = In progress

---

## PHASE 1: Foundation & Authentication (Week 1-2)

### TASK 1: Update Dependencies ⏱️ Est: 30 min

**Branch**: `feature/task-1-deps`

**Checklist**:
- [ ] Open [pyproject.toml](pyproject.toml)
- [ ] Replace `dependencies = []` with:
  ```toml
  dependencies = [
      "msal>=1.25.0",
      "msgraph-core>=1.0.0",
      "pydantic-settings>=2.0.0",
      "azure-identity>=1.14.0",
  ]
  ```
- [ ] Add `[project.optional-dependencies]` section:
  ```toml
  [project.optional-dependencies]
  dev = [
      "pytest>=7.0",
      "pytest-asyncio>=0.21.0",
      "pytest-cov>=4.0",
      "responses>=0.23.0",
  ]
  ```
- [ ] Run: `pip install -e ".[dev]"`
- [ ] Verify: `pip list | grep msal`
- [ ] Commit: `git add pyproject.toml && git commit -m "chore: add MSAL and Graph dependencies"`

**Success Criteria**: All packages install without errors

---

### TASK 2: Enhance Settings Configuration ⏱️ Est: 45 min

**Branch**: `feature/task-2-settings`

**Checklist**:
- [ ] Update [settings.py](settings.py):
  - Add Graph-related fields with validation
  - Add App Insights field
  - Create `.env` validation method
- [ ] Create actual `.env` from `.env.example`:
  ```bash
  cp .env.example .env
  ```
- [ ] Edit `.env` and set temporary test values
- [ ] Write test: `tests/test_settings.py`
  - Test missing Graph vars when mode=m365-agent
  - Test .env loading
- [ ] Run: `pytest tests/test_settings.py -v`

**Files to Create**:
- Update: [settings.py](settings.py)
- Create: [tests/test_settings.py](tests/test_settings.py)
- Create: `.env` (from `.env.example`)

**Success Criteria**: Settings validate Graph credentials, test passes

---

### TASK 3: Create MSAL Authentication Module ⏱️ Est: 1.5 hours

**Branch**: `feature/task-3-msal-auth`

**Checklist**:
- [ ] Create [graph_auth.py](graph_auth.py) with:
  - `GraphAuthClient` class
  - Token caching to `~/.event_agent_token_cache.json`
  - `get_access_token()` method
  - `_acquire_token_for_client()` method
  - `_refresh_token_if_expired()` method
  - Error handling (InvalidClientError, etc.)
  - Logging statements
- [ ] Test manual instantiation:
  ```python
  from settings import Settings
  from graph_auth import GraphAuthClient
  
  settings = Settings()  # loads from .env
  auth = GraphAuthClient(settings)
  token = auth.get_access_token()
  print(f"Token: {token[:20]}...")
  ```
- [ ] Verify cache file created
- [ ] Commit changes

**Files to Create**:
- Create: [graph_auth.py](graph_auth.py)

**Dependencies**:
- Task 1 & 2 must be complete

**Success Criteria**: Token acquired & cached successfully

---

### TASK 4: Write Auth Unit Tests ⏱️ Est: 1 hour

**Branch**: `feature/task-4-auth-tests`

**Checklist**:
- [ ] Create [tests/test_graph_auth.py](tests/test_graph_auth.py)
- [ ] Mock MSAL ConfidentialClientApplication
- [ ] Write tests:
  - `test_init_with_valid_settings`
  - `test_get_access_token_caches_result`
  - `test_refresh_token_on_expiry`
  - `test_invalid_credentials_raises_error`
- [ ] Run: `pytest tests/test_graph_auth.py -v --cov=graph_auth`

**Files to Create**:
- Create: [tests/test_graph_auth.py](tests/test_graph_auth.py)

**Dependencies**: Task 3 complete

**Success Criteria**: All tests pass with >80% coverage

---

### TASK 5: Create Graph Service Module ⏱️ Est: 2 hours

**Branch**: `feature/task-5-graph-service`

**Checklist**:
- [ ] Create [graph_service.py](graph_service.py):
  - `GraphEventService` class
  - `__init__(auth_client, cache_ttl=300)`
  - `fetch_user_events(user_id) -> List[Dict]`
  - `_transform_graph_event(event_json) -> Dict` (Graph → agent schema)
  - Response caching with TTL
  - Rate limit handling (check Retry-After header)
  - Error handling (401, 429, 500)
- [ ] Mapping:
  - `subject` → `title`
  - `start.dateTime` → `start`
  - `end.dateTime` → `end`
  - `location.displayName` → `location`
  - Generate `tags` from subject keywords (parse "AI", "agents", etc.)
  - Default `popularity: 0.5`
- [ ] Add logging for all API calls
- [ ] Manual test:
  ```python
  from graph_auth import GraphAuthClient
  from graph_service import GraphEventService
  from settings import Settings
  
  auth = GraphAuthClient(Settings())
  svc = GraphEventService(auth)
  events = svc.fetch_user_events("user@tenant.onmicrosoft.com")
  ```

**Files to Create**:
- Create: [graph_service.py](graph_service.py)

**Dependencies**: Task 3 & 1 complete

**Success Criteria**: Service retrieves & transforms events correctly

---

### TASK 6: Write Graph Service Tests ⏱️ Est: 1.5 hours

**Branch**: `feature/task-6-service-tests`

**Checklist**:
- [ ] Create [tests/test_graph_service.py](tests/test_graph_service.py)
- [ ] Mock graph_core responses with realistic Graph API JSON
- [ ] Write tests:
  - `test_fetch_user_events_returns_list`
  - `test_event_transformation_mapping`
  - `test_caching_ttl_behavior`
  - `test_rate_limit_429_backoff`
  - `test_unauthorized_401_raises_error`
  - `test_tags_extracted_from_subject`
- [ ] Run: `pytest tests/test_graph_service.py -v --cov=graph_service`

**Files to Create**:
- Create: [tests/test_graph_service.py](tests/test_graph_service.py)
- Create: [tests/fixtures/graph_responses.json](tests/fixtures/graph_responses.json) (mock data)

**Dependencies**: Task 5 complete

**Success Criteria**: All tests pass, >85% coverage

---

### TASK 7: Update Core Module ⏱️ Est: 1 hour

**Branch**: `feature/task-7-core-graph`

**Checklist**:
- [ ] Update [core.py](core.py):
  - Add `recommend_from_graph(user_id, interests, top_n, service) -> Dict`
  - Reuse existing scoring logic
  - Accept `GraphEventService` as parameter
- [ ] Keep backward compatibility with manifest-based `recommend()`
- [ ] Test manually:
  ```python
  from core import recommend_from_graph
  from graph_service import GraphEventService
  from graph_auth import GraphAuthClient
  
  auth = GraphAuthClient(...)
  svc = GraphEventService(auth)
  result = recommend_from_graph("user@tenant.com", ["ai", "agents"], 3, svc)
  print(result)
  ```

**Files to Update**:
- Update: [core.py](core.py)

**Dependencies**: Task 5 complete

**Success Criteria**: Graph-based recommendation works with existing score logic

---

### TASK 8: Update Agent CLI ⏱️ Est: 1.5 hours

**Branch**: `feature/task-8-cli-source`

**Checklist**:
- [ ] Update [agent.py](agent.py) `recommend` command:
  - Add `--source` flag: `manifest` (default) | `graph`
  - Add `--user-id` flag (required if `--source graph`)
  - Conditionally call `recommend()` or `recommend_from_graph()`
- [ ] Update argparse setup
- [ ] Test commands:
  ```bash
  python agent.py recommend --interests "ai, agents" --top 3
  python agent.py recommend --source graph --user-id "user@tenant.com" --interests "ai, agents" --top 3
  ```
- [ ] Verify both work

**Files to Update**:
- Update: [agent.py](agent.py)

**Dependencies**: Task 7 complete

**Success Criteria**: Both `--source manifest` and `--source graph` work

---

### TASK 9: Add Graph Endpoint to HTTP Server ⏱️ Est: 1 hour

**Branch**: `feature/task-9-http-graph`

**Checklist**:
- [ ] Update HTTP server handler in [agent.py](agent.py):
  - Add `GET /recommend-graph` endpoint
  - Query params: `user_id`, `interests`, `top`, `card` (optional)
  - Validate user_id format (email)
  - Return 400 if missing params
  - Return 401 if Graph credentials not configured
  - Call `core.recommend_from_graph()`
  - Wrap in try/catch, return 500 on Graph errors
  - Add to telemetry
- [ ] Test:
  ```bash
  python agent.py serve --port 8010
  curl "http://localhost:8010/recommend-graph?user_id=user@tenant.com&interests=ai,agents&top=3"
  ```

**Files to Update**:
- Update: [agent.py](agent.py)

**Dependencies**: Task 8 complete

**Success Criteria**: Endpoint returns recommendations or appropriate error

---

### TASK 10: Create Integration Test ⏱️ Est: 1.5 hours

**Branch**: `feature/task-10-integration`

**Checklist**:
- [ ] Create [tests/test_graph_integration.py](tests/test_graph_integration.py)
- [ ] End-to-end test flow:
  1. Mock MSAL token acquisition
  2. Mock Graph API calendar response
  3. Call `recommend_from_graph()`
  4. Verify scoring works with real Graph schema
  5. Verify events transformed correctly
- [ ] Test error scenarios:
  - Invalid credentials → raises GraphAuthError
  - Graph API 429 → retries with backoff
  - Empty calendar → returns empty recommendations
- [ ] Run: `pytest tests/test_graph_integration.py -v`

**Files to Create**:
- Create: [tests/test_graph_integration.py](tests/test_graph_integration.py)

**Dependencies**: Tasks 6 & 7 complete

**Success Criteria**: Full flow works end-to-end with mocks

---

### TASK 11: Add Logging & Observability ⏱️ Est: 1.5 hours

**Branch**: `feature/task-11-observability`

**Checklist**:
- [ ] Update [telemetry.py](telemetry.py):
  - Track Graph API calls with latency
  - Log cache hits/misses
  - Log token acquisition events
  - Add correlation IDs (UUID per request)
- [ ] Add structured logging to:
  - [graph_auth.py](graph_auth.py): token events
  - [graph_service.py](graph_service.py): API calls, cache, rate limits
- [ ] Add logging statements:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.info("Acquired token", extra={"cached": False, "latency_ms": 45})
  logger.warning("Rate limited, backing off", extra={"retry_after": 60})
  ```
- [ ] Test:
  ```bash
  python agent.py recommend --source graph --user-id "user@tenant.com" --interests "ai" 2>&1 | grep -i graph
  ```

**Files to Update**:
- Update: [telemetry.py](telemetry.py)
- Update: [graph_auth.py](graph_auth.py)
- Update: [graph_service.py](graph_service.py)

**Dependencies**: Task 5 & 11 complete

**Success Criteria**: Logs contain correlation IDs, latencies, cache events

---

### TASK 12: Documentation ⏱️ Est: 1.5 hours

**Branch**: `feature/task-12-docs`

**Checklist**:
- [ ] Create [docs/graph-setup.md](docs/graph-setup.md):
  - Step-by-step app registration in Azure AD
  - Required scopes: `Calendars.Read`, `User.Read`
  - Service account vs interactive user flow
  - Creating `.env` file
  - Troubleshooting section
- [ ] Update [QUICKSTART.md](QUICKSTART.md):
  - Add Graph example commands
  - Link to graph-setup.md
- [ ] Update [README.md](README.md):
  - Mention Graph data source
- [ ] Verify all links work

**Files to Create**:
- Create: [docs/graph-setup.md](docs/graph-setup.md)

**Files to Update**:
- Update: [QUICKSTART.md](QUICKSTART.md)
- Update: [README.md](README.md)

**Dependencies**: Tasks 1-11 complete

**Success Criteria**: Docs are clear and actionable

---

### TASK 13: Local Testing ⏱️ Est: 1 hour

**Branch**: `feature/task-13-local-test`

**Checklist**:
- [ ] Populate real `.env` with Azure AD test app credentials
- [ ] Test sequence:
  ```bash
  # Test manifest mode still works
  python agent.py recommend --interests "ai, agents" --top 2
  
  # Test Graph mode (if real creds available)
  python agent.py recommend --source graph --user-id "user@tenant.com" --interests "ai" --top 2
  
  # Test HTTP endpoints
  python agent.py serve --port 8010 &
  curl http://localhost:8010/health
  curl http://localhost:8010/recommend?interests=ai,agents&top=2
  curl "http://localhost:8010/recommend-graph?user_id=user@tenant.com&interests=ai&top=2"
  
  # Test token caching
  python agent.py recommend --source graph --user-id "user@tenant.com" --interests "ai" --top 1
  # Should use cached token on second call (faster)
  ```
- [ ] Verify telemetry logged correctly

**Dependencies**: Tasks 1-12 complete

**Success Criteria**: All flows work without errors

---

### TASK 14: Security Hardening ⏱️ Est: 1 hour

**Branch**: `feature/task-14-security`

**Checklist**:
- [ ] Add startup validation in `agent.py` main:
  - Check Graph credentials if `--source graph` requested
  - Raise error if missing
- [ ] Add input validation:
  - User ID must be email format
  - Interests: only alphanumeric + commas, semicolons
  - Top: must be 1-100
- [ ] Mask secrets in logs (never print full tokens)
- [ ] Add rate limiting to `/recommend-graph`:
  ```python
  # Simple: 100 requests per minute per IP
  ```
- [ ] Write tests for invalid inputs
- [ ] Run: `pytest tests/ -v` (all tests should pass)

**Files to Update**:
- Update: [agent.py](agent.py)
- Update: [tests/](tests/) - add security tests

**Dependencies**: Tasks 1-13 complete

**Success Criteria**: Invalid inputs rejected, secrets not logged

---

### TASK 15: Dependency Lock ⏱️ Est: 30 min

**Branch**: `feature/task-15-lock`

**Checklist**:
- [ ] Generate requirements.txt:
  ```bash
  pip freeze > requirements.txt
  ```
- [ ] Or use pip-tools:
  ```bash
  pip install pip-tools
  pip-compile pyproject.toml
  ```
- [ ] Create clean venv and test:
  ```bash
  python -m venv test_env
  source test_env/bin/activate  # or test_env\Scripts\activate on Windows
  pip install -r requirements.txt
  pytest tests/ -v
  ```
- [ ] Verify all tests pass
- [ ] Commit files

**Files to Create**:
- Create: [requirements.txt](requirements.txt)

**Dependencies**: Task 1 complete

**Success Criteria**: Clean install works, all tests pass

---

## PHASE 2: Agents SDK Integration (Week 3-4)

*(Tasks 16-25 follow similar structure)*

### Summary for Phase 2
- Task 16: Add SDK dependencies
- Task 17: Agent declaration file
- Task 18: SDK adapter module
- Task 19: Update runner.py
- Task 20: Teams activity handler
- Task 21: Teams bot manifest
- Task 22: SDK integration tests
- Task 23: Copilot plugin manifest (optional)
- Task 24: SDK documentation
- Task 25: End-to-end SDK test

---

## PHASE 3: Enterprise & Deployment (Week 5-6)

*(Tasks 26-35 follow similar structure)*

### Summary for Phase 3
- Task 26: Application Insights
- Task 27: Distributed tracing
- Task 28: Security middleware
- Task 29: Error handling
- Task 30: Bicep templates
- Task 31: Docker optimization
- Task 32: Dev container
- Task 33: CI/CD pipeline
- Task 34: Deployment docs
- Task 35: Testing & validation

---

## PHASE 4: Polish & Documentation (Week 6)

*(Tasks 36-40 follow similar structure)*

### Summary for Phase 4
- Task 36: Update README
- Task 37: Architecture doc
- Task 38: Operations guide
- Task 39: Sample Graph events
- Task 40: Final QA

---

## Rollup Checklist

### Phase 1 Complete When:
- [x] All 15 tasks done
- [x] 95%+ test coverage for auth & Graph modules
- [x] Local Graph integration works
- [x] Docs complete

### Phase 2 Complete When:
- [x] All 10 tasks done
- [x] Teams Bot Emulator integration works
- [x] SDK tests pass
- [x] Copilot hosting ready

### Phase 3 Complete When:
- [x] All 10 tasks done
- [x] Bicep deployment works
- [x] CI/CD pipeline green
- [x] Monitoring configured

### Phase 4 Complete When:
- [x] All 5 tasks done
- [x] README reflects all features
- [x] Architecture doc complete
- [x] Operations runbook ready

---

## Tools & Commands Reference

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=. --cov-report=html

# Run specific test
pytest tests/test_graph_auth.py::test_get_access_token_caches_result -v

# Format code
pip install black isort pylint
black . && isort .

# Create new branch
git checkout -b feature/task-X-description

# Push & create PR
git push -u origin feature/task-X-description

# Run app locally
python agent.py recommend --interests "ai" --top 3
python agent.py serve --port 8010

# Docker build
docker build -t eventkit:dev .
docker run -e GRAPH_TENANT_ID=... -p 8010:8010 eventkit:dev

# Azure deployment (after Task 30)
az deployment group create \
  --resource-group mygroup \
  --template-file infra/main.bicep \
  --parameters infra/dev.bicepparam
```

---

## Next Steps

**To start**: Pick any tasks from Phase 1 and create a branch. I recommend:
1. **Task 1** (30 min): Update dependencies - validates your environment
2. **Task 3** (1.5 hrs): Create MSAL auth - core functionality
3. **Task 5** (2 hrs): Create Graph service - integrates with auth

This gives you a working Graph API client by end of day 1!
