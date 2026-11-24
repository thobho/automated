"""Contact data in texts that go public (D9: no e-mail or phone on the public page).

Detection is the AI scrubber's (`ai/scrub.py`); here the text is first normalised so that common
spellings are caught and ordinary dates and price ranges are not taken for phone numbers.
"""

import re
import unicodedata

from .ai.scrub import emails_in, phones_in

_DASHES = re.compile("[‐‑‒–—−]")
_DATE = re.compile(r"(?<!\d)\d{1,2}(?:\s*-\s*\d{1,2})?\.\d{1,2}\.\d{4}(?!\d)")
# At most six digits, not preceded by another digit group: "600 700 800 - 900 zł" keeps its phone.
_AMOUNT = r"(?:\d{1,3}[ .]\d{3}|\d{1,6})(?:,\d{2})?"
_PRICE_RANGE = re.compile(rf"(?<![\d+])(?<!\d[ .-]){_AMOUNT}\s*-\s*{_AMOUNT}\s*(?:zł|pln)\b", re.I)


def contacts_in(text: str, also: str = "") -> list[str]:
    """E-mail addresses and phone numbers in `text` (unique, in order of kind). `also` is one
    address that counts however it is written (the artist's login e-mail)."""
    text = unicodedata.normalize("NFKC", text or "")
    text = _DASHES.sub("-", text)
    found = emails_in(text)
    if also and also.lower() in text.lower() and also.lower() not in map(str.lower, found):
        found.append(also)
    text = _DATE.sub(" | ", text)
    text = _PRICE_RANGE.sub(" | ", text)
    text = re.sub(r":(?!\d)", " ", text)  # "600 700 800: dzwoń" (the scrubber skips "1:30" times)
    return found + phones_in(text)
