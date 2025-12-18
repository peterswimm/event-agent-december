# 🚀 Event Kit Documentation

Welcome to Event Kit! This is a **minimal declarative event recommendation agent** that demonstrates core agent patterns with Microsoft Graph integration for live calendar events.

Choose your path below to get started:

---

## 👤 Pick Your Path

### 🏃 I want to run it in 5 minutes

→ **[Quick Start Guide](01-GETTING-STARTED/quick-start.md)**

Install dependencies and run your first recommendation command in under 5 minutes. No configuration required.

---

### 👨‍💼 I'm a User - I want to use Event Kit

**Start here if you want to:**

- Run recommendations with your calendar
- Set up Graph API authentication
- Use the CLI or HTTP API
- Configure sessions and profiles
- Troubleshoot issues

**Recommended reading order:**

1. [Quick Start](01-GETTING-STARTED/quick-start.md) (5 min) — Get it running
2. [Installation & Setup](01-GETTING-STARTED/installation.md) (10 min) — Full setup
3. [Configuration Guide](01-GETTING-STARTED/configuration.md) (5 min) — Configure for your environment
4. [CLI Usage](02-USER-GUIDES/cli-usage.md) (10 min) — Command reference
5. [HTTP API](02-USER-GUIDES/http-api.md) (10 min) — API endpoints
6. [Graph API Setup](03-GRAPH-API/setup.md) (15 min) — Azure AD + credentials
7. [Troubleshooting](03-GRAPH-API/troubleshooting.md) (5 min) — Common issues

**Quick reference:**

