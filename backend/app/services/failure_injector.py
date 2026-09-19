import asyncpg
from datetime import date
from app.config import settings
from app.security.identifiers import validate_identifier


async def _conn():
    return await asyncpg.connect(dsn=settings.database_url.replace("+asyncpg", ""))


SAMPLE_ROWS = [
    (1, 101, date(2026, 1, 1), 150.00),
    (2, 102, date(2026, 1, 2), 200.50),
    (3, 103, date(2026, 1, 3), 99.99),
    (4, 104, date(2026, 1, 4), 320.00),
    (5, 105, date(2026, 1, 5), 45.00),
]


async def reset_and_seed(table_name: str):
    validate_identifier(table_name, "table_name")
    conn = await _conn()
    try:
        await conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        await conn.execute(
            f"""
            CREATE TABLE {table_name} (
                order_id INT,
                customer_id INT,
                order_date DATE,
                total_amount NUMERIC
            )
            """
        )
        await conn.executemany(
            f"INSERT INTO {table_name} (order_id, customer_id, order_date, total_amount) VALUES ($1, $2, $3, $4)",
            SAMPLE_ROWS,
        )
    finally:
        await conn.close()


async def inject_column_rename(table_name: str):
    validate_identifier(table_name, "table_name")
    conn = await _conn()
    try:
        await conn.execute(f"ALTER TABLE {table_name} RENAME COLUMN customer_id TO client_id")
    finally:
        await conn.close()


async def inject_unexpected_nulls(table_name: str):
    validate_identifier(table_name, "table_name")
    conn = await _conn()
    try:
        await conn.execute(f"UPDATE {table_name} SET total_amount = NULL WHERE order_id IN (2, 4)")
    finally:
        await conn.close()


async def inject_datetime_drift(table_name: str):
    validate_identifier(table_name, "table_name")
    conn = await _conn()
    try:
        await conn.execute(
            f"ALTER TABLE {table_name} ALTER COLUMN order_date TYPE TIMESTAMP WITHOUT TIME ZONE USING order_date::timestamp"
        )
    finally:
        await conn.close()


FAILURE_INJECTORS = {
    "column_rename": inject_column_rename,
    "unexpected_nulls": inject_unexpected_nulls,
    "datetime_drift": inject_datetime_drift,
}