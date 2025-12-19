# Knowledge Agent → Microsoft 365 SDK Agent
## Expansion Roadmap & Architecture

**Status**: Expansion Plan
**Date**: December 18, 2025
**Goal**: Integrate Knowledge Agent with Microsoft 365 services via Graph SDK

---

## 🎯 Vision

Expand the current Knowledge Agent POC into a Microsoft 365-integrated agent that can:
- Extract knowledge from SharePoint documents
- Process Teams meeting transcripts and recordings
- Analyze files from OneDrive/SharePoint libraries
- Create structured knowledge artifacts from enterprise content
- Store extraction results back to Microsoft 365

---

## 🏗️ Current Architecture → Microsoft 365 Architecture

### Current State (Knowledge Agent POC)
```
User Input (local files)
    ↓
Knowledge Agent (paper/talk/repo)
    ↓
LLM Extraction
    ↓
JSON + Markdown Output (local files)
```

### Target State (Microsoft 365 Agent)
```
Microsoft 365 Content
    ↓
Microsoft Graph API ← [EXISTING: graph_auth.py, graph_service.py]
    ↓
Knowledge Agent (paper/talk/repo) ← [EXISTING: agents/]
    ↓
LLM Extraction
    ↓
Microsoft 365 Storage + Local Output
    ↓
SharePoint/Teams/OneDrive
```

---

## 🔗 Integration Architecture

### Phase 1: Microsoft Graph Integration (Foundation)

**Leverage Existing Infrastructure**:
- ✅ `graph_auth.py` - Already handles Azure AD authentication
- ✅ `graph_service.py` - Already provides Graph API methods
- 🆕 Extend for Knowledge Agent scenarios

**New Components**:
```python
# knowledge-agent-poc/integrations/m365_connector.py
class M365KnowledgeConnector:
    """Connect Knowledge Agent to Microsoft 365"""

    def __init__(self, graph_service):
        self.graph = graph_service

    # Download content from Microsoft 365
    def get_sharepoint_document(self, site_id, file_path)
    def get_onedrive_file(self, file_id)
    def get_teams_meeting_transcript(self, meeting_id)

    # Upload extraction results
    def save_artifact_to_sharepoint(self, artifact, site_id, library)
    def save_artifact_to_onedrive(self, artifact, folder_path)
    def post_summary_to_teams(self, artifact, channel_id)
```

### Phase 2: Microsoft 365 Content Sources

**SharePoint Documents**:
```python
# Extract from SharePoint document library
connector = M365KnowledgeConnector(graph_service)
pdf_content = connector.get_sharepoint_document(
    site_id="contoso.sharepoint.com,abc123",
    file_path="/Research/Papers/transformer.pdf"
)

agent = PaperAgent()
artifact = agent.extract_from_bytes(pdf_content)

# Save back to SharePoint
connector.save_artifact_to_sharepoint(
    artifact,
    site_id="contoso.sharepoint.com,abc123",
    library="Knowledge Artifacts"
)
```

**Teams Meeting Transcripts**:
```python
# Extract from Teams meeting
transcript = connector.get_teams_meeting_transcript(
    meeting_id="19:meeting_abc123@thread.v2"
)

agent = TalkAgent()
artifact = agent.extract_from_text(transcript)

# Post summary to Teams channel
connector.post_summary_to_teams(
    artifact,
    channel_id="19:channel_xyz789@thread.tacv2"
)
```

**OneDrive Files**:
```python
# Extract from OneDrive file
file_content = connector.get_onedrive_file(
    file_id="01ABC123DEF456"
)

agent = RepositoryAgent()  # or PaperAgent depending on type
artifact = agent.extract(file_content)
```

### Phase 3: Agent Extensions

**New Agent Types for Microsoft 365**:

1. **TeamsMeetingAgent** (extends TalkAgent)
   - Extract from Teams meeting transcripts
   - Include speaker identification
   - Link to meeting recordings
   - Extract action items and decisions

2. **SharePointAgent** (generic document agent)
   - Auto-detect document type
   - Route to appropriate extraction agent
   - Handle Office formats (Word, PowerPoint)
   - Preserve Microsoft 365 metadata

3. **CollaborativeRepoAgent** (extends RepositoryAgent)
   - Extract from Azure DevOps repos
   - Extract from GitHub Enterprise (via Microsoft 365)
   - Include team collaboration patterns

---

## 📋 Implementation Phases

### Phase 1: Core Integration (2-3 days)
**Goal**: Connect Knowledge Agent to Microsoft 365 content

**Tasks**:
1. ✅ Review existing `graph_auth.py` and `graph_service.py`
2. Create `M365KnowledgeConnector` class
3. Implement file download from SharePoint/OneDrive
4. Test authentication flow
5. Add Microsoft 365 source tracking to artifacts

