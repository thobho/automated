"""Builds the synthetic RSPO export fixture (`fixtures/rspo_sample.csv`) and variants of it.

The header is the real one from rspo.gov.pl "Pobierz CSV" (read 2026-11-18, D100); every row is
made up: RSPO numbers from 990001, `example.invalid` addresses, no real names (D57).
Regenerate the committed file with `uv run python -m apps.institutions.tests.rspo_fixture`.
"""

import csv
import io
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "rspo_sample.csv"

HEADER = [
    "Numer RSPO", "REGON", "NIP", "Typ", "Nazwa", "Kod terytorialny województwo",
    "Kod terytorialny powiat", "Kod terytorialny gmina", "Kod terytorialny miejscowość",
    "Kod terytorialny ulica", "Województwo", "Powiat", "Gmina", "Miejscowość",
    "Rodzaj miejscowości", "Ulica", "Numer budynku", "Numer lokalu", "Kod pocztowy", "Poczta",
    "Telefon", "Faks", "E-mail", "Strona www", "Publiczność status", "Kategoria uczniów",
    "Specyfika placówki", "Imię i nazwisko dyrektora", "Data założenia",
    "Data rozpoczęcia działalności", "Data likwidacji", "Typ organu prowadzącego",
    "Nazwa organu prowadzącego", "REGON organu prowadzącego", "NIP organu prowadzącego",
    "Województwo organu prowadzącego", "Powiat organu prowadzącego",
    "Gmina organu prowadzącego", "Miejsce w strukturze", "RSPO podmiotu nadrzędnego",
    "Typ podmiotu nadrzędnego", "Nazwa podmiotu nadrzędnego", "Liczba uczniów",
    "Tereny sportowe", "Języki nauczane", "Czy zatrudnia logopedę", "Czy zatrudnia psychologa",
    "Czy zatrudnia pedagoga", "Oddziały podstawowe wg specyfiki", "Oddziały dodatkowe",
    "Zawód", "Zawód artystyczny", "Zawód w KPSS", "Dziedzina BCU",
]  # fmt: skip

# (RSPO number, type, name, voivodeship, locality, e-mail)
ROWS = [
    (990001, "Szkoła podstawowa", "Szkoła Podstawowa nr 5 Testowa", "DOLNOŚLĄSKIE", "Wrocław",
     "sekretariat@sp5.example.invalid"),
    (990002, "Przedszkole", "Przedszkole Publiczne nr 1 Testowe", "OPOLSKIE", "Opole",
     "PP1@Przedszkole1.Example.Invalid"),
    (990003, "Liceum ogólnokształcące", "Liceum Ogólnokształcące nr 2 Testowe", "ŁÓDZKIE",
     "Łódź", ""),
    (990004, "Młodzieżowy dom kultury", "Młodzieżowy Dom Kultury Testowy", "ŚLĄSKIE",
     "Zębowice Testowe", "mdk@mdk.example.invalid"),
    (990005, "Bursa", "Bursa Szkolna nr 3 Testowa", "WARMIŃSKO-MAZURSKIE", "Olsztyn",
     "nie-adres"),
]  # fmt: skip


def row(number, kind, name, voivodeship, locality, email) -> list[str]:
    values = dict.fromkeys(HEADER, "")
    values.update(
        {
            "Numer RSPO": str(number) if number is not None else "",
            "Typ": kind,
            "Nazwa": name,
            "Województwo": voivodeship,
            "Miejscowość": locality,
            "E-mail": email,
            "Publiczność status": "publiczna",
            "Imię i nazwisko dyrektora": "Dyrektor Testowy",
        }
    )
    return [values[column] for column in HEADER]


def build(rows=ROWS, *, header=HEADER, delimiter=";", encoding="utf-8-sig") -> bytes:
    """CSV bytes like the export: quoted, `;`, UTF-8 with BOM, CRLF line ends."""
    out = io.StringIO()
    writer = csv.writer(out, delimiter=delimiter, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    writer.writerow(header)
    for values in rows:
        writer.writerow(row(*values) if len(values) == 6 else values)
    return out.getvalue().encode(encoding)


if __name__ == "__main__":
    FIXTURE.write_bytes(build())
