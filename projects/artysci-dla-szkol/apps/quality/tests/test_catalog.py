"""Error catalog (US-11.7): the real catalog, every failure with temporary catalog files, the
command, the manifest. No network, no AI calls."""

import copy
import json
from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from apps.accounts.tests.conftest import queue  # noqa: F401  (fixture)
from apps.quality import catalog, registry
from config.settings.storage import build_storages

pytestmark = pytest.mark.django_db

SLUG = "gliniane-ludki"


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


def entry(**changes):
    base = {
        "code": "jezyk-procesu",
        "name": "Język procesu",
        "description": "Opis.",
        "found": "2026-11-18",
        "handling": {"kind": "validator_rule", "rule": "RULE_PHRASES"},
        "cases": [
            {
                "kind": "validator",
                "package": SLUG,
                "fixture": "jezyk-procesu/gliniane-ludki.json",
            }
        ],
    }
    return {**base, **changes}


@pytest.fixture
def write(tmp_path):
    def _write(*entries):
        path = tmp_path / "catalog.json"
        path.write_text(
            json.dumps({"format": "error-catalog/1", "errors": list(entries)}), encoding="utf-8"
        )
        return path

    return _write


def run(path, **kw):
    return catalog.check(path, **kw)


# --- the real catalog ----------------------------------------------------------------------


def test_the_real_catalog_passes():
    """The same check as `manage.py error_catalog_check`: CI fails on a broken catalog."""
    results = catalog.check()
    assert [r.code for r in results] == [
        "jezyk-procesu",
        "fakt-z-nawiasem",
        "opinia-ucznia",
        "liczba-spoza-zrodel",
        "szacunek-bez-zastrzezenia",
        "opinia-nie-doslownie",
        "media-spoza-materialow",
        "obietnica-gwarancji",
        "przekroczony-limit-dlugosci",
    ]
    assert all(r.ok and r.cases for r in results), [r.line() for r in results]


def test_the_command_prints_a_line_per_entry():
    out = StringIO()
    call_command("error_catalog_check", stdout=out)
    lines = out.getvalue().splitlines()
    assert lines[0].startswith(
        "jezyk-procesu [validator_rule RULE_PHRASES] OK: case gliniane-ludki"
    )
    assert lines[1].startswith("fakt-z-nawiasem [validator_rule RULE_FACTS] OK")
    assert lines[2].startswith(
        "opinia-ucznia [validator_rule RULE_PUPIL + instruction_example opinia-ucznia] OK"
    )
    assert lines[3].startswith("liczba-spoza-zrodel [validator_rule RULE_NUMBERS")
    assert lines[4].startswith("szacunek-bez-zastrzezenia [validator_rule RULE_HEDGE")
    assert lines[5].startswith("opinia-nie-doslownie [validator_rule RULE_QUOTES] OK")
    assert lines[6].startswith("media-spoza-materialow [validator_rule RULE_MEDIA] OK")
    assert lines[7].startswith("obietnica-gwarancji [validator_rule RULE_PHRASES] OK")
    assert lines[8].startswith("przekroczony-limit-dlugosci [validator_rule RULE_LENGTHS] OK")
    assert lines[9] == "9 of 9 entries ok"


def test_the_command_fails_and_names_the_entry(write):
    broken = entry(handling={"kind": "validator_rule", "rule": "RULE_NOPE"})
    path = write(broken)
    with pytest.raises(CommandError, match="jezyk-procesu"):
        from unittest import mock

        with mock.patch.object(catalog, "CATALOG_FILE", path):
            call_command("error_catalog_check", stdout=StringIO())


def test_the_command_needs_the_lab(settings):
    settings.QUALITY_LAB_ENABLED = False
    with pytest.raises(CommandError, match="QUALITY_LAB_ENABLED"):
        call_command("error_catalog_check", stdout=StringIO())


# --- failures ------------------------------------------------------------------------------


def test_an_unknown_rule_code_names_the_entry(write):
    [result] = run(write(entry(handling={"kind": "validator_rule", "rule": "RULE_NOPE"})))
    assert not result.ok and result.code == "jezyk-procesu"
    assert "RULE_NOPE is not defined" in result.errors[0]


def test_a_missing_instruction_anchor_names_the_entry(write, tmp_path):
    instructions = tmp_path / "instructions.md"
    instructions.write_text("Brak znacznika.", encoding="utf-8")
    handling = {"kind": "instruction_example", "anchor": "przyklad"}
    [result] = run(write(entry(handling=handling)), instructions=instructions)
    assert not result.ok and "<!-- katalog:przyklad --> is missing" in result.errors[0]


