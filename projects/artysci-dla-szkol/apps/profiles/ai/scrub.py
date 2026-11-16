"""PII minimisation (D59): remove contact data before any text goes to an AI provider.

Only artists' marketing materials are sent to AI, but they often contain a booking e-mail, a
phone number or a bank account. Those are replaced by placeholders, and so are the names in a
configured list (`AI_SCRUB_NAMES`, plus names passed per call). Pure functions, no Django.
"""

import re
from collections.abc import Iterable

EMAIL = "[email]"
PHONE = "[phone]"
IBAN = "[iban]"
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


def _phone(match: re.Match) -> str:
    text = match.group(0)
    digits = sum(ch.isdigit() for ch in text)
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
    """Return `text` without e-mails, phone numbers, IBANs/account numbers and listed names."""
    text = _EMAIL.sub(EMAIL, text)
    text = _IBAN.sub(IBAN, text)
    text = _NRB.sub(IBAN, text)
    text = _PHONE.sub(_phone, text)
    pattern = _names_pattern(names)
    if pattern is not None:
        text = pattern.sub(NAME, text)
    return text


def scrub_messages(messages: list[dict], names: Iterable[str] = ()) -> list[dict]:
    """Copy of chat `messages` with every string `content` scrubbed."""
    names = list(names)
    cleaned = []
    for message in messages:
        message = dict(message)
        if isinstance(message.get("content"), str):
            message["content"] = scrub(message["content"], names)
        cleaned.append(message)
    return cleaned
