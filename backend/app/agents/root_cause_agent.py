from google.adk.agents import LlmAgent
from app.schemas.incident import Incident
from app.observability.tracing import on_agent_start, on_agent_end, on_model_response



root_cause_agent = LlmAgent(
    name="root_cause_agent",
    model="gemini-3.1-flash-lite-preview",
    instruction=(
        "You are synthesizing a data pipeline incident report from two "
        "diagnostic findings for pipeline_run_id={pipeline_run_id}.\n\n"
        "Schema drift finding:\n{schema_drift_finding}\n\n"
        "Anomaly finding:\n{anomaly_finding}\n\n"
        "Determine the single most likely root_cause:\n"
        "- 'column_rename' if the schema drift finding shows a confident "
        "rename pair\n"
        "- 'unexpected_nulls' if the anomaly finding shows elevated null "
        "rates without a schema change\n"
        "- 'datetime_drift' if type_mismatch_examples mention date/time "
        "parsing issues\n"
        "- 'unknown' if neither finding is confident enough to act on\n\n"
        "Set severity based on how many downstream columns are affected. "
        "Set incident_id to the literal string 'PENDING' — the application "
        "will assign the real ID."
    ),
    before_agent_callback=on_agent_start,
    after_agent_callback=on_agent_end,
    after_model_callback=on_model_response,
    output_schema=Incident,
    output_key="incident",
)