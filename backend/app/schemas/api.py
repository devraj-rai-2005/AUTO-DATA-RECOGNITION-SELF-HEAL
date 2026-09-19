from pydantic import BaseModel
from typing import Literal


class TriggerRequest(BaseModel):
    table_name: str = "customer_orders_live"
    failure_type: Literal["column_rename", "unexpected_nulls", "datetime_drift"]


class TriggerResponse(BaseModel):
    run_id: str
    status: str


class DecisionRequest(BaseModel):
    approved: bool
    reviewer_notes: str = ""


class IncidentSummary(BaseModel):
    id: str
    pipeline_run_id: str
    root_cause: str
    affected_table: str
    severity: str
    status: str



class IncidentDetail(IncidentSummary):
    explanation: str
    migration_sql: str | None
    rollback_sql: str | None
    rows_before: int | None = None
    rows_after: int | None = None
    changed_sample: list[str] | None = None
    dry_run_notes: str | None = None