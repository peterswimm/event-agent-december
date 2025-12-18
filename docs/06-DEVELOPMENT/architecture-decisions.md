# Architecture Decisions

Key architectural decisions and their rationale for Event Kit.

## Overview

This document records significant architecture decisions made during Event Kit development, following the Architecture Decision Record (ADR) format.

## Decision Format

Each decision includes:

- **Status:** Accepted, Proposed, Deprecated, Superseded
- **Context:** The issue motivating this decision
- **Decision:** What was decided
- **Consequences:** Trade-offs and impacts

---

## ADR-001: Use JSON for Manifest Storage

**Status:** Accepted

**Context:**

Event Kit needs to store session data, weights, and configuration. Options considered:

- JSON file
- YAML file
- SQLite database
- TOML file

**Decision:**

Use JSON for manifest storage (`agent.json`).

**Rationale:**

- ✅ Simple: No external dependencies
- ✅ Ubiquitous: Built into Python stdlib
- ✅ Readable: Easy to edit manually
- ✅ Versioned: Works with Git
- ✅ Fast: Quick to parse for <10k sessions

**Consequences:**

- Limited query capabilities (no SQL)
- Manual schema validation needed
- File locking not built-in (single writer only)
- No automatic indexing

**Alternatives rejected:**

- YAML: Requires external library, more complex
- SQLite: Overkill for simple use case, harder to version control
- TOML: Less common, limited nesting support

---

## ADR-002: Weighted Multi-Factor Scoring

**Status:** Accepted

**Context:**

Need a recommendation algorithm that balances:

- User interests (personalization)
- Session popularity (wisdom of crowds)
- Diversity (exploration)

**Decision:**

Use weighted multi-factor scoring:

```python
score = (interest_match × W_interest) + 
        (popularity × W_popularity) + 
        (diversity × W_diversity)
```

**Rationale:**

- ✅ Transparent: Easy to explain to users
- ✅ Tunable: Weights adjustable without code changes
- ✅ Fast: O(N × M) complexity acceptable for <10k sessions
- ✅ Debuggable: Score breakdown shows contributions

**Consequences:**

- Linear combination may not capture complex relationships
- Requires manual weight tuning
- No learning from user feedback

**Alternatives rejected:**

- Machine learning model: Too complex, requires training data
- Collaborative filtering: Needs multiple users
- Content-based only: Ignores popularity signal

---

## ADR-003: Local-Only Data Storage

**Status:** Accepted

**Context:**

Event Kit needs to store profiles, telemetry, and cache tokens. Options:

- Local files (JSON/JSONL)
- Remote database (PostgreSQL, MongoDB)
- Cloud storage (Azure Blob, S3)

**Decision:**

Store all data locally in files:

- Profiles: `~/.event_agent_profiles.json`
- Telemetry: `./telemetry.jsonl`
- Token cache: `~/.msal_token_cache.bin`

**Rationale:**

- ✅ Simple: No database setup required
- ✅ Portable: Works anywhere Python runs
- ✅ Private: Data never leaves server
- ✅ Fast: No network latency
- ✅ Versionable: Files can be tracked in Git

**Consequences:**

- Single-server deployment only (no distributed state)
- Manual backup required
- File locking needed for concurrent writes
- Disk space management required

**Alternatives rejected:**

- Database: Too complex for small datasets
- Cloud storage: Introduces network dependency

---

## ADR-004: HTTP Server for API

**Status:** Accepted (with caveats)

**Context:**

Need to expose Event Kit as an HTTP API. Options:

- Python built-in HTTPServer
- Flask framework
- FastAPI framework
- Django framework

**Decision:**

Use Python's built-in `http.server.HTTPServer` for initial implementation.

**Rationale:**

- ✅ Zero dependencies: Built into stdlib
- ✅ Simple: Easy to understand
- ✅ Lightweight: Minimal overhead
- ✅ Sufficient for demos and testing

**Consequences:**

- Single-threaded (one request at a time)
- Limited features (no middleware, routing)
- Not production-ready at scale
- Manual JSON parsing required

**Migration path:**

- Production: Use Gunicorn or uvicorn
- Complex apps: Migrate to FastAPI or Flask

**Alternatives rejected:**

- Flask: Adds dependency, more complex
- FastAPI: Requires ASGI server, async code
- Django: Massive overkill

---

## ADR-005: MSAL for Graph Authentication

**Status:** Accepted

**Context:**

Need to authenticate with Microsoft Graph API. Options:

- MSAL (Microsoft Authentication Library)
- Custom OAuth implementation
- azure-identity library

**Decision:**

Use MSAL with application permissions (client credentials flow).

**Rationale:**

- ✅ Official: Microsoft-supported library
- ✅ Token caching: Automatic token refresh
- ✅ Secure: Encrypted token storage
- ✅ Well-documented: Examples available

