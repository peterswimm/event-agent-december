# Contributing Guide

Guidelines for contributing to Event Kit.

## Welcome Contributors

Thank you for your interest in contributing to Event Kit! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv or conda)
- Basic understanding of recommendation systems

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/event-agent-example.git
cd event-agent-example

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Run tests to verify setup
pytest tests/ -v
```

### Project Structure

```text
event-agent-example/
├── agent.py              # Main entry point
├── core.py               # Core recommendation logic
├── settings.py           # Configuration management
├── telemetry.py          # Telemetry logging
├── graph_auth.py         # MSAL authentication
├── graph_service.py      # Graph API client
├── agent.json            # Session manifest
├── tests/                # Test suite
│   ├── test_recommend.py
│   ├── test_graph_*.py
│   └── ...
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── deploy/               # Deployment configs
```

## Contribution Workflow

### 1. Create an Issue

Before starting work:

- Search existing issues to avoid duplicates
- Create a new issue describing the problem or feature
- Wait for maintainer feedback/approval
- Assign yourself to the issue

### 2. Create a Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
# Or for bug fixes
git checkout -b fix/issue-description
```

**Branch naming conventions:**

- `feature/` — New features
- `fix/` — Bug fixes
- `docs/` — Documentation updates
- `refactor/` — Code refactoring
- `test/` — Test improvements

### 3. Make Changes

**Code style guidelines:**

- Follow PEP 8 for Python code
- Use type hints where possible
- Write docstrings for public functions
- Keep functions small and focused
- Add comments for complex logic

**Example:**

```python
def score_session(
    session: Dict[str, Any],
    interests: List[str],
    weights: Dict[str, float]
) -> Dict[str, Any]:
    """Score a session against user interests.
    
    Args:
        session: Session dictionary with tags and metadata
        interests: List of user interests (normalized to lowercase)
        weights: Scoring weights for interest/popularity/diversity
    
    Returns:
        Dictionary with session, score, and contribution breakdown
    
    Example:
        >>> session = {"title": "AI Workshop", "tags": ["ai", "ml"], "popularity": 5}
        >>> result = score_session(session, ["ai"], {"interest": 2.0, "popularity": 0.5})
        >>> result["score"]
        4.5
    """
    # Implementation...
```

### 4. Write Tests

**All new code must include tests:**

```python
# tests/test_new_feature.py
import pytest
from agent import new_feature

def test_new_feature_basic():
    """Test basic functionality."""
    result = new_feature(input_data)
    assert result == expected_output

def test_new_feature_edge_case():
    """Test edge case handling."""
    result = new_feature(edge_case_input)
    assert result is not None

def test_new_feature_error_handling():
    """Test error handling."""
    with pytest.raises(ValueError):
        new_feature(invalid_input)
```

**Run tests:**

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_new_feature.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

**Coverage requirements:**

- New code: 100% coverage
- Modified code: Maintain existing coverage
- Overall project: >80% coverage

### 5. Format and Lint

**Before committing:**

```bash
# Format code with black
black agent.py core.py tests/

# Lint with flake8
flake8 agent.py core.py tests/

# Type check with mypy
mypy agent.py core.py --ignore-missing-imports
```

**Fix common issues:**

```bash
# Auto-fix import sorting
isort agent.py core.py tests/

# Fix line length issues
black --line-length 100 agent.py
```

### 6. Commit Changes

**Commit message format:**

```text
<type>: <subject>

<body>

Fixes #<issue-number>
```

**Types:**

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `test:` — Test additions or fixes
- `refactor:` — Code refactoring
- `perf:` — Performance improvements
- `chore:` — Build/tooling changes

**Example:**

```bash
git add agent.py tests/test_recommend.py
git commit -m "feat: add diversity factor to scoring algorithm

Adds configurable diversity weight to encourage exploration of
varied interests in recommendations. Includes tests and docs.

Fixes #123"
```

### 7. Push and Create PR

```bash
# Push branch to remote
git push origin feature/your-feature-name

# Create pull request via GitHub UI
```

**PR template:**

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #123

## Changes Made
- Added diversity factor to scoring
- Updated tests for new behavior
- Updated documentation

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex logic
- [ ] Updated documentation
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

### 8. Code Review

**Respond to feedback:**

- Address all reviewer comments
- Push additional commits to same branch
- Mark conversations as resolved when fixed
- Request re-review when ready

**Example response:**

```text
> Can you add error handling for empty interests?

Good catch! Added validation in commit abc123.
```

### 9. Merge

Once approved:

- Maintainer will merge PR
- Delete feature branch
- Close related issue

## Coding Standards

### Python Style

**Follow PEP 8 with these specifics:**

- Line length: 100 characters (not 79)
- Use double quotes for strings
- Use trailing commas in multi-line collections
- Organize imports: stdlib → third-party → local

**Example:**

```python
from typing import Dict, List, Any  # stdlib
import json
import pathlib

from pydantic_settings import BaseSettings  # third-party

from telemetry import get_telemetry  # local


def recommend(
    manifest: Dict[str, Any],
    interests: List[str],
    top: int,
) -> Dict[str, Any]:
    """Implementation..."""
    pass
```

### Type Hints

**Use type hints for all public functions:**

