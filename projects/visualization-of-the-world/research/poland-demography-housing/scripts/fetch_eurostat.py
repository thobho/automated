#!/usr/bin/env python3
"""Fetch Poland series from the Eurostat API into data/raw/eurostat_poland.csv (dataset,series,period,value,flag).

demo_pjanind (median age, dependency ratios), demo_gind (births, deaths, natural change, net migration + adjustment),
demo_find (total fertility rate), migr_imm1ctz / migr_emi1ctz (immigration / emigration, total and Ukrainian citizens),
migr_asytpsm (beneficiaries of temporary protection, Ukrainian citizens, monthly), lfst_hhantych (persons per household).
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eurostat  # noqa: E402

RAW = eurostat.CACHE.parent
PL = ("geo", "PL")
SINCE = ("sinceTimePeriod", "2000")
REQUESTS = [
    ("demo_pjanind", "median_age", [PL, SINCE, ("indic_de", "MEDAGEPOP")], "indic_de"),
    ("demo_pjanind", "old_age_dependency_65_per_15_64", [PL, SINCE, ("indic_de", "OLDDEP1")], "indic_de"),
    ("demo_pjanind", "total_dependency_per_15_64", [PL, SINCE, ("indic_de", "DEPRATIO1")], "indic_de"),
    ("demo_gind", "live_births", [PL, SINCE, ("indic_de", "LBIRTH")], "indic_de"),
    ("demo_gind", "deaths", [PL, SINCE, ("indic_de", "DEATH")], "indic_de"),
    ("demo_gind", "natural_change", [PL, SINCE, ("indic_de", "NATGROW")], "indic_de"),
    ("demo_gind", "net_migration_plus_adjustment", [PL, SINCE, ("indic_de", "CNMIGRAT")], "indic_de"),
    ("demo_find", "total_fertility_rate", [PL, SINCE, ("indic_de", "TOTFERRT")], "indic_de"),
    ("migr_imm1ctz", "immigration_all_citizenships", [PL, SINCE, ("citizen", "TOTAL"), ("sex", "T"), ("age", "TOTAL"), ("agedef", "COMPLET")], "citizen"),
    ("migr_imm1ctz", "immigration_ukrainian_citizens", [PL, SINCE, ("citizen", "UA"), ("sex", "T"), ("age", "TOTAL"), ("agedef", "COMPLET")], "citizen"),
    ("migr_emi1ctz", "emigration_all_citizenships", [PL, SINCE, ("citizen", "TOTAL"), ("sex", "T"), ("age", "TOTAL"), ("agedef", "COMPLET")], "citizen"),
    ("migr_asytpsm", "temporary_protection_ukrainian_citizens_end_of_month", [PL, ("citizen", "UA"), ("sex", "T"), ("age", "TOTAL"), ("unit", "PER")], "citizen"),
    ("lfst_hhantych", "persons_per_private_household_eu_lfs", [PL, SINCE, ("phhcomp", "TOTAL"), ("agechild", "TOTAL"), ("n_child", "TOTAL")], "phhcomp"),
]


def main():
    rows = []
    for ds, series, params, _ in REQUESTS:
        d = eurostat.get(ds, params)
        n = 0
        for coords, val, flag in eurostat.observations(d):
            rows.append((ds, series, coords["time"], val, flag, d["updated"][:10]))
            n += 1
        print(ds, series, n, "obs", flush=True)
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    with open(RAW / "eurostat_poland.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "series", "period", "value", "eurostat_flag", "dataset_updated"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
