"""Page versions, locks, field edits and section regeneration (US-2.6)."""

import json

import pytest
from django.test import Client

from apps.accounts.tests.conftest import make_artist
from apps.profiles import ai, generation, pages, sections
from apps.profiles.models import PageVersion
from apps.quality import services as quality
from apps.quality.models import Generation

from .factories import make_seed_artist, valid_profile

pytestmark = pytest.mark.django_db

PREVIEW = "/panel/podglad/"


@pytest.fixture
def fake(monkeypatch):
    client = ai.FakeClient(reply=json.dumps(valid_profile()), cost_usd="0.001")
    monkeypatch.setattr(ai, "get_client", lambda: client)
    return client


@pytest.fixture
def artist(fake):
    return make_seed_artist()


@pytest.fixture
def generated(artist):
    """The artist after a clean full run: version 1."""
    record = generation.request_generation(artist, "manual")
    generation.run_generation(record.pk)
    return artist


def reply_with(fake, **changes):
    """The fake answers with the valid profile, `changes` laid over it (top-level keys)."""
    fake.reply = json.dumps(valid_profile(**changes))


def queued(queue):
    """Section jobs in the in-memory queue (the full run of the `generated` fixture is not one)."""
    names = [j["task_name"] for j in queue.jobs.values()]
    return [n for n in names if n == "profiles.regenerate_section"]


def run_section(artist, section):
    record = sections.request_section(artist, section)
    return sections.run_section(record.pk, section)


# --- versions ---------------------------------------------------------------------------------


def test_a_ready_generation_creates_version_one(generated):
    (version,) = PageVersion.objects.all()
    assert version.number == 1 and version.source == "generated"
    assert version.content["about"] == "Opis testowy."
    assert version.content["tagline"] == "Teatr Kwiatki"
    assert version.content["facts"] == ["Czas: 45 min"]
    assert version.generation.status == Generation.Status.READY
    assert pages.page_content(generated).about == "Opis testowy."


def test_a_held_generation_creates_no_version(artist, fake):
    bad = valid_profile(facts=[{"label": "Czas", "value": "x" * 30}])
    fake.reply = json.dumps(bad)
    record = generation.request_generation(artist, "manual")
    done = generation.run_generation(record.pk)
    assert done.status == Generation.Status.REVIEW
    assert PageVersion.objects.count() == 0
    assert pages.page_content(artist).facts == []


def test_an_approved_review_creates_the_version(artist):
    from apps.accounts.tests.conftest import make_admin

    record = quality.start_generation(artist, "manual", generation.COMPONENTS)
    quality.finish_generation(record, valid_profile(), [], 2, Generation.Status.REVIEW)
    assert PageVersion.objects.count() == 0
    quality.review_generation(record, make_admin(), "ready", "Sprawdzone.")
    assert PageVersion.objects.get().source == "generated"


def test_record_generated_is_idempotent(generated):
    record = Generation.objects.get()
    assert pages.record_generated(record).number == 1
    assert PageVersion.objects.count() == 1


def test_edit_creates_a_version_locks_the_field_and_escapes_html(generated):
    version = pages.edit_field(generated, "about", "Nowy <b>tekst</b> <script>x</script>")
    assert version.number == 2 and version.source == "edited"
    assert version.locks == ["about"]
    assert pages.current_version(generated).content["about"].startswith("Nowy <b>")
    assert PageVersion.objects.get(number=1).content["about"] == "Opis testowy."


def test_unchanged_text_makes_no_version(generated):
    assert pages.edit_field(generated, "about", "Opis testowy.") is None
    assert PageVersion.objects.count() == 1


@pytest.mark.parametrize(
    "path, value",
    [
        ("facts.0", "x" * 23),
        ("facts.0", "Czas (45 min)"),
        ("facts.0", ""),
        ("tagline", "x" * 71),
        ("about", "x" * 801),
        ("faq.0.answer", "x" * 501),
        ("faq.0.question", ""),
        ("nope", "x"),
        ("facts.5", "x"),
        ("faq.0.other", "x"),
    ],
)
def test_invalid_edits_are_refused_and_save_nothing(generated, path, value):
    with pytest.raises(pages.InvalidEdit) as error:
        pages.edit_field(generated, path, value)
    assert str(error.value.message)
    assert PageVersion.objects.count() == 1 and pages.current_version(generated).locks == []


def test_an_edit_of_a_fact_of_22_characters_is_accepted(generated):
    assert pages.edit_field(generated, "facts.0", "x" * 22).content["facts"] == ["x" * 22]


