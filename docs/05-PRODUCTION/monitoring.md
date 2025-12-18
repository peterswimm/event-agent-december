# Monitoring & Observability

Comprehensive guide to monitoring, logging, and observability for Event Kit.

## Overview

Event Kit provides multiple observability layers:

```text
┌─────────────────────────────────────┐
│  Metrics (Telemetry Aggregation)   │
├─────────────────────────────────────┤
│  Logs (Application & System)        │
├─────────────────────────────────────┤
│  Health Checks (HTTP Endpoint)      │
├─────────────────────────────────────┤
│  Tracing (Request Flow)             │
└─────────────────────────────────────┘
```

## Telemetry System

### Telemetry Schema

Each action logged to `telemetry.jsonl`:

```json
{
    "ts": 1732540000.123,        // Unix timestamp (float)
    "action": "recommend",        // Action name
    "success": true,              // Success flag
    "latency_ms": 12.5,          // Latency in milliseconds
    "payload": {                  // Action-specific data
        "interests_count": 3,
        "top": 5,
        "source": "manifest",
        "conflicts": 2
    },
    "error": null                 // Error message if failed
}
```

### Telemetry Configuration

In `agent.json`:

```json
{
    "telemetry": {
        "enabled": true,
        "file": "telemetry.jsonl",
        "maxSizeBytes": 52428800  // 50 MB
    }
}
```

### Telemetry Analysis

**Summarize telemetry:**

```bash
python scripts/summarize_telemetry.py
```

**Output:**

```text
=== Telemetry Summary ===
Total actions: 1,234
Success rate: 98.5%

Action breakdown:
  recommend: 800 (64.8%)
  explain: 300 (24.3%)
  export: 134 (10.9%)

Latency (ms):
  recommend: p50=12.5, p95=18.2, p99=25.1
  explain: p50=8.1, p95=11.3, p99=14.7
  export: p50=22.3, p95=35.8, p99=42.1

Error rate: 1.5% (18 failures)
```

**Query telemetry with jq:**

```bash
# Count actions by type
jq -r '.action' telemetry.jsonl | sort | uniq -c

# Average latency by action
jq -r 'select(.action == "recommend") | .latency_ms' telemetry.jsonl | \
    awk '{sum+=$1; n++} END {print "Avg: " sum/n "ms"}'

# Find slow requests (>100ms)
jq 'select(.latency_ms > 100)' telemetry.jsonl

# Errors in last hour
jq --arg now $(date +%s) \
    'select(.success == false and .ts > ($now | tonumber - 3600))' \
    telemetry.jsonl
```

## Application Logging

### Log Configuration

`logging_config.py` configures structured logging:

```python
import logging
from pathlib import Path

def setup_logging(level="INFO"):
    log_file = Path.home() / ".event_agent.log"
    
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
```

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Development details | "Scoring session: AI Safety Workshop" |
| INFO | Normal operations | "Serving HTTP on port 8000" |
| WARNING | Recoverable issues | "Graph API rate limit, retrying" |
| ERROR | Operation failures | "Failed to load manifest" |
| CRITICAL | System failures | "Cannot start server, port in use" |

### Log Locations

- **Application logs:** `~/.event_agent.log`
- **Telemetry logs:** `./telemetry.jsonl`
- **System logs (systemd):** `journalctl -u event-agent`
- **Docker logs:** `docker logs event-agent`

### Log Analysis

**View recent errors:**

```bash
grep ERROR ~/.event_agent.log | tail -20
```

**Monitor logs in real-time:**

```bash
tail -f ~/.event_agent.log
```

**Count errors by type:**

```bash
grep ERROR ~/.event_agent.log | \
    awk -F ' - ' '{print $NF}' | \
    sort | uniq -c | sort -rn
```

## Health Checks

### HTTP Health Endpoint

**Endpoint:** `GET /health`

**Response (healthy):**

```json
{
    "status": "healthy",
    "timestamp": "2024-03-15T08:30:00Z",
    "version": "1.0.0",
    "uptime_seconds": 86400
}
```

**Response (unhealthy):**

```json
{
    "status": "unhealthy",
    "timestamp": "2024-03-15T08:30:00Z",
    "errors": [
        "Cannot load manifest",
        "Graph API authentication failed"
    ]
}
```

### Uptime Monitoring

**Ping health endpoint:**

```bash
#!/bin/bash
# monitor_health.sh

while true; do
    response=$(curl -s http://localhost:8000/health)
    status=$(echo $response | jq -r '.status')
    
    if [ "$status" != "healthy" ]; then
        echo "[ALERT] Service unhealthy: $response" | \
            mail -s "Event Agent Down" admin@example.com
    fi
    
    sleep 60  # Check every minute
done
```

**External monitoring:**

- **Pingdom** — HTTP uptime checks
- **UptimeRobot** — Free uptime monitoring
- **StatusCake** — Global monitoring network

## Metrics Collection

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Request Rate** | Requests per second | >10/s production |
| **Success Rate** | % of successful requests | >99% |
| **Latency P50** | Median response time | <25ms (manifest) |
| **Latency P95** | 95th percentile | <50ms (manifest) |
| **Latency P99** | 99th percentile | <100ms (manifest) |
| **Error Rate** | % of failed requests | <1% |
| **Uptime** | % of time service available | >99.9% |

