# Scoring Algorithm

Deep dive into Event Kit's recommendation scoring algorithm.

## Overview

Event Kit uses a **weighted multi-factor scoring model** to rank sessions based on user interests. The algorithm balances three factors:

1. **Interest Match** — How many of the user's interests match session tags
2. **Popularity** — Session popularity score (organizer-defined)
3. **Diversity** — Reward for diverse interests (encourages exploration)

## Scoring Formula

For each session, the score is calculated as:

```text
score = (interest_match × W_interest) + 
        (popularity × W_popularity) + 
        (diversity_component × W_diversity)

where:
    interest_match = count of matched tags
    popularity = session.popularity (0-10)
    diversity_component = unique_interests_count × 0.01
```

### Default Weights

```json
{
    "interest": 2.0,
    "popularity": 0.5,
    "diversity": 0.3
}
```

## Scoring Breakdown

### 1. Interest Match

**Formula:** `interest_hits × W_interest`

**Calculation:**

```python
# Normalize interests to lowercase
interests = ["ai", "safety", "agents"]

# Normalize session tags to lowercase
session_tags = [t.lower() for t in session["tags"]]

# Count exact matches
interest_hits = sum(1 for tag in session_tags if tag in interests)
interest_score = interest_hits * weights["interest"]
```

**Example:**

```python
# Session: "AI Safety Workshop"
# Tags: ["ai", "safety", "machine learning"]
# Interests: ["ai", "safety", "agents"]

matched_tags = ["ai", "safety"]  # 2 matches
interest_score = 2 × 2.0 = 4.0
```

### 2. Popularity

**Formula:** `session.popularity × W_popularity`

**Calculation:**

```python
popularity_score = session.get("popularity", 0) * weights["popularity"]
```

**Example:**

```python
# Session: "Keynote: Future of AI"
# Popularity: 10 (highest)

popularity_score = 10 × 0.5 = 5.0
```

**Popularity guidelines:**

| Score | Description |
|-------|-------------|
| 0-2 | Niche/specialized |
| 3-5 | Standard session |
| 6-8 | Popular track |
| 9-10 | Keynote/featured |

### 3. Diversity

**Formula:** `len(set(interests)) × 0.01 × W_diversity`

**Calculation:**

```python
unique_interests = len(set(interests))
diversity_component = unique_interests * 0.01
diversity_score = diversity_component * weights["diversity"]
```

**Example:**

```python
# Interests: ["ai", "safety", "agents", "gen ai"]
unique_interests = 4
diversity_component = 4 × 0.01 = 0.04
diversity_score = 0.04 × 0.3 = 0.012
```

**Purpose:** Encourages diverse interest exploration rather than single-topic focus.

## Complete Scoring Example

### Input

**Session:**

```json
{
    "id": "session-42",
    "title": "AI Safety Workshop",
    "tags": ["ai", "safety", "machine learning"],
    "popularity": 7
}
```

**User interests:** `["ai", "safety", "agents"]`

**Weights:**

```json
{
    "interest": 2.0,
    "popularity": 0.5,
    "diversity": 0.3
}
```

### Calculation

```python
# Interest match
matched_tags = ["ai", "safety"]  # 2 matches
interest_score = 2 × 2.0 = 4.0

# Popularity
popularity_score = 7 × 0.5 = 3.5

# Diversity
unique_interests = 3
diversity_component = 3 × 0.01 = 0.03
diversity_score = 0.03 × 0.3 = 0.009

# Total
total_score = 4.0 + 3.5 + 0.009 = 7.509
```

### Scoring Breakdown

```json
{
    "title": "AI Safety Workshop",
    "score": 7.509,
    "contributions": {
        "interest_match": 4.0,
        "popularity": 3.5,
        "diversity": 0.009
    },
    "matched_tags": ["ai", "safety"]
}
```

## Scoring Behavior

### Interest Dominance

With default weights, **interest matching dominates** the score:

- Interest weight: 2.0 (high impact)
- Popularity weight: 0.5 (moderate)
- Diversity weight: 0.3 (low)

**Effect:** Sessions with many matched tags rank higher, even if less popular.

**Example:**

| Session | Matched Tags | Popularity | Score |
|---------|--------------|------------|-------|
| A | 3 | 5 | 8.5 |
| B | 1 | 10 | 7.0 |

Session A ranks higher despite lower popularity.

### Tuning for Balance

To balance interest vs. popularity:

```json
{
    "interest": 1.5,    // Reduce interest weight
    "popularity": 1.0,  // Increase popularity weight
    "diversity": 0.3
}
```

**Effect:** Popular sessions gain more weight, even with fewer matched tags.

### Tuning for Diversity

To encourage broader exploration:

```json
{
    "interest": 2.0,
    "popularity": 0.5,
    "diversity": 1.0    // Increase diversity weight
}
```

**Effect:** Users with diverse interests get slight boost.

## Edge Cases

### No Matched Tags

**Scenario:** Session has no tags matching user interests.

```python
interest_score = 0 × 2.0 = 0.0
total_score = 0.0 + popularity_score + diversity_score
```

**Result:** Score depends only on popularity and diversity. Session may still rank if very popular.

### Zero Popularity

**Scenario:** Session has no popularity score set.

```python
popularity_score = 0 × 0.5 = 0.0
total_score = interest_score + 0.0 + diversity_score
```

**Result:** Purely interest-driven ranking.

### Single Interest

**Scenario:** User provides one interest.

```python
unique_interests = 1
diversity_score = 1 × 0.01 × 0.3 = 0.003
```

**Result:** Minimal diversity contribution.

### Empty Tags

**Scenario:** Session has no tags.

