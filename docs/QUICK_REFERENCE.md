# Developer Quick Reference

## Essential Commands

### Development Setup
```bash
# Install project in dev mode
pip install -e ".[dev]"

# Verify installation
python -c "import msal; import msgraph_core; print('✓ Dependencies OK')"

# Create .env file
cp .env.example .env
# Edit .env with real credentials
```

### Running the Agent

#### Manifest Mode (Default)
```bash
# Recommend sessions
python agent.py recommend --interests "ai, agents" --top 3

# Explain a session
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"

# Export itinerary
python agent.py export --interests "ai, agents" --output my_itinerary.md

# Start HTTP server
python agent.py serve --port 8010 --card
```

#### Graph Mode (After Phase 1)
```bash
# Recommend from user's calendar
python agent.py recommend --source graph \
  --user-id "user@tenant.onmicrosoft.com" \
  --interests "ai, agents" --top 3

# Explain from Graph events
python agent.py explain --source graph \
  --user-id "user@tenant.onmicrosoft.com" \
  --session "Meeting Title" --interests "ai"
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_graph_auth.py -v

# Run specific test
pytest tests/test_graph_auth.py::test_get_access_token_caches_result -v

# Run with coverage report
pytest tests/ -v --cov=. --cov-report=html
# Open: htmlcov/index.html

# Run only Graph-related tests (after Phase 1)
pytest tests/ -k graph -v

# Run with debugging output
pytest tests/ -v -s  # -s shows print statements
pytest tests/ -v --tb=short  # shorter traceback
```

### HTTP Server Testing

```bash
# Start server in background
python agent.py serve --port 8010 &

# Test health
curl http://localhost:8010/health

# Test manifest recommendation
curl "http://localhost:8010/recommend?interests=ai,agents&top=3&card=1"

# Test Graph recommendation (after Phase 1)
curl "http://localhost:8010/recommend-graph?user_id=user@tenant.com&interests=ai&top=2"

# Test with jq for pretty printing
curl -s http://localhost:8010/health | jq .

# Kill background server
pkill -f "python agent.py serve"
```

### Git Workflow

```bash
# Create feature branch for task
git checkout -b feature/task-1-deps

# Check status
git status
git diff  # see what changed

# Add changes
git add <file>
git add .  # add all changed files

# Commit with descriptive message
git commit -m "feat: task 1 - update dependencies"
git commit -m "test: add unit tests for graph auth"
git commit -m "docs: add graph setup guide"

# Push to remote
git push -u origin feature/task-1-deps

# View log
git log --oneline -10

# Switch branches
git checkout main
git checkout feature/task-1-deps
```

### Code Quality

```bash
# Format code
pip install black isort
black .  # format all Python files
isort .  # sort imports

# Lint
pip install pylint
pylint *.py
pylint graph_auth.py  # specific file

# Type checking
pip install mypy
mypy graph_auth.py --strict
```

### Docker

```bash
# Build image
docker build -t eventkit:dev .

# Run container
docker run -e GRAPH_TENANT_ID=... \
           -e GRAPH_CLIENT_ID=... \
           -e GRAPH_CLIENT_SECRET=... \
           -p 8010:8010 \
           eventkit:dev

# Docker Compose (local)
docker-compose up -d
curl http://localhost:8010/health
docker-compose down
```

### Debugging

```bash
# Print debug info
python -c "from settings import Settings; s = Settings(); print(s)"

# Check token cache
cat ~/.event_agent_token_cache.json | jq .

# Trace HTTP requests (verbose curl)
curl -v http://localhost:8010/health

# Python debugger
python -m pdb agent.py recommend --interests "ai"
# Commands: (l)ist, (n)ext, (c)ontinue, (q)uit, (p) var, (w)here

# VS Code debugger launch.json
# Debug > "Start Debugging" (requires .vscode/launch.json)
```

### Environment Variables

```bash
# View .env variables
cat .env

# Load .env into shell (bash/zsh)
export $(grep -v '^#' .env | xargs)

# Verify loaded
echo $GRAPH_TENANT_ID

# Set individually
export GRAPH_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export GRAPH_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export GRAPH_CLIENT_SECRET=xxxx~xxxx~xxxxxxxxxxxxxxxxxxxx
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'msal'"
```bash
# Fix: Install dependencies
pip install -e ".[dev]"

# Verify
python -c "import msal; print(msal.__version__)"
```

### "GRAPH_TENANT_ID not set"
```bash
# Fix: Check .env file
cat .env | grep GRAPH_TENANT_ID

# If empty, load from .env
export $(grep -v '^#' .env | xargs)

# Verify
echo $GRAPH_TENANT_ID
```

### Tests Fail with "ConnectionError"
```bash
# Ensure Graph service mocked
# In test: use @patch or responses library
# Example:
from unittest.mock import patch
@patch('graph_service.GraphEventService.fetch_user_events')
def test_something(mock_fetch):
    mock_fetch.return_value = [...]
```

### "AADSTS700016: Application not found in directory"
```bash
# Fix: Verify app registered in Azure AD
# 1. Go to https://portal.azure.com
# 2. Azure Active Directory → App registrations
# 3. Search for your app
# 4. Copy correct Client ID to .env
```

### HTTP Server Won't Start
```bash
# Check port in use
netstat -ano | grep 8010  # Windows
lsof -i :8010              # macOS/Linux

