"""Generator component registry (US-11.1, D13, D14).

A generator component is one versioned part of the profile generator, declared in code:

    from apps.quality.registry import Component, registry

    INSTRUCTIONS = registry.register(
        Component("instructions", "profile_draft", "1", files=("apps/profiles/prompts/draft.md",))
    )

`files` are paths relative to the project folder (or absolute), read in the given order;
`content` is inline text. The content hash is SHA-256 over the files' names and bytes (or the
inline text), so any change to a component changes its hash.

`MANIFEST_PATH` (`components.json`, checked in) maps `kind:name` -> version -> hash. The
registry test fails when a registered component's hash is not the one recorded for its version,
so a content change needs a version bump in the same PR. After a bump, add the new version with
`uv run python manage.py generator_manifest --write` (it never rewrites a recorded version).
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

KINDS = ("instructions", "schema", "validator", "template")
# Text kinds keep a full content snapshot in the database; code kinds point at git by hash.
SNAPSHOT_KINDS = ("instructions", "schema")
MANIFEST_PATH = Path(__file__).resolve().parent / "components.json"


class RegistryError(ValueError):
    pass


def _resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else Path(settings.BASE_DIR) / candidate


@dataclass(frozen=True)
class Component:
    kind: str
    name: str
    version: str
    files: tuple[str, ...] = ()
    content: str | None = None

    def __post_init__(self):
        if self.kind not in KINDS:
            raise RegistryError(f"Unknown component kind {self.kind!r}; one of {KINDS}.")
        if not self.name or not self.version:
            raise RegistryError("A component needs a name and a version.")
        if (self.content is None) == (not self.files):
            raise RegistryError(f"{self.key}: give either files or content (exactly one).")
        object.__setattr__(self, "files", tuple(self.files))

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.name}"

    def text(self) -> str:
        """The component's content as text (files joined with a header line each)."""
        if self.content is not None:
            return self.content
        parts = []
        for path in self.files:
            parts.append(f"=== {path}\n{_resolve(path).read_text(encoding='utf-8')}")
        return "\n".join(parts)

    @property
    def content_hash(self) -> str:
        # Not cached: the registry test must see the content as it is on disk now.
        # Name, length and bytes of each file, so moving bytes between files changes the hash.
        digest = hashlib.sha256()
        if self.content is not None:
            digest.update(b"content\0" + self.content.encode())
        else:
            for path in self.files:
                data = _resolve(path).read_bytes()
                digest.update(f"file\0{path}\0{len(data)}\0".encode() + data)
        return digest.hexdigest()


class Registry:
    def __init__(self):
        self._components: dict[str, Component] = {}

    def register(self, component: Component) -> Component:
        existing = self._components.get(component.key)
        if existing is not None:
            if existing != component:
                raise RegistryError(
                    f"{component.key} is already registered as v{existing.version}."
                )
            return existing  # the same declaration imported twice
        self._components[component.key] = component
        return component

    def get(self, kind: str, name: str) -> Component:
        try:
            return self._components[f"{kind}:{name}"]
        except KeyError:
            raise RegistryError(f"No component {kind}:{name} is registered.") from None

    def all(self) -> list[Component]:
        return [self._components[key] for key in sorted(self._components)]


registry = Registry()


def load_manifest(path: Path | None = None) -> dict:
    path = path or MANIFEST_PATH
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_errors(components, manifest: dict) -> list[str]:
    """One message per component whose content does not match its recorded version."""
    errors = []
    for component in components:
        recorded = manifest.get(component.key, {}).get(component.version)
        actual = component.content_hash
        if recorded is None:
            errors.append(
                f"{component.key} v{component.version} is not in the manifest: run "
                "`manage.py generator_manifest --write` and commit components.json."
            )
        elif recorded != actual:
            errors.append(
                f"{component.key} v{component.version} changed without a version bump "
                f"(manifest {recorded[:12]}, now {actual[:12]}): bump its version."
            )
    return errors


def updated_manifest(components, manifest: dict) -> dict:
    """The manifest plus the versions not yet recorded. Raises RegistryError when a recorded
    version's content changed (that needs a version bump, never a manifest rewrite)."""
    result = {key: dict(versions) for key, versions in manifest.items()}
    for component in components:
        versions = result.setdefault(component.key, {})
        recorded = versions.get(component.version)
        if recorded is not None and recorded != component.content_hash:
            raise RegistryError(
                f"{component.key} v{component.version} changed without a version bump."
            )
        versions[component.version] = component.content_hash
    return {key: dict(sorted(result[key].items())) for key in sorted(result)}


def write_manifest(manifest: dict, path: Path | None = None) -> None:
    path = path or MANIFEST_PATH
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
