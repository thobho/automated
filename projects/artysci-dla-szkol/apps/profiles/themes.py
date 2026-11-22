"""Page themes (US-3.2): a closed list, one source of truth for the colours, WCAG contrast.

`THEME_TOKENS` maps each theme to its colour tokens. `static/profiles/themes.css` holds the same
values as CSS custom properties (one `[data-theme="<slug>"]` block per theme); a test parses the
CSS and compares it with this mapping, so the two cannot drift. Another test checks the contrast
of the pairs in `TEXT_PAIRS` (4.5:1) and `LARGE_PAIRS` (3:1).

Adding a fifth theme: see README, "Page themes".
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Theme(models.TextChoices):
    # Slugs are the values of the `theme` enum in the AI profile schema (quality/schemas).
    BURGUNDY_LIGHT = "burgundy_light", _("Jasny burgund")
    CREAM_GREEN = "cream_green", _("Kremowa zieleń")
    NAVY_GOLD = "navy_gold", _("Granat ze złotem")
    CORAL_DARK = "coral_dark", _("Ciemny koral")


DEFAULT_THEME = Theme.BURGUNDY_LIGHT

# token -> meaning
#   paper        page background            ink        body text
#   muted        secondary text             heading    headings
#   link         links on paper and card    card       cards/pills background (text = ink)
#   band         "for schools" background  band-ink    text on the band, band-link links there
#   accent       button background          accent-ink button text
#   accent-hover button hover background    focus      focus outline colour
#   line         decorative borders (not text)
THEME_TOKENS: dict[str, dict[str, str]] = {
    Theme.BURGUNDY_LIGHT: {
        "paper": "#fbf8f4",
        "ink": "#1d1b20",
        "muted": "#5a5663",
        "heading": "#6b1530",
        "link": "#7a1f3d",
        "card": "#ffffff",
        "band": "#f3e6e8",
        "band-ink": "#1d1b20",
        "band-link": "#7a1f3d",
        "accent": "#7a1f3d",
        "accent-ink": "#ffffff",
        "accent-hover": "#5c1630",
        "focus": "#7a1f3d",
        "line": "#e4dcd2",
    },
    Theme.CREAM_GREEN: {
        "paper": "#faf6e9",
        "ink": "#1f2a22",
        "muted": "#4f5d52",
        "heading": "#1e4d33",
        "link": "#1e5c3a",
        "card": "#fffdf5",
        "band": "#e6eedb",
        "band-ink": "#1f2a22",
        "band-link": "#1e5c3a",
        "accent": "#1e5c3a",
        "accent-ink": "#ffffff",
        "accent-hover": "#143f28",
        "focus": "#1e5c3a",
        "line": "#d9d4bc",
    },
    Theme.NAVY_GOLD: {
        "paper": "#0f1f3d",
        "ink": "#f4efe0",
        "muted": "#c5c9d6",
        "heading": "#e8c36a",
        "link": "#f0cd7a",
        "card": "#172c54",
        "band": "#1c335f",
        "band-ink": "#f4efe0",
        "band-link": "#f0cd7a",
        "accent": "#e8c36a",
        "accent-ink": "#0f1f3d",
        "accent-hover": "#f5d98f",
        "focus": "#f0cd7a",
        "line": "#34497a",
    },
    Theme.CORAL_DARK: {
        "paper": "#1e1a1c",
        "ink": "#f6ede9",
        "muted": "#cdbfba",
        "heading": "#ff9a85",
        "link": "#ff9a85",
        "card": "#2b2427",
        "band": "#33292d",
        "band-ink": "#f6ede9",
        "band-link": "#ff9a85",
        "accent": "#ff8a73",
        "accent-ink": "#1e1a1c",
        "accent-hover": "#ffa391",
        "focus": "#ff9a85",
        "line": "#4a3e42",
    },
}

# (foreground token, background token): normal text, at least 4.5:1.
TEXT_PAIRS = [
    ("ink", "paper"),  # body text
    ("muted", "paper"),
    ("heading", "paper"),
    ("link", "paper"),
    ("ink", "card"),
    ("muted", "card"),
    ("link", "card"),
    ("accent-ink", "accent"),  # button text
    ("accent-ink", "accent-hover"),
    ("band-ink", "band"),  # "for schools" band
    ("band-link", "band"),
    ("heading", "band"),
]
# Large text, focus outline and graphics: at least 3:1.
LARGE_PAIRS = [
    ("focus", "paper"),
    ("focus", "card"),
    ("focus", "band"),
    ("accent", "paper"),  # frame of the initial, price accent
]

AA_TEXT = 4.5
AA_LARGE = 3.0


def _channel(value: int) -> float:
    c = value / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(color: str) -> float:
    h = color.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(fg: str, bg: str) -> float:
    """WCAG 2.x contrast ratio of two `#rrggbb` colours: 1 (equal) to 21 (black on white)."""
    lighter, darker = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def theme_or_default(value) -> str:
    """The slug when it is one of the four themes, otherwise the default (never raises)."""
    return value if value in Theme.values else DEFAULT_THEME.value
