from google.adk.apps import App
from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.apps import ResumabilityConfig
from app.agents.schema_drift_agent import schema_drift_agent
from app.agents.anomaly_validator_agent import anomaly_validator_agent
from app.agents.root_cause_agent import root_cause_agent
from app.agents.patch_generation_agent import patch_generation_agent
from app.agents.sandbox_dryrun_agent import sandbox_dryrun_agent
from app.agents.hitl_gate import hitl_gate
from app.agents.resolution_agent import resolution_agent

triage_team = ParallelAgent(
    name="triage_team",
    sub_agents=[schema_drift_agent, anomaly_validator_agent],
)

incident_pipeline = SequentialAgent(
    name="incident_pipeline",
    sub_agents=[
        triage_team,
        root_cause_agent,
        patch_generation_agent,
        sandbox_dryrun_agent,
        hitl_gate,
        resolution_agent,
    ],
)

pipeline_app = App(
    name="pipeline_healer",
    root_agent=incident_pipeline,
    resumability_config=ResumabilityConfig(is_resumable=True),
)