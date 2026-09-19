from pydantic import BaseModel, Field
from typing import Literal


class SchemaDriftFinding(BaseModel):
    """Output of the Schema Drift Analyzer agent."""
    drift_detected: bool
    changed_columns: list[str] = Field(
        default_factory=list,
        description="Columns present in the incoming batch but absent from, "
                    "or renamed relative to, the expected staging schema."
    )
    likely_rename_pairs: list[list[str]] = Field(
        default_factory=list,
        description="Best-guess [old_name, new_name] pairs when a rename is suspected."
    )
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str


class AnomalyFinding(BaseModel):
    """Output of the Null/Type Anomaly Validator agent."""
    anomaly_detected: bool
    affected_columns: list[str] = Field(default_factory=list)
    null_rate_by_column: dict[str, float] = Field(default_factory=dict)
    type_mismatch_examples: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str


class Incident(BaseModel):
    """Root Cause Agent's synthesized output — the shared incident record."""
    incident_id: str
    pipeline_run_id: str
    root_cause: Literal["column_rename", "unexpected_nulls", "datetime_drift", "unknown"]
    affected_table: str
    affected_columns: list[str]
    explanation: str
    rename_pairs: list[list[str]] = Field(default_factory=list)
    null_columns: list[str] = Field(default_factory=list)
    severity: Literal["low", "medium", "high"]


class Remediation(BaseModel):
    """Patch Generation Agent's output."""
    incident_id: str
    migration_sql: str
    rollback_sql: str
    risk_notes: str


class DryRunResult(BaseModel):
    incident_id: str
    rows_before: int
    rows_after: int | None
    changed_sample: list[str]
    dry_run_succeeded: bool
    notes: str


class HumanDecision(BaseModel):
    incident_id: str
    approved: bool
    reviewer_notes: str


class Resolution(BaseModel):
    incident_id: str
    applied: bool
    status: Literal["applied", "rejected"]
    note: str