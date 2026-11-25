"""Generator test set (US-11.2): package format, checks, expectations, loader, commands, scripted
profile. Photos are drawn with Pillow; the scanner is the fake; no network."""

import copy
import json
import shutil
import socket
from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from apps.accounts.tests.conftest import queue  # noqa: F401  (fixture)
from apps.artists import checks
from apps.artists.models import Artist, Material, Offer, WebsiteImport
from apps.profiles import ai, generation, inputs, validation, validator
from apps.profiles.ai.scrub import scrub
from apps.profiles.generator_components import COMPONENTS
from apps.quality import scripted, services, testset
from apps.quality.models import Generation, TestsetLoad
from config.settings.storage import build_storages

pytestmark = pytest.mark.django_db

T41_SLUGS = {
    "gliniane-ludki",
    "iluzjonista-marek",
    "kwartet-allegretto",
    "pracownia-eureka",
    "teatr-lalek-pod-debem",
    "zwierzaki-z-zagrody",
}
SLUGS = sorted(p.parent.name for p in testset.TESTSET_DIR.glob("*/package.json"))


@pytest.fixture(autouse=True)
def _env(queue, settings, tmp_path):  # noqa: F811
    settings.STORAGE_BACKEND = "filesystem"
    settings.STORAGES = build_storages(
        "filesystem",
        public_base_url="http://media.test:8101/",
        private_root=tmp_path / "private",
        public_root=tmp_path / "public",
        signed_url_ttl=settings.MEDIA_SIGNED_URL_TTL,
    )
    settings.MALWARE_SCANNER_FAKE_RESULT = "clean"
    settings.QUALITY_LAB_ENABLED = True


@pytest.fixture
def no_network(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("the test set must not use the network")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)


def package(slug="teatr-lalek-pod-debem") -> dict:
    return testset.get_package(slug)


