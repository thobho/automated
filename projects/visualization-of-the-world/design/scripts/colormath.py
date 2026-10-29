"""Colour maths for the design-system checks. Python 3 standard library only.

- WCAG 2.x relative luminance and contrast ratio
  (https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio)
- OKLab / OKLCH (Bjorn Ottosson, https://bottosson.github.io/posts/oklab/)
- Colour-vision-deficiency simulation with the Machado, Oliveira & Fernandes (2009)
  matrices at severity 1.0, applied in linear RGB - the same model and thresholds as
  the dataviz skill's validate_palette.js, so results match it.
"""
import math
import re

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

MACHADO = {
    "protan": ((0.152286, 1.052583, -0.204868),
               (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968),
               (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
}


def is_hex(value):
    return isinstance(value, str) and bool(_HEX.match(value))


def hex_to_srgb(value):
    if not is_hex(value):
        raise ValueError(f"not a #rrggbb colour: {value!r}")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5))


def _to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_rgb(value):
    return tuple(_to_linear(c) for c in hex_to_srgb(value))


def relative_luminance(value):
    r, g, b = linear_rgb(value)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b):
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _oklab_from_linear(rgb):
    r, g, b = rgb
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklab(value):
    return _oklab_from_linear(linear_rgb(value))


def oklch(value):
    """Return (L, C, hue in degrees)."""
    L, a, b = oklab(value)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def simulate(value, kind):
    m = MACHADO[kind]
    rgb = linear_rgb(value)
    return tuple(min(1.0, max(0.0, sum(m[i][k] * rgb[k] for k in range(3)))) for i in range(3))


def delta_e(a, b, kind=None):
    """Euclidean OKLab distance x100. kind=None is normal vision, else 'protan'/'deutan'."""
    la = _oklab_from_linear(simulate(a, kind) if kind else linear_rgb(a))
    lb = _oklab_from_linear(simulate(b, kind) if kind else linear_rgb(b))
    return 100 * math.dist(la, lb)
