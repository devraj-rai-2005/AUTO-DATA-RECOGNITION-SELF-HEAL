from google.adk.agents import LlmAgent
from app.tools.schema_inspection import inspect_schema_diff
from app.schemas.incident import SchemaDriftFinding
from app.observability.tracing import on_agent_start, on_agent_end, on_model_response



schema_drift_agent = LlmAgent(
    name="schema_drift_agent",
    model="gemini-3.1-flash-lite-preview",
    instruction=(
        "You are a data pipeline schema drift analyzer. You will be told a "
        "table name and its expected columns. Call inspect_schema_diff to check "
        "the actual schema. If columns are missing, use the possible_renames "
        "field to judge whether this looks like a rename versus a genuine "
        "removed column. Be conservative with confidence — only report high "
        "confidence when the rename mapping is unambiguous."
    ),
    
    before_agent_callback=on_agent_start,
    after_agent_callback=on_agent_end,
    after_model_callback=on_model_response,
    tools=[inspect_schema_diff],
    output_schema=SchemaDriftFinding,
    output_key="schema_drift_finding",
)
