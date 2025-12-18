# Testing & Evaluation Guide

Comprehensive testing and evaluation practices for Event Kit.

## Testing Overview

Event Kit maintains **126 passing tests** with >80% code coverage:

```bash
pytest tests/ -v
# ======================== 126 passed in 2.5s ========================
```

## Test Suite Structure

```text
tests/
├── conftest.py              # Shared fixtures
├── test_recommend.py        # Recommendation logic
├── test_explain.py          # Explanation logic
├── test_export.py           # Export functionality
├── test_profile.py          # Profile management
├── test_external_sessions.py # External data integration
├── test_graph_auth.py       # Graph authentication
├── test_graph_service.py    # Graph API client
├── test_server.py           # HTTP server
└── test_telemetry.py        # Telemetry logging
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_recommend.py

# Run specific test
pytest tests/test_recommend.py::test_recommend_basic

# Run tests matching pattern
pytest tests/ -k "recommend"
```

### Test Coverage

```bash
# Run with coverage
pytest tests/ --cov=. --cov-report=term

# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Coverage summary
pytest tests/ --cov=. --cov-report=term-missing
```

**Coverage targets:**

- Overall: >80%
- Core modules (agent.py, core.py): >90%
- New code: 100%

### Test Performance

```bash
# Show slowest tests
pytest tests/ --durations=10

# Run in parallel (requires pytest-xdist)
pytest tests/ -n auto
```

## Test Categories

### Unit Tests

**Purpose:** Test individual functions in isolation.

**Example:**

```python
def test_score_session_basic():
    """Test basic session scoring."""
    session = {
        "id": "1",
        "title": "AI Workshop",
        "tags": ["ai", "ml"],
        "popularity": 5
    }
    interests = ["ai"]
    weights = {"interest": 2.0, "popularity": 0.5, "diversity": 0.3}
    
    result = score_session(session, interests, weights)
    
    assert result["score"] > 0
    assert result["session"] == session
    assert "interest_match" in result["contributions"]
```

### Integration Tests

**Purpose:** Test multiple components working together.

**Example:**

```python
def test_recommend_end_to_end():
    """Test full recommendation flow."""
    manifest = load_manifest()
    interests = ["ai", "ml", "safety"]
    
    result = recommend(manifest, interests, top=5)
    
    assert "sessions" in result
    assert "scoring" in result
    assert "conflicts" in result
    assert len(result["sessions"]) <= 5
```

### Graph API Tests

**Purpose:** Test Microsoft Graph integration (requires credentials).

**Setup:**

```bash
# Configure Graph credentials
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
export CLIENT_SECRET="your-secret"
export DEFAULT_USER_ID="user@example.com"

# Run Graph tests
pytest tests/test_graph_*.py
```

**Example:**

```python
@pytest.mark.skipif(not GRAPH_AVAILABLE, reason="Graph credentials not configured")
def test_graph_recommend():
    """Test recommendations from Graph API."""
    settings = Settings()
    auth = GraphAuthClient(
        settings.TENANT_ID,
        settings.CLIENT_ID,
        settings.CLIENT_SECRET
    )
    service = GraphEventService(auth, settings.DEFAULT_USER_ID)
    
    result = recommend_from_graph(service, ["ai", "ml"], top=5)
    
    assert result["source"] == "graph"
    assert len(result["sessions"]) > 0
```

## Evaluation Framework

### Evaluation Metrics

Event Kit recommendations are evaluated on four key dimensions:

| Metric | Description | Target |
|--------|-------------|--------|
| **Relevance** | % of results with ≥1 matched interest | ≥80% |
| **Diversity** | Unique interests across results | ≥60% |
| **Conflict Rate** | % of recommendations with time conflicts | <20% |
| **Latency** | Median response time | <25ms |

### Manual Evaluation

**Step 1: Define test profiles**

```json
{
    "test_profiles": [
        {
            "profile_id": "ai_researcher",
            "interests": ["ai", "ml", "research"],
            "expected_sessions": ["AI Safety Workshop", "ML Research Panel"]
        },
        {
            "profile_id": "product_manager",
            "interests": ["product", "strategy"],
            "expected_sessions": ["Product Roadmap", "Strategy Workshop"]
        }
    ]
}
```

**Step 2: Run recommendations**

```bash
# Generate recommendations for each profile
for profile in ai_researcher product_manager; do
    python agent.py recommend \
        --profile-load $profile \
        --top 5 \
        --output results_${profile}.json
done
```

**Step 3: Inspect results**

