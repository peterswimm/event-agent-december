# Installation & Setup

Complete setup guide for Event Kit, including dependencies and optional Graph API configuration.

## System Requirements

- **Python**: 3.8 or later (tested on 3.10+)
- **OS**: Windows, macOS, or Linux
- **Disk**: ~50 MB for dependencies
- **Network**: Required for Graph API mode

## Step 1: Clone the Repository

```bash
git clone https://github.com/microsoft/Microsoft-365-samples.git
cd Microsoft-365-samples/samples/event-agent-example
```

Or if already cloned:
```bash
cd event-agent-example
```

## Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Step 3: Install Dependencies

### Basic Setup (Manifest Mode Only)

```bash
pip install -r requirements.txt
```

**What this installs:**
- `pydantic` — Data validation & configuration
- `pydantic-settings` — Environment variable management
- `pytest` — Testing framework
- `requests` — HTTP client (for API calls)
- `python-dotenv` — .env file support

### Full Setup (Manifest + Graph API)

For Microsoft Graph integration, install additional dependencies:

```bash
pip install -r requirements.txt
# Plus these for Graph:
pip install msal msgraph-core azure-identity
```

**Additional packages:**
- `msal` — Microsoft authentication library (MSAL)
- `msgraph-core` — Microsoft Graph API client
- `azure-identity` — Azure authentication

Or install all at once:
```bash
pip install -r requirements.txt msal msgraph-core azure-identity
```

## Step 4: Verify Installation

### Test Basic Installation

```bash
python agent.py recommend --interests "agents" --top 2
```

If this works, basic setup is complete ✅

### Test Graph Installation (Optional)

```bash
python -c "
from settings import Settings
s = Settings()
print('Graph ready:', s.validate_graph_ready())
"
```

If this prints `Graph ready: False`, that's normal — Graph needs credentials (see [Configuration](configuration.md)).

## Optional: Docker Setup

If you prefer containerized setup:

```bash
# Build image
docker build -f deploy/Dockerfile -t event-kit .

# Run container
docker run -p 8080:8080 event-kit python agent.py serve --port 8080
```

See [Deployment Guide](../05-PRODUCTION/deployment.md) for more Docker options.

## Optional: systemd Service (Linux)

To run Event Kit as a system service:

1. Create service file at `/etc/systemd/system/eventkit.service`:

```ini
[Unit]
Description=Event Kit Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/event-kit
ExecStart=/usr/bin/python3 agent.py serve --port 8080 --card
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

2. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable eventkit.service
sudo systemctl start eventkit.service
sudo systemctl status eventkit.service
```

## Next Steps

- ✅ **Installation complete!**
- 📖 See [Configuration Guide](configuration.md) for environment setup
- 🚀 Jump to [Quick Start](quick-start.md) to run it
- 📚 Read [CLI Usage](../02-USER-GUIDES/cli-usage.md) for commands
- 📅 Read [Graph API Setup](../03-GRAPH-API/setup.md) for calendar integration

## Troubleshooting

**"pip: command not found"**
- Python not installed. Download from [python.org](https://www.python.org/downloads/)

**"ModuleNotFoundError: No module named 'pydantic'"**
- Run `pip install -r requirements.txt`

**"Permission denied" on Linux/macOS**
- Try `python3 agent.py` instead of `python agent.py`

**Virtual environment not activating**
- Windows: Try `venv\Scripts\activate.bat` (for CMD) or `venv\Scripts\Activate.ps1` (for PowerShell)
- macOS/Linux: Try `source venv/bin/activate`

For more help, see [Troubleshooting Guide](../03-GRAPH-API/troubleshooting.md).
