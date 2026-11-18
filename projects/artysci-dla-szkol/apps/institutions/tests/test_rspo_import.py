"""RSPO CSV import (US-1.4): upsert by RSPO number, encoding, delimiter, skips, the command."""

import logging
import re

import pytest
from django.core.management import CommandError, call_command

from apps.institutions import services
from apps.institutions.models import RspoEntry

from .rspo_fixture import FIXTURE, HEADER, ROWS, build

pytestmark = pytest.mark.django_db


def run(capsys, path) -> str:
    call_command("import_rspo", str(path))
    return capsys.readouterr().out


def test_committed_fixture_is_the_generated_one():
    """The committed file has the real header and only synthetic data."""
    data = FIXTURE.read_bytes()
    assert data == build()
    text = data.decode("utf-8-sig")
    assert text.splitlines()[0].count(";") == len(HEADER) - 1
    addresses = re.findall(r"[^\";]*@[^\";]*", text)
    assert addresses and all(a.lower().endswith(".example.invalid") for a in addresses)


def test_fixture_imported_twice_creates_five_rows_then_changes_nothing(capsys):
    first = run(capsys, FIXTURE)
    second = run(capsys, FIXTURE)
    assert RspoEntry.objects.count() == 5
    assert "import_rspo: created 5, updated 0, unchanged 0, skipped 0, verified 0" in first
    assert "import_rspo: created 0, updated 0, unchanged 5, skipped 0, verified 0" in second


def test_changed_name_updates_without_duplicating(tmp_path):
    services.import_rspo(build())
    rows = [ROWS[0][:2] + ("Szkoła Podstawowa nr 5 Nowa Nazwa",) + ROWS[0][3:], *ROWS[1:]]
    report = services.import_rspo(build(rows))
    assert (report.created, report.updated, report.unchanged) == (0, 1, 4)
    assert RspoEntry.objects.filter(rspo_number=990001).count() == 1
    entry = RspoEntry.objects.get(rspo_number=990001)
    assert entry.name == "Szkoła Podstawowa nr 5 Nowa Nazwa"
    assert entry.name_search == "szkoła podstawowa nr 5 nowa nazwa"


def test_row_without_rspo_number_is_skipped_and_its_content_never_shown(tmp_path, capsys, caplog):
    secret_name = "Szkoła Bez Numeru Tajna"
    rows = [*ROWS, (None, "Szkoła podstawowa", secret_name, "OPOLSKIE", "Opole", "x@y.invalid")]
    path = tmp_path / "export.csv"
    path.write_bytes(build(rows))
    with caplog.at_level(logging.DEBUG):
        out = run(capsys, path)
    assert "created 5, updated 0, unchanged 0, skipped 1" in out
    assert RspoEntry.objects.count() == 5
    everything = out + caplog.text + "".join(str(r.__dict__) for r in caplog.records)
    assert secret_name not in everything and "y.invalid" not in everything


@pytest.mark.parametrize(
    "bad",
    [
        ("abc", "Szkoła podstawowa", "Zła", "OPOLSKIE", "Opole", ""),  # not a number
        (990009, "Szkoła podstawowa", "", "OPOLSKIE", "Opole", ""),  # no name
        (990009, "Szkoła podstawowa", "Zła", "OPOLSKIE", "", ""),  # no locality
        (990009, "Szkoła podstawowa", "Zła", "BAWARIA", "Opole", ""),  # unknown voivodeship
        (0, "Szkoła podstawowa", "Zła", "OPOLSKIE", "Opole", ""),  # zero
    ],
)
def test_invalid_rows_are_counted_as_skipped(bad):
    report = services.import_rspo(build([bad]))
    assert (report.created, report.skipped) == (0, 1)


def test_blank_lines_are_ignored():
    report = services.import_rspo(build(ROWS[:1]) + b"\r\n\r\n")
    assert (report.created, report.skipped) == (1, 0)


