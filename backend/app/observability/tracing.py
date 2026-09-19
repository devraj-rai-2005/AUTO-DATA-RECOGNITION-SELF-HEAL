from datetime import datetime
from app.db.session import AsyncSessionLocal
from app.db.models import AgentTrace
from app.services.status_events import publish_status


def _is_eval(run_id: str | None) -> bool:
    return not run_id or run_id == "unknown" or run_id.startswith("eval")


async def on_agent_start(callback_context) -> None:
    run_id = callback_context.state.get("pipeline_run_id", "unknown")
    agent_name = callback_context.agent_name

    if _is_eval(run_id):
        return

    async with AsyncSessionLocal() as db:
        await db.merge(AgentTrace(
            id=f"{run_id}:{agent_name}",
            pipeline_run_id=run_id,
            agent_name=agent_name,
            started_at=datetime.utcnow(),
            status="started",
        ))
        await db.commit()
    await publish_status(run_id, agent_name, "started")


async def on_agent_end(callback_context) -> None:
    run_id = callback_context.state.get("pipeline_run_id", "unknown")
    agent_name = callback_context.agent_name

    if _is_eval(run_id):
        return

    async with AsyncSessionLocal() as db:
        trace = await db.get(AgentTrace, f"{run_id}:{agent_name}")
        if trace:
            trace.completed_at = datetime.utcnow()
            if trace.started_at:
                trace.duration_ms = int((trace.completed_at - trace.started_at).total_seconds() * 1000)
            trace.status = "completed"
            await db.commit()
    await publish_status(run_id, agent_name, "completed")


async def on_model_response(callback_context, llm_response=None) -> None:
    run_id = callback_context.state.get("pipeline_run_id", "unknown")
    agent_name = callback_context.agent_name

    if _is_eval(run_id):
        return

    # Optional token usage capture if available from the LLM response
    usage = getattr(llm_response, "usage_metadata", None) or getattr(llm_response, "usage", None)
    if not usage:
        return

    prompt_tokens = getattr(usage, "prompt_token_count", None) or getattr(usage, "prompt_tokens", None)
    completion_tokens = getattr(usage, "candidates_token_count", None) or getattr(usage, "completion_tokens", None)

    async with AsyncSessionLocal() as db:
        trace = await db.get(AgentTrace, f"{run_id}:{agent_name}")
        if trace:
            if prompt_tokens is not None:
                trace.prompt_tokens = (trace.prompt_tokens or 0) + prompt_tokens
            if completion_tokens is not None:
                trace.completion_tokens = (trace.completion_tokens or 0) + completion_tokens
            await db.commit()
