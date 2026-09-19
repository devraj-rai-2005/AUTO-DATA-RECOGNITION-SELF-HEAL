import re

# These patterns intentionally mirror ONLY what draft_migration_sql's
# templates can produce (Phase 3). Anything outside this shape gets
# rejected here even if a human approved it — approval means "yes, apply
# the reviewed patch," not "yes, run arbitrary SQL I was shown a diff of."
_ALLOWED_PATTERNS = [
    re.compile(r"^ALTER TABLE [a-z][a-z0-9_]* RENAME COLUMN [a-z][a-z0-9_]* TO [a-z][a-z0-9_]*;?$", re.IGNORECASE),
    re.compile(r"^UPDATE [a-z][a-z0-9_]* SET [a-z][a-z0-9_]* = 0 WHERE [a-z][a-z0-9_]* IS NULL;?.*$", re.IGNORECASE),
]


def validate_migration_shape(migration_sql: str) -> None:
    """Raises ValueError if migration_sql doesn't match one of the known
    safe templates. Called immediately before execution against real
    Postgres — the last line of defense before a human approval actually
    results in a database mutation."""
    statements = [s.split("--")[0].strip() for s in migration_sql.split("\n") if s.strip() and not s.strip().startswith("--")]
    for stmt in statements:
        if not any(p.match(stmt) for p in _ALLOWED_PATTERNS):
            raise ValueError(f"Migration statement doesn't match an approved template shape: {stmt!r}")