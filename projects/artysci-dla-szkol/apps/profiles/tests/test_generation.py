import json
import logging
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from procrastinate.contrib.django import app

from apps.artists.models import MaterialKind, TextStatus
from apps.profiles import ai, generation
from apps.profiles.models import AICall
from apps.quality import services as quality
from apps.quality.models import Generation

from .factories import SITE_EMAIL, add_material, make_seed_artist, valid_profile

pytestmark = pytest.mark.django_db


@pytest.fixture
def client(monkeypatch):
    """Install a fake client; tests set `.reply` and read `.requests`."""
    fake = ai.FakeClient(cost_usd="0.002", model="fake/model-1", reply=json.dumps(valid_profile()))
    monkeypatch.setattr(ai, "get_client", lambda: fake)
    return fake


@pytest.fixture
def artist():
    artist = make_seed_artist()
    add_material(artist, MaterialKind.PDF, text="Cennik: 1200 zł.", text_status=TextStatus.DONE)
    return artist


def jobs(queue):
    return [j for j in queue.jobs.values() if j["task_name"] == "profiles.generate_profile"]


@pytest.mark.django_db(transaction=True)
def test_request_then_job_gives_a_ready_generation(artist, client, queue):
    record = generation.request_generation(artist, "manual")
    assert record.status == Generation.Status.RUNNING
    assert len(jobs(queue)) == 1 and jobs(queue)[0]["queue_name"] == "ai"

    import asyncio

    asyncio.run(
        app.run_worker_async(wait=False, install_signal_handlers=False, listen_notify=False)
    )

    record = Generation.objects.get()
    assert record.status == Generation.Status.READY
    assert record.result == valid_profile()
    assert record.trigger == "manual" and record.duration_ms is not None
    versions = {(c.kind, c.name): c.version for c in record.components.all()}
    assert versions[("schema", "profile")] == "0.2"
    assert versions[("instructions", "profile_draft")] == "0.5"
    assert record.cost_usd == Decimal("0.002") == AICall.objects.get().cost_usd
    assert AICall.objects.get().profile_generation_id == record.pk
    assert quality.generation_summary(record)["status"] == "ready"


def test_the_ai_gets_instructions_schema_and_the_input(artist, client):
    record = generation.request_generation(artist, "manual")
    generation.run_generation(record.pk)
    (request,) = client.requests
    system, user = request.messages
    assert "v0.5" in system["content"] and request.purpose == "profile_draft"
    assert request.schema["title"].startswith("Profil artysty")
    payload = json.loads(user["content"])
    assert payload["artist"]["name"] == "Teatr Kwiatki"
    assert payload["documents"][0]["text"] == "Cennik: 1200 zł."


@pytest.mark.parametrize(
    "reply, reason",
    [
        ("to nie jest JSON", "JSON"),
        (json.dumps({"hero": {}}), "schematu"),
        (json.dumps([1, 2]), "schematu"),
        (json.dumps(valid_profile(theme="neon")), "$.theme"),
    ],
)
def test_a_bad_reply_is_an_error_without_a_result(artist, client, reply, reason):
    client.reply = reply
    record = generation.request_generation(artist, "manual")
    done = generation.run_generation(record.pk)
    assert done.status == Generation.Status.ERROR and done.result is None
    assert reason in done.warnings[0]
    assert "neon" not in done.warnings[0] and "to nie jest" not in done.warnings[0]


def test_the_cost_cap_stops_the_job_without_a_call(artist, client, settings):
    settings.AI_DAILY_CAP_USD = "0.01"
    settings.AI_PER_CALL_CAP_USD = "0.05"
    record = generation.request_generation(artist, "manual")
    done = generation.run_generation(record.pk)
    assert done.status == Generation.Status.ERROR and "kosztów" in done.warnings[0]
    assert client.requests == [] and AICall.objects.count() == 0


