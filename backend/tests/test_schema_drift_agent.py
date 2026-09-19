import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.agents.schema_drift_agent import schema_drift_agent


async def main():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=schema_drift_agent,
        app_name="pipeline_healer_test",
        session_service=session_service,
    )
    session = await session_service.create_session(
        app_name="pipeline_healer_test", user_id="dev"
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=(
            "Table: customer_orders. "
            "Expected columns: order_id, customer_id, order_date, total_amount."
        ))],
    )

    async for event in runner.run_async(
        user_id="dev", session_id=session.id, new_message=message
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)

    final_session = await session_service.get_session(
        app_name="pipeline_healer_test", user_id="dev", session_id=session.id
    )
    print("State:", final_session.state.get("schema_drift_finding"))


if __name__ == "__main__":
    asyncio.run(main())