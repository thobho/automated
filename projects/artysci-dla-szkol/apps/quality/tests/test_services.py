import json
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.db import IntegrityError

from apps.artists.models import Artist, Material
from apps.profiles.ai import AIError, FakeClient
from apps.profiles.models import AICall
from apps.quality import services
from apps.quality.models import Generation, GeneratorComponentVersion, RegistryImmutable
from apps.quality.registry import Component, RegistryError

from .fake_generator import fake_components, run

pytestmark = pytest.mark.django_db


@pytest.fixture
def artist():
    user = get_user_model().objects.create_user(email="gen.artysta@example.invalid")
    return Artist.objects.create(user=user, name="Artysta Generacja", q_age_from=6, q_age_to=10)


def link(artist, video_id, **kwargs):
    return Material.objects.create(
        artist=artist,
        kind="link",
        status="ready",
        provider="youtube",
        video_id=video_id,
        canonical_url=f"https://www.youtube.com/watch?v={video_id}",
        **kwargs,
    )


# --- the full record -------------------------------------------------------------------------


def test_fake_generator_writes_the_full_record(artist):
    link(artist, "aaaaaaaaaaa")
    generation = run(artist)

    assert Generation.objects.count() == 1
    generation.refresh_from_db()
    assert generation.status == Generation.Status.REVIEW
    assert sorted(generation.components.values_list("kind", flat=True)) == [
        "instructions",
        "schema",
        "template",
        "validator",
    ]
    assert generation.ai_model == "fake/model-1"
    assert generation.input_fingerprint == services.input_fingerprint(artist)
    assert generation.result["final"] == {"title": generation.result["final"]["title"]}
    assert generation.warnings == ["brak zdjęć"]
    assert generation.repair_rounds == 1
    assert generation.started_at <= generation.finished_at
    assert generation.duration_ms >= 0
    calls = AICall.objects.filter(profile_generation=generation)
    assert calls.count() == 2
    assert generation.cost_usd == sum(c.cost_usd for c in calls) == Decimal("0.0024")


def test_generation_without_ai_calls_costs_zero(artist):
    generation = services.start_generation(artist, "questionnaire", fake_components())
    done = services.finish_generation(generation, None, [], 0, Generation.Status.ERROR)
    assert done.cost_usd == 0
    assert done.ai_model == ""


def test_several_models_are_all_recorded(artist):
    generation = services.start_generation(artist, "manual", fake_components())
    for model in ("fake/b", "fake/a"):
        FakeClient(model=model).complete(
            [{"role": "user", "content": "x"}],
            purpose="t",
            max_cost_usd="0.01",
            generation=generation,
        )
    done = services.finish_generation(generation, {}, [], 0, "ready")
    assert done.ai_model == "fake/a, fake/b"


# --- component versions ----------------------------------------------------------------------


def test_same_content_is_stored_once(artist):
    components = fake_components()
    services.start_generation(artist, "manual", components)
    services.start_generation(artist, "rerun", fake_components())
    assert GeneratorComponentVersion.objects.count() == 4
    assert services.component_version(components[0]) == services.component_version(
        fake_components()[0]
    )


def test_snapshot_for_text_kinds_and_git_pointer_for_code(artist):
    generation = run(artist)
    versions = {v["kind"]: v for v in services.versions_of(generation)}
    assert versions["instructions"]["content"] == "Napisz krótki opis."
    assert json.loads(versions["schema"]["content"])["type"] == "object"
    assert versions["validator"] == {
        "kind": "validator",
        "name": "fake_check",
        "version": "1",
        "content_hash": versions["validator"]["content_hash"],
        "source": "git",
        "files": ["apps/quality/tests/fake_generator.py"],
    }
    stored = GeneratorComponentVersion.objects.get(kind="validator")
    assert stored.content == ""
    # A code kind declared inline has no file in git: its content is kept.
    assert versions["template"]["content"] == "<h1>{{ title }}</h1>"
    assert "source" not in versions["template"]


def test_same_version_with_other_content_is_refused(artist):
    services.component_version(Component("instructions", "x", "1", content="a"))
    with pytest.raises(RegistryError, match="bump its version"):
        services.component_version(Component("instructions", "x", "1", content="b"))


def test_old_generation_keeps_its_old_instructions(artist):
    old = run(artist)
    newer = fake_components(instructions_version="2", instructions_text="Nowa instrukcja.")
    new = run(artist, components=newer)
    old_text = {v["kind"]: v for v in services.versions_of(old)}["instructions"]
    new_text = {v["kind"]: v for v in services.versions_of(new)}["instructions"]
    assert (old_text["version"], old_text["content"]) == ("1", "Napisz krótki opis.")
    assert (new_text["version"], new_text["content"]) == ("2", "Nowa instrukcja.")