def root_with(tmp_path, slug="zwierzaki-z-zagrody", **changes):
    """A package root holding a modified copy of one package (`changes` replace top-level keys;
    a value of `...` deletes the key)."""
    data = copy.deepcopy(package(slug))
    for key, value in changes.items():
        if value is ...:
            data.pop(key)
        else:
            data[key] = value
    folder = tmp_path / "root" / data.get("slug", slug)
    folder.mkdir(parents=True)
    (folder / "package.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return tmp_path / "root"


# --- the shipped packages -------------------------------------------------------------------


def test_the_set_has_thirty_valid_packages_ten_per_level():
    report = testset.check_all()
    assert [folder for folder, _, _ in report] == SLUGS
    assert len(SLUGS) == 30
    assert all(problems == [] for _, _, problems in report)
    items = [p for _, p, _ in report]
    assert {level: sum(p["level"] == level for p in items) for level in testset.LEVELS} == {
        "weak": 10,
        "medium": 10,
        "rich": 10,
    }
    assert all(len(p["expectations"]) >= 3 for p in items)
    assert all(p["origin"] == "synthetic" for p in items)
    assert [p["slug"] for p in testset.packages()] == SLUGS


ARTIST_TYPES = ("theatre", "illusion", "music", "science_show", "animal_show", "workshops", "other")


def test_every_artist_type_has_three_packages_and_every_level_covers_five_types():
    items = testset.packages()
    for artist_type in ARTIST_TYPES:
        assert sum(p["artist"]["type"] == artist_type for p in items) >= 3, artist_type
    for level in testset.LEVELS:
        types = {p["artist"]["type"] for p in items if p["level"] == level}
        assert len(types) >= 5, (level, types)


def test_every_expectation_kind_is_used_at_least_three_times():
    kinds = [e["kind"] for p in testset.packages() for e in p["expectations"]]
    for kind in testset.EXPECTATION_KINDS:
        assert kinds.count(kind) >= 3, kind


def test_no_two_packages_share_an_artist_name_or_site_text():
    items = testset.packages()
    names = [p["artist"]["name"].casefold() for p in items]
    assert len(set(names)) == len(names)
    texts = [" ".join(p["site_text"].split()).casefold() for p in items if p["site_text"].strip()]
    assert len(set(texts)) == len(texts)


def test_levels_have_the_content_their_names_promise():
    # the six T41 packages are not changed by T42 and are exempt from the strict richness rule
    for p in testset.packages():
        photos = [s for s in p["photos"] if s["kind"] == "normal"]
        if p["level"] == "rich" and p["slug"] not in T41_SLUGS:
            assert len(photos) >= 4 and len(p["offers"]) >= 3 and p["documents"], p["slug"]
            assert len(p["site_text"]) > 400, p["slug"]
        if p["level"] == "weak":
            assert len(p["site_text"]) < 100 and len(photos) <= 1, p["slug"]
            assert not p["documents"], p["slug"]


def test_the_set_covers_the_special_cases():
    items = {p["slug"]: p for p in testset.packages()}
    packages_ = list(items.values())
    assert any(
        not p["offers"] and any(e["kind"] == "no_price" for e in p["expectations"])
        for p in packages_
    )  # no price anywhere
    assert any(  # a price in a document only
        not any(o.get("price_pln") for o in p["offers"])
        and p["questionnaire"].get("q_price_from_pln") is None
        and any("zł" in d["text"] for d in p["documents"])
        for p in packages_
    )
    assert any("„" in d["text"] and "”" in d["text"] for p in packages_ for d in p["documents"])
    assert any(p["photos"] and all(s["kind"] == "poster" for s in p["photos"]) for p in packages_)
    assert any(
        p["photos"] and all(s["kind"] == "screenshot" for s in p["photos"]) for p in packages_
    )
    assert any(len(p["offers"]) == 20 for p in packages_)
    contradictory = items["ferma-dziadka-stasia"]
    assert contradictory["questionnaire"]["q_age_from"] != contradictory["offers"][0]["age_from"]
    assert (
        contradictory["questionnaire"]["q_duration_minutes"]
        != (contradictory["offers"][0]["duration_minutes"])
    )


def test_the_set_covers_no_price_and_no_usable_main_photo():
    kinds = [(p["slug"], e) for p in testset.packages() for e in p["expectations"]]
    assert any(e["kind"] == "no_price" for _, e in kinds)
    assert any(e == {"kind": "field_empty", "path": "hero.main_photo_id"} for _, e in kinds)


@pytest.mark.parametrize("slug", SLUGS)
def test_package_texts_are_clean_for_the_scrubber_and_use_only_invalid_hosts(slug):
    texts = list(testset._strings(package(slug)))
    assert texts and all(scrub(text) == text for text in texts)
    for text in texts:
        for url in testset._URL.findall(text):
            host = url.split("/")[2].lower().rstrip(".")
            assert host.endswith("example.invalid") or host in testset._VIDEO_HOSTS


# --- check_package --------------------------------------------------------------------------


def problems_of(**changes) -> list[str]:
    data = copy.deepcopy(package("zwierzaki-z-zagrody"))
    for key, value in changes.items():
        data[key] = value
    return testset.check_package(data)


def test_a_missing_field_an_unknown_level_and_extra_keys_are_problems():
    data = copy.deepcopy(package())
    del data["site_text"]
    assert any("site_text" in p for p in testset.check_package(data))
    assert any("level" in p or "$.level" in p for p in problems_of(level="strong"))
    assert any("origin" in p for p in problems_of(origin="stolen"))
    assert problems_of(surprise=1)


def test_an_unknown_kind_or_a_path_not_in_the_profile_schema_is_a_problem():
    unknown = problems_of(expectations=[{"kind": "looks_nice"}])
    assert any("kind" in p for p in unknown)
    bad_path = problems_of(expectations=[{"kind": "field_empty", "path": "hero.colour"}])
    assert any("hero.colour" in p and "profile schema" in p for p in bad_path)
    assert any("needs 'text'" in p for p in problems_of(expectations=[{"kind": "text_present"}]))
    assert any(
        "not used" in p
        for p in problems_of(expectations=[{"kind": "no_price", "path": "hero.headline"}])
    )
    assert problems_of(expectations=[{"kind": "field_empty", "path": "hero.main_photo_id"}]) == []


def test_content_rules_reuse_the_services_and_catch_bad_values():
    assert any(
        "voivodeship" in p
        for p in problems_of(artist={**package()["artist"], "voivodeships": ["narnia"]})
    )
    assert any(
        "questionnaire.q_age_to" in p
        for p in problems_of(questionnaire={"q_age_from": 9, "q_age_to": 3})
    )
    assert any(
        "offers[0].price_pln" in p for p in problems_of(offers=[{"title": "A", "description": "b"}])
    )
    assert any(
        "not a YouTube" in p
        for p in problems_of(videos=[{"url": "https://example.invalid/x", "title": "t"}])
    )
    twice = [{"url": "https://youtu.be/aBcDeF12345", "title": "a"}] * 2
    assert any("twice" in p for p in problems_of(videos=twice))


def test_the_slug_must_match_the_folder():
    assert any("folder" in p for p in testset.check_package(package(), folder="inne"))


def test_synthetic_packages_may_hold_no_contact_data_and_no_real_site():
    assert any("contact" in p for p in problems_of(site_text="Pisz: jan.kowalski@gmail.com"))
    assert any("contact" in p for p in problems_of(site_text="Dzwoń: 601 234 567"))
    assert any(
        "real host" in p for p in problems_of(site_text="Zobacz https://teatr-prawdziwy.pl/oferta")
    )
    assert any("real site" in p for p in problems_of(site_text="Strona www.teatr-prawdziwy.pl"))
    assert problems_of(site_text="Zobacz https://x.example.invalid/oferta.") == []
    assert problems_of(site_text="Film https://www.youtube.com/watch?v=aBcDeF12345") == []


def test_check_all_reports_unreadable_files_without_raising(tmp_path):
    (tmp_path / "zepsuty").mkdir()
    (tmp_path / "zepsuty" / "package.json").write_text("{nope", encoding="utf-8")
    (tmp_path / "pusty").mkdir()
    ((a, pa, problems_a), (b, pb, problems_b)) = testset.check_all(tmp_path)
    assert (a, pa, b, pb) == ("pusty", None, "zepsuty", None)
    assert "no package.json" in problems_a[0] and "not valid JSON" in problems_b[0]
    with pytest.raises(testset.PackageError, match="pusty"):
        testset.packages(tmp_path)
    with pytest.raises(testset.PackageError, match="no such package"):
        testset.get_package("nie-ma")


# --- expectations ---------------------------------------------------------------------------


def profile(**changes) -> dict:
    base = {
        "hero": {
            "headline": "Teatr  Kwiatki",
            "subheadline": "",
            "main_photo_id": 7,
            "button_label": "",
        },
        "description": {"paragraphs": ["Spektakl dla dzieci. Bilet kosztuje 20 zł."]},
        "faq": [],
        "gaps": [{"code": "no_video", "message": "x"}],
        "testimonials": [],
    }
    base.update(changes)
    return base


def run(kind, profile_json, **item):
    (result,) = testset.check_expectations(
        {"slug": "x", "expectations": [{"kind": kind, **item}]}, profile_json
    )
    return result


def test_field_empty_and_field_not_empty():
    path = {"path": "hero.main_photo_id"}
    assert not run("field_empty", profile(), **path).passed
    with_none = profile(hero={"main_photo_id": None})
    assert run("field_empty", with_none, **path).passed
    assert run("field_not_empty", profile(), **path).passed
    assert not run("field_not_empty", with_none, **path).passed
    assert run("field_empty", profile(), path="testimonials").passed  # an empty list
    assert not run("field_not_empty", profile(), path="faq").passed
    assert run("field_empty", {}, path="hero.main_photo_id").passed  # a missing value is empty


def test_text_present_and_absent_ignore_case_and_whitespace():
    assert run("text_present", profile(), text="teatr kwiatki").passed
    assert not run("text_present", profile(), text="teatr lalek").passed
    assert run("text_absent", profile(), text="Teatr Lalek").passed
    failing = run("text_absent", profile(), text="DLA   dzieci")
    assert not failing.passed and "$.description.paragraphs[0]" in failing.message
    quote = profile(testimonials=[{"quote": "Cudowne!", "author": "A", "source_material_id": None}])
    assert run("text_present", quote, text="cudowne").passed


def test_no_price_fails_with_the_path_of_the_text_and_passes_without_a_price():
    failing = run("no_price", profile())
    assert not failing.passed and failing.detail == "$.description.paragraphs[0]"
    assert "$.description.paragraphs[0]" in failing.message
    assert run("no_price", profile(description={"paragraphs": ["Spektakl dla dzieci."]})).passed
    for price in (
        "od 1 200 zł", "800 PLN", "cena: 900", "Koszt to 500", "PLN 500", "500,-",
        "2 tys. zł", "1,5 tys. zł", "cenę 900", "500 złoty", "ceną od 700",
    ):  # fmt: skip
        text = profile(description={"paragraphs": [f"Występ {price}."]})
        assert not run("no_price", text).passed, price
    for clean in (
        "Występ trwa 45 minut.",
        "Cena na zapytanie dla 30 dzieci.",
        "Cena na zapytanie, czas 45 minut.",
        "Koszt dojazdu do 50 km wliczony.",
    ):
        assert run("no_price", profile(description={"paragraphs": [clean]})).passed, clean
    fact = profile(description={"paragraphs": ["x"]}, facts=[{"label": "Cena", "value": "od 900"}])
    result = run("no_price", fact)
    assert not result.passed and result.detail == "$.facts[0].value"


def test_gap_reported():
    assert run("gap_reported", profile(), code="no_video").passed
    failing = run("gap_reported", profile(), code="no_price")
    assert not failing.passed and "no_price" in failing.message


def test_unknown_kind_or_path_in_expectations_is_an_error_not_a_pass():
    for item in (
        {"kind": "vibes"},
        {"kind": "field_empty", "path": "hero.nope"},
        {"kind": "text_present"},
    ):
        with pytest.raises(testset.PackageError, match="x"):
            testset.check_expectations({"slug": "x", "expectations": [item]}, profile())


# --- drawing photos -------------------------------------------------------------------------


def test_photos_are_drawn_deterministically_in_the_requested_size():
    import io

    from PIL import Image

    spec = {"kind": "normal", "width": 400, "height": 300}
    first = testset.draw_photo(spec, "a:1")
    assert first == testset.draw_photo(spec, "a:1")
    assert first != testset.draw_photo(spec, "a:2")
    assert Image.open(io.BytesIO(first)).size == (400, 300)
    for kind, size in testset.PHOTO_SIZES.items():
        assert Image.open(io.BytesIO(testset.draw_photo({"kind": kind}, "s"))).size == size


# --- the loader -----------------------------------------------------------------------------


def snapshot(artist):
    return (
        Material.objects.filter(artist=artist).count(),
        Offer.objects.filter(artist=artist).count(),
        services.input_fingerprint(artist),
    )


def test_loading_creates_one_artist_with_the_package_content(no_network):
    artist = testset.load_package("teatr-lalek-pod-debem")
    assert artist.user.email == "testset-teatr-lalek-pod-debem@example.invalid"
    assert (artist.name, artist.city, artist.artist_type) == (
        "Teatr Lalek Pod Dębem",
        "Wrocław",
        "theatre",
    )
    data = inputs.build_input(artist)
    assert len(data["offers"]) == 3 and len(data["photos"]) == 5 and len(data["videos"]) == 2
    assert len(data["documents"]) == 2 and "Wrocławiu" in data["site_text"]
    assert data["questionnaire"]["q_duration_minutes"] == 45
    assert {v["title"] for v in data["videos"]} >= {"Kwiatowa opowieść – fragment spektaklu"}
    assert WebsiteImport.objects.get(artist=artist).url.endswith(".example.invalid/")


def test_loading_twice_changes_nothing():
    first = testset.load("zwierzaki-z-zagrody")
    before = snapshot(first.artist)
    second = testset.load("zwierzaki-z-zagrody")
    assert first.changed and not second.changed
    assert second.artist.pk == first.artist.pk
    assert snapshot(second.artist) == before
    assert (
        Artist.objects.filter(user__email="testset-zwierzaki-z-zagrody@example.invalid").count()
        == 1
    )
    assert TestsetLoad.objects.count() == 1


def test_a_changed_package_replaces_materials_and_offers(tmp_path):
    root = root_with(tmp_path)
    artist = testset.load_package("zwierzaki-z-zagrody", root=root)
    before = snapshot(artist)
    old_ids = set(Material.objects.filter(artist=artist).values_list("pk", flat=True))
    changed = json.loads(
        (root / "zwierzaki-z-zagrody" / "package.json").read_text(encoding="utf-8")
    )
    changed["offers"] = [{"title": "Nowy pokaz", "description": "Inny.", "price_on_request": True}]
    changed["photos"] = [{"kind": "normal", "width": 1300, "height": 900}]
    (root / "zwierzaki-z-zagrody" / "package.json").write_text(
        json.dumps(changed), encoding="utf-8"
    )
    again = testset.load_package("zwierzaki-z-zagrody", root=root)
    after = snapshot(again)
    assert again.pk == artist.pk and after[2] != before[2]
    assert not old_ids & set(Material.objects.filter(artist=artist).values_list("pk", flat=True))
    assert list(Offer.objects.filter(artist=artist).values_list("title", flat=True)) == [
        "Nowy pokaz"
    ]
    assert after[:2] == (1, 1)
    assert inputs.build_input(again)["photos"][0]["flags"] == []


def test_loading_never_touches_a_stored_generation():
    artist = testset.load_package("zwierzaki-z-zagrody")
    generation_row = services.start_generation(artist, "manual", COMPONENTS)
    services.finish_generation(generation_row, {"x": 1}, [], 0, Generation.Status.READY)
    Material.objects.filter(artist=artist).update(text="zmiana")  # force a changed digest below
    TestsetLoad.objects.update(digest="stale")
    testset.load_package("zwierzaki-z-zagrody")
    assert Generation.objects.filter(pk=generation_row.pk, status=Generation.Status.READY).exists()


def test_a_poster_photo_shows_its_flag_and_cannot_be_main():
    artist = testset.load_package("iluzjonista-marek")
    (photo,) = inputs.build_input(artist)["photos"]
    assert checks.Flag.POSTER in photo["flags"] and photo["can_be_main"] is False


def test_photo_kinds_get_their_flags():
    data = inputs.build_input(testset.load_package("teatr-lalek-pod-debem"))
    flags = [p["flags"] for p in data["photos"]]
    assert flags[:3] == [[], [], []]
    assert flags[3] == ["low_resolution"]
    assert "poster" in flags[4]
    assert [p["can_be_main"] for p in data["photos"]][4] is False
    assert sum(p["can_be_main"] for p in data["photos"]) == 4


def test_a_screenshot_photo_is_flagged_and_blocked(tmp_path):
    root = root_with(tmp_path, photos=[{"kind": "screenshot"}])
    (photo,) = inputs.build_input(testset.load_package("zwierzaki-z-zagrody", root=root))["photos"]
    assert "screenshot_or_ai" in photo["flags"] and photo["can_be_main"] is False


def test_the_rights_statement_makes_materials_count():
    artist = testset.load_package("pracownia-eureka")
    assert inputs.materials_allowed(artist)


def test_consented_packages_are_refused_and_create_no_rows(tmp_path):
    root = root_with(tmp_path, origin="consented")
    with pytest.raises(testset.PackageError, match="consent"):
        testset.load_package("zwierzaki-z-zagrody", root=root)
    assert Artist.objects.count() == 0 and TestsetLoad.objects.count() == 0


def test_an_invalid_package_is_refused_and_creates_no_rows(tmp_path):
    root = root_with(tmp_path, level="strong")
    with pytest.raises(testset.PackageError, match="zwierzaki-z-zagrody"):
        testset.load_package("zwierzaki-z-zagrody", root=root)
    assert Artist.objects.count() == 0
    with pytest.raises(testset.PackageError, match="no such package"):
        testset.load_package("nie-ma")


def test_loading_is_refused_when_the_lab_is_off(settings):
    settings.QUALITY_LAB_ENABLED = False
    with pytest.raises(testset.LabDisabled):
        testset.load_package("zwierzaki-z-zagrody")
    assert Artist.objects.count() == 0


# --- scripted profile, validator, expectations, generation job ------------------------------


@pytest.mark.parametrize("slug", SLUGS)
def test_the_scripted_profile_is_valid_clean_and_meets_every_expectation(slug):
    artist = testset.load_package(slug)
    data = inputs.build_input(artist)
    profile_json = scripted.scripted_profile(data)
    assert validation.schema_errors(profile_json) == []
    report = validator.validate_profile(profile_json, inputs.collect_sources(artist, data))
    assert report.hard == [], [f.line() for f in report.hard]
    results = testset.check_expectations(package(slug), profile_json)
    assert len(results) == len(package(slug)["expectations"])
    assert all(r.passed for r in results), [r.message for r in results if not r.passed]
    assert scripted.scripted_profile(data) == profile_json  # deterministic


def test_the_scripted_profile_reports_gaps_and_picks_a_usable_main_photo():
    poster_only = scripted.scripted_profile(
        inputs.build_input(testset.load_package("iluzjonista-marek"))
    )
    assert poster_only["hero"]["main_photo_id"] is None
    assert "no_main_photo" in [g["code"] for g in poster_only["gaps"]]
    rich = inputs.build_input(testset.load_package("teatr-lalek-pod-debem"))
    main = scripted.scripted_profile(rich)["hero"]["main_photo_id"]
    assert main in [p["id"] for p in rich["photos"] if p["can_be_main"]]


def test_the_existing_generation_job_gives_a_ready_generation(monkeypatch):
    artist = testset.load_package("teatr-lalek-pod-debem")
    reply = json.dumps(scripted.scripted_profile(inputs.build_input(artist)))
    client = ai.FakeClient(cost_usd="0.002", model="fake/model-1", reply=reply)
    monkeypatch.setattr(ai, "get_client", lambda: client)
    record = generation.request_generation(artist, "manual")
    done = generation.run_generation(record.pk)
    assert done.status == Generation.Status.READY
    assert done.input_fingerprint == services.input_fingerprint(artist)


# --- commands -------------------------------------------------------------------------------


def command(name, *args):
    out = StringIO()
    call_command(name, *args, stdout=out)
    return out.getvalue()


def test_testset_check_prints_the_table_and_exits_zero():
    output = command("testset_check")
    lines = output.splitlines()
    assert lines[0].split() == ["slug", "origin", "level", "type", "expectations"]
    assert [line.split()[0] for line in lines[1:31]] == SLUGS
    assert "30 valid package(s) of 30" in lines[-1]
    assert "teatr-lalek-pod-debem" in output and "rich" in output and "science_show" in output


def test_testset_check_fails_naming_the_package_and_the_problem(tmp_path, monkeypatch):
    root = root_with(tmp_path, level="strong")
    shutil.copytree(testset.TESTSET_DIR / "gliniane-ludki", root / "gliniane-ludki")
    monkeypatch.setattr(testset, "TESTSET_DIR", root)
    with pytest.raises(CommandError) as raised:
        command("testset_check")
    message = str(raised.value)
    assert "zwierzaki-z-zagrody" in message and "level" in message
    assert "gliniane-ludki" not in message


def test_testset_load_loads_one_package_and_repeats_with_the_same_fingerprint():
    first = command("testset_load", "--package", "zwierzaki-z-zagrody")
    second = command("testset_load", "--package", "zwierzaki-z-zagrody")
    assert "loaded" in first and "unchanged" in second
    fingerprint = first.split("fingerprint=")[1].strip()
    assert fingerprint == second.split("fingerprint=")[1].strip()
    assert "materials=1 offers=1" in first
    assert Artist.objects.count() == 1


def test_testset_load_without_a_package_loads_them_all():
    output = command("testset_load")
    assert len(output.strip().splitlines()) == 30
    assert Artist.objects.count() == 30


def test_testset_load_reports_a_refusal_as_an_error():
    with pytest.raises(CommandError, match="no such package"):
        command("testset_load", "--package", "nie-ma")


@pytest.mark.parametrize(
    "name,args", [("testset_check", ()), ("testset_load", ("--package", "zwierzaki-z-zagrody"))]
)
def test_both_commands_refuse_when_the_lab_is_off(settings, name, args):
    settings.QUALITY_LAB_ENABLED = False
    with pytest.raises(CommandError, match="QUALITY_LAB_ENABLED"):
        command(name, *args)
    assert Artist.objects.count() == 0 and TestsetLoad.objects.count() == 0


def test_a_package_above_the_material_limits_is_reported_not_half_loaded(tmp_path, settings):
    settings.MATERIAL_MAX_PHOTOS = 2
    problems = testset.check_package(package("teatr-lalek-pod-debem"))
    assert any(p.startswith("photos:") and "limit is 2" in p for p in problems)
    root = root_with(tmp_path, "teatr-lalek-pod-debem")
    with pytest.raises(testset.PackageError, match="photos"):
        testset.load_package("teatr-lalek-pod-debem", root=root)
    assert Artist.objects.count() == 0


def test_a_malformed_url_in_a_text_is_a_problem_not_a_crash():
    data = copy.deepcopy(package("zwierzaki-z-zagrody"))
    data["site_text"] += " Zobacz http://[x tutaj."
    assert any("malformed URL" in p for p in testset.check_package(data))
