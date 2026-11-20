import time

import pytest

from apps.profiles.ai.scrub import scrub, scrub_messages


@pytest.mark.parametrize(
    "text",
    [
        "Kontakt: jan.kowalski@example.invalid",
        "pisz na Booking+Teatr@poczta.example.invalid.",
    ],
)
def test_emails_removed(text):
    out = scrub(text)
    assert "@" not in out
    assert "[email]" in out


@pytest.mark.parametrize(
    "phone",
    [
        "+48 601 234 567",
        "601-234-567",
        "601234567",
        "(22) 123 45 67",
        "0048 601 234 567",
        "+48601234567",
        "22 123-45-67",
    ],
)
def test_phone_numbers_removed(phone):
    out = scrub(f"Zadzwoń: {phone} po 16.")
    assert out == "Zadzwoń: [phone] po 16."


@pytest.mark.parametrize(
    "kept",
    [
        "Koncert 2026-11-13 o 18:00",
        "Koncert 13.11.2026 18:00, sala 2",
        "Gramy od 1999 roku, 120 koncertów",
        "Cena: 1500 zł za 45 minut",
        "Lata 2010-2020",
    ],
)
def test_dates_prices_and_years_kept(kept):
    assert scrub(kept) == kept


@pytest.mark.parametrize(
    "account",
    [
        "PL61 1090 1014 0000 0712 1981 2874",
        "PL61109010140000071219812874",
        "61 1090 1014 0000 0712 1981 2874",
        "DE89 3704 0044 0532 0130 00",
    ],
)
def test_ibans_and_account_numbers_removed(account):
    out = scrub(f"Konto: {account}.")
    assert out == "Konto: [iban]."


def test_configured_names_removed_case_insensitive_whole_words():
    text = "Anna Nowak i ANNA  NOWAK grają z Annabelle. Nowakowski też."
    out = scrub(text, names=["Anna Nowak", "Nowak"])
    assert out == "[name] i [name] grają z Annabelle. Nowakowski też."


def test_no_names_means_names_untouched():
    assert scrub("Anna Nowak", names=["", "  "]) == "Anna Nowak"


def test_prompt_with_email_and_phone_has_neither():
    text = "Zespół Dźwięki. Rezerwacje: zespol@example.invalid, tel. +48 601 234 567."
    out = scrub(text)
    assert "zespol@example.invalid" not in out
    assert "601" not in out
    assert out == "Zespół Dźwięki. Rezerwacje: [email], tel. [phone]."


@pytest.mark.parametrize("filler", ["x", "1 ", "a.", "PL"])
def test_long_text_scrubs_in_linear_time(filler):
    text = filler * 100_000 + " a@example.invalid"
    started = time.monotonic()
    out = scrub(text)
    assert time.monotonic() - started < 2
    assert out.endswith("[email]")


VALID_PESEL = "44051401359"
VALID_ID_CARD = "ABA300000"


@pytest.mark.parametrize("pesel", [VALID_PESEL, "02070803628"])
def test_valid_pesel_removed(pesel):
    assert scrub(f"PESEL: {pesel}, dziękujemy.") == "PESEL: [pesel], dziękujemy."


@pytest.mark.parametrize(
    "kept",
    [
        "Numer zamówienia 44051401358 z wtorku",  # wrong checksum
        "Kod 12345678901",  # wrong checksum
        "Seria 440514013590",  # 12 digits
        "ID x44051401359",  # inside a word
    ],
)
def test_eleven_digits_without_pesel_checksum_kept(kept):
    assert scrub(kept) == kept


@pytest.mark.parametrize("card", [VALID_ID_CARD, "ABA 300000"])
def test_valid_id_card_removed(card):
    assert scrub(f"Dowód {card}.") == "Dowód [id_card]."


@pytest.mark.parametrize(
    "kept",
    [
        "Dowód ABA300001",  # wrong checksum
        "kod aba300000",  # lower case: not an ID card
        "XABA300000",  # longer token
        "Sala ABC123",  # too few digits
    ],
)
def test_id_card_false_positives_kept(kept):
    assert scrub(kept) == kept


def test_all_identifiers_in_one_text():
    text = (
        f"Konto PL61 1090 1014 0000 0712 1981 2874, NRB 61 1090 1014 0000 0712 1981 2874, "
        f"PESEL {VALID_PESEL}, dowód {VALID_ID_CARD}, inny numer 44051401358."
    )
    assert scrub(text) == (
        "Konto [iban], NRB [iban], PESEL [pesel], dowód [id_card], inny numer 44051401358."
    )


def test_contact_helpers_list_emails_and_phones_only():
    from apps.profiles.ai.scrub import emails_in, phones_in

    text = (
        "Pisz: a@example.invalid lub a@example.invalid, tel. +48 601  234 567, "
        f"konto 61 1090 1014 0000 0712 1981 2874, PESEL {VALID_PESEL}"
    )
    assert emails_in(text) == ["a@example.invalid"]
    assert phones_in(text) == ["+48 601 234 567"]


def test_scrub_messages_copies_and_scrubs_content():
    messages = [{"role": "user", "content": "mail a@example.invalid"}]
    out = scrub_messages(messages)
    assert out == [{"role": "user", "content": "mail [email]"}]
    assert messages[0]["content"] == "mail a@example.invalid"  # input untouched
