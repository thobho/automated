#!/usr/bin/env python3
"""Build data/processed/population_by_class.csv and urbanization_and_big_cities.csv
from data/raw/bdl_*.csv (see fetch_bdl.py). Standard library only.

Classes: big cities = cities (urban gminas, BDL type digit 1) with >= 100,000 inhabitants
in the latest year (fixed list); small cities = national urban total minus big cities;
villages = national rural total. See README for the full method and caveats.
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
THRESHOLD = 100_000
# City series that BDL splits over several unit ids (renamed/re-coded units). Same city, no overlap in years.
MERGE = {
    "071412831001": "071412865011",  # Warszawa to 2001 -> since 2002
    "030210363011": "030210365011",  # Wałbrzych to 2002
    "030210321091": "030210365011",  # Wałbrzych 2003-2012 -> since 2013
}
CITY_NAME = {"071412865011": "Warszawa", "030210365011": "Wałbrzych"}


def read_national(path=RAW / "bdl_national.csv"):
    nat = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            nat[(int(r["year"]), r["indicator"])] = int(r["value"]) if r["value"] else None
    return nat


def read_cities(path=RAW / "bdl_gminas.csv"):
    """Return ({unit_id: name}, {unit_id: {year: value}}) for urban gminas (type digit 1), merged."""
    names, vals = {}, defaultdict(dict)
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            uid = r["unit_id"]
            if uid[-1] != "1":
                continue
            uid = MERGE.get(uid, uid)
            names[uid] = CITY_NAME.get(uid, r["name"])
            if r["value"]:
                y = int(r["year"])
                if y in vals[uid]:
                    raise ValueError(f"duplicate value for {uid} {y}")
                vals[uid][y] = int(r["value"])
    return names, vals


def big_city_ids(vals, latest, threshold=THRESHOLD):
    return sorted(u for u, v in vals.items() if v.get(latest, 0) >= threshold)


def build(nat, names, vals, years, threshold=THRESHOLD):
    latest = max(years)
    big = big_city_ids(vals, latest, threshold)
    pop_rows, urb_rows = [], []
    for y in years:
        total, urban, rural = nat[(y, "total")], nat[(y, "urban")], nat[(y, "rural")]
        missing = [names[u] for u in big if y not in vals[u]]
        if missing:
            raise ValueError(f"{y}: big city values missing for {missing}")
        bigpop = sum(vals[u][y] for u in big)
        classes = [
            ("big_cities", bigpop, "derived", f"sum of {len(big)} city populations (list fixed at {latest}, >= {threshold})", "S1"),
            ("small_cities", urban - bigpop, "derived", "urban total - big_cities", "S1"),
            ("villages", rural, "reported", "BDL rural-areas total", "S1"),
        ]
        for cls, pop, kind, formula, sid in classes:
            pop_rows.append({"year": y, "class": cls, "population": pop,
                             "share_of_total_pct": f"{100 * pop / total:.2f}",
                             "value_type": kind, "formula": formula, "source_id": sid})
        in_year = sum(1 for u, v in vals.items() if v.get(y, 0) >= threshold)
        urb_rows.append({"year": y, "population_total": total, "population_urban": urban, "population_rural": rural,
                         "urbanization_rate_pct": f"{100 * urban / total:.2f}",
                         "big_cities_fixed_list_count": len(big),
                         "big_cities_ge100k_in_year_count": in_year,
                         "big_cities_pop_share_pct": f"{100 * bigpop / total:.2f}",
                         "value_type": "derived",
                         "formula": "urban/total; counts of urban gminas with >=100k that year; fixed-list sum/total",
                         "source_id": "S1"})
    return pop_rows, urb_rows, big


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    nat = read_national()
    names, vals = read_cities()
    years = sorted({y for y, _ in nat})
    pop_rows, urb_rows, big = build(nat, names, vals, years)
    write(OUT / "population_by_class.csv", pop_rows)
    write(OUT / "urbanization_and_big_cities.csv", urb_rows)
    write(OUT / "big_city_list.csv", [
        {"unit_id": u, "city": names[u], "population_latest_year": vals[u][max(years)], "latest_year": max(years), "source_id": "S1"}
        for u in sorted(big, key=lambda u: -vals[u][max(years)])])
    print(len(big), "big cities;", len(pop_rows), "rows")


if __name__ == "__main__":
    main()
