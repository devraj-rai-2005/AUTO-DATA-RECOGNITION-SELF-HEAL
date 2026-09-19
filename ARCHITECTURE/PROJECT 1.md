Bro, I want you to act as my **AI Engineering mentor, system architect, senior developer, and project reviewer**.

These should NOT be simple tutorial projects or CRUD applications.

project must feel like a **real-world AI product that could be shown to an AI Engineer interviewer or recruiter.**

## 🎯 Main Goal

For project, help me build a complete system from:

**Idea → Architecture → Folder Structure → Environment → Backend → Agents → Tools → Memory → RAG → Database → APIs → Frontend → Observability → Testing → Docker → Deployment → Documentation**

You will write and build the code by yourself i am just telling you that it is done go towards the next phase.

You will act as my **senior AI Engineer who is helping making a complete project for me.**.

Do NOT dump the entire project code at once, do it every phase.

Instead, guide me and explain me the theroy stuff , build the project and i will copy it and them  implement it.

---


# PROJECT: Autonomous Data Pipeline Self-Healing & Reconciliation Engine — Google ADK

```
I'm building Project :- Autonomous Data Pipeline Self-Healing & Reconciliation Engine using
Google ADK.

CONCEPT: The user connects a database/warehouse staging schema (e.g.,
PostgreSQL/DuckDB) and simulated data ingestion pipeline (CSV/JSON/SQL
transforms). When ingestion jobs fail due to schema drift, type mismatches,
or constraint violations, an ADK multi-agent system diagnoses root causes,
validates anomalies, drafts a deterministic migration/patch script, runs a
dry-run reconciliation in an isolated sandbox, and escalates via HITL
before applying schema or pipeline updates.

REQUIRED CAPABILITIES TO DEMONSTRATE:
- ADK SequentialAgent (Failure Ingestion → Root Cause Analysis →
  Patch Generation → Sandbox Dry-Run → HITL Verification → Resolution)
- ADK ParallelAgent (concurrently execute: Schema Drift Analyzer,
  Null/Type Anomaly Validator, Upstream Lineage Impact Inspector)
- Model Context Protocol (MCP) or ADK Tools (database metadata inspection,
  SQL explain/dry-run runner, data profiling/row count reconciler)
- Sessions + State (persist pipeline incident logs, error context,
  and migration state across multi-turn analysis)
- Callbacks & Event Streaming (stream agent thoughts, sandbox dry-run
  diffs, and intermediate triage progress via SSE/WebSocket)
- Artifacts (store generated SQL migration scripts, rollback plans, and
  pre/post data distribution summary cards)
- Human-in-the-Loop (HITL) approval step: Schema altering scripts (ALTER
  TABLE, backfill DML) pause for human review before execution.
- Structured Outputs (standardized JSON Incident & Remediation schema
  shared across agents)

BACKEND: FastAPI, PostgreSQL (metadata, pipeline logs, audit store),
DuckDB (isolated dry-run sandbox execution), Redis (event bus/job queue),
SSE for streaming agent execution trace.

FRONTEND: Next.js + TypeScript + Tailwind + shadcn/ui. Ingestion pipeline
dashboard, real-time agent execution pipeline visualizer, interactive SQL
diff/dry-run preview with Approve/Reject/Modify controls, and an incident
reconciliation audit log.
```

---


# 🧠 PROJECT REQUIREMENTS

Every project should demonstrate real Agentic AI engineering.

Depending on the project, use appropriate capabilities such as:

- Multi-agent architecture
- Agent orchestration
- Tool calling
- MCP where useful
- RAG
- Vector databases
- Long-term / short-term memory
- Structured outputs
- Human-in-the-loop
- Planning
- Reflection / critique
- Agent delegation
- Parallel execution
- Sequential workflows
- Event-driven workflows
- Streaming
- Authentication
- REST APIs
- WebSockets when useful
- Background jobs
- Caching
- Database persistence
- Error handling
- Retry mechanisms
- Observability
- Logging
- Evaluation
- Guardrails
- Rate limiting
- Docker
- CI/CD
- Deployment

Do NOT force every technology into every project.

Use only what genuinely makes architectural sense.

---

# 🏗️ PRODUCTION-GRADE STANDARD

For every project, design it as if it needs to support a real user.

Think about:

### Architecture
- Scalability
- Reliability
- Maintainability
- Modularity
- Security
- Performance

### AI Engineering
- Agent boundaries
- Tool boundaries
- Context management
- Token efficiency
- Model selection
- Hallucination reduction
- Evaluation
- Guardrails

### Backend
- API design
- Authentication
- Database
- Async processing
- Error handling
- Logging

### Frontend
The frontend should NOT look like a basic ChatGPT clone.

Create a **modern AI product experience** with things such as:

- Agent activity
- Streaming responses
- Tool execution visibility
- Workflow progress
- Sources/citations
- Agent reasoning STATUS, but never expose hidden chain-of-thought
- Tasks/jobs
- History
- Dashboard
- Results
- Human approval when required

The UI should make the multi-agent system **visually understandable**.

---

# 🎨 FRONTEND EXPERIENCE

I want the frontend to feel like a modern AI product.

Possible stack:

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- WebSockets / SSE
- Framer Motion when useful

