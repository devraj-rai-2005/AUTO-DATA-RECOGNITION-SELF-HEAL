from google.adk.agents import LlmAgent
from app.tools.data_profiling import profile_nulls_and_types
from app.schemas.incident import AnomalyFinding
from app.observability.tracing import on_agent_start, on_agent_end, on_model_response

anomaly_validator_agent = LlmAgent(
    name="anomaly_validator_agent",
    model="gemini-3.1-flash-lite-preview",
    instruction=(
        "You are a data pipeline anomaly validator. You will be told a table "
        "name and the expected Postgres type for each column. Call "
        "profile_nulls_and_types to check for unexpected NULLs and type "
        "mismatches. A null rate above 5% in a column that previously had "
        "none is worth flagging even if it isn't catastrophic. Be "
        "conservative with confidence — only report high confidence when "
        "the evidence is unambiguous."
    ),
    before_agent_callback=on_agent_start,
    after_agent_callback=on_agent_end,
    after_model_callback=on_model_response,
    tools=[profile_nulls_and_types],
    output_schema=AnomalyFinding,
    output_key="anomaly_finding",
)