def test_artists_own_numbers_are_not_checked_against_the_source(generated):
    version = pages.edit_field(generated, "about", "Cena 9999 zł, 777 osób.")
    assert "9999" in version.content["about"]


def test_unlock_only_removes_the_lock(generated):
    pages.edit_field(generated, "about", "Mój tekst")
    assert pages.unlock(generated, "about") is True
    current = pages.current_version(generated)
    assert current.number == 2 and current.locks == [] and current.content["about"] == "Mój tekst"
    assert pages.unlock(generated, "about") is False


def test_only_ten_versions_stay_and_the_current_one_is_intact(generated):
    for i in range(10):  # versions 2..11
        pages.edit_field(generated, "about", f"Tekst {i}")
    numbers = list(PageVersion.objects.order_by("number").values_list("number", flat=True))
    assert numbers == list(range(2, 12))
    assert pages.current_version(generated).content["about"] == "Tekst 9"


def test_restore_makes_a_new_version_and_keeps_locks(generated):
    for text in ("A", "B", "C"):
        pages.edit_field(generated, "about", text)  # versions 2, 3, 4
    pages.edit_field(generated, "tagline", "Hasło")  # version 5, locks about + tagline
    version = pages.restore(generated, 3)
    assert version.number == 6 and version.source == "restored"
    assert version.content["about"] == "B" and version.content["tagline"] == "Teatr Kwiatki"
    assert version.locks == ["about", "tagline"]
    assert PageVersion.objects.filter(number__in=[3, 5]).count() == 2


def test_restore_of_an_unknown_number_fails(generated):
    with pytest.raises(PageVersion.DoesNotExist):
        pages.restore(generated, 99)


def test_a_new_full_generation_keeps_locked_fields(generated, fake):
    pages.edit_field(generated, "about", "Mój tekst")
    reply_with(fake, description={"paragraphs": ["Inny opis."]})
    record = generation.request_generation(generated, "manual")
    generation.run_generation(record.pk)
    current = pages.current_version(generated)
    assert current.number == 3 and current.source == "generated"
    assert current.content["about"] == "Mój tekst" and current.locks == ["about"]


def test_apply_locks_extends_lists_and_ignores_missing_old_items():
    old = {"facts": ["a", "b", "c"], "faq": [{"question": "q", "answer": "r"}], "about": "x"}
    new = {"facts": ["n"], "faq": [], "about": "y"}
    merged = pages.apply_locks(new, old, ["facts.2", "faq.0.answer", "faq.4.answer", "about"])
    assert merged["facts"] == ["n", "b", "c"]
    assert merged["faq"] == [{"question": "q", "answer": "r"}]
    assert merged["about"] == "x"


# --- section regeneration -----------------------------------------------------------------------


def test_a_section_is_replaced_by_the_reply(generated, fake):
    reply_with(fake, faq=[{"question": "Nowe pytanie?", "answer": "Nowa odpowiedź."}])
    done = run_section(generated, "faq")
    assert done.status == Generation.Status.READY and done.trigger == "section"
    current = pages.current_version(generated)
    assert current.number == 2 and current.source == "regenerated"
    assert current.content["faq"] == [{"question": "Nowe pytanie?", "answer": "Nowa odpowiedź."}]
    assert current.content["about"] == "Opis testowy."  # other sections untouched
    assert current.generation_id == done.pk


def test_locked_fields_of_a_section_stay_and_unlocked_ones_change(generated, fake):
    pages.edit_field(generated, "faq.0.question", "Moje pytanie?")
    reply_with(fake, faq=[{"question": "AI pytanie?", "answer": "AI odpowiedź."}])
    run_section(generated, "faq")
    (item,) = pages.current_version(generated).content["faq"]
    assert item == {"question": "Moje pytanie?", "answer": "AI odpowiedź."}
    sent = json.loads(fake.requests[-1].messages[1]["content"])
    assert sent["task"] == "section" and sent["section"] == "faq"
    assert sent["fixed"] == {"faq.0.question": "Moje pytanie?"}
    assert sent["input"]["artist"]["name"] == "Teatr Kwiatki"


def test_a_fully_locked_about_is_unchanged(generated, fake):
    pages.edit_field(generated, "about", "Mój tekst")
    reply_with(fake, description={"paragraphs": ["Inny opis."]})
    run_section(generated, "about")
    current = pages.current_version(generated)
    assert current.content["about"] == "Mój tekst" and current.number == 3


