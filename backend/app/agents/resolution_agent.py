from google.adk.agents import LlmAgent
from app.tools.resolution import apply_resolution
from app.schemas.incident import Resolution
from app.observability.tracing import on_agent_start, on_agent_end, on_model_response

resolution_agent = LlmAgent(
    name="resolution_agent",
    model="gemini-3.1-flash-lite-preview",
    instruction=(
        "Incident {incident}, remediation {remediation}, human decision "
        "{human_decision}. Call apply_resolution with the incident_id, "
        "the remediation's migration_sql, and the human decision's "
        "approved flag and reviewer_notes. Report the result exactly as "
        "returned — do not editorialize about whether the decision was "
        "correct."
    ),
    before_agent_callback=on_agent_start,
    after_agent_callback=on_agent_end,
    after_model_callback=on_model_response,
    tools=[apply_resolution],
    output_schema=Resolution,
    output_key="resolution",
)