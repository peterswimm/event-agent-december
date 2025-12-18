# Application Patterns

Common patterns and workflows for using Event Kit effectively.

## Overview

This guide covers real-world usage patterns for Event Kit, including:

- Profiles-first recommendation workflow
- External data integration
- Governance-aware export
- Adaptive card delivery
- Daily rotation strategies

## Pattern 1: Profiles-First Recommendation

**Use case:** Users with consistent interests who want quick, repeatable recommendations.

### Workflow

```text
1. Define profile with saved interests
2. Run recommendations using profile
3. Compare results over time
4. Adjust profile as interests evolve
```

### Implementation

**Step 1: Create and save profile**

```bash
# Save profile with interests
python agent.py recommend \
    --interests "ai safety, agents, alignment" \
    --profile-save research_focus \
    --top 5
```

**Profile storage** (`~/.event_agent_profiles.json`):

```json
{
    "research_focus": ["ai safety", "agents", "alignment"],
    "product_mgmt": ["product", "roadmap", "strategy"]
}
```

**Step 2: Load profile for recommendations**

```bash
# Quick recommendations using saved profile
python agent.py recommend \
    --profile-load research_focus \
    --top 5
```

**Step 3: Compare over time**

```bash
# Run daily and track changes
python agent.py recommend --profile-load research_focus --top 5 > day1.json
python agent.py recommend --profile-load research_focus --top 5 > day2.json
diff day1.json day2.json
```

**Step 4: Update profile**

```bash
# Add new interest to existing profile
python agent.py recommend \
    --interests "ai safety, agents, alignment, rlhf" \
    --profile-save research_focus \
    --top 5
```

### Benefits

- ✅ **Fast**: No need to type interests repeatedly
- ✅ **Consistent**: Same criteria across runs
- ✅ **Auditable**: Profile history in version control
- ✅ **Scalable**: Multiple profiles for different contexts

### Use Cases

- Daily event recommendations for recurring conferences
- A/B testing different interest sets
- Team-based profiles for group schedules
- Persona-based recommendations

## Pattern 2: External Data Refresh

**Use case:** Integrate upstream data sources (CSV, API, database) into recommendations.

### Workflow

```text
1. Fetch data from external source
2. Transform to Event Kit schema
3. Write to sessions_external.json
4. Enable external sessions feature
5. Run recommendations (uses external data)
```

### Implementation

**Step 1: Fetch data from API**

```python
# scripts/fetch_external_sessions.py
import requests
import json

# Fetch from upstream API
response = requests.get("https://api.example.com/events")
external_events = response.json()

# Transform to Event Kit schema
sessions = []
for event in external_events:
    sessions.append({
        "id": event["id"],
        "title": event["name"],
        "start": event["start_time"],
        "end": event["end_time"],
        "location": event["room"],
        "tags": event["topics"],
        "popularity": event.get("attendee_count", 0) // 10
    })

# Write to external sessions file
with open("sessions_external.json", "w") as f:
    json.dump(sessions, f, indent=2)
```

**Step 2: Enable external sessions**

In `agent.json`:

```json
{
    "features": {
        "externalSessions": {
            "enabled": true,
            "file": "sessions_external.json"
        }
    }
}
```

**Step 3: Run recommendations**

```bash
# Automatically uses external data
python agent.py recommend --interests "ai, ml" --top 5
```

**External file format** (`sessions_external.json`):

```json
[
    {
        "id": "ext-session-1",
        "title": "AI Safety Workshop",
        "start": "2024-03-15T09:00:00",
        "end": "2024-03-15T10:30:00",
        "location": "Room 101",
        "tags": ["ai", "safety", "research"],
        "popularity": 8
    }
]
```

### Benefits

- ✅ **Decoupled**: No changes to agent.py code
- ✅ **Flexible**: Works with any data source
- ✅ **Override**: External data replaces manifest sessions
- ✅ **Testable**: Switch between manifest and external for testing

### Use Cases

- Live conference schedule updates
- Integration with ticketing systems (Eventbrite, Cvent)
- SharePoint calendar sync
- Database-backed session management

## Pattern 3: Governance-Aware Export

**Use case:** Export recommendations with telemetry summary for review and compliance.

### Workflow

```text
1. Run recommendations and collect telemetry
2. Export itinerary with telemetry summary
3. Review export for accuracy and compliance
4. Distribute to users
```

### Implementation

**Step 1: Run recommendations (telemetry logged)**

```bash
python agent.py recommend \
    --interests "ai, safety" \
    --top 5
```

**Step 2: Export with telemetry summary**

```bash
python agent.py export \
    --interests "ai, safety" \
    --top 5 \
    --output itinerary.md
```

**Output** (`itinerary.md`):

```markdown
# Event Itinerary

**Recommended for:** ai, safety

## AI Safety Workshop

Time: 9:00 - 10:30 | Location: Room 101
Tags: ai, safety, research

## Machine Learning Ethics

Time: 11:00 - 12:00 | Location: Room 202
Tags: ml, ethics, governance

---

## Telemetry Summary

- Total actions: 15
- Success rate: 93%
- Median latency: 12.5ms
- Last run: 2024-03-15 08:30:00
```

