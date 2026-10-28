import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import process_population as pp  # noqa: E402


class Build(unittest.TestCase):
    def setUp(self):
        self.nat = {}
        for y, (t, u, r) in {2000: (100, 60, 40), 2001: (100, 62, 38)}.items():
            self.nat[(y, "total")], self.nat[(y, "urban")], self.nat[(y, "rural")] = t, u, r
        self.names = {"a": "A", "b": "B", "c": "C"}
        # B is below threshold in the latest year, so it is not a big city; C reaches the threshold only later.
        self.vals = {"a": {2000: 30, 2001: 31}, "b": {2000: 12, 2001: 9}, "c": {2000: 8, 2001: 10}}

    def test_classes_sum_to_total_and_fixed_list(self):
        rows, urb, big = pp.build(self.nat, self.names, self.vals, [2000, 2001], threshold=10)
        self.assertEqual(sorted(big), ["a", "c"])
        for y in (2000, 2001):
            r = [x for x in rows if x["year"] == y]
            self.assertEqual(sum(x["population"] for x in r), self.nat[(y, "total")])
        self.assertEqual({x["class"]: x["population"] for x in rows if x["year"] == 2000},
                         {"big_cities": 38, "small_cities": 22, "villages": 40})

    def test_in_year_count_differs_from_fixed_list(self):
        _, urb, _ = pp.build(self.nat, self.names, self.vals, [2000, 2001], threshold=10)
        self.assertEqual([u["big_cities_ge100k_in_year_count"] for u in urb], [2, 2])  # 2000: a,b ; 2001: a,c
        self.assertEqual(urb[0]["urbanization_rate_pct"], "60.00")

    def test_missing_big_city_value_raises(self):
        del self.vals["a"][2000]
        with self.assertRaises(ValueError):
            pp.build(self.nat, self.names, self.vals, [2000, 2001], threshold=10)


class RealData(unittest.TestCase):
    """Checks on the committed raw + processed data."""

    def test_national_parts_add_up(self):
        nat = pp.read_national()
        years = sorted({y for y, _ in nat})
        self.assertEqual((years[0], years[-1] >= 2024), (2000, True))
        for y in years:
            self.assertEqual(nat[(y, "urban")] + nat[(y, "rural")], nat[(y, "total")])

    def test_gmina_sum_matches_national_total(self):
        import csv
        nat = pp.read_national()
        with open(ROOT / "data" / "raw" / "bdl_gmina_sums.csv", newline="") as f:
            for r in csv.DictReader(f):
                self.assertEqual(int(r["sum_gminas_types_1_2_3"]), nat[(int(r["year"]), "total")])

    def test_processed_matches_national(self):
        import csv
        nat = pp.read_national()
        by_year = {}
        with open(ROOT / "data" / "processed" / "population_by_class.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                by_year.setdefault(int(r["year"]), []).append(r)
        for y, rows in by_year.items():
            self.assertEqual(len(rows), 3)
            self.assertEqual(sum(int(r["population"]) for r in rows), nat[(y, "total")])
            self.assertAlmostEqual(sum(float(r["share_of_total_pct"]) for r in rows), 100, delta=0.02)
            self.assertTrue(all(r["source_id"] for r in rows))


if __name__ == "__main__":
    unittest.main()
