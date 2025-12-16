# Governance Guide

## Policy Surface

- Feature flags provide coarse control: disable export or external data ingestion when not approved.
- Telemetry captures action metadata for auditing (success, errors, latency).

## Data Boundaries

- External sessions file is local-only; no network calls performed.
- Profiles stored under user home directory—avoid sensitive interests where possible.

## Observability

- Telemetry JSONL can be rotated and ingested into a broader monitoring stack.
- Summaries allow quick detection of anomalous latency or error spikes.

## Security Considerations

- Input sanitation: interests and session titles are treated as plain text—no execution.
- Avoid embedding secrets in tags or titles; telemetry may log them.

## Compliance Hooks

- Attach export results & telemetry summary for review before distribution.
- Optionally enrich telemetry with user/session identifiers when integrating into enterprise ecosystem (future extension).

## Change Management

- Track manifest edits in version control.
- Maintain `CHANGELOG.md` for weight and feature adjustments.
