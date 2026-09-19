adk-pipeline-healer/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── schema_drift_agent.py
│   │   │   ├── anomaly_validator_agent.py
│   │   │   ├── root_cause_agent.py
│   │   │   ├── patch_generation_agent.py
│   │   │   ├── sandbox_dryrun_agent.py
│   │   │   ├── resolution_agent.py
│   │   │   └── pipeline.py          # wires the SequentialAgent/ParallelAgent tree + App/ResumabilityConfig
│   │   ├── tools/
│   │   │   ├── schema_inspection.py # inspect_schema_diff
│   │   │   ├── data_profiling.py    # profile_nulls_and_types
│   │   │   ├── migration_drafting.py# draft_migration_sql
│   │   │   ├── sandbox_runner.py    # run_duckdb_dryrun
│   │   │   └── approval.py          # request_human_approval (LongRunningFunctionTool)
│   │   ├── schemas/
│   │   │   ├── incident.py          # Pydantic Incident/Remediation structured-output schema
│   │   │   └── events.py            # SSE event payload schemas
│   │   ├── services/
│   │   │   ├── session_service.py   # ADK DatabaseSessionService → Postgres
│   │   │   ├── artifact_service.py  # ADK artifact storage config
│   │   │   ├── failure_injector.py  # simulated ingestion + fault injection
│   │   │   └── job_queue.py         # Redis queue wrapper (arq)
│   │   ├── api/
│   │   │   ├── routes_pipeline.py   # trigger ingestion, list runs
│   │   │   ├── routes_incidents.py  # incident detail, decision endpoint
│   │   │   └── routes_stream.py     # SSE endpoint
│   │   ├── db/
│   │   │   ├── models.py            # pipeline_run, incident, audit_log
│   │   │   ├── session.py           # async engine/session
│   │   │   └── migrations/          # alembic
│   │   ├── worker.py                # consumes Redis queue, runs the ADK Runner
│   │   ├── config.py                # pydantic-settings
│   │   └── main.py                  # FastAPI app factory
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   ├── incidents/[id]/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── pipeline-visualizer/
│   │   ├── incident-diff-viewer/
│   │   └── ui/                      # shadcn components
│   ├── lib/
│   │   ├── sse.ts
│   │   └── api.ts
│   └── package.json
│
├── docker/
│   ├── docker-compose.dev.yml       # Postgres + Redis only, for local dev
│   ├── backend.Dockerfile           # built in Phase 10
│   └── frontend.Dockerfile          # built in Phase 10
│
├── .env.example
└── README.md