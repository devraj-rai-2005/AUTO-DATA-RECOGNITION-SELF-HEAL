from app.tools.migration_drafting import draft_migration_sql
from app.schemas.incident import Incident, SchemaDriftFinding


def test_rename_template_produces_symmetric_rollback():
    result = draft_migration_sql(
        root_cause="column_rename", table_name="orders",
        rename_pairs=[("order_date", "order_dt")], null_columns=[],
    )
    assert "RENAME COLUMN order_date TO order_dt" in result["migration_sql"]
    assert "RENAME COLUMN order_dt TO order_date" in result["rollback_sql"]  # rollback must exactly reverse it


def test_unexpected_nulls_template_has_no_automatic_rollback():
    result = draft_migration_sql(
        root_cause="unexpected_nulls", table_name="orders",
        rename_pairs=[], null_columns=["total_amount"],
    )
    assert "backfill" in result["rollback_sql"].lower() or "snapshot" in result["rollback_sql"].lower()


def test_unknown_root_cause_returns_no_template():
    result = draft_migration_sql(root_cause="unknown", table_name="orders", rename_pairs=[], null_columns=[])
    assert result["template_used"] == "none"


def test_incident_schema_rejects_invalid_root_cause():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Incident(
            incident_id="1", pipeline_run_id="1", root_cause="not_a_real_cause",
            affected_table="t", affected_columns=[], explanation="x", severity="low",
        )