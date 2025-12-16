# CLI Usage Guide

Event Kit provides a command-line interface for recommendations, explanations, and exports.

## Basic Commands

All commands start with `python agent.py [command] [options]`

### Recommend Sessions

Get personalized session recommendations based on interests:

```bash
# Basic recommendation
python agent.py recommend --interests "agents, ai safety" --top 3

# Shorter syntax
python agent.py recommend -i "agents" -t 3

# Multiple interests
python agent.py recommend --interests "ai, machine learning, privacy" --top 5

# Save to profile
python agent.py recommend --interests "agents" --profile-save myprofile

# Load from profile
python agent.py recommend --profile-load myprofile --top 5
```

**Options:**
- `--interests` (required): Comma-separated interests or topics
- `-i`: Shorthand for `--interests`
- `--top` (optional, default=3): Number of recommendations
- `-t`: Shorthand for `--top`
- `--profile-save`: Save these interests to a profile
- `--profile-load`: Load interests from a saved profile

### Explain a Session

Get scoring details for why a session was recommended:

```bash
# Explain a session
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"

# Why was this session scored highly?
python agent.py explain --session "Session Title" --interests "topic1, topic2"
```

**Options:**
- `--session` (required): Session title to explain
- `-s`: Shorthand
- `--interests` (required): Your interests
- `-i`: Shorthand

### Export Itinerary

Export recommended sessions as a Markdown document:

```bash
# Export to file
python agent.py export --interests "agents, privacy" --output my_itinerary.md

# Export to console
python agent.py export --interests "agents, privacy"

# Export with top 5
python agent.py export --interests "agents" --top 5 --output itinerary.md
```

**Options:**
- `--interests` (required): Comma-separated interests
- `--output` (optional): Output filename (default: prints to console)
- `--top` (optional, default=3): Number of sessions to export

## Server Mode (HTTP API)

Start the HTTP server for REST API calls:

```bash
# Start server on port 8080
python agent.py serve --port 8080

# Start with Adaptive Cards enabled
python agent.py serve --port 8080 --card

# Start on custom port
python agent.py serve --port 8000
```

**Options:**
- `--port`: Port to listen on (default: 8080)
- `--card`: Enable Adaptive Card output format

Once running, test endpoints:

```bash
# Health check
curl http://localhost:8080/health

# Get recommendations
curl "http://localhost:8080/recommend?interests=agents,ai&top=3"

# Explain a session
curl "http://localhost:8080/explain?session=Generative+Agents+in+Production&interests=agents"

# Export itinerary
curl "http://localhost:8080/export?interests=agents,privacy"
```

See [HTTP API Guide](http-api.md) for detailed endpoint documentation.

## Graph API Mode

Use your Microsoft 365 calendar for recommendations:

### Setup (One-Time)

```bash
# Set credentials in .env file
# See: ../03-GRAPH-API/setup.md

# Verify setup
python -c "from settings import Settings; print(Settings().validate_graph_ready())"
```

### Use Graph Mode

```bash
# Recommend based on your calendar events
python agent.py recommend --source graph --interests "agents" --top 3 --user-id user@company.com

# Shorter syntax
python agent.py recommend --source graph -i "agents" -t 3 --user-id user@company.com

# Or set GRAPH_USER_ID in .env, then omit --user-id
python agent.py recommend --source graph --interests "agents" --top 3
```

**Options:**
- `--source graph`: Use Microsoft Graph API instead of manifest
- `-s graph`: Shorthand
- `--user-id`: User's email address
- `-u`: Shorthand
- `--interests` (required): Your interests
- `--top` (optional): Number of recommendations

### Explain with Graph

```bash
# Explain why a session was recommended based on calendar
python agent.py explain --source graph --session "Meeting Title" --interests "agents" --user-id user@company.com
```

### Export with Graph

```bash
# Export calendar-based recommendations
python agent.py export --source graph --interests "agents" --output calendar_itinerary.md --user-id user@company.com
```

## Profile Management

Profiles save your interests for quick reuse:

### Save a Profile

```bash
# Save current interests
python agent.py recommend --interests "agents, ai, machine learning" --profile-save myprofile

# Now you can quickly reuse these interests:
python agent.py recommend --profile-load myprofile --top 5
```

### List Profiles

Profiles are stored in `~/.event_agent_profiles.json`:

```bash
# View all profiles
cat ~/.event_agent_profiles.json

# Example output:
# {
#   "myprofile": {
#     "interests": ["agents", "ai", "machine learning"],
#     "created": "2024-01-15T10:30:00"
#   }
# }
```

### Delete a Profile

Edit `~/.event_agent_profiles.json` and remove the profile entry.

## Command Reference

### All Options

| Command | Option | Shorthand | Required | Default |
|---------|--------|-----------|----------|---------|
| recommend | `--interests` | `-i` | ✓ | — |
| recommend | `--top` | `-t` | ✗ | 3 |
| recommend | `--source` | `-s` | ✗ | manifest |
| recommend | `--user-id` | `-u` | ✗ (✓ for graph) | — |
| recommend | `--profile-save` | — | ✗ | — |
| recommend | `--profile-load` | — | ✗ | — |
| explain | `--session` | `-s` | ✓ | — |
| explain | `--interests` | `-i` | ✓ | — |
| explain | `--source` | — | ✗ | manifest |
| explain | `--user-id` | `-u` | ✗ (✓ for graph) | — |
| export | `--interests` | `-i` | ✓ | — |
| export | `--output` | `-o` | ✗ | console |
| export | `--top` | `-t` | ✗ | 3 |
| export | `--source` | `-s` | ✗ | manifest |
| export | `--user-id` | `-u` | ✗ (✓ for graph) | — |
| serve | `--port` | `-p` | ✗ | 8080 |
| serve | `--card` | `-c` | ✗ | false |

## Error Messages

### "error: the following arguments are required: --interests"
Missing required argument. Add `--interests`:
```bash
python agent.py recommend --interests "your interests"
```

### "Session not found"
Session title doesn't exist. Check `agent.json` for valid sessions:
```bash
# View available sessions
grep '"title"' agent.json
```

### "Graph not initialized"
Graph credentials not set. See [Graph API Setup](../03-GRAPH-API/setup.md) or:
```bash
# Check if configured
python -c "from settings import Settings; print(Settings().validate_graph_ready())"
```

### "Port already in use"
Another service is using that port. Try a different one:
```bash
python agent.py serve --port 8081
```

## Examples

### Example 1: Get Agent-Related Recommendations

```bash
python agent.py recommend --interests "agents, copilot, automation" --top 5
```

### Example 2: Explain a Recommendation

```bash
python agent.py explain --session "Building Agentic Systems" --interests "agents, ai"
```

### Example 3: Export for Meeting Prep

```bash
python agent.py export --interests "generative ai, enterprise" --output meeting_prep.md
```

### Example 4: Use Your Calendar

```bash
python agent.py recommend --source graph --interests "agents" --top 5 --user-id john@company.com
```

### Example 5: Save and Reuse Profile

```bash
# First time
python agent.py recommend --interests "ai safety, alignment, ethics" --profile-save safety-team

# Later, reuse
python agent.py recommend --profile-load safety-team --top 10
```

## Next Steps

- 📡 Want to use HTTP API? See [HTTP API Guide](http-api.md)
- 📅 Want to use your calendar? See [Graph API Setup](../03-GRAPH-API/setup.md)
- 🔧 Need more options? See [Command Reference](../REFERENCE.md)
- 🆘 Troubleshooting? See [Troubleshooting Guide](../03-GRAPH-API/troubleshooting.md)
