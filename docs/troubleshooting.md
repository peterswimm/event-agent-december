# Troubleshooting

## Common Issues

### Empty Interests Error

Message: `{ "error": "no interests provided" }`

Cause: No `--interests` or profile load returned empty list.
Fix: Supply `--interests` or save a profile with `--profile-save` earlier.

### Session Not Found

Explain output: `{ "error": "session not found" }`
Fix: Verify exact title or list available sessions via a recommend call.

### External Sessions Ignored

Cause: `features.externalSessions.enabled` false or file missing/invalid.
Fix: Enable flag in manifest and create valid `sessions_external.json` list.

### Telemetry File Not Created

Cause: `telemetry.enabled` set to false or no actions executed.
Fix: Enable flag and trigger `recommend` or `explain`.

### High Latency Spikes

Cause: Large external sessions list or system load.
Fix: Profile with `cProfile`; pre-index tags or reduce session set for test runs.

### Export Not Saving File

Cause: Export feature disabled or no write permission.
Fix: Enable `features.export.enabled`; check directory permissions.

## Verification Checklist

- Manifest weights present and numeric
- Features block enabled as needed
- Telemetry file grows after actions
- External sessions override returns expected titles

## Collect Diagnostics

```bash
wc -l telemetry.jsonl
tail -n 5 telemetry.jsonl
python scripts/summarize_telemetry.py
```
