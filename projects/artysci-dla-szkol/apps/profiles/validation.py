"""Schema check of a generated profile (US-2.5A). The hard rules and soft warnings of the
validator (US-2.5B) come later; here a reply is good when it matches the JSON Schema.

This file is the generator's `validator` component (registered in `generator_components.py`):
change it only together with a version bump there.
"""

import json
from functools import cache
from pathlib import Path

from django.conf import settings
from jsonschema import Draft202012Validator

SCHEMA_PATH = "apps/quality/schemas/profile.json"


@cache
def profile_schema() -> dict:
    return json.loads((Path(settings.BASE_DIR) / SCHEMA_PATH).read_text(encoding="utf-8"))


def schema_errors(data) -> list[str]:
    """One short line per violation: the JSON path and the keyword that failed. Never the
    offending value (it is reply text and must not reach logs or the database)."""
    validator = Draft202012Validator(profile_schema())
    errors = sorted(validator.iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path])
    lines = []
    for error in errors:
        path = "$" + "".join(
            f"[{p}]" if isinstance(p, int) else f".{p}" for p in error.absolute_path
        )
        lines.append(f"{path}: {error.validator}")
    return lines
