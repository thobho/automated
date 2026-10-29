#!/usr/bin/env python3
"""Generate tokens.css from tokens.json (Python 3 standard library only).

Usage:  python3 scripts/build_tokens.py          # writes ../tokens.css
        python3 scripts/build_tokens.py --check  # exit 1 if tokens.css is out of date

Theme and direction switching (classes on <html>):
  no class            -> default direction, light, or dark when the OS asks for dark
  .theme-light / .theme-dark -> force a theme
  .dir-<name>         -> an alternative direction (its light and dark values)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

FONT_FILES = [
    # (family name used in CSS, file stem, weight range)
    ("Public Sans Variable", "public-sans", "100 900"),
    ("Schibsted Grotesk Variable", "schibsted-grotesk", "400 900"),
    ("IBM Plex Sans Variable", "ibm-plex-sans", "100 700"),
    ("Atkinson Hyperlegible Next Variable", "atkinson-hyperlegible-next", "200 800"),
]
# unicode-range values as published by Fontsource 5.3.0 (see sources.md). Polish needs both:
# "ó" is in latin, "ą ć ę ł ń ś ź ż" are in latin-ext.
UNICODE_RANGE = {
    "latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,"
             "U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
    "latin-ext": "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,"
                 "U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,"
                 "U+2C60-2C7F,U+A720-A7FF",
}


def decl(name, value, indent="  "):
    return f"{indent}--{name}: {value};"


def font_faces():
    out = []
    for family, stem, weights in FONT_FILES:
        for subset in ("latin-ext", "latin"):
            out.append(
                "@font-face {\n"
                f"  font-family: \"{family}\";\n"
                "  font-style: normal;\n"
                "  font-display: swap;\n"
                f"  font-weight: {weights};\n"
                f"  src: url(\"fonts/{stem}-{subset}-wght-normal.woff2\") format(\"woff2\");\n"
                f"  unicode-range: {UNICODE_RANGE[subset]};\n"
                "}")
    return out


def direction_colours(d, theme):
    lines = [decl(f"color-{k}", v) for k, v in d[theme].items()]
    return lines


def direction_static(d):
    lines = [decl("font-display", d["fonts"]["display"]), decl("font-text", d["fonts"]["text"])]
    lines += [decl(f"neutral-{k}", v) for k, v in d["neutral"].items()]
    return lines


def data_theme(data, theme):
    lines = [decl(f"data-cat-{i + 1}", c) for i, c in enumerate(data["categorical"][theme])]
    lines += [decl(f"data-place-{k}", c) for k, c in zip(data["placeType"]["keys"], data["placeType"][theme])]
    lines += [decl(f"data-div-{i + 1}", c) for i, c in enumerate(data["diverging"][theme])]
    lines += [decl(f"data-map-{i + 1}", c) for i, c in enumerate(data["map"][theme])]
    return lines


def shadows(tokens, theme):
    return [decl(f"shadow-{k}", v) for k, v in tokens["shadow"][theme].items()]


def block(selector, lines, indent=""):
    inner = "\n".join(indent + line for line in lines)
    return f"{indent}{selector} {{\n{inner}\n{indent}}}"


def build(tokens):
    meta = tokens["meta"]
    default = meta["defaultDirection"]
    dirs = tokens["directions"]
    data = tokens["data"]
    t = tokens["typography"]
    light_cls, dark_cls = meta["themeClasses"]["light"], meta["themeClasses"]["dark"]
    prefix = meta["directionClassPrefix"]

    base = ["  color-scheme: light;"]
    base += direction_static(dirs[default]) + direction_colours(dirs[default], "light")
    base += data_theme(data, "light") + shadows(tokens, "light")
    base += [decl(f"data-seq-{hue}-{k}", v) for hue, ramp in data["sequential"].items() for k, v in ramp.items()]
    base += [decl(f"data-status-{k}", v) for k, v in data["status"].items() if k != "note"]
    base += [decl(f"weight-{k}", v) for k, v in t["weights"].items()]
    for step, s in t["scale"].items():
        base += [decl(f"text-{step}", s["size"]), decl(f"leading-{step}", s["line"])]
    base += [decl(f"tracking-{k}", v) for k, v in t["tracking"].items()]
    base.append(decl("measure", t["measure"]))
    base += [decl(f"space-{k}", v) for k, v in tokens["space"].items()]
    base += [decl(f"radius-{k}", v) for k, v in tokens["radius"].items()]
    base += [decl(f"dur-{k}", v) for k, v in tokens["motion"]["duration"].items()]
    base += [decl(f"ease-{k}", v) for k, v in tokens["motion"]["easing"].items()]
    base.append(decl("play-step", f"{tokens['motion']['playStepMs']}ms"))
    lay = tokens["layout"]
    for k in ("columns", "gutter", "margin"):
        base += [decl(f"grid-{k}-{bp}", v) for bp, v in lay[k].items()]
    base += [decl("max-width", lay["maxWidth"]), decl("top-bar-height", lay["topBarHeight"]),
             decl("touch-target", lay["touchTarget"])]

    dark_default = ["  color-scheme: dark;"] + direction_colours(dirs[default], "dark") + data_theme(data, "dark") + shadows(tokens, "dark")

    parts = ["/* GENERATED by scripts/build_tokens.py from tokens.json - do not edit by hand. */",
             f"/* Classes on <html>: .{light_cls} / .{dark_cls} force a theme; "
             + ", ".join(f".{prefix}{n}" for n in dirs if n != default)
             + f" switch to an alternative direction. Default direction: {default}. */", ""]
    parts += font_faces() + [""]
    parts.append(block(":root", base))
    parts.append("@media (prefers-color-scheme: dark) {\n"
                 + block(f":root:not(.{light_cls})", dark_default, "  ") + "\n}")
    parts.append(block(f":root.{dark_cls}", dark_default))
    for name, d in dirs.items():
        if name == default:
            continue
        sel = f":root.{prefix}{name}"
        parts.append(f"/* Alternative direction: {d['label']} - {d['rationale']} */")
        parts.append(block(sel, direction_static(d) + direction_colours(d, "light")))
        parts.append("@media (prefers-color-scheme: dark) {\n"
                     + block(f"{sel}:not(.{light_cls})", direction_colours(d, "dark"), "  ") + "\n}")
        parts.append(block(f"{sel}.{dark_cls}", direction_colours(d, "dark")))
    reduced = [decl(f"dur-{k}", "0ms") for k in tokens["motion"]["duration"]]
    parts.append("@media (prefers-reduced-motion: reduce) {\n" + block(":root", reduced, "  ") + "\n}")
    return "\n".join(parts) + "\n"


def main(argv):
    with open(os.path.join(ROOT, "tokens.json"), encoding="utf-8") as f:
        tokens = json.load(f)
    css = build(tokens)
    target = os.path.join(ROOT, "tokens.css")
    if "--check" in argv:
        current = open(target, encoding="utf-8").read() if os.path.exists(target) else ""
        if current != css:
            print("tokens.css is out of date: run python3 scripts/build_tokens.py")
            return 1
        print("tokens.css is up to date")
        return 0
    with open(target, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
