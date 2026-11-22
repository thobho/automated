"""Generation registry services (US-11.1, D13, D14, D107).

A generator run calls, in this order:

    generation = start_generation(artist, "import", [INSTRUCTIONS, SCHEMA, VALIDATOR])
    result = ai.complete(messages, ..., generation=generation)  # or record_ai_call() after
    finish_generation(generation, data, warnings, repair_rounds, Generation.Status.READY)

`versions_of(generation)` returns what is needed to reproduce the run later.
"""

import hashlib
import json
from collections.abc import Iterable
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone

from apps.artists.materials import QUESTIONNAIRE_FIELDS
from apps.artists.models import Artist, Material, ScanStatus
from apps.profiles.models import AICall

from .models import Generation, GenerationReview, GeneratorComponentVersion, RegistryImmutable
from .registry import SNAPSHOT_KINDS, Component, RegistryError

FINGERPRINT_VERSION = 1
# What a material's content hash covers: everything a generator could read from the row. File
# bytes are not read: a storage key is unique per upload and an upload is never overwritten.
MATERIAL_CONTENT_FIELDS = (
    "kind",
    "storage_key",
    "content_type",
    "size",
    "provider",
    "video_id",
    "canonical_url",
    "title",
    "text",
    "text_status",
)


class GenerationError(ValueError):
    pass


def _sha256_json(value) -> str:
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


# --- component versions ----------------------------------------------------------------------


def component_version(component: Component) -> GeneratorComponentVersion:
    """The stored row for this component's current content (created once per hash).

    Raises RegistryError when the same version is already stored with other content: that
    content change needed a version bump.
    """
    content_hash = component.content_hash
    existing = GeneratorComponentVersion.objects.filter(
        kind=component.kind, name=component.name, content_hash=content_hash
    ).first()
    if existing is not None:
        return existing
    # Inline content has no file in git to point at, so it is always kept.
    keep = component.kind in SNAPSHOT_KINDS or not component.files
    snapshot = component.text() if keep else ""
    try:
        with transaction.atomic():
            return GeneratorComponentVersion.objects.create(
                kind=component.kind,
                name=component.name,
                version=component.version,
                content_hash=content_hash,
                content=snapshot,
                files=list(component.files),
                created_at=timezone.now(),
            )
    except IntegrityError:
        # A concurrent run stored the same hash, or this version exists with other content.
        existing = GeneratorComponentVersion.objects.filter(
            kind=component.kind, name=component.name, content_hash=content_hash
        ).first()
        if existing is not None:
            return existing
        raise RegistryError(
            f"{component.key} v{component.version} is stored with other content: bump its version."
        ) from None


# --- input fingerprint -----------------------------------------------------------------------


def material_content_hash(material: Material) -> str:
    return _sha256_json({f: getattr(material, f) for f in MATERIAL_CONTENT_FIELDS})


def fingerprint_input(artist: Artist) -> dict:
    """The canonical, ordered input the fingerprint is computed from (no material content)."""
    materials = Material.objects.filter(artist=artist, status=ScanStatus.READY).order_by("pk")
    return {
        "v": FINGERPRINT_VERSION,
        "materials": [[m.pk, material_content_hash(m)] for m in materials],
        "questionnaire": {field: getattr(artist, field) for field in QUESTIONNAIRE_FIELDS},
    }


def input_fingerprint(artist: Artist) -> str:
    """SHA-256 over the artist's ready materials (id + content hash, by id) and questionnaire."""
    return _sha256_json(fingerprint_input(artist))


# --- generations -----------------------------------------------------------------------------


def start_generation(artist: Artist, trigger: str, components: Iterable[Component]) -> Generation:
    """Record a running generation with the current version of every component it uses."""
    if trigger not in Generation.Trigger.values:
        raise GenerationError(f"Unknown trigger {trigger!r}.")
    components = list(components)
    keys = [c.key for c in components]
    if not components or len(set(keys)) != len(keys):
        raise GenerationError("Give each component once (at least one).")
    versions = [component_version(c) for c in components]
    with transaction.atomic():
        generation = Generation.objects.create(
            artist=artist,
            trigger=trigger,
            input_fingerprint=input_fingerprint(artist),
            started_at=timezone.now(),
        )
        generation.components.set(versions)
    return generation


def _running(generation: Generation) -> Generation:
    """The generation's row locked for this transaction; refuses a finished one."""
    locked = Generation.objects.select_for_update().get(pk=generation.pk)
    if locked.finished:
        raise RegistryImmutable(f"Generation {locked.pk} is finished.")
    return locked