**Consequences:**

- Requires Azure AD app registration
- Admin consent needed for permissions
- Daemon app pattern (not user-delegated)

**Alternatives rejected:**

- Custom OAuth: Reinventing the wheel, error-prone
- azure-identity: Higher-level, less control

---

## ADR-006: JSONL for Telemetry

**Status:** Accepted

**Context:**

Need structured logging for observability. Options:

- JSONL (JSON Lines)
- CSV
- SQLite
- Standard Python logging

**Decision:**

Use JSONL format with one JSON object per line.

**Rationale:**

- ✅ Structured: Easy to parse with `jq`
- ✅ Append-only: Fast writes, no locking
- ✅ Streamable: Can process line-by-line
- ✅ Standard: Widely supported format

**Consequences:**

- File grows unbounded (rotation needed)
- No automatic indexing (must scan file)
- No schema enforcement

**Alternatives rejected:**

- CSV: Less flexible, harder to extend
- SQLite: Requires locking, more complex
- Python logging: Text format harder to parse

---

## ADR-007: Pydantic for Configuration

**Status:** Accepted

**Context:**

Need type-safe configuration loading from environment variables. Options:

- Manual `os.getenv()`
- ConfigParser (INI files)
- Pydantic Settings
- python-dotenv

**Decision:**

Use Pydantic Settings with `.env` file support.

**Rationale:**

- ✅ Type-safe: Automatic validation
- ✅ IDE support: Type hints for autocomplete
- ✅ Clear errors: Validation failures explicit
- ✅ Defaults: Easy to specify fallbacks

**Consequences:**

- Adds dependency on pydantic
- Requires Python 3.8+ (type hints)

**Alternatives rejected:**

- Manual getenv: Error-prone, no validation
- ConfigParser: INI format less common
- python-dotenv alone: No type validation

---

## ADR-008: External Sessions via File Override

**Status:** Accepted

**Context:**

Need to integrate external data sources (APIs, databases) without modifying code. Options:

- Direct API integration in agent.py
- Database connector
- File-based override
- Plugin system

**Decision:**

Allow external sessions via `sessions_external.json` file with feature flag.

**Rationale:**

- ✅ Decoupled: No code changes needed
- ✅ Flexible: Any upstream system can generate file
- ✅ Testable: Easy to switch between manifest and external
- ✅ Simple: Just write JSON file

**Consequences:**

- File must be written atomically (temp file + rename)
- No automatic sync (external system responsible)
- Schema must match expected format

**Alternatives rejected:**

- Direct API: Couples agent to specific upstream systems
- Database: Adds complexity, requires setup
- Plugin system: Over-engineered for simple use case

---

## ADR-009: Feature Flags in Manifest

**Status:** Accepted

**Context:**

Need to control capabilities without code deployment. Options:

- Environment variables
- Separate config file
- Manifest-embedded flags
- Remote config service

**Decision:**

Embed feature flags in `agent.json` manifest:

```json
{
    "features": {
        "externalSessions": {"enabled": true, "file": "..."},
        "export": {"enabled": true}
    }
}
```

**Rationale:**

- ✅ Co-located: Config with data
- ✅ Versioned: Track changes in Git
- ✅ Simple: No external dependencies
- ✅ Auditable: Changes visible in version control

**Consequences:**

- Requires manifest reload to change flags
- All deployments share same flags (no per-environment)

**Alternatives rejected:**

- Environment variables: Harder to version, scattered
- Remote config: Adds complexity, network dependency

---

## ADR-010: Conflict Detection Post-Ranking

**Status:** Accepted

**Context:**

Users may select sessions with overlapping time slots. Options:

- Filter conflicts before ranking
- Penalize conflicts in scoring
- Detect conflicts after ranking (report only)

**Decision:**

Detect conflicts after ranking and report count, but don't filter.

**Rationale:**

- ✅ User choice: Let users decide trade-offs
- ✅ Transparent: Show conflict count in results
- ✅ Simple: No complex scheduling logic
- ✅ Informative: Users see what conflicts exist

**Consequences:**

- Users may receive infeasible schedules
- No automatic conflict resolution
- Conflict count may be high

**Alternatives rejected:**

- Pre-filter: May eliminate best matches
- Penalize in scoring: Adds complexity, unclear weights

---

## ADR-011: Single-Module Design

**Status:** Accepted (evolving)

**Context:**

Initial implementation had all logic in `agent.py`. As project grew, needed better organization. Options:

- Keep single file
- Split into multiple modules
- Package structure with submodules

**Decision:**

Split into focused modules:

- `agent.py` — CLI & HTTP entry point
- `core.py` — Recommendation logic
- `settings.py` — Configuration
- `telemetry.py` — Telemetry
- `graph_*.py` — Graph API integration

**Rationale:**

