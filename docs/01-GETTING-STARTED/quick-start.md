# Quick Start — Get Running in 5 Minutes

Event Kit is a **minimal declarative agent** that works with sample data out of the box. No setup required.

## Option 1: Manifest Mode (Sample Data)

Event Kit comes with sample sessions. Get recommendations immediately:

```bash
# Clone or navigate to the repo
cd event-agent-example

# Install dependencies (if not already done)
pip install -r requirements.txt

# Run a recommendation
python agent.py recommend --interests "agents, ai safety" --top 3

# Explain a session
python agent.py explain --session "Generative Agents in Production" --interests "agents, gen ai"

# Export an itinerary
python agent.py export --interests "agents, ai safety"
```

**That's it!** You're using Event Kit.

---

## Option 2: Start the HTTP Server

Want to use the API instead of CLI? Start the server:

```bash
# Start server on port 8080
python agent.py serve --port 8080

# In another terminal, try the API:
curl "http://localhost:8080/recommend?interests=agents,ai+safety&top=3"
curl "http://localhost:8080/health"
```

---

## Option 3: Use Your Own Calendar (Graph API)

Want to use your actual calendar events instead of samples? See [Graph API Setup](../03-GRAPH-API/setup.md) for a 10-minute setup guide.

---

## 📁 What You'll See

```text
event-agent-example/
├── agent.json              ← Session definitions & weights
├── agent.py                ← Main agent logic
├── README.md               ← Full documentation
├── GRAPH_QUICK_REFERENCE.md ← Graph API quick reference
└── docs/                   ← All documentation
```

---

## Next Steps

### I want to

- **Use the CLI** → Read [CLI Usage Guide](../02-USER-GUIDES/cli-usage.md)
- **Use the HTTP API** → Read [HTTP API Guide](../02-USER-GUIDES/http-api.md)
- **Use my calendar** → Read [Graph API Setup](../03-GRAPH-API/setup.md)
- **Understand how it works** → Read [Architecture Guide](../04-ARCHITECTURE/design.md)
- **Deploy to production** → Read [Deployment Guide](../05-PRODUCTION/deployment.md)
- **See all commands** → Read [Command Reference](../REFERENCE.md)

---

## Troubleshooting

**"Module not found" error?**
```bash
pip install -r requirements.txt
```

**"No such file or directory"?**
Make sure you're in the `event-agent-example` directory.

**Still stuck?**
See [Troubleshooting Guide](../03-GRAPH-API/troubleshooting.md) or [FAQ](../03-GRAPH-API/troubleshooting.md#faq).

---

✅ **Congrats!** You're ready to use Event Kit. Next, explore [Installation & Setup](installation.md) for configuration options or jump to [User Guides](../02-USER-GUIDES/) to learn more.
