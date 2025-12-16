# Implementation Plan Summary

## Quick Overview

This scaffolding plan adds **Microsoft Graph integration + Agents SDK hosting** to your event-kit agent.

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT KIT ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Data Sources:                                                   │
│  ├─ Manifest (agent.json) ─────┐                               │
│  └─ Microsoft Graph Calendar ──┤                               │
│                                 ├─→ [Core Agent Logic]          │
│  Authentication:                │   - Scoring                   │
│  └─ MSAL (Service Account) ────┘   - Recommendation            │
│                                     - Explanation               │
│  Deployment Targets:                                            │
│  ├─ HTTP Server (localhost)                                    │
│  ├─ Teams/Copilot (Agents SDK)                                 │
│  └─ SharePoint (Publishing)                                    │
│                                                                   │
│  Observability:                                                  │
│  ├─ Telemetry (JSONL)                                           │
│  └─ Application Insights (optional)                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Timeline & Effort

| Phase | Focus | Tasks | Duration | Difficulty |
|-------|-------|-------|----------|------------|
| 1 | MSAL + Graph API | 15 | 2 weeks | ⭐⭐ |
| 2 | Agents SDK | 10 | 1.5 weeks | ⭐⭐⭐ |
| 3 | Enterprise + Deploy | 10 | 1.5 weeks | ⭐⭐ |
| 4 | Polish + Docs | 5 | 1 week | ⭐ |
| **Total** | | **40** | **6 weeks** | |

---

## What Gets Built

### Phase 1: Foundation (After 2 weeks)
✅ MSAL authentication working  
✅ Microsoft Graph Calendar API integrated  
✅ User events fetched & transformed  
✅ Agent recommends from real calendar  
✅ HTTP `/recommend-graph` endpoint working  
✅ Full test coverage (>85%)  
✅ Comprehensive documentation

### Phase 2: Agent SDK (After 3.5 weeks)
✅ Teams/Copilot hosting via SDK  
✅ Bot activity handler  
✅ Agent declaration in SDK format  
✅ Teams Bot Emulator testing  
✅ Optional Copilot plugin manifest

### Phase 3: Enterprise Ready (After 5 weeks)
✅ Application Insights monitoring  
✅ Bicep/Terraform infrastructure  
✅ Docker multi-stage build  
✅ Dev Container for VSCode  
✅ CI/CD pipeline (GitHub Actions/Azure Pipelines)  
✅ Rate limiting & security hardening

### Phase 4: Production Grade (After 6 weeks)
✅ Architecture documentation  
✅ Operations runbook  
✅ Complete API reference  
✅ Deployment guide  
✅ Troubleshooting guide

---

## Key Files Created

```
event-agent-example/
├── graph_auth.py              ← MSAL token management
├── graph_service.py            ← Graph API wrapper
├── agents_sdk_adapter.py       ← Teams/SDK integration
├── teams_activity_handler.py   ← Bot activity handling
├── errors.py                   ← Custom exceptions
│
├── tests/
│   ├── test_graph_auth.py
│   ├── test_graph_service.py
│   ├── test_graph_integration.py
│   ├── test_agents_sdk.py
│   └── fixtures/
│       └── graph_responses.json
│
├── infra/
│   ├── main.bicep
│   ├── dev.bicepparam
│   └── prod.bicepparam
│
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
│
├── .github/workflows/
│   ├── test.yml
│   ├── lint.yml
│   └── deploy.yml
│
├── docs/
│   ├── graph-setup.md
│   ├── agents-sdk-setup.md
│   ├── architecture.md
│   ├── deployment.md
│   └── operations.md
│
├── teams-manifest.json
├── agent-declaration.json
├── copilot-manifest.json       (optional)
├── requirements.txt
├── .env                        (credentials)
├── Dockerfile                  (updated)
└── docker-compose.yml          (updated)
```

---

## Recommended Start Sequence

### Day 1 (3 hours)
1. **Task 1** (30 min): Update dependencies in `pyproject.toml`
2. **Task 2** (45 min): Enhance `settings.py`
3. **Task 3** (1.5 hrs): Create `graph_auth.py` (MSAL client)
4. **Task 4** (45 min): Write auth tests

→ **Result**: MSAL token acquisition working, cached tokens

### Day 2 (3 hours)
5. **Task 5** (2 hrs): Create `graph_service.py` (Graph wrapper)
6. **Task 6** (1 hr): Write Graph service tests

→ **Result**: Can fetch real calendar events from Graph API

