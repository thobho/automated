"""Tests for the synthetic data generator and the shipped data files (stdlib only)."""
import csv, json, os, subprocess, sys, tempfile, unittest, shutil

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(SITE, "data")


def read(name):
    return open(os.path.join(DATA, name), encoding="utf-8").read()


class DemoData(unittest.TestCase):
    def test_generator_is_deterministic_and_matches_shipped_files(self):
        tmp = tempfile.mkdtemp()
        try:
            # run a copy of the site folder so shipped files are not touched
            shutil.copytree(SITE, os.path.join(tmp, "site"), ignore=shutil.ignore_patterns("docs", "vendor", "node_modules"))
            subprocess.run([sys.executable, os.path.join(tmp, "site", "scripts", "make_demo_data.py")], check=True)
            for f in ("demo.json", "demo-regions.csv", "demo-powiats.csv", "demo-cities.csv"):
                self.assertEqual(open(os.path.join(tmp, "site", "data", f), encoding="utf-8").read(), read(f), f)
        finally:
            shutil.rmtree(tmp)

    def test_shares_sum_to_100_and_are_flagged(self):
        j = json.loads(read("demo.json"))
        self.assertIn("DEMO DATA, NOT REAL", j["meta"]["note"])
        self.assertEqual(len(j["regions"]), 16)
        for r in j["regions"]:
            for i in range(len(j["years"])):
                s = sum(r["shares"][k][i] for k in ("big_cities", "small_cities", "villages"))
                self.assertAlmostEqual(s, 100, delta=0.25, msg=r["name"])

    def test_every_csv_row_is_flagged_demo(self):
        for f in ("demo-regions.csv", "demo-powiats.csv", "demo-cities.csv"):
            rows = list(csv.DictReader(open(os.path.join(DATA, f), encoding="utf-8")))
            self.assertTrue(rows)
            self.assertTrue(all(r["demo_flag"] == "DEMO DATA, NOT REAL" for r in rows), f)

    def test_geo_files_are_small(self):
        total = sum(os.path.getsize(os.path.join(DATA, "geo", f)) for f in os.listdir(os.path.join(DATA, "geo")))
        self.assertLess(total, 1_000_000)

    def test_capabilities_matrix_is_complete(self):
        c = json.loads(read("capabilities.json"))["capabilities"]
        for r in c:
            self.assertIn(r["status"], ("works", "limits", "no"))
            self.assertTrue(r["notes"] and r["code"], r["capability"])
            if r["status"] != "no":
                self.assertTrue(r["code"] != "-", r["capability"])


if __name__ == "__main__":
    unittest.main()
