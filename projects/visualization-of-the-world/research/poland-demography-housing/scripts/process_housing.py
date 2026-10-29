#!/usr/bin/env python3
"""Build the task-04 housing CSVs in data/processed/ from the committed raw extracts written by fetch_bdl_housing.py:
data/raw/bdl_housing_class_sums.csv (gmina-level series summed by place class), bdl_housing_national.csv and
bdl_housing_powiats_big.csv, plus population_by_class.csv (task 01) for per-1000 rates. Standard library only.

Outputs: housing_completions_by_class.csv, housing_floor_area_by_class.csv, housing_stock_by_class.csv,
housing_permits_by_class.csv, housing_starts_big_cities_vs_rest.csv, housing_completions_by_form_national.csv,
housing_national_crosscheck.csv. See README section "Task 04".
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from process_structure import write  # noqa: E402  (same CSV writer as the other tasks)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
CLASSES = ("big_cities", "small_cities", "villages")
YEARS = list(range(2000, 2026))

# BDL variable ids (verified against the live API, see README)
V_TOTAL, V_AREA = 748601, 748603                    # dwellings completed, total: number, useful floor area (P3824)
V_OWNUSE, V_OWNUSE_AREA = 748604, 748606            # ... private, from 2005 = own use of the investor (P3824)
V_INDIV = 430                                       # ... private = individual construction, 2000-2017 (P1735)
V_SF, V_MF = 748247, 748250                         # P3821: dwellings in single-family / multi-family new residential buildings
V_SF_AREA, V_MF_AREA = 748249, 748252               # P3821: useful floor area of those dwellings
V_STOCK, V_STOCK_AREA = 60811, 60813                # dwelling stock, useful floor area (P2166)
V_PERMIT_TOTAL, V_PERMIT_SF, V_PERMIT_2, V_PERMIT_3 = 1641096, 1641098, 1641099, 1641100   # P4216 dwellings in permits
V_START_TOTAL = (217340, 567218)                    # starts, total: P2956 (2005-2017), P3747 (2016-2019)
V_START_PRIVATE = (217389, 567219)                  # starts, private

SRC = {"completed": "S41", "forms": "S42", "bytype": "S43", "stock": "S44", "permits": "S45", "starts": "S46",
       "buildings": "S47", "census": "S48"}


def fmt(x, nd=2):
    return f"{x:.{nd}f}"


# ---------- readers ----------
def read_class_sums(path=RAW / "bdl_housing_class_sums.csv"):
    """{variable_id: {(class, year): (value, units_with_value)}}; class may also be 'all_whole_gminas_types_1_2_3'."""
    out = defaultdict(dict)
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[int(r["variable_id"])][(r["class"], int(r["year"]))] = (int(float(r["value"])), int(r["units_with_value"]))
    return out


# BDL attribute ids meaning "no number" (the value field is a placeholder 0). Same set as fetch_bdl_gminas.NO_VALUE_ATTRS.
NO_VALUE_ATTRS = {0, 4, 7, 14, 15, 17, 50, 91}


def read_national(path=RAW / "bdl_housing_national.csv"):
    """{variable_id: {year: value}} without placeholder zeros; plus {variable_id: label}."""
    vals, labels = defaultdict(dict), {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            vid = int(r["variable_id"])
            labels[vid] = " | ".join(x for x in (r["subject_id"], r["n1"], r["n2"], r["n3"], r["n4"]) if x)
            attr = int(r["attr_id"]) if r["attr_id"] != "" else 1
            if r["value"] != "" and attr not in NO_VALUE_ATTRS:
                v = float(r["value"])
                vals[vid][int(r["year"])] = int(v) if v == int(v) else v
    return vals, labels


def read_population(path=OUT / "population_by_class.csv"):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[(r["class"], int(r["year"]))] = int(r["population"])
    return out


def read_powiats(path=RAW / "bdl_housing_powiats_big.csv"):
    """{variable_id: {year: sum over the big-city powiats}}, {variable_id: {year: number of powiats with a value}}"""
    sums, counts = defaultdict(lambda: defaultdict(int)), defaultdict(lambda: defaultdict(int))
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            attr = int(r["attr_id"]) if r["attr_id"] != "" else 1
            if r["value"] != "" and attr not in NO_VALUE_ATTRS:
                sums[int(r["variable_id"])][int(r["year"])] += int(float(r["value"]))
                counts[int(r["variable_id"])][int(r["year"])] += 1
    return sums, counts


def cv(cs, vid, cls, year):
    """Class value of a variable or None when the class has no value that year."""
    e = cs.get(vid, {}).get((cls, year))
    return None if e is None else e[0]


# ---------- builders ----------
def completions_rows(cs, pop):
    rows = []

    def add(year, cls, typ, basis, dwellings, formula, sid, vtype="derived"):
        total = cv(cs, V_TOTAL, cls, year)
        rows.append({"year": year, "class": cls, "type": typ, "basis": basis, "dwellings": dwellings,
                     "share_of_total_pct": fmt(100 * dwellings / total) if total else "",
                     "per_1000_residents": fmt(1000 * dwellings / pop[(cls, year)]) if pop.get((cls, year)) else "",
                     "value_type": vtype, "formula": formula, "source_id": sid})

    for cls in CLASSES:
        for y in YEARS:
            tot = cv(cs, V_TOTAL, cls, y)
            if tot is None:
                continue
            add(y, cls, "total", "total", tot, "sum over gmina-level units of the class, var 748601", SRC["completed"])
            sf, mf = cv(cs, V_SF, cls, y), cv(cs, V_MF, cls, y)
            if sf is not None and mf is not None:
                add(y, cls, "house", "direct", sf, "sum of var 748247: dwellings in new single-family (one-dwelling) residential buildings",
                    SRC["bytype"])
                add(y, cls, "flat", "direct", mf, "sum of var 748250: dwellings in new multi-family residential buildings",
                    SRC["bytype"])
                add(y, cls, "other", "direct", tot - sf - mf,
                    "total - house - flat: dwellings in non-residential buildings, expansions and conversions", f"{SRC['completed']};{SRC['bytype']}")
            ind = cv(cs, V_INDIV, cls, y)
            if ind is not None:
                add(y, cls, "house_proxy_individual", "proxy", ind,
                    "sum of var 430: individual (private) construction, includes private dwellings for sale or rent",
                    SRC["forms"])
                add(y, cls, "flat_proxy_non_individual", "proxy", tot - ind,
                    "total - var 430 (developer, cooperative, municipal, TBS, company)", f"{SRC['completed']};{SRC['forms']}")
            own = cv(cs, V_OWNUSE, cls, y)
            if own is not None:
                add(y, cls, "house_proxy_own_use", "proxy", own,
                    "sum of var 748604: private dwellings for the own use of the investor (from 2005)", SRC["completed"])
                add(y, cls, "flat_proxy_not_own_use", "proxy", tot - own,
                    "total - var 748604 (sale or rent incl. private, cooperative, municipal, TBS, company)", SRC["completed"])
    return rows


def avg_area_rows(cs):
    rows = []
    specs = [("all_completed", V_AREA, V_TOTAL, SRC["completed"]),
             ("house_direct", V_SF_AREA, V_SF, SRC["bytype"]),
             ("flat_direct", V_MF_AREA, V_MF, SRC["bytype"])]
    for cls in CLASSES:
        for y in YEARS:
            for name, va, vn, sid in specs:
                a, n = cv(cs, va, cls, y), cv(cs, vn, cls, y)
                if a is None or n is None:
                    continue
                rows.append({"year": y, "class": cls, "measure": name, "dwellings": n, "useful_floor_area_m2": a,
                             "avg_m2_per_dwelling": fmt(a / n) if n else "", "value_type": "derived",
                             "formula": f"sum of area var {va} / sum of dwellings var {vn} over the class", "source_id": sid})
    return rows


def stock_rows(cs, pop):
    rows = []
    for cls in CLASSES:
        for y in YEARS:
            n, a = cv(cs, V_STOCK, cls, y), cv(cs, V_STOCK_AREA, cls, y)
            if n is None:
                continue
            p = pop.get((cls, y))
            rows.append({"year": y, "class": cls, "dwellings": n, "useful_floor_area_m2": "" if a is None else a,
                         "avg_m2_per_dwelling": fmt(a / n) if a and n else "",
                         "dwellings_per_1000_residents": fmt(1000 * n / p) if p else "",
                         "persons_per_dwelling": fmt(p / n) if p and n else "", "value_type": "derived",
                         "formula": "sum over gmina-level units of the class (vars 60811, 60813); per 1000 and persons per dwelling use "
                                    "31 Dec population of the class from population_by_class.csv (S1)",
                         "source_id": f"{SRC['stock']};S1"})
    return rows


def permits_rows(cs, pop, nat=None):
    """Gmina-level class values exist from 2018; the national total (class 'poland', reported) is added for 2009-2025 when `nat` is given."""
    rows = []
    for cls in CLASSES:
        for y in YEARS:
            tot, sf = cv(cs, V_PERMIT_TOTAL, cls, y), cv(cs, V_PERMIT_SF, cls, y)
            two, three = cv(cs, V_PERMIT_2, cls, y), cv(cs, V_PERMIT_3, cls, y)
            if None in (tot, sf, two, three):
                continue
            p = pop.get((cls, y))

            def add(typ, n, formula):
                rows.append({"year": y, "class": cls, "type": typ, "dwellings": n,
                             "per_1000_residents": fmt(1000 * n / p) if p else "", "value_type": "derived",
                             "formula": formula, "source_id": SRC["permits"]})

            add("total", tot, "sum of var 1641096: dwellings in permits and registrations with a construction project, all works")
            add("house", sf, "sum of var 1641098: dwellings in new single-family (one-dwelling) buildings")
            add("flat", two + three, "vars 1641099 + 1641100: dwellings in new two-dwelling and three-or-more-dwelling buildings")
            add("other", tot - sf - two - three, "total - house - flat: non-residential buildings, expansions, conversions")
    for y in YEARS if nat else []:
        v = [nat.get(k, {}).get(y) for k in (V_PERMIT_TOTAL, V_PERMIT_SF, V_PERMIT_2, V_PERMIT_3)]
        if None in v:
            continue
        for typ, n, formula in (("total", v[0], f"BDL national value, var {V_PERMIT_TOTAL}"), ("house", v[1], f"BDL national value, var {V_PERMIT_SF}"),
                                ("flat", v[2] + v[3], f"BDL national vars {V_PERMIT_2} + {V_PERMIT_3}"),
                                ("other", v[0] - v[1] - v[2] - v[3], "total - house - flat")):
            rows.append({"year": y, "class": "poland", "type": typ, "dwellings": n, "per_1000_residents": "",
                         "value_type": "reported" if typ in ("total", "house") else "derived", "formula": formula,
                         "source_id": SRC["permits"]})
    return rows


def starts_rows(nat, big_sums):
    """Construction starts: big cities (powiats that are exactly the 34 cities) vs the rest of Poland. Small cities and villages
    cannot be separated because BDL publishes starts only to powiat level."""
    rows = []
    for typ, ids in (("total", V_START_TOTAL), ("private", V_START_PRIVATE)):
        for y in range(2005, 2026):
            vid = ids[0] if y <= 2017 else ids[1]   # P2956 to 2017, P3747 from 2018
            if y not in nat.get(vid, {}) or y not in big_sums.get(vid, {}):
                continue
            poland, big = nat[vid][y], big_sums[vid][y]
            src = SRC["starts"]
            for area, n, formula in (("big_cities", big, f"sum of the 34 big-city powiats, var {vid}"),
                                     ("rest_of_poland", poland - big, f"Poland (var {vid}) - big_cities; small cities and villages together"),
                                     ("poland", poland, f"BDL national value, var {vid}")):
                rows.append({"year": y, "area": area, "type": typ, "dwellings": n,
                             "value_type": "reported" if area == "poland" else "derived", "formula": formula, "source_id": src})
    return rows


FORM_VARS = [  # (form, dwellings var, area var or None, table, note)
    ("total", 415, 417, "P1735", "to 2017"), ("total", 748601, 748603, "P3824", "1995-2025"),
    ("individual_incl_private_for_sale", 430, 432, "P1735", "to 2017; 'private' = individual construction, includes private dwellings for sale or rent"),
    ("own_use_of_investor", 748604, 748606, "P3824", "from 2005; private dwellings for the own use of the investor"),
    ("for_sale_or_rent_excl_private", 2250, None, "P1735", "to 2017; developers etc., private dwellings for sale are in 'individual'"),
    ("for_sale_or_rent_incl_private", 748610, None, "P3824", "from 2005; includes private dwellings for sale or rent"),
    ("cooperative", 418, None, "P1735", "to 2017"), ("cooperative", 748607, None, "P3824", "from 2005"),
    ("municipal", 424, None, "P1735", "to 2017"), ("municipal", 748616, None, "P3824", "from 2005"),
    ("social_rental_tbs", 1554, None, "P1735", "to 2017"), ("social_rental_tbs", 748619, None, "P3824", "from 2005"),
    ("company", 421, None, "P1735", "to 2017"), ("company", 748622, None, "P3824", "from 2005"),
]


def forms_rows(nat):
    rows = []
    for form, vd, va, table, note in FORM_VARS:
        for y in YEARS:
            if y not in nat.get(vd, {}):
                continue
            rows.append({"year": y, "form": form, "table": table, "dwellings": nat[vd][y],
                         "useful_floor_area_m2": nat.get(va, {}).get(y, ""), "value_type": "reported",
                         "variable_id": vd, "note": note, "source_id": SRC["forms"] if table == "P1735" else SRC["completed"]})
    return rows


def crosscheck_rows(cs, nat):
    """Sum of the three class values vs the BDL national value for every class-summed variable and year."""
    rows = []
    for vid in sorted(cs):
        for y in YEARS:
            parts = [cv(cs, vid, c, y) for c in CLASSES]
            if None in parts or y not in nat.get(vid, {}):
                continue
            n = nat[vid][y]
            rows.append({"variable_id": vid, "year": y, "national_bdl": n, "sum_of_three_classes": sum(parts),
                         "difference": sum(parts) - n, "value_type": "derived",
                         "formula": "sum of big_cities + small_cities + villages minus BDL national value", "source_id": "S41;S42;S43;S44;S45"})
    return rows


def main():
    cs = read_class_sums()
    nat, _labels = read_national()
    pop = read_population()
    big_sums, _ = read_powiats()
    write(OUT / "housing_completions_by_class.csv", completions_rows(cs, pop))
    write(OUT / "housing_floor_area_by_class.csv", avg_area_rows(cs))
    write(OUT / "housing_stock_by_class.csv", stock_rows(cs, pop))
    write(OUT / "housing_permits_by_class.csv", permits_rows(cs, pop, nat))
    write(OUT / "housing_starts_big_cities_vs_rest.csv", starts_rows(nat, big_sums))
    write(OUT / "housing_completions_by_form_national.csv", forms_rows(nat))
    write(OUT / "housing_national_crosscheck.csv", crosscheck_rows(cs, nat))
    print("done")


if __name__ == "__main__":
    main()