# Use different port
python agent.py serve --port 8011
```

---

## File Quick Reference

| File | Purpose | When to Edit |
|------|---------|------------|
| [agent.py](agent.py) | CLI + HTTP server | Add endpoints, CLI flags |
| [core.py](core.py) | Recommendation logic | Update scoring, core algorithms |
| [settings.py](settings.py) | Configuration | Add env vars, validation |
| [graph_auth.py](graph_auth.py) | MSAL auth | Token flow, caching (Phase 1) |
| [graph_service.py](graph_service.py) | Graph API wrapper | API calls, transformation (Phase 1) |
| [telemetry.py](telemetry.py) | Logging | Add metrics, events |
| [agent.json](agent.json) | Manifest config | Sessions, weights, features |
| [pyproject.toml](pyproject.toml) | Dependencies | Add packages |
| [.env.example](.env.example) | Env template | Add new config options |
| [EXECUTION_PLAN.md](EXECUTION_PLAN.md) | Task details | Reference task steps |

---

## Phase-Specific Commands

### Phase 1: After Task 1
```bash
# Verify new dependencies installed
pip list | grep -E "msal|msgraph|pydantic-settings"
```

### Phase 1: After Task 3
```bash
# Test MSAL token flow (requires .env setup)
python -c "
from settings import Settings
from graph_auth import GraphAuthClient
auth = GraphAuthClient(Settings())
token = auth.get_access_token()
print(f'Token acquired: {token[:20]}...')
"
```

### Phase 1: After Task 5
```bash
# Test Graph service
python -c "
from settings import Settings
from graph_auth import GraphAuthClient
from graph_service import GraphEventService
auth = GraphAuthClient(Settings())
svc = GraphEventService(auth)
events = svc.fetch_user_events('user@tenant.com')
print(f'Events: {len(events)}')
"
```

### Phase 1: After Task 8
```bash
# Test --source flag
python agent.py recommend --source graph \
  --user-id "user@tenant.com" \
  --interests "ai" --top 2
```

### Phase 2: After Task 16
```bash
# Verify Agents SDK installed
python -c "from azure.ai import projects; print('✓ SDK OK')"
```

### Phase 3: After Task 30
```bash
# Validate Bicep template
az bicep build --file infra/main.bicep

# Deploy to Azure
az deployment group create \
  --resource-group mygroup \
  --template-file infra/main.bicep \
  --parameters infra/dev.bicepparam
```

---

## VS Code Extensions to Install

```bash
# Python
code --install-extension ms-python.python

# Pylance (type checking)
code --install-extension ms-python.vscode-pylance

# REST Client (test HTTP endpoints)
code --install-extension humao.rest-client

# Azure Tools
code --install-extension ms-vscode.vscode-node-azure-pack

# GitHub Copilot (optional)
code --install-extension GitHub.copilot
```

### REST Client Usage
Create `test.http`:
```http
@host = http://localhost:8010

### Health
GET {{host}}/health

### Recommend
GET {{host}}/recommend?interests=ai,agents&top=3

### Recommend Graph
GET {{host}}/recommend-graph?user_id=user@tenant.com&interests=ai&top=2
```

Then click "Send Request" above each request.

---

## Useful Links

### Documentation
- [Python Docs](https://python.org/docs)
- [pytest Documentation](https://docs.pytest.org)
- [MSAL Python](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [Microsoft Graph API](https://learn.microsoft.com/graph/api)

### Azure Resources
- [Azure Portal](https://portal.azure.com)
- [Azure CLI Docs](https://learn.microsoft.com/cli/azure)
- [Bicep Language](https://learn.microsoft.com/azure/azure-resource-manager/bicep)

### Teams & Copilot
- [Teams Bot Framework](https://learn.microsoft.com/microsoftteams/platform/bots)
- [Copilot Extensions](https://learn.microsoft.com/copilot/extensibility)
- [Agents SDK](https://learn.microsoft.com/agents)

### Tools
- [GitHub Flow](https://guides.github.com/introduction/flow)
- [Conventional Commits](https://conventionalcommits.org)
- [Semantic Versioning](https://semver.org)

---

## Common Errors & Solutions

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: msal` | `pip install -e ".[dev]"` |
| `GRAPH_TENANT_ID not set` | `export $(grep -v '^#' .env \| xargs)` |
| `Port 8010 already in use` | `python agent.py serve --port 8011` |
| `401 Unauthorized from Graph` | Check `.env` credentials, verify app permissions |
| `429 Too Many Requests` | Implement backoff (already in Phase 1 Task 5) |
| `Tests fail with mock errors` | Use `@patch` decorators, verify mock setup |
| `Git merge conflict` | Resolve manually, `git add <file>`, `git commit` |
| `Docker build fails` | Check Dockerfile syntax, verify base image available |

---

## Tips & Tricks

- **Watch tests**: `pytest-watch tests/` (auto-rerun on file change)
- **Interactive Python**: `python -i graph_auth.py` (loads module, keeps REPL open)
- **View JSON neatly**: `curl ... | python -m json.tool`
- **Search code**: `grep -r "function_name" . --include="*.py"`
- **Find TODOs**: `grep -r "TODO" . --include="*.py"`
- **Run last command**: Press `↑` in terminal
- **Kill stuck process**: `pkill -f "python agent.py"`

---

## Before Asking for Help

1. ✅ Check error message carefully
2. ✅ Run `pip install -e ".[dev]"` (fresh install)
3. ✅ Check `.env` file is correctly populated
4. ✅ Run failing test with `-v -s` flags
5. ✅ Google the error message
6. ✅ Check relevant documentation
7. ✅ Ask in team channel with error output

---

**Last Updated**: 2025-12-16
