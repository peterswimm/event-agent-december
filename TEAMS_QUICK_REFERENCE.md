# Event Kit Agent - Teams Integration Quick Reference

**Updated**: December 18, 2025

---

## 🚀 Fast Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Local Bot Server
```bash
python bot_server.py
```
Server starts on `http://localhost:3978`

### 3. Test with Bot Emulator
- Download [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator/releases)
- Open Bot Emulator
- Connect to `http://localhost:3978/api/messages`
- Type: `@bot recommend agents`

---

## 📝 Command Reference

| Command | Format | Example |
|---------|--------|---------|
| Recommend | `@bot recommend <interests> --top <n>` | `@bot recommend agents, ai safety --top 5` |
| Explain | `@bot explain "<title>" --interests <list>` | `@bot explain "Generative Agents" --interests agents` |
| Export | `@bot export <interests> --profile <name>` | `@bot export agents --profile my_profile` |
| Help | `@bot help` | `@bot help` |

---

## 📂 Key Files

### Manifests
- `agent-declaration.json` - Agent capabilities (Agents SDK)
- `teams-app.json` - Teams bot configuration
- `copilot-plugin.json` - Copilot Studio plugin

### Code
- `agents_sdk_adapter.py` - Agents SDK adapter (539 lines)
- `bot_handler.py` - Teams message handler (539 lines)
- `bot_server.py` - aiohttp server (223 lines)

### Documentation
- `docs/agents-sdk-setup.md` - Complete setup guide
- `docs/deployment-guide.md` - Production deployment
- `PHASE3_COMPLETION.md` - What was built

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Bot Configuration
BOT_ID=your-bot-app-id
BOT_PASSWORD=your-bot-password
BOT_ENDPOINT=https://your-domain.azurewebsites.net/api/messages

# Graph API (optional)
GRAPH_TENANT_ID=your-tenant-id
GRAPH_CLIENT_ID=your-client-id
GRAPH_CLIENT_SECRET=your-client-secret

# Application Insights
APP_INSIGHTS_CONNECTION_STRING=your-connection-string
```

---

## 🧪 Testing Scenarios

### Scenario 1: Basic Recommendation
```
User: @bot recommend agents, machine learning
Bot: [Returns 5 recommended sessions with scoring]
```

### Scenario 2: Explanation
```
User: @bot explain "Generative Agents in Production" --interests agents, ai
Bot: [Explains why this session matches, shows matched keywords and score]
```

### Scenario 3: Export Profile
```
User: @bot export agents, ai safety --profile tech_days_2025
Bot: [Exports itinerary as markdown, saves profile for future use]
```

### Scenario 4: Natural Language
```
User: I want sessions about agents and machine learning
Bot: [Detects intent, extracts keywords, returns recommendations]
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot not responding | Check `python bot_server.py` is running |
| "Unknown command" | Use exact format: `@bot <command> <args>` |
| Graph recommendations fail | Verify Graph credentials in `.env` |
| Timeout errors | Reduce `--top` parameter or check manifest size |

See `docs/troubleshooting.md` for detailed solutions.

---

## 📦 Deployment Checklist

- [ ] Environment variables configured
- [ ] Local testing passed
- [ ] Docker image built
- [ ] Infrastructure deployed (Bicep)
- [ ] Bot Service registered in Azure
- [ ] Teams manifest uploaded
- [ ] Health endpoint responds
- [ ] Bot responds in Teams
- [ ] Logs appear in Application Insights

---

## 🔗 Useful Links

- **Bot Framework Docs**: https://docs.microsoft.com/en-us/azure/bot-service/
- **Teams Development**: https://docs.microsoft.com/en-us/microsoftteams/platform/
- **Copilot Studio**: https://copilotstudio.microsoft.com
- **Azure CLI Reference**: https://docs.microsoft.com/en-us/cli/azure/

---

## 💡 Tips & Tricks

### Get Agent Capabilities Programmatically
```python
from agents_sdk_adapter import EventKitAgent
agent = EventKitAgent()
capabilities = agent.get_capabilities()
for cap in capabilities:
    print(f"{cap['name']}: {cap['description']}")
```

### Test Tool Call Locally
```python
from agents_sdk_adapter import EventKitAgent
agent = EventKitAgent()
result = agent.handle_tool_call("recommend_sessions", {
    "interests": "agents, ai safety",
    "top": 3,
    "correlation_id": "test-123"
})
print(result["markdown"])
```

### Parse Custom Commands
```python
from bot_handler import EventKitBotHandler
handler = EventKitBotHandler()
command, params = handler._parse_message("recommend agents --top 5")
print(f"Command: {command}")
print(f"Params: {params}")
```

---

## ✅ Success Indicators

You'll know it's working when:
- ✅ Bot responds to `@bot help` in Teams
- ✅ Recommendations return in <2 seconds
- ✅ Adaptive cards display properly
- ✅ Profiles save successfully
- ✅ Logs appear in Application Insights

---

## 📞 Getting Help

1. Check `docs/troubleshooting.md`
2. Review `docs/agents-sdk-setup.md` for detailed setup
3. Check Application Insights logs
4. Create GitHub issue with:
   - Command tried
   - Error message
   - Environment (local/Azure)
   - Log snippet

---

**Version**: 1.0.0  
**Status**: Production Ready ✅