```python
import json

def evaluate_recommendation(result, expected_sessions):
    """Evaluate recommendation quality."""
    recommended_titles = [s["title"] for s in result["sessions"]]
    
    # Relevance: How many expected sessions were included?
    matches = sum(1 for title in expected_sessions if title in recommended_titles)
    relevance = matches / len(expected_sessions) if expected_sessions else 0
    
    # Diversity: How many unique interests?
    all_tags = set()
    for session in result["sessions"]:
        all_tags.update(session.get("tags", []))
    diversity = len(all_tags)
    
    # Conflicts
    conflict_rate = result["conflicts"] / len(result["sessions"]) if result["sessions"] else 0
    
    return {
        "relevance": relevance,
        "diversity": diversity,
        "conflict_rate": conflict_rate
    }

# Load and evaluate
with open("results_ai_researcher.json") as f:
    result = json.load(f)
    metrics = evaluate_recommendation(result, ["AI Safety Workshop", "ML Research Panel"])
    print(f"Relevance: {metrics['relevance']:.2%}")
    print(f"Diversity: {metrics['diversity']} unique interests")
    print(f"Conflict rate: {metrics['conflict_rate']:.2%}")
```

### Automated Evaluation

**Batch evaluation script:**

```python
# scripts/evaluate_profiles.py
import json
from pathlib import Path
from agent import recommend, load_manifest

def run_evaluation(test_profiles_file):
    """Run automated evaluation on test profiles."""
    manifest = load_manifest()
    profiles = json.loads(Path(test_profiles_file).read_text())
    
    results = []
    for profile in profiles:
        result = recommend(manifest, profile["interests"], top=5)
        
        # Calculate metrics
        recommended_titles = [s["title"] for s in result["sessions"]]
        expected = profile.get("expected_sessions", [])
        
        relevance = sum(1 for t in expected if t in recommended_titles) / len(expected) if expected else 0
        
        all_tags = set()
        for s in result["sessions"]:
            all_tags.update(s.get("tags", []))
        diversity_score = len(all_tags) / len(profile["interests"]) if profile["interests"] else 0
        
        conflict_rate = result["conflicts"] / len(result["sessions"]) if result["sessions"] else 0
        
        results.append({
            "profile_id": profile["profile_id"],
            "relevance": relevance,
            "diversity": diversity_score,
            "conflict_rate": conflict_rate,
            "passed": relevance >= 0.8 and diversity_score >= 0.6 and conflict_rate < 0.2
        })
    
    # Print summary
    print("\n=== Evaluation Results ===")
    for r in results:
        status = "✓ PASS" if r["passed"] else "✗ FAIL"
        print(f"{status} {r['profile_id']}")
        print(f"  Relevance: {r['relevance']:.2%} (target: ≥80%)")
        print(f"  Diversity: {r['diversity']:.2f} (target: ≥0.6)")
        print(f"  Conflicts: {r['conflict_rate']:.2%} (target: <20%)")
    
    # Overall pass rate
    pass_rate = sum(1 for r in results if r["passed"]) / len(results)
    print(f"\nOverall pass rate: {pass_rate:.2%}")
    
    return results

if __name__ == "__main__":
    run_evaluation("test_profiles.json")
```

**Run evaluation:**

```bash
python scripts/evaluate_profiles.py
```

**Expected output:**

```text
=== Evaluation Results ===
✓ PASS ai_researcher
  Relevance: 85% (target: ≥80%)
  Diversity: 0.67 (target: ≥0.6)
  Conflicts: 10% (target: <20%)

✓ PASS product_manager
  Relevance: 80% (target: ≥80%)
  Diversity: 0.70 (target: ≥0.6)
  Conflicts: 5% (target: <20%)

Overall pass rate: 100%
```

### Telemetry-Based Evaluation

**Analyze latency from telemetry:**

```python
# scripts/analyze_latency.py
import json
from pathlib import Path
import statistics

def analyze_latency(telemetry_file):
    """Analyze latency metrics from telemetry."""
    latencies = {"recommend": [], "explain": [], "export": []}
    
    with open(telemetry_file) as f:
        for line in f:
            entry = json.loads(line)
            action = entry["action"]
            if action in latencies and entry["success"]:
                latencies[action].append(entry["latency_ms"])
    
    # Calculate percentiles
    for action, values in latencies.items():
        if values:
            values.sort()
            p50 = values[int(len(values) * 0.50)]
            p95 = values[int(len(values) * 0.95)]
            p99 = values[int(len(values) * 0.99)]
            
            print(f"{action}:")
            print(f"  P50: {p50:.2f}ms")
            print(f"  P95: {p95:.2f}ms")
            print(f"  P99: {p99:.2f}ms")
            print(f"  Mean: {statistics.mean(values):.2f}ms")
            print(f"  Median: {statistics.median(values):.2f}ms")

if __name__ == "__main__":
    analyze_latency("telemetry.jsonl")
```

