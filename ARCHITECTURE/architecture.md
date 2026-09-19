incident_pipeline (SequentialAgent)
├── triage_team (ParallelAgent)
│   ├── schema_drift_agent     — tool: inspect_schema_diff(table)
│   └── anomaly_validator_agent — tool: profile_nulls_and_types(table)
├── root_cause_agent            — synthesizes triage_team outputs → structured Incident JSON
├── patch_generation_agent      — tool: draft_migration_sql(incident) → SQL + rollback, saved as Artifacts
├── sandbox_dryrun_agent        — tool: run_duckdb_dryrun(patch) → diff + row-count reconciliation Artifact
├── hitl_gate                   — LongRunningFunctionTool: request_human_approval(diff)  [PAUSES HERE]
└── resolution_agent            — applies patch to Postgres if approved, writes audit record