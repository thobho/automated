import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import eurostat  # noqa: E402
import process_structure as ps  # noqa: E402


class Geometry(unittest.TestCase):
    def test_haversine_warsaw_krakow(self):
        d = ps.haversine_km(21.0122, 52.2297, 19.9450, 50.0647)
        self.assertAlmostEqual(d, 252, delta=3)

    def test_polygon_centroid_square(self):
        sq = {"type": "Polygon", "coordinates": [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]]}
        self.assertEqual(ps.geometry_centroid(sq), (1.0, 1.0))

    def test_multipolygon_weighted_by_area(self):
        big = [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]]       # area 4, centre (1, 1)
        small = [[[10, 0], [11, 0], [11, 1], [10, 1], [10, 0]]]  # area 1, centre (10.5, 0.5)
        x, y = ps.geometry_centroid({"type": "MultiPolygon", "coordinates": [big, small]})
        self.assertAlmostEqual(x, (4 * 1 + 1 * 10.5) / 5)
        self.assertAlmostEqual(y, (4 * 1 + 1 * 0.5) / 5)


class Codes(unittest.TestCase):
    def test_unit_teryt(self):
        self.assertEqual(ps.unit_teryt("030210101011"), "0201011")   # Boleslawiec
        self.assertEqual(ps.unit_teryt("071412865011"), "1465011")   # Warszawa
        self.assertEqual(ps.unit_teryt("030210365011"), "0265011")   # Walbrzych

    def test_pct_change(self):
        self.assertEqual(ps.pct_change(100, 150), 50.0)
        self.assertIsNone(ps.pct_change(None, 5))
        self.assertIsNone(ps.pct_change(0, 5))


def unit(vol, gm, typ):  # fake 12-char id whose tail gives TERYT vol+gm+typ
    return f"03{vol}10{gm}{typ}"[:12].ljust(12, "0")


class Belt(unittest.TestCase):
    def setUp(self):
        # one gmina changed type 2 -> 3 between 2000 and 2025 (same territory): series must be merged
        self.rural = "030210101012"
        self.urbrur = "030210101013"
        self.far = "030210909012"
        self.city = "030210564011"
        self.pop = {
            self.rural: ("G", {2000: 1000, 2025: None}),
            self.urbrur: ("G", {2000: None, 2025: 1500}),
            self.far: ("Far", {2000: 500, 2025: 400}),
            self.city: ("City", {2000: 100000, 2025: 120000}),
            "030210101014": ("G - urban area", {2025: 800}),  # town part, must be ignored by whole_gminas
        }

    def test_whole_gminas_merges_type_change(self):
        w = ps.whole_gminas(self.pop)
        self.assertEqual(w["020101"]["vals"], {2000: 1000, 2025: 1500})
        self.assertEqual(w["020101"]["uid"], self.urbrur)

    def test_select_belt_radius_and_exclusion(self):
        w = ps.whole_gminas(self.pop)
        cent = {"020101": (17.1, 51.1), "020901": (20.0, 52.0), "020564": (17.0, 51.1)}
        got = ps.select_belt(w, {"020564"}, {self.city: (17.0, 51.1)}, cent, radius=25)
        self.assertEqual([g[0] for g in got], ["020101"])  # far one outside, city itself excluded
        self.assertLess(got[0][2], 10)

    def test_belt_rows_growth_and_missing(self):
        big = [(self.city, "City", 120000)]
        pts = {self.city: (17.0, 51.1)}
        cent = {"020101": (17.1, 51.1), "020901": (17.1, 51.2)}
        pop = dict(self.pop)
        pop["030210909012"] = ("Far", {2000: None, 2025: 400})
        rows = ps.belt_rows(pop, big, pts, cent, n_cores=1)
        by = {r["gmina"]: r for r in rows}
        self.assertEqual(by["G"]["change_2000_2025_pct"], "50.00")
        self.assertEqual(by["G"]["rank_growth_2000_2025"], 1)
        self.assertEqual(by["Far"]["change_2000_2025_pct"], "")      # missing, not invented
        self.assertIn("missing", by["Far"]["note"])
        self.assertEqual(by["Far"]["rank_growth_2000_2025"], "")


class Merge(unittest.TestCase):
    def test_merge_and_drop_warsaw_districts(self):
        raw = {
            "071412831001": ("Capital city Warszawa to 2001", {2000: 10, 2001: 11}),
            "071412865011": ("Capital city Warszawa", {2002: 12}),
            "071412831011": ("Warszawa - Mokotow to 2001", {2000: 3}),
        }
        out = ps.merged_series(raw)
        self.assertEqual(list(out), ["071412865011"])
        self.assertEqual(out["071412865011"][1], {2000: 10, 2001: 11, 2002: 12})


class Classes(unittest.TestCase):
    def test_class_assignment_and_sums_with_parts(self):
        big = {"b1"}
        self.assertEqual(ps.gmina_class("b1", big), "big_cities")
        self.assertEqual(ps.gmina_class("x1", big), "small_cities")
        self.assertEqual(ps.gmina_class("x4", big), "small_cities")
        self.assertEqual(ps.gmina_class("x5", big), "villages")
        self.assertEqual(ps.gmina_class("x2", big), "villages")
        data = {"b1": ("B", {2020: 10}), "t1": ("T", {2020: 5}), "m3": ("M", {2020: 7}),
                "m4": ("M town", {2020: 4}), "m5": ("M rural", {2020: 3}), "v2": ("V", {2020: 2})}
        sums, _ = ps.class_sums(data, big, [2020], use_parts=True)
        self.assertEqual(dict(sums["big_cities"]), {2020: 10})
        self.assertEqual(dict(sums["small_cities"]), {2020: 9})   # T + town part
        self.assertEqual(dict(sums["villages"]), {2020: 5})       # V + rural part
        self.assertNotIn("urban_rural_gminas_whole", sums)        # whole type-3 unit skipped to avoid double count
        total = sum(sum(v.values()) for v in sums.values())
        self.assertEqual(total, 24)                               # = 10+5+7+2, nothing lost or doubled


