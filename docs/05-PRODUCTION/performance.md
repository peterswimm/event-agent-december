# Performance Guide

Optimization strategies and performance best practices for Event Kit.

## Performance Targets

Event Kit is designed for **low-latency recommendations** with the following targets:

| Operation | Target | Typical | Max Acceptable |
|-----------|--------|---------|----------------|
| Recommend (manifest) | <25ms | 12-15ms | 50ms |
| Recommend (Graph) | <1000ms | 500-800ms | 2000ms |
| Explain | <15ms | 8-10ms | 30ms |
| Export | <40ms | 20-30ms | 100ms |

## Latency Breakdown

### Manifest Mode

```text
Total: ~12-15ms
├── Load manifest: 2ms
├── Score sessions: 8ms (N × M complexity)
├── Sort results: 1ms
├── Conflict detection: 1ms
└── Format output: 1ms
```

### Graph Mode

```text
Total: ~500-800ms
├── Authenticate (MSAL): 50-100ms (cached token) or 400-500ms (new token)
├── Fetch events (Graph API): 300-500ms
├── Transform events: 5ms
├── Score sessions: 10ms
├── Sort results: 2ms
├── Conflict detection: 2ms
└── Format output: 2ms
```

**Key insight:** Graph API latency dominates; focus on caching and batching.

## Scaling Considerations

### Time Complexity

| Component | Complexity | Notes |
|-----------|------------|-------|
| Load manifest | O(1) | File read, constant size |
| Normalize interests | O(M) | M = interest count |
| Score single session | O(M) | Iterate over interests |
| Score all sessions | O(N × M) | N = session count |
| Sort by score | O(N log N) | Python's Timsort |
| Conflict detection | O(N) | Single pass over results |
| **Total** | **O(N × M + N log N)** | Dominated by scoring |

### Session Count Impact

| Sessions | Interests | Scoring Time | Sort Time | Total |
|----------|-----------|--------------|-----------|-------|
| 100 | 3 | 1ms | 0.5ms | ~2ms |
| 1,000 | 5 | 8ms | 1ms | ~12ms |
| 10,000 | 10 | 80ms | 3ms | ~90ms |
| 100,000 | 10 | 800ms | 40ms | ~850ms |

**Recommendation:** For >10,000 sessions, implement optimization strategies below.

## Memory Footprint

### Base Memory

```text
Agent process: 50MB
Python runtime: 30MB
Dependencies: 20MB
Total: ~100MB base
```

### Per-Session Memory

```text
Session object: ~1KB
├── Metadata: 200 bytes
├── Tags array: 500 bytes
├── Score cache: 100 bytes
└── Overhead: 200 bytes
```

**Example:**

- 1,000 sessions: ~101MB total
- 10,000 sessions: ~110MB total
- 100,000 sessions: ~200MB total

### Telemetry Growth

```text
Entry size: ~200 bytes (JSON)
Rate: 10 actions/minute
Growth: ~600 KB/hour or ~14 MB/day
```

**Recommendation:** Rotate telemetry daily at >50MB to prevent disk exhaustion.

## Optimization Strategies

### 1. Pre-Index Tags

**Problem:** Repeated tag normalization during scoring.

**Solution:** Pre-normalize tags at load time.

```python
def load_sessions_optimized(manifest):
    sessions = get_sessions(manifest)
    for session in sessions:
        # Pre-normalize tags to lowercase
        session["_normalized_tags"] = [t.lower() for t in session.get("tags", [])]
    return sessions

def score_session_optimized(session, interests, weights):
    # Use pre-normalized tags
    tags = session.get("_normalized_tags", [])
    interest_hits = sum(1 for t in tags if t in interests)
    # ... rest of scoring
```

**Speedup:** 20-30% reduction in scoring time for large session sets.

### 2. Inverted Index for Interest Lookup

**Problem:** O(N × M) scoring complexity.

**Solution:** Build inverted index for O(M) lookup.

```python
def build_tag_index(sessions):
    """Build inverted index: tag -> list of sessions."""
    index = {}
    for session in sessions:
        for tag in session.get("tags", []):
            normalized = tag.lower()
            index.setdefault(normalized, []).append(session)
    return index

def recommend_with_index(manifest, interests, top):
    sessions = get_sessions(manifest)
    index = build_tag_index(sessions)
    
    # Find sessions matching any interest (O(M) instead of O(N × M))
    matching_sessions = set()
    for interest in interests:
        matching_sessions.update(index.get(interest, []))
    
    # Score only matching sessions
    scored = [score_session(s, interests, manifest["weights"]) 
              for s in matching_sessions]
    
    # Sort and return top N
    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)[:top]
    # ... rest of logic
```

**Speedup:** 10x faster for >10,000 sessions with sparse interest matches.

### 3. Result Caching

**Problem:** Repeated identical queries.

