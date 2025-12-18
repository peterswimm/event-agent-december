# Event Kit Quick Start Guide

> **AI-powered event recommendation agent** with CLI, HTTP API, Teams Bot, and Copilot Studio integration

## 🚀 Installation

```bash
# Clone the repo
cd event-agent-example

# Install dependencies
pip install -r requirements.txt

# Verify installation
python agent.py recommend --interests "agents" --top 3
```

✅ **147 tests passing** | 📚 **Complete documentation** | 🐳 **Docker ready**

---

## 🎯 Quick Start: Choose Your Mode

### 1️⃣ CLI Mode (Instant Testing)

**Best for**: Quick testing, scripting, automation

```bash
# Get recommendations
python agent.py recommend --interests "agents, ai safety" --top 3

# Explain a session match
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"

# Export itinerary to Markdown
python agent.py export --interests "agents, privacy" --output my_itinerary.md

# Save/load profiles
python agent.py recommend --interests "agents" --profile-save demo
python agent.py recommend --profile-load demo --top 5
```

### 2️⃣ HTTP API Server

**Best for**: REST API testing, integration, web apps

```bash
# Start server (port 8010 by default)
python agent.py serve --port 8010 --card

# Test endpoints
curl http://localhost:8010/health
curl "http://localhost:8010/recommend?interests=agents,ai+safety&top=3&card=1"
curl "http://localhost:8010/explain?session=Generative+Agents+in+Production&interests=agents"
curl "http://localhost:8010/export?interests=agents"
```

**Available endpoints**:
- `GET /health` - Health check
- `GET /recommend` - Get recommendations
- `GET /recommend-graph` - Calendar-based recommendations (requires Graph credentials)
- `GET /explain` - Explain session match
- `GET /export` - Export itinerary

### 3️⃣ Bot Framework Emulator

**Best for**: Conversation testing, adaptive cards, bot development