**Step 3: Review export**

Check for:

- ✅ No PII in session titles or tags
- ✅ Accurate scoring (verify matched tags)
- ✅ No time conflicts
- ✅ Telemetry shows expected latency

**Step 4: Distribute**

```bash
# Send to attendees
cat itinerary.md | mail -s "Your Event Schedule" attendee@example.com
```

### Benefits

- ✅ **Auditable**: Telemetry summary included
- ✅ **Compliant**: Review before distribution
- ✅ **Traceable**: Track recommendation history
- ✅ **Transparent**: Users see scoring rationale

### Use Cases

- Enterprise compliance (GDPR, CCPA)
- Internal audit trails
- SLA monitoring (latency tracking)
- Quality assurance workflows

## Pattern 4: Adaptive Card Delivery

**Use case:** Deliver recommendations as actionable Adaptive Cards in Microsoft Teams/Outlook.

### Workflow

```text
1. Generate recommendations
2. Format as Adaptive Card JSON
3. Send via Teams webhook or Bot Framework
4. Users interact (view, register, dismiss)
```

### Implementation

**Step 1: Generate Adaptive Card**

```python
# Generate card from recommendations
from agent import recommend, load_manifest, _build_adaptive_card

manifest = load_manifest()
result = recommend(manifest, ["ai", "safety"], 3)
card = _build_adaptive_card(result["sessions"])
```

**Card format:**

```json
{
    "type": "AdaptiveCard",
    "version": "1.4",
    "body": [
        {
            "type": "Container",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "1. AI Safety Workshop",
                    "weight": "Bolder"
                },
                {
                    "type": "TextBlock",
                    "text": "Time: 9:00 - 10:30 | Location: Room 101"
                }
            ]
        }
    ],
    "actions": [
        {
            "type": "Action.OpenUrl",
            "title": "View Details",
            "url": "https://example.com/session/1"
        }
    ]
}
```

**Step 2: Send via Teams webhook**

```python
import requests

webhook_url = "https://outlook.office.com/webhook/..."
payload = {
    "type": "message",
    "attachments": [{
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": card
    }]
}

requests.post(webhook_url, json=payload)
```

**Step 3: User interaction**

Users can:

- Click "View Details" to open session page
- Reply with feedback
- Dismiss card when done

### Benefits

- ✅ **Interactive**: Clickable actions in cards
- ✅ **Rich formatting**: Images, buttons, layout
- ✅ **Integrated**: Works in Teams/Outlook
- ✅ **Actionable**: Users can act directly

### Use Cases

- Daily digest cards in Teams channels
- Personal recommendations via bot
- Outlook calendar invites
- Mobile-friendly notifications

## Pattern 5: Daily Rotation

**Use case:** Automatically generate and send recommendations daily.

### Workflow

```text
1. Schedule cron job or systemd timer
2. Run recommendations for multiple profiles
3. Export itineraries
4. Send via email or Teams
5. Rotate telemetry logs
```

### Implementation

**Step 1: Create rotation script**

```bash
#!/bin/bash
# scripts/daily_rotation.sh

# Run recommendations for each team profile
for profile in product_mgmt research_focus engineering; do
    python agent.py export \
        --profile-load $profile \
        --top 5 \
        --output /tmp/${profile}_itinerary.md
    
    # Send via email
    cat /tmp/${profile}_itinerary.md | \
        mail -s "Daily Event Recommendations" ${profile}@example.com
done

# Rotate telemetry if >50MB
if [ $(stat -f%z telemetry.jsonl) -gt 52428800 ]; then
    mv telemetry.jsonl telemetry.$(date +%Y%m%d).jsonl
    touch telemetry.jsonl
fi
```

**Step 2: Schedule with cron**

```cron
# Run daily at 8am
0 8 * * * /path/to/daily_rotation.sh
```

**Or systemd timer:**

```ini
# /etc/systemd/system/event-agent-rotation.timer
[Unit]
Description=Daily Event Agent Rotation

[Timer]
OnCalendar=daily
OnCalendar=08:00
Persistent=true

[Install]
WantedBy=timers.target
```

**Step 3: Enable timer**

```bash
sudo systemctl enable event-agent-rotation.timer
sudo systemctl start event-agent-rotation.timer
```

### Benefits

- ✅ **Automated**: No manual intervention
- ✅ **Scalable**: Multiple profiles supported
- ✅ **Reliable**: systemd handles failures
- ✅ **Maintainable**: Telemetry rotation prevents disk fill

### Use Cases

- Daily conference briefings
- Weekly schedule planning
- Monthly summary reports
- Automated event digests

## Pattern 6: Batch Evaluation

**Use case:** Evaluate recommendation quality across multiple scenarios.

### Workflow

```text
1. Define test profiles with expected results
2. Run recommendations for each profile
3. Measure relevance, diversity, conflicts
4. Adjust weights based on results
5. Re-evaluate until targets met
```

### Implementation

**Step 1: Create test profiles**

