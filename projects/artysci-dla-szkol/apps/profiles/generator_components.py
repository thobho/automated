"""The profile generator's registered components (US-2.5A, D5, D13): instructions, JSON Schema
and the validator slot, all v0.2. Imported by `ProfilesConfig.ready()`.

Changing a file below without bumping its version fails the registry test (`components.json`).
After a bump: `uv run python manage.py generator_manifest --write`.
"""

from apps.quality.registry import Component, registry

PROFILE_VERSION = "0.2"

INSTRUCTIONS = registry.register(
    Component(
        "instructions",
        "profile_draft",
        PROFILE_VERSION,
        files=("apps/profiles/prompts/profile_instructions.md",),
    )
)
SCHEMA = registry.register(
    Component("schema", "profile", PROFILE_VERSION, files=("apps/quality/schemas/profile.json",))
)
# Only the schema check for now; US-2.5B replaces this with the hard-rule validator.
VALIDATOR = registry.register(
    Component(
        "validator", "profile_checks", PROFILE_VERSION, files=("apps/profiles/validation.py",)
    )
)

COMPONENTS = (INSTRUCTIONS, SCHEMA, VALIDATOR)
