"""Alternative texts of the public page (US-3.6). No AI call: the artist's own text when there
is one, otherwise a Polish fallback built from the artist's name and the photo's position."""

from django.utils.translation import gettext as _

ALT_MAX_LENGTH = 200


def fallback_photo_alt(artist_name: str, position: int) -> str:
    """Polish fallback, e.g. "Teatr Kwiatki – zdjęcie 2" (position counts from 1)."""
    name = " ".join((artist_name or "").split())
    if not name:
        return _("Zdjęcie %(n)d") % {"n": position}
    return _("%(name)s – zdjęcie %(n)d") % {"name": name, "n": position}


def photo_alt(stored: str, artist_name: str, position: int) -> str:
    """The stored alt text (whitespace trimmed) or the fallback. Never empty: a photo that
    carries content must have a text; decorative images use an empty `alt` in the template."""
    text = " ".join((stored or "").split())[:ALT_MAX_LENGTH]
    return text or fallback_photo_alt(artist_name, position)
