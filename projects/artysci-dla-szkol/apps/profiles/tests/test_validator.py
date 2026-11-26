"""Hard-rule validator (US-2.5B): one passing and one failing test per rule, boundaries, the
clean profile, soft rules, `collect_sources` and the job integration. Synthetic data only (D12)."""

import copy
import json

import pytest

from apps.artists.models import MaterialKind, TextStatus, VideoProvider
from apps.profiles import ai, generation, inputs, validator
from apps.profiles.validator import (
    FACT_MAX_CHARS,
    LENGTH_LIMITS,
    RULE_FACTS,
    RULE_LENGTHS,
    RULE_MEDIA,
    RULE_NUMBERS,
    RULE_PHRASES,
    RULE_QUOTES,
    SOFT_MISSING,
    SOFT_VAGUE,
    Sources,
    normalise_number,
    validate_profile,
)
from apps.quality.models import Generation

from .factories import add_material, make_seed_artist, valid_profile

SOURCE_TEXT = (
    "Teatr Kwiatki gra spektakle we Wrocławiu. Cennik: 1 200 zł za spektakl, "
    "45 minut, wiek widzów 4–9 lat. Pani Anna: „Dzieci były zachwycone,\n"
    "przedstawienie bardzo nam się podobało.”"
)
QUOTE = "Dzieci były zachwycone, przedstawienie bardzo nam się podobało."


def sources(**kw) -> Sources:
    base = {
        "texts": (SOURCE_TEXT,),
        "photo_ids": frozenset({10, 11}),
        "video_ids": frozenset({20}),
        "material_ids": frozenset({10, 11, 20, 30}),
        "offer_ids": frozenset({5}),
        "links": frozenset({("youtube", "abcDEF12345")}),
        "anchors": ("Teatr Kwiatki", "Wrocław", "Kwiatowa opowieść"),
    }
    return Sources(**{**base, **kw})


def clean_profile(**overrides) -> dict:
    """A profile that satisfies every rule against `sources()`."""
    profile = valid_profile(
        description={
            "paragraphs": [
                "Teatr Kwiatki gra we Wrocławiu spektakle trwające 45 minut, "
                "dla przedszkoli i klas młodszych szkoły podstawowej."
            ]
        },
        schools={
            "headline": "Dla szkół",
            "points": ["Spektakl 45 minut"],
            "age_range": "",
            "requirements": [],
        },
        testimonials=[{"quote": QUOTE, "author": "Pani Anna", "source_material_id": 30}],
        gallery={
            "photo_ids": [10],
            "video_ids": [20],
            "captions": [{"material_id": 10, "alt": "Scena ze spektaklu"}],
        },
        offers=[{"offer_id": 5, "tagline": "Spektakl za 1200 zł"}],
        faq=[{"question": "Ile trwa?", "answer": "45 minut."}],
    )
    profile.update(overrides)
    return profile


def hard(profile, **kw):
    return validate_profile(profile, sources(**kw)).hard


def rules(findings):
    return [f.rule for f in findings]


# --- clean profile and report shape -------------------------------------------------------------


def test_clean_profile_is_ok_with_both_lists_empty():
    report = validate_profile(clean_profile(), sources())
    assert report.ok and report.hard == [] and report.soft == []
    assert report.as_dict() == {"ok": True, "hard": [], "soft": []}


def test_finding_has_rule_path_message_and_value():
    profile = clean_profile(faq=[{"question": "Ile?", "answer": "250 zł."}])
    (finding,) = hard(profile)
    assert finding.as_dict() == {
        "rule": RULE_NUMBERS,
        "path": "$.faq[0].answer",
        "message": finding.message,
        "value": "250",
    }
    assert "250" in finding.message and "Usuń" in finding.message


# --- liczby i ceny tylko ze źródła -----------------------------------------------------------


def test_number_missing_from_sources_is_hard_with_its_path():
    profile = clean_profile(offers=[{"offer_id": 5, "tagline": "Od 250 zł"}])
    (finding,) = hard(profile)
    assert finding.rule == RULE_NUMBERS and finding.path == "$.offers[0].tagline"


def test_number_from_pdf_text_passes():
    profile = clean_profile(offers=[{"offer_id": 5, "tagline": "Od 250 zł"}])
    assert hard(profile, texts=(SOURCE_TEXT, "Z cennika PDF: 250 zł od klasy")) == []


