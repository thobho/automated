#!/usr/bin/env python3
"""Fetch the BDL housing series for task 04 (see README section "Task 04").

Writes three small, committed extracts under data/raw/:
  bdl_housing_national.csv       national (unit 000000000000) series, one row per variable and year, with BDL names + attribute id
  bdl_housing_powiats_big.csv    powiat-level (unit-level 5) series for the powiats that are exactly the 34 big cities
                                 (construction starts exist only at powiat level)
  bdl_housing_class_sums.csv     gmina-level (unit-level 6) series summed by place class, same class assignment as task 01/02
The full gmina-level responses (about 42 requests of 100 units per variable) are cached in the git-ignored data/raw/cache/.
Anonymous BDL limit: 100 requests / 15 min and 1000 / 12 h; the client in bdl.py waits automatically. A cold run needs about 650 requests.
Standard library only.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bdl  # noqa: E402
import fetch_bdl_gminas as fg  # noqa: E402
import process_structure as ps  # noqa: E402

RAW = bdl.ROOT / "data" / "raw"
OUT = bdl.ROOT / "data" / "processed"
NATIONAL = "000000000000"
YEARS = list(range(2000, 2026))

# variable id -> short role (documentation only; names come live from the API)
NATIONAL_VARS = [
    # dwellings completed: totals and forms of construction (P1735 to 2017, P3824 1995-2025)
    415, 417, 430, 432, 411017, 411018, 2250, 418, 421, 424, 1554,
    748601, 748603, 748604, 748606, 748607, 748610, 748616, 748619, 748622,
    # dwellings completed by building type (P3821, "year" = January-December), 2009-2025
    748241, 748243, 748244, 748246, 748247, 748249, 748250, 748252, 748253, 748255, 748256, 748259,
    # new buildings completed by number of dwellings (P2479 to 2017, P3769 2017): cross-check of the building-type split
    64016, 377354, 377356, 377350, 377348, 632895, 632897, 632898,
    # housing stock (P2166, P2430) and census 2021 (P4383)
    60811, 60813, 60807, 60812, 60572, 60573, 410600, 1723485, 1723486,
    # permits (P2956 2005-2017, P3747 2016-2019, P4216 2009-2025) and construction starts (P2956, P3747)
    217329, 217377, 567225, 567226, 217340, 217389, 567218, 567219,
    1641096, 1641098, 1641099, 1641100,
]
# gmina-level variables summed by class: id -> years that matter (all fetched for 2000-2025)
GMINA_VARS = [
    748601,  # dwellings completed, total (P3824)
    748603,  # useful floor area of dwellings completed, total
    748604,  # ... private (own use of the investor from 2005; 0 + attribute x before 2005)
    430,     # ... private = individual construction, 2000-2017 (P1735)
    748247, 748250,    # P3821: dwellings in single-family / multi-family new residential buildings
    748249, 748252,    # P3821: useful floor area of dwellings in single-family / multi-family buildings
    60811, 60813,      # stock: dwellings, useful floor area (P2166)
    1641096, 1641098, 1641099, 1641100,   # P4216: dwellings in permits: total, single-family, two-dwelling, three+ dwelling
]
POWIAT_VARS = [217340, 567218, 217389, 567219]   # construction starts: total, private; P2956 and P3747


def fetch_national():
    rows = []
    for i in range(0, len(NATIONAL_VARS), 20):
        chunk = NATIONAL_VARS[i:i + 20]
        params = [("var-id", v) for v in chunk] + [("year", y) for y in YEARS]
        by_id = {r["id"]: r for r in bdl.paged(f"/data/by-unit/{NATIONAL}", params)}
        for vid in chunk:
            meta = bdl.get(f"/variables/{vid}")
            for val in by_id.get(vid, {}).get("values", []):
                rows.append([meta["subjectId"], vid, meta.get("n1") or "", meta.get("n2") or "", meta.get("n3") or "",
                             meta.get("n4") or "", meta.get("measureUnitName") or "", int(val["year"]),
                             "" if val.get("val") is None else val["val"], val.get("attrId", "")])
    rows.sort(key=lambda r: (r[1], r[7]))
    with open(RAW / "bdl_housing_national.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["subject_id", "variable_id", "n1", "n2", "n3", "n4", "unit", "year", "value", "attr_id"])
        w.writerows(rows)
    print("national rows", len(rows), flush=True)


def powiat_id(city_unit_id):
    """Powiat unit of a city with powiat rights: the first 9 characters of the gmina id + '000'."""
    return city_unit_id[:9] + "000"


def fetch_powiats(big_ids):
    want = {powiat_id(u): u for u in big_ids}
    rows = []
    for vid in POWIAT_VARS:
        params = [("unit-level", 5)] + [("year", y) for y in YEARS]
        for r in bdl.paged(f"/data/by-variable/{vid}", params):
            if r["id"] in want:
                for v in r["values"]:
                    rows.append([vid, r["id"], want[r["id"]], r["name"], int(v["year"]),
                                 "" if v.get("val") is None else v["val"], v.get("attrId", "")])
    rows.sort(key=lambda r: (r[0], r[1], r[4]))
    with open(RAW / "bdl_housing_powiats_big.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["variable_id", "powiat_unit_id", "city_unit_id", "powiat_name", "year", "value", "attr_id"])
        w.writerows(rows)
    print("powiat rows", len(rows), flush=True)


def class_sum_rows(vid, series, big_ids):
    """Sum one gmina-level variable by place class (urban/rural parts instead of whole urban-rural gminas) and also over
    whole gminas (types 1-3) as the control total. Returns rows [variable_id, year, class, value, units_with_value]."""
    s_parts, c_parts = ps.class_sums(series, big_ids, YEARS, True)
    s_whole, c_whole = ps.class_sums(series, big_ids, YEARS, False)
    whole_total = defaultdict(int)
    whole_units = defaultdict(int)
    for cls in s_whole:
        if cls == "urban_rural_gminas_whole" or cls in ("big_cities", "small_cities", "villages"):
            for y, v in s_whole[cls].items():
                whole_total[y] += v
                whole_units[y] += c_whole[cls][y]
    rows = []
    for y in YEARS:
        for cls in ("big_cities", "small_cities", "villages"):
            if c_parts[cls].get(y):
                rows.append([vid, y, cls, s_parts[cls][y], c_parts[cls][y]])
        if whole_units.get(y):
            rows.append([vid, y, "all_whole_gminas_types_1_2_3", whole_total[y], whole_units[y]])
    return rows


def fetch_gmina_class_sums(big_ids):
    rows = []
    for vid in GMINA_VARS:
        series = ps.merged_series(fg.load_gmina_var(vid, YEARS, skip_missing=True))
        rows += class_sum_rows(vid, series, big_ids)
        print("gmina var", vid, len(series), "units", flush=True)
    with open(RAW / "bdl_housing_class_sums.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["variable_id", "year", "class", "value", "units_with_value"])
        w.writerows(rows)
    print("class-sum rows", len(rows), flush=True)


def main(parts=("national", "powiats", "gminas")):
    big_ids = {c["unit_id"] for c in csv.DictReader(open(OUT / "big_city_list.csv", encoding="utf-8"))}
    if "national" in parts:
        fetch_national()
    if "powiats" in parts:
        fetch_powiats(big_ids)
    if "gminas" in parts:
        fetch_gmina_class_sums(big_ids)


if __name__ == "__main__":
    main(tuple(sys.argv[1:]) or ("national", "powiats", "gminas"))
