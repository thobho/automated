import copy

import pytest

from apps.profiles import validation
from apps.profiles.generator_components import COMPONENTS, INSTRUCTIONS, SCHEMA, VALIDATOR
from apps.quality import registry as reg

from .factories import valid_profile

BLOCKS = {
    "hero", "facts", "description", "schools", "offers", "gallery", "testimonials", "faq",
    "theme", "seo", "gaps", "claims_audit",
}  # fmt: skip


def test_the_valid_sample_matches():
    assert validation.schema_errors(valid_profile()) == []


def test_the_schema_has_every_block_of_the_story():
    assert set(validation.profile_schema()["required"]) == BLOCKS


@pytest.mark.parametrize("block", sorted(BLOCKS))
def test_a_missing_block_is_reported(block):
    profile = valid_profile()
    del profile[block]
    assert validation.schema_errors(profile) == ["$: required"]


@pytest.mark.parametrize(
    "path, value, expected",
    [
        (("theme",), "neon", "$.theme: enum"),
        (("hero", "main_photo_id"), "abc", "$.hero.main_photo_id: type"),
        (("offers",), [{"offer_id": "x", "tagline": "t"}], "$.offers[0].offer_id: type"),
        (("extra",), 1, "$: additionalProperties"),
        (("claims_audit",), [{"claim": "c", "source": "web", "source_id": None}],
         "$.claims_audit[0].source: enum"),
    ],
)  # fmt: skip
def test_invalid_samples_are_reported_by_path_only(path, value, expected):
    profile = copy.deepcopy(valid_profile())
    target = profile
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    errors = validation.schema_errors(profile)
    assert errors == [expected]
    assert "neon" not in errors[0] and "abc" not in errors[0]


def test_a_non_object_reply_is_reported():
    assert validation.schema_errors([1]) == ["$: type"]


def test_the_components_are_registered_with_version_and_hash():
    registered = {c.key: c for c in reg.registry.all()}
    for component in COMPONENTS:
        assert registered[component.key] is component
        assert component.version == "0.2"
        assert len(component.content_hash) == 64
    assert (INSTRUCTIONS.kind, SCHEMA.kind, VALIDATOR.kind) == (
        "instructions",
        "schema",
        "validator",
    )


def test_the_manifest_records_the_v02_hashes():
    manifest = reg.load_manifest()
    assert reg.manifest_errors(COMPONENTS, manifest) == []
    for component in COMPONENTS:
        assert manifest[component.key]["0.2"] == component.content_hash


def test_a_changed_file_without_a_bump_fails_the_manifest(tmp_path):
    changed = reg.Component("schema", "profile", "0.2", files=(str(tmp_path / "s.json"),))
    (tmp_path / "s.json").write_text("{}")
    errors = reg.manifest_errors([changed], reg.load_manifest())
    assert errors and "changed without a version bump" in errors[0]


def test_the_instructions_mention_the_schema_blocks():
    text = INSTRUCTIONS.text()
    for block in BLOCKS:
        assert f"`{block}`" in text