def test_the_kill_switch_and_provider_errors_are_readable(artist, client, settings):
    settings.AI_KILL_SWITCH = True
    done = generation.run_generation(generation.request_generation(artist, "manual").pk)
    assert done.status == Generation.Status.ERROR and "wyłączone" in done.warnings[0]


def test_a_provider_error_is_an_error(artist, client):
    def boom(request):
        raise ai.AIProviderError("down", code="http_500")

    client.reply = boom
    done = generation.run_generation(generation.request_generation(artist, "manual").pk)
    assert done.status == Generation.Status.ERROR and "AI" in done.warnings[0]
    assert AICall.objects.get().status == "error"


def test_an_unexpected_crash_is_an_error(artist, client, monkeypatch):
    monkeypatch.setattr(generation.inputs, "build_input", lambda a: 1 / 0)
    done = generation.run_generation(generation.request_generation(artist, "manual").pk)
    assert done.status == Generation.Status.ERROR and "Nieoczekiwany" in done.warnings[0]


def test_a_second_request_while_running_is_refused(artist, client, queue):
    generation.request_generation(artist, "manual")
    with pytest.raises(generation.GenerationRefused):
        generation.request_generation(artist, "rerun")
    assert Generation.objects.count() == 1 and len(jobs(queue)) == 1


def test_a_new_request_is_fine_after_the_run_finished(artist, client, queue):
    generation.run_generation(generation.request_generation(artist, "manual").pk)
    generation.request_generation(artist, "rerun")
    assert Generation.objects.count() == 2 and len(jobs(queue)) == 2


def test_another_artist_is_not_blocked(artist, client, queue):
    generation.request_generation(artist, "manual")
    generation.request_generation(make_seed_artist("inny@example.invalid"), "manual")
    assert Generation.objects.count() == 2


def test_a_stale_run_is_closed_and_does_not_block(artist, client, queue, settings):
    old = generation.request_generation(artist, "manual")
    stale = Generation.objects.get(pk=old.pk)
    stale.started_at = timezone.now() - timedelta(seconds=settings.GENERATION_STALE_SECONDS + 5)
    stale.save()
    fresh = generation.request_generation(artist, "manual")
    assert fresh.pk != old.pk
    old.refresh_from_db()
    assert old.status == Generation.Status.ERROR and "przerwane" in old.warnings[0]


def test_an_unknown_trigger_is_refused(artist, client):
    with pytest.raises(quality.GenerationError):
        generation.request_generation(artist, "nope")


def test_a_failed_enqueue_ends_the_run(artist, client, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("queue down")

    monkeypatch.setattr(generation.jobs, "enqueue", broken)
    with pytest.raises(generation.GenerationRefused):
        generation.request_generation(artist, "manual")
    assert Generation.objects.get().status == Generation.Status.ERROR


def test_a_finished_or_missing_generation_is_skipped(artist, client):
    done = generation.run_generation(generation.request_generation(artist, "manual").pk)
    assert generation.run_generation(done.pk) is None
    assert generation.run_generation(999999) is None
    assert len(client.requests) == 1


def test_not_ready_material_never_reaches_the_ai(artist, client):
    add_material(artist, MaterialKind.PDF, status="pending", text="NIEGOTOWY", text_status="done")
    generation.run_generation(generation.request_generation(artist, "manual").pk)
    assert "NIEGOTOWY" not in client.requests[0].messages[1]["content"]


def test_logs_hold_no_email_token_prompt_or_reply(artist, client, caplog):
    client.reply = "ODPOWIEDZ-TAJNA-TEKST"
    with caplog.at_level(logging.DEBUG):
        generation.run_generation(generation.request_generation(artist, "manual").pk)
    logged = "\n".join(
        record.getMessage() + " " + json.dumps(record.__dict__, default=str)
        for record in caplog.records
    )
    assert logged
    for secret in (SITE_EMAIL, "ODPOWIEDZ-TAJNA-TEKST", "Cennik", "Teatr Kwiatki", "artysta.seed"):
        assert secret not in logged
