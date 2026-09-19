import asyncpg
from app.config import settings
from app.security.identifiers import validate_identifier
from app.security.sql_guardrail import validate_migration_shape


async def _conn():
    return await asyncpg.connect(dsn=settings.database_url.replace("+asyncpg", ""))


async def apply_resolution(
    incident_id: str,
    migration_sql: str,
    approved: bool,
    reviewer_notes: str,
) -> dict:
    """Applies an approved migration to the real Postgres staging schema, or
    records a rejection without touching production data.
    """
    if not approved:
        return {"applied": False, "status": "rejected", "note": reviewer_notes}

    validate_migration_shape(migration_sql)

    conn = await _conn()
    try:
        for statement in migration_sql.split(";"):
            statement = statement.split("--")[0].strip()
            if statement:
                await conn.execute(statement)
    finally:
        await conn.close()

    return {"applied": True, "status": "applied", "note": reviewer_notes}