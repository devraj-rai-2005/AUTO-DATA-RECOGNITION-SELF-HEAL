┌─────────────┐      ┌──────────────┐      ┌───────────────────┐
│   Next.js   │ SSE  │   FastAPI    │      │  ADK Runner        │
│  Dashboard  │◄────►│  (API layer) │◄────►│  (incident_pipeline)│
└─────────────┘      └──────┬───────┘      └──────────┬─────────┘
                             │                          │
                      ┌──────▼──────┐          ┌────────▼────────┐
                      │   Redis     │          │  Postgres        │
                      │ (job queue) │          │  - staging schema│
                      └─────────────┘          │  - ADK sessions  │
                                                │  - audit log     │
                                                └────────┬─────────┘
                                                          │
                                                 ┌────────▼─────────┐
                                                 │  DuckDB (ephemeral)│
                                                 │  sandbox dry-run   │
                                                 └────────────────────┘