```python
matched_tags = []
interest_score = 0.0
```

**Result:** Falls back to popularity ranking.

## Conflict Detection

After scoring and ranking, Event Kit detects **time slot conflicts**:

```python
def _count_conflicts(sessions: List[Dict]) -> int:
    slots = {}
    for s in sessions:
        slot = (s.get("start"), s.get("end"))
        slots.setdefault(slot, 0)
        slots[slot] += 1
    return sum(1 for count in slots.values() if count > 1)
```

**Example:**

```python
# Recommendations
sessions = [
    {"title": "AI Safety", "start": "9:00", "end": "10:00"},
    {"title": "ML Basics", "start": "9:00", "end": "10:00"},
    {"title": "Ethics", "start": "11:00", "end": "12:00"}
]

conflicts = 2  # Two sessions in 9:00-10:00 slot
```

**Note:** Conflict detection does not affect ranking; it's reported separately.

## Optimization Strategies

### Pre-indexing Tags

For large session sets (>10,000), pre-index tags for faster lookup:

```python
# Build inverted index
tag_index = {}
for session in sessions:
    for tag in session["tags"]:
        tag_index.setdefault(tag.lower(), []).append(session)

# Fast lookup
matching_sessions = set()
for interest in interests:
    matching_sessions.update(tag_index.get(interest, []))
```

**Speedup:** O(1) tag lookup vs. O(N × M) iteration.

### Pre-normalization

Normalize tags once at load time:

```python
def load_sessions_optimized(sessions):
    for session in sessions:
        session["_normalized_tags"] = [t.lower() for t in session["tags"]]
    return sessions
```

**Benefit:** Avoid repeated `.lower()` calls during scoring.

### Caching

Cache scoring results for repeated queries:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def score_session_cached(session_id, interests_tuple, weights_tuple):
    return score_session(session, list(interests_tuple), dict(weights_tuple))
```

**Use case:** HTTP API with repeated similar queries.

## Weight Tuning Guide

### Step 1: Baseline Evaluation

Run recommendations with default weights:

```bash
python agent.py recommend --interests "ai, safety" --top 5
```

Inspect results for:

- Relevance: Are matched tags accurate?
- Diversity: Are results too narrow?
- Popularity: Are popular sessions ranked fairly?

### Step 2: Adjust Weights

**Problem:** Too many obscure sessions ranked high.

**Solution:** Increase popularity weight.

```json
{
    "interest": 2.0,
    "popularity": 1.0,  // Increase from 0.5
    "diversity": 0.3
}
```

**Problem:** All results are from same topic.

**Solution:** Increase diversity weight.

```json
{
    "interest": 2.0,
    "popularity": 0.5,
    "diversity": 1.5  // Increase from 0.3
}
```

**Problem:** Interest matching too dominant.

**Solution:** Reduce interest weight.

```json
{
    "interest": 1.0,  // Reduce from 2.0
    "popularity": 0.8,
    "diversity": 0.5
}
```

### Step 3: Batch Evaluation

Test on multiple profiles:

```bash
python scripts/evaluate_profiles.py
```

Measure:

- **Relevance:** % of results with ≥1 matched tag
- **Diversity:** Unique interests across top 5 results
- **Conflict rate:** % of recommendations with conflicts

### Step 4: Iterate

Adjust weights iteratively until:

- Relevance ≥ 80%
- Diversity ≥ 60%
- Conflict rate < 20%

## Extensibility

### Adding New Scoring Factors

To add a new factor (e.g., **recency**):

**1. Add weight to manifest:**

```json
{
    "weights": {
        "interest": 2.0,
        "popularity": 0.5,
        "diversity": 0.3,
        "recency": 0.4
    }
}
```

**2. Update scoring function:**

```python
def score_session(session, interests, weights):
    # ... existing code ...
    
    # Add recency factor
    days_until = (session["start_date"] - today).days
    recency_score = max(0, 30 - days_until) * weights.get("recency", 0)
    
    contributions["recency"] = recency_score
    total += recency_score
    
    return {"session": session, "score": total, "contributions": contributions}
```

**3. Update scoring breakdown:**

```json
{
    "contributions": {
        "interest_match": 4.0,
        "popularity": 3.5,
        "diversity": 0.009,
        "recency": 12.0
    }
}
```

### Custom Scoring Strategies

Replace the default scoring entirely:

```python
def score_session_custom(session, interests, weights):
    # Semantic similarity using embeddings
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    interest_embedding = model.encode(" ".join(interests))
    session_embedding = model.encode(" ".join(session["tags"]))
    
    similarity = cosine_similarity(interest_embedding, session_embedding)
    
    return {
        "session": session,
        "score": similarity,
        "contributions": {"semantic_similarity": similarity}
    }
```

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Score single session | O(M) | M = interest count |
| Score all sessions | O(N × M) | N = session count |
| Sort by score | O(N log N) | |
| Conflict detection | O(N) | Linear pass |
| **Total** | **O(N × M + N log N)** | Dominated by scoring |

### Latency Benchmarks

| Sessions | Interests | Latency |
|----------|-----------|---------|
| 100 | 3 | 2ms |
| 1,000 | 5 | 12ms |
| 10,000 | 10 | 80ms |
| 100,000 | 10 | 800ms |

**Recommendation:** For >10,000 sessions, use pre-indexing optimization.

## Next Steps

- 🏗️ [System Design](design.md) — Architecture overview
- 📖 [Module Reference](modules.md) — Code reference
- 🎨 [Application Patterns](patterns.md) — Usage patterns
- 📊 [Performance Guide](../05-PRODUCTION/performance.md) — Optimization tips