**New Files**:
- `knowledge-agent-poc/integrations/__init__.py`
- `knowledge-agent-poc/integrations/m365_connector.py`
- `knowledge-agent-poc/integrations/m365_schemas.py` (Microsoft 365-specific metadata)

**Example**:
```python
# m365_schemas.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class M365SourceMetadata:
    """Microsoft 365 source information"""
    source_type: str  # "sharepoint", "onedrive", "teams"
    site_id: Optional[str]
    drive_id: Optional[str]
    item_id: str
    web_url: str
    last_modified: str
    last_modified_by: str
```

### Phase 2: Bidirectional Integration (3-4 days)
**Goal**: Save extraction results back to Microsoft 365

**Tasks**:
1. Implement artifact upload to SharePoint
2. Create document libraries for knowledge artifacts
3. Add Teams integration for notifications
4. Implement search across extracted artifacts
5. Add compliance/retention policies

**New Features**:
- Automatic artifact storage in SharePoint
- Teams notifications on extraction completion
- SharePoint metadata for artifacts (tags, categories)
- Microsoft 365 search integration

**Example**:
```python
# Upload to SharePoint with metadata
connector.save_artifact_to_sharepoint(
    artifact,
    site_id="contoso.sharepoint.com,abc123",
    library="Knowledge Artifacts",
    metadata={
        "ContentType": "Research Artifact",
        "Department": "AI Research",
        "Confidence": artifact.confidence_score,
        "ExtractionDate": artifact.extraction_date
    }
)
```

### Phase 3: Advanced Scenarios (5-7 days)
**Goal**: Enterprise-grade Microsoft 365 agent

**Tasks**:
1. Batch processing of SharePoint libraries
2. Scheduled extraction jobs
3. Teams bot integration
4. Power Automate connectors
5. Compliance and audit logging
6. Multi-tenant support

**Advanced Features**:
- Bulk extraction from SharePoint sites
- Automated monitoring of document libraries
- Teams bot for conversational extraction
- Power Automate flows triggered by extractions
- Microsoft Purview integration

---

## 🔧 Technical Implementation

### 1. Extend Existing Graph Service

```python
# In graph_service.py - Add Knowledge Agent methods

class GraphService:
    # ... existing methods ...

    async def download_file_content(self, drive_id: str, item_id: str) -> bytes:
        """Download file content from SharePoint/OneDrive"""
        endpoint = f"drives/{drive_id}/items/{item_id}/content"
        return await self._get_binary(endpoint)

    async def upload_file(self, drive_id: str, folder_path: str,
                         filename: str, content: bytes):
        """Upload file to SharePoint/OneDrive"""
        endpoint = f"drives/{drive_id}/root:/{folder_path}/{filename}:/content"
        return await self._put(endpoint, content)

    async def get_meeting_transcript(self, meeting_id: str) -> str:
        """Get Teams meeting transcript"""
        endpoint = f"chats/{meeting_id}/messages"
        messages = await self._get(endpoint)
        # Parse transcript from messages
        return self._parse_transcript(messages)

    async def post_to_channel(self, team_id: str, channel_id: str,
                            message: str):
        """Post message to Teams channel"""
        endpoint = f"teams/{team_id}/channels/{channel_id}/messages"
        return await self._post(endpoint, {"body": {"content": message}})
```

### 2. Create M365 Connector

