# Event Kit Documentation

Complete documentation for Event Kit - a lightweight event recommendation agent.

## ðŸš€ Start Here

**New to Event Kit?** â†’ [00-START-HERE.md](00-START-HERE.md) â€” Choose your path based on your role

## Quick Access

| I want to... | Go to... |
|--------------|----------|
| Get started in 5 minutes | [Quick Start](01-GETTING-STARTED/quick-start.md) |
| Set up production deployment | [Deployment Guide](05-PRODUCTION/deployment.md) |
| Understand the scoring algorithm | [Scoring Algorithm](04-ARCHITECTURE/scoring-algorithm.md) |
| Contribute code | [Contributing Guide](06-DEVELOPMENT/contributing.md) |
| Use Microsoft Graph API | [Graph API Setup](03-GRAPH-API/setup.md) |
| Run CLI commands | [CLI Usage](02-USER-GUIDES/cli-usage.md) |
| Monitor in production | [Monitoring Guide](05-PRODUCTION/monitoring.md) |
| Run tests | [Testing Guide](06-DEVELOPMENT/testing.md) |

## Documentation Structure

```text
docs/
â”œâ”€â”€ 00-START-HERE.md              # ðŸ‘ˆ Start here! Audience selector
â”œâ”€â”€ 01-GETTING-STARTED/           # Setup and configuration
â”‚   â”œâ”€â”€ quick-start.md
â”‚   â”œâ”€â”€ installation.md
â”‚   â””â”€â”€ configuration.md
â”œâ”€â”€ 02-USER-GUIDES/               # Using Event Kit
â”‚   â”œâ”€â”€ cli-usage.md
â”‚   â””â”€â”€ http-api.md
â”œâ”€â”€ 03-GRAPH-API/                 # Microsoft Graph integration
â”‚   â”œâ”€â”€ setup.md
â”‚   â”œâ”€â”€ architecture.md
â”‚   â””â”€â”€ troubleshooting.md
â”œâ”€â”€ 04-ARCHITECTURE/              # System design
â”‚   â”œâ”€â”€ design.md
â”‚   â”œâ”€â”€ modules.md
â”‚   â”œâ”€â”€ scoring-algorithm.md
â”‚   â””â”€â”€ patterns.md
â”œâ”€â”€ 05-PRODUCTION/                # Deployment and operations
â”‚   â”œâ”€â”€ deployment.md
â”‚   â”œâ”€â”€ performance.md
â”‚   â”œâ”€â”€ security.md
â”‚   â””â”€â”€ monitoring.md
â”œâ”€â”€ 06-DEVELOPMENT/               # Contributing
â”‚   â”œâ”€â”€ contributing.md
â”‚   â”œâ”€â”€ testing.md
â”‚   â””â”€â”€ architecture-decisions.md
â””â”€â”€ REFERENCE.md                  # Complete reference
```

## By Audience

### ðŸ‘¤ End Users

**Goal:** Use Event Kit to get personalized event recommendations

1. [Quick Start](01-GETTING-STARTED/quick-start.md) â€” Get up and running
2. [CLI Usage](02-USER-GUIDES/cli-usage.md) â€” Command reference
3. [HTTP API](02-USER-GUIDES/http-api.md) â€” API endpoints
4. [Graph API Setup](03-GRAPH-API/setup.md) â€” Connect to Microsoft Graph

### ðŸ‘¨â€ðŸ’» Developers

**Goal:** Understand, modify, and extend Event Kit

1. [Installation](01-GETTING-STARTED/installation.md) â€” Full dev setup
2. [Architecture Design](04-ARCHITECTURE/design.md) â€” System overview
3. [Modules Reference](04-ARCHITECTURE/modules.md) â€” Code structure
4. [Scoring Algorithm](04-ARCHITECTURE/scoring-algorithm.md) â€” How recommendations work
5. [Application Patterns](04-ARCHITECTURE/patterns.md) â€” Common workflows
6. [Contributing Guide](06-DEVELOPMENT/contributing.md) â€” How to contribute
7. [Testing Guide](06-DEVELOPMENT/testing.md) â€” Test suite
8. [Architecture Decisions](06-DEVELOPMENT/architecture-decisions.md) â€” Design rationale