```python
from typing import Dict, List, Any, Optional

def recommend(
    manifest: Dict[str, Any],
    interests: List[str],
    top: int = 5
) -> Dict[str, Any]:
    """Type-hinted function."""
    pass

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Returns user or None if not found."""
    return None
```

### Error Handling

**Be explicit about error cases:**

```python
def recommend(manifest, interests, top):
    # Validate inputs
    if not interests:
        raise ValueError("At least one interest is required")
    
    if top < 1 or top > 50:
        raise ValueError("top must be between 1 and 50")
    
    # Handle missing data gracefully
    sessions = manifest.get("sessions", [])
    if not sessions:
        logger.warning("No sessions available")
        return {"sessions": [], "scoring": [], "conflicts": 0}
    
    # Implementation...
```

### Documentation

**Write clear docstrings:**

```python
def score_session(session, interests, weights):
    """Score a session against user interests.
    
    Calculates a weighted score based on interest matches,
    popularity, and diversity factors.
    
    Args:
        session: Session dict with required keys: title, tags, popularity
        interests: List of lowercase interest strings
        weights: Dict with keys: interest, popularity, diversity
    
    Returns:
        Dict containing:
            - session: Original session dict
            - score: Float score value
            - contributions: Dict of score breakdown by factor
    
    Raises:
        KeyError: If required keys missing from session or weights
    
    Example:
        >>> session = {"title": "AI Workshop", "tags": ["ai"], "popularity": 5}
        >>> weights = {"interest": 2.0, "popularity": 0.5, "diversity": 0.3}
        >>> result = score_session(session, ["ai"], weights)
        >>> result["score"]
        4.5
    """
    pass
```

## Testing Guidelines

### Test Organization

```text
tests/
├── conftest.py           # Shared fixtures
├── test_recommend.py     # Recommendation tests
├── test_explain.py       # Explanation tests
├── test_graph_auth.py    # Graph auth tests
├── test_graph_service.py # Graph service tests
└── test_telemetry.py     # Telemetry tests
```

### Test Fixtures

**Use pytest fixtures for common setup:**

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_manifest():
    return {
        "weights": {"interest": 2.0, "popularity": 0.5, "diversity": 0.3},
        "sessions": [
            {
                "id": "session-1",
                "title": "AI Workshop",
                "tags": ["ai", "ml"],
                "popularity": 5
            }
        ]
    }

@pytest.fixture
def sample_interests():
    return ["ai", "ml", "safety"]
```

**Use in tests:**

```python
def test_recommend_basic(sample_manifest, sample_interests):
    result = recommend(sample_manifest, sample_interests, top=5)
    assert len(result["sessions"]) > 0
```

### Test Coverage

**Aim for comprehensive coverage:**

- ✅ Happy path (normal inputs)
- ✅ Edge cases (empty, large, boundary values)
- ✅ Error cases (invalid inputs, exceptions)
- ✅ Integration (multiple components together)

**Example:**

```python
def test_recommend_empty_interests():
    """Test error handling for empty interests."""
    with pytest.raises(ValueError, match="At least one interest"):
        recommend(manifest, [], top=5)

def test_recommend_large_top():
    """Test boundary condition for large top value."""
    with pytest.raises(ValueError, match="top must be between"):
        recommend(manifest, ["ai"], top=1000)

def test_recommend_no_sessions():
    """Test graceful handling of empty session list."""
    manifest = {"weights": {...}, "sessions": []}
    result = recommend(manifest, ["ai"], top=5)
    assert result["sessions"] == []
```

## Documentation Guidelines

### Update Documentation

When making changes:

- ✅ Update relevant documentation in `/docs`
- ✅ Update docstrings for modified functions
- ✅ Update README.md if public API changes
- ✅ Add examples for new features
- ✅ Update CHANGELOG.md

### Documentation Structure

```text
docs/
├── 00-START-HERE.md          # Entry point
├── 01-GETTING-STARTED/       # Setup guides
├── 02-USER-GUIDES/           # Usage guides
├── 03-GRAPH-API/             # Graph integration
├── 04-ARCHITECTURE/          # System design
├── 05-PRODUCTION/            # Deployment
└── 06-DEVELOPMENT/           # Contributing
```

## Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in appropriate files
- [ ] Tag created: `git tag v1.2.3`
- [ ] Tag pushed: `git push origin v1.2.3`
- [ ] GitHub release created
- [ ] Release notes published

## Getting Help

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Questions, ideas
- **Pull Requests:** Code reviews, discussions
- **Email:** <maintainers@example.com>

### Questions?

- Check existing documentation
- Search closed issues
- Ask in GitHub Discussions
- Tag maintainers in issues

## Recognition

Contributors are recognized in:

- CONTRIBUTORS.md file
- Release notes
- GitHub insights
- Annual contributor summary

## Code of Conduct

Be respectful, inclusive, and collaborative:

- ✅ Be welcoming to newcomers
- ✅ Respect different viewpoints
- ✅ Accept constructive criticism
- ✅ Focus on what's best for the project
- ❌ No harassment or discrimination
- ❌ No trolling or insulting comments

## Next Steps

- 🧪 [Testing Guide](testing.md) — Test suite details
- 🏗️ [Architecture Decisions](architecture-decisions.md) — Design rationale
- 📊 [Performance Guide](../05-PRODUCTION/performance.md) — Optimization
- 🔒 [Security Guide](../05-PRODUCTION/security.md) — Security practices
