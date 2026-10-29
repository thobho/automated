"""Tests for the design-system scripts. Run: python3 -m unittest discover -s tests (from design/)."""
import copy
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(DESIGN, "scripts"))

import build_tokens  # noqa: E402
import check_contrast  # noqa: E402
from colormath import contrast_ratio, delta_e, hex_to_srgb, oklch, relative_luminance  # noqa: E402


def load_tokens():
    with open(os.path.join(DESIGN, "tokens.json"), encoding="utf-8") as f:
        return json.load(f)


class ColourMath(unittest.TestCase):
    def test_contrast_extremes(self):
        self.assertAlmostEqual(contrast_ratio("#000000", "#ffffff"), 21.0, places=6)
        self.assertAlmostEqual(contrast_ratio("#777777", "#777777"), 1.0, places=6)

    def test_contrast_symmetric(self):
        self.assertAlmostEqual(contrast_ratio("#0a6c74", "#ffffff"), contrast_ratio("#ffffff", "#0a6c74"))

    def test_known_wcag_value(self):
        # #767676 on white is the well-known 4.54:1 grey
        self.assertAlmostEqual(contrast_ratio("#767676", "#ffffff"), 4.54, places=2)

    def test_luminance_range(self):
        self.assertEqual(relative_luminance("#000000"), 0)
        self.assertAlmostEqual(relative_luminance("#ffffff"), 1.0)

    def test_bad_hex_rejected(self):
        for bad in ("fff", "#fff", "#gggggg", "", None, "#12345"):
            with self.assertRaises(ValueError):
                hex_to_srgb(bad)

    def test_oklch_white_and_grey(self):
        L, C, _ = oklch("#ffffff")
        self.assertAlmostEqual(L, 1.0, places=3)
        self.assertLess(C, 0.001)
        self.assertLess(oklch("#808080")[1], 0.001)

    def test_delta_e_matches_dataviz_validator(self):
        # Values reported by the dataviz skill's validate_palette.js for the reference palette
        self.assertAlmostEqual(delta_e("#eda100", "#1baf7a", "protan"), 9.1, delta=0.05)
        self.assertAlmostEqual(delta_e("#e87ba4", "#eda100"), 19.6, delta=0.05)

    def test_red_green_collapse_for_protan(self):
        # green vs orange is obvious to normal vision but collapses for protanopes
        self.assertGreater(delta_e("#008300", "#eb6834"), 20)
        self.assertLess(delta_e("#008300", "#eb6834", "protan"), 6)


class ContrastChecks(unittest.TestCase):
    def test_committed_tokens_pass(self):
        report = check_contrast.run(load_tokens())
        fails = [r for r in report.rows if r[0] == "FAIL"]
        self.assertEqual(fails, [])
        self.assertEqual(report.count("WARN"), 0, [r for r in report.rows if r[0] == "WARN"])

    def test_low_contrast_text_fails(self):
        tokens = load_tokens()
        tokens["directions"]["baltyk"]["light"]["text-muted"] = "#b4bfc7"
        report = check_contrast.run(tokens)
        self.assertFalse(report.ok)
        self.assertTrue(any("text-muted" in r[1] and r[0] == "FAIL" for r in report.rows))

    def test_exception_turns_fail_into_accepted(self):
        tokens = load_tokens()
        rows = [r for r in check_contrast.run(tokens).rows if r[0] == "EXCEPTION"]
        self.assertTrue(rows)
        tokens["contrast"]["exceptions"] = []
        self.assertFalse(check_contrast.run(tokens).ok)

    def test_unused_exception_is_warned(self):
        tokens = load_tokens()
        tokens["contrast"]["exceptions"].append({"set": "categorical", "theme": "dark", "color": "#3987e5", "reason": "x"})
        report = check_contrast.run(tokens)
        self.assertTrue(any(r[0] == "WARN" and r[1] == "unused exception" for r in report.rows))

    def test_cvd_collapse_in_place_type_fails(self):
        tokens = load_tokens()
        tokens["data"]["placeType"]["light"] = ["#2a78d6", "#eb6834", "#008300"]
        report = check_contrast.run(tokens)
        self.assertTrue(any(r[0] == "FAIL" and r[1].startswith("placeType/light CVD") for r in report.rows))

    def test_rainbow_midpoint_fails_diverging(self):
        tokens = load_tokens()
        tokens["data"]["diverging"]["light"][3] = "#eda100"
        report = check_contrast.run(tokens)
        self.assertTrue(any(r[0] == "FAIL" and "neutral midpoint" in r[1] for r in report.rows))

    def test_non_monotone_map_fails(self):
        tokens = load_tokens()
        m = tokens["data"]["map"]["light"]
        m[2], m[3] = m[3], m[2]
        report = check_contrast.run(tokens)
        self.assertTrue(any(r[0] == "FAIL" and "map monotone" in r[1] for r in report.rows))

    def test_missing_token_fails(self):
        tokens = load_tokens()
        del tokens["directions"]["noc"]["dark"]["focus-ring"]
        self.assertFalse(check_contrast.run(tokens).ok)

    def test_main_exit_codes(self):
        self.assertEqual(check_contrast.main([os.path.join(DESIGN, "tokens.json")]), 0)


