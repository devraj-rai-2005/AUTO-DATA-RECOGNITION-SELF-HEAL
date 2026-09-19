import asyncio
import uuid
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.agents.pipeline import incident_pipeline_partial


async def run_case(table: str, description: str):
    session_service = InMemorySessionService()
    runner = Runner(
        agent=incident_pipeline_partial,
        app_name="pipeline_healer_test",
        session_service=session_service,
    )
    run_id = str(uuid.uuid4())
    session = await session_service.create_session(
        app_name="pipeline_healer_test",
        user_id="dev",
        state={"pipeline_run_id": run_id},
    )

    message = types.Content(role="user", parts=[types.Part(text=description)])

    async for event in runner.run_async(user_id="dev", session_id=session.id, new_message=message):
        if event.is_final_response():
            print(f"  [{event.author}] responded")

    final_session = await session_service.get_session(
        app_name="pipeline_healer_test", user_id="dev", session_id=session.id
    )
    incident = final_session.state.get("incident")
    if incident:
        incident["incident_id"] = str(uuid.uuid4())
        incident["pipeline_run_id"] = run_id
    print(f"\n=== {table} ===")
    print("schema_drift_finding:", final_session.state.get("schema_drift_finding"))
    print("anomaly_finding:", final_session.state.get("anomaly_finding"))
    print("incident:", incident)


async def main():
    # Run all three so you can see how root_cause_agent behaves differently
    # per scenario — not just whether one case works.
    await run_case("customer_orders_renamed", "Table: customer_orders_renamed. Expected columns: order_id, customer_id, order_date, total_amount. Expected types: order_id=integer, customer_id=integer, order_date=date, total_amount=numeric.")
    await run_case("customer_orders_nulls", "Table: customer_orders_nulls. Expected columns: order_id, customer_id, order_date, total_amount. Expected types: order_id=integer, customer_id=integer, order_date=date, total_amount=numeric.")
    await run_case("customer_orders_clean", "Table: customer_orders_clean. Expected columns: order_id, customer_id, order_date, total_amount. Expected types: order_id=integer, customer_id=integer, order_date=date, total_amount=numeric.")


if __name__ == "__main__":
    asyncio.run(main())