**Run analysis:**

```bash
python scripts/analyze_latency.py
```

**Expected output:**

```text
recommend:
  P50: 12.5ms
  P95: 18.2ms
  P99: 25.1ms
  Mean: 13.8ms
  Median: 12.5ms

explain:
  P50: 8.1ms
  P95: 11.3ms
  P99: 14.7ms
  Mean: 8.9ms
  Median: 8.1ms
```

## Weight Tuning

### Iterative Tuning Process

**Goal:** Optimize weights to achieve target metrics.

**Process:**

```text
1. Set baseline weights
2. Run evaluation
3. Analyze results (which metric is low?)
4. Adjust relevant weight
5. Repeat until targets met
```

**Example tuning session:**

```bash
# Initial weights
{
    "interest": 2.0,
    "popularity": 0.5,
    "diversity": 0.3
}

# Problem: Diversity too low (0.45, target 0.6)
# Solution: Increase diversity weight

{
    "interest": 2.0,
    "popularity": 0.5,
    "diversity": 1.0  # Increased from 0.3
}

# Re-evaluate
python scripts/evaluate_profiles.py
# Result: Diversity now 0.62 ✓

# Problem: Relevance dropped to 75% (target 80%)
# Solution: Slightly increase interest weight

{
    "interest": 2.5,  # Increased from 2.0
    "popularity": 0.5,
    "diversity": 1.0
}

# Re-evaluate
python scripts/evaluate_profiles.py
# Result: Relevance 82% ✓, Diversity 0.61 ✓
```

### Score Interpretation

**Understanding contribution breakdown:**

```json
{
    "title": "AI Safety Workshop",
    "score": 7.509,
    "contributions": {
        "interest_match": 4.0,   // Dominant factor
        "popularity": 3.5,       // Moderate impact
        "diversity": 0.009       // Minimal impact
    }
}
```

**Insights:**

- Interest match dominates (4.0 out of 7.5 total)
- Popularity provides secondary signal
- Diversity has minimal effect with default weights

**Adjustment strategy:**

- If too interest-focused → Reduce interest weight or increase others
- If unpopular sessions rank high → Increase popularity weight
- If results too narrow → Increase diversity weight

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest tests/ --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/
        language: system
        pass_filenames: false
        always_run: true
```

**Install pre-commit:**

```bash
pip install pre-commit
pre-commit install
```

## Performance Testing

### Load Testing

```python
# tests/test_performance.py
import time
from agent import recommend, load_manifest

def test_recommend_latency():
    """Test recommendation latency meets target."""
    manifest = load_manifest()
    interests = ["ai", "ml", "safety"]
    
    # Warm up
    recommend(manifest, interests, 5)
    
    # Measure latency
    latencies = []
    for _ in range(100):
        start = time.perf_counter()
        recommend(manifest, interests, 5)
        latencies.append((time.perf_counter() - start) * 1000)
    
    # Assert targets
    p50 = sorted(latencies)[50]
    p95 = sorted(latencies)[95]
    
    assert p50 < 25, f"P50 latency {p50:.2f}ms exceeds 25ms target"
    assert p95 < 50, f"P95 latency {p95:.2f}ms exceeds 50ms target"
```

### Stress Testing

```python
def test_recommend_high_load():
    """Test recommendation under high load."""
    manifest = load_manifest()
    
    # Simulate 1000 concurrent users
    for i in range(1000):
        result = recommend(manifest, ["ai", "ml"], 5)
        assert len(result["sessions"]) > 0
```

## Best Practices

### Test Writing

- ✅ **One assertion per test** (or closely related assertions)
- ✅ **Clear test names** describing what is tested
- ✅ **Arrange-Act-Assert pattern** for clarity
- ✅ **Use fixtures** for common setup
- ✅ **Test edge cases** not just happy path
- ✅ **Mock external dependencies** (Graph API)
- ✅ **Clean up test data** in teardown

### Evaluation

- ✅ **Define success criteria** before testing
- ✅ **Use realistic test data** matching production
- ✅ **Test multiple personas** (different interests)
- ✅ **Track metrics over time** (regression detection)
- ✅ **Document weight tuning decisions** in CHANGELOG
- ✅ **Re-evaluate after code changes** (CI integration)

## Next Steps

- 🤝 [Contributing Guide](contributing.md) — How to contribute
- 🏗️ [Architecture Decisions](architecture-decisions.md) — Design rationale
- 📊 [Performance Guide](../05-PRODUCTION/performance.md) — Optimization
- 🎯 [Scoring Algorithm](../04-ARCHITECTURE/scoring-algorithm.md) — Deep dive
