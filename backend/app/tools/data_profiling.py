import asyncpg
from typing import Any
from app.config import settings
from app.security.identifiers import validate_identifier


async def _conn():
    return await asyncpg.connect(dsn=settings.database_url.replace("+asyncpg", ""))


async def profile_nulls_and_types(
    table_name: str, expected_columns: list[str]
) -> dict[str, Any]:
    """Profiles the table for null counts and column types.

    Safely handles columns that might be missing or renamed due to drift.
    """
    validate_identifier(table_name, "table_name")
    conn = await _conn()

    try:
        # 1. Fetch the actual existing columns in the table
        actual_cols_records = await conn.fetch(
            """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = $1
            """,
            table_name,
        )
        actual_cols = {r["column_name"]: r["data_type"] for r in actual_cols_records}

        column_stats = {}

        for col in expected_columns:
            validate_identifier(col, "column_name")

            if col not in actual_cols:
                column_stats[col] = {
                    "exists": False,
                    "error": "Column not found in table (possible rename or drop)",
                    "null_count": None,
                    "actual_type": None,
                }
                continue

            try:
                # 2. Check null counts safely for columns that actually exist
                null_count = await conn.fetchval(
                    f'SELECT count(*) FROM "{table_name}" WHERE "{col}" IS NULL'
                )
                column_stats[col] = {
                    "exists": True,
                    "null_count": null_count,
                    "actual_type": actual_cols[col],
                }
            except asyncpg.exceptions.UndefinedColumnError:
                column_stats[col] = {
                    "exists": False,
                    "error": "UndefinedColumnError",
                    "null_count": None,
                    "actual_type": None,
                }

        # 3. Also capture any new/unexpected columns present in the table
        unexpected_columns = [c for c in actual_cols if c not in expected_columns]

        return {
            "table_name": table_name,
            "column_stats": column_stats,
            "actual_columns": list(actual_cols.keys()),
            "unexpected_columns": unexpected_columns,
        }

    finally:
        await conn.close()