def test_fields_are_mapped_from_the_export():
    services.import_rspo(build())
    school = RspoEntry.objects.get(rspo_number=990001)
    assert (school.institution_type, school.voivodeship, school.locality) == (
        "primary_school",
        "dolnoslaskie",
        "Wrocław",
    )
    assert school.email_domain == "sp5.example.invalid"
    kindergarten = RspoEntry.objects.get(rspo_number=990002)
    assert kindergarten.institution_type == "kindergarten"
    assert kindergarten.email_domain == "przedszkole1.example.invalid"  # lower-cased
    assert RspoEntry.objects.get(rspo_number=990003).institution_type == "secondary_school"
    assert RspoEntry.objects.get(rspo_number=990003).email_domain == ""  # no address
    assert RspoEntry.objects.get(rspo_number=990003).voivodeship == "lodzkie"
    assert RspoEntry.objects.get(rspo_number=990004).institution_type == "culture_centre"
    assert RspoEntry.objects.get(rspo_number=990004).voivodeship == "slaskie"
    bursa = RspoEntry.objects.get(rspo_number=990005)
    assert (bursa.institution_type, bursa.email_domain) == ("other", "")  # "nie-adres"


def test_windows_1250_and_comma_delimiter():
    report = services.import_rspo(build(delimiter=",", encoding="cp1250"))
    assert report.created == 5
    assert RspoEntry.objects.get(rspo_number=990003).locality == "Łódź"


def test_tab_delimited_utf8_without_bom():
    assert services.import_rspo(build(delimiter="\t", encoding="utf-8")).created == 5


def test_header_matching_ignores_case_and_spaces():
    header = [column.upper().replace(" ", "  ") for column in HEADER]
    assert services.import_rspo(build(header=header)).created == 5


def test_missing_required_column_is_an_error():
    header = ["Numer RSPO", "Nazwa", "Typ", "Miejscowość"]
    with pytest.raises(services.RspoImportError, match="Województwo"):
        services.import_rspo(build([], header=header))


def test_without_email_column_the_domain_is_kept_and_reported(capsys, tmp_path):
    services.import_rspo(build())
    columns = ["Numer RSPO", "Typ", "Nazwa", "Województwo", "Miejscowość"]
    path = tmp_path / "no_email.csv"
    path.write_bytes(build([list(row[:5]) for row in ROWS], header=columns))
    out = run(capsys, path)
    assert "created 0, updated 0, unchanged 5" in out
    assert "no e-mail column, the domain rule is off" in out
    assert RspoEntry.objects.get(rspo_number=990001).email_domain == "sp5.example.invalid"


def test_empty_file_and_unknown_encoding_are_errors():
    with pytest.raises(services.RspoImportError):
        services.import_rspo(b"")
    with pytest.raises(services.RspoImportError):
        services.import_rspo(b"\x81\x81\x98")  # undefined in cp1250 and invalid UTF-8


def test_malformed_csv_is_an_error():
    data = build(ROWS[:1]) + b'"990009";"' + b"x" * 200_000 + b'"\r\n'  # over the field limit
    with pytest.raises(services.RspoImportError, match="malformed"):
        services.import_rspo(data)


def test_command_reports_unreadable_file_and_bad_file(tmp_path):
    with pytest.raises(CommandError, match="cannot read"):
        call_command("import_rspo", str(tmp_path / "missing.csv"))
    bad = tmp_path / "bad.csv"
    bad.write_bytes(b"a;b\r\n1;2\r\n")
    with pytest.raises(CommandError, match="missing columns"):
        call_command("import_rspo", str(bad))


@pytest.mark.parametrize(
    ("address", "domain"),
    [
        ("dyrektor@SP5.example.invalid", "sp5.example.invalid"),
        ("  a@b.example.invalid. ", "b.example.invalid"),
        ("brak", ""),
        ("a@localhost", ""),
        ("a@bad_domain.invalid", ""),
        ("", ""),
    ],
)
def test_email_domain(address, domain):
    assert services.email_domain(address) == domain


def test_seed_rows_and_registry_rows_share_the_upsert():
    entry, created = services.add_rspo_entry(990100, "Szkoła X", "other", "Opole", "opolskie")
    assert created and entry.email_domain == ""
    assert services.upsert_rspo_entry(990100, "Szkoła X", "other", "Opole", "opolskie") is (
        services.Upsert.UNCHANGED
    )