```python
# knowledge-agent-poc/integrations/m365_connector.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from graph_service import GraphService
from graph_auth import get_authenticated_client
from typing import Optional, Dict, Any
import json

class M365KnowledgeConnector:
    """Connect Knowledge Agent to Microsoft 365 services"""

    def __init__(self, graph_service: Optional[GraphService] = None):
        """Initialize connector with Graph service"""
        self.graph = graph_service or self._get_default_graph_service()

    def _get_default_graph_service(self) -> GraphService:
        """Get default Graph service from existing auth"""
        # Leverage existing graph_auth.py
        from graph_auth import GraphAuth
        auth = GraphAuth()
        client = auth.get_authenticated_client()
        return GraphService(client)

    # SharePoint Operations
    async def get_sharepoint_file(self, site_id: str,
                                 file_path: str) -> bytes:
        """Download file from SharePoint"""
        # Get drive ID for site
        site_drive = await self.graph.get_site_drive(site_id)
        drive_id = site_drive['id']

        # Get item by path
        item = await self.graph.get_item_by_path(drive_id, file_path)
        item_id = item['id']

        # Download content
        return await self.graph.download_file_content(drive_id, item_id)

    async def save_artifact_to_sharepoint(
        self,
        artifact: 'BaseKnowledgeArtifact',
        site_id: str,
        library: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Save knowledge artifact to SharePoint"""
        # Get drive ID
        site_drive = await self.graph.get_site_drive(site_id)
        drive_id = site_drive['id']

        # Prepare files
        json_filename = f"{artifact.title.replace(' ', '_')}.json"
        md_filename = f"{artifact.title.replace(' ', '_')}.md"

        json_content = json.dumps(artifact.__dict__, default=str).encode()
        md_content = self._generate_markdown_summary(artifact).encode()

        # Upload files
        json_result = await self.graph.upload_file(
            drive_id, library, json_filename, json_content
        )
        md_result = await self.graph.upload_file(
            drive_id, library, md_filename, md_content
        )

        # Set metadata if provided
        if metadata:
            await self._set_sharepoint_metadata(
                drive_id, json_result['id'], metadata
            )

        return {
            "json_url": json_result['webUrl'],
            "markdown_url": md_result['webUrl']
        }

    # OneDrive Operations
    async def get_onedrive_file(self, file_id: str) -> bytes:
        """Download file from OneDrive"""
        return await self.graph.download_file_content("me/drive", file_id)

    # Teams Operations
    async def get_teams_meeting_transcript(
        self,
        meeting_id: str
    ) -> str:
        """Get Teams meeting transcript"""
        return await self.graph.get_meeting_transcript(meeting_id)

    async def post_extraction_summary_to_teams(
        self,
        artifact: 'BaseKnowledgeArtifact',
        team_id: str,
        channel_id: str
    ):
        """Post extraction summary to Teams channel"""
        summary = self._format_teams_message(artifact)
        await self.graph.post_to_channel(team_id, channel_id, summary)

    # Helper methods
    def _generate_markdown_summary(
        self,
        artifact: 'BaseKnowledgeArtifact'
    ) -> str:
        """Generate markdown summary for artifact"""
        return f"""# {artifact.title}

**Contributors**: {', '.join(artifact.contributors)}
**Confidence**: {artifact.confidence_score:.0%}
**Extraction Date**: {artifact.extraction_date}

## Overview
{artifact.plain_language_overview}

## Technical Problem
{artifact.technical_problem_addressed}

## Key Methods
{artifact.key_methods_approach}

## Primary Claims
{artifact.primary_claims_capabilities}

## Novelty
{artifact.novelty_vs_prior_work}

## Limitations
{artifact.limitations_constraints}

## Potential Impact
{artifact.potential_impact}
"""

    def _format_teams_message(
        self,
        artifact: 'BaseKnowledgeArtifact'
    ) -> str:
        """Format artifact as Teams message"""
        return f"""
# 🎯 Knowledge Extraction Complete

**Title**: {artifact.title}
**Type**: {artifact.source_type.value}
**Confidence**: {artifact.confidence_score:.0%}

**Overview**: {artifact.plain_language_overview[:200]}...

[View Full Artifact](artifact_link)
"""
```

### 3. Update Knowledge Agent Bot

```python
# In knowledge_agent_bot.py - Add M365 integration

class KnowledgeExtractionAgent:
    def __init__(
        self,
        default_llm_provider: str = "azure-openai",
        output_dir: str = "./outputs",
        enable_m365: bool = False,  # NEW
        graph_service: Optional[Any] = None  # NEW
    ):
        # ... existing init ...

        # Microsoft 365 integration
        self.enable_m365 = enable_m365
        if enable_m365:
            from integrations.m365_connector import M365KnowledgeConnector
            self.m365 = M365KnowledgeConnector(graph_service)
        else:
            self.m365 = None

    async def extract_from_sharepoint(
        self,
        site_id: str,
        file_path: str,
        llm_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract knowledge from SharePoint file"""
        if not self.enable_m365:
            return {"success": False, "error": "Microsoft 365 not enabled"}

        # Download file
        content = await self.m365.get_sharepoint_file(site_id, file_path)

        # Detect type and extract
        if file_path.endswith('.pdf'):
            agent = PaperAgent(llm_provider=llm_provider or self.default_llm_provider)
            artifact = agent.extract_from_bytes(content)
        elif file_path.endswith('.txt'):
            agent = TalkAgent(llm_provider=llm_provider or self.default_llm_provider)
            artifact = agent.extract_from_text(content.decode())
        else:
            return {"success": False, "error": "Unsupported file type"}

        # Save back to SharePoint
        urls = await self.m365.save_artifact_to_sharepoint(
            artifact,
            site_id,
            library="Knowledge Artifacts"
        )

        return {
            "success": True,
            "artifact": artifact,
            "sharepoint_urls": urls
        }
```

---

## 🎬 Usage Examples

### Example 1: Extract from SharePoint
```python
from knowledge_agent_bot import KnowledgeExtractionAgent
from graph_service import GraphService

# Initialize with Microsoft 365 enabled
agent = KnowledgeExtractionAgent(enable_m365=True)

# Extract from SharePoint
result = await agent.extract_from_sharepoint(
    site_id="contoso.sharepoint.com,abc123",
    file_path="/Shared Documents/Research/transformer_paper.pdf"
)

# Artifact automatically saved to SharePoint Knowledge Artifacts library
print(f"Artifact available at: {result['sharepoint_urls']['json_url']}")
```

