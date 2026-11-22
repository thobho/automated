"""Repair loop and review fallback (US-2.5C), driven by a scripted fake AI client."""

import json

import pytest
from django.test import Client

from apps.artists.models import MaterialKind, TextStatus
from apps.profiles import ai, generation, repair
from apps.profiles.models import AICall
from apps.quality.models import Generation

from .factories import add_material, make_seed_artist, valid_profile

pytestmark = pytest.mark.django_db

BAD_FACT = [{"label": "Czas", "value": "45 min (ok)"}]  # hard: facts carry no brackets


def bad():
    return json.dumps(valid_profile(facts=BAD_FACT))


def good():
    return json.dumps(valid_profile())


@pytest.fixture
def artist():
    artist = make_seed_artist()
    add_material(artist, MaterialKind.PDF, text="Cennik: 1200 zł.", text_status=TextStatus.DONE)
    return artist


@pytest.fixture
def script(monkeypatch):
    """`script(reply1, reply2, ...)`: the fake client answers with these, one per call."""

    def install(*replies, cost_usd="0.001"):
        queue = list(replies)

        def reply(request):
            item = queue.pop(0)
            if isinstance(item, Exception):
                raise item
            return item

        fake = ai.FakeClient(reply=reply, cost_usd=cost_usd, model="fake/model-1")
        monkeypatch.setattr(ai, "get_client", lambda: fake)
        return fake

    return install


def run(artist):
    return generation.run_generation(generation.request_generation(artist, "manual").pk)


def test_a_clean_first_reply_needs_no_repair(artist, script):
    fake = script(good())
    done = run(artist)
    assert done.status == Generation.Status.READY and done.repair_rounds == 0
    assert len(fake.requests) == 1 and "repair" not in done.report


def test_one_hard_violation_is_repaired_in_round_one(artist, script):
    fake = script(bad(), good())
    done = run(artist)
    assert done.status == Generation.Status.READY
    assert done.repair_rounds == 1
    assert done.result == valid_profile()
    assert len(fake.requests) == 2
    assert AICall.objects.filter(profile_generation=done).count() == 2
    assert done.report["ok"] is True and done.report["repair"] == {"rounds": 1, "stopped": ""}


def test_a_fix_on_round_two(artist, script):
    fake = script(bad(), bad(), good())
    done = run(artist)
    assert done.status == Generation.Status.READY and done.repair_rounds == 2
    assert len(fake.requests) == 3 and AICall.objects.count() == 3


def test_never_fixed_goes_to_review_after_exactly_two_repair_calls(artist, script):
    fake = script(bad(), bad(), bad())
    done = run(artist)
    assert done.status == Generation.Status.REVIEW
    assert done.repair_rounds == 2 and len(fake.requests) == 3
    assert [h["rule"] for h in done.report["hard"]] == ["fakty"]
    assert done.report["repair"]["stopped"] == ""
    assert done.result["facts"] == BAD_FACT  # kept for the administrator, hidden from the artist


def test_soft_findings_never_trigger_a_repair(artist, script):
    vague = valid_profile(description={"paragraphs": ["Ok."]})
    fake = script(json.dumps(vague))
    done = run(artist)
    assert len(fake.requests) == 1
    assert done.status == Generation.Status.READY and done.repair_rounds == 0
    assert done.report["soft"] and not done.report["hard"]


def test_the_cost_cap_in_round_one_stops_the_loop(artist, script, settings):
    script(bad(), cost_usd="0.02")
    # Enough for the first call only: the repair reservation (0.05) no longer fits in 0.06.
    settings.AI_PER_CALL_CAP_USD = "0.05"
    settings.AI_DAILY_CAP_USD = "0.06"
    done = run(artist)
    assert done.status == Generation.Status.REVIEW
    assert done.repair_rounds == 0
    assert done.report["repair"] == {"rounds": 0, "stopped": repair.STOP_COST_CAP}
    assert any("kosztów" in w for w in done.warnings)
    assert AICall.objects.count() == 1


@pytest.mark.parametrize(
    "bad_reply, stopped",
    [
        ("to nie jest JSON", repair.STOP_INVALID_JSON),
        (json.dumps({"hero": {}}), repair.STOP_SCHEMA),
        (ai.AIProviderError("down", code="http_500"), repair.STOP_PROVIDER),
        (ai.AIError("boom"), repair.STOP_PROVIDER),
    ],
)
def test_an_invalid_repair_reply_stops_the_loop(artist, script, bad_reply, stopped):
    fake = script(bad(), bad_reply, good())
    done = run(artist)
    assert done.status == Generation.Status.REVIEW
    assert done.repair_rounds == 1 and len(fake.requests) == 2  # no second round after a stop
    assert done.report["repair"] == {"rounds": 1, "stopped": stopped}
    assert done.result["facts"] == BAD_FACT  # the last valid result is kept
    assert done.warnings and "przerwane" in done.warnings[-1]


def test_the_kill_switch_during_repair_goes_to_review(artist, script, monkeypatch):
    script(bad())
    calls = iter([None])

    def disabled(*args, **kwargs):
        if next(calls, "off") == "off":
            raise ai.AIDisabled("off")

    monkeypatch.setattr(ai.base.budget, "check_kill_switch", disabled)
    done = run(artist)
    assert done.status == Generation.Status.REVIEW
    assert done.report["repair"]["stopped"] == repair.STOP_DISABLED


def test_a_validator_crash_during_repair_goes_to_review(artist, script, monkeypatch):
    script(bad(), good())
    real = generation.validator.validate_profile
    seen = []

    def flaky(profile, sources):
        seen.append(1)
        if len(seen) > 1:
            raise RuntimeError("boom")
        return real(profile, sources)

    monkeypatch.setattr(repair.validator, "validate_profile", flaky)
    monkeypatch.setattr(generation.validator, "validate_profile", flaky)
    done = run(artist)
    assert done.status == Generation.Status.REVIEW
    assert done.report["repair"]["stopped"] == repair.STOP_VALIDATOR


def test_the_repair_prompt_has_the_findings_and_no_personal_data(artist, script):
    fake = script(bad(), good())
    run(artist)
    system, user = fake.requests[1].messages
    assert "repair" in system["content"] and "tylko tyle, ile trzeba" in system["content"]
    payload = json.loads(user["content"])
    assert payload["task"] == "repair"
    assert payload["previous_result"]["facts"] == BAD_FACT
    (finding,) = payload["findings"]
    assert set(finding) == {"rule", "path", "message"}
    assert finding["path"] == "$.facts[0].value" and finding["rule"] == "fakty"
    assert payload["input"]["artist"]["name"] == "Teatr Kwiatki"
    text = user["content"] + system["content"]
    assert "kontakt@example.invalid" not in text and "artysta.seed@example.invalid" not in text


def test_the_repair_instructions_say_change_only_the_listed_fields():
    text = repair.INSTRUCTIONS.text()
    assert "wyłącznie pola wskazane w `findings`" in text
    assert "nie dodajesz żadnych nowych faktów" in text


def test_the_artist_panel_shows_the_wait_message_and_no_generated_text(artist, script):
    script(bad(), bad(), bad())
    done = run(artist)
    assert done.status == Generation.Status.REVIEW
    web = Client()
    web.force_login(artist.user)
    for url in ("/artysta/profil/generowanie/", "/artysta/profil/generowanie/status/"):
        response = web.get(url)
        body = response.content.decode()
        assert response.status_code == 200
        assert "Profil czeka na przegląd" in body and 'data-status="review"' in body
        assert "45 min (ok)" not in body and "gotowa" not in body
