# Event Kit Agent - Prioritized Implementation Roadmap

**Status**: Phase 1 (MSAL + Graph) = 85% Complete | Remaining: 25 tasks across Phases 1-4

---

## 🎯 Executive Summary

This roadmap completes the transformation from local demo agent to production-ready enterprise agent with Microsoft Graph integration and Teams/Copilot hosting via Agents SDK.

**Current State**: ✅ Core agent + Graph API integration working  
**Target State**: Full enterprise deployment with SDK hosting, monitoring, CI/CD

**Estimated Timeline**: 4-6 weeks (assuming 1 developer, full-time)

---

## 📊 Priority Matrix

```text
                    HIGH IMPACT
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    │   🟢 QUICK WINS    │   🔴 CRITICAL      │
    │   (Do First)       │   (Plan & Execute) │
    │                    │                    │
LOW │  - Security (T1)   │  - CI/CD (T10)     │ HIGH
EFF │  - Requirements    │  - Bicep (T8)      │ EFF
ORT │    (T2)            │  - Agents SDK      │ ORT
    │  - Errors (T3)     │    (T11-19)        │
    │                    │                    │
    ├────────────────────┼────────────────────┤
    │                    │                    │
    │   🟡 FILL-IN       │   🟠 STRATEGIC     │
    │   (If Time)        │   (Long-term Value)│
    │                    │                    │
    │  - Pre-commit (T23)│  - OpenAPI (T20)   │
    │  - Copilot (T17)   │  - Operations (T22)│
    │                    │  - Bot Emulator(T25)│
    │                    │                    │
    └────────────────────┼────────────────────┘
                         │
                    LOW IMPACT
```

---

## 🚀 Phase-by-Phase Breakdown

### **PHASE 1: Security & Foundation (COMPLETE THIS FIRST)**
**Timeline**: 1-2 days | **Risk**: LOW | **Value**: CRITICAL

| Task | Title | Effort | Blockers | Value |
|------|-------|--------|----------|-------|
| T1 | Security hardening (validation, rate limiting, CORS) | 4h | None | 🔴 Critical |
| T2 | Generate requirements.txt | 30m | None | 🔴 Critical |
| T3 | Create errors.py with custom exceptions | 2h | None | 🟢 High |

**Deliverables**:

- ✅ Production-ready security posture
- ✅ Reproducible dependency management
- ✅ Consistent error handling

---

### **PHASE 2: Observability & DevOps (HIGHEST ROI)**

**Timeline**: 3-5 days | **Risk**: MEDIUM | **Value**: CRITICAL

| Task | Title | Effort | Blockers | Value |
|------|-------|--------|----------|-------|
| T4 | Application Insights integration | 3h | Azure subscription | 🔴 Critical |
| T5 | Enhanced logging with correlation IDs | 2h | T4 | 🔴 Critical |
| T6 | Docker multi-stage build | 2h | None | 🟢 High |
| T7 | Docker Compose for local dev | 1h | T6 | 🟢 High |
| T8 | Bicep infrastructure templates | 6h | Azure subscription | 🔴 Critical |
| T9 | VSCode Dev Container | 2h | None | 🟡 Medium |
| T10 | GitHub Actions CI/CD pipeline | 4h | T2, T8 | 🔴 Critical |

**Deliverables**:

- ✅ Full observability (logs, traces, metrics)
- ✅ Infrastructure-as-Code for Azure
- ✅ Automated testing & deployment
- ✅ Consistent local dev environment

**Why This Phase First?**

- Enables rapid iteration on Phase 3
- Sets up monitoring before production deployment
- CI/CD catches issues early in Phase 3 development

---

### **PHASE 3: Agents SDK Integration (HIGHEST COMPLEXITY)**

**Timeline**: 1.5-2 weeks | **Risk**: HIGH | **Value**: HIGH

| Task | Title | Effort | Blockers | Value |
|------|-------|--------|----------|-------|
| T11 | Agent SDK dependency setup | 1h | None | 🔴 Critical |
| T12 | Create agent-declaration.json | 2h | T11 | 🔴 Critical |
| T13 | Build Agents SDK adapter module | 6h | T11, T12 | 🔴 Critical |
| T14 | Update runner.py for SDK mode | 3h | T13 | 🔴 Critical |
| T15 | Create Teams activity handler | 4h | T13 | 🔴 Critical |
| T16 | Generate Teams Bot manifest | 2h | T15 | 🔴 Critical |
| T17 | Create Copilot plugin manifest (optional) | 2h | T16 | 🟡 Medium |
| T18 | Write Agents SDK integration tests | 4h | T13-T15 | 🟢 High |
| T19 | Create docs/agents-sdk-setup.md | 3h | T11-T16 | 🟢 High |

**Deliverables**:

- ✅ Teams/Copilot hosting capability
- ✅ Bot Framework integration
- ✅ Full test coverage for SDK features
- ✅ Complete SDK documentation

**Dependencies**: Requires Azure AD app registration for bot

**Risk Mitigation**:

