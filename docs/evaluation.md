# Evaluation Guide

## Metrics

- Recommendation relevance: fraction of recommended sessions with ≥1 matched interest tag.
- Diversity: count of unique interests represented across top-N sessions.
- Conflict count: overlapping time slots among recommended sessions.
- Latency: median `latency_ms` for recommend and explain actions.

## Manual Evaluation

1. Define interest profiles (e.g., `governance`, `agents`, `responsible ai`).
2. Run recommendations, capture scoring contributions.
3. Inspect diversity vs conflicts trade-off.

## Automated Batch (Future Script)

Pseudo-flow for `evaluate_profiles.py`:

```text
for profile in profiles:
  run recommend
  record relevance, diversity, conflicts, latency
aggregate summary table
```

## Interpreting Scores

- High interest contribution dominance may hide diversity value; adjust `weights.diversity` upward.
- Frequent conflicts can indicate clustering—consider schedule rebalancing.

## Telemetry-Based Latency

Use summarizer to compute median latency:

```bash
python scripts/summarize_telemetry.py | jq '.latency.median'
```

## Adjusting Thresholds

Tune weights iteratively and re-run evaluation to converge on acceptable relevance/diversity ratio (e.g., ≥80% relevance with ≥60% diversity coverage).