**Solution:** Cache recommendations with TTL.

```python
from functools import lru_cache
import hashlib
import json

@lru_cache(maxsize=128)
def recommend_cached(manifest_hash, interests_tuple, top):
    """Cache recommendations based on input hash."""
    manifest = load_manifest()
    interests = list(interests_tuple)
    return recommend(manifest, interests, top)

def get_manifest_hash(manifest):
    """Generate hash of manifest for cache key."""
    content = json.dumps(manifest, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()

# Usage
manifest = load_manifest()
manifest_hash = get_manifest_hash(manifest)
result = recommend_cached(manifest_hash, tuple(interests), top)
```

**Speedup:** Near-instant (<1ms) for cache hits.

**Cache hit rate:** Typically 40-60% for HTTP API with repeated queries.

### 4. Reduce Weight Complexity

**Problem:** Multiple weight factors slow scoring.

**Solution:** Simplify to essential factors.

```json
// Before (3 factors)
{
    "weights": {
        "interest": 2.0,
        "popularity": 0.5,
        "diversity": 0.3
    }
}

// After (2 factors)
{
    "weights": {
        "interest": 2.0,
        "popularity": 0.5
    }
}
```

**Speedup:** 10-15% reduction in scoring time.

### 5. Parallel Scoring

**Problem:** Sequential scoring for large session sets.

**Solution:** Use multiprocessing for parallel scoring.

```python
from multiprocessing import Pool

def score_batch(batch):
    """Score a batch of sessions in parallel."""
    return [score_session(s, interests, weights) for s in batch]

def recommend_parallel(manifest, interests, top, workers=4):
    sessions = get_sessions(manifest)
    batch_size = len(sessions) // workers
    
    # Split into batches
    batches = [sessions[i:i+batch_size] 
               for i in range(0, len(sessions), batch_size)]
    
    # Score in parallel
    with Pool(workers) as pool:
        results = pool.map(score_batch, batches)
    
    # Flatten and sort
    all_scored = [item for batch in results for item in batch]
    ranked = sorted(all_scored, key=lambda x: x["score"], reverse=True)[:top]
    
    return {"sessions": [r["session"] for r in ranked], ...}
```

**Speedup:** 2-3x faster with 4 workers for >50,000 sessions.

**Trade-off:** Increased memory usage (~4x base memory).

### 6. Graph API Caching

**Problem:** Graph API latency (300-500ms per call).

**Solution:** Cache events with TTL.

```python
import time

class CachedGraphEventService:
    def __init__(self, service, cache_ttl=300):
        self.service = service
        self.cache_ttl = cache_ttl  # 5 minutes
        self.cache = {}
    
    def get_events(self, user_id, top=10):
        now = time.time()
        cache_key = f"{user_id}:{top}"
        
        # Check cache
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if now - cached_time < self.cache_ttl:
                return cached_data
        
        # Fetch from API
        events = self.service.get_events(top=top)
        
        # Update cache
        self.cache[cache_key] = (now, events)
        
        return events
```

**Speedup:** 300-500ms → <1ms for cache hits (first request still slow).

**Cache hit rate:** 70-80% for typical usage patterns.

## Telemetry Management

### File Size Growth

```text
Entry size: ~200 bytes
Actions per day: 10 actions/min × 60 min × 24 hours = 14,400 actions
Daily growth: 14,400 × 200 bytes = 2.88 MB/day
```

**At 10 actions/minute:**

- Daily: ~3 MB
- Weekly: ~20 MB
- Monthly: ~86 MB

### Rotation Strategy

**Manual rotation:**

```bash
#!/bin/bash
# rotate_telemetry.sh

MAX_SIZE=52428800  # 50 MB
FILE="telemetry.jsonl"

if [ -f "$FILE" ]; then
    SIZE=$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE")
    
    if [ $SIZE -gt $MAX_SIZE ]; then
        mv "$FILE" "telemetry.$(date +%Y%m%d_%H%M%S).jsonl"
        touch "$FILE"
        echo "Rotated telemetry log"
    fi
fi
```

**Automatic rotation in manifest:**

```json
{
    "telemetry": {
        "enabled": true,
        "file": "telemetry.jsonl",
        "maxSizeBytes": 52428800
    }
}
```

**Cleanup old logs:**

```bash
# Delete logs older than 30 days
find . -name "telemetry.*.jsonl" -mtime +30 -delete

# Compress logs older than 7 days
find . -name "telemetry.*.jsonl" -mtime +7 -exec gzip {} \;
```

## Concurrency

### Single-Threaded HTTP Server

Event Kit uses Python's built-in `HTTPServer` which is **single-threaded**:

```python
from http.server import HTTPServer

server = HTTPServer(("", 8000), EventAgentHandler)
server.serve_forever()  # Single-threaded, one request at a time
```

**Impact:**