### Example 2: Batch Process SharePoint Library
```python
# Process all PDFs in a library
library_path = "/Shared Documents/Research Papers"
files = await connector.list_sharepoint_files(site_id, library_path)

for file in files:
    if file['name'].endswith('.pdf'):
        result = await agent.extract_from_sharepoint(
            site_id,
            f"{library_path}/{file['name']}"
        )
        print(f"Extracted: {result['artifact'].title}")
```

### Example 3: Teams Integration
```python
# Extract and notify Teams
result = await agent.extract_from_sharepoint(site_id, file_path)

# Post summary to Teams channel
await connector.post_extraction_summary_to_teams(
    result['artifact'],
    team_id="19:team_abc@thread.tacv2",
    channel_id="19:channel_xyz@thread.tacv2"
)
```

---

## 📊 Microsoft 365 Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Microsoft 365 Services                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │SharePoint│  │ OneDrive │  │  Teams   │  │  Graph   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼────────────┼─────────────┼──────────────┼──────────┘
        │            │             │              │
        └────────────┴─────────────┴──────────────┘
                            │
                    ┌───────▼────────┐
                    │ M365 Connector │ ← NEW
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼────┐      ┌──────▼──────┐      ┌────▼─────┐
    │ Paper  │      │    Talk     │      │Repository│
    │ Agent  │      │   Agent     │      │  Agent   │
    └───┬────┘      └──────┬──────┘      └────┬─────┘
        │                  │                   │
        └──────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  LLM Layer  │
                    │ (Azure/OAI) │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Artifact  │
                    │   Output    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼────┐      ┌─────▼──────┐      ┌───▼────┐
    │ Local  │      │ SharePoint │      │ Teams  │
    │Storage │      │  Library   │      │Message │
    └────────┘      └────────────┘      └────────┘
```

---

## 🔐 Security & Compliance

### Authentication
- Use existing `graph_auth.py` for Azure AD authentication
- Support delegated (user) and application (daemon) permissions
- Implement token caching and refresh

### Permissions Required
```
# Microsoft Graph API Permissions
- Files.Read.All (SharePoint/OneDrive read)
- Files.ReadWrite.All (SharePoint/OneDrive write)
- ChannelMessage.Send (Teams posting)
- OnlineMeetings.Read.All (Teams transcripts)
- Sites.Read.All (SharePoint sites)
```

### Compliance
- Respect Microsoft 365 retention policies
- Honor sensitivity labels
- Implement audit logging
- Support eDiscovery requirements

---

## 📦 New Dependencies

```txt
# Add to requirements.txt
msgraph-core>=1.0.0
azure-identity>=1.15.0
msal>=1.26.0

# Already have:
# - graph_auth.py provides authentication
# - graph_service.py provides Graph API methods
```

---

## 🚀 Deployment Scenarios

### Scenario 1: Enterprise Knowledge Base
- Extract knowledge from all research papers in SharePoint
- Store structured artifacts in dedicated library
- Enable enterprise-wide search across artifacts
- Track research themes and trends

### Scenario 2: Meeting Intelligence
- Process Teams meeting transcripts automatically
- Extract action items and decisions
- Link to related documents
- Generate meeting summaries

### Scenario 3: Repository Documentation
- Analyze code repositories in Azure DevOps
- Extract API documentation
- Generate architecture diagrams
- Track technical debt

---

## 📅 Timeline

### Week 1: Core Integration
- Day 1-2: Review existing Graph infrastructure
- Day 3-4: Build M365 connector
- Day 5: Integration testing

### Week 2: Bidirectional Flow
- Day 1-2: Implement artifact storage
- Day 3-4: Teams integration
- Day 5: End-to-end testing

### Week 3: Advanced Features
- Day 1-2: Batch processing
- Day 3-4: Bot integration
- Day 5: Documentation & deployment

---

## ✅ Success Criteria

- ✅ Extract knowledge from SharePoint documents
- ✅ Save artifacts back to SharePoint
- ✅ Process Teams meeting transcripts
- ✅ Post summaries to Teams channels
- ✅ Handle authentication seamlessly
- ✅ Maintain extraction quality (>85% confidence)
- ✅ Support batch operations
- ✅ Pass security review

---

**Next Steps**:
1. Review existing `graph_auth.py` and `graph_service.py`
2. Create `integrations/m365_connector.py`
3. Test authentication flow
4. Implement file download from SharePoint
5. Test with sample SharePoint documents

**Status**: 🎯 Ready to expand into Microsoft 365 agent