def test_a_violation_in_locked_text_is_not_a_failure(generated, fake):
    pages.edit_field(generated, "about", "Gwarantujemy sukces.")  # the artist's own words
    reply_with(fake, description={"paragraphs": ["Inny opis."]})
    assert run_section(generated, "about").status == Generation.Status.READY


def test_a_bad_reply_is_repaired_in_one_round(generated, fake):
    bad = valid_profile(facts=[{"label": "", "value": "x" * 30}])
    replies = [json.dumps(bad), json.dumps(valid_profile(facts=[{"label": "", "value": "ok"}]))]
    fake.reply = lambda request: replies.pop(0)
    done = run_section(generated, "facts")
    assert done.status == Generation.Status.READY and done.repair_rounds == 1
    assert pages.current_version(generated).content["facts"] == ["ok"]


def test_an_invalid_reply_after_the_repair_rounds_keeps_the_current_version(generated, fake):
    reply_with(fake, facts=[{"label": "", "value": "x" * 30}])
    before = len(fake.requests)
    done = run_section(generated, "facts")
    assert done.status == Generation.Status.ERROR and "po poprawkach" in done.warnings[0]
    assert len(fake.requests) - before == 3  # the first call and two repair rounds
    assert PageVersion.objects.count() == 1
    assert pages.current_version(generated).content["facts"] == ["Czas: 45 min"]


def test_a_reply_that_breaks_a_rule_outside_the_section_does_not_matter(generated, fake):
    reply_with(fake, seo={"title": "x" * 99, "description": "ok"}, tagline="")
    reply_with(fake, seo={"title": "x" * 99, "description": "ok"})
    assert run_section(generated, "about").status == Generation.Status.READY


@pytest.mark.parametrize("reply", ["to nie jest JSON", json.dumps({"hero": {}})])
def test_broken_replies_end_with_a_polish_reason_and_no_version(generated, fake, reply):
    fake.reply = reply
    done = run_section(generated, "about")
    assert done.status == Generation.Status.ERROR and done.warnings
    assert PageVersion.objects.count() == 1


def test_the_cost_cap_keeps_the_current_version(generated, fake, settings):
    settings.AI_DAILY_CAP_USD = "0.01"
    settings.AI_PER_CALL_CAP_USD = "0.05"
    calls = len(fake.requests)
    done = run_section(generated, "about")
    assert done.status == Generation.Status.ERROR and "kosztów" in done.warnings[0]
    assert len(fake.requests) == calls and PageVersion.objects.count() == 1


def test_the_kill_switch_is_readable(generated, settings):
    settings.AI_KILL_SWITCH = True
    done = run_section(generated, "about")
    assert done.status == Generation.Status.ERROR and "wyłączone" in done.warnings[0]


def test_an_unknown_section_is_refused(generated):
    with pytest.raises(generation.GenerationRefused):
        sections.request_section(generated, "seo")


def test_a_second_run_is_refused_while_one_runs(generated, queue):
    sections.request_section(generated, "about")
    with pytest.raises(generation.GenerationRefused):
        sections.request_section(generated, "faq")
    assert queued(queue) == ["profiles.regenerate_section"]


def test_a_finished_or_missing_run_is_not_run_again(generated):
    record = sections.request_section(generated, "about")
    sections.run_section(record.pk, "about")
    assert sections.run_section(record.pk, "about") is None
    assert sections.run_section(0, "about") is None


def test_an_edit_made_during_the_run_is_kept(generated, fake):
    record = sections.request_section(generated, "faq")

    def reply(request):
        pages.edit_field(generated, "about", "Wpisane w trakcie")
        return json.dumps(valid_profile(faq=[{"question": "N?", "answer": "N."}]))

    fake.reply = reply
    sections.run_section(record.pk, "faq")
    current = pages.current_version(generated)
    assert current.content["about"] == "Wpisane w trakcie" and current.locks == ["about"]
    assert current.content["faq"] == [{"question": "N?", "answer": "N."}]


# --- views --------------------------------------------------------------------------------------


@pytest.fixture
def web(generated):
    client = Client(enforce_csrf_checks=True)
    client.force_login(generated.user)
    return client


def post(web, name, **data):
    token = web.get(PREVIEW).cookies["csrftoken"].value
    return web.post(f"{PREVIEW}{name}/", {**data, "csrfmiddlewaretoken": token})