### âš™ï¸ DevOps / Operations

**Goal:** Deploy, monitor, and maintain Event Kit in production

1. [Configuration](01-GETTING-STARTED/configuration.md) â€” Environment setup
2. [Deployment Guide](05-PRODUCTION/deployment.md) â€” Production deployment
3. [Performance Guide](05-PRODUCTION/performance.md) â€” Optimization
4. [Security Guide](05-PRODUCTION/security.md) â€” Security hardening
5. [Monitoring Guide](05-PRODUCTION/monitoring.md) â€” Observability
6. [Graph API Troubleshooting](03-GRAPH-API/troubleshooting.md) â€” Common issues

## By Topic

### Getting Started

- [00-START-HERE.md](00-START-HERE.md) â€” Choose your path
- [Quick Start](01-GETTING-STARTED/quick-start.md) â€” 5-minute setup
- [Installation](01-GETTING-STARTED/installation.md) â€” Full setup guide
- [Configuration](01-GETTING-STARTED/configuration.md) â€” Environment setup

### Using Event Kit

- [CLI Usage](02-USER-GUIDES/cli-usage.md) â€” Command reference
- [HTTP API](02-USER-GUIDES/http-api.md) â€” API endpoints
- [Application Patterns](04-ARCHITECTURE/patterns.md) â€” Common workflows

### Microsoft Graph Integration

- [Graph API Setup](03-GRAPH-API/setup.md) â€” Azure AD configuration
- [Graph Architecture](03-GRAPH-API/architecture.md) â€” How it works
- [Graph Troubleshooting](03-GRAPH-API/troubleshooting.md) â€” Common issues

### Architecture & Design

- [System Design](04-ARCHITECTURE/design.md) â€” Architecture overview
- [Module Reference](04-ARCHITECTURE/modules.md) â€” Code structure
- [Scoring Algorithm](04-ARCHITECTURE/scoring-algorithm.md) â€” Recommendation engine
- [Application Patterns](04-ARCHITECTURE/patterns.md) â€” Usage patterns
- [Architecture Decisions](06-DEVELOPMENT/architecture-decisions.md) â€” ADRs

### Production Operations

- [Deployment Guide](05-PRODUCTION/deployment.md) â€” Deploy to production
- [Performance Guide](05-PRODUCTION/performance.md) â€” Optimize performance
- [Security Guide](05-PRODUCTION/security.md) â€” Security best practices
- [Monitoring Guide](05-PRODUCTION/monitoring.md) â€” Observability setup

### Development

- [Contributing Guide](06-DEVELOPMENT/contributing.md) â€” Contribution workflow
- [Testing Guide](06-DEVELOPMENT/testing.md) â€” Test suite details
- [Architecture Decisions](06-DEVELOPMENT/architecture-decisions.md) â€” Design rationale

### Reference

- [Complete Reference](REFERENCE.md) â€” Comprehensive command/API/config reference

## Getting Help

### Documentation Issues

- **Missing information?** Open an issue
- **Unclear explanation?** Suggest improvement
- **Found an error?** Submit a PR with fix

### Support Channels

- **GitHub Issues** â€” Bug reports, feature requests
- **GitHub Discussions** â€” Questions, community support

## Contributing to Docs

See [Contributing Guide](06-DEVELOPMENT/contributing.md) for how to improve documentation.

## Changelog

**2024-12-16:** Documentation reorganization complete

- Consolidated 18 docs into audience-based structure
- Added comprehensive guides for all audiences
- Created entry point (00-START-HERE.md)
- Archived old planning docs

## Next Steps

**Never been here before?**

ðŸ‘‰ Start with [00-START-HERE.md](00-START-HERE.md)

**Know what you need?**

ðŸ‘‰ Use the quick access table above

**Want everything?**

ðŸ‘‰ Check out [REFERENCE.md](REFERENCE.md)
