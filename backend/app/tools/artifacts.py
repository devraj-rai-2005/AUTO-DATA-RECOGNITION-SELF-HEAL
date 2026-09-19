import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("pipeline_healer.artifacts")

ARTIFACTS_DIR = Path("./data/artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


async def save_migration_artifacts(
    table_name: str,
    migration_sql: str,
    rollback_sql: str,
    tool_context: Any = None,
) -> dict[str, Any]:
    """Saves migration and rollback SQL for auditing and inspection."""
    filename_base = f"{table_name}_remediation"

    # Always persist locally to disk
    migration_path = ARTIFACTS_DIR / f"{filename_base}_migration.sql"
    rollback_path = ARTIFACTS_DIR / f"{filename_base}_rollback.sql"

    migration_path.write_text(migration_sql, encoding="utf-8")
    rollback_path.write_text(rollback_sql, encoding="utf-8")

    artifact_saved = False
    if tool_context and hasattr(tool_context, "save_artifact"):
        try:
            # ADK artifact save attempt
            await tool_context.save_artifact(
                f"{filename_base}_migration.sql",
                migration_sql.encode("utf-8"),
            )
            await tool_context.save_artifact(
                f"{filename_base}_rollback.sql",
                rollback_sql.encode("utf-8"),
            )
            artifact_saved = True
        except Exception as exc:
            logger.warning(
                f"ADK Artifact service failed ({exc}). Persisted locally to {ARTIFACTS_DIR} instead."
            )

    return {
        "status": "saved",
        "adk_artifact_service": artifact_saved,
        "migration_file": str(migration_path),
        "rollback_file": str(rollback_path),
    }