def test_an_instruction_anchor_that_exists_is_accepted(write, tmp_path):
    instructions = tmp_path / "instructions.md"
    instructions.write_text("Przykład\n<!-- katalog:przyklad -->\n", encoding="utf-8")
    handling = {"kind": "instruction_example", "anchor": "przyklad"}
    expectation = {"kind": "text_absent", "text": "x"}
    package = _package_with(expectation)
    case = {"kind": "expectation", "package": SLUG, "expectation": expectation}
    [result] = run(
        write(entry(handling=handling, cases=[case])),
        instructions=instructions,
        packages_root=package,
    )
    assert result.ok, result.line()


def test_a_fixture_the_validator_does_not_flag_fails_the_case(write, tmp_path):
    good = json.loads(
        (catalog.CASES_DIR / "jezyk-procesu/gliniane-ludki.json").read_text(encoding="utf-8")
    )
    good["description"]["paragraphs"][0] = "Warsztaty lepienia z gliny."
    (tmp_path / "jezyk-procesu").mkdir()
    (tmp_path / "jezyk-procesu/gliniane-ludki.json").write_text(json.dumps(good), encoding="utf-8")
    [result] = run(write(entry()), cases_dir=tmp_path)
    assert not result.ok
    assert "gliniane-ludki/jezyk-procesu/gliniane-ludki.json" in result.errors[0]
    assert "does not flag" in result.errors[0]


def test_a_missing_fixture_fails_the_case(write, tmp_path):
    [result] = run(write(entry()), cases_dir=tmp_path)
    assert "fixture is missing" in result.errors[0]


def test_a_fixture_that_breaks_the_profile_schema_fails_the_case(write, tmp_path):
    (tmp_path / "jezyk-procesu").mkdir()
    (tmp_path / "jezyk-procesu/gliniane-ludki.json").write_text("{}", encoding="utf-8")
    [result] = run(write(entry()), cases_dir=tmp_path)
    assert "breaks the profile schema" in result.errors[0]


def test_an_entry_without_a_case_fails(write):
    [result] = run(write(entry(cases=[])))
    assert result.errors == ["no regression case"]


def test_a_case_with_an_unknown_package_fails(write):
    case = {"kind": "validator", "package": "nie-ma-takiego", "fixture": "a/b.json"}
    [result] = run(write(entry(cases=[case])))
    assert "package nie-ma-takiego does not exist" in result.errors[0]


def test_a_case_with_a_package_that_is_not_synthetic_fails(write, tmp_path):
    root = _package_with(None, origin="consented")
    case = {"kind": "validator", "package": SLUG, "fixture": "a/b.json"}
    [result] = run(write(entry(cases=[case])), packages_root=root)
    assert "is not synthetic" in result.errors[0]


def test_an_expectation_the_package_does_not_have_fails(write):
    case = {
        "kind": "expectation",
        "package": SLUG,
        "expectation": {"kind": "text_absent", "text": "tego nie ma w paczce"},
    }
    [result] = run(write(entry(cases=[case])))
    assert "the package has no such expectation" in result.errors[0]


def test_an_expectation_the_package_has_passes(write):
    package = catalog.testset.get_package(SLUG)
    case = {"kind": "expectation", "package": SLUG, "expectation": package["expectations"][0]}
    [result] = run(write(entry(cases=[case])))
    assert result.ok, result.line()


def test_a_validator_case_needs_a_validator_rule(write, tmp_path):
    instructions = tmp_path / "i.md"
    instructions.write_text("<!-- katalog:a -->", encoding="utf-8")
    [result] = run(
        write(entry(handling={"kind": "instruction_example", "anchor": "a"})),
        instructions=instructions,
    )
    assert "needs a validator_rule" in result.errors[0]


def test_a_good_profile_flagged_by_the_rule_fails_the_case(write, tmp_path, monkeypatch):
    from apps.quality import scripted

    bad = json.loads(
        (catalog.CASES_DIR / "jezyk-procesu/gliniane-ludki.json").read_text(encoding="utf-8")
    )
    monkeypatch.setattr(scripted, "scripted_profile", lambda data: copy.deepcopy(bad))
    [result] = run(write(entry()))
    assert "scripted good profile is flagged" in result.errors[0]


# --- the catalog file ----------------------------------------------------------------------


