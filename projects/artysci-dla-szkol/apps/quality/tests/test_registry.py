import json

import pytest
from django.core.management import CommandError, call_command

from apps.quality import registry as reg
from apps.quality.registry import Component, Registry, RegistryError


def test_every_registered_component_matches_the_manifest():
    """The guard of D13/D14: a content change without a version bump fails here."""
    errors = reg.manifest_errors(reg.registry.all(), reg.load_manifest())
    assert not errors, "\n".join(errors)


@pytest.fixture
def prompt_file(tmp_path):
    path = tmp_path / "prompt.md"
    path.write_text("Napisz opis.", encoding="utf-8")
    return path


def test_changed_content_without_bump_fails_naming_the_component(prompt_file):
    component = Component("instructions", "draft", "1", files=(str(prompt_file),))
    manifest = reg.updated_manifest([component], {})
    assert reg.manifest_errors([component], manifest) == []

    prompt_file.write_text("Napisz dłuższy opis.", encoding="utf-8")
    errors = reg.manifest_errors([component], manifest)
    assert len(errors) == 1
    assert "instructions:draft v1 changed without a version bump" in errors[0]
    with pytest.raises(RegistryError, match="instructions:draft"):
        reg.updated_manifest([component], manifest)

    bumped = Component("instructions", "draft", "2", files=(str(prompt_file),))
    assert "not in the manifest" in reg.manifest_errors([bumped], manifest)[0]
    manifest = reg.updated_manifest([bumped], manifest)
    assert reg.manifest_errors([bumped], manifest) == []
    assert set(manifest["instructions:draft"]) == {"1", "2"}  # the old version stays recorded


def test_hash_covers_file_names_and_order(tmp_path):
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text("x")
    b.write_text("y")
    ab = Component("template", "page", "1", files=(str(a), str(b))).content_hash
    ba = Component("template", "page", "1", files=(str(b), str(a))).content_hash
    assert ab != ba
    inline = Component("template", "page", "1", content="x").content_hash
    assert len({ab, ba, inline}) == 3


def test_relative_files_resolve_from_the_project_folder():
    component = Component("validator", "v", "1", files=("apps/quality/registry.py",))
    assert component.text().startswith("=== apps/quality/registry.py\n")
    assert len(component.content_hash) == 64


@pytest.mark.parametrize(
    "kwargs",
    [
        {"kind": "prompt", "name": "x", "version": "1", "content": "a"},
        {"kind": "schema", "name": "", "version": "1", "content": "a"},
        {"kind": "schema", "name": "x", "version": "", "content": "a"},
        {"kind": "schema", "name": "x", "version": "1"},
        {"kind": "schema", "name": "x", "version": "1", "content": "a", "files": ("f",)},
    ],
)
def test_invalid_component_is_refused(kwargs):
    with pytest.raises(RegistryError):
        Component(**kwargs)


def test_registry_refuses_two_versions_of_one_component():
    registry = Registry()
    one = registry.register(Component("schema", "s", "1", content="{}"))
    assert registry.register(Component("schema", "s", "1", content="{}")) == one
    with pytest.raises(RegistryError, match="already registered"):
        registry.register(Component("schema", "s", "2", content="{}"))
    assert registry.get("schema", "s") is one
    assert registry.all() == [one]
    with pytest.raises(RegistryError):
        registry.get("schema", "other")


def test_manifest_round_trip(tmp_path):
    path = tmp_path / "components.json"
    assert reg.load_manifest(path) == {}
    reg.write_manifest({"schema:s": {"1": "abc"}}, path)
    assert reg.load_manifest(path) == {"schema:s": {"1": "abc"}}


@pytest.fixture
def temp_registry(tmp_path, monkeypatch):
    registry = Registry()
    monkeypatch.setattr(reg, "registry", registry)
    monkeypatch.setattr(reg, "MANIFEST_PATH", tmp_path / "components.json")
    return registry, tmp_path / "components.json"


def test_generator_manifest_command(temp_registry, capsys):
    registry, path = temp_registry
    registry.register(Component("schema", "s", "1", content="{}"))
    with pytest.raises(CommandError, match="schema:s v1 is not in the manifest"):
        call_command("generator_manifest")
    call_command("generator_manifest", "--write")
    assert json.loads(path.read_text())["schema:s"]["1"]
    call_command("generator_manifest")
    assert "matches 1 component" in capsys.readouterr().out


def test_generator_manifest_write_refuses_a_rewrite(temp_registry):
    registry, path = temp_registry
    path.write_text(json.dumps({"schema:s": {"1": "0" * 64}}))
    registry.register(Component("schema", "s", "1", content="{}"))
    with pytest.raises(CommandError, match="without a version bump"):
        call_command("generator_manifest", "--write")
