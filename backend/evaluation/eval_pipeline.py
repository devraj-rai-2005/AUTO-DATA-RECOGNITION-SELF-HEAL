import copy
from google.adk.agents import SequentialAgent
from app.agents.schema_drift_agent import schema_drift_agent
from app.agents.anomaly_validator_agent import anomaly_validator_agent
from app.agents.root_cause_agent import root_cause_agent

# Clone all agents required for diagnosis evaluation
eval_schema_drift = copy.deepcopy(schema_drift_agent)
eval_anomaly_validator = copy.deepcopy(anomaly_validator_agent)
eval_root_cause = copy.deepcopy(root_cause_agent)

# Clear parent_agent pointers on all cloned agents
for ag in [eval_schema_drift, eval_anomaly_validator, eval_root_cause]:
    if hasattr(ag, "parent_agent"):
        ag.parent_agent = None
    if hasattr(ag, "_parent_agent"):
        ag._parent_agent = None
    if hasattr(ag, "_parent"):
        ag._parent = None

# Build sequential evaluation triage team to avoid parallel burst rate limits
eval_triage_team = SequentialAgent(
    name="eval_triage_team",
    sub_agents=[eval_schema_drift, eval_anomaly_validator],
)

# Root evaluation pipeline
eval_pipeline = SequentialAgent(
    name="eval_incident_pipeline",
    sub_agents=[eval_triage_team, eval_root_cause],
)
