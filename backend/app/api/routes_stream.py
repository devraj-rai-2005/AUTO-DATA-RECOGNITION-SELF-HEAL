import asyncio
import json
import redis.asyncio as redis
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.config import settings

router = APIRouter(prefix="/pipelines", tags=["stream"])

TERMINAL_STATUSES = {"awaiting_approval", "resolved", "failed", "failed_no_incident"}


@router.get("/{run_id}/stream")
async def stream_run_events(run_id: str, request: Request):
    async def event_generator():
        client = redis.from_url(settings.redis_url)
        pubsub = client.pubsub()
        await pubsub.subscribe(f"run:{run_id}:events")
        try:
            while True:
                if await request.is_disconnected():
                    break

                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    # Yield the event to the client first
                    raw_data = message["data"]
                    if isinstance(raw_data, bytes):
                        raw_data = raw_data.decode("utf-8")

                    yield {"event": "agent_status", "data": raw_data}

                    # Check if this is a terminal pipeline event
                    try:
                        payload = json.loads(raw_data)
                        if (
                            payload.get("agent") == "pipeline"
                            and payload.get("status") in TERMINAL_STATUSES
                        ):
                            break
                    except (json.JSONDecodeError, TypeError):
                        pass

                await asyncio.sleep(0.1)
        finally:
            await pubsub.unsubscribe(f"run:{run_id}:events")
            await client.close()

    return EventSourceResponse(event_generator())