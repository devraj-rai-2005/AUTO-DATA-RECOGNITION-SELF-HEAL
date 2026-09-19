# backend/tests/test_worker_e2e.py
import asyncio, uuid
from app.db.session import AsyncSessionLocal
from app.db.models import PipelineRun
from app.services.job_queue import enqueue_run_pipeline, enqueue_resume_pipeline

async def main():
    run_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as db:
        db.add(PipelineRun(id=run_id, table_name="customer_orders_renamed", injected_failure="column_rename"))
        await db.commit()

    await enqueue_run_pipeline(
        run_id, "customer_orders_renamed",
        ["order_id", "customer_id", "order_date", "total_amount"],
        {"order_id": "integer", "customer_id": "integer", "order_date": "date", "total_amount": "numeric"},
    )
    print(f"Enqueued run {run_id} — watch the arq worker terminal, then check the incident row.")
    # Once status flips to awaiting_approval, grab adk_session_id/adk_invocation_id
    # and the incident id from Postgres, then call:
    # await enqueue_resume_pipeline(run_id, session_id, invocation_id, {"status": "approved", "reviewer_notes": "test"})

if __name__ == "__main__":
    asyncio.run(main())