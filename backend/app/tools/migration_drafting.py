def draft_migration_sql(
    root_cause: str,
    table_name: str,
    rename_pairs: list[tuple[str, str]],
    null_columns: list[str],
) -> dict:
    """Drafts a migration SQL statement and its rollback for a known,
    templated class of pipeline incident. Does NOT freely generate SQL —
    only fills in parameters for a small set of vetted templates. If the
    root cause doesn't match a known template, returns empty SQL and a
    note explaining why no automatic patch is possible.

    Args:
        root_cause: One of 'column_rename', 'unexpected_nulls', 'datetime_drift'.
        table_name: The affected staging table.
        rename_pairs: (old_name, new_name) pairs, used when root_cause is 'column_rename'.
        null_columns: Columns with unexpected NULLs, used when root_cause is 'unexpected_nulls'.

    Returns:
        A dict with 'migration_sql', 'rollback_sql', and 'template_used'.
    """
    if root_cause == "column_rename" and rename_pairs:
        migration = "\n".join(
            f"ALTER TABLE {table_name} RENAME COLUMN {old} TO {new};"
            for old, new in rename_pairs
        )
        rollback = "\n".join(
            f"ALTER TABLE {table_name} RENAME COLUMN {new} TO {old};"
            for old, new in rename_pairs
        )
        return {"migration_sql": migration, "rollback_sql": rollback, "template_used": "column_rename"}

    if root_cause == "unexpected_nulls" and null_columns:
        migration = "\n".join(
            f"UPDATE {table_name} SET {col} = 0 WHERE {col} IS NULL;  -- TEMPLATE DEFAULT: verify 0 is a safe backfill value"
            for col in null_columns
        )
        rollback = "-- No automatic rollback: backfilled NULLs cannot be distinguished from " \
                    "genuine zeros after the fact. Restore from pre-migration snapshot if needed."
        return {"migration_sql": migration, "rollback_sql": rollback, "template_used": "unexpected_nulls"}

    if root_cause == "datetime_drift":
        return {
            "migration_sql": "-- No safe generic template for datetime format drift yet.",
            "rollback_sql": "-- N/A",
            "template_used": "none",
        }

    return {
        "migration_sql": "-- No template available for this root cause.",
        "rollback_sql": "-- N/A",
        "template_used": "none",
    }