class SmallTowns(unittest.TestCase):
    def test_ranking_and_exclusions(self):
        big = [("b1", "B", 200000)]
        pop = {
            "b1": ("B", {2000: 1, 2025: 200000}),
            "a1": ("A", {2000: 10000, 2025: 7000}),                 # -30%
            "c1": ("C", {2000: 10000, 2025: 11000}),                # +10%
            "d4": ("D - urban area", {2000: 3000, 2025: 2500}),     # -16.7%
            "e1": ("E", {2025: 4000}),                              # no 2000 value
            "f1": ("F", {2000: 500, 2025: 100}),                    # below min size, not ranked
            "g1": ("G", {2000: 150000, 2025: 100500}),              # >= 100k in 2025 -> not small
            "h2": ("H", {2000: 9, 2025: 8}),                        # rural, ignored
        }
        rows = ps.small_town_rows(pop, big)
        ranked = [(r["town"], r["rank_loss_pct"]) for r in rows if r["rank_loss_pct"] != ""]
        self.assertEqual(ranked, [("A", 1), ("D", 2), ("C", 3)])
        names = {r["town"] for r in rows}
        self.assertEqual(names, {"A", "C", "D", "E", "F"})
        e = [r for r in rows if r["town"] == "E"][0]
        self.assertEqual(e["pop_2000"], "")
        self.assertIn("no 2000 value", e["note"])


class Pyramid(unittest.TestCase):
    def test_pyramid_sex_labels_and_order(self):
        bdl = {1: {"subject": "P2137", "n1": "5-9", "n2": "males", "n3": "", "vals": {2000: 5}},
               2: {"subject": "P2137", "n1": "5-9", "n2": "females", "n3": "", "vals": {2000: 4}},
               3: {"subject": "P2137", "n1": "0-4", "n2": "males", "n3": "", "vals": {2000: 6}},
               4: {"subject": "P2137", "n1": "total", "n2": "total", "n3": "", "vals": {2000: 15}},
               5: {"subject": "P2137", "n1": "70 and more", "n2": "males", "n3": "", "vals": {2000: 2}}}
        rows = ps.build_pyramid(bdl)
        self.assertEqual([(r["age_group"], r["sex"]) for r in rows],
                         [("0-4", "male"), ("5-9", "female"), ("5-9", "male"), ("70+", "male")])


class EurostatDecode(unittest.TestCase):
    def test_observations_decodes_multi_dim_index(self):
        d = {"id": ["indic", "time"], "size": [2, 3],
             "dimension": {"indic": {"category": {"index": {"A": 0, "B": 1}}},
                           "time": {"category": {"index": {"2000": 0, "2001": 1, "2002": 2}}}},
             "value": {"0": 1.0, "4": 9.5}, "status": {"4": "p"}}
        got = list(eurostat.observations(d))
        self.assertEqual(got[0], ({"indic": "A", "time": "2000"}, 1.0, ""))
        self.assertEqual(got[1], ({"indic": "B", "time": "2001"}, 9.5, "p"))


class Households(unittest.TestCase):
    def test_census_average_derived_for_2002(self):
        def v(sub, val, year):
            return {"subject": sub, "n1": "", "n2": "", "n3": "", "vals": {year: val}}
        bdl = {9199: v("P2115", 100, 2002)}
        for h, p, hv, pv in [(194837, 194838, 40, 40), (194835, 194836, 30, 60), (194833, 194834, 20, 60),
                             (194831, 194832, 5, 20), (194829, 194830, 5, 30)]:
            bdl[h], bdl[p] = v("P2871", hv, 2002), v("P2871", pv, 2002)
        for k, val in {450473: 200, 450478: 560, 450479: 2.8, 450472: 1, 450474: 1, 450475: 1, 450476: 1, 450477: 1}.items():
            bdl[k] = v("P3420", val, 2011)
        for k, val in {1652549: 300, 1652555: 900, 1652556: 3.0, 1652550: 1, 1652551: 1, 1652552: 1, 1652553: 1, 1652554: 1}.items():
            bdl[k] = v("P4287", val, 2021)
        eu = {"persons_per_private_household_eu_lfs": {"2006": (2.9, "")}}
        rows = ps.households_rows(bdl, eu, {"villages": (10, 29)})
        r02 = [r for r in rows if r["year"] == 2002][0]
        self.assertEqual(r02["avg_persons_per_household"], 2.1)  # 210 / 100
        self.assertEqual(r02["value_type"], "households reported; population and average derived")
        self.assertEqual([r["source_id"] for r in rows], ["S16", "S17", "S18", "S18", "S24"])
        self.assertEqual([r for r in rows if r["area"] == "villages"][0]["avg_persons_per_household"], 2.9)


if __name__ == "__main__":
    unittest.main()