But choose the stack based on the project.

The frontend should communicate:

**"This is an AI system, not just a Python script."**

---

# 🤖 FRAMEWORK-SPECIFIC REQUIREMENTS

## Google ADK Projects

Use Google ADK properly.

Explore appropriate concepts such as:

- Agents
- LLM agents
- Workflow agents
- Sequential agents
- Parallel agents
- Loop agents
- Tools
- Sessions
- State
- Callbacks
- Artifacts
- Evaluation
- Streaming
- Multi-agent orchestration
- Gemini integration
- MCP where useful

Do not use ADK merely as a wrapper around an LLM.

The architecture should clearly demonstrate why ADK is useful.

---

# 📁 FOLDER STRUCTURE

Before writing implementation code, give me:

1. Complete architecture
2. System architecture diagram
3. Agent architecture
4. Data flow
5. Request flow
6. Complete folder structure
7. Responsibilities of every major folder/file
8. Technology stack
9. Dependencies
10. Environment variables
11. Database schema
12. API design
13. Agent communication design

Example style:

```text
project/
│
├── backend/
│   ├── agents/
│   ├── tools/
│   ├── workflows/
│   ├── memory/
│   ├── rag/
│   ├── models/
│   ├── services/
│   ├── api/
│   ├── database/
│   ├── evaluation/
│   ├── observability/
│   └── main.py
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   └── ...
│
├── tests/
├── docker/
├── .env.example
├── docker-compose.yml
├── README.md
└── ...
```

Modify this structure according to the actual project.

---

# 🛠️ DEVELOPMENT PROCESS

Build the project in phases.

## Phase 0 — Product Definition

Define:

- Problem
- Target users
- Real-world use case
- Core features
- Advanced features
- Success criteria

---

## Phase 1 — Architecture

Create:

- High-level architecture
- Agent architecture
- Data flow
- Component interaction
- Technology decisions

Explain WHY each major technology is selected.

---

## Phase 2 — Project Setup

Give me:

- Folder structure
- Python environment
- Node environment
- requirements.txt / pyproject.toml
- package.json
- .env.example
- configuration strategy

---

## Phase 3 — Core Agent System

Build:

- Agents
- Agent roles
- Tools
- Orchestration
- State
- Memory
- Structured outputs

---

## Phase 4 — Knowledge / Data Layer

If required:

- Document ingestion
- Chunking
- Embeddings
- Vector database
- Retrieval
- Reranking
- Metadata
- Citation system

---

## Phase 5 — Backend

Build:

- FastAPI
- API routes
- Services
- Database
- Authentication
- Async jobs
- Streaming
- WebSockets/SSE where appropriate

---

## Phase 6 — Frontend

Build a polished production-style UI.

Include:

- Dashboard
- AI workspace
- Agent activity
- Streaming
- Tool execution
- Results
- Sources
- History
- Settings
- Error states
- Loading states

---

## Phase 7 — Observability

Add:

- Structured logging
- Agent traces
- Tool traces
- Latency
- Token usage
- Errors
- Evaluation metrics

Never expose private chain-of-thought.

Show only safe execution information such as:

```text
Research Agent → searching documents
Data Agent → querying database
Critic Agent → validating result
Final Agent → generating response
```

---

## Phase 8 — Evaluation

Create a proper evaluation system.

Include:

- Test datasets
- Agent tests
- Tool tests
- RAG evaluation
- Response quality
- Hallucination checks
- Latency
- Cost
- Regression tests

---

## Phase 9 — Security

Consider:

- Authentication
- Authorization
- Input validation
- Prompt injection
- Tool abuse
- Secrets management
- Rate limiting
- File validation
- Sandboxing if code execution exists

---

## Phase 10 — Production

Add:

- Docker
- Docker Compose
- Environment configuration
- Production configuration
- Health checks
- CI/CD
- Deployment architecture

---

# 📊 FINAL PROJECT QUALITY CHECK

At the end, review the project as an **AI Engineering interviewer**.

Give me scores for:

| Category | Score |
|---|---:|
| AI Architecture | /10 |
| Agent Design | /10 |
| Framework Usage | /10 |
| Backend | /10 |
| Frontend | /10 |
| RAG | /10 |
| Memory | /10 |
| Tooling | /10 |
| Observability | /10 |
| Evaluation | /10 |
| Security | /10 |
| Scalability | /10 |
| Code Quality | /10 |
| Production Readiness | /10 |

Then tell me:

### 🔴 Weak Areas
What is missing or weak?

### 🟡 Improvements
What should I improve?

### 🟢 Strong Areas
What makes this project impressive?

### 💼 Interview Questions
Give me the questions an interviewer could ask about this project.

### 🎯 Resume
Give me 3–5 strong resume bullet points.

### 🐙 GitHub
Create a professional README structure and explain what screenshots/videos/architecture diagrams I should include.

---

# ⚠️ IMPORTANT RULES

1. **Do not dump the entire codebase at once. Do it in Phases**

2. Give me a Code and i Will copy paste it.

3. Prefer production-quality architecture over unnecessary complexity.

4. Do not add technologies just to make the project look impressive.

5. The frontend must be treated as a Last part of the project.