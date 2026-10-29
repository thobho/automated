#!/usr/bin/env python3
"""Fetch the European comparison series from the Eurostat API into data/raw/eurostat_europe.csv.

Countries: PL, CZ, SK, HU, DE, RO, LT and the EU-27 aggregate (EU27_2020), 2000 onwards.
Datasets: demo_gind (population 1 Jan, change, natural change, net migration + adjustment and its crude rate),
demo_find (TFR), demo_pjanind (median age, old-age dependency 65+/15-64), demo_mlexpec (life expectancy at birth),
ilc_lvho01 (share of population by degree of urbanisation, EU-SILC), lfsa_pgauws (population 15+ by degree of
urbanisation, EU-LFS), cens_21urb01 (2021 census round population by degree of urbanisation).
Output columns: dataset,series,geo,period,value,eurostat_flag,dataset_updated.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eurostat  # noqa: E402

RAW = eurostat.CACHE.parent
GEOS = ["PL", "CZ", "SK", "HU", "DE", "RO", "LT", "EU27_2020"]
GEO = [("geo", g) for g in GEOS]
SINCE = [("sinceTimePeriod", "2000")]


def indic(code):
    return [("indic_de", code)]


# (dataset, series name, extra params, dimension that varies inside the series or None)
REQUESTS = [
    ("demo_gind", "population_1_jan", indic("JAN"), None),
    ("demo_gind", "population_change_total", indic("GROW"), None),
    ("demo_gind", "natural_change", indic("NATGROW"), None),
    ("demo_gind", "net_migration_plus_adjustment", indic("CNMIGRAT"), None),
    ("demo_gind", "net_migration_plus_adjustment_rate_per_1000", indic("CNMIGRATRT"), None),
    ("demo_find", "total_fertility_rate", indic("TOTFERRT"), None),
    ("demo_pjanind", "median_age_1_jan", indic("MEDAGEPOP"), None),
    ("demo_pjanind", "old_age_dependency_65_per_15_64", indic("OLDDEP1"), None),
    ("demo_mlexpec", "life_expectancy_at_birth", [("age", "Y_LT1"), ("sex", "T"), ("sex", "M"), ("sex", "F")], "sex"),
    ("ilc_lvho01", "share_of_population_by_degurba_pct",
     [("rskpovth", "TOTAL"), ("building", "TOTAL"), ("deg_urb", "TOTAL"), ("deg_urb", "DEG1"),
      ("deg_urb", "DEG2"), ("deg_urb", "DEG3")], "deg_urb"),
    ("lfsa_pgauws", "population_15plus_by_degurba_thousand",
     [("sex", "T"), ("age", "Y_GE15"), ("wstatus", "POP"), ("deg_urb", "TOTAL"), ("deg_urb", "DEG1"),
      ("deg_urb", "DEG2"), ("deg_urb", "DEG3")], "deg_urb"),
]
CENSUS = ("cens_21urb01", "census_2021_population_by_degurba",
          [("sex", "T"), ("age", "TOTAL"), ("deg_urb", "TOTAL"), ("deg_urb", "DEG1"), ("deg_urb", "DEG2"),
           ("deg_urb", "DEG3")], "deg_urb")


def main():
    rows = []
    jobs = [(ds, s, p + SINCE, dim) for ds, s, p, dim in REQUESTS] + [(CENSUS[0], CENSUS[1], CENSUS[2], CENSUS[3])]
    for ds, series, params, dim in jobs:
        d = eurostat.get(ds, GEO + params)
        n = 0
        for coords, val, flag in eurostat.observations(d):
            name = series if dim is None else f"{series}:{coords[dim]}"
            rows.append((ds, name, coords["geo"], coords["time"], val, flag, d["updated"][:10]))
            n += 1
        print(ds, series, n, "obs", flush=True)
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    with open(RAW / "eurostat_europe.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "series", "geo", "period", "value", "eurostat_flag", "dataset_updated"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
