# Performance Guide

## Latency Targets

- Recommend (in-memory, up to 200 sessions): < 25 ms median
- Explain: < 15 ms median
- Export (Markdown build): < 40 ms median

## Scaling Considerations

- Session count growth is linear in scoring time: O(N) over sessions.
- For >10k sessions, pre-index tags (dict tag -> list[session]) to reduce interest match cost.
- Consider caching last recommendation result for identical interest sets.

## Telemetry File Growth

- Each line ~0.5–1 KB. At 10 actions/minute → ~600 KB/hour.
- Rotate file daily or when size > 50 MB.
- Summarizer script aggregates counts; archive raw lines after summary.

## Memory Footprint

- Sessions: ~1 KB per session typical (JSON parsed in memory)
- External override does not duplicate; only active list retained.

## Optimization Levers

- Reduce weight complexity (fewer contributions) for ultra-low latency.
- Pre-normalize interests (lowercase + strip) early.
- Use a list of tags per session already lowercased.

## Concurrency

`HTTPServer` is single-threaded; for higher throughput wrap agent functions in a WSGI/ASGI server (Gunicorn/Uvicorn) or use `ThreadingHTTPServer`.

## Profiling Tips

```bash
python -m cProfile -o profile.out agent.py recommend --interests "agents, ai safety"
snakeviz profile.out
```
