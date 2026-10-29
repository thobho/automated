import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import fetch_bdl_gminas as fg  # noqa: E402
import fetch_bdl_housing as fh  # noqa: E402
import process_housing as ph  # noqa: E402


def cs_fixture():
    """Tiny class sums for 2010: total 100/60/40, single-family 20/30/30, multi-family 70/20/5, individual 25/40/35, own use 20/35/30."""
    data = {
        ph.V_TOTAL: (100, 60, 40), ph.V_SF: (20, 30, 30), ph.V_MF: (70, 20, 5),
        ph.V_INDIV: (25, 40, 35), ph.V_OWNUSE: (20, 35, 30),
    }
    cs = {}
    for vid, vals in data.items():
        cs[vid] = {(c, 2010): (v, 3) for c, v in zip(ph.CLASSES, vals)}
    return cs


POP = {(c, 2010): p for c, p in zip(ph.CLASSES, (1000, 2000, 4000))}


class Completions(unittest.TestCase):
    def setUp(self):
        self.rows = ph.completions_rows(cs_fixture(), POP)

    def get(self, cls, typ):
        return next(r for r in self.rows if r["class"] == cls and r["type"] == typ)

    def test_direct_split_adds_up(self):
        for cls in ph.CLASSES:
            parts = sum(self.get(cls, t)["dwellings"] for t in ("house", "flat", "other"))
            self.assertEqual(parts, self.get(cls, "total")["dwellings"])
        self.assertEqual(self.get("big_cities", "other")["dwellings"], 10)

    def test_proxy_is_complement(self):
        for cls in ph.CLASSES:
            for a, b in (("house_proxy_individual", "flat_proxy_non_individual"),
                         ("house_proxy_own_use", "flat_proxy_not_own_use")):
                self.assertEqual(self.get(cls, a)["dwellings"] + self.get(cls, b)["dwellings"],
                                 self.get(cls, "total")["dwellings"])
                self.assertEqual(self.get(cls, a)["basis"], "proxy")

    def test_rates_and_sources(self):
        r = self.get("villages", "house")
        self.assertEqual(r["per_1000_residents"], "7.50")
        self.assertEqual(r["share_of_total_pct"], "75.00")
        self.assertTrue(all(row["source_id"] for row in self.rows))

    def test_missing_years_are_skipped_not_filled(self):
        cs = cs_fixture()
        del cs[ph.V_SF]
        rows = ph.completions_rows(cs, POP)
        self.assertFalse([r for r in rows if r["type"] in ("house", "flat", "other")])
        self.assertTrue([r for r in rows if r["type"] == "total"])


class Others(unittest.TestCase):
    def test_avg_area(self):
        cs = {ph.V_SF_AREA: {("villages", 2010): (3000, 2)}, ph.V_SF: {("villages", 2010): (30, 2)}}
        r = ph.avg_area_rows(cs)
        self.assertEqual(r[0]["avg_m2_per_dwelling"], "100.00")

    def test_permits_other_is_residual(self):
        cs = {ph.V_PERMIT_TOTAL: {("big_cities", 2012): (100, 1)}, ph.V_PERMIT_SF: {("big_cities", 2012): (10, 1)},
              ph.V_PERMIT_2: {("big_cities", 2012): (5, 1)}, ph.V_PERMIT_3: {("big_cities", 2012): (70, 1)}}
        rows = {r["type"]: r["dwellings"] for r in ph.permits_rows(cs, {})}
        self.assertEqual(rows, {"total": 100, "house": 10, "flat": 75, "other": 15})

    def test_permits_national_rows_for_years_without_class_data(self):
        nat = {ph.V_PERMIT_TOTAL: {2010: 100}, ph.V_PERMIT_SF: {2010: 30}, ph.V_PERMIT_2: {2010: 10}, ph.V_PERMIT_3: {2010: 50}}
        rows = {r["type"]: r["dwellings"] for r in ph.permits_rows({}, {}, nat) if r["class"] == "poland"}
        self.assertEqual(rows, {"total": 100, "house": 30, "flat": 60, "other": 10})

    def test_starts_split_and_table_switch(self):
        nat = {217340: {2017: 1000}, 567218: {2017: 999, 2018: 800}}
        big = {217340: {2017: 300}, 567218: {2018: 250}}
        rows = {(r["year"], r["area"]): r["dwellings"] for r in ph.starts_rows(nat, big) if r["type"] == "total"}
        self.assertEqual(rows[(2017, "big_cities")], 300)
        self.assertEqual(rows[(2017, "rest_of_poland")], 700)   # 2017 uses P2956, not P3747
        self.assertEqual(rows[(2018, "poland")], 800)

    def test_crosscheck_difference(self):
        cs = cs_fixture()
        nat = {ph.V_TOTAL: {2010: 200}}
        r = ph.crosscheck_rows(cs, nat)
        self.assertEqual(r[0]["difference"], 0)

    def test_read_national_drops_placeholder_zero(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "n.csv"
            with open(p, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["subject_id", "variable_id", "n1", "n2", "n3", "n4", "unit", "year", "value", "attr_id"])
                w.writerow(["P3824", 748604, "private", "dwellings", "", "", "-", 2000, 0, 4])
                w.writerow(["P3824", 748604, "private", "dwellings", "", "", "-", 2005, 58685, 1])
            vals, _ = ph.read_national(p)
        self.assertEqual(vals[748604], {2005: 58685})

    def test_gmina_loader_attr_set_matches(self):
        self.assertEqual(ph.NO_VALUE_ATTRS, fg.NO_VALUE_ATTRS)

    def test_powiat_id_of_city(self):
        self.assertEqual(fh.powiat_id("011212161011"), "011212161000")

    def test_class_sum_rows_use_parts_and_control_total(self):
        series = {"011212001011": ("Town", {2010: 10}),          # urban gmina -> small_cities
                  "011212002013": ("UrbRur", {2010: 7}),         # whole urban-rural gmina, control only
                  "011212002014": ("UrbRur urban part", {2010: 4}),
                  "011212002015": ("UrbRur rural part", {2010: 3}),
                  "011212003012": ("Rural", {2010: 5})}
        rows = {(r[2]): r[3] for r in fh.class_sum_rows(1, series, set()) if r[1] == 2010}
        self.assertEqual(rows["small_cities"], 14)
        self.assertEqual(rows["villages"], 8)
        self.assertEqual(rows["all_whole_gminas_types_1_2_3"], 22)
        self.assertEqual(rows["small_cities"] + rows["villages"], rows["all_whole_gminas_types_1_2_3"])


if __name__ == "__main__":
    unittest.main()