- Start with T11-T13 (adapter only) before full Teams integration
- Use Bot Emulator for local testing before Azure deployment
- Keep manifest-based and Graph modes working (backward compatibility)

---

### **PHASE 4: Documentation & Polish (FINAL MILE)**

**Timeline**: 3-5 days | **Risk**: LOW | **Value**: MEDIUM

| Task | Title | Effort | Blockers | Value |
|------|-------|--------|----------|-------|
| T20 | Complete OpenAPI/Swagger spec | 4h | T1 | 🟡 Medium |
| T21 | Create deployment guide | 3h | T8, T10 | 🟢 High |
| T22 | Create operations runbook | 4h | T4, T8 | 🟠 Strategic |
| T23 | Add pre-commit hooks & dev tooling | 2h | T2 | 🟡 Medium |
| T24 | Update README with architecture diagram | 2h | T13-T16 | 🟢 High |
| T25 | End-to-end testing with Bot Emulator | 3h | T11-T16 | 🟠 Strategic |

**Deliverables**:

- ✅ Complete API documentation
- ✅ Deployment & operations guides
- ✅ Enhanced developer experience
- ✅ Production readiness validation

---

## 🎯 Recommended Execution Sequence

### **Week 1: Foundation + Observability (Days 1-5)**

```text
Day 1 (AM): T1 Security hardening (4h)
Day 1 (PM): T2 Requirements.txt (30m) + T3 Errors.py (2h)

Day 2 (AM): T4 Application Insights (3h)
Day 2 (PM): T5 Correlation IDs (2h) + T6 Docker optimization (2h)

Day 3 (AM): T7 Docker Compose (1h) + T9 Dev Container (2h)
Day 3 (PM): T8 Bicep templates (6h) - START

Day 4 (AM): T8 Bicep templates (CONTINUE)
Day 4 (PM): T8 Bicep templates (FINISH) + T10 CI/CD (4h) - START

Day 5: T10 CI/CD (FINISH) + Deploy & validate infrastructure
```

**Checkpoint 1**: ✅ Production-ready infrastructure deployed to Azure

---

### **Week 2-3: Agents SDK Integration (Days 6-15)**

```text
Day 6: T11 SDK setup (1h) + T12 Agent declaration (2h) + T13 Adapter (6h) - START
Day 7: T13 Adapter (FINISH) + T18 SDK tests (4h)
Day 8: T14 Runner update (3h) + T15 Teams handler (4h)
Day 9: T15 Teams handler (FINISH) + T16 Bot manifest (2h)
Day 10: T19 SDK documentation (3h) + T17 Copilot manifest (2h)

Day 11-12: Integration testing & debugging (2 full days buffer)
Day 13: T25 Bot Emulator E2E testing (3h)
Day 14-15: Deploy to Azure & test in real Teams environment
```

**Checkpoint 2**: ✅ Agent running in Teams with full functionality

---

### **Week 3-4: Documentation & Finalization (Days 16-20)**

```text
Day 16: T20 OpenAPI spec (4h) + T23 Pre-commit hooks (2h)
Day 17: T21 Deployment guide (3h) + T24 README update (2h)
Day 18: T22 Operations runbook (4h)
Day 19: Final testing across all modes (manifest, graph, SDK)
Day 20: Documentation review, release prep, CHANGELOG update
```

**Checkpoint 3**: ✅ Production release ready (v1.0.0)

---

## 📋 Task Dependencies Graph

```text
Phase 1 (Foundation)
T1, T2, T3 → (parallel, no dependencies)
         ↓
Phase 2 (Observability)
T2 → T10 (CI/CD needs requirements.txt)
T4 → T5 (Correlation IDs need App Insights)
T6 → T7 (Docker Compose needs optimized Dockerfile)
T8, T9 (parallel to others)
         ↓
Phase 3 (Agents SDK)
T11 → T12 → T13 → T14, T15 (parallel)
              ↓        ↓
             T18      T16 → T17
                       ↓
                      T19
         ↓
Phase 4 (Documentation)
T20, T21, T22, T23, T24 → T25 (E2E test needs all features)
```

---

## 🎲 Alternative Paths

### **Path A: Minimal Viable Production (MVP)**`n`n**Timeline**: 1 week | **Focus**: Security + Infrastructure

1. T1-T3 (Foundation) ✅ Security hardened
2. T4-T5 (Observability basics) ✅ Logging working
3. T6-T8 (Infrastructure) ✅ Deployed to Azure
4. T10 (CI/CD) ✅ Automated deployments
5. Skip Agents SDK (use HTTP API only)

**Use Case**: Need production deployment ASAP without Teams integration

---

### **Path B: Agents SDK First (Teams-Focused)**`n`n**Timeline**: 2 weeks | **Focus**: Teams/Copilot hosting

1. T1-T3 (Foundation - required for security)
2. T11-T19 (Full Agents SDK implementation)
3. T4-T5 (Observability for debugging SDK)
4. T6-T7 (Docker for local testing)
5. Defer T8, T10 (infrastructure & CI/CD)

