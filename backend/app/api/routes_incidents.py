from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import Incident, PipelineRun, AuditLog
from app.services.job_queue import enqueue_resume_pipeline
from app.schemas.api import DecisionRequest, IncidentSummary, IncidentDetail
from app.security.api_key import require_api_key

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("/", response_model=list[IncidentSummary])
async def list_incidents():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Incident).order_by(Incident.pipeline_run_id.desc()))
        return result.scalars().all()


@router.get("/{incident_id}", response_model=IncidentDetail)
async def get_incident(incident_id: str):
    async with AsyncSessionLocal() as db:
        incident = await db.get(Incident, incident_id)
        if not incident:
            raise HTTPException(404, "Incident not found")
        return incident


@router.post(
    "/{incident_id}/decision",
    dependencies=[Depends(require_api_key)],
)
async def decide_incident(incident_id: str, decision: DecisionRequest):
    async with AsyncSessionLocal() as db:
        incident = await db.get(Incident, incident_id)
        if not incident:
            raise HTTPException(404, "Incident not found")
        if incident.status != "pending_review":
            raise HTTPException(409, f"Incident already {incident.status}, cannot decide again")

        run = await db.get(PipelineRun, incident.pipeline_run_id)
        if not run or not run.adk_session_id or not run.adk_invocation_id:
            raise HTTPException(409, "Run has no paused invocation to resume")

        incident.status = "approved" if decision.approved else "rejected"
        db.add(
            AuditLog(
                incident_id=incident_id,
                action="decision_submitted",
                actor="human_reviewer",
                notes=decision.reviewer_notes,
            )
        )
        await db.commit()

    await enqueue_resume_pipeline(
        run.pipeline_run_id if hasattr(run, "pipeline_run_id") else run.id,
        run.adk_session_id,
        run.adk_invocation_id,
        {"status": "approved" if decision.approved else "rejected", "reviewer_notes": decision.reviewer_notes},
    )
    return {"status": "decision_submitted"}