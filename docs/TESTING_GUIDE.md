# EventKit Agent - Testing Guide

**Last Updated**: December 18, 2025
**Version**: 1.0.0
**Test Coverage**: 40+ test cases across 19 test files

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Writing Tests](#writing-tests)
6. [Coverage Reports](#coverage-reports)
7. [CI/CD Integration](#cicd-integration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

EventKit uses **pytest** as the testing framework with support for:

- ✅ **Unit tests** - Fast, isolated component tests
- ✅ **Integration tests** - Graph API, external services
- ✅ **Bot tests** - Teams/Outlook Bot Framework integration
- ✅ **Foundry tests** - Microsoft Foundry Agent Framework
- ✅ **Async tests** - Full asyncio support with pytest-asyncio
- ✅ **Coverage reporting** - Terminal, HTML, and XML formats

### Test Statistics

| Category | Test Files | Test Cases | Coverage |
|----------|-----------|------------|----------|
| **Core Logic** | 7 | 80+ | ~90% |
| **Bot Framework** | 1 | 15+ | ~75% |
| **Microsoft Foundry** | 2 | 25+ | ~80% |
| **Graph API** | 4 | 35+ | ~85% |
| **Settings & Config** | 3 | 20+ | ~95% |
| **Utilities** | 2 | 12+ | ~90% |
| **Total** | **19** | **187+** | **~87%** |

---

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_core_graph.py             # Graph API recommendations (476 lines)
├── test_unified_adapters.py       # Unified adapter framework tests (NEW)
├── test_agents_sdk.py             # Legacy Agents SDK adapter (552 lines)
├── test_bot_handler.py            # Bot Framework handler (180 lines)
├── test_agent_framework_adapter.py # Foundry Agent Framework (160 lines)
├── test_prompt_flow.py            # Prompt Flow integration (150 lines)
├── test_recommend.py              # Core recommendation logic
├── test_explain.py                # Session explanation logic
├── test_export.py                 # Itinerary export
├── test_profile.py                # Profile persistence
├── test_graph_service.py          # Graph API service
├── test_graph_integration.py      # Graph integration tests
├── test_graph_auth.py             # Graph authentication
├── test_graph_server.py           # Graph API server
├── test_external_sessions.py      # External session data
├── test_settings.py               # Settings and configuration
├── test_security.py               # Input validation
├── test_telemetry.py              # Application Insights
├── test_logging_config.py         # Logging configuration
└── test_server.py                 # HTTP API server
```

**Note**: The new `test_unified_adapters.py` tests the unified adapter framework (base_adapter, foundry_adapter, power_adapter, bot_adapter). See [UNIFIED_ADAPTER_ARCHITECTURE.md](UNIFIED_ADAPTER_ARCHITECTURE.md) for architecture details.

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_recommend.py

# Run specific test class
pytest tests/test_agents_sdk.py::TestEventKitAgentInitialization

# Run specific test case
pytest tests/test_recommend.py::test_recommend_basic -v
```

### Using Test Markers

```bash
# Run only unit tests (fast, no external dependencies)
pytest -m unit

# Run bot framework tests
pytest -m bot

# Run Microsoft Foundry tests
pytest -m foundry

# Run integration tests (may call external APIs)
pytest -m integration

# Run smoke tests only
pytest -m smoke

# Skip slow tests
pytest -m "not slow"
```

### Coverage Reports

```bash
# Run tests with coverage
pytest --cov

# Generate HTML coverage report
pytest --cov --cov-report=html
open htmlcov/index.html  # View in browser

# Coverage for specific module
pytest --cov=core tests/test_recommend.py

# Show missing lines
pytest --cov --cov-report=term-missing
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Auto-detect CPU count
pytest -n auto
```

---

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

**Purpose**: Fast, isolated tests with no external dependencies

**Characteristics**:
- No network calls
- Mocked external services
- Tests single functions/methods
- Execution time: <100ms per test

**Examples**:
```python
@pytest.mark.unit
def test_recommend_basic(manifest):
    """Test basic recommendation logic."""
    result = recommend(manifest, ["agents"], 3)
    assert len(result["sessions"]) <= 3
```

**Files**: Most test files use unit tests by default

### Integration Tests (`@pytest.mark.integration`)

**Purpose**: Test interactions with external services

**Characteristics**:
- May call Microsoft Graph API
- Tests Graph authentication
- Calendar integration
- Requires valid credentials

**Examples**:
```python
@pytest.mark.integration
def test_graph_get_events(graph_service):
    """Test fetching events from Microsoft Graph."""
    events = graph_service.get_events("user@company.com")
    assert isinstance(events, list)
```

**Files**:
- [tests/test_graph_integration.py](d:\code\event-agent-example\tests\test_graph_integration.py)
- [tests/test_graph_service.py](d:\code\event-agent-example\tests\test_graph_service.py)
- [tests/test_graph_auth.py](d:\code\event-agent-example\tests\test_graph_auth.py)

### Bot Framework Tests (`@pytest.mark.bot`)

**Purpose**: Test Teams/Outlook bot integration

**Characteristics**:
- Tests Bot Framework activity handling
- Command parsing
- Adaptive card generation
- Async message handling

**Examples**:
```python
@pytest.mark.bot
@pytest.mark.asyncio
async def test_on_message_activity_with_recommend(mock_turn_context):
    """Test recommend command handling."""
    mock_turn_context.activity.text = "@bot recommend agents --top 3"
    handler = EventKitBotHandler()
    await handler.on_message_activity(mock_turn_context)
    assert mock_turn_context.send_activity.called
```

**Files**: [tests/test_bot_handler.py](d:\code\event-agent-example\tests\test_bot_handler.py)

### Microsoft Foundry Tests (`@pytest.mark.foundry`)

**Purpose**: Test Agent Framework and Prompt Flow integration

**Characteristics**:
- Tests EventKitAgentFramework
- Azure AI Project integration
- Async agent run/stream methods
- Tool call handling

**Examples**:
```python
@pytest.mark.foundry
@pytest.mark.asyncio
async def test_run_with_recommendation_query(foundry_settings):
    """Test running agent with recommendation query."""
    agent = EventKitAgentFramework(settings=foundry_settings)
    response = await agent.run("recommend sessions about AI agents")
    assert response is not None
```

**Files**:
- [tests/test_agent_framework_adapter.py](d:\code\event-agent-example\tests\test_agent_framework_adapter.py)
- [tests/test_prompt_flow.py](d:\code\event-agent-example\tests\test_prompt_flow.py)

---

## Writing Tests

### Using Shared Fixtures

All fixtures are defined in [tests/conftest.py](d:\code\event-agent-example\tests\conftest.py):

```python
def test_with_sample_manifest(sample_manifest):
    """Use shared sample manifest fixture."""
    assert len(sample_manifest["sessions"]) == 5

def test_with_mock_settings(mock_settings):
    """Use shared settings mock."""
    assert mock_settings.graph_enabled == False

def test_with_mock_turn_context(mock_turn_context):
    """Use shared Bot Framework context."""
    assert mock_turn_context.activity.text == "@bot help"
```

### Testing Async Functions

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function with pytest-asyncio."""
    result = await my_async_function()
    assert result is not None
```

### Mocking External Calls

```python
from unittest.mock import Mock, patch

def test_with_mocked_graph_api():
    """Mock Graph API calls."""
    with patch("graph_service.GraphEventService.get_events") as mock_get:
        mock_get.return_value = [{"id": "event1"}]

        # Test code here
        result = recommend_from_graph(...)
        assert mock_get.called
```

### Parametrized Tests

```python
@pytest.mark.parametrize("interests,expected_count", [
    (["agents"], 3),
    (["ai", "safety"], 5),
    (["machine learning"], 2),
])
def test_recommend_various_interests(manifest, interests, expected_count):
    """Test recommendations with different interests."""
    result = recommend(manifest, interests, 10)
    assert len(result["sessions"]) >= expected_count
```

### Test Organization

```python
class TestRecommendations:
    """Group related tests in a class."""

    @pytest.fixture
    def manifest(self):
        """Class-specific fixture."""
        return {"sessions": [...]}

    def test_basic_recommend(self, manifest):
        """Test basic functionality."""
        pass

    def test_recommend_with_profile(self, manifest):
        """Test with profile."""
        pass
```

---

## Coverage Reports

### Terminal Report

```bash
pytest --cov --cov-report=term-missing
```

Output:
```text
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
core.py                         250     15    94%   45-50, 120-125
agent.py                        450     35    92%   200-210, 300-315
adapters/base_adapter.py        450     20    95%   150-165
adapters/foundry_adapter.py     150      8    95%   120-125
adapters/bot_adapter.py         150     10    93%   100-110
bot_handler.py                  280     40    86%   220-240
settings.py                      80      5    94%   65-70
-----------------------------------------------------------
TOTAL                          1810    133    93%
```

### HTML Report

```bash
pytest --cov --cov-report=html
```

Opens interactive HTML report in `htmlcov/index.html`:
- Line-by-line coverage highlighting
- Branch coverage analysis
- Missing line identification
- Module-level statistics

### XML Report (for CI/CD)

```bash
pytest --cov --cov-report=xml
```

Generates `coverage.xml` compatible with:
- Azure DevOps
- GitHub Actions
- Jenkins
- SonarQube

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        run: |
          pytest --cov --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Azure Pipelines

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'

- script: |
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
  displayName: 'Install dependencies'

- script: |
    pytest --cov --cov-report=xml --cov-report=html --junitxml=test-results.xml
  displayName: 'Run tests'

- task: PublishTestResults@2
  inputs:
    testResultsFiles: 'test-results.xml'
    testRunTitle: 'EventKit Tests'

- task: PublishCodeCoverageResults@1
  inputs:
    codeCoverageTool: 'Cobertura'
    summaryFileLocation: 'coverage.xml'
```

---

## Troubleshooting

### Issue 1: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'adapters'` or import errors with unified adapters

**Solution**:
```bash
# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Verify adapters package is installed
python -c "from adapters import base_adapter; print('✅ Adapters imported successfully')"
```

### Issue 2: Async Tests Failing

**Problem**: `RuntimeError: Event loop is closed`

**Solution**: Ensure `pytest-asyncio` is installed and configured:
```bash
pip install pytest-asyncio

# In pytest.ini:
[pytest]
asyncio_mode = auto
```

### Issue 3: Bot Framework Tests Skipped

**Problem**: `SKIPPED [1] Bot Framework SDK not installed`

**Solution**:
```bash
pip install botbuilder-core botbuilder-integration-aiohttp
```

### Issue 4: Graph API Tests Failing

**Problem**: Authentication errors in integration tests

**Solution**: Set environment variables:
```bash
export GRAPH_TENANT_ID=your-tenant-id
export GRAPH_CLIENT_ID=your-client-id
export GRAPH_CLIENT_SECRET=your-client-secret

# Or skip integration tests
pytest -m "not integration"
```

### Issue 5: Coverage Too Low

**Problem**: Coverage below expected threshold

**Solution**: Identify missing coverage:
```bash
# Show missing lines
pytest --cov --cov-report=term-missing

# Generate HTML report for detailed view
pytest --cov --cov-report=html
open htmlcov/index.html
```

---

## Best Practices

### 1. Test Naming

```python
# Good: Descriptive, action-oriented
def test_recommend_returns_top_3_sessions():
    pass

# Bad: Vague
def test_recommend():
    pass
```

### 2. Arrange-Act-Assert Pattern

```python
def test_recommend_with_interests():
    # Arrange: Set up test data
    manifest = {"sessions": [...]}
    interests = ["agents", "ai"]

    # Act: Execute function
    result = recommend(manifest, interests, 3)

    # Assert: Verify results
    assert len(result["sessions"]) == 3
    assert result["sessions"][0]["title"] is not None
```

### 3. Use Fixtures for Common Setup

```python
# Define once in conftest.py
@pytest.fixture
def sample_manifest():
    return load_manifest("test_data.json")

# Use in multiple tests
def test_recommend(sample_manifest):
    result = recommend(sample_manifest, ["agents"], 3)
    assert result
```

### 4. Test Edge Cases

```python
def test_recommend_with_empty_interests():
    """Test error handling for empty interests."""
    with pytest.raises(ValueError, match="At least one interest"):
        recommend(manifest, [], 3)

def test_recommend_with_zero_results():
    """Test behavior when no matches found."""
    result = recommend(manifest, ["nonexistent"], 3)
    assert len(result["sessions"]) == 0
```

### 5. Keep Tests Fast

```python
# Use markers for slow tests
@pytest.mark.slow
def test_large_dataset():
    # This test takes >5 seconds
    pass

# Skip slow tests in development
# pytest -m "not slow"
```

---

## Additional Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **Coverage.py**: https://coverage.readthedocs.io/
- **Test Fixtures**: [tests/conftest.py](d:\code\event-agent-example\tests\conftest.py)
- **Test Examples**: [tests/](d:\code\event-agent-example\tests)

---

**Last Updated**: December 18, 2025
**Maintained by**: EventKit Team
**Test Framework**: pytest 7.0+, pytest-asyncio 0.21+, pytest-cov 4.0+