**Use Case**: Prototype Teams bot quickly, deploy manually for now

---

### **Path C: Documentation Sprint (Knowledge Transfer)**`n`n**Timeline**: 3 days | **Focus**: Team enablement

1. T20 (OpenAPI spec)
2. T21-T22 (Deployment + Operations guides)
3. T24 (README with diagrams)
4. T23 (Dev tooling for contributors)

**Use Case**: Current system works, need documentation for team handoff

---

## 🚨 Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Agents SDK breaking changes | 🔴 High | 🟡 Medium | Pin SDK version, test frequently, monitor releases |
| Azure subscription limits | 🟠 Medium | 🟢 Low | Verify quotas early, request increases if needed |
| Graph API rate limiting | 🟡 Low | 🟡 Medium | Implement caching, respect retry-after headers |
| Teams manifest approval delays | 🟠 Medium | 🟡 Medium | Start approval process early, have fallback (HTTP API) |
| CI/CD complexity | 🟡 Low | 🟢 Low | Start simple (test only), add deployment incrementally |

---

## 📈 Success Metrics

### **Phase 1 (Foundation)**`n`n- [ ] All security tests pass (input validation, rate limiting)
- [ ] `pip install -r requirements.txt` works in clean venv
- [ ] Error responses use consistent format

### **Phase 2 (Observability)**`n`n- [ ] Application Insights shows telemetry events
- [ ] Docker image builds < 500MB
- [ ] Bicep deployment completes without errors
- [ ] CI/CD runs tests on every PR

### **Phase 3 (Agents SDK)**`n`n- [ ] Agent responds in Teams Bot Emulator
- [ ] Recommend/Explain tools callable from Teams
- [ ] Agent declaration validates against SDK schema
- [ ] All SDK tests pass (>85% coverage maintained)

### **Phase 4 (Documentation)**`n`n- [ ] New developer can deploy locally in <30 minutes
- [ ] OpenAPI spec validates in Swagger Editor
- [ ] Operations runbook tested by non-developer
- [ ] README diagrams render correctly on GitHub

---

## 🛠️ Quick Reference Commands

```bash
# Phase 1: Security & Foundation
python -m pytest tests/test_security.py -v        # After T1
pip-compile pyproject.toml -o requirements.txt    # T2
python -m pytest tests/ --cov                     # Verify coverage

# Phase 2: Infrastructure
docker build -t eventkit:latest .                 # T6
docker-compose up                                 # T7
az deployment group create -f infra/main.bicep    # T8
az webapp browse                                  # Verify deployment

# Phase 3: Agents SDK
pip install azure-ai-projects                     # T11
python runner.py --mode m365-agent --port 5000    # T14
ngrok http 5000                                   # Expose for Teams

# Phase 4: Testing
swagger-cli validate docs/openapi.yaml            # T20
python -m pytest tests/test_integration.py -v     # T25
```

---

## 🎓 Learning Resources

- **MSAL Python**: <https://github.com/AzureAD/microsoft-authentication-library-for-python>
- **Microsoft Graph API**: <https://learn.microsoft.com/en-us/graph/overview>
- **Azure Agents SDK**: <https://learn.microsoft.com/en-us/azure/ai-services/agents/>
- **Bot Framework**: <https://dev.botframework.com/>
- **Bicep**: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/>

---

## 📞 Decision Points

### **After Phase 1** (Week 1 End)`n`n- ❓ Deploy to production with HTTP API only? (Path A)
- ❓ Continue to Phase 2 (recommended)?

### **After Phase 2** (Week 2 End)`n`n- ❓ Production deployment ready? Infrastructure stable?
- ❓ Proceed with Agents SDK (Phase 3) or defer?

### **After Phase 3** (Week 3 End)`n`n- ❓ Teams integration working? Ready for user testing?
- ❓ Prioritize documentation (Phase 4) or more features?

---

## 🏁 Definition of Done

**Project Complete When**:
- ✅ All 25 tasks checked off
- ✅ 126+ tests passing (coverage ≥85%)
- ✅ Deployed to Azure with CI/CD working
- ✅ Agent accessible via 3 modes: CLI, HTTP API, Teams/Copilot
- ✅ Documentation complete (setup, API, deployment, operations)
- ✅ Security hardened (validation, rate limiting, monitoring)
- ✅ No critical/high severity security vulnerabilities
- ✅ Operations runbook tested by team

---

## 📝 Next Steps

1. **Review this roadmap** with stakeholders
2. **Choose execution path**: Recommended (full), MVP (Path A), or Teams-first (Path B)
3. **Set up project tracking**: Copy tasks to GitHub Issues/Azure DevOps
4. **Start Phase 1, Task 1**: Security hardening (4 hours)

**Questions?** See [SCAFFOLD_ANALYSIS.md](SCAFFOLD_ANALYSIS.md) for detailed task descriptions.

---

*Last Updated*: 2025-12-16  
*Status*: Phase 1 = 85% | Phases 2-4 = 0%  
*Next Task*: T1 - Security hardening

