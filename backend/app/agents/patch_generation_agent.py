from google.adk.agents import LlmAgent
from app.tools.migration_drafting import draft_migration_sql
from app.tools.artifacts import save_migration_artifacts
from app.schemas.incident import Remediation
from app.observability.tracing import on_agent_start, on_agent_end, on_model_response

patch_generation_agent = LlmAgent(
    name="patch_generation_agent",
    model="gemini-3.1-flash-lite-preview",
    instruction=(
        "You are drafting a remediation for this incident:\n{incident}\n\n"
        "1. Call draft_migration_sql with the incident's root_cause, "
        "affected_table (as table_name), rename_pairs, and null_columns.\n"
        "2. Then call save_migration_artifacts with the resulting SQL.\n"
        "3. Finally, return your response matching the Remediation schema with: "
        "incident_id (use the incident's incident_id or 'PENDING'), migration_sql, "
        "rollback_sql, and risk_notes explaining any assumptions made."
    ),
    before_agent_callback=on_agent_start,
    after_agent_callback=on_agent_end,
    after_model_callback=on_model_response,
    tools=[draft_migration_sql, save_migration_artifacts],
    output_schema=Remediation,
    output_key="remediation",
)