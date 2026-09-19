# Autonomous Data Pipeline Self-Healing & Reconciliation Engine

A multi-agent system, built on Google ADK, that detects data pipeline ingestion failures (schema drift, unexpected NULLs, datetime format drift), diagnoses the root cause, drafts a deterministic migration + rollback script, dry-runs it in an isolated sandbox, and pauses for human approval before applying anything to production.



## Problem & Approach

Data pipelines fail silently when upstream data shape changes — a renamed column, a null rate spike, a datetime format flip. Someone gets paged, manually inspects the failure, and hand-writes a fix. This project automates diagnosis and patch drafting with an agentic pipeline, but treats schema mutation as too risky to fully automate: every fix is dry-run in a disposable sandbox and requires an explicit human approval before touching real data.

**v1 scope** (see [Known Limitations](#known-limitations) for what's intentionally out of scope):

- Column rename detection
- Unexpected NULL detection
- Datetime format drift detection (diagnosed, not yet auto-remediated)

## Architecture

```mermaid
flowchart LR
    subgraph Client
        FE[Next.js Dashboard]
    end
    subgraph Backend
        API[FastAPI]
        Worker[arq Worker]
    end
    subgraph Data
        PG[(Postgres — staging schema, ADK sessions, audit log)]
        Redis[(Redis — job queue + pub/sub)]
        Duck[(DuckDB — ephemeral sandbox)]
    end

    FE -- SSE --> API
    FE -- REST --> API
    API -- enqueue job --> Redis
    Worker -- consumes --> Redis
    Worker -- ADK Runner --> PG
    Worker -- dry-run --> Duck
```

### Agent tree

```mermaid
flowchart TD
    SEQ["incident_pipeline (SequentialAgent)"] --> PAR["triage_team (ParallelAgent)"]
    PAR --> SD[schema_drift_agent]
    PAR --> AV[anomaly_validator_agent]
    SEQ --> RC[root_cause_agent]
    RC --> PG2[patch_generation_agent]
    PG2 --> DR[sandbox_dryrun_agent]
    DR --> HG["hitl_gate (pauses for human approval)"]
    HG --> RES[resolution_agent]
```

## Key Design Decisions

- **Templated, deterministic SQL — not freeform LLM-authored DDL.** `patch_generation_agent` selects parameters into vetted SQL templates keyed by root cause; it never writes arbitrary `ALTER TABLE`/`UPDATE` statements itself. `resolution_agent`'s `apply_resolution` re-validates the SQL shape against those same templates immediately before execution, even after human approval — approval means "apply the reviewed patch," not "run arbitrary SQL I was shown a diff of."
- **SSE for status streaming, plain REST for approval — decoupled on purpose.** Resuming a paused ADK run while a live SSE stream is attached is a known rough edge in current ADK versions. Approval decisions go through an ordinary `POST /incidents/{id}/decision` endpoint instead of the live socket, sidestepping that entirely.
- **ADK 1.x, pinned exactly, not a version range.** Human-in-the-loop pause/resume (`ResumabilityConfig` + `LongRunningFunctionTool`) is a newer, actively-changing feature with documented regressions across recent releases. Pin the exact version you tested against.
- **Postgres serves both app data and ADK sessions.** `DatabaseSessionService` points at the same Postgres instance as the app's own tables, so "Sessions + State" and "audit store" aren't two systems to keep in sync.
- **No RAG / vector database.** Every agent reasons over structured schema metadata and profiling output — there's no unstructured corpus to retrieve from. Adding one would be complexity without purpose.
- **Hand-rolled observability instead of OpenTelemetry.** Structured JSON logs + a Postgres `agent_trace` table cover latency/token tracking for a solo build at this scale. Upgrade path: swap for OTel + a real backend (Honeycomb, Tempo) if this needed to scale past a demo.
- **"Request Changes" instead of a full patch-editing "Modify" flow.** Scoped down from the original three-way approval design to fit the build timeline — it's an honest, smaller feature (reject + tagged reason) rather than a half-built editor.

## Tech Stack

| Layer           | Technology                                                          |
| --------------- | ------------------------------------------------------------------- |
| Agent framework | Google ADK (Python, 1.x — pin exact version)                       |
| Backend         | FastAPI, arq (async worker), Redis, SQLAlchemy (async)              |
| Databases       | PostgreSQL 16 (app data + ADK sessions), DuckDB (ephemeral sandbox) |
| Frontend        | Next.js, TypeScript, Tailwind CSS v4, shadcn/ui                     |
| Observability   | Structured JSON logging, custom`agent_trace` Postgres table       |
| Evaluation      | LLM classification harness + deterministic pytest suite             |
| Infra           | Docker, Docker Compose, GitHub Actions                              |

---

## Requirements

Install these before doing anything else:

| Requirement             | Version       | Notes                                                                                                          |
| ----------------------- | ------------- | -------------------------------------------------------------------------------------------------------------- |
| Python                  | 3.11+         | Required by ADK                                                                                                |
| Node.js                 | 20+           | For the Next.js frontend                                                                                       |
| Docker + Docker Compose | Recent stable | For Postgres/Redis (dev) or the full stack (prod-style)                                                        |
| Google API key          | —            | From[Google AI Studio](https://aistudio.google.com/apikey) — used as `GOOGLE_API_KEY`, no GCP project needed |

Ports used locally: `3000` (frontend), `8000` (backend API), `5432` (Postgres), `6379` (Redis).

---

## Complete Setup & Run Guide

This assumes you've placed all the code into the folder structure below and are starting from a completely clean machine.

### 0. Expected folder layout

```
adk-pipeline-healer/
├── backend/
│   ├── app/            # agents, tools, api, db, services, worker.py, main.py, config.py
│   ├── tests/
│   ├── evaluation/
│   ├── migrations/     # created by alembic in step 3
│   ├── alembic.ini      # created by alembic in step 3
│   └── pyproject.toml
├── frontend/            # Next.js app
├── docker/
│   ├── docker-compose.dev.yml
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── docker-compose.yml   # full stack, for prod-style runs
└── .env                 # copy from your own notes — see step 1
```

### 1. Environment variables

Create `backend/.env`:

```bash
GOOGLE_API_KEY=your-ai-studio-key
GOOGLE_GENAI_MODEL=gemini-2.5-flash

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pipeline_healer
ADK_SESSION_SERVICE_URI=postgresql+psycopg2://postgres:postgres@localhost:5432/pipeline_healer

REDIS_URL=redis://localhost:6379/0
DUCKDB_SANDBOX_DIR=./data/sandbox

ENV=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
API_KEY=dev-local-key-change-me
```

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 2. Start Postgres + Redis

```bash
docker compose -f docker/docker-compose.dev.yml up -d
```

Confirm both are up: `docker ps` should show `postgres:16` and `redis:7` running.

### 3. Backend: install, migrate

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"

# One-time: initialize alembic if migrations/ doesn't exist yet
alembic init migrations

# Point alembic at your DB — edit migrations/env.py to import settings
# and set target_metadata = Base.metadata, and set sqlalchemy.url from
# settings.adk_session_service_uri (sync driver) rather than hardcoding it.

alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

### 4. Start the worker (own terminal, keep running)

```bash
# from backend/, with the venv active
arq app.worker.WorkerSettings
```

### 5. Start the API (own terminal, keep running)

```bash
# from backend/, with the venv active
uvicorn app.main:app --reload --port 8000
```

Confirm: `curl.exe http://localhost:8000/health` returns `{"status": "ok", "checks": {"database": true, "redis": true}}`.

$decision = @{
    approved = $true
    reviewer_notes = "Verified column rename fix via DuckDB dry-run"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/incidents/<incident_id>/decision" `  -Method Post`
  -Headers @{ "X-API-Key" = "dev-local-key-change-me" } `  -ContentType "application/json"`
  -Body $decision

### 6. Start the frontend (own terminal, keep running)

```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:3000/dashboard**.

### 7. Run the demo

1. Click a failure type (e.g. "Column rename") on the dashboard.
2. Watch the live agent status feed populate as `triage_team` runs in parallel, then `root_cause_agent`, `patch_generation_agent`, and `sandbox_dryrun_agent` run in sequence.
3. Once it appears under **Incidents**, click into it.
4. Review the root cause, dry-run row counts, and the migration/rollback SQL.
5. Click **Approve** (or **Reject**, or **Request Changes** with a note) and watch the status settle.
6. Click **View agent trace** to see per-agent latency and token usage.

### Alternative: run everything via Docker Compose (no local Python/Node needed)

```bash
docker compose up --build
```

This builds and runs Postgres, Redis, the backend API, the worker, and the frontend from the root `docker-compose.yml`. Same URLs apply (`localhost:3000`, `localhost:8000`).

### Running the test suites

```bash
# Free, fast, no API calls — safe to run constantly
cd backend
pytest tests/test_deterministic.py -v

# Costs real API calls, takes a few minutes — run before merging significant agent changes
python -m evaluation.run_eval
```

---

## Evaluation Results

[Paste the output table from `python -m evaluation.run_eval` here, including overall accuracy and the false-positive count on clean-table cases.]

## Known Limitations

- Frontend is functionally complete but not exhaustively polished beyond the dashboard/incident/trace pages.
- SSE has no reconnect story (`Last-Event-ID`) if a backend instance restarts mid-stream.
- Evaluation harness runs a small sample size (N=3 per case) and isn't gated in CI.
- Single shared API key rather than per-reviewer identity — adequate for a solo demo, not for multi-user production use.
- `datetime_drift` is correctly diagnosed but has no automatic remediation template yet.
- HITL pause/resume depends on a newer ADK feature (`ResumabilityConfig`) with open upstream issues on some version combinations — pin your ADK version and test the resume flow before relying on it.
- Upstream Lineage Impact Inspector agent and `LoopAgent`-based patch refinement were scoped out of v1 as stretch goals.

## Production Deployment Notes

The included `docker-compose.yml` is single-host, single-instance — fine for a demo, not for real traffic. For an actual production deployment:

- Managed Postgres (Cloud SQL / RDS) instead of a containerized instance, for backups and failover.
- Managed Redis (Memorystore / ElastiCache), removing it as a shared single point of failure between the job queue and SSE pub/sub.
- Horizontally scaled `arq` workers — since Redis is already the queue, this requires no code changes.
- Secrets in a real secrets manager instead of `.env`.
- SSE reconnect handling for backend restarts.

For a live demo link rather than local-only: a single small VM or a PaaS (Render/Fly.io) running `docker-compose.yml` as-is is genuinely sufficient — it's honest about being a demo, not a claim of production scale.
