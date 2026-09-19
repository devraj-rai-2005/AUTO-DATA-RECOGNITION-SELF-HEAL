import duckdb
import asyncpg
from app.config import settings
from app.security.identifiers import validate_identifier


async def _conn():
    return await asyncpg.connect(dsn=settings.database_url.replace("+asyncpg", ""))


async def run_duckdb_dryrun(table_name: str, migration_sql: str) -> dict:
    """Clones the current snapshot of a Postgres staging table into an
    isolated, in-memory DuckDB instance, applies the proposed migration
    there, and reports before/after row counts and affected-row samples.
    """
    validate_identifier(table_name, "table_name")

    conn = await _conn()
    try:
        rows = await conn.fetch(f"SELECT * FROM {table_name}")
    finally:
        await conn.close()

    records = [dict(r) for r in rows]
    ddb = duckdb.connect(database=":memory:")
    ddb.register("snapshot_df", records)
    ddb.execute(f"CREATE TABLE {table_name} AS SELECT * FROM snapshot_df")

    rows_before = ddb.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

    try:
        for statement in migration_sql.split(";"):
            statement = statement.split("--")[0].strip()
            if statement:
                ddb.execute(statement)
    except Exception as e:
        return {
            "rows_before": rows_before,
            "rows_after": None,
            "rows_changed_sample": [],
            "error": str(e),
        }

    rows_after = ddb.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    sample = ddb.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchall()

    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_changed_sample": [str(r) for r in sample],
        "error": None,
    }