# Documentation Organization Plan

## Current State Analysis

### Existing Files (18 total)

1. **Planning/Tracking** (should be archived or moved):
   - EXECUTION_PLAN.md (600 lines) - outdated, Phase 1 complete
   - SCAFFOLD_ANALYSIS.md (600 lines) - outdated, analysis done
   - PLAN_SUMMARY.md - obsolete
   - TASK_TRACKING.md - obsolete
   - EVENT_KIT.md - duplicate info


2. **User Guides** (should be consolidated):
   - QUICKSTART.md - at root level, duplicates
   - QUICK_REFERENCE.md - duplicates QUICKSTART
   - graph-setup.md - Graph-specific, good
   - troubleshooting.md - good, needs org


3. **Technical** (should be consolidated):
   - technical-guide.md - good
   - performance-guide.md - good
   - data-integration.md - good
   - application-patterns.md - good


4. **Other**:
   - governance.md - good
   - evaluation.md - good
   - README.md - duplicate info
   - INDEX.md - poor UX
   - openapi-snippet.yaml - API reference

## Proposed New Structure

```text
docs/
├── 00-START-HERE.md           # ONE entry point for all audiences
├── 01-GETTING-STARTED/
│   ├── installation.md        # Setup & dependencies
│   ├── quick-start.md         # First 5 minutes
│   └── configuration.md       # .env setup
├── 02-USER-GUIDES/
│   ├── cli-usage.md          # CLI commands (manifest & Graph)
│   ├── http-api.md           # HTTP endpoints & examples
│   └── profiles.md           # Profile management
├── 03-GRAPH-API/
│   ├── setup.md              # Azure AD & credentials
│   ├── architecture.md       # How Graph integration works
│   └── troubleshooting.md    # Graph-specific issues
├── 04-ARCHITECTURE/
│   ├── design.md             # System design & patterns
│   ├── modules.md            # Module reference
│   └── scoring-algorithm.md  # How recommendations work
├── 05-PRODUCTION/
│   ├── deployment.md         # Deployment guide
│   ├── performance.md        # Performance & scaling
│   ├── security.md           # Security hardening
│   └── monitoring.md         # Logging & observability
├── 06-DEVELOPMENT/
│   ├── contributing.md       # How to contribute
│   ├── testing.md            # Testing guide
│   └── architecture-decisions.md  # ADRs
├── REFERENCE.md              # Command & API reference
└── openapi-snippet.yaml      # API schema
```

## Audience Mapping

### 🚀 Quick Starters (5 mins)

- START-HERE.md → Quick Start section
- Installation (5 mins)
- First CLI command

### 📚 Users (want to use the app)

- Getting Started
- User Guides (CLI, HTTP, Profiles)
- Graph API (if using Graph)
- Troubleshooting

### 🏗️ Developers (want to understand code)

- Architecture sections
- Module reference
- Testing guide
- Contributing guide

### 🚢 Operations (want to deploy)

- Installation
- Configuration
- Deployment
- Monitoring/Performance
- Security

## Consolidation Actions

1. **Delete/Archive** (no longer needed):
   - EXECUTION_PLAN.md → Archive as PHASE1_EXECUTION.md.bak
   - SCAFFOLD_ANALYSIS.md → Archive as ARCHITECTURE_GAP_ANALYSIS.md.bak
   - PLAN_SUMMARY.md → DELETE
   - TASK_TRACKING.md → DELETE
   - EVENT_KIT.md → Merge into architecture.md
   - INDEX.md → Replace with 00-START-HERE.md

2. **Consolidate**:
   - QUICKSTART.md (root) + QUICK_REFERENCE.md + graph-setup.md → Multiple files in docs/
   - troubleshooting.md (keep but enhance)
   - technical-guide.md → modules.md + design.md

3. **Keep/Enhance**:
   - performance-guide.md → 05-PRODUCTION/performance.md
   - governance.md → 05-PRODUCTION/security.md (merge)
   - evaluation.md → 06-DEVELOPMENT/testing.md (merge)
   - application-patterns.md → 04-ARCHITECTURE/patterns.md
   - data-integration.md → Keep as is (it's good)

4. **Create New**:
   - 00-START-HERE.md (audience selector + quick start)
   - 01-GETTING-STARTED/installation.md
   - 01-GETTING-STARTED/configuration.md
   - 02-USER-GUIDES/cli-usage.md
   - 02-USER-GUIDES/http-api.md
   - 03-GRAPH-API/architecture.md
   - 04-ARCHITECTURE/design.md
   - 04-ARCHITECTURE/modules.md
   - 05-PRODUCTION/deployment.md
   - 05-PRODUCTION/monitoring.md
   - 06-DEVELOPMENT/contributing.md
   - REFERENCE.md (quick command reference)

## Implementation Steps

1. Create directory structure ✓ (planned)
2. Create 00-START-HERE.md (audience selector)
3. Extract/create Getting Started docs
4. Consolidate User Guides
5. Create/consolidate Architecture docs
6. Create Production docs
7. Create Development docs
8. Update root README.md to point to docs/
9. Archive old planning docs
10. Test all cross-references

## Success Criteria

- ✅ Single entry point (START-HERE.md)
- ✅ Clear audience navigation
- ✅ No duplicate information
- ✅ Each doc has clear purpose
- ✅ All links working
- ✅ 15 min to find any answer
- ✅ Old planning docs archived