- ⚡ [Command Reference](REFERENCE.md#commands)
- 🔑 [Environment Variables](REFERENCE.md#environment-variables)
- 🆘 [FAQ & Troubleshooting](03-GRAPH-API/troubleshooting.md)

---

### 🏗️ I'm a Developer - I want to understand the code

**Start here if you want to:**

- Understand the architecture and design
- Add new features or modify the agent
- Understand how recommendations work
- Integrate with other systems
- Contribute to the project

**Recommended reading order:**

1. [Quick Start](01-GETTING-STARTED/quick-start.md) (5 min) — Get it running first
2. [System Architecture](04-ARCHITECTURE/design.md) (15 min) — High-level overview
3. [Module Reference](04-ARCHITECTURE/modules.md) (20 min) — Code structure
4. [Scoring Algorithm](04-ARCHITECTURE/scoring-algorithm.md) (15 min) — How it works
5. [Architecture Patterns](04-ARCHITECTURE/patterns.md) (10 min) — Design patterns
6. [Graph Integration](03-GRAPH-API/architecture.md) (15 min) — How Graph API works
7. [Testing Guide](06-DEVELOPMENT/testing.md) (15 min) — How to test
8. [Contributing](06-DEVELOPMENT/contributing.md) (10 min) — Development workflow

**Deep dives:**

- 📊 [Data Integration Patterns](data-integration.md)
- 🎯 [Application Patterns](04-ARCHITECTURE/patterns.md)
- 🔐 [Security Considerations](05-PRODUCTION/security.md)
- 🎨 [Architecture Decisions](06-DEVELOPMENT/architecture-decisions.md)

---

### 🚢 I'm Ops/DevOps - I want to deploy and maintain it

**Start here if you want to:**

- Deploy to production
- Configure for your environment
- Monitor performance and health
- Troubleshoot deployment issues
- Set up security and governance
- Scale the application

**Recommended reading order:**

1. [Quick Start](01-GETTING-STARTED/quick-start.md) (5 min) — Understand what it does
2. [Installation & Setup](01-GETTING-STARTED/installation.md) (10 min) — Dependencies
3. [Configuration Guide](01-GETTING-STARTED/configuration.md) (10 min) — Environment setup
4. [Deployment Guide](05-PRODUCTION/deployment.md) (20 min) — Production setup
5. [Performance Guide](05-PRODUCTION/performance.md) (15 min) — Optimization & scaling
6. [Monitoring & Logging](05-PRODUCTION/monitoring.md) (15 min) — Observability
7. [Security Hardening](05-PRODUCTION/security.md) (15 min) — Security practices
8. [Troubleshooting](03-GRAPH-API/troubleshooting.md) (10 min) — Common issues

**Quick reference:**

- ⚙️ [Configuration Reference](REFERENCE.md#configuration)
- 📊 [Monitoring Metrics](05-PRODUCTION/monitoring.md#metrics)
- 🔐 [Security Checklist](05-PRODUCTION/security.md#security-checklist)

---

## 📚 Full Documentation Structure

```text
docs/
├── 00-START-HERE.md                    ← YOU ARE HERE
├── REFERENCE.md                        ← Quick command/config reference
│
├── 01-GETTING-STARTED/
│   ├── quick-start.md                  ← 5-minute getting started
│   ├── installation.md                 ← Full setup & dependencies
│   └── configuration.md                ← Environment configuration
│
├── 02-USER-GUIDES/
│   ├── cli-usage.md                    ← CLI commands reference
│   ├── http-api.md                     ← HTTP endpoints & examples
│   └── profiles.md                     ← Profile management
│
├── 03-GRAPH-API/
│   ├── setup.md                        ← Azure AD & credential setup
│   ├── architecture.md                 ← How Graph integration works
│   └── troubleshooting.md              ← Graph-specific issues
│
├── 04-ARCHITECTURE/
│   ├── design.md                       ← System architecture & design
│   ├── modules.md                      ← Module reference & structure
│   ├── scoring-algorithm.md            ← How recommendations are scored
│   └── patterns.md                     ← Design patterns & data integration
│
├── 05-PRODUCTION/
│   ├── deployment.md                   ← Deployment guide
│   ├── performance.md                  ← Performance & scaling
│   ├── security.md                     ← Security hardening & governance
│   └── monitoring.md                   ← Logging & observability
│
├── 06-DEVELOPMENT/
│   ├── contributing.md                 ← How to contribute
│   ├── testing.md                      ← Testing guide & evaluation
│   └── architecture-decisions.md       ← Architecture decision records
│
├── archive/                            ← Archived planning documents
│   ├── EXECUTION_PLAN.md.bak
│   ├── SCAFFOLD_ANALYSIS.md.bak
│   ├── PLAN_SUMMARY.md.bak
│   └── TASK_TRACKING.md.bak
│
├── (Other reference docs)
├── application-patterns.md
├── data-integration.md
├── evaluation.md
├── governance.md
└── openapi-snippet.yaml
```

---

## 🎯 What is Event Kit?

Event Kit demonstrates core agent patterns with:

- **📋 Declarative manifest** — Sessions, weights, and feature flags in JSON
- **🖥️ CLI + HTTP server** — Recommend, explain, export endpoints
- **📱 Adaptive Cards** — Interactive UI for Copilot experiences
- **📊 Telemetry** — Structured JSONL logging for observability
- **👤 Profile persistence** — Save/load user preferences
- **📅 Microsoft Graph** — Live calendar events with MSAL authentication
- **🔄 External data override** — Swap in real event feeds

---

## ⚡ Quick Reference

**First time? Run this:**

```bash
# Install dependencies
pip install -r requirements.txt

# Run a recommendation (using sample data)
python agent.py recommend --interests "agents, ai" --top 3
```

**Set up Graph API:**

```bash
# Create .env file with your credentials
cp .env.example .env
# Edit .env with your Azure AD tenant ID, client ID, and client secret
```

**See all options:**

- 📄 Full command reference: [REFERENCE.md](REFERENCE.md)
- 🔍 Graph setup guide: [Graph API Setup](03-GRAPH-API/setup.md)
- 🆘 Troubleshooting: [Troubleshooting Guide](03-GRAPH-API/troubleshooting.md)

---

## 🔗 Important Links

- 📖 Main README: [README.md](../README.md)
- ⚡ Graph Quick Reference: [GRAPH_QUICK_REFERENCE.md](../GRAPH_QUICK_REFERENCE.md)
- 🐙 GitHub Repository: [Microsoft 365 Samples](https://github.com/microsoft/Microsoft-365-samples)
- 📚 Agent Framework Docs: [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)

---

## ❓ Still Lost?

**I need to:**

- 📖 [Learn about the overall architecture](04-ARCHITECTURE/design.md)
- 🔧 [Set up or configure something](01-GETTING-STARTED/configuration.md)
- 🐛 [Fix a problem or error](03-GRAPH-API/troubleshooting.md)
- 🚀 [Get it running as fast as possible](01-GETTING-STARTED/quick-start.md)
- 🐙 [Contribute or modify the code](06-DEVELOPMENT/contributing.md)
- 📊 [Deploy to production](05-PRODUCTION/deployment.md)

---

**Last updated:** Phase 1 Implementation Complete (126 tests passing)

**Questions?** Check the [Troubleshooting Guide](03-GRAPH-API/troubleshooting.md) or review relevant section above.