### Metrics from Telemetry

**Calculate metrics:**

```python
# scripts/calculate_metrics.py
import json
from pathlib import Path
from datetime import datetime, timedelta

def calculate_metrics(telemetry_file, window_hours=24):
    now = datetime.now().timestamp()
    cutoff = now - (window_hours * 3600)
    
    entries = []
    with open(telemetry_file) as f:
        for line in f:
            entry = json.loads(line)
            if entry["ts"] >= cutoff:
                entries.append(entry)
    
    total = len(entries)
    success = sum(1 for e in entries if e["success"])
    latencies = [e["latency_ms"] for e in entries]
    
    # Sort for percentiles
    latencies.sort()
    
    metrics = {
        "total_requests": total,
        "success_rate": (success / total * 100) if total > 0 else 0,
        "error_rate": ((total - success) / total * 100) if total > 0 else 0,
        "latency_p50": latencies[int(len(latencies) * 0.5)] if latencies else 0,
        "latency_p95": latencies[int(len(latencies) * 0.95)] if latencies else 0,
        "latency_p99": latencies[int(len(latencies) * 0.99)] if latencies else 0,
        "requests_per_second": total / (window_hours * 3600)
    }
    
    return metrics

# Run
metrics = calculate_metrics("telemetry.jsonl", window_hours=24)
print(json.dumps(metrics, indent=2))
```

### Export to Prometheus

**Expose metrics endpoint:**

```python
# metrics_exporter.py
from prometheus_client import Counter, Histogram, start_http_server
import json
import time

# Define metrics
request_counter = Counter('event_agent_requests_total', 'Total requests', ['action'])
latency_histogram = Histogram('event_agent_latency_seconds', 'Request latency', ['action'])
error_counter = Counter('event_agent_errors_total', 'Total errors', ['action'])

def export_metrics(telemetry_file):
    """Read telemetry and export to Prometheus."""
    with open(telemetry_file) as f:
        for line in f:
            entry = json.loads(line)
            action = entry["action"]
            
            request_counter.labels(action=action).inc()
            latency_histogram.labels(action=action).observe(entry["latency_ms"] / 1000)
            
            if not entry["success"]:
                error_counter.labels(action=action).inc()

# Start Prometheus exporter on port 9090
start_http_server(9090)
export_metrics("telemetry.jsonl")

# Keep running
while True:
    time.sleep(60)
```

**Prometheus scrape config:**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'event-agent'
    static_configs:
      - targets: ['localhost:9090']
```

## Alerting

### Alert Conditions

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| Service Down | Health check fails 3x | Critical | Page on-call |
| High Error Rate | >5% errors in 5min | High | Notify team |
| High Latency | P95 >100ms for 10min | Medium | Investigate |
| Disk Full | <10% disk free | High | Rotate logs |
| Auth Failures | >10 failures in 1min | Medium | Review access |

### Alerting with AlertManager

**AlertManager rules:**

```yaml
# alert_rules.yml
groups:
  - name: event_agent
    interval: 30s
    rules:
      - alert: EventAgentDown
        expr: up{job="event-agent"} == 0
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "Event Agent service is down"
          description: "Service has been down for 3 minutes"
      
      - alert: HighErrorRate
        expr: rate(event_agent_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, event_agent_latency_seconds) > 0.1
        for: 10m
        labels:
          severity: medium
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s"
```

### Email Alerts

**Simple email alerting:**

```bash
#!/bin/bash
# alert_on_errors.sh

ERROR_THRESHOLD=10
ERROR_COUNT=$(jq 'select(.success == false)' telemetry.jsonl | tail -100 | wc -l)

if [ $ERROR_COUNT -gt $ERROR_THRESHOLD ]; then
    echo "High error rate: $ERROR_COUNT errors in last 100 requests" | \
        mail -s "[ALERT] Event Agent Errors" admin@example.com
fi
```

**Schedule with cron:**

```cron
*/5 * * * * /path/to/alert_on_errors.sh
```

## Dashboards

### Grafana Dashboard

**Import dashboard JSON:**

```json
{
    "dashboard": {
        "title": "Event Agent Monitoring",
        "panels": [
            {
                "title": "Request Rate",
                "targets": [
                    {
                        "expr": "rate(event_agent_requests_total[5m])"
                    }
                ]
            },
            {
                "title": "Error Rate",
                "targets": [
                    {
                        "expr": "rate(event_agent_errors_total[5m]) / rate(event_agent_requests_total[5m])"
                    }
                ]
            },
            {
                "title": "Latency Percentiles",
                "targets": [
                    {
                        "expr": "histogram_quantile(0.5, event_agent_latency_seconds)",
                        "legendFormat": "P50"
                    },
                    {
                        "expr": "histogram_quantile(0.95, event_agent_latency_seconds)",
                        "legendFormat": "P95"
                    },
                    {
                        "expr": "histogram_quantile(0.99, event_agent_latency_seconds)",
                        "legendFormat": "P99"
                    }
                ]
            }
        ]
    }
}
```

### Terminal Dashboard

**Real-time monitoring with watch:**

```bash
#!/bin/bash
# dashboard.sh

