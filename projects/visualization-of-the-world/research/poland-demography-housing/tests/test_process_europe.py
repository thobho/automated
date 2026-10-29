import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import eurostat  # noqa: E402
import fetch_eurostat_europe as fe  # noqa: E402
import process_europe as pe  # noqa: E402


def raw(series, geo, period, value, dataset="x", flag=""):
    return {"dataset": dataset, "series": series, "geo": geo, "period": str(period), "value": str(value),
            "eurostat_flag": flag, "dataset_updated": "2026-01-01"}


class Helpers(unittest.TestCase):
    def test_fmt(self):
        self.assertEqual(pe.fmt(12.50), "12.5")
        self.assertEqual(pe.fmt(3.0), "3")
        self.assertEqual(pe.fmt(None), "")
        self.assertEqual(pe.fmt(-0.001, 2), "0")

    def test_rank_desc(self):
        vals = {"PL": 2.0, "CZ": 3.0, "SK": 1.0, "HU": None}
        self.assertEqual(pe.rank_desc(vals, "PL"), 2)
        self.assertEqual(pe.rank_desc(vals, "CZ"), 1)
        self.assertIsNone(pe.rank_desc(vals, "HU"))
        self.assertEqual(pe.rank_desc({"PL": 5, "CZ": 5}, "PL"), 1)


class Annual(unittest.TestCase):
    def test_population_index_and_flags(self):
        rows = pe.build_annual([
            raw("population_1_jan", "PL", 2000, 200, "demo_gind", "b"),
            raw("population_1_jan", "PL", 2001, 190, "demo_gind"),
            raw("life_expectancy_at_birth:F", "PL", 2000, 78.0, "demo_mlexpec"),
            raw("unknown_series", "PL", 2000, 1)])
        idx = [r for r in rows if r["indicator"] == "population_index_2000_eq_100"]
        self.assertEqual([r["value"] for r in idx], ["100", "95"])
        self.assertTrue(all(r["value_type"] == "derived" and r["formula"] for r in idx))
        rep = [r for r in rows if r["indicator"] == "population_1_jan" and r["year"] == "2000"][0]
        self.assertEqual((rep["eurostat_flag"], rep["source_id"], rep["dataset_code"]), ("b", "S29", "demo_gind"))
        le = [r for r in rows if r["indicator"] == "life_expectancy_at_birth"][0]
        self.assertEqual((le["sex"], le["source_id"]), ("women", "S32"))
        self.assertEqual(len(rows), 5)  # 3 reported + 2 derived index rows; unknown series dropped

    def test_empty_values_not_filled(self):
        rows = pe.build_annual([raw("total_fertility_rate", "PL", 2000, "", "demo_find")])
        self.assertEqual(rows, [])


class Degurba(unittest.TestCase):
    def test_census_shares_derived(self):
        data = [raw(f"census_2021_population_by_degurba:{c}", "PL", 2021, v, "cens_21urb01")
                for c, v in (("TOTAL", 100), ("DEG1", 30), ("DEG2", 30), ("DEG3", 40))]
        rows = pe.build_degurba(data)
        shares = {r["degurba_class"]: r["value"] for r in rows if r["measure"] == "census_2021_share_of_population"}
        self.assertEqual(shares, {"cities": "30", "towns_and_suburbs": "30", "rural_areas": "40"})
        self.assertTrue(all(r["source_id"] == "S35" for r in rows))

    def test_no_share_when_class_missing(self):
        data = [raw(f"population_15plus_by_degurba_thousand:{c}", "PL", 2006, v, "lfsa_pgauws")
                for c, v in (("TOTAL", 100), ("DEG1", 30), ("DEG3", 40))]
        rows = pe.build_degurba(data)
        self.assertEqual([r for r in rows if r["measure"].startswith("share")], [])

    def test_ilc_total_row_dropped(self):
        data = [raw("share_of_population_by_degurba_pct:TOTAL", "PL", 2010, 100, "ilc_lvho01"),
                raw("share_of_population_by_degurba_pct:DEG1", "PL", 2010, 40, "ilc_lvho01")]
        rows = pe.build_degurba(data)
        self.assertEqual([r["degurba_class"] for r in rows], ["cities"])


