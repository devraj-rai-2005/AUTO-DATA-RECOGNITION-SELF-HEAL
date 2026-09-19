import asyncio
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from app.agents.pipeline_app import hitl_test_app

DB_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/pipeline_healer"


async def run_one_incident(runner, session_service, session_id, incident_state):
    await session_service.create_session(
        app_name="hitl_isolation_test", user_id="dev", session_id=session_id, state=incident_state
    )
    message = types.Content(role="user", parts=[types.Part(text="Please seek approval for this incident.")])

    pending_call_id = None
    invocation_id = None
    async for event in runner.run_async(user_id="dev", session_id=session_id, new_message=message):
        invocation_id = event.invocation_id
        for call in event.get_function_calls():
            if call.name == "request_human_approval":
                pending_call_id = call.id
        print(f"  event: author={event.author} final={event.is_final_response()}")

    assert pending_call_id, "Expected the run to pause on request_human_approval — it didn't."
    print(f"  PAUSED. invocation_id={invocation_id}, pending call={pending_call_id}")

    # Simulate the human clicking Approve, resuming the SAME invocation.
    decision_message = types.Content(
        role="user",
        parts=[types.Part(function_response=types.FunctionResponse(
            id=pending_call_id,
            name="request_human_approval",
            response={"status": "approved", "reviewer_notes": "Looks safe, backfill default is fine here."},
        ))],
    )
    async for event in runner.run_async(
        user_id="dev", session_id=session_id, new_message=decision_message, invocation_id=invocation_id
    ):
        if event.is_final_response():
            print("  RESUMED, final:", event.content.parts[0].text)


async def main():
    session_service = DatabaseSessionService(db_url=DB_URL)
    runner = Runner(app=hitl_test_app, session_service=session_service)

    print("=== First incident in this session ===")
    await run_one_incident(runner, session_service, "hitl-test-session", {
        "incident": {"incident_id": "inc-1", "affected_table": "t1"},
        "remediation": {"migration_sql": "-- test"},
        "dry_run_result": {"dry_run_succeeded": True},
    })

    print("\n=== Second incident, SAME session (this is the regression to watch for) ===")
    await run_one_incident(runner, session_service, "hitl-test-session", {
        "incident": {"incident_id": "inc-2", "affected_table": "t2"},
        "remediation": {"migration_sql": "-- test 2"},
        "dry_run_result": {"dry_run_succeeded": True},
    })


if __name__ == "__main__":
    asyncio.run(main())