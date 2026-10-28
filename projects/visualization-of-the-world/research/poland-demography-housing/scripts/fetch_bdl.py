#!/usr/bin/env python3
"""Fetch population data from GUS BDL API v1 into data/raw/*.csv.

Variables (subject P1336, "Population by place of residence and sex divided into
urban and rural areas", place of residence, as of 31 December, total sexes):
  60641 total, 60617 urban areas, 60633 rural areas
Gmina-level (unit level 6) total population comes from the same variable 60641.
Output (all committed, small):
  data/raw/bdl_national.csv  year,indicator,value  (country level)
  data/raw/bdl_gminas.csv    unit_id,name,type_digit,year,value  (gminas with >= MIN_KEEP inhabitants in any year, plus
                             per-year sum of ALL gminas in data/raw/bdl_gmina_sums.csv)
Raw API responses are cached (git-ignored) in data/raw/cache/.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bdl  # noqa: E402

RAW = bdl.ROOT / "data" / "raw"
YEARS = list(range(2000, 2026))
VARS = {"total": 60641, "urban": 60617, "rural": 60633}
MIN_KEEP = 50_000  # keep gminas that ever reached this size (candidates for the 100k class)


def year_params():
    return [("year", y) for y in YEARS]


def fetch_national():
    rows = []
    for name, vid in VARS.items():
        d = bdl.get(f"/data/by-variable/{vid}", [("unit-level", 0)] + year_params())
        res = d["results"]
        assert len(res) == 1 and res[0]["id"] == "000000000000", res
        for v in res[0]["values"]:
            rows.append((int(v["year"]), name, v.get("val")))
    return sorted(rows)


def fetch_gminas():
    units = {}
    sums = defaultdict(int)
    counts = defaultdict(int)
    for r in bdl.paged(f"/data/by-variable/{VARS['total']}", [("unit-level", 6)] + year_params()):
        if r["id"][-1] not in "123":  # 4/5 = urban/rural parts of urban-rural gminas: would double count
            continue
        # Until 2001 Warsaw is one unit ("Capital city Warszawa to 2001") plus its 11 districts
        # ("Warszawa - <district> to 2001"). Keep the whole-city unit, drop the districts (double count).
        if r["name"].endswith(" to 2001") and not r["name"].startswith("Capital city"):
            continue
        units[r["id"]] = {"name": r["name"], "vals": {int(v["year"]): v.get("val") for v in r["values"]}}
        for v in r["values"]:
            if v.get("val") is not None:
                sums[int(v["year"])] += v["val"]
                counts[int(v["year"])] += 1
    return units, sums, counts


def main():
    nat = fetch_national()
    with open(RAW / "bdl_national.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "indicator", "value", "source_id"])
        for y, ind, val in nat:
            w.writerow([y, ind, "" if val is None else val, "S1"])
    units, sums, counts = fetch_gminas()
    with open(RAW / "bdl_gminas.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["unit_id", "name", "year", "value", "source_id"])
        for uid in sorted(units):
            u = units[uid]
            if max((v for v in u["vals"].values() if v is not None), default=0) >= MIN_KEEP:
                for y in YEARS:
                    v = u["vals"].get(y)
                    w.writerow([uid, u["name"], y, "" if v is None else v, "S1"])
    with open(RAW / "bdl_gmina_sums.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "units_with_value", "sum_gminas_types_1_2_3", "source_id"])
        for y in YEARS:
            w.writerow([y, counts[y], sums[y], "S1"])
    print("units", len(units))


if __name__ == "__main__":
    main()
