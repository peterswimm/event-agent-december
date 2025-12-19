# Project Knowledge Agent POC v1

**Status**: Proof of Concept (Local Development Only)
**Branch**: `poc1219`
**Parent Project**: EventKit (kept on `main` branch)

---

## 📋 POC Overview

This is a localized, in-progress development folder for the **Project Knowledge Agent – Knowledge Extraction POC (v1)**.

The goal is to validate foundational building blocks for automatically extracting structured knowledge from three research artifact types:
- **Research papers** (PDF)
- **Research talks/transcripts** (text)
- **Code/model repositories** (URL)

### Core Outputs
- Structured JSON knowledge artifacts
- Human-readable summaries
- Expert review and iteration
- (Stretch) Project-level knowledge compilation

---

## 🏗️ Folder Structure

```
knowledge-agent-poc/
├── core/
│   ├── schemas/              # JSON schema definitions
│   │   ├── base_schema.py
│   │   ├── paper_schema.py
│   │   ├── talk_schema.py
│   │   └── repository_schema.py
│   ├── extraction.py         # Core extraction logic
│   └── compilation.py        # Project-level compilation (stretch)
│
├── agents/                   # Knowledge extraction agents
│   ├── base_agent.py
│   ├── paper_agent.py
│   ├── talk_agent.py
│   └── repository_agent.py
│
├── prompts/                  # LLM prompt engineering
│   ├── paper_prompts.py
│   ├── talk_prompts.py
│   └── repository_prompts.py
│
├── inputs/                   # Sample research artifacts
│   ├── papers/              # PDF files (optional)
│   ├── transcripts/         # Talk transcripts
│   └── repositories/        # Repo metadata/links
│
├── outputs/                 # Generated knowledge artifacts
│   ├── structured/          # JSON outputs
│   └── summaries/           # Human-readable summaries
│
├── requirements.txt         # POC dependencies
├── README.md               # This file
└── .env.example            # Environment template
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your LLM credentials (Azure OpenAI, etc.)
```

### 3. Run a Sample Extraction
```bash
# Extract from a paper
python -m agents.paper_agent input.pdf

# Extract from a transcript
python -m agents.talk_agent transcript.txt

# Extract from a repo
python -m agents.repository_agent https://github.com/example/repo
```

### 4. Review Outputs
```bash
# Outputs in:
outputs/structured/    # JSON knowledge artifacts
outputs/summaries/     # Human-readable analysis
```

---

## 📊 Scope & Constraints

### In Scope (POC v1)
- ✅ Manual artifact selection (3–4 projects)
- ✅ Artifact-level knowledge extraction
- ✅ Prompt-based LLM agents
- ✅ Structured JSON schemas
- ✅ Human expert review
- ✅ Iterative prompt tuning

### Out of Scope
- ❌ Model fine-tuning
- ❌ Automated publishing
- ❌ Full knowledge graph
- ❌ Continuous ingestion pipelines
- ❌ MSR-wide deployment

---

## 🎯 Success Metrics

**POC Success Indicators:**
- Expert accuracy rating ≥ 4/5
- High inter-reviewer agreement
- Clear improvement over baseline abstracts
- Successful JSON production across all 3 artifact types
- Feasibility of project-level compilation (stretch goal)

---

## 📝 Knowledge Schema

All agents produce outputs following a **common baseline schema**:

- Title & Contributors
- Plain-language overview
- Technical problem addressed
- Key methods/approach
- Primary claims/capabilities
- Novelty vs. prior work
- Limitations & constraints
- Potential impact
- Open questions/future work
- Key evidence/citations
- Confidence score
- Provenance (agent + source type)

Each agent appends **datatype-specific sections** plus a flexible **Additional/Found Knowledge** section.

### Paper Schema Extension
- Publication & Context (venue, year, peer-review status)
- Data & Evaluation (datasets, benchmarks, metrics)
- Results & Evidence (quantitative results, reproducibility)
- Research Maturity (stage, limitations, ethics)

### Talk Schema Extension
- Presentation Structure (type, duration, sections)
- Demonstration & Evidence (demo included, live vs. recorded)
- Challenges & Forward-Looking Content (technical challenges, next steps)
- Audience & Framing (audience level, assumed knowledge)

### Repository Schema Extension
- Artifact Classification (type, purpose, intended users)
- Technical Stack (languages, frameworks, platforms)
- Operational Details (setup, training/inference, dependencies)
- Usage & Maturity (use cases, API, limitations)
- Governance & Access (license, data constraints)

---

## 🔄 Workflow

1. **Select Artifacts**: Choose 3–4 RRS projects with overlapping artifacts
2. **Collect Inputs**: Gather papers, transcripts, and repos
3. **Design Schemas**: Define v1 schema for each artifact type
4. **Run Extraction**: Execute agents to generate structured outputs
5. **Expert Review**: Assess quality, accuracy, completeness
6. **Iterate**: Refine prompts and schemas based on feedback
7. **Finalize**: Produce final v1 knowledge artifacts

---

## 🎨 Stretch Goal – Project-Level Compilation

Explore collating paper, talk, and repo knowledge JSON into a single project-level knowledge base:

- Synthesized project overview
- Project-level knowledge FAQ
- Resolution of conflicts/overlaps

**Success** = Technical feasibility demonstrated (not production-ready)

---

## 📖 Related Documentation

- [DECISION_GUIDE.md](../docs/DECISION_GUIDE.md) - General project guidance
- [docs/UNIFIED_ADAPTER_ARCHITECTURE.md](../docs/UNIFIED_ADAPTER_ARCHITECTURE.md) - EventKit adapter pattern
- Parent project: [EventKit on main branch](https://github.com/peterswimm/event-agent-december)

---

## 🛠️ Development Notes

- **LLMs Only**: No model fine-tuning; prompt engineering only
- **Iterative**: Expect multiple refinement cycles
- **Human-First**: All AI outputs are drafts requiring human review
- **Source Attribution**: All claims must reference original sources
- **Opt-In**: Only projects with explicit approval are included

---

## 📞 Feedback & Iteration

This is a living POC. Feedback from expert reviewers will drive:
- Prompt refinement
- Schema improvements
- New extraction capabilities
- Integration insights

---

**Last Updated**: December 18, 2025
**Status**: Active Development
**Branch**: poc1219
