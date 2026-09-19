import json
import redis.asyncio as redis
from app.config import settings

_redis = redis.from_url(settings.redis_url)


async def publish_status(run_id: str, agent_name: str, status: str, detail: str = "") -> None:
    payload = json.dumps({"agent": agent_name, "status": status, "detail": detail})
    await _redis.publish(f"run:{run_id}:events", payload)