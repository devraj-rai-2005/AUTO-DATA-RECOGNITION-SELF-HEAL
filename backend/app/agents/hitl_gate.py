from google.adk.agents import LlmAgent
from google.adk.tools import LongRunningFunctionTool
from app.tools.approval import request_human_approval
from app.schemas.incident import HumanDecision

hitl_gate = LlmAgent(
    name="hitl_gate",
    model="gemini-3.1-flash-lite-preview",
    instruction=(
        "Incident {incident}, remediation {remediation}, dry-run result "
        "{dry_run_result}. Call request_human_approval with the "
        "incident_id, migration_sql, and a one-sentence dry_run_summary. "
        "Wait for the human's decision, then report it verbatim as "
        "HumanDecision — you make no approval judgment yourself, you only "
        "relay what the human decided."
    ),
    tools=[LongRunningFunctionTool(func=request_human_approval)],
    output_schema=HumanDecision,
    output_key="human_decision",
)