class TokenStructure(unittest.TestCase):
    def setUp(self):
        self.tokens = load_tokens()

    def test_every_direction_has_same_token_names(self):
        dirs = self.tokens["directions"]
        names = set(dirs["baltyk"]["light"])
        for name, d in dirs.items():
            for theme in ("light", "dark"):
                self.assertEqual(set(d[theme]), names, f"{name}/{theme}")

    def test_exactly_one_chosen_direction(self):
        chosen = [n for n, d in self.tokens["directions"].items() if d["chosen"]]
        self.assertEqual(chosen, [self.tokens["meta"]["defaultDirection"]])

    def test_categorical_has_eight(self):
        for theme in ("light", "dark"):
            self.assertGreaterEqual(len(self.tokens["data"]["categorical"][theme]), 8)

    def test_place_type_is_first_three_categorical(self):
        d = self.tokens["data"]
        for theme in ("light", "dark"):
            self.assertEqual(d["placeType"][theme], d["categorical"][theme][:3])

    def test_no_cream_page_background(self):
        # The brief bans cream / warm off-white pages: a light page must be pure white or visibly cool.
        for name, d in self.tokens["directions"].items():
            r, g, b = hex_to_srgb(d["light"]["bg-page"])
            self.assertTrue((r, g, b) == (1, 1, 1) or b > r, f"{name} page {d['light']['bg-page']} looks warm")


class GeneratedCss(unittest.TestCase):
    def test_tokens_css_in_sync(self):
        css = build_tokens.build(load_tokens())
        with open(os.path.join(DESIGN, "tokens.css"), encoding="utf-8") as f:
            self.assertEqual(f.read(), css, "run python3 scripts/build_tokens.py")

    def test_font_files_exist_and_no_remote_urls(self):
        css = build_tokens.build(load_tokens())
        urls = re.findall(r'url\("([^"]+)"\)', css)
        self.assertTrue(urls)
        for u in urls:
            self.assertFalse(u.startswith(("http:", "https:", "//")), u)
            self.assertTrue(os.path.exists(os.path.join(DESIGN, u)), u)

    def test_each_alternative_direction_has_light_and_dark_blocks(self):
        css = build_tokens.build(load_tokens())
        for name in ("beton", "noc"):
            self.assertIn(f":root.dir-{name} {{", css)
            self.assertIn(f":root.dir-{name}.theme-dark {{", css)
            self.assertIn(f":root.dir-{name}:not(.theme-light) {{", css)

    def test_reduced_motion_zeroes_durations(self):
        css = build_tokens.build(load_tokens())
        block = css.split("@media (prefers-reduced-motion: reduce)")[1]
        for k in load_tokens()["motion"]["duration"]:
            self.assertIn(f"--dur-{k}: 0ms;", block)

    def test_check_mode_detects_drift(self):
        path = os.path.join(DESIGN, "tokens.css")
        original = open(path, encoding="utf-8").read()
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write("/* drift */\n")
            self.assertEqual(build_tokens.main(["--check"]), 1)
        finally:
            with open(path, "w", encoding="utf-8") as f:
                f.write(original)
        self.assertEqual(build_tokens.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