- ✅ Separation of concerns: Each module has clear purpose
- ✅ Testability: Easier to mock and test
- ✅ Reusability: `core.py` importable by other hosts
- ✅ Maintainability: Smaller files easier to navigate

**Consequences:**

- More files to manage
- Import dependencies between modules

**Evolution:**

- Phase 1: Single file (v0.1)
- Phase 2: Split into modules (v0.2)
- Phase 3: (Future) Package structure with setup.py

---

## ADR-012: No Machine Learning (For Now)

**Status:** Accepted

**Context:**

Could use ML for personalization:

- Collaborative filtering
- Content-based deep learning
- Reinforcement learning

**Decision:**

Use simple weighted scoring without ML.

**Rationale:**

- ✅ Transparent: Users understand how it works
- ✅ Debuggable: Easy to explain why session ranked high
- ✅ No training data: Works without historical feedback
- ✅ Fast: No model inference overhead
- ✅ Deterministic: Same inputs → same outputs

**Consequences:**

- Limited personalization (no learning from feedback)
- Weights must be tuned manually
- May not capture complex patterns

**Future consideration:**

- Add ML as optional enhancement
- Keep weighted scoring as fallback
- Learn from telemetry data over time

---

## ADR-013: Pytest for Testing

**Status:** Accepted

**Context:**

Need testing framework. Options:

- unittest (stdlib)
- pytest
- nose2

**Decision:**

Use pytest as test framework.

**Rationale:**

- ✅ Simple: Less boilerplate than unittest
- ✅ Fixtures: Powerful setup/teardown
- ✅ Plugins: Ecosystem of extensions (coverage, xdist)
- ✅ Assertions: Better error messages

**Consequences:**

- Adds pytest dependency
- Different style from stdlib unittest

**Alternatives rejected:**

- unittest: More verbose, less features
- nose2: Less maintained, smaller ecosystem

---

## ADR-014: Markdown for Documentation

**Status:** Accepted

**Context:**

Need user-facing documentation. Options:

- Markdown
- reStructuredText (Sphinx)
- HTML
- Wiki

**Decision:**

Use Markdown in `/docs` folder with audience-based structure.

**Rationale:**

- ✅ Simple: Easy to write and read
- ✅ Universal: GitHub rendering, VS Code support
- ✅ Versioned: Lives with code in Git
- ✅ Portable: Renders anywhere

**Consequences:**

- Limited layout options vs. HTML
- No automatic API docs generation

**Alternatives rejected:**

- Sphinx/RST: More complex, Python-specific
- HTML: Harder to write, maintain
- Wiki: Separate from code repository

---

## Future Decisions

### Under Consideration

**ADR-015: Database Backend**

- **Status:** Proposed
- **Context:** File-based storage doesn't scale beyond 100k sessions
- **Options:** PostgreSQL, SQLite, MongoDB
- **Decision:** TBD

**ADR-016: Async/ASGI Support**

- **Status:** Proposed
- **Context:** Single-threaded HTTP server limits concurrency
- **Options:** FastAPI + uvicorn, Starlette, aiohttp
- **Decision:** TBD

**ADR-017: Multi-Tenant Support**

- **Status:** Proposed
- **Context:** Single deployment per organization limits scale
- **Options:** Tenant ID in requests, separate manifests, database partitioning
- **Decision:** TBD

## Decision Log Summary

| ADR | Decision | Status |
|-----|----------|--------|
| 001 | JSON manifest | ✅ Accepted |
| 002 | Weighted scoring | ✅ Accepted |
| 003 | Local storage | ✅ Accepted |
| 004 | HTTPServer | ✅ Accepted |
| 005 | MSAL auth | ✅ Accepted |
| 006 | JSONL telemetry | ✅ Accepted |
| 007 | Pydantic config | ✅ Accepted |
| 008 | External sessions | ✅ Accepted |
| 009 | Feature flags | ✅ Accepted |
| 010 | Conflict detection | ✅ Accepted |
| 011 | Multi-module | ✅ Accepted |
| 012 | No ML (yet) | ✅ Accepted |
| 013 | Pytest | ✅ Accepted |
| 014 | Markdown docs | ✅ Accepted |
| 015 | Database | 🤔 Proposed |
| 016 | Async/ASGI | 🤔 Proposed |
| 017 | Multi-tenant | 🤔 Proposed |

## Contributing Decisions

When proposing an architecture change:

1. Create ADR document with context and options
2. Discuss in GitHub issue or PR
3. Update this file with decision once accepted
4. Implement and reference ADR in commit message

## Next Steps

- 🤝 [Contributing Guide](contributing.md) — How to contribute
- 🧪 [Testing Guide](testing.md) — Test suite details
- 🏗️ [System Design](../04-ARCHITECTURE/design.md) — Architecture overview
- 🎯 [Scoring Algorithm](../04-ARCHITECTURE/scoring-algorithm.md) — Deep dive