def record_ai_call(generation: Generation, call_id: int) -> AICall:
    """Link an AICall row (`AIResult.call_id`) to a running generation."""
    with transaction.atomic():
        _running(generation)
        call = AICall.objects.select_for_update().get(pk=call_id)
        if call.profile_generation_id not in (None, generation.pk):
            raise GenerationError(f"AI call {call_id} belongs to another generation.")
        call.profile_generation_id = generation.pk
        call.save(update_fields=["profile_generation"])
    return call


def finish_generation(
    generation: Generation,
    result,
    warnings: Iterable[str],
    repair_rounds: int,
    status: str,
    report: dict | None = None,
) -> Generation:
    """Close a running generation: result, warnings, rounds, times, AI model and cost, and the
    validator's report when there is one."""
    if status not in Generation.Status.values or status == Generation.Status.RUNNING:
        raise GenerationError(f"A generation cannot finish as {status!r}.")
    if repair_rounds < 0:
        raise GenerationError("repair_rounds cannot be negative.")
    warnings = [str(w) for w in warnings]
    json.dumps(report)
    json.dumps(result)  # refuse what the JSON column could not store, before writing anything
    with transaction.atomic():
        locked = _running(generation)
        calls = AICall.objects.filter(profile_generation=locked)
        if calls.filter(status=AICall.Status.PENDING).exists():
            raise GenerationError("An AI call of this generation is still pending.")
        models = sorted(set(calls.values_list("model", flat=True)))
        finished_at = timezone.now()
        locked.status = status
        locked.result = result
        locked.warnings = warnings
        locked.report = report
        locked.repair_rounds = repair_rounds
        locked.finished_at = finished_at
        locked.duration_ms = int((finished_at - locked.started_at).total_seconds() * 1000)
        locked.cost_usd = calls.aggregate(s=Sum("cost_usd"))["s"] or Decimal(0)
        locked.ai_model = ", ".join(models)[:500]
        locked.save()
    return locked


def versions_of(generation: Generation) -> list[dict]:
    """What reproduces the run: per component its version and hash, plus the stored content
    (text kinds) or the files to take from git at a commit where the hash matches (code)."""
    rows = generation.components.order_by("kind", "name")
    out = []
    for row in rows:
        item = {
            "kind": row.kind,
            "name": row.name,
            "version": row.version,
            "content_hash": row.content_hash,
        }
        if row.kind in SNAPSHOT_KINDS or not row.files:
            item["content"] = row.content
        else:
            item["source"] = "git"
            item["files"] = row.files
        out.append(item)
    return out


def generation_summary(generation: Generation) -> dict:
    """The JSON form shown by `generation_show` (no prompt or reply text, no materials)."""
    return {
        "id": generation.pk,
        "artist_id": generation.artist_id,
        "trigger": generation.trigger,
        "status": generation.status,
        "ai_model": generation.ai_model,
        "input_fingerprint": generation.input_fingerprint,
        "components": [
            {k: v for k, v in item.items() if k != "content"} for item in versions_of(generation)
        ],
        "warnings": generation.warnings,
        "repair_rounds": generation.repair_rounds,
        "started_at": generation.started_at.isoformat(),
        "finished_at": generation.finished_at.isoformat() if generation.finished_at else None,
        "duration_ms": generation.duration_ms,
        "cost_usd": str(generation.cost_usd) if generation.cost_usd is not None else None,
        "ai_calls": list(
            AICall.objects.filter(profile_generation=generation)
            .order_by("pk")
            .values_list("pk", flat=True)
        ),
    }


# --- manual review (US-2.5C) -----------------------------------------------------------------


def review_generation(generation: Generation, reviewer, decision: str, note: str) -> Generation:
    """A staff user closes a generation waiting for review as `gotowa` or `błąd`, with a note.

    Writes a `GenerationReview` audit row (who, when, what, why). Refuses a non-staff user, an
    empty note, another decision and a generation that is not `do przeglądu`.
    """
    if not (getattr(reviewer, "is_active", False) and getattr(reviewer, "is_staff", False)):
        raise PermissionError("Only staff can review generations.")
    if decision not in GenerationReview.Decision.values:
        raise GenerationError(f"A review cannot end as {decision!r}.")
    note = (note or "").strip()
    if not note:
        raise GenerationError("A review needs a note.")
    with transaction.atomic():
        locked = Generation.objects.select_for_update().get(pk=generation.pk)
        if locked.status != Generation.Status.REVIEW:
            raise GenerationError(f"Generation {locked.pk} is not waiting for review.")
        locked.status = decision
        if decision == GenerationReview.Decision.ERROR:
            locked.warnings = ["Profil nie przeszedł przeglądu. Spróbuj wygenerować go ponownie."]
        locked._closing_review = True
        locked.save()
        GenerationReview.objects.create(
            generation=locked, reviewer=reviewer, decision=decision, note=note[:2000],
            created_at=timezone.now(),
        )  # fmt: skip
    return locked
