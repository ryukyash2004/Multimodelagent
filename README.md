# Atlas — Enterprise Multimodal AI Assistant Platform

> A serverless, multi-agent RAG platform on Google Cloud that securely connects Gemini to Google Workspace via OAuth, supports text/voice/image/video input, and enforces enterprise governance through VPC-SC, CMEK, and full audit logging.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Cloud Run](https://img.shields.io/badge/deploy-Cloud%20Run-4285F4.svg)](https://cloud.google.com/run)
[![LangGraph](https://img.shields.io/badge/orchestration-LangGraph-1C3C3C.svg)](https://langchain-ai.github.io/langgraph/)
[![MCP](https://img.shields.io/badge/protocol-MCP-6E4AFF.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [MCP Integrations](#-mcp-integrations)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Learning Roadmap](#-learning-roadmap)
- [Evaluation](#-evaluation)
- [Security & Governance](#-security--governance)
- [Deployment](#-deployment)
- [Demo](#-demo)
- [What I'd Do Next](#-what-id-do-next)
- [Acknowledgements](#-acknowledgements)
- [License](#-license)

---

## 🎯 Overview

**Atlas** is a production-grade generative AI platform that lets enterprise employees:

1. **Ask questions** across internal documents and databases using Retrieval-Augmented Generation (RAG).
2. **Automate workflows** in Google Workspace (Gmail, Calendar, Docs, Drive) through secure OAuth 2.0 connectors.
3. **Interact multimodally** — via text, voice, images, and video — through a unified agent interface.
4. **Trust the output** — every response is governed by VPC Service Controls, CMEK encryption, PII redaction, and full audit logging.

This project was built as a **hands-on learning journey** to master modern AI engineering: agent orchestration, RAG, multimodal LLMs, MCP integrations, and enterprise cloud deployment.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Agent Orchestration** | LangGraph state machine routing between RAG, Workspace, SQL, and Media agents |
| 📚 **Hybrid RAG** | BM25 + dense retrieval with re-ranking over internal documents |
| 🔐 **Secure Workspace Connectors** | OAuth 2.0 with least-privilege scopes for Gmail, Calendar, Docs, Drive |
| 🎙️ **Multimodal I/O** | Text, voice (STT/TTS), image understanding, video summarization |
| 🧩 **MCP-Native** | Uses Model Context Protocol servers for Workspace, Postgres, and multimodal tools |
| ☁️ **Serverless** | Cloud Run + Cloud Functions + Cloud Workflows (scales to zero) |
| 🛡️ **Enterprise Governance** | VPC-SC, CMEK, Model Armor, DLP, RBAC, Cloud Audit Logs |
| 📊 **Eval Harness** | RAGAS metrics + agent trajectory accuracy on a 50-task golden set |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Clients: Web App / Slack / Mobile / Voice (Twilio)          │
└───────────────┬──────────────────────────────────────────────┘
                │
        ┌───────▼────────┐
        │  API Gateway   │  (Cloud Endpoints / Apigee + IAP)
        └───────┬────────┘
                │
     ┌──────────▼───────────┐
     │  Orchestrator Agent  │  ← LangGraph / Google ADK
     │  (Router + Planner)  │
     └──┬────┬────┬────┬────┘
        │    │    │    │
   ┌────▼─┐ ┌▼───┐ ┌▼────┐ ┌▼─────┐
   │ RAG  │ │GW  │ │Media│ │SQL   │
   │Agent │ │Agt │ │Agent│ │Agent │
   └──┬───┘ └┬───┘ └┬────┘ └┬─────┘
      │      │      │       │
   Vertex  MCP:    MCP:    MCP:
   Vector  Work-   Open-   Postgres
   Search  space   Router
```

**Flow:** Client → API Gateway → Orchestrator → specialized Agent → MCP tool → external system → Compliance filter → response.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.11 |
| **Agent Framework** | LangGraph + LangChain (fallback: Google ADK, AutoGen) |
| **LLM** | Gemini 1.5 Pro / Flash (fallback: GPT-4o-mini) |
| **Embeddings** | `text-embedding-004` / `nomic-embed-text` (local dev) |
| **Vector Store** | Vertex AI Vector Search (prod) / ChromaDB (local) |
| **Relational** | BigQuery + Cloud SQL (Postgres) |
| **Multimodal** | Gemini Vision, Whisper, Cloud STT/TTS |
| **Protocol** | Model Context Protocol (MCP) |
| **Cloud** | GCP: Cloud Run, Functions, Workflows, Pub/Sub, Secret Manager |
| **IaC** | Terraform |
| **Observability** | Cloud Logging + LangSmith / OpenTelemetry |
| **Auth** | IAP + OAuth 2.0 (Workspace scopes) |
| **Eval** | RAGAS, LangSmith, custom trajectory scorer |

---

## 🧩 MCP Integrations

Atlas is built **MCP-first**, meaning external capabilities are consumed as Model Context Protocol servers rather than hardcoded SDK calls.

| Phase | MCP Server | Purpose | Notes |
|-------|-----------|---------|-------|
| 3 | **Google Workspace MCP** (official, public preview) | Gmail, Drive, Calendar, Docs, Sheets, Slides | Requires enabling `gmailmcp.googleapis.com`, `drivemcp.googleapis.com`, etc. |
| 3 | `workspace-mcp` (community, PyPI) | Fallback Workspace connector | Streamable HTTP/SSE, granular tool selection, OAuth 2.1 multi-user |
| 1 | `@modelcontextprotocol/server-postgres` | Internal SQL database access | Widely used, well-maintained |
| 1 | **MariaDB Enterprise MCP** (optional) | Enterprise-grade RAG + hybrid search | Secure SQL gateway with built-in vector search |
| 4 | **OpenRouter Multimodal MCP** | Text, image, audio, video via one key | 19 tools, 300+ models, async video jobs |
| 5 | **Cloud Run MCP** (`GoogleCloudPlatform/cloud-run-mcp`) | Deploy apps from the agent | Directly supports Step 5.2 |

> **Tip:** Use [best-of-mcp-servers](https://github.com/tolkonepiu/best-of-mcp-servers) and [awesome-mcp](https://github.com/abordage/awesome-mcp) to discover more servers. Check **Trust Scores** on [mcpworld.com](https://mcpworld.com) before adopting community MCPs.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/) (for local dev)
- Google Cloud SDK (`gcloud`)
- Docker
- A Google Cloud project with billing enabled

### Local Setup (Phase 1)

```bash
# Clone and enter
git clone https://github.com/<you>/atlas.git
cd atlas

# Create virtualenv
python -m venv .venv && source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Pull local models
ollama pull gemma3:4b
ollama pull nomic-embed-text

# Run the naive RAG demo
python scripts/hello_rag.py
```

### Configure Secrets

```bash
cp .env.example .env
# Edit .env and add:
#   GEMINI_API_KEY=...
#   GOOGLE_CLIENT_ID=...
#   GOOGLE_CLIENT_SECRET=...
#   PROJECT_ID=...
```

> ⚠️ **Never commit** `credentials.json`, `token.pkl`, or `.env`.

### Run Locally (FastAPI)

```bash
uvicorn app.main:app --reload --port 8080
# Then: curl -X POST localhost:8080/chat -d '{"text":"What was revenue growth?"}'
```

---

## 📁 Project Structure

```
atlas/
├── agents/                  # LangGraph orchestrator + specialized agents
│   ├── orchestrator.py
│   ├── rag_agent.py
│   ├── workspace_agent.py
│   ├── media_agent.py
│   ├── sql_agent.py
│   └── compliance_agent.py
├── rag/                     # Ingestion + retrieval pipeline
│   ├── ingest.py
│   ├── chunking.py
│   ├── retriever.py
│   └── reranker.py
├── mcp/                     # MCP client wrappers
│   ├── workspace_client.py
│   ├── postgres_client.py
│   └── openrouter_client.py
├── connectors/              # OAuth + API adapters
│   ├── gmail.py
│   ├── calendar.py
│   ├── docs.py
│   └── oauth.py
├── multimodal/              # Voice, image, video handlers
│   ├── voice.py
│   ├── image.py
│   └── video.py
├── app/                     # FastAPI service
│   ├── main.py
│   └── schemas.py
├── eval/                    # RAGAS + trajectory harness
│   ├── golden.json
│   ├── run_ragas.py
│   └── run_trajectory.py
├── infra/                   # Terraform
│   ├── main.tf
│   ├── cloud_run.tf
│   ├── vpc_sc.tf
│   └── kms.tf
├── scripts/                 # One-off helpers
│   └── hello_rag.py
├── tests/
├── Dockerfile
├── requirements.txt
├── .env.example
├── AGENT.md                 # Learning guide (student-facing)
├── GOVERNANCE.md            # Security controls documentation
└── README.md
```

---

## 📚 Learning Roadmap

Atlas is designed as a **7-phase guided build**. See [`AGENT.md`](./AGENT.md) for the full student-facing guide with Notes → Questions → Hints → Approach → Answer.

| Phase | Focus | Deliverable |
|-------|-------|-------------|
| 1 | Local RAG foundation | PDF Q&A with RAGAS scores |
| 2 | Agentic orchestration | LangGraph router + tool calling |
| 3 | Workspace connectors | OAuth tools for Gmail/Calendar/Docs |
| 4 | Multimodal | Voice in/out, image, video summary |
| 5 | Serverless deploy | FastAPI on Cloud Run |
| 6 | Governance | VPC-SC, CMEK, audit logs, RBAC |
| 7 | Evaluation & demo | Eval harness + README + Loom |

---

## 🧪 Evaluation

Atlas is evaluated on two axes:

### RAG Quality (RAGAS)
| Metric | Target |
|--------|--------|
| Faithfulness | ≥ 0.90 |
| Answer Relevancy | ≥ 0.85 |
| Context Precision | ≥ 0.80 |
| Context Recall | ≥ 0.75 |

### Agent Trajectory
- **Tool-F1** on a 50-task golden set ≥ 0.85
- **End-to-end latency** P95 < 4s (text), < 8s (voice)
- **Cost per query** tracked in BigQuery

Run locally:

```bash
python eval/run_ragas.py
python eval/run_trajectory.py
```

---

## 🔐 Security & Governance

| Control | Implementation |
|---------|---------------|
| **Network isolation** | VPC Service Controls perimeter around project |
| **Encryption** | CMEK via Cloud KMS (data + model endpoints) |
| **Secrets** | Secret Manager (never in image or env files) |
| **AuthN/AuthZ** | IAP + OAuth 2.0 with least-privilege scopes |
| **RBAC** | `viewer`, `agent-user`, `admin` roles |
| **Prompt defense** | Model Armor for injection/jailbreak filtering |
| **PII protection** | Cloud DLP redaction pre- and post-LLM |
| **Audit** | Cloud Audit Logs → BigQuery sink → Looker Studio |
| **Human-in-the-loop** | `interrupt_before=["tools"]` for write actions |

Full details in [`GOVERNANCE.md`](./GOVERNANCE.md).

---

## ☁️ Deployment

### One-Command Deploy (Cloud Run)

```bash
# Build & push image
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT/atlas/api

# Deploy
gcloud run deploy atlas-api \
  --image us-central1-docker.pkg.dev/$PROJECT/atlas/api \
  --region us-central1 \
  --set-secrets GEMINI_API_KEY=gemini-key:latest \
  --no-allow-unauthenticated   # IAP in front
```

### Terraform (recommended for reproducibility)

```bash
cd infra
terraform init
terraform plan -var="project_id=$PROJECT"
terraform apply
```

Resources provisioned: Cloud Run service, Artifact Registry, Secret Manager, KMS keyring, VPC-SC perimeter, BigQuery audit dataset, IAM bindings.

---

## 🎥 Demo

> 📹 **[Watch the 2-minute Loom demo →](https://loom.com/your-demo)**

**Demo script:**
1. Ask: *"Summarize the latest unread email from finance."* → Workspace MCP fires, Gmail tool runs.
2. Ask: *"What was Q3 revenue growth?"* → RAG retrieves from annual report.
3. Upload a chart image → MediaAgent describes the trend.
4. Say via voice: *"Schedule a follow-up with Alice next Tuesday."* → Human-in-the-loop confirmation → Calendar event created.
5. Show the **audit log** in BigQuery: every tool call, user, timestamp, latency.

---

## 🔭 What I'd Do Next

- **Fine-tune Gemma 2** for intent routing to reduce per-query cost.
- **Streaming voice agent** with barge-in support (user interrupts mid-answer).
- **AutoGen swarm** for complex multi-step research tasks.
- **On-device Gemini Nano** path for PII-sensitive queries.
- **Multi-tenant workspaces** with per-tenant CMEK keys.
- **Continuous eval** — run RAGAS nightly on fresh production queries.

---

## 🙏 Acknowledgements

- [LangGraph](https://langchain-ai.github.io/langgraph/) — agent orchestration
- [Model Context Protocol](https://modelcontextprotocol.io/) — tool interoperability
- [Google Cloud Vertex AI + Gemini Enterprise](https://cloud.google.com/vertex-ai) — managed GenAI platform
- [RAGAS](https://github.com/explodinggradients/ragas) — RAG evaluation
- [best-of-mcp-servers](https://github.com/tolkonepiu/best-of-mcp-servers) & [awesome-mcp](https://github.com/abordage/awesome-mcp) — MCP discovery
- [Agentic AI Learning Roadmap](https://github.com/) — curriculum inspiration

---

## 📄 License

MIT © 2026 — See [LICENSE](./LICENSE).

---

<p align="center">
  <b>Built as a learning journey from naive RAG to enterprise-grade GenAI.</b><br/>
  <i>If you're a student reading this — fork it, break it, ship it. 🚀</i>
</p>