# --- fingerprint -----------------------------------------------------------------------------


def test_fingerprint_is_stable_and_order_independent(artist):
    first = link(artist, "aaaaaaaaaaa")
    second = link(artist, "bbbbbbbbbbb")
    before = services.input_fingerprint(artist)
    assert services.input_fingerprint(Artist.objects.get(pk=artist.pk)) == before
    # Creation order and the default ordering do not matter: materials are sorted by id.
    Material.objects.filter(pk=first.pk).update(created_at=second.created_at)
    Material.objects.filter(pk=second.pk).update(created_at=first.created_at.replace(year=2000))
    assert services.input_fingerprint(artist) == before
    assert [m[0] for m in services.fingerprint_input(artist)["materials"]] == [
        first.pk,
        second.pk,
    ]


def test_fingerprint_changes_with_materials_and_questionnaire(artist):
    material = link(artist, "aaaaaaaaaaa")
    base = services.input_fingerprint(artist)

    extra = link(artist, "bbbbbbbbbbb")
    with_extra = services.input_fingerprint(artist)
    assert with_extra != base

    extra.delete()
    assert services.input_fingerprint(artist) == base
    material.delete()
    assert services.input_fingerprint(artist) != base

    link(artist, "aaaaaaaaaaa")  # same content, new id
    readded = services.input_fingerprint(artist)
    assert readded != base

    artist.q_tech_room = "sala gimnastyczna"
    assert services.input_fingerprint(artist) != readded


def test_fingerprint_ignores_materials_that_are_not_ready(artist):
    base = services.input_fingerprint(artist)
    Material.objects.create(artist=artist, kind="photo", status="pending", storage_key="k1")
    Material.objects.create(artist=artist, kind="photo", status="rejected", storage_key="k2")
    assert services.input_fingerprint(artist) == base


def test_fingerprint_covers_material_content(artist):
    pdf = Material.objects.create(
        artist=artist, kind="pdf", status="ready", storage_key="k", text="A", text_status="done"
    )
    before = services.input_fingerprint(artist)
    Material.objects.filter(pk=pdf.pk).update(text="B")
    assert services.input_fingerprint(artist) != before


def test_fingerprint_holds_no_material_text(artist):
    Material.objects.create(
        artist=artist, kind="pdf", status="ready", storage_key="k", text="TAJNY TEKST"
    )
    assert "TAJNY" not in json.dumps(services.fingerprint_input(artist))


# --- append-only -----------------------------------------------------------------------------


def test_finished_generation_cannot_be_edited_or_deleted(artist):
    generation = run(artist)
    generation.warnings = []
    with pytest.raises(RegistryImmutable):
        generation.save()
    with pytest.raises(RegistryImmutable):
        generation.delete()
    with pytest.raises(RegistryImmutable):
        Generation.objects.filter(pk=generation.pk).update(status="ready")
    with pytest.raises(RegistryImmutable):
        Generation.objects.all().delete()
    with pytest.raises(RegistryImmutable):
        services.finish_generation(generation, {}, [], 0, "ready")
    assert Generation.objects.get(pk=generation.pk).warnings == ["brak zdjęć"]


def test_component_versions_cannot_be_edited_or_deleted(artist):
    run(artist)
    row = GeneratorComponentVersion.objects.first()
    row.version = "9"
    with pytest.raises(RegistryImmutable):
        row.save()
    with pytest.raises(RegistryImmutable):
        row.delete()
    with pytest.raises(RegistryImmutable):
        GeneratorComponentVersion.objects.update(version="9")
    with pytest.raises(RegistryImmutable):
        GeneratorComponentVersion.objects.all().delete()


def test_finished_generation_takes_no_more_ai_calls(artist):
    generation = run(artist)
    client = FakeClient()
    with pytest.raises(AIError, match="running generation"):
        client.complete(
            [{"role": "user", "content": "x"}],
            purpose="t",
            max_cost_usd="0.01",
            generation=generation,
        )
    other = client.complete([{"role": "user", "content": "x"}], purpose="t", max_cost_usd="0.01")
    with pytest.raises(RegistryImmutable):
        services.record_ai_call(generation, other.call_id)


def test_status_constraint_in_the_database(artist):
    with pytest.raises(IntegrityError):
        Generation.objects.create(
            artist=artist, trigger="manual", input_fingerprint="x", started_at=artist.created_at,
            status="ready",
        )  # fmt: skip


def test_artist_with_generations_is_protected(artist):
    from django.db.models import ProtectedError

    run(artist)
    with pytest.raises(ProtectedError):
        artist.delete()


