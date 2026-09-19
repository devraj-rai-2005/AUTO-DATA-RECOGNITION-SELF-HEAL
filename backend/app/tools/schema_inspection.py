import asyncpg
from app.config import settings
from app.security.identifiers import validate_identifier


async def _conn():
    return await asyncpg.connect(dsn=settings.database_url.replace("+asyncpg", ""))


async def inspect_schema_diff(table_name: str, expected_columns: list[str]) -> dict:
    """Compares the actual columns of a staging table against the expected
    schema and reports any columns that are missing, extra, or possibly renamed.
    """
    validate_identifier(table_name, "table_name")
    for col in expected_columns:
        validate_identifier(col, "column_name")

    conn = await _conn()
    try:
        rows = await conn.fetch(
            "SELECT column_name FROM information_schema.columns WHERE table_name = $1",
            table_name,
        )
        actual_columns = [r["column_name"] for r in rows]
    finally:
        await conn.close()

    missing = [c for c in expected_columns if c not in actual_columns]
    extra = [c for c in actual_columns if c not in expected_columns]

    possible_renames = []
    for m in missing:
        for e in extra:
            if (
                m.lower().replace("_", "") in e.lower().replace("_", "")
                or e.lower().replace("_", "") in m.lower().replace("_", "")
            ):
                possible_renames.append((m, e))

    return {
        "actual_columns": actual_columns,
        "missing_columns": missing,
        "extra_columns": extra,
        "possible_renames": possible_renames,
    }