def test_preview_shows_the_current_version_and_the_editor(web):
    body = web.get(PREVIEW).content.decode()
    assert "Opis testowy." in body and "Edycja tekstów" in body
    assert 'name="value"' in body and "Przywróć" not in body  # only one version
    assert "Wersje strony" in body


def test_the_edit_view_saves_and_the_page_escapes_html(web):
    response = post(web, "edycja", path="about", value="Hej <script>alert(1)</script> <b>x</b>")
    assert response.status_code == 302
    body = web.get(PREVIEW).content.decode()
    assert "<script>alert(1)</script>" not in body and "&lt;script&gt;alert(1)" in body
    assert "zablokowane" in body and "Odblokuj" in body
    post(web, "odblokuj", path="about")
    assert "Odblokuj" not in web.get(PREVIEW).content.decode()


def test_an_invalid_edit_shows_a_polish_error_and_saves_nothing(web):
    response = web.get(PREVIEW)  # sets the csrf cookie
    token = response.cookies["csrftoken"].value
    response = web.post(
        PREVIEW + "edycja/",
        {"path": "facts.0", "value": "x" * 23, "csrfmiddlewaretoken": token},
        follow=True,
    )
    assert "Fakt ma 23 znaków" in response.content.decode()
    assert PageVersion.objects.count() == 1


def test_restore_view_and_version_list(web):
    post(web, "edycja", path="about", value="Zmiana")
    body = web.get(PREVIEW).content.decode()
    assert 'data-version="2"' in body and "Przywróć" in body
    post(web, "przywroc", number="1")
    body = web.get(PREVIEW).content.decode()
    assert "Opis testowy." in body and 'data-version="3"' in body and "przywrócona" in body
    assert post(web, "przywroc", number="99").status_code == 404
    assert post(web, "przywroc", number="abc").status_code == 404


def test_regenerate_view_queues_the_job_and_shows_the_status(web, queue):
    assert post(web, "sekcja", section="about").status_code == 302
    assert queued(queue) == ["profiles.regenerate_section"]
    body = web.get(PREVIEW).content.decode()
    assert 'data-running="true"' in body and "every 3s" in body
    status = web.get(PREVIEW + "sekcja/status/")
    assert status.status_code == 200 and "HX-Refresh" not in status.headers
    assert post(web, "sekcja", section="seo").status_code == 302  # refused with a message


def test_a_failed_section_run_shows_the_reason(web, generated, fake):
    fake.reply = "to nie jest JSON"
    run_section(generated, "about")
    body = web.get(PREVIEW).content.decode()
    assert "Obecna wersja została bez zmian" in body and 'data-running="false"' in body
    assert web.get(PREVIEW + "sekcja/status/").headers["HX-Refresh"] == "true"


def test_unsafe_methods_need_csrf(web):
    for name in ("edycja", "odblokuj", "sekcja", "przywroc"):
        assert web.post(f"{PREVIEW}{name}/", {"path": "about", "value": "x"}).status_code == 403


def test_other_artists_and_anonymous_users_are_refused(generated):
    other = make_artist("inny@example.invalid")
    client = Client()
    client.force_login(other)
    # Another artist has their own (empty) pages: they cannot reach the first artist's versions.
    assert client.post(PREVIEW + "przywroc/", {"number": "1"}).status_code == 404
    assert client.post(PREVIEW + "edycja/", {"path": "about", "value": "x"}).status_code == 302
    assert PageVersion.objects.get(artist=generated).content["about"] == "Opis testowy."
    assert PageVersion.objects.filter(artist=generated).count() == 1
    anonymous = Client()
    for name in ("edycja", "odblokuj", "sekcja", "przywroc"):
        response = anonymous.post(f"{PREVIEW}{name}/", {"path": "about"})
        assert response.status_code == 302 and "logowanie" in response["Location"]
    assert anonymous.get(PREVIEW).status_code == 302


def test_a_held_generation_is_not_shown_in_the_preview(artist, fake):
    fake.reply = json.dumps(
        valid_profile(
            hero={**valid_profile()["hero"], "headline": "TAJNY-NAGLOWEK"},
            facts=[{"label": "", "value": "x" * 30}],
        )
    )
    record = generation.request_generation(artist, "manual")
    assert generation.run_generation(record.pk).status == Generation.Status.REVIEW
    client = Client()
    client.force_login(artist.user)
    assert "TAJNY-NAGLOWEK" not in client.get(PREVIEW).content.decode()
