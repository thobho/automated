"""Theme choice of the artist page (US-3.2).

The artist's own choice is stored on `Artist.theme` (empty = not chosen yet; there is no stored
page draft before US-2.6). Without a choice, the theme proposed by the latest usable generation
is used (US-2.5), otherwise the default. A later generation therefore never overrides a choice.
"""

from apps.artists.models import Artist
from apps.quality.models import Generation

from .themes import DEFAULT_THEME, Theme, theme_or_default


class InvalidTheme(ValueError):
    pass


def set_theme(artist: Artist, slug: str) -> None:
    """Store the artist's choice. Only the four known slugs are accepted."""
    if slug not in Theme.values:
        raise InvalidTheme(slug)
    artist.theme = slug
    artist.save(update_fields=["theme"])


def ai_proposed_theme(artist: Artist) -> str | None:
    """The valid `theme` of the latest finished generation (`gotowa` or `do przeglądu`)."""
    record = (
        Generation.objects.filter(
            artist=artist, status__in=[Generation.Status.READY, Generation.Status.REVIEW]
        )
        .order_by("-started_at", "-pk")
        .first()
    )
    result = record.result if record is not None else None
    proposed = result.get("theme") if isinstance(result, dict) else None
    return proposed if isinstance(proposed, str) and proposed in Theme.values else None


def theme_for(artist: Artist) -> str:
    """Choice of the artist, else a valid AI proposal, else the default. Never raises."""
    if artist.theme in Theme.values:
        return artist.theme
    return theme_or_default(ai_proposed_theme(artist) or DEFAULT_THEME.value)