class Summary(unittest.TestCase):
    def test_change_and_rank(self):
        annual = []
        for geo, a, b in (("PL", 10, 20), ("CZ", 10, 30), ("SK", 10, 15), ("HU", 1, 1), ("DE", 1, 1), ("RO", 1, 1),
                          ("LT", 1, 1), ("EU27_2020", 5, 6)):
            for y, v in ((2000, a), (2025, b)):
                annual.append({"geo": geo, "year": str(y), "indicator": "median_age_1_jan", "sex": "total",
                               "value": str(v), "unit": "years", "value_type": "reported",
                               "dataset_code": "demo_pjanind", "source_id": "S31"})
        out = {r["geo"]: r for r in pe.build_summary(annual)}
        self.assertEqual(out["PL"]["change_abs"], "10")
        self.assertEqual(out["PL"]["change_pct"], "100")
        self.assertEqual(out["PL"]["poland_rank_latest_of_7"], 2)
        self.assertEqual(out["CZ"]["poland_rank_latest_of_7"], "")

    def test_no_rank_for_counts_or_mixed_latest_years(self):
        annual = [{"geo": g, "year": y, "indicator": "natural_change", "sex": "total", "value": v, "unit": "persons",
                   "value_type": "reported", "dataset_code": "demo_gind", "source_id": "S29"}
                  for g, y, v in (("PL", "2000", "1"), ("PL", "2025", "2"), ("CZ", "2000", "1"), ("CZ", "2025", "3"))]
        self.assertEqual(pe.build_summary(annual)[0]["poland_rank_latest_of_7"], "")


class Fetch(unittest.TestCase):
    def test_request_urls_use_expected_codes(self):
        url = eurostat.url_for("demo_find", fe.GEO + fe.indic("TOTFERRT") + fe.SINCE)
        self.assertIn("geo=PL", url)
        self.assertIn("geo=EU27_2020", url)
        self.assertIn("indic_de=TOTFERRT", url)
        self.assertEqual(len(fe.GEOS), 8)

    def test_every_series_has_a_mapping(self):
        for _, s, _, dim in fe.REQUESTS:
            if dim is None:
                self.assertIn(s, pe.ANNUAL)


class CommittedData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = ROOT / "data" / "processed"
        cls.annual = list(csv.DictReader(open(d / "europe_annual.csv", encoding="utf-8")))
        cls.degurba = list(csv.DictReader(open(d / "europe_degurba.csv", encoding="utf-8")))
        cls.summary = list(csv.DictReader(open(d / "europe_summary.csv", encoding="utf-8")))

    def test_dataset_code_and_source_everywhere(self):
        for rows in (self.annual, self.degurba, self.summary):
            for r in rows:
                self.assertTrue(r["dataset_code"] and r["source_id"], r)

    def test_all_eight_geos_present(self):
        self.assertEqual({r["geo"] for r in self.annual}, set(pe.COUNTRIES) | {"EU27_2020"})

    def test_degurba_census_shares_sum_to_100(self):
        by = {}
        for r in self.degurba:
            if r["measure"] == "census_2021_share_of_population":
                by.setdefault(r["geo"], 0)
                by[r["geo"]] += float(r["value"])
        self.assertEqual(len(by), 8)
        for g, s in by.items():
            self.assertAlmostEqual(s, 100, delta=0.02, msg=g)

    def test_degurba_survey_shares_sum_to_100(self):
        by = {}
        for r in self.degurba:
            if r["measure"] == "share_of_population_all_ages":
                by[(r["geo"], r["year"])] = by.get((r["geo"], r["year"]), 0) + float(r["value"])
        for k, s in by.items():
            self.assertAlmostEqual(s, 100, delta=0.31, msg=k)

    def test_poland_anchor_values(self):
        def get(ind, year, sex="total"):
            return [float(r["value"]) for r in self.annual
                    if r["geo"] == "PL" and r["indicator"] == ind and r["year"] == str(year) and r["sex"] == sex][0]
        self.assertEqual(get("median_age_1_jan", 2025), 43.4)   # same as Eurostat figure already used in task 02
        self.assertEqual(get("total_fertility_rate", 2000), 1.37)
        self.assertEqual(get("population_index_2000_eq_100", 2000), 100)


if __name__ == "__main__":
    unittest.main()