**Setup**:
1. Download [Bot Framework Emulator v4.14.1+](https://github.com/microsoft/BotFramework-Emulator/releases)
2. Start the bot server:
   ```bash
   python bot_server.py
   ```
3. Open Bot Framework Emulator
4. Connect to: `http://localhost:3978/api/messages`

**Test commands**:
```
@bot recommend agents, ai safety --top 5
@bot explain "Session Title" --interests agents
@bot export agents --profile my_profile
@bot help
```

📖 **Full guide**: [LOCAL_TESTING.md](LOCAL_TESTING.md#3-bot-framework-emulator)

### 4️⃣ Microsoft Teams Bot

**Best for**: Real Teams integration, production testing

**Setup** (requires ngrok + Azure Bot registration):
1. Install ngrok: `choco install ngrok` (Windows) or [download](https://ngrok.com/download)
2. Start bot server: `python bot_server.py`
3. Start ngrok tunnel: `ngrok http 3978`
4. Update Teams manifest with ngrok URL
5. Upload to Teams: **Apps → Manage your apps → Upload an app**

**In Teams**:
```
@EventKit recommend agents, ai safety --top 5
@EventKit explain "Session Title" --interests agents
@EventKit help
```

📖 **Full guide**: [docs/agents-sdk-setup.md](docs/agents-sdk-setup.md)

### 5️⃣ Docker Container

**Best for**: Production-like testing, deployment validation

```bash
# Build image
docker build -t eventkit:latest -f deploy/Dockerfile .

# Run container
docker run -d -p 8010:8010 --name eventkit eventkit:latest

# Test
curl http://localhost:8010/health
curl "http://localhost:8010/recommend?interests=agents&top=3"

# View logs
docker logs eventkit

# Stop
docker stop eventkit
```

**With Docker Compose**:
```bash
cd deploy
docker compose up -d
docker compose logs -f
```

📖 **Full guide**: [LOCAL_TESTING.md](LOCAL_TESTING.md#5-docker-local)

---

## 🔧 Microsoft Graph Integration (Optional)

**Best for**: Calendar-based recommendations, real user data

**One-time setup** (5 minutes):
```bash
# Set Graph credentials
export GRAPH_TENANT_ID=your-tenant-id
export GRAPH_CLIENT_ID=your-client-id
export GRAPH_CLIENT_SECRET=your-client-secret

# Verify
python -c "from settings import Settings; print('Ready:', Settings().validate_graph_ready())"
```

**Usage**:
```bash
# CLI
python agent.py recommend --source graph --interests "ai safety" --top 3 --user-id user@company.com

# HTTP API
curl "http://localhost:8010/recommend-graph?interests=ai+safety&top=3&userId=user@company.com"
```

📖 **Full setup**: [docs/03-GRAPH-API/graph-setup.md](docs/03-GRAPH-API/graph-setup.md)

---

## 🧪 Testing Environments Comparison

| Environment | Setup Time | Use Case | Authentication | Adaptive Cards |
|-------------|------------|----------|----------------|----------------|
| **CLI** | 0 min | Quick testing | ❌ | ❌ |
| **HTTP API** | 0 min | REST testing | ❌ | ✅ |
| **Bot Emulator** | 5 min | Conversation testing | ❌ | ✅ |
| **Teams (ngrok)** | 15 min | Teams integration | ✅ | ✅ |
| **Docker** | 5 min | Production-like | ❌ | ✅ |
| **Copilot Studio** | 30 min | Copilot testing | ✅ | ✅ |
| **Azure Production** | 60 min | Live deployment | ✅ | ✅ |

📖 **Complete testing guide**: [LOCAL_TESTING.md](LOCAL_TESTING.md)

---

## 📚 Documentation Hub

### Getting Started
- **[README.md](README.md)** - Main documentation
- **[QUICKSTART.md](QUICKSTART.md)** (this file) - Quick start guide
- **[LOCAL_TESTING.md](LOCAL_TESTING.md)** - Multi-channel testing guide

### Integration Guides
- **[docs/agents-sdk-setup.md](docs/agents-sdk-setup.md)** - Teams/Copilot integration (650+ lines)
- **[docs/deployment-guide.md](docs/deployment-guide.md)** - Production deployment (500+ lines)
- **[TEAMS_QUICK_REFERENCE.md](TEAMS_QUICK_REFERENCE.md)** - Bot commands reference

### Development
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Developer guide
- **[docs/api-guide.md](docs/api-guide.md)** - API reference (100+ examples)
- **[docs/technical-guide.md](docs/technical-guide.md)** - Architecture deep dive

### Project Status
- **[PHASE3_COMPLETION.md](PHASE3_COMPLETION.md)** - Implementation status
- **[ROADMAP.md](ROADMAP.md)** - Roadmap & progress tracking

---

## 🎨 Manifest Editing

**No code changes required** - edit `agent.json` to:
- Add/remove sessions
- Adjust scoring weights
- Configure features (telemetry, export, external data)

```json
{
  "weights": {
    "interest_match": 0.40,
    "relevance": 0.25,
    "speaker_quality": 0.20,
    "novelty": 0.15
  },
  "features": {
    "telemetry": true,
    "export": true,
    "externalSessions": false
  }
}
```

After editing, rerun any command - changes take effect immediately.

---

## 🧪 Run Tests

```bash
# All tests (147 passing)
python -m pytest tests -v

# Specific test file
python -m pytest tests/test_agents_sdk.py -v

# With coverage
python -m pytest tests --cov=. --cov-report=html
```

---

## 🐳 systemd Service (Optional)

```ini
[Unit]
Description=Event Kit Agent
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/event-agent-example
ExecStart=/usr/bin/python3 agent.py serve --port 8010 --card
Restart=on-failure
Environment="GRAPH_TENANT_ID=your-tenant-id"
Environment="GRAPH_CLIENT_ID=your-client-id"
Environment="GRAPH_CLIENT_SECRET=your-client-secret"

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable --now eventkit.service
sudo systemctl status eventkit
```

---

## 🚀 Next Steps

1. **Test locally**: Choose your preferred testing environment above
2. **Configure Graph**: [docs/03-GRAPH-API/graph-setup.md](docs/03-GRAPH-API/graph-setup.md)
3. **Deploy to Teams**: [docs/agents-sdk-setup.md](docs/agents-sdk-setup.md)
4. **Deploy to Azure**: [docs/deployment-guide.md](docs/deployment-guide.md)
5. **Customize scoring**: Edit `agent.json` weights

---

## 💡 Tips

- **Profile persistence**: Saved at `~/.event_agent_profiles.json`
- **External sessions**: Drop `sessions_external.json` and enable feature in `agent.json`
- **Telemetry**: Check `telemetry.jsonl` for request logs
- **Adaptive Cards**: Add `?card=1` to HTTP endpoints or use `--card` flag
- **Docker logs**: `docker logs eventkit` or `docker compose logs -f`

---

## 🆘 Troubleshooting

### Bot server won't start
```bash
# Check if port 3978 is in use
netstat -ano | findstr :3978  # Windows
lsof -i :3978                 # macOS/Linux

# Use different port
python bot_server.py --port 3979
```

### Graph authentication fails
```bash
# Verify credentials
python -c "from settings import Settings; s=Settings(); print('Tenant:', s.graph_tenant_id); print('Ready:', s.validate_graph_ready())"

# Check Azure AD app permissions
# Required: Calendars.Read, User.Read
```

### Tests failing
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run specific test
python -m pytest tests/test_agents_sdk.py::test_adapter_recommend -v
```

**More help**: [docs/troubleshooting.md](docs/troubleshooting.md)

---

**Need help?** Check [docs/troubleshooting.md](docs/troubleshooting.md) or [PHASE3_INDEX.md](PHASE3_INDEX.md)