@pytest.mark.parametrize(
    "written, source",
    [
        ("3500 zł", "3 500 zł"),
        ("3 500 zł", "3500 zł"),
        ("3.500 zł", "3500 PLN"),
        ("3500,00 zł", "3500 zł"),
        ("7,5 godz.", "7,5 h"),
        ("90 min", "90 minut"),
    ],
)
def test_separators_currency_and_units_are_normalised(written, source):
    profile = clean_profile(faq=[{"question": "Cena?", "answer": written}])
    assert rules(hard(profile)) == [RULE_NUMBERS]  # not in the base source
    assert hard(profile, texts=(SOURCE_TEXT, source)) == []


@pytest.mark.parametrize(
    "raw, expected",
    [("1 200", "1200"), ("1.200,50", "1200.5"), ("007", "7"), ("0,50", "0.5"), ("45", "45")],
)
def test_normalise_number(raw, expected):
    assert normalise_number(raw) == expected


def test_number_inside_a_word_is_not_a_number():
    profile = clean_profile(faq=[{"question": "Kod?", "answer": "Plik a1b2c3."}])
    assert hard(profile) == []


def test_different_amount_is_not_matched_by_a_substring_of_it():
    profile = clean_profile(faq=[{"question": "Cena?", "answer": "200 zł"}])
    assert rules(hard(profile)) == [RULE_NUMBERS]  # source has 1200, not 200


def test_numbers_in_quotes_are_left_to_the_verbatim_rule():
    quote = "Było nas 99 osób i wszystkim się podobało."
    profile = clean_profile(
        testimonials=[{"quote": quote, "author": "Ktoś", "source_material_id": 30}]
    )
    assert rules(hard(profile)) == [RULE_QUOTES]  # not reported twice as a number
    assert hard(profile, texts=(SOURCE_TEXT, quote)) == []


# --- opinie dosłownie ----------------------------------------------------------------------------


def test_quote_differing_by_one_word_is_hard():
    wrong = QUOTE.replace("zachwycone", "zadowolone")
    profile = clean_profile(
        testimonials=[{"quote": wrong, "author": "A", "source_material_id": 30}]
    )
    (finding,) = hard(profile)
    assert finding.rule == RULE_QUOTES and finding.path == "$.testimonials[0].quote"


def test_exact_quote_with_other_line_breaks_passes():
    quote = "Dzieci były zachwycone,\n\n  przedstawienie bardzo\tnam się podobało."
    profile = clean_profile(
        testimonials=[{"quote": quote, "author": "A", "source_material_id": 30}]
    )
    assert hard(profile) == []


# --- zdjęcia i filmy tylko z materiałów artysty ---------------------------------------------


@pytest.mark.parametrize(
    "change, path",
    [
        ({"hero": {**valid_profile()["hero"], "main_photo_id": 99}}, "$.hero.main_photo_id"),
        (
            {"gallery": {"photo_ids": [99], "video_ids": [], "captions": []}},
            "$.gallery.photo_ids[0]",
        ),
        (
            {"gallery": {"photo_ids": [], "video_ids": [10], "captions": []}},
            "$.gallery.video_ids[0]",
        ),  # a photo is not a video
        (
            {
                "gallery": {
                    "photo_ids": [],
                    "video_ids": [],
                    "captions": [{"material_id": 99, "alt": "x"}],
                }
            },
            "$.gallery.captions[0].material_id",
        ),
        (
            {"testimonials": [{"quote": QUOTE, "author": "A", "source_material_id": 99}]},
            "$.testimonials[0].source_material_id",
        ),
        ({"offers": [{"offer_id": 99, "tagline": "x"}]}, "$.offers[0].offer_id"),
    ],
)
def test_id_outside_the_artists_ready_materials_is_hard(change, path):
    (finding,) = hard(clean_profile(**change))
    assert finding.rule == RULE_MEDIA and finding.path == path


def test_own_ids_pass_including_a_video_frame_as_main_photo():
    hero = {**valid_profile()["hero"], "main_photo_id": 11}
    assert hard(clean_profile(hero=hero)) == []


@pytest.mark.parametrize(
    "link",
    [
        "https://www.youtube.com/watch?v=OTHER123456",
        "https://youtu.be/OTHER123456",
        "https://vimeo.com/123456",
        "youtube.com/watch",
    ],
)
def test_link_not_among_the_artists_links_is_hard(link):
    profile = clean_profile(faq=[{"question": "Gdzie?", "answer": f"Zobacz {link}"}])
    (finding,) = hard(profile)
    assert finding.rule == RULE_MEDIA and finding.path == "$.faq[0].answer"


