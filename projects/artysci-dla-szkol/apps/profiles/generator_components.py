"""The profile generator's registered components (US-2.5A, D5, D13): instructions, JSON Schema
and the validator slot, all v0.2. Imported by `ProfilesConfig.ready()`.

Changing a file below without bumping its version fails the registry test (`components.json`).
After a bump: `uv run python manage.py generator_manifest --write`.
"""

from apps.quality.registry import Component, registry

PROFILE_VERSION = "0.2"

# v0.3 adds the repair task (US-2.5C); the schema stays v0.2.
INSTRUCTIONS_VERSION = "0.3"
INSTRUCTIONS = registry.register(
    Component(
        "instructions",
        "profile_draft",
        INSTRUCTIONS_VERSION,
        files=("apps/profiles/prompts/profile_instructions.md",),
    )
)
SCHEMA = registry.register(
    Component("schema", "profile", PROFILE_VERSION, files=("apps/quality/schemas/profile.json",))
)
# Schema check plus the hard-rule validator (US-2.5B). Its own version: v0.1 is the first
# validator with hard rules; the 0.2 entry of the schema-only file stays in the manifest.
VALIDATOR_VERSION = "0.1"
VALIDATOR = registry.register(
    Component(
        "validator",
        "profile_checks",
        VALIDATOR_VERSION,
        files=("apps/profiles/validation.py", "apps/profiles/validator.py"),
    )
)

COMPONENTS = (INSTRUCTIONS, SCHEMA, VALIDATOR)
