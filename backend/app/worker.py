import logging
from arq.connections import RedisSettings
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.errors.already_exists_error import AlreadyExistsError
from google.genai import types

from app.observability.logging_config import configure_logging, run_id_var
from app.config import settings
from app.agents.pipeline import pipeline_app
from app.db.session import AsyncSessionLocal
from app.db.models import PipelineRun, Incident, AuditLog
from app.services.status_events import publish_status

logger = logging.getLogger("pipeline_healer.worker")

session_service = DatabaseSessionService(db_url=settings.adk_session_service_uri)
runner = Runner(app=pipeline_app, session_service=session_service)


async def run_pipeline_job(
    ctx,
    run_id: str,
    table_name: str,
    expected_columns: list[str],
    expected_types: dict,
) -> None:
    run_id_var.set(run_id)
    logger.info(f"Starting pipeline run for table={table_name}")

    try:
        session_id = f"run-{run_id}"

        # Idempotent session creation
        try:
            await session_service.create_session(
                app_name="pipeline_healer",
                user_id="system",
                session_id=session_id,
                state={"pipeline_run_id": run_id},
            )
        except AlreadyExistsError:
            logger.info(f"Session {session_id} already exists. Resuming existing session.")
            await session_service.get_session(
                app_name="pipeline_healer", user_id="system", session_id=session_id
            )

        message = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=(
                        f"Table: {table_name}. Expected columns: {', '.join(expected_columns)}. "
                        f"Expected types: {expected_types}."
                    )
                )
            ],
        )

        pending_call_id, invocation_id = None, None
        async for event in runner.run_async(
            user_id="system", session_id=session_id, new_message=message
        ):
            invocation_id = event.invocation_id
            for call in event.get_function_calls():
                if call.name == "request_human_approval":
                    pending_call_id = call.id

        final_session = await session_service.get_session(
            app_name="pipeline_healer", user_id="system", session_id=session_id
        )
        incident_data = final_session.state.get("incident")

        async with AsyncSessionLocal() as db:
            run = await db.get(PipelineRun, run_id)
            if run:
                run.adk_session_id = session_id
                run.adk_invocation_id = invocation_id
                run.status = (
                    "awaiting_approval" if pending_call_id else "failed_no_incident"
                )

            if incident_data:
                remediation = final_session.state.get("remediation", {})
                dry_run = final_session.state.get("dry_run_result", {})

                incident = Incident(
                    id=incident_data["incident_id"],
                    pipeline_run_id=run_id,
                    root_cause=incident_data["root_cause"],
                    affected_table=incident_data["affected_table"],
                    severity=incident_data["severity"],
                    explanation=incident_data["explanation"],
                    migration_sql=remediation.get("migration_sql"),
                    rollback_sql=remediation.get("rollback_sql"),
                    rows_before=dry_run.get("rows_before"),
                    rows_after=dry_run.get("rows_after"),
                    changed_sample=dry_run.get("changed_sample", []),
                    dry_run_notes=dry_run.get("notes"),
                )
                db.add(incident)
                db.add(
                    AuditLog(
                        incident_id=incident.id,
                        action="created",
                        actor="system",
                        notes="Incident detected and remediation drafted.",
                    )
                )
            await db.commit()

        await publish_status(
            run_id,
            "pipeline",
            "awaiting_approval" if pending_call_id else "failed_no_incident",
        )

    except Exception:
        logger.exception("Pipeline run failed")
        async with AsyncSessionLocal() as db:
            run = await db.get(PipelineRun, run_id)
            if run:
                run.status = "failed"
                await db.commit()
        await publish_status(
            run_id,
            "pipeline",
            "failed",
            "Unhandled exception — check server logs",
        )
        raise


async def resume_pipeline_job(
    ctx, run_id: str, session_id: str, invocation_id: str, decision: dict
) -> None:
    run_id_var.set(run_id)

    try:
        session = await session_service.get_session(
            app_name="pipeline_healer", user_id="system", session_id=session_id
        )
        pending_call_id = None
        for event in reversed(session.events):
            for call in event.get_function_calls():
                if call.name == "request_human_approval":
                    pending_call_id = call.id
                    break
            if pending_call_id:
                break

        decision_message = types.Content(
            role="user",
            parts=[
                types.Part(
                    function_response=types.FunctionResponse(
                        id=pending_call_id,
                        name="request_human_approval",
                        response=decision,
                    )
                )
            ],
        )
        async for _ in runner.run_async(
            user_id="system",
            session_id=session_id,
            new_message=decision_message,
            invocation_id=invocation_id,
        ):
            pass

        final_session = await session_service.get_session(
            app_name="pipeline_healer", user_id="system", session_id=session_id
        )
        resolution = final_session.state.get("resolution", {})
        incident_data = final_session.state.get("incident", {})

        async with AsyncSessionLocal() as db:
            run = await db.get(PipelineRun, run_id)
            if run:
                run.status = "resolved"
            incident = await db.get(Incident, incident_data.get("incident_id"))
            if incident:
                incident.status = resolution.get("status", "unknown")
                db.add(
                    AuditLog(
                        incident_id=incident.id,
                        action=resolution.get("status", "unknown"),
                        actor="human_reviewer",
                        notes=decision.get("reviewer_notes", ""),
                    )
                )
            await db.commit()

        await publish_status(run_id, "pipeline", "resolved")

    except Exception:
        logger.exception("Resume failed")
        await publish_status(
            run_id,
            "pipeline",
            "failed",
            "Resume error — check server logs",
        )
        raise


async def startup(ctx):
    configure_logging(settings.log_level)


class WorkerSettings:
    functions = [run_pipeline_job, resume_pipeline_job]
    on_startup = startup
    redis_settings = RedisSettings.from_dsn(settings.redis_url)