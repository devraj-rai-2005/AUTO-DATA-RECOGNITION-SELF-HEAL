from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
import redis.asyncio as redis
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.db.session import engine
from app.limiter import limiter
from app.api import routes_pipeline, routes_incidents, routes_stream

app = FastAPI(title="Pipeline Healer")

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_pipeline.router)
app.include_router(routes_incidents.router)
app.include_router(routes_stream.router)


@app.get("/health")
async def health():
    checks = {"database": False, "redis": False}

    # 1. Check PostgreSQL connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass

    # 2. Check Redis connectivity
    try:
        r = redis.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
        checks["redis"] = True
    except Exception:
        pass

    healthy = all(checks.values())

    # Return 200 if fully healthy, or 503 Service Unavailable if degraded
    return JSONResponse(
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ok" if healthy else "degraded", "checks": checks},
    )