@pytest.mark.parametrize(
    "link",
    ["https://www.youtube.com/watch?v=abcDEF12345", "https://youtu.be/abcDEF12345?t=3"],
)
def test_the_artists_own_link_passes(link):
    assert hard(clean_profile(faq=[{"question": "Gdzie?", "answer": f"Zobacz {link}"}])) == []


def test_a_vimeo_link_of_the_artist_passes():
    profile = clean_profile(faq=[{"question": "Gdzie?", "answer": "https://vimeo.com/55555"}])
    assert hard(profile, links=frozenset({("vimeo", "55555")})) == []


# --- bez języka procesu i bez dodanych obietnic ---------------------------------------------


@pytest.mark.parametrize("phrase", ["w materiałach", "gwarantujemy", "100% satysfakcji"])
def test_banned_phrase_is_hard_and_named(phrase):
    profile = clean_profile(
        faq=[{"question": "Czy?", "answer": f"Tak, {phrase.upper()} dla klas."}]
    )
    (finding,) = [f for f in hard(profile) if f.rule == RULE_PHRASES]
    assert finding.value == phrase and phrase in finding.message
    assert finding.path == "$.faq[0].answer"


def test_phrase_lists_are_named_constants_and_text_without_them_passes():
    assert "w materiałach" in validator.BANNED_PROCESS_PHRASES
    assert "gwarantujemy" in validator.PROMISE_PHRASES
    assert [f for f in hard(clean_profile()) if f.rule == RULE_PHRASES] == []


def test_a_testimonial_may_contain_a_promise_word_verbatim():
    quote = "Gwarantuję, że warto."
    profile = clean_profile(
        testimonials=[{"quote": quote, "author": "A", "source_material_id": 30}]
    )
    assert hard(profile, texts=(SOURCE_TEXT, quote)) == []


# --- fakty ---------------------------------------------------------------------------------------


def fact(value, label="Czas"):
    return {"facts": [{"label": label, "value": value}]}


def test_fact_of_22_characters_passes_and_23_is_hard():
    assert hard(clean_profile(**fact("a" * FACT_MAX_CHARS))) == []
    (finding,) = hard(clean_profile(**fact("a" * (FACT_MAX_CHARS + 1))))
    assert finding.rule == RULE_FACTS and finding.path == "$.facts[0].value"


@pytest.mark.parametrize("value", ["45 min (z przerwą)", "(45 min)", "45 min)"])
def test_fact_with_a_parenthesis_is_hard(value):
    findings = hard(clean_profile(**fact(value)))
    assert RULE_FACTS in rules(findings)


def test_fact_label_follows_the_same_rule():
    (finding,) = hard(clean_profile(**fact("45 min", label="x" * 23)))
    assert finding.path == "$.facts[0].label"


# --- limity długości -----------------------------------------------------------------------------

FIELDS = {
    "hero.headline": lambda text: {"hero": {**valid_profile()["hero"], "headline": text}},
    "hero.subheadline": lambda text: {"hero": {**valid_profile()["hero"], "subheadline": text}},
    "hero.button_label": lambda text: {"hero": {**valid_profile()["hero"], "button_label": text}},
    "description.paragraph": lambda text: {"description": {"paragraphs": [text]}},
    "schools.headline": lambda text: {"schools": {**valid_profile()["schools"], "headline": text}},
    "schools.age_range": lambda text: {
        "schools": {**valid_profile()["schools"], "age_range": text}
    },
    "schools.point": lambda text: {"schools": {**valid_profile()["schools"], "points": [text]}},
    "schools.requirement": lambda text: {
        "schools": {**valid_profile()["schools"], "requirements": [text]}
    },
    "offers.tagline": lambda text: {"offers": [{"offer_id": 5, "tagline": text}]},
    "gallery.alt": lambda text: {
        "gallery": {
            "photo_ids": [10],
            "video_ids": [],
            "captions": [{"material_id": 10, "alt": text}],
        }
    },
    "faq.question": lambda text: {"faq": [{"question": text, "answer": "Tak."}]},
    "faq.answer": lambda text: {"faq": [{"question": "Czy?", "answer": text}]},
    "seo.title": lambda text: {"seo": {"title": text, "description": "Opis."}},
    "seo.description": lambda text: {"seo": {"title": "Tytuł", "description": text}},
}