while true; do
    clear
    echo "=== Event Agent Dashboard ==="
    echo ""
    
    # Service status
    echo "Service Status:"
    curl -s http://localhost:8000/health | jq '.status'
    echo ""
    
    # Request count (last hour)
    echo "Requests (last hour):"
    jq --arg now $(date +%s) \
        'select(.ts > ($now | tonumber - 3600))' \
        telemetry.jsonl | wc -l
    echo ""
    
    # Error rate (last hour)
    echo "Error Rate (last hour):"
    jq --arg now $(date +%s) \
        'select(.ts > ($now | tonumber - 3600) and .success == false)' \
        telemetry.jsonl | wc -l
    echo ""
    
    # Average latency (last 100)
    echo "Avg Latency (last 100):"
    tail -100 telemetry.jsonl | \
        jq -r '.latency_ms' | \
        awk '{sum+=$1; n++} END {printf "%.2fms\n", sum/n}'
    
    sleep 5
done
```

**Run dashboard:**

```bash
./dashboard.sh
```

## Tracing

### Request Tracing

**Add trace ID to requests:**

```python
import uuid
from functools import wraps

def trace_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        trace_id = str(uuid.uuid4())
        logger.info(f"[{trace_id}] Request started: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"[{trace_id}] Request completed")
            return result
        except Exception as e:
            logger.error(f"[{trace_id}] Request failed: {e}")
            raise
    
    return wrapper

@trace_request
def recommend(manifest, interests, top):
    # ... implementation
```

### Distributed Tracing

**OpenTelemetry integration:**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Setup tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Add span processor
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

# Trace function
def recommend_traced(manifest, interests, top):
    with tracer.start_as_current_span("recommend"):
        with tracer.start_as_current_span("load_sessions"):
            sessions = get_sessions(manifest)
        
        with tracer.start_as_current_span("score_sessions"):
            scored = [score_session(s, interests, manifest["weights"]) 
                      for s in sessions]
        
        with tracer.start_as_current_span("sort_results"):
            ranked = sorted(scored, key=lambda x: x["score"], reverse=True)[:top]
        
        return {"sessions": [r["session"] for r in ranked]}
```

## Log Rotation

### Automatic Rotation

**systemd-based rotation:**

```ini
# /etc/logrotate.d/event-agent
/home/appuser/.event_agent.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 appuser appuser
}
```

**Test rotation:**

```bash
sudo logrotate -f /etc/logrotate.d/event-agent
```

### Manual Rotation Script

```bash
#!/bin/bash
# rotate_logs.sh

LOG_FILE="$HOME/.event_agent.log"
MAX_SIZE=104857600  # 100 MB

if [ -f "$LOG_FILE" ]; then
    SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE")
    
    if [ $SIZE -gt $MAX_SIZE ]; then
        # Rotate log
        mv "$LOG_FILE" "$LOG_FILE.$(date +%Y%m%d_%H%M%S)"
        touch "$LOG_FILE"
        
        # Compress old logs
        gzip "$LOG_FILE".*[0-9] 2>/dev/null
        
        # Delete logs older than 30 days
        find . -name ".event_agent.log.*.gz" -mtime +30 -delete
        
        echo "Log rotated"
    fi
fi
```

## Troubleshooting

### High Memory Usage

**Identify memory leak:**

```bash
# Monitor memory over time
while true; do
    ps aux | grep python | awk '{print $4, $6}'
    sleep 60
done
```

**Solution:** Restart service periodically or investigate with memory profiler.

### Missing Telemetry

**Check telemetry config:**

```bash
jq '.telemetry' agent.json
```

**Verify file permissions:**

```bash
ls -l telemetry.jsonl
```

**Check disk space:**

```bash
df -h .
```

### Slow Queries

**Analyze slow requests:**

```bash
jq 'select(.latency_ms > 100)' telemetry.jsonl | \
    jq -r '"\(.action): \(.latency_ms)ms - \(.payload)"'
```

**Solution:** Enable caching, optimize scoring, or increase resources.

## Best Practices

- ✅ **Monitor P95/P99 latency** — More reliable than averages
- ✅ **Set up alerts early** — Don't wait for production issues
- ✅ **Rotate logs daily** — Prevent disk exhaustion
- ✅ **Track error rate trends** — Catch regressions early
- ✅ **Dashboard key metrics** — Make data visible
- ✅ **Correlate metrics** — Latency + error rate + request rate
- ✅ **Test alerting** — Verify alerts fire correctly
- ✅ **Document runbooks** — How to respond to alerts
- ✅ **Review metrics weekly** — Identify long-term trends
- ✅ **Archive telemetry** — Keep for compliance/analysis

## Next Steps

- 🚀 [Deployment Guide](deployment.md) — Production deployment
- 📊 [Performance Guide](performance.md) — Optimization strategies
- 🔒 [Security Guide](security.md) — Security best practices
- 🏗️ [Architecture](../04-ARCHITECTURE/design.md) — System design