def test_a_catalog_that_breaks_its_schema_fails_with_the_path(write):
    path = write(entry(code="Zły Kod"))
    with pytest.raises(catalog.CatalogError) as caught:
        catalog.load(path)
    assert caught.value.problems[0].startswith("$.errors[0].code")


def test_a_rule_with_an_anchor_that_is_missing_in_the_instructions_fails(write, tmp_path):
    instructions = tmp_path / "instructions.md"
    instructions.write_text("Brak znacznika.", encoding="utf-8")
    handling = {"kind": "validator_rule", "rule": "RULE_PHRASES", "anchor": "przyklad"}
    [result] = run(write(entry(handling=handling)), instructions=instructions)
    assert not result.ok and "<!-- katalog:przyklad --> is missing" in result.errors[0]


def test_a_handling_with_an_unknown_field_breaks_the_schema(write):
    handling = {"kind": "validator_rule", "rule": "RULE_FACTS", "extra": "a"}
    with pytest.raises(catalog.CatalogError):
        catalog.load(write(entry(handling=handling)))


def test_duplicate_codes_fail(write):
    with pytest.raises(catalog.CatalogError, match="duplicate code 'jezyk-procesu'"):
        catalog.load(write(entry(), entry()))


def test_an_unreadable_catalog_fails(tmp_path):
    with pytest.raises(catalog.CatalogError, match="file not found"):
        catalog.load(tmp_path / "nie-ma.json")
    broken = tmp_path / "x.json"
    broken.write_text("{", encoding="utf-8")
    with pytest.raises(catalog.CatalogError, match="not valid JSON"):
        catalog.load(broken)


def test_the_command_reports_a_broken_file(tmp_path, monkeypatch):
    broken = tmp_path / "x.json"
    broken.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(catalog, "CATALOG_FILE", broken)
    with pytest.raises(CommandError, match=r"\$: "):
        call_command("error_catalog_check", stdout=StringIO())


def test_codes_by_rule(monkeypatch, tmp_path):
    assert catalog.codes_by_rule() == {
        "bez języka procesu i bez dodanych obietnic": "jezyk-procesu",
        "fakty": "fakt-z-nawiasem",
        "opinie tylko od dorosłych i instytucji": "opinia-ucznia",
        "liczby i ceny tylko ze źródła": "liczba-spoza-zrodel",
        "zastrzeżenie ze źródła": "szacunek-bez-zastrzezenia",
        "opinie dosłownie": "opinia-nie-doslownie",
        "zdjęcia i filmy tylko z materiałów artysty": "media-spoza-materialow",
        "limity długości": "przekroczony-limit-dlugosci",
    }
    monkeypatch.setattr(catalog, "CATALOG_FILE", tmp_path / "nie-ma.json")
    assert catalog.codes_by_rule() == {}


# --- manifest ------------------------------------------------------------------------------


def test_the_catalog_is_a_registered_component_outside_the_generator():
    from apps.profiles.generator_components import COMPONENTS

    component = registry.registry.get("catalog", "error_catalog")
    assert component.version == "0.3" and component not in COMPONENTS
    assert not registry.manifest_errors([component], registry.load_manifest())


def test_a_catalog_change_without_a_version_bump_fails_the_manifest(tmp_path):
    copy_path = tmp_path / "error_catalog.json"
    copy_path.write_text(catalog.CATALOG_FILE.read_text(encoding="utf-8") + " ", encoding="utf-8")
    changed = registry.Component("catalog", "error_catalog", "0.2", files=(str(copy_path),))
    errors = registry.manifest_errors([changed], registry.load_manifest())
    assert "changed without a version bump" in errors[0]


def test_a_fixture_is_part_of_the_component():
    files = catalog.COMPONENT.files
    assert "apps/quality/error_cases/jezyk-procesu/gliniane-ludki.json" in files


# --- helpers -------------------------------------------------------------------------------


def _package_with(expectation, origin="synthetic"):
    """A temporary packages folder holding a copy of the real package with `expectation`."""
    import tempfile
    from pathlib import Path

    root = Path(tempfile.mkdtemp())
    package = copy.deepcopy(catalog.testset.get_package(SLUG))
    package["origin"] = origin
    if expectation is not None:
        package["expectations"] = [*package["expectations"], expectation]
    folder = root / SLUG
    folder.mkdir()
    (folder / "package.json").write_text(json.dumps(package), encoding="utf-8")
    return root