### Day 3 (3 hours)
7. **Task 7** (1 hr): Update `core.py` for Graph data
8. **Task 8** (1.5 hrs): Add `--source graph` CLI flag
9. **Task 9** (1 hr): Add `/recommend-graph` HTTP endpoint

→ **Result**: Can run `python agent.py recommend --source graph --user-id user@tenant.com`

### Week 2
- Tasks 10-15: Integration tests, logging, security, documentation, validation

→ **Result**: Full Phase 1 complete, ready for SDK integration

---

## Prerequisites & Setup

### Required
- Python 3.11+
- Azure AD tenant with registered application
- Microsoft Graph API permissions:
  - `Calendars.Read` (read calendar events)
  - `User.Read` (read user profile)

### Setup Steps (Before Starting)
```bash
# 1. Register app in Azure AD (https://portal.azure.com)
#    - Copy: Tenant ID, Client ID, Client Secret
#    - Grant calendar permissions

# 2. Create .env file
cp .env.example .env
# Edit .env with your credentials:
# GRAPH_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# GRAPH_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# GRAPH_CLIENT_SECRET=xxxx~xxx~xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 3. Install dev dependencies
pip install -e ".[dev]"

# 4. Start with Phase 1, Task 1
```

---

## Success Metrics

### Phase 1 ✅
- [x] `pytest tests/ -v --cov` shows >85% coverage
- [x] `python agent.py recommend --source graph --user-id user@tenant.com --interests ai` works
- [x] HTTP server `/recommend-graph` endpoint responds correctly
- [x] All 15 tasks completed & committed
- [x] No security warnings (secrets not in logs)

### Phase 2 ✅
- [x] Teams Bot Emulator connects to agent
- [x] Recommend/Explain tools callable from Teams
- [x] Agent declaration file valid
- [x] All 10 tasks completed

### Phase 3 ✅
- [x] `az deployment group create` deploys infrastructure
- [x] Docker image builds & runs
- [x] CI/CD pipeline triggers on PR
- [x] Application Insights logs visible
- [x] All 10 tasks completed

### Phase 4 ✅
- [x] Documentation complete & accurate
- [x] Operations runbook tested
- [x] All 5 tasks completed

---

## Git Workflow

Each task should follow this pattern:

```bash
# Create feature branch
git checkout -b feature/task-X-description

# Work on task (make commits)
git add <files>
git commit -m "feat: task X - description"

# Push & create PR
git push -u origin feature/task-X-description
# Go to GitHub, create PR, request review

# After review approved
git merge

# Mark task complete in EXECUTION_PLAN.md
# Commit & push
```

---

## Questions to Ask When Stuck

**Authentication Issues?**
- Check `.env` file has valid credentials
- Verify app permissions in Azure AD
- Run `python -c "from graph_auth import GraphAuthClient; ..."`

**Graph API Errors?**
- Check scopes granted to app
- Verify user has calendar
- Review Graph API docs for response schema

**Agent SDK Not Working?**
- Ensure SDK package installed: `pip list | grep azure-ai`
- Check agent declaration JSON syntax
- Test with Teams Bot Emulator

**Deployment Failing?**
- Verify Bicep syntax: `az bicep build --file infra/main.bicep`
- Check Azure subscription & permissions
- Review Activity Log in portal

---

## Branching Strategy

```
main (production)
 ├─ feature/task-1-deps
 ├─ feature/task-2-settings
 ├─ feature/task-3-msal-auth
 ├─ feature/task-4-auth-tests
 ├─ feature/task-5-graph-service
 ... (continue for all 40 tasks)
```

**Branch Protection Rules** (recommended):
- Require 1 approval before merge
- Run tests on PR
- Require up-to-date branch before merge

---

## Cost Estimate (Azure)

### Phase 1-4 Infrastructure
| Resource | Estimate |
|----------|----------|
| App Service (Standard) | $60/month |
| Application Insights | Free tier |
| Key Vault | $0.6/month |
| SQL Database (if needed) | $15-200/month |
| Total Baseline | ~$75/month |

*Adjust based on actual usage & region*

---

## Next Steps

1. **Read** [EXECUTION_PLAN.md](EXECUTION_PLAN.md) for detailed task-by-task steps
2. **Start** Task 1: Update `pyproject.toml`
3. **Create** branch: `git checkout -b feature/task-1-deps`
4. **Execute** task checklist
5. **Run** tests: `pytest tests/ -v`
6. **Commit & Push**
7. **Repeat** for Task 2, 3, etc.

Good luck! 🚀