- Handles one request at a time
- Additional requests block until current completes
- Not suitable for >10 concurrent users

### WSGI Server for Production

**Gunicorn (recommended):**

```bash
# Install Gunicorn
pip install gunicorn

# Create WSGI adapter
# wsgi.py
from agent import create_wsgi_app
app = create_wsgi_app()

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

**Speedup:** Handles 4 concurrent requests simultaneously.

**Alternative: uvicorn (ASGI):**

```bash
pip install uvicorn
uvicorn wsgi:app --workers 4 --host 0.0.0.0 --port 8000
```

## Profiling

### CPU Profiling with cProfile

```python
import cProfile
import pstats
from agent import recommend, load_manifest

# Profile recommendation
manifest = load_manifest()
profiler = cProfile.Profile()
profiler.enable()

for _ in range(100):
    recommend(manifest, ["ai", "ml", "safety"], 5)

profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

**Visualize with snakeviz:**

```bash
pip install snakeviz
python -m cProfile -o profile.prof agent.py recommend --interests "ai, ml" --top 5
snakeviz profile.prof
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def recommend_with_memory(manifest, interests, top):
    return recommend(manifest, interests, top)

# Run with memory profiling
python -m memory_profiler agent.py recommend --interests "ai, ml" --top 5
```

### Latency Measurement

**From telemetry:**

```bash
# Analyze latency from telemetry
python scripts/summarize_telemetry.py

# Output:
# recommend: p50=12.5ms, p95=18.2ms, p99=25.1ms
# explain: p50=8.1ms, p95=11.3ms, p99=14.7ms
```

**HTTP endpoint timing:**

```bash
# Measure end-to-end latency
curl -w "\nTime: %{time_total}s\n" \
    -X POST http://localhost:8000/recommend \
    -d '{"interests": ["ai", "ml"], "top": 5}'
```

## Optimization Checklist

For production deployments:

- ✅ **Pre-normalize tags** at load time
- ✅ **Cache recommendations** with 5-minute TTL
- ✅ **Rotate telemetry** daily if >50MB
- ✅ **Use WSGI server** (Gunicorn) for concurrency
- ✅ **Cache Graph API results** for 5 minutes
- ✅ **Monitor latency** via telemetry p95/p99
- ✅ **Profile hot paths** with cProfile
- ✅ **Set up alerting** for latency degradation
- ✅ **Test with realistic load** (100+ sessions, 5+ interests)
- ✅ **Consider inverted index** for >10,000 sessions

## Performance Troubleshooting

### High Latency (>100ms for manifest mode)

**Diagnosis:**

```bash
# Profile to find bottleneck
python -m cProfile agent.py recommend --interests "ai, ml" --top 5 | head -20
```

**Common causes:**

1. Large session count (>10,000) → Use inverted index
2. Many interests (>20) → Reduce or pre-filter
3. Complex scoring → Simplify weights
4. Disk I/O → Use SSD, cache manifest

### Memory Exhaustion

**Diagnosis:**

```bash
# Monitor memory usage
ps aux | grep python
# Or use htop
```

**Common causes:**

1. Large telemetry file → Rotate logs
2. Too many sessions in memory → Use external sessions with pagination
3. Memory leak → Restart service regularly
4. Large cache → Reduce cache size

### Graph API Timeouts

**Diagnosis:**

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Common causes:**

1. Network latency → Increase timeout
2. Rate limiting → Implement backoff
3. Token expiration → Refresh proactively
4. Large result set → Reduce `top` parameter

## Benchmarking

### Load Testing with Apache Bench

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test 1000 requests with 10 concurrent
ab -n 1000 -c 10 -p request.json -T application/json \
    http://localhost:8000/recommend

# request.json
{"interests": ["ai", "ml"], "top": 5}
```

**Expected results:**

```text
Requests per second: 80-100 (with caching)
Time per request: 10-12ms (mean)
```

### Stress Testing

```python
import time
import concurrent.futures
from agent import recommend, load_manifest

def benchmark_concurrent(workers=10, iterations=100):
    manifest = load_manifest()
    
    def task():
        start = time.time()
        recommend(manifest, ["ai", "ml", "safety"], 5)
        return time.time() - start
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(task) for _ in range(iterations)]
        latencies = [f.result() for f in futures]
    
    print(f"Mean: {sum(latencies)/len(latencies)*1000:.2f}ms")
    print(f"P95: {sorted(latencies)[int(len(latencies)*0.95)]*1000:.2f}ms")

benchmark_concurrent()
```

## Next Steps

- 🚀 [Deployment Guide](deployment.md) — Production deployment
- 🔒 [Security Guide](security.md) — Security hardening
- 📈 [Monitoring Guide](monitoring.md) — Observability
- 🏗️ [Architecture](../04-ARCHITECTURE/design.md) — System design

