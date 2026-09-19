import re

# Table names in this system only ever come from two places: the failure
# injector (which creates them) and requests to the /pipelines/trigger
# endpoint (which choose a name for a NEW table to create). This pattern
# is deliberately strict — it's not trying to allow "any valid Postgres
# identifier," it's trying to allow only what this app actually needs.
_SAFE_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]{0,62}$")


def validate_identifier(name: str, kind: str = "identifier") -> str:
    """Raises ValueError if `name` isn't a safe SQL identifier for this app.
    Use this on every table_name or column_name before it touches a query
    string, even ones that only ever come from "trusted" internal callers —
    the LLM-facing tools are exactly the callers this exists to protect
    against, since their inputs originate from model output.
    """
    if not _SAFE_IDENTIFIER.match(name):
        raise ValueError(f"Unsafe {kind}: {name!r}")
    return name