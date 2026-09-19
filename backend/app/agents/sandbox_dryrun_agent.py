from google.adk.agents import LlmAgent
from app.tools.sandbox_runner import run_duckdb_dryrun
from app.schemas.incident import DryRunResult
from app.observability.tracing import on_agent_start, on_agent_end, on_model_response

sandbox_dryrun_agent = LlmAgent(
    name="sandbox_dryrun_agent",
    model="gemini-3.1-flash-lite-preview",
    instruction=(
        "Incident: {incident}\n"
        "Proposed remediation: {remediation}\n\n"
        "Call run_duckdb_dryrun with the incident's affected_table (as table_name) "
        "and the remediation's migration_sql.\n"
        "Then return your response matching the DryRunResult schema with: "
        "incident_id, rows_before, rows_after, changed_sample, dry_run_succeeded, and notes."
    ),
    before_agent_callback=on_agent_start,
    after_agent_callback=on_agent_end,
    after_model_callback=on_model_response,
    tools=[run_duckdb_dryrun],
    output_schema=DryRunResult,
    output_key="dry_run_result",
)