```json
// test_profiles.json
[
    {
        "name": "ai_researcher",
        "interests": ["ai", "ml", "research"],
        "expected_tags": ["ai", "ml", "research", "papers"],
        "min_relevance": 0.8,
        "min_diversity": 0.6
    },
    {
        "name": "product_manager",
        "interests": ["product", "strategy", "roadmap"],
        "expected_tags": ["product", "pm", "strategy"],
        "min_relevance": 0.75,
        "min_diversity": 0.5
    }
]
```

**Step 2: Run batch evaluation**

```python
# scripts/evaluate_profiles.py
import json
from agent import recommend, load_manifest

manifest = load_manifest()
profiles = json.load(open("test_profiles.json"))

for profile in profiles:
    result = recommend(manifest, profile["interests"], 5)
    
    # Measure relevance
    matched = sum(1 for s in result["sessions"] 
                  if any(t in profile["expected_tags"] 
                         for t in s["tags"]))
    relevance = matched / len(result["sessions"])
    
    # Measure diversity
    all_tags = set()
    for s in result["sessions"]:
        all_tags.update(s["tags"])
    diversity = len(all_tags) / len(profile["interests"])
    
    # Check thresholds
    print(f"{profile['name']}: relevance={relevance:.2f}, diversity={diversity:.2f}")
    assert relevance >= profile["min_relevance"]
    assert diversity >= profile["min_diversity"]
```

**Step 3: Run evaluation**

```bash
python scripts/evaluate_profiles.py
```

**Output:**

```text
ai_researcher: relevance=0.85, diversity=0.67
product_manager: relevance=0.78, diversity=0.55
```

### Benefits

- ✅ **Quantitative**: Measure quality objectively
- ✅ **Repeatable**: Same tests after changes
- ✅ **Data-driven**: Guide weight tuning
- ✅ **Regression testing**: Catch quality drops

### Use Cases

- Pre-deployment validation
- A/B testing weight configurations
- SLA enforcement (quality thresholds)
- Continuous integration testing

## Pattern 7: Graph API with Fallback

**Use case:** Use Microsoft Graph for live data, fall back to manifest if Graph unavailable.

### Workflow

```text
1. Try to fetch from Graph API
2. If fails, fall back to manifest
3. Log fallback event to telemetry
4. Return recommendations with source indicator
```

### Implementation

```python
from agent import recommend, load_manifest
from core import recommend_from_graph
from graph_auth import GraphAuthClient, GraphAuthError
from graph_service import GraphEventService, GraphServiceError
from settings import Settings

def recommend_with_fallback(interests, top):
    manifest = load_manifest()
    
    try:
        # Try Graph API first
        settings = Settings()
        auth = GraphAuthClient(
            settings.TENANT_ID,
            settings.CLIENT_ID,
            settings.CLIENT_SECRET
        )
        service = GraphEventService(auth, settings.DEFAULT_USER_ID)
        
        result = recommend_from_graph(service, interests, top)
        result["source"] = "graph"
        return result
        
    except (GraphAuthError, GraphServiceError) as e:
        # Fall back to manifest
        print(f"Graph API failed: {e}, using manifest")
        result = recommend(manifest, interests, top)
        result["source"] = "manifest"
        return result
```

### Benefits

- ✅ **Resilient**: Works even if Graph down
- ✅ **Graceful**: No user impact on fallback
- ✅ **Transparent**: Source indicated in response
- ✅ **Observable**: Fallback events in telemetry

### Use Cases

- Production deployments with HA requirements
- Testing Graph integration incrementally
- Hybrid environments (some users on Graph, others not)
- Disaster recovery scenarios

## Best Practices

### Profile Management

- ✅ **Version control profiles** for team-wide consistency
- ✅ **Use descriptive profile names** (e.g., `ml_research_focus`, not `profile1`)
- ✅ **Review profiles monthly** to keep interests current
- ✅ **Share profiles** across teams for common roles

### External Data Integration

- ✅ **Validate external schema** before enabling
- ✅ **Test with small dataset first** (10-50 sessions)
- ✅ **Monitor file size** and rotate if >10MB
- ✅ **Use atomic writes** (write to temp, then rename)

### Governance

- ✅ **Review exports before distribution** for PII/sensitive data
- ✅ **Track telemetry summaries** for audit trails
- ✅ **Set up alerting** for error rate spikes
- ✅ **Rotate logs daily** in production

### Adaptive Cards

- ✅ **Keep cards concise** (max 5 sessions per card)
- ✅ **Include action buttons** for user engagement
- ✅ **Test on mobile** (Teams mobile client)
- ✅ **Use fallback text** for clients without card support

### Automation

- ✅ **Use systemd timers** instead of cron for reliability
- ✅ **Log rotation script output** for debugging
- ✅ **Set up monitoring** for job failures
- ✅ **Test rotation script manually** before scheduling

## Next Steps

- 🏗️ [System Design](design.md) — Architecture overview
- 📖 [Module Reference](modules.md) — Code reference
- 🎯 [Scoring Algorithm](scoring-algorithm.md) — Deep dive
- 📊 [Performance Guide](../05-PRODUCTION/performance.md) — Optimization tips