# --- argument checks -------------------------------------------------------------------------


def test_start_generation_checks_its_arguments(artist):
    with pytest.raises(services.GenerationError, match="trigger"):
        services.start_generation(artist, "cron", fake_components())
    with pytest.raises(services.GenerationError, match="once"):
        services.start_generation(artist, "manual", [])
    components = fake_components()
    with pytest.raises(services.GenerationError, match="once"):
        services.start_generation(artist, "manual", [components[0], components[0]])
    assert Generation.objects.count() == 0


def test_finish_generation_checks_its_arguments(artist):
    generation = services.start_generation(artist, "manual", fake_components())
    with pytest.raises(services.GenerationError):
        services.finish_generation(generation, {}, [], 0, "running")
    with pytest.raises(services.GenerationError):
        services.finish_generation(generation, {}, [], 0, "gone")
    with pytest.raises(services.GenerationError):
        services.finish_generation(generation, {}, [], -1, "ready")
    with pytest.raises(TypeError):
        services.finish_generation(generation, {"x": object()}, [], 0, "ready")
    generation.refresh_from_db()
    assert generation.status == Generation.Status.RUNNING


def test_finish_refuses_a_pending_ai_call(artist):
    generation = services.start_generation(artist, "manual", fake_components())
    AICall.objects.create(
        client="fake", purpose="t", model="m", status="pending", profile_generation=generation
    )
    with pytest.raises(services.GenerationError, match="pending"):
        services.finish_generation(generation, {}, [], 0, "ready")


def test_record_ai_call_refuses_a_call_of_another_generation(artist):
    first = services.start_generation(artist, "manual", fake_components())
    second = services.start_generation(artist, "manual", fake_components())
    result = FakeClient().complete(
        [{"role": "user", "content": "x"}], purpose="t", max_cost_usd="0.01", generation=first
    )
    assert services.record_ai_call(first, result.call_id).profile_generation_id == first.pk
    with pytest.raises(services.GenerationError, match="another generation"):
        services.record_ai_call(second, result.call_id)


def test_unsaved_generation_is_refused_by_the_adapter():
    with pytest.raises(AIError):
        FakeClient().complete(
            [{"role": "user", "content": "x"}],
            purpose="t",
            max_cost_usd="0.01",
            generation=Generation(),
        )


# --- generation_show -------------------------------------------------------------------------


def test_generation_show_prints_json_without_prompt_text(artist, capsys):
    generation = run(artist)
    call_command("generation_show", str(generation.pk))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["id"] == generation.pk
    assert data["status"] == "review"
    assert data["input_fingerprint"] == generation.input_fingerprint
    assert data["repair_rounds"] == 1
    assert data["duration_ms"] == generation.duration_ms
    assert data["cost_usd"] == "0.0024000000"
    assert {c["kind"] for c in data["components"]} == {
        "instructions",
        "schema",
        "validator",
        "template",
    }
    assert all(len(c["content_hash"]) == 64 for c in data["components"])
    assert len(data["ai_calls"]) == 2
    assert "Napisz" not in out  # the instructions text
    assert "Opis profilu" not in out  # the prompt sent


def test_generation_show_running_and_missing(artist, capsys):
    generation = services.start_generation(artist, "manual", fake_components())
    call_command("generation_show", str(generation.pk))
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "running"
    assert data["finished_at"] is None
    assert data["cost_usd"] is None
    with pytest.raises(CommandError, match="No generation"):
        call_command("generation_show", "999999")


# --- admin -----------------------------------------------------------------------------------


def test_admin_lists_generations_read_only(admin_client, artist):
    generation = run(artist)
    response = admin_client.get("/django-admin/quality/generation/")
    assert response.status_code == 200
    assert b"fake/model-1" in response.content
    detail = admin_client.get(f"/django-admin/quality/generation/{generation.pk}/change/")
    assert detail.status_code == 200
    assert b"instructions:fake_draft v1" in detail.content
    assert b"brak zdj" in detail.content
    assert b'name="_save"' not in detail.content
    assert admin_client.get("/django-admin/quality/generation/add/").status_code == 403
    delete_url = f"/django-admin/quality/generation/{generation.pk}/delete/"
    assert admin_client.get(delete_url).status_code == 403
    versions = admin_client.get("/django-admin/quality/generatorcomponentversion/")
    assert versions.status_code == 200


def test_non_staff_cannot_open_generations(client, artist):
    generation = run(artist)
    client.force_login(artist.user)
    for url in (
        "/django-admin/quality/generation/",
        f"/django-admin/quality/generation/{generation.pk}/change/",
    ):
        response = client.get(url)
        assert response.status_code == 302
        assert "/django-admin/login/" in response["Location"]