@pytest.mark.parametrize("key", sorted(FIELDS))
def test_field_at_its_limit_passes_and_one_over_is_hard(key):
    limit = LENGTH_LIMITS[key]
    assert hard(clean_profile(**FIELDS[key]("a" * limit))) == []
    findings = hard(clean_profile(**FIELDS[key]("a" * (limit + 1))))
    assert rules(findings) == [RULE_LENGTHS]


def test_description_total_limit():
    limit = LENGTH_LIMITS["description.total"]
    paragraph = LENGTH_LIMITS["description.paragraph"]
    ok = [("a" * paragraph)] * (limit // paragraph) + ["a" * (limit % paragraph)]
    assert hard(clean_profile(description={"paragraphs": ok})) == []
    over = [*ok, "a"]
    (finding,) = hard(clean_profile(description={"paragraphs": over}))
    assert finding.path == "$.description.paragraphs"


def test_every_limit_has_a_test():
    assert set(LENGTH_LIMITS) - set(FIELDS) == {"description.total"}


# --- soft rules ----------------------------------------------------------------------------------


def test_vague_description_is_soft_only_and_ok_stays_true():
    profile = clean_profile(
        description={"paragraphs": ["Wspaniały, magiczny, wyjątkowy spektakl."]}
    )
    report = validate_profile(profile, sources())
    assert report.ok and report.hard == []
    assert [f.rule for f in report.soft] == [SOFT_VAGUE]


def test_concrete_description_has_no_vague_warning():
    assert validate_profile(clean_profile(), sources()).soft == []


def test_missing_sections_are_soft_notes():
    profile = clean_profile(faq=[], testimonials=[], facts=[])
    report = validate_profile(profile, sources(texts=(SOURCE_TEXT,)))
    assert report.ok
    assert {f.path for f in report.soft if f.rule == SOFT_MISSING} == {
        "$.faq",
        "$.testimonials",
        "$.facts",
    }


# --- collect_sources and the job ------------------------------------------------------------------


@pytest.fixture
def artist():
    artist = make_seed_artist()
    add_material(artist, MaterialKind.PDF, text="Cennik: 1200 zł.", text_status=TextStatus.DONE)
    return artist


@pytest.mark.django_db
def test_collect_sources_reuses_the_input_builder_and_adds_links(artist):
    photo = add_material(artist, MaterialKind.PHOTO, content_type="image/jpeg")
    link = add_material(
        artist,
        MaterialKind.LINK,
        provider=VideoProvider.YOUTUBE,
        video_id="abcDEF12345",
        canonical_url="https://www.youtube.com/watch?v=abcDEF12345",
        title="Fragment spektaklu",
    )
    other = make_seed_artist("inny.artysta@example.invalid")
    foreign = add_material(other, MaterialKind.PHOTO, content_type="image/jpeg")
    data = inputs.build_input(artist)
    found = inputs.collect_sources(artist)
    assert found == inputs.collect_sources(artist, data)
    assert photo.pk in found.photo_ids and foreign.pk not in found.photo_ids
    assert link.pk in found.video_ids and ("youtube", "abcDEF12345") in found.links
    assert any("Cennik: 1200" in text for text in found.texts)
    assert any("Fragment spektaklu" in text for text in found.texts)
    assert len(found.offer_ids) == 1 and "Wrocław" in found.anchors


@pytest.mark.django_db
def test_not_ready_and_without_consent_materials_are_not_sources(artist):
    pending = add_material(artist, MaterialKind.PHOTO, status="pending")
    assert pending.pk not in inputs.collect_sources(artist).photo_ids
    private = make_seed_artist("bez.zgody@example.invalid", consent=False)
    add_material(private, MaterialKind.PDF, text="Sekret 777", text_status=TextStatus.DONE)
    assert not any("777" in text for text in inputs.collect_sources(private).texts)


@pytest.fixture
def client(monkeypatch):
    fake = ai.FakeClient(cost_usd="0.002", model="fake/model-1", reply=json.dumps(valid_profile()))
    monkeypatch.setattr(ai, "get_client", lambda: fake)
    return fake


@pytest.mark.django_db
def test_job_with_a_clean_reply_is_ready_and_stores_an_ok_report(artist, client):
    record = generation.request_generation(artist, "manual")
    generation.run_generation(record.pk)
    done = Generation.objects.get(pk=record.pk)
    assert done.status == Generation.Status.READY
    assert done.report["ok"] is True and done.report["hard"] == []


@pytest.mark.django_db
def test_job_with_a_violating_reply_goes_to_review_with_the_findings(artist, client):
    bad = copy.deepcopy(valid_profile())
    bad["faq"] = [{"question": "Ile?", "answer": "Tylko 250 zł, gwarantujemy."}]
    client.reply = json.dumps(bad)
    record = generation.request_generation(artist, "manual")
    generation.run_generation(record.pk)
    done = Generation.objects.get(pk=record.pk)
    assert done.status == Generation.Status.REVIEW and done.finished
    assert done.result == bad
    found = {(f["rule"], f["path"]) for f in done.report["hard"]}
    assert found == {(RULE_NUMBERS, "$.faq[0].answer"), (RULE_PHRASES, "$.faq[0].answer")}
    assert done.report["ok"] is False


@pytest.mark.django_db
def test_soft_findings_become_warnings_and_do_not_block(artist, client):
    soft = copy.deepcopy(valid_profile())
    soft["description"] = {"paragraphs": ["Magiczny spektakl."]}
    client.reply = json.dumps(soft)
    record = generation.request_generation(artist, "manual")
    generation.run_generation(record.pk)
    done = Generation.objects.get(pk=record.pk)
    assert done.status == Generation.Status.READY
    assert any(SOFT_VAGUE in w for w in done.warnings)
    assert done.report["soft"] and done.report["ok"]


# --- opinia ucznia (RULE_PUPIL) and szacunek bez zastrzeżenia (RULE_HEDGE), D125 ---------------


def _testimonial(author):
    return {"testimonials": [{"quote": QUOTE, "author": author, "source_material_id": 30}]}


@pytest.mark.parametrize(
    "author", ["Kasia, 3b", "Uczeń klasy 4", "uczennica", "Jaś, kl. 2", "dziecko z grupy"]
)
def test_pupil_author_is_hard(author):
    findings = hard(clean_profile(**_testimonial(author)))
    assert [f for f in findings if f.rule == validator.RULE_PUPIL][0].path == (
        "$.testimonials[0].author"
    )


@pytest.mark.parametrize("author", ["wicedyrektor SP Nr 12", "Pani Anna", "Dyrektor przedszkola"])
def test_adult_or_institution_author_is_not_pupil(author):
    assert validator.RULE_PUPIL not in rules(hard(clean_profile(**_testimonial(author))))


def soft(profile, **kw):
    return validate_profile(profile, sources(**kw)).soft


def _with_sentence(text):
    return clean_profile(description={"paragraphs": [text]})


HEDGED = {"texts": (SOURCE_TEXT + " Wystąpiliśmy w około 200 szkołach.",)}


def test_dropped_hedge_is_soft_not_hard():
    profile = _with_sentence(
        "Teatr Kwiatki wystąpił w 200 szkołach we Wrocławiu, spektakl 45 minut."
    )
    assert validator.RULE_HEDGE in rules(soft(profile, **HEDGED))
    assert validator.RULE_HEDGE not in rules(hard(profile, **HEDGED))


@pytest.mark.parametrize(
    "text", ["w około 200 szkołach", "w ponad 200 szkołach", "w ok. 200 szkołach"]
)
def test_kept_hedge_passes(text):
    profile = _with_sentence(f"Teatr Kwiatki wystąpił {text} we Wrocławiu, spektakl 45 minut.")
    assert validator.RULE_HEDGE not in rules(soft(profile, **HEDGED))


def test_number_also_stated_exactly_in_source_is_not_a_hedge_error():
    texts = (*HEDGED["texts"], "Dokładnie 200 szkół, w tym 3 przedszkola.")
    profile = _with_sentence(
        "Teatr Kwiatki wystąpił w 200 szkołach we Wrocławiu, spektakl 45 minut."
    )
    assert validator.RULE_HEDGE not in rules(soft(profile, texts=texts))


def test_computed_number_is_hard_numbers_rule():
    profile = _with_sentence("Teatr Kwiatki zagrał dla ponad 10 000 widzów we Wrocławiu.")
    assert RULE_NUMBERS in rules(hard(profile))
