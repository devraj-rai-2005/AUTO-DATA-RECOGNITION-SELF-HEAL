from arq import create_pool
from arq.connections import RedisSettings
from app.config import settings


async def get_redis_pool():
    return await create_pool(RedisSettings.from_dsn(settings.redis_url))


async def enqueue_run_pipeline(run_id: str, table_name: str, expected_columns: list[str], expected_types: dict) -> None:
    pool = await get_redis_pool()
    await pool.enqueue_job("run_pipeline_job", run_id, table_name, expected_columns, expected_types)


async def enqueue_resume_pipeline(run_id: str, session_id: str, invocation_id: str, decision: dict) -> None:
    pool = await get_redis_pool()
    await pool.enqueue_job("resume_pipeline_job", run_id, session_id, invocation_id, decision)