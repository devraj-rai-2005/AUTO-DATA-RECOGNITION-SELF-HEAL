from dataclasses import dataclass
from app.services.failure_injector import (
    reset_and_seed, inject_column_rename, inject_unexpected_nulls, inject_datetime_drift,
)

DESCRIPTION_TEMPLATE = (
    "Table: {table}. Expected columns: order_id, customer_id, order_date, total_amount. "
    "Expected types: order_id=integer, customer_id=integer, order_date=date, total_amount=numeric."
)


@dataclass
class EvalCase:
    name: str
    table: str
    expected_root_cause: str
    setup: callable  # async fn(table_name) -> None


async def _setup_clean(table): await reset_and_seed(table)
async def _setup_rename(table):
    await reset_and_seed(table)
    await inject_column_rename(table)
async def _setup_nulls(table):
    await reset_and_seed(table)
    await inject_unexpected_nulls(table)
async def _setup_drift(table):
    await reset_and_seed(table)
    await inject_datetime_drift(table)


EVAL_CASES = [
    EvalCase("rename_1", "eval_rename_1", "column_rename", _setup_rename),
    EvalCase("rename_2", "eval_rename_2", "column_rename", _setup_rename),
    EvalCase("nulls_1", "eval_nulls_1", "unexpected_nulls", _setup_nulls),
    EvalCase("nulls_2", "eval_nulls_2", "unexpected_nulls", _setup_nulls),
    EvalCase("drift_1", "eval_drift_1", "datetime_drift", _setup_drift),
    EvalCase("clean_1", "eval_clean_1", "unknown", _setup_clean),
    EvalCase("clean_2", "eval_clean_2", "unknown", _setup_clean),
]