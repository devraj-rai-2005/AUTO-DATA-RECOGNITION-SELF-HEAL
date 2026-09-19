import logging
import uuid
from typing import Any
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import Incident as DBIncident, PipelineRun, AuditLog

logger = logging.getLogger("pipeline_healer.approval")


async def request_human_approval(
    incident_id: str,
    migration_sql: str,
    dry_run_summary: str,
    tool_context: Any = None,
) -> dict:
    """Persists the incident and dry-run report to PostgreSQL with status 'pending_review'.

    This allows the incident to appear on the frontend triage dashboard for human review.
    """
    logger.info(f"Triggering request_human_approval for incident: {incident_id}")

    # Extract state from tool_context if available
    state = getattr(tool_context, "state", {}) if tool_context else {}
    pipeline_run_id = state.get("pipeline_run_id") or incident_id

    # Fall back to incident / remediation / dry_run data in state if present
    incident_data = state.get("incident", {})
    remediation_data = state.get("remediation", {})
    dry_run_data = state.get("dry_run_result", {})

    actual_incident_id = (
        incident_id
        if incident_id and incident_id != "PENDING"
        else f"inc-{str(uuid.uuid4())[:8]}"
    )
    final_migration_sql = migration_sql or remediation_data.get("migration_sql", "")
    rollback_sql = remediation_data.get("rollback_sql", "")

    async with AsyncSessionLocal() as db:
        # Check if record already exists to avoid primary key duplicate conflicts
        existing = await db.get(DBIncident, actual_incident_id)
        if not existing:
            new_incident = DBIncident(
                id=actual_incident_id,
                pipeline_run_id=pipeline_run_id,
                root_cause=incident_data.get("root_cause", "column_rename"),
                affected_table=incident_data.get(
                    "affected_table", "customer_orders_live"
                ),
                severity=incident_data.get("severity", "high"),
                explanation=incident_data.get(
                    "explanation", "Automated incident detected by triage agents."
                ),
                migration_sql=final_migration_sql,
                rollback_sql=rollback_sql,
                status="pending_review",
                rows_before=dry_run_data.get("rows_before"),
                rows_after=dry_run_data.get("rows_after"),
                changed_sample=dry_run_data.get("changed_sample", []),
                dry_run_notes=dry_run_summary
                or dry_run_data.get("notes", "Dry run completed."),
            )
            db.add(new_incident)

        # Update PipelineRun status to awaiting_approval and save invocation info
        run_record = await db.get(PipelineRun, pipeline_run_id)
        if run_record:
            run_record.status = "awaiting_approval"
            if tool_context and hasattr(tool_context, "session_id"):
                run_record.adk_session_id = tool_context.session_id
            if tool_context and hasattr(tool_context, "invocation_id"):
                run_record.adk_invocation_id = tool_context.invocation_id

        # Add AuditLog
        db.add(
            AuditLog(
                incident_id=actual_incident_id,
                action="approval_requested",
                actor="system",
                notes=f"Generated remediation SQL awaiting human decision: {final_migration_sql[:80]}...",
            )
        )
        await db.commit()

    logger.info(
        f"Successfully persisted incident {actual_incident_id} to PostgreSQL with status 'pending_review'"
    )
    return {
        "status": "pending_review",
        "incident_id": actual_incident_id,
        "migration_sql": final_migration_sql,
        "dry_run_summary": dry_run_summary,
    }