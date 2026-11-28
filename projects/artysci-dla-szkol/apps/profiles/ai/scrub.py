"""PII minimisation (D59): remove contact data before any text goes to an AI provider.

Only artists' marketing materials are sent to AI, but they often contain a booking e-mail, a
phone number, a bank account or even a PESEL or ID card number (on invoices pasted to a
website). Those are replaced by placeholders, and so are the names in a
configured list (`AI_SCRUB_NAMES`, plus names passed per call). Pure functions, no Django.
"""

import re
from collections.abc import Iterable

EMAIL = "[email]"
PHONE = "[phone]"
IBAN = "[iban]"
PESEL = "[pesel]"
ID_CARD = "[id_card]"
NAME = "[name]"

# Patterns start only at a boundary (lookbehind) and repeat boundedly, so long texts scrub in
# linear time (no backtracking from every character of a long word).
_EMAIL = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
)
# IBAN with a country code (PL61 1090 1014 0000 0712 1981 2874), spaces optional.
_IBAN = re.compile(r"(?<![A-Za-z0-9])[A-Z]{2}\d{2}(?:[ -]?[A-Z0-9]){11,30}(?![A-Za-z0-9])")
# Polish account number (NRB) without the country code: 26 digits, usually grouped 2+4x6.
_NRB = re.compile(r"(?<!\d)\d{2}(?:[ -]?\d{4}){6}(?!\d)")
# Phone candidates: optional +/00 prefix, digits with spaces, dots, dashes or brackets.
# Not followed by ":" so "13.11.2026 18:00" stays a date and a time.
_PHONE = re.compile(r"(?<![\w+])(?:\+|00)?\(?\d[\d\s().-]{6,24}\d(?![\w:])")
_PHONE_MIN_DIGITS = 9  # PL numbers have 9 digits; shorter runs are dates, prices, years
_PHONE_MAX_DIGITS = 15  # E.164 maximum
# PESEL: 11 digits, the last one a checksum (weights 1 3 7 9 1 3 7 9 1 3).
_PESEL = re.compile(r"(?<![\w+])\d{11}(?!\w)")
_PESEL_WEIGHTS = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
# Polish ID card: 3 capital letters and 6 digits, the first digit a checksum (weights
# 7 3 1 for the letters, A=10 ... Z=35, and 7 3 1 7 3 for the other digits).
_ID_CARD = re.compile(r"(?<![A-Za-z0-9])([A-Z]{3}) ?(\d{6})(?![A-Za-z0-9])")
_ID_WEIGHTS = (7, 3, 1, 7, 3, 1, 7, 3)


def pesel_valid(digits: str) -> bool:
    if len(digits) != 11 or not digits.isdigit():
        return False
    total = sum(int(d) * w for d, w in zip(digits, _PESEL_WEIGHTS, strict=False))
    return (10 - total % 10) % 10 == int(digits[10])


def id_card_valid(letters: str, digits: str) -> bool:
    if len(letters) != 3 or len(digits) != 6 or not letters.isupper() or not digits.isdigit():
        return False
    values = [ord(ch) - ord("A") + 10 for ch in letters] + [int(d) for d in digits[1:]]
    return sum(v * w for v, w in zip(values, _ID_WEIGHTS, strict=True)) % 10 == int(digits[0])


def _pesel(match: re.Match) -> str:
    return PESEL if pesel_valid(match.group(0)) else match.group(0)


def _id_card(match: re.Match) -> str:
    return ID_CARD if id_card_valid(match.group(1), match.group(2)) else match.group(0)


def _phone(match: re.Match) -> str:
    text = match.group(0)
    digits = sum(ch.isdigit() for ch in text)
    if text.isdigit() and digits != _PHONE_MIN_DIGITS:
        # A bare run of digits is a phone only with exactly 9 digits; longer bare runs
        # (an 11-digit number that is not a PESEL, an order number) are kept.
        return text
    if _PHONE_MIN_DIGITS <= digits <= _PHONE_MAX_DIGITS:
        return PHONE
    return text


def _names_pattern(names: Iterable[str]) -> re.Pattern | None:
    cleaned = sorted({n.strip() for n in names if n and n.strip()}, key=len, reverse=True)
    if not cleaned:
        return None
    alternatives = "|".join(r"\s+".join(map(re.escape, n.split())) for n in cleaned)
    return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)", re.IGNORECASE)


def scrub(text: str, names: Iterable[str] = ()) -> str:
    """Return `text` without e-mails, IBANs/account numbers, PESEL and ID card numbers (valid
    checksum only), phone numbers and listed names."""
    text = _EMAIL.sub(EMAIL, text)
    text = _IBAN.sub(IBAN, text)
    text = _NRB.sub(IBAN, text)
    text = _PESEL.sub(_pesel, text)
    text = _ID_CARD.sub(_id_card, text)
    text = _PHONE.sub(_phone, text)
    pattern = _names_pattern(names)
    if pattern is not None:
        text = pattern.sub(NAME, text)
    return text


def emails_in(text: str) -> list[str]:
    """E-mail addresses the scrubber would remove (in order, unique)."""
    return list(dict.fromkeys(m.group(0) for m in _EMAIL.finditer(text)))


def phones_in(text: str) -> list[str]:
    """Phone numbers the scrubber would remove (in order, unique, whitespace normalised).
    Account, PESEL and ID card numbers are taken out first, so they are never listed."""
    for pattern, repl in ((_EMAIL, EMAIL), (_IBAN, IBAN), (_NRB, IBAN), (_PESEL, _pesel),
                          (_ID_CARD, _id_card)):  # fmt: skip
        text = pattern.sub(repl, text)
    found = (" ".join(m.group(0).split()) for m in _PHONE.finditer(text) if _phone(m) == PHONE)
    return list(dict.fromkeys(found))


def scrub_messages(messages: list[dict], names: Iterable[str] = ()) -> list[dict]:
    """Copy of chat `messages` with every string `content` scrubbed."""
    names = list(names)
    cleaned = []
    for message in messages:
        message = dict(message)
        content = message.get("content")
        if isinstance(content, str):
            message["content"] = scrub(content, names)
        elif isinstance(content, list):  # parts: text is scrubbed, images pass through
            message["content"] = [
                {**part, "text": scrub(part["text"], names)} if part.get("type") == "text" else part
                for part in content
            ]
        cleaned.append(message)
    return cleaned
