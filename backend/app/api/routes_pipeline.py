import uuid
from fastapi import APIRouter, Depends, HTTPException, Request  # <-- added Request
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import PipelineRun, AgentTrace
from app.services.failure_injector import reset_and_seed, FAILURE_INJECTORS
from app.services.job_queue import enqueue_run_pipeline
from app.schemas.api import TriggerRequest, TriggerResponse
from app.security.identifiers import validate_identifier
from app.security.api_key import require_api_key
from app.limiter import limiter  # <-- added limiter

router = APIRouter(prefix="/pipelines", tags=["pipelines"])

EXPECTED_COLUMNS = ["order_id", "customer_id", "order_date", "total_amount"]
EXPECTED_TYPES = {
    "order_id": "integer",
    "customer_id": "integer",
    "order_date": "date",
    "total_amount": "numeric",
}


@router.post(
    "/trigger",
    response_model=TriggerResponse,
    dependencies=[Depends(require_api_key)],
)
@limiter.limit("10/minute")  # <-- added rate limit decorator
async def trigger_pipeline(request: Request, req: TriggerRequest):  # <-- added request: Request
    # 1. SQL identifier safety check
    try:
        validate_identifier(req.table_name, "table_name")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Namespace safety check (sandbox tables only)
    if not req.table_name.startswith("customer_orders_") and not req.table_name.startswith("eval_"):
        raise HTTPException(
            status_code=400,
            detail="table_name must start with 'customer_orders_' or 'eval_' — this demo only manages its own sandbox tables",
        )

    if req.failure_type not in FAILURE_INJECTORS:
        raise HTTPException(400, f"Unknown failure_type: {req.failure_type}")

    await reset_and_seed(req.table_name)
    await FAILURE_INJECTORS[req.failure_type](req.table_name)

    run_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as db:
        db.add(PipelineRun(id=run_id, table_name=req.table_name, injected_failure=req.failure_type))
        await db.commit()

    await enqueue_run_pipeline(run_id, req.table_name, EXPECTED_COLUMNS, EXPECTED_TYPES)
    return TriggerResponse(run_id=run_id, status="running")


@router.get("/")
async def list_runs():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(PipelineRun).order_by(PipelineRun.created_at.desc()).limit(50))
        return result.scalars().all()


@router.get("/{run_id}")
async def get_run(run_id: str):
    async with AsyncSessionLocal() as db:
        run = await db.get(PipelineRun, run_id)
        if not run:
            raise HTTPException(404, "Run not found")
        return run


@router.get("/{run_id}/trace")
async def get_trace(run_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AgentTrace).where(AgentTrace.pipeline_run_id == run_id).order_by(AgentTrace.started_at)
        )
        return result.scalars().all()