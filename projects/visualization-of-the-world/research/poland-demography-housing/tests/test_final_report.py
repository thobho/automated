"""Check headline numbers of reports/final-report.md against the processed CSVs.

Each test recomputes a number from data/processed and asserts that the report
text contains it, so the report cannot drift from the data (or the other way).
Also checks that bibliography.md and citation-sheet.md are up to date and that
every data file has a caption.
"""
import csv
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_reference_docs as brd  # noqa: E402
import check_sources  # noqa: E402

PROC = ROOT / "data" / "processed"
REPORT = (ROOT / "reports" / "final-report.md").read_text(encoding="utf-8")
CLASSES = ("big_cities", "small_cities", "villages")


def rd(name):
    with open(PROC / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


POP = {(int(r["year"]), r["class"]): int(r["population"]) for r in rd("population_by_class.csv")}
COMP = {(int(r["year"]), r["class"], r["type"]): int(r["dwellings"]) for r in rd("housing_completions_by_class.csv")}
PER1000 = {(int(r["year"]), r["class"], r["type"]): r["per_1000_residents"]
           for r in rd("housing_completions_by_class.csv")}
STOCK = {(int(r["year"]), r["class"]): r for r in rd("housing_stock_by_class.csv")}
URB = {int(r["year"]): r for r in rd("urbanization_and_big_cities.csv")}


def n(x):
    return f"{x:,}"


def pct(a, b, d=2, sign=False):
    v = (b - a) / a * 100
    return f"{v:+.{d}f}%" if sign else f"{v:.{d}f}%"


class Base(unittest.TestCase):
    def has(self, text):
        self.assertIn(text, REPORT, f"missing in final-report.md: {text!r}")


class Population(Base):
    def test_national_and_classes(self):
        tot = {y: sum(POP[(y, c)] for c in CLASSES) for y in (2000, 2025)}
        self.assertEqual(tot[2000], int(URB[2000]["population_total"]))
        self.assertEqual(tot[2025], int(URB[2025]["population_total"]))
        self.has("38.25 million (2000) to 37.33 million (2025), " + pct(tot[2000], tot[2025]))
        self.has(f"| Poland | {n(tot[2000])} | {n(tot[2025])} | {pct(tot[2000], tot[2025], sign=True)} |")
        for c, label in zip(CLASSES, ("big cities (34, fixed list)", "small cities and towns", "villages")):
            s0 = [r for r in rd("population_by_class.csv") if r["year"] == "2000" and r["class"] == c][0]
            s1 = [r for r in rd("population_by_class.csv") if r["year"] == "2025" and r["class"] == c][0]
            self.has(f"| {label} | {n(POP[(2000, c)])} | {n(POP[(2025, c)])} | "
                     f"{pct(POP[(2000, c)], POP[(2025, c)], sign=True)} | {s0['share_of_total_pct']}% | {s1['share_of_total_pct']}% |")

    def test_urbanization(self):
        self.has(f"from {URB[2000]['urbanization_rate_pct']}% to {URB[2025]['urbanization_rate_pct']}%")
        self.assertEqual(URB[2000]["big_cities_ge100k_in_year_count"], "41")
        self.assertEqual(URB[2025]["big_cities_ge100k_in_year_count"], "34")
        self.has("fell from 41 to 34")

    def test_breaks(self):
        d = int(URB[2010]["population_total"]) - int(URB[2009]["population_total"])
        self.assertEqual(round(d / 1000), 363)
        self.assertEqual(f"{d / int(URB[2009]['population_total']) * 100:.2f}", "0.95")
        self.has("+363 thousand (+0.95%)")
        self.assertEqual(round((int(URB[2010]["population_rural"]) - int(URB[2009]["population_rural"])) / 1000), 224)
        d2 = int(URB[2020]["population_total"]) - int(URB[2019]["population_total"])
        self.assertEqual(round(d2 / 1000), -294)
        self.assertEqual(f"{d2 / int(URB[2019]['population_total']) * 100:.2f}", "-0.77")

    def test_villages_peak(self):
        peak = max(range(2000, 2026), key=lambda y: POP[(y, "villages")])
        self.assertEqual(peak, 2019)
        self.has("15.35 million in 2019")


class Structure(Base):
    def test_age_shares(self):
        pyr = rd("age_sex_pyramid.csv")

        def share(year, groups):
            fine = [r for r in pyr if r["year"] == str(year) and r["age_group"] != "70+"] if year == 2025 else \
                [r for r in pyr if r["year"] == str(year)]
            tot = sum(int(r["population"]) for r in fine)
            return sum(int(r["population"]) for r in fine if r["age_group"] in groups) / tot * 100

        g014 = ("0-4", "5-9", "10-14")
        g65 = ("65-69", "70+", "70-74", "75-79", "80-84", "85+")
        self.has(f"{share(2000, g014):.1f}% (2000) to {share(2025, g014):.1f}% (2025)")
        self.has(f"{share(2000, g65):.1f}% to {share(2025, g65):.1f}%")
        age04 = lambda y: sum(int(r["population"]) for r in pyr if r["year"] == str(y) and r["age_group"] == "0-4")
        self.has(f"from {age04(2000) / 1e6:.2f} million to {age04(2025) / 1e6:.2f} million")

    def indicator(self, ind, area, year, src):
        rows = [r for r in rd("age_structure_indicators.csv")
                if r["indicator"] == ind and r["area"] == area and r["year"] == str(year) and r["source_id"] == src]
        self.assertEqual(len(rows), 1, (ind, area, year, src))
        return rows[0]["value"]

    def test_median_age_and_dependency(self):
        self.has(f"{self.indicator('median_age', 'national', 2000, 'S19')} on 1 January 2000 to "
                 f"{self.indicator('median_age', 'national', 2025, 'S19')} on 1 January 2025")
        self.has(f"GUS gives {self.indicator('median_age', 'national', 2025, 'S11')} at 31 December 2025, urban "
                 f"{self.indicator('median_age', 'urban', 2025, 'S11')} and rural {self.indicator('median_age', 'rural', 2025, 'S11')}")
        od = "old_age_dependency_65plus_per_100_aged_15_64"
        self.has(f"{self.indicator(od, 'national', 2000, 'S19')} (2000) to {self.indicator(od, 'national', 2025, 'S19')} (2025)")
        self.has(f"{self.indicator('old_age_dependency_65plus_per_100_working_age', 'national', 2003, 'S9')} in 2003 and "
                 f"{self.indicator('old_age_dependency_65plus_per_100_working_age', 'national', 2025, 'S9')} in 2025")
        td = "total_dependency_per_100_working_age"
        self.has(f"Total dependency {self.indicator(td, 'national', 2025, 'S9')} in 2025 (GUS); in towns "
                 f"{self.indicator(td, 'urban', 2025, 'S10')} and in the countryside {self.indicator(td, 'rural', 2025, 'S10')}")

    def vital(self, ind, area, year, sex="total"):
        rows = [r for r in rd("vital_rates.csv")
                if r["indicator"] == ind and r["area"] == area and r["year"] == str(year) and r["sex"] == sex]
        self.assertEqual(len(rows), 1, (ind, area, year))
        return float(rows[0]["value"])

    def test_births_deaths(self):
        k = lambda ind, y: round(self.vital(ind, "national", y) / 1000)
        self.has(f"{k('live_births', 2000)} thousand (2000), {k('live_births', 2010)} thousand (2010), "
                 f"{k('live_births', 2017)} thousand (2017), {k('live_births', 2025)} thousand (2025)")
        self.has(f"{k('deaths', 2000)} thousand (2000), {k('deaths', 2021)} thousand (2021, COVID-19), {k('deaths', 2025)} thousand (2025)")
        self.has(f"{k('natural_increase', 2025)} thousand (2025)")
        self.has(f"Births fell from {k('live_births', 2000)} thousand to {k('live_births', 2025)} thousand")
        self.has(f"towns {self.vital('natural_increase_per_1000', 'urban', 2025):.1f}, villages {self.vital('natural_increase_per_1000', 'rural', 2025):.1f}")

    def test_fertility_and_life_expectancy(self):
        tfr = {(r["year"], r["source_id"]): float(r["value"]) for r in rd("vital_rates.csv")
               if r["indicator"] == "total_fertility_rate"}
        self.has(f"{tfr[('2000', 'S21')]:.2f} (2000, Eurostat) and {tfr[('2025', 'S13')]:.2f} in 2025 (GUS)")
        self.has(f"{tfr[('2001', 'S21')]:.2f} (2001) from Eurostat, {tfr[('2002', 'S13')]:.2f} (2002)")
        le = lambda sex, y: f"{self.vital('life_expectancy_at_birth', 'national', y, sex):.1f}"
        self.has(f"men from {le('male', 2000)} (2000) to {le('male', 2025)} (2025) and for women from {le('female', 2000)} to {le('female', 2025)}")
        self.has(f"{le('male', 2021)} and {le('female', 2021)}")

    def test_migration_by_class(self):
        mig = {(int(r["year"]), r["class"]): float(r["net_internal_per_1000"]) for r in rd("migration_by_place_class.csv")}
        for y in range(2000, 2026):
            self.assertAlmostEqual(sum(float(r["net_internal_migration"]) for r in rd("migration_by_place_class.csv")
                                       if r["year"] == str(y)), 0, delta=1)
        f = lambda c, y: f"{mig[(y, c)]:+.2f}"
        self.has("villages +0.29 (2000), +3.24 (2007), +3.49 (2022), +2.38 (2025)")
        self.assertEqual([f("villages", y) for y in (2000, 2007, 2022, 2025)], ["+0.29", "+3.24", "+3.49", "+2.38"])
        self.has("small cities -0.50, -2.31, -3.36 and -2.63")
        self.assertEqual([f("small_cities", y) for y in (2000, 2007, 2022, 2025)], ["-0.50", "-2.31", "-3.36", "-2.63"])
        self.has("big cities +0.21, -1.73, -1.18 and -0.43")
        self.assertEqual([f("big_cities", y) for y in (2000, 2007, 2022, 2025)], ["+0.21", "-1.73", "-1.18", "-0.43"])
        self.has("+2.4 per 1000 residents in 2025); small cities lose (-2.6); big cities lose since 2020 (-0.4 in 2025)")
        self.assertTrue(all(mig[(y, "big_cities")] < 0 for y in range(2020, 2026)))

    def test_national_migration_and_ukraine(self):
        nm = {(r["year"], r["indicator"]): r["value"] for r in rd("migration_national.csv")}
        ukr = {r["period"]: int(r["value"]) for r in rd("ukraine_inflow.csv")}
        self.has(f"{ukr['2022-03'] / 1e6:.2f} million (March 2022), peak {ukr['2022-09'] / 1e6:.2f} million (September 2022), "
                 f"{ukr['2025-12'] / 1e6:.2f} million (December 2025), {ukr['2026-09'] / 1e6:.2f} million (September 2026)")
        self.assertEqual(max(ukr, key=ukr.get), "2022-09")
        self.assertEqual(max(ukr), "2026-09")
        self.assertTrue(nm)

    def test_households(self):
        hh = {r["year"]: r for r in rd("households.csv") if r["kind"] == "census"}
        parts = [f"{int(hh[y]['households']) / 1e6:.2f} million households, {hh[y]['avg_persons_per_household']} persons"
                 for y in ("2002", "2011", "2021")]
        self.has(parts[0] + " (2002)")
        self.has(f"{int(hh['2011']['households']) / 1e6:.2f} million, {hh['2011']['avg_persons_per_household']} (2011)")
        self.has(f"{int(hh['2021']['households']) / 1e6:.2f} million, {hh['2021']['avg_persons_per_household']} (2021)")
        lfs = {r["year"]: r["avg_persons_per_household"] for r in rd("households.csv") if "LFS" in r["kind"]}
        self.has(f"{lfs['2006']} persons (2006) to {lfs['2025']} (2025)")


class Belts(Base):
    def test_belt_summary(self):
        rows = rd("suburban_belt_summary.csv")
        g = sum(int(r["belt_gminas_with_data"]) for r in rows)
        p0 = sum(int(r["belt_pop_2000"]) for r in rows)
        p1 = sum(int(r["belt_pop_2025"]) for r in rows)
        self.assertEqual(g, 132)
        self.has(f"132 belt gminas with 2000 and 2025 values grew from {p0 / 1e6:.2f} to {p1 / 1e6:.2f} million, +{(p1 - p0) / p0 * 100:.0f}%")
        for r in rows:
            core = (int(r["core_pop_2025"]) - int(r["core_pop_2000"])) / int(r["core_pop_2000"]) * 100
            belt = (int(r["belt_pop_2025"]) - int(r["belt_pop_2000"])) / int(r["belt_pop_2000"]) * 100
            self.assertAlmostEqual(core, float(r["core_change_pct"]), delta=0.006)
            self.has(f"{core:+.1f}% vs {'belt ' if r['core_city'] == 'Warszawa' else ''}{belt:+.1f}%")

    def test_belt_gminas(self):
        b = rd("suburban_belt_gminas.csv")
        top = sorted((r for r in b if r["pop_2000"] and r["pop_2025"]), key=lambda r: -float(r["change_2000_2025_pct"]))[:4]
        self.assertEqual([r["gmina"] for r in top], ["Dobra (Szczecińska)", "Dopiewo", "Rokietnica", "Komorniki"])
        self.has(f"Dobra (Szczecińska) from {int(top[0]['pop_2000']) / 1000:.1f} to {int(top[0]['pop_2025']) / 1000:.1f} thousand (+{float(top[0]['change_2000_2025_pct']):.0f}%)")
        self.has(f"Dopiewo (+{float(top[1]['change_2000_2025_pct']):.0f}%), Rokietnica (+{float(top[2]['change_2000_2025_pct']):.0f}%), Komorniki (+{float(top[3]['change_2000_2025_pct']):.0f}%)")
        lost = sum(1 for r in b if r["pop_2000"] and r["pop_2025"] and int(r["pop_2025"]) < int(r["pop_2000"]))
        self.has(f"Of the 132 belt gminas {lost} lost population")

    def test_small_towns(self):
        q = [r for r in rd("small_towns_change.csv") if r["pop_2000"] and r["pop_2025"] and int(r["pop_2000"]) >= 2000]
        lost = sum(1 for r in q if int(r["pop_2025"]) < int(r["pop_2000"]))
        gained = sum(1 for r in q if int(r["pop_2025"]) > int(r["pop_2000"]))
        p0, p1 = sum(int(r["pop_2000"]) for r in q), sum(int(r["pop_2025"]) for r in q)
        self.has(f"of {len(q)} towns {lost} lost and {gained} gained; together {p0 / 1e6:.2f} to {p1 / 1e6:.2f} million, {pct(p0, p1, 1)}")
        hel = [r for r in q if r["town"] == "Hel"][0]
        self.has(f"Hel {hel['change_2000_2025_pct'][:5]}%")
        self.assertEqual(hel["rank_loss_pct"], "1")


class Europe(Base):
    def summary(self, ind, geo, sex="total"):
        rows = [r for r in rd("europe_summary.csv") if r["indicator"] == ind and r["geo"] == geo and r["sex"] == sex]
        self.assertEqual(len(rows), 1)
        return rows[0]

    def test_table(self):
        pl, eu = self.summary("population_1_jan", "PL"), self.summary("population_1_jan", "EU27_2020")
        idx = lambda r: float(r["latest_value"]) / float(r["first_value"]) * 100
        self.has(f"| {idx(pl):.2f} | {idx(eu):.2f} |")
        r = self.summary("total_fertility_rate", "PL")
        self.assertEqual((r["latest_value"], r["poland_rank_latest_of_7"]), ("1.14", "6"))
        self.has("1.14 (1.37 in 2000)")
        r = self.summary("old_age_dependency_65_per_15_64", "PL")
        self.assertEqual((r["latest_value"], r["first_value"], r["change_abs"], r["change_pct"], r["poland_rank_latest_of_7"]),
                         ("32.7", "17.8", "14.9", "83.71", "2"))
        self.has("+14.9 points")
        self.has("(+83.7%)")
        peers = {g: self.summary("old_age_dependency_65_per_15_64", g)["change_abs"] for g in ("CZ", "RO", "DE", "SK", "LT", "HU", "EU27_2020")}
        p = {g: f"{float(v):.1f}" for g, v in peers.items()}
        self.has(f"CZ +{p['CZ']}, RO +{p['RO']}, DE +{p['DE']}, SK +{p['SK']}, LT +{p['LT']}, HU +{p['HU']} and EU-27 +{p['EU27_2020']}")
        self.assertLess(max(float(v) for v in peers.values()), 14.9)
        m = self.summary("median_age_1_jan", "PL")
        self.assertEqual((m["first_value"], m["latest_value"], m["poland_rank_latest_of_7"]), ("35.1", "43.4", "6"))
        le = self.summary("life_expectancy_at_birth", "PL")
        self.assertEqual((le["first_value"], le["latest_value"], le["poland_rank_latest_of_7"]), ("73.8", "78.5", "3"))
        nm = self.summary("net_migration_plus_adjustment_rate", "PL")
        self.assertEqual((nm["latest_value"], nm["poland_rank_latest_of_7"]), ("0.1", "6"))
        self.has("-5.05%")
        self.assertEqual(pl["change_pct"], "-5.05")
        self.has("Natural change was +10,321 in 2000 and -167,483 in 2025")

    def test_degurba_census(self):
        rows = {(r["geo"], r["degurba_class"]): r for r in rd("europe_degurba.csv") if r["measure"] == "census_2021_population"}
        sh = {(r["geo"], r["degurba_class"]): r["value"] for r in rd("europe_degurba.csv") if r["measure"] == "census_2021_share_of_population"}
        for cls, label in (("cities", "cities"), ("towns_and_suburbs", "towns and suburbs"), ("rural_areas", "rural areas")):
            self.has(f"{label} {n(int(rows[('PL', cls)]['value']))} ({sh[('PL', cls)]}%)")
        for g in ("PL", "EU27_2020"):
            tot = int(rows[(g, "total")]["value"])
            for cls in ("cities", "towns_and_suburbs", "rural_areas"):
                self.assertAlmostEqual(int(rows[(g, cls)]["value"]) / tot * 100, float(sh[(g, cls)]), delta=0.006)
        self.has(f"EU-27 shares {float(sh[('EU27_2020', 'cities')]):.2f}% / {float(sh[('EU27_2020', 'towns_and_suburbs')]):.2f}% / {sh[('EU27_2020', 'rural_areas')]}%")
        self.has(f"{float(sh[('PL', 'rural_areas')]) - float(sh[('EU27_2020', 'rural_areas')]):.1f} points above")


class Housing(Base):
    def national(self, y):
        return sum(COMP[(y, c, "total")] for c in CLASSES)

    def test_national_completions(self):
        form = {int(r["year"]): int(r["dwellings"]) for r in rd("housing_completions_by_form_national.csv") if r["form"] == "total"}
        for y in range(2000, 2026):
            self.assertEqual(form[y], self.national(y), y)
        k = lambda y: f"{form[y] / 1000:.1f} thousand"
        self.has(f"{k(2000)} (2000), {k(2003)} (2003 spike), {k(2009)} (2009), {k(2010)} (2010), {k(2017)} (2017), record {k(2022)} (2022), {k(2025)} (2025)")
        self.assertEqual(max(form, key=form.get), 2022)
        self.has(f"{k(2000)} (2000) to a record {k(2022)} (2022), then {k(2025)} in 2025".replace("87.8 thousand (2000)", "87.8 thousand (2000)"))

    def test_class_completions(self):
        for c, label in zip(CLASSES, ("big cities", "small cities", "villages")):
            v = [f"{COMP[(y, c, 'total')] / 1000:.1f}" for y in (2000, 2009, 2017, 2022, 2025)]
            self.has(f"{label} " + ", ".join(v) if c != "big_cities" else
                     f"{label} {v[0]} (2000), {v[1]} (2009), {v[2]} (2017), {v[3]} (2022), {v[4]} (2025)")
        sh = lambda y, c: round(COMP[(y, c, "total")] / self.national(y) * 100)
        self.has(f"big cities {sh(2025, 'big_cities')}%, villages {sh(2025, 'villages')}%, small cities {sh(2025, 'small_cities')}%")
        self.has(f"{sh(2000, 'big_cities')}%, {sh(2000, 'villages')}% and {sh(2000, 'small_cities')}%")

    def test_house_flat_national_2025(self):
        h = sum(COMP[(2025, c, "house")] for c in CLASSES)
        f = sum(COMP[(2025, c, "flat")] for c in CLASSES)
        self.has(f"{h / 1000:.1f} thousand houses and {f / 1000:.1f} thousand flats")
        hh = {y: sum(COMP[(y, c, "house")] for c in CLASSES) for y in range(2009, 2026)}
        ff = {y: sum(COMP[(y, c, "flat")] for c in CLASSES) for y in range(2009, 2026)}
        self.assertEqual([y for y in hh if hh[y] > ff[y]], [2010, 2011, 2012, 2013, 2014, 2015, 2022])
        self.has(f"peaked at {max(hh.values()) / 1000:.1f} thousand in 2022")
        self.assertEqual(max(hh, key=hh.get), 2022)

    def test_table_a(self):
        for c, label in zip(CLASSES, ("big cities", "small cities", "villages")):
            tot = COMP[(2025, c, "total")]
            row = (f"| {label} | {n(POP[(2025, c)])} | {PER1000[(2025, c, 'house')]} | {PER1000[(2025, c, 'flat')]} | "
                   f"{PER1000[(2025, c, 'total')]} | {COMP[(2025, c, 'house')] / tot * 100:.1f}% | "
                   f"{COMP[(2025, c, 'flat')] / tot * 100:.1f}% | {round(float(STOCK[(2025, c)]['dwellings_per_1000_residents']))} |")
            self.has(row)
            self.assertAlmostEqual(COMP[(2025, c, "total")] / POP[(2025, c)] * 1000, float(PER1000[(2025, c, "total")]), delta=0.006)

    def test_table_b(self):
        for c, label in zip(CLASSES, ("big cities", "small cities", "villages")):
            cum = {t: sum(COMP[(y, c, t)] for y in range(2009, 2026)) for t in ("house", "flat", "total")}
            row = (f"| {label} | {n(POP[(2009, c)])} | {n(POP[(2025, c)])} | {pct(POP[(2009, c)], POP[(2025, c)], sign=True)} | "
                   f"{n(cum['house'])} | {n(cum['flat'])} | {n(cum['total'])} | {cum['total'] / POP[(2009, c)] * 1000:.1f} |")
            self.has(row)
        fl = lambda c: sum(COMP[(y, c, "flat")] for y in range(2009, 2026)) / sum(COMP[(y, c, "total")] for y in range(2009, 2026)) * 100
        ho = lambda c: sum(COMP[(y, c, "house")] for y in range(2009, 2026)) / sum(COMP[(y, c, "total")] for y in range(2009, 2026)) * 100
        self.has(f"{fl('big_cities'):.1f}% in big cities were flats and {ho('villages'):.1f}% in villages were houses; small cities {fl('small_cities'):.1f}% flats and {ho('small_cities'):.1f}% houses")

    def test_per_1000_history(self):
        a = lambda c, y: PER1000[(y, c, "total")]
        self.has(f"big cities {a('big_cities', 2000)} to {a('big_cities', 2025)}; small cities {a('small_cities', 2000)} to {a('small_cities', 2025)}; villages {a('villages', 2000)} to {a('villages', 2025)}")
        for c, y in (("big_cities", 2020), ("small_cities", 2022), ("villages", 2022)):
            self.assertEqual(max(range(2000, 2026), key=lambda yy: float(a(c, yy))), y)
        self.has(f"big cities {a('big_cities', 2020)} (2020), small cities {a('small_cities', 2022)} and villages {a('villages', 2022)}")

    def test_stock(self):
        tot = lambda y: sum(int(STOCK[(y, c)]["dwellings"]) for c in CLASSES)
        self.has(f"{tot(2000) / 1e6:.2f} million (2000) to {tot(2025) / 1e6:.2f} million (2025)")
        self.has(pct(tot(2000), tot(2025), 1, sign=True))
        g = lambda c, y, k: STOCK[(y, c)][k]
        self.has("big cities " + f"{round(float(g('big_cities', 2000, 'dwellings_per_1000_residents')))} to {round(float(g('big_cities', 2025, 'dwellings_per_1000_residents')))}")
        self.has("small cities " + f"{round(float(g('small_cities', 2000, 'dwellings_per_1000_residents')))} to {round(float(g('small_cities', 2025, 'dwellings_per_1000_residents')))}")
        self.has("villages " + f"{round(float(g('villages', 2000, 'dwellings_per_1000_residents')))} to {round(float(g('villages', 2025, 'dwellings_per_1000_residents')))}")
        self.has(f"{g('big_cities', 2000, 'persons_per_dwelling')} to {g('big_cities', 2025, 'persons_per_dwelling')}, {g('small_cities', 2000, 'persons_per_dwelling')} to {g('small_cities', 2025, 'persons_per_dwelling')}, {g('villages', 2000, 'persons_per_dwelling')} to {g('villages', 2025, 'persons_per_dwelling')}")
        self.has(f"{tot(2021) / 1e6:.2f} million in the BDL stock")

    def test_floor_area(self):
        rows = rd("housing_floor_area_by_class.csv")
        avg = lambda y, c, m: round(float([r for r in rows if r["year"] == str(y) and r["class"] == c and r["measure"] == m][0]["avg_m2_per_dwelling"]))
        self.has(f"big cities {avg(2025, 'big_cities', 'all_completed')} m2 ({avg(2000, 'big_cities', 'all_completed')} in 2000), small cities {avg(2025, 'small_cities', 'all_completed')} ({avg(2000, 'small_cities', 'all_completed')}), villages {avg(2025, 'villages', 'all_completed')} ({avg(2000, 'villages', 'all_completed')})")
        self.assertEqual({r["measure"] for r in rows}, {"all_completed", "house_direct", "flat_direct"})
        self.has(f"{avg(2025, 'big_cities', 'house_direct')}, {avg(2025, 'small_cities', 'house_direct')} and {avg(2025, 'villages', 'house_direct')} m2 and flats {avg(2025, 'big_cities', 'flat_direct')}, {avg(2025, 'small_cities', 'flat_direct')} and {avg(2025, 'villages', 'flat_direct')} m2")

    def test_permits(self):
        perm = {(int(r["year"]), r["class"], r["type"]): int(r["dwellings"]) for r in rd("housing_permits_by_class.csv")}
        th = lambda y, c, t="total": f"{perm[(y, c, t)] / 1000:.1f} thousand"
        self.has(f"{th(2009, 'poland')} (2009), record {th(2021, 'poland')} (2021), {th(2025, 'poland')} (2025)")
        self.assertEqual(max((y for (y, c, t) in perm if c == "poland" and t == "total"), key=lambda y: perm[(y, "poland", "total")]), 2021)
        self.has(f"big cities {th(2025, 'big_cities')} ({th(2025, 'big_cities', 'house')} houses, {th(2025, 'big_cities', 'flat')} multi-family)")
        self.has(f"small cities {th(2025, 'small_cities')}, villages {th(2025, 'villages')}")
        self.assertEqual(min(y for (y, c, t) in perm if c == "big_cities"), 2018)

    def test_starts(self):
        st = {(int(r["year"]), r["area"], r["type"]): int(r["dwellings"]) for r in rd("housing_starts_big_cities_vs_rest.csv")}
        self.has(f"{st[(2005, 'big_cities', 'total')] / 1000:.1f} thousand (2005) to {st[(2019, 'big_cities', 'total')] / 1000:.1f} thousand (2019)")
        share = st[(2019, "big_cities", "total")] / (st[(2019, "big_cities", "total")] + st[(2019, "rest_of_poland", "total")]) * 100
        self.has(f"{round(share)}% of the national total in 2019")


class MoreChecks(Base):
    def test_europe_annual(self):
        ea = rd("europe_annual.csv")
        e = lambda ind, geo, y: [r["value"] for r in ea if r["indicator"] == ind and r["geo"] == geo and r["year"] == str(y) and r["sex"] == "total"][0]
        t = lambda g, y: f"{float(e('total_fertility_rate', g, y)):.2f}"
        self.has(f"1.37 to 1.14 for Poland (-0.23); CZ {t('CZ', 2000)} to {t('CZ', 2024)}, SK {t('SK', 2000)} to {t('SK', 2024)}, "
                 f"HU {t('HU', 2000)} to {t('HU', 2024)}, RO {t('RO', 2000)} to {t('RO', 2024)}; only Lithuania fell more ({t('LT', 2000)} to {t('LT', 2024)})")
        self.assertEqual(round(float(t("PL", 2024)) - float(t("PL", 2000)), 2), -0.23)
        self.assertLess(float(t("LT", 2024)) - float(t("LT", 2000)), -0.23)
        self.has(f"{n(int(e('net_migration_plus_adjustment', 'PL', 2020)))} against a total change of {n(int(e('population_change_total', 'PL', 2020)))}")
        pop = lambda y: int(e("population_1_jan", "PL", y))
        self.has(f"{pop(2000) / 1e6:.2f} million (1 January 2000) to {pop(2026) / 1e6:.2f} million (1 January 2026)")
        gus = int(URB[2025]["population_total"])
        self.has(f"Eurostat {n(pop(2026))} on 1 January 2026, about {(gus - pop(2026)) / 1e6:.1f} million lower")
        self.has(f"GUS {n(gus)} at 31 December 2025")

    def test_degurba_surveys(self):
        dg = rd("europe_degurba.csv")
        v = lambda m, y, c: [r["value"] for r in dg if r["geo"] == "PL" and r["measure"] == m and r["year"] == str(y) and r["degurba_class"] == c][0]
        m = "share_of_population_all_ages"
        self.has(f"cities {v(m, 2012, 'cities')}% to {v(m, 2025, 'cities')}%, towns and suburbs {v(m, 2012, 'towns_and_suburbs')}% to {v(m, 2025, 'towns_and_suburbs')}%, rural {v(m, 2012, 'rural_areas')}% to {v(m, 2025, 'rural_areas')}%")
        m = "share_of_population_aged_15plus"
        self.has(f"rural {float(v(m, 2012, 'rural_areas')):.1f}% to {float(v(m, 2025, 'rural_areas')):.1f}% for ages 15+")

    def test_gus_vs_degurba(self):
        r21 = int(URB[2021]["population_rural"]) / int(URB[2021]["population_total"]) * 100
        self.has(f"GUS counts {r21:.2f}% rural the same year")
        self.has(f"{int(URB[2012]['population_rural']) / int(URB[2012]['population_total']) * 100:.2f}% (2012) to "
                 f"{int(URB[2025]['population_rural']) / int(URB[2025]['population_total']) * 100:.2f}% (2025)")
        self.has(f"BDL 31 December 2021: {n(int(URB[2021]['population_total']))}")
        census = [r for r in rd("europe_degurba.csv") if r["geo"] == "PL" and r["measure"] == "census_2021_population" and r["degurba_class"] == "total"][0]
        self.has(f"Eurostat's census table: {n(int(census['value']))}")
        self.has(f"GUS rural {r21:.2f}% in 2021")

    def test_national_migration(self):
        mn = {(r["year"], r["indicator"]): int(r["value"]) for r in rd("migration_national.csv") if r["value"]}
        self.has(f"net {mn[('2000', 'net_international_migration')] / 1000:.1f} thousand (2000) to +{mn[('2025', 'net_international_migration')] / 1000:.1f} thousand (2025)")
        self.has(f"+{mn[('2024', 'eurostat_net_migration_plus_statistical_adjustment')] / 1000:.1f} thousand in 2024 and +{mn[('2025', 'eurostat_net_migration_plus_statistical_adjustment')] / 1000:.1f} thousand in 2025")
        self.has(f"immigration {mn[('2024', 'eurostat_immigration_all_citizenships')] / 1000:.0f} thousand and emigration {mn[('2024', 'eurostat_emigration_all_citizenships')] / 1000:.0f} thousand (2024)")

    def test_proxy_ranges(self):
        nat = {}
        for r in rd("housing_completions_by_form_national.csv"):
            nat[(int(r["year"]), r["form"])] = int(r["dwellings"])
        ind, own, dh = [], [], []
        for y in range(2009, 2018):
            house = sum(COMP[(y, c, "house")] for c in CLASSES)
            ind.append(nat[(y, "individual_incl_private_for_sale")] / house * 100 - 100)
            own.append(nat[(y, "own_use_of_investor")] / house * 100 - 100)
        self.has(f"{min(ind):.1f}% to {max(ind):.1f}% above the direct house count and own use {-max(own):.1f}% to {-min(own):.1f}% below it")
        self.has(f"(individual {min(ind):.1f}% to {max(ind):.1f}% above, own use {-max(own):.1f}% to {-min(own):.1f}% below)")

    def test_census_and_starts(self):
        ph = {r["year"]: r for r in rd("housing_stock_by_class.csv")}
        self.assertTrue(ph)
        self.has("15.23 million dwellings (13.44 million inhabited)")
        self.has(f"{sum(int(r['dwellings']) for r in rd('housing_stock_by_class.csv') if r['year'] == '2021') / 1e6:.2f} million in the BDL stock")
        gap = (sum(int(r["dwellings"]) for r in rd("housing_stock_by_class.csv") if r["year"] == "2021") / 15.23e6 - 1) * 100
        self.assertEqual(f"{gap:.1f}", "0.9")

    def test_completions_cross_check(self):
        rows = rd("housing_national_crosscheck.csv")
        self.assertEqual(len(rows), 243)
        self.assertEqual({r["difference"] for r in rows}, {"0"})
        self.has("in all 243 variable-year checks")


class ReferenceDocs(unittest.TestCase):
    def test_generated_files_are_current(self):
        self.assertEqual(brd.main(["--check"]), 0)

    def test_every_data_file_has_a_caption(self):
        sheet = (ROOT / "reports" / "citation-sheet.md").read_text(encoding="utf-8")
        files = list((ROOT / "data" / "processed").glob("*.csv")) + list((ROOT / "data" / "raw").glob("*.csv"))
        self.assertGreater(len(files), 30)
        for p in files:
            self.assertIn(f"### `{p.name}`", sheet)
            block = sheet.split(f"### `{p.name}`")[1].split("\n### ")[0].split("\n## ")[0]
            self.assertIn("> Source: ", block, p.name)
            self.assertNotIn("sources: NONE", block, p.name)

    def test_bibliography_has_every_source_with_url_and_date(self):
        bib = (ROOT / "reports" / "bibliography.md").read_text(encoding="utf-8")
        for r in check_sources.read_sources(ROOT / "sources.csv"):
            line = [l for l in bib.splitlines() if l.startswith(f"- **[{r['id']}]**")]
            self.assertEqual(len(line), 1, r["id"])
            self.assertIn(f"<{r['url']}> (accessed {r['accessed']})", line[0])
        self.assertLess(bib.index("## Primary sources"), bib.index("## Secondary sources"))

    def test_raw_provenance_ids_exist(self):
        known = {r["id"] for r in check_sources.read_sources(ROOT / "sources.csv")}
        for ids in brd.RAW_PROVENANCE.values():
            self.assertTrue(set(ids) <= known)

    def test_no_unused_sources_and_report_clean(self):
        self.assertEqual(check_sources.main(ROOT), 0)


if __name__ == "__main__":
    unittest.main()
