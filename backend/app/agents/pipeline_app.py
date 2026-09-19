from google.adk.agents import App
from google.adk.apps import ResumabilityConfig
from app.agents.hitl_gate import hitl_gate

hitl_test_app = App(
    name="hitl_isolation_test",
    root_agent=hitl_gate,
    resumability_config=ResumabilityConfig(is_resumable=True),
)