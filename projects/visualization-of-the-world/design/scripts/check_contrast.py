#!/usr/bin/env python3
"""Check every text, UI and data colour in tokens.json.

Usage:  python3 scripts/check_contrast.py [path/to/tokens.json] [--verbose]
Exit 0 when everything passes (accepted exceptions are listed), 1 on any failure.

Checks, for every direction x theme (light, dark):
  * text tokens on every background: >= 4.5:1 (WCAG 2.2 SC 1.4.3)
  * extra fg/bg pairs (button text on accent, badge text on tint, ...): their own minimum
  * non-text UI (control borders, focus ring, accent): >= 3:1 (SC 1.4.11)
  * categorical and place-type data colours against the chart surface: >= 3:1
    unless listed in contrast.exceptions with a reason
Data palette checks (shared by all directions, per theme):
  * categorical: adjacent pairs colour-blind separation (Machado 2009 protan/deutan,
    OKLab dE x100 >= 8; 6-8 = warning), normal-vision dE >= 15 (hard floor)
  * place type: the same, on ALL pairs (they meet in any order on maps and scatter)
  * map and diverging ramps: monotone lightness, adjacent dL >= rampMinDeltaL,
    the strong end >= 3:1 on the surface, diverging arms symmetric, neutral midpoint
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from colormath import contrast_ratio, delta_e, is_hex, oklch  # noqa: E402

THEMES = ("light", "dark")
CVD_TARGET, CVD_FLOOR, NORMAL_FLOOR = 8.0, 6.0, 15.0
LIGHTNESS_BAND = {"light": (0.43, 0.77), "dark": (0.48, 0.67)}
CHROMA_FLOOR = 0.10


class Report:
    def __init__(self):
        self.rows = []  # (status, check, detail); status in PASS / WARN / FAIL / EXCEPTION

    def add(self, status, check, detail):
        self.rows.append((status, check, detail))

    def count(self, status):
        return sum(1 for r in self.rows if r[0] == status)

    @property
    def ok(self):
        return self.count("FAIL") == 0


def ratio_row(report, check, fg, bg, minimum, exception=None):
    """exception: optional zero-argument callable returning the accepted reason (or None);
    it is only consulted when the ratio fails, so unused exceptions are detected."""
    r = contrast_ratio(fg, bg)
    detail = f"{fg} on {bg} = {r:.2f}:1 (min {minimum})"
    if r >= minimum:
        report.add("PASS", check, detail)
    elif exception and exception():
        report.add("EXCEPTION", check, f"{detail} - {exception()}")
    else:
        report.add("FAIL", check, detail)
    return r


def check_theme(report, direction, theme, tokens, rules):
    tag = f"{direction}/{theme}"
    for name in list(rules["text"]) + list(rules["textOn"]) + list(rules["ui"]) + list(rules["uiOn"]):
        if name not in tokens:
            report.add("FAIL", f"{tag} missing token", name)
    for fg in rules["text"]:
        for bg in rules["textOn"]:
            if fg in tokens and bg in tokens:
                ratio_row(report, f"{tag} text {fg} / {bg}", tokens[fg], tokens[bg], 4.5)
    for pair in rules["pairs"]:
        fg, bg = pair["fg"], pair["bg"]
        if fg not in tokens or bg not in tokens:
            report.add("FAIL", f"{tag} missing token", f"{fg} or {bg}")
            continue
        ratio_row(report, f"{tag} pair {fg} / {bg}", tokens[fg], tokens[bg], pair["min"])
    for fg in rules["ui"]:
        for bg in rules["uiOn"]:
            if fg in tokens and bg in tokens:
                ratio_row(report, f"{tag} ui {fg} / {bg}", tokens[fg], tokens[bg], 3.0)


def exception_for(exceptions, used, set_name, theme, color):
    for i, e in enumerate(exceptions):
        if e["set"] == set_name and e["theme"] == theme and e["color"].lower() == color.lower():
            used.add(i)
            return e["reason"]
    return None


def pairlist(n, all_pairs):
    if all_pairs:
        return [(i, j) for i in range(n) for j in range(i + 1, n)]
    return [(i, i + 1) for i in range(n - 1)]


def check_separation(report, label, colors, all_pairs):
    """Colour-blind and normal-vision separation. Returns (worst_cvd, worst_normal)."""
    pairs = pairlist(len(colors), all_pairs)
    kind = "all pairs" if all_pairs else "adjacent"
    worst_cvd = min(((delta_e(colors[i], colors[j], k), k, colors[i], colors[j])
                     for i, j in pairs for k in ("protan", "deutan")), default=None)
    worst_norm = min(((delta_e(colors[i], colors[j]), colors[i], colors[j]) for i, j in pairs), default=None)
    if worst_cvd:
        d, k, a, b = worst_cvd
        status = "PASS" if d >= CVD_TARGET else "WARN" if d >= CVD_FLOOR else "FAIL"
        report.add(status, f"{label} CVD {kind}", f"worst {a}/{b} dE {d:.1f} ({k}); target {CVD_TARGET}, floor {CVD_FLOOR}")
    if worst_norm:
        d, a, b = worst_norm
        report.add("PASS" if d >= NORMAL_FLOOR else "FAIL", f"{label} normal vision {kind}",
                   f"worst {a}/{b} dE {d:.1f}; floor {NORMAL_FLOOR}")
    return worst_cvd, worst_norm


def check_band(report, label, theme, colors):
    lo, hi = LIGHTNESS_BAND[theme]
    off = [c for c in colors if not lo <= oklch(c)[0] <= hi]
    grey = [c for c in colors if oklch(c)[1] < CHROMA_FLOOR]
    report.add("FAIL" if off else "PASS", f"{label} lightness band", f"outside L {lo}-{hi}: {off}" if off else f"all inside L {lo}-{hi}")
    report.add("FAIL" if grey else "PASS", f"{label} chroma floor", f"below C {CHROMA_FLOOR}: {grey}" if grey else f"all >= C {CHROMA_FLOOR}")


def check_ramp(report, label, colors, min_dl, surface, strong_end):
    """Monotone lightness with a minimum step; the strong end must reach 3:1 on the surface."""
    ls = [oklch(c)[0] for c in colors]
    diffs = [b - a for a, b in zip(ls, ls[1:])]
    monotone = all(d > 0 for d in diffs) or all(d < 0 for d in diffs)
    small = min(abs(d) for d in diffs) if diffs else 0
    report.add("PASS" if monotone else "FAIL", f"{label} monotone lightness", " -> ".join(f"{x:.2f}" for x in ls))
    report.add("PASS" if small >= min_dl else "FAIL", f"{label} step size", f"smallest dL {small:.3f} (min {min_dl})")
    ratio_row(report, f"{label} strong end on surface", colors[strong_end], surface, 3.0)


def check_diverging(report, label, colors, min_dl):
    n = len(colors)
    if n % 2 == 0 or n < 3:
        report.add("FAIL", f"{label} shape", f"needs an odd number >= 3 of colours, got {n}")
        return
    mid = n // 2
    c_mid = oklch(colors[mid])[1]
    report.add("PASS" if c_mid < 0.03 else "FAIL", f"{label} neutral midpoint", f"{colors[mid]} chroma {c_mid:.3f} (max 0.03)")
    worst = max(abs(oklch(colors[mid - k])[0] - oklch(colors[mid + k])[0]) for k in range(1, mid + 1))
    report.add("PASS" if worst <= 0.03 else "FAIL", f"{label} symmetric arms", f"largest left/right dL {worst:.3f} (max 0.03)")
    for side, arm in (("left", colors[:mid + 1][::-1]), ("right", colors[mid:])):
        ls = [oklch(c)[0] for c in arm]
        diffs = [b - a for a, b in zip(ls, ls[1:])]
        ok = (all(d > 0 for d in diffs) or all(d < 0 for d in diffs)) and min(abs(d) for d in diffs) >= min_dl
        report.add("PASS" if ok else "FAIL", f"{label} {side} arm", " -> ".join(f"{x:.2f}" for x in ls))


def run(tokens):
    report = Report()
    rules = tokens["contrast"]
    exceptions = rules.get("exceptions", [])
    used = set()
    data = tokens["data"]
    directions = tokens["directions"]

    for dname, d in directions.items():
        for theme in THEMES:
            bad = [k for k, v in d[theme].items() if not is_hex(v)]
            if bad:
                report.add("FAIL", f"{dname}/{theme} hex format", str(bad))
                continue
            check_theme(report, dname, theme, d[theme], rules)
            surface = d[theme]["chart-surface"]
            for set_name in ("categorical", "placeType"):
                for c in data[set_name][theme]:
                    ratio_row(report, f"{dname}/{theme} data {set_name}", c, surface, rules["dataMin"],
                              lambda c=c, s=set_name, t=theme: exception_for(exceptions, used, s, t, c))
            for key in ("good", "warning", "serious", "critical"):
                c = data["status"][key]
                ratio_row(report, f"{dname}/{theme} status {key}", c, surface, rules["dataMin"],
                          lambda c=c, t=theme: exception_for(exceptions, used, "status", t, c))
            # map: light = pale->dark (strong end last); dark = flipped (strong end last as well,
            # the lightest step, which must stand out from the dark surface)
            check_ramp(report, f"{dname}/{theme} map", data["map"][theme], rules["rampMinDeltaL"], surface, -1)

    for theme in THEMES:
        check_band(report, f"categorical/{theme}", theme, data["categorical"][theme])
        check_separation(report, f"categorical/{theme}", data["categorical"][theme], all_pairs=False)
        check_separation(report, f"placeType/{theme}", data["placeType"][theme], all_pairs=True)
        check_diverging(report, f"diverging/{theme}", data["diverging"][theme], rules["rampMinDeltaL"])

    for i, e in enumerate(exceptions):
        if i not in used:
            report.add("WARN", "unused exception", f"{e['set']}/{e['theme']} {e['color']} - remove it or fix the token")
    return report


def main(argv):
    verbose = "--verbose" in argv
    args = [a for a in argv if not a.startswith("--")]
    path = args[0] if args else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tokens.json")
    with open(path, encoding="utf-8") as f:
        tokens = json.load(f)
    report = run(tokens)
    for status, check, detail in report.rows:
        if verbose or status != "PASS":
            print(f"[{status}] {check}: {detail}")
    print(f"\n{len(report.rows)} checks: {report.count('PASS')} pass, {report.count('EXCEPTION')} accepted exceptions, "
          f"{report.count('WARN')} warnings, {report.count('FAIL')} failures")
    print("RESULT:", "PASS" if report.ok else "FAIL")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
