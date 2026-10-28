import csv
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_geo as b  # noqa: E402

DATA = ROOT / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class HelperTests(unittest.TestCase):
    def test_bdl_to_teryt(self):
        self.assertEqual(b.bdl_to_teryt("071412865011"), "1465011")  # Warszawa
        self.assertEqual(b.bdl_to_teryt("011212001063"), "1201063")  # Nowy Wisnicz (type 3)
        self.assertEqual(b.bdl_to_teryt("011212001000"), "1201")  # powiat bochenski
        self.assertEqual(b.bdl_to_teryt("011200000000"), "12")  # voivodeship
        self.assertEqual(b.bdl_to_teryt("010000000000"), "")  # country
        with self.assertRaises(ValueError):
            b.bdl_to_teryt("123")

    def test_norm_name(self):
        self.assertEqual(b.norm_name("Łódź"), "lodz")
        self.assertEqual(b.norm_name("Bielsko-Biała"), "bielskobiala")

    def test_city_name_and_kind(self):
        self.assertEqual(b.city_name("Pieszyce - miasto"), "Pieszyce")
        self.assertEqual(b.city_name("Bochnia"), "Bochnia")
        self.assertEqual(b.city_name("Wałbrzych od 2013"), "Wałbrzych")
        self.assertEqual(b.city_name("M.st.Warszawa od 2002"), "Warszawa")
        self.assertTrue(b.is_city_kind("1") and b.is_city_kind("4"))
        self.assertFalse(b.is_city_kind("2") or b.is_city_kind("3") or b.is_city_kind("5"))

    def test_point_in_geometry_with_hole(self):
        outer = [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
        hole = [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]
        g = {"type": "Polygon", "coordinates": [outer, hole]}
        self.assertTrue(b.point_in_geometry(g, 1, 1))
        self.assertFalse(b.point_in_geometry(g, 5, 5))
        self.assertFalse(b.point_in_geometry(g, 11, 5))

    def test_representative_point_inside_concave_shape(self):
        # "U" shape whose centroid lies in the notch
        u = [[0, 0], [9, 0], [9, 9], [6, 9], [6, 3], [3, 3], [3, 9], [0, 9], [0, 0]]
        g = {"type": "Polygon", "coordinates": [u]}
        x, y = b.representative_point(g)
        self.assertTrue(b.point_in_geometry(g, x, y))

    def test_pick_geonames_prefers_seat_then_population(self):
        c = [{"fcode": "PPL", "population": 9000}, {"fcode": "PPLA2", "population": 10},
             {"fcode": "PPLA2", "population": 50}]
        self.assertEqual(b.pick_geonames(c)["population"], 50)

    def test_explain_unmatched(self):
        out = b.explain_unmatched_bdl(["0202031", "9999991", "0216"], ["0202033"])
        self.assertEqual(out, {"type_changed_current_gmina_exists": 1,
                               "no_current_gmina_with_this_code": 1, "not_a_gmina_code": 1})


@unittest.skipUnless((DATA / "cities.geojson").exists(), "run scripts/build_geo.py first")
class BuiltDataTests(unittest.TestCase):
    def test_counts_and_codes(self):
        for name, n, pat in (("voivodeships", 16, r"\d{2}"), ("powiats", 380, r"\d{4}"),
                             ("gminas", 2479, r"\d{7}")):
            fc = load(name + ".geojson")
            self.assertEqual(len(fc["features"]), n, name)
            codes = [f["properties"]["teryt"] for f in fc["features"]]
            self.assertEqual(len(set(codes)), n, name)
            for f in fc["features"]:
                p = f["properties"]
                self.assertRegex(p["teryt"], "^" + pat + "$")
                self.assertTrue(p["name"])
                self.assertEqual(p["source_id"], "S1")

    def test_hierarchy_consistent(self):
        v = {f["properties"]["teryt"] for f in load("voivodeships.geojson")["features"]}
        p = {f["properties"]["teryt"] for f in load("powiats.geojson")["features"]}
        for f in load("powiats.geojson")["features"]:
            self.assertIn(f["properties"]["voivodeship_teryt"], v)
        for f in load("gminas.geojson")["features"]:
            self.assertIn(f["properties"]["powiat_teryt"], p)

    def test_coordinates_in_poland_wgs84(self):
        def walk(c):
            if isinstance(c[0], (int, float)):
                yield c
            else:
                for x in c:
                    yield from walk(x)
        for name in ("voivodeships", "powiats", "gminas", "cities"):
            for f in load(name + ".geojson")["features"]:
                for lon, lat in walk(f["geometry"]["coordinates"]):
                    self.assertTrue(14.0 < lon < 24.2 and 48.9 < lat < 54.9, (name, lon, lat))

    def test_topojson_matches_geojson(self):
        for name in ("voivodeships", "powiats", "gminas"):
            t = load(name + ".topojson")
            geoms = next(iter(t["objects"].values()))["geometries"]
            g = load(name + ".geojson")["features"]
            self.assertEqual(len(geoms), len(g), name)
            self.assertEqual({x["properties"]["teryt"] for x in geoms},
                             {f["properties"]["teryt"] for f in g})
            self.assertIn("transform", t)

    def test_cities(self):
        fc = load("cities.geojson")["features"]
        teryts = [f["properties"]["teryt"] for f in fc]
        self.assertEqual(len(teryts), len(set(teryts)))
        for f in fc:
            p = f["properties"]
            self.assertRegex(p["teryt"], r"^\d{7}$")
            self.assertIn(p["gmina_type"], (1, 4))
            self.assertEqual(p["big_city"], p["population"] >= 100000)
            self.assertEqual(p["population_year"], 2025)
            self.assertEqual(p["source_id"], "S3")

    def test_big_cities_match_demography_series(self):
        ref = {r["unit_id"]: int(r["population_latest_year"]) for r in csv.DictReader(
            open(DATA / "reference" / "big_city_list_demography_2025.csv", encoding="utf-8"))}
        got = {f["properties"]["bdl_unit_id"]: f["properties"]["population"]
               for f in load("cities.geojson")["features"] if f["properties"]["big_city"]}
        self.assertEqual(got, ref)

    def test_join_report_full_coverage_of_geometry(self):
        rep = load("bdl_join_report.json")
        for k in ("voivodeships", "powiats", "gminas"):
            self.assertEqual(rep[k]["percent_geometry_found_in_bdl"], 100.0, k)

    def test_file_sizes_phone_friendly(self):
        for name, limit in (("voivodeships.topojson", 100_000), ("powiats.topojson", 400_000),
                            ("gminas.topojson", 1_200_000), ("cities.geojson", 500_000)):
            self.assertLess((DATA / name).stat().st_size, limit, name)


if __name__ == "__main__":
    unittest.main()
