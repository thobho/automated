#!/usr/bin/env python3
"""Build data/processed/europe_*.csv from data/raw/eurostat_europe.csv (see fetch_eurostat_europe.py).

europe_annual.csv   Eurostat annual indicators for PL, CZ, SK, HU, DE, RO, LT and EU27_2020, 2000 onwards.
europe_degurba.csv  Population by degree of urbanisation (cities / towns and suburbs / rural areas).
europe_summary.csv  First and latest value per indicator and country, change, and Poland's rank among the 7 countries.
Every row carries the Eurostat dataset code and a source_id registered in sources.csv. Missing values are not filled.
Standard library only.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "eurostat_europe.csv"
OUT = ROOT / "data" / "processed"

COUNTRIES = ["PL", "CZ", "SK", "HU", "DE", "RO", "LT"]
GEO_NAMES = {"PL": "Poland", "CZ": "Czechia", "SK": "Slovakia", "HU": "Hungary", "DE": "Germany",
             "RO": "Romania", "LT": "Lithuania", "EU27_2020": "EU-27"}

# raw series -> (indicator, sex, unit, dataset, source_id)
ANNUAL = {
    "population_1_jan": ("population_1_jan", "total", "persons", "demo_gind", "S29"),
    "population_change_total": ("population_change_total", "total", "persons", "demo_gind", "S29"),
    "natural_change": ("natural_change", "total", "persons", "demo_gind", "S29"),
    "net_migration_plus_adjustment": ("net_migration_plus_adjustment", "total", "persons", "demo_gind", "S29"),
    "net_migration_plus_adjustment_rate_per_1000": ("net_migration_plus_adjustment_rate", "total", "per 1000 inhabitants", "demo_gind", "S29"),
    "total_fertility_rate": ("total_fertility_rate", "total", "live births per woman", "demo_find", "S30"),
    "median_age_1_jan": ("median_age_1_jan", "total", "years", "demo_pjanind", "S31"),
    "old_age_dependency_65_per_15_64": ("old_age_dependency_65_per_15_64", "total", "persons 65+ per 100 aged 15-64", "demo_pjanind", "S31"),
    "life_expectancy_at_birth:T": ("life_expectancy_at_birth", "total", "years", "demo_mlexpec", "S32"),
    "life_expectancy_at_birth:M": ("life_expectancy_at_birth", "men", "years", "demo_mlexpec", "S32"),
    "life_expectancy_at_birth:F": ("life_expectancy_at_birth", "women", "years", "demo_mlexpec", "S32"),
}
# absolute counts depend on country size, so no rank is given for them
COUNT_INDICATORS = {"population_1_jan", "population_change_total", "natural_change", "net_migration_plus_adjustment"}
CLASSES = {"DEG1": "cities", "DEG2": "towns_and_suburbs", "DEG3": "rural_areas"}

ANNUAL_COLS = ["geo", "geo_name", "year", "indicator", "sex", "value", "unit", "eurostat_flag",
               "value_type", "formula", "dataset_code", "source_id"]
DEGURBA_COLS = ["geo", "geo_name", "year", "measure", "degurba_class", "value", "unit", "eurostat_flag",
                "value_type", "formula", "dataset_code", "source_id"]
SUMMARY_COLS = ["indicator", "sex", "geo", "geo_name", "first_year", "first_value", "latest_year", "latest_value",
                "change_abs", "change_pct", "poland_rank_latest_of_7", "unit", "value_type", "formula",
                "dataset_code", "source_id"]


def num(s):
    """'' -> None, otherwise float."""
    return None if s is None or str(s).strip() == "" else float(s)


def fmt(v, nd=2):
    """Number to text without trailing zeros; None -> ''."""
    if v is None:
        return ""
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def load_raw(path=RAW):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_annual(raw):
    rows = []
    jan = {}
    for r in raw:
        spec = ANNUAL.get(r["series"])
        if not spec:
            continue
        ind, sex, unit, ds, sid = spec
        v = num(r["value"])
        if v is None:
            continue
        rows.append({"geo": r["geo"], "geo_name": GEO_NAMES[r["geo"]], "year": r["period"], "indicator": ind,
                     "sex": sex, "value": r["value"], "unit": unit, "eurostat_flag": r["eurostat_flag"],
                     "value_type": "reported", "formula": "", "dataset_code": ds, "source_id": sid})
        if ind == "population_1_jan":
            jan[(r["geo"], int(r["period"]))] = v
    for (geo, year), v in sorted(jan.items()):
        base = jan.get((geo, 2000))
        if base:
            rows.append({"geo": geo, "geo_name": GEO_NAMES[geo], "year": str(year),
                         "indicator": "population_index_2000_eq_100", "sex": "total",
                         "value": fmt(v / base * 100, 2), "unit": "index, 1 Jan 2000 = 100", "eurostat_flag": "",
                         "value_type": "derived", "formula": "population_1_jan(year) / population_1_jan(2000) * 100",
                         "dataset_code": "demo_gind", "source_id": "S29"})
    rows.sort(key=lambda r: (r["indicator"], r["sex"], GEO_ORDER[r["geo"]], int(r["year"])))
    return rows


GEO_ORDER = {g: i for i, g in enumerate(COUNTRIES + ["EU27_2020"])}


def build_degurba(raw):
    rows = []
    lfs = {}      # (geo, year) -> {class or TOTAL: value}
    cens = {}
    for r in raw:
        name, _, cls = r["series"].partition(":")
        v = num(r["value"])
        if v is None:
            continue
        key = (r["geo"], r["period"])
        if name == "share_of_population_by_degurba_pct" and cls in CLASSES:
            rows.append(_dg(r, "share_of_population_all_ages", CLASSES[cls], r["value"], "% of population",
                            "reported", "", "ilc_lvho01", "S33"))
        elif name == "population_15plus_by_degurba_thousand" and cls in (*CLASSES, "TOTAL"):
            lfs.setdefault(key, {})[cls] = (r["value"], r["eurostat_flag"])
        elif name == "census_2021_population_by_degurba" and cls in (*CLASSES, "TOTAL"):
            cens.setdefault(key, {})[cls] = (r["value"], r["eurostat_flag"])
    for store, meas_n, meas_s, ds, sid, unit_n, scale in (
            (lfs, "population_aged_15plus", "share_of_population_aged_15plus", "lfsa_pgauws", "S34", "thousand persons", 1),
            (cens, "census_2021_population", "census_2021_share_of_population", "cens_21urb01", "S35", "persons", 1)):
        for (geo, year), d in sorted(store.items()):
            fake = {"geo": geo, "period": year}
            for cls, (val, flag) in d.items():
                if cls == "TOTAL":
                    rows.append(_dg(dict(fake, eurostat_flag=flag), meas_n, "total", val, unit_n, "reported", "", ds, sid))
                else:
                    rows.append(_dg(dict(fake, eurostat_flag=flag), meas_n, CLASSES[cls], val, unit_n, "reported", "", ds, sid))
            if "TOTAL" in d and all(c in d for c in CLASSES):
                total = float(d["TOTAL"][0])
                for c in CLASSES:
                    sh = float(d[c][0]) / total * 100
                    rows.append(_dg(fake | {"eurostat_flag": d[c][1]}, meas_s, CLASSES[c], fmt(sh, 2), "% of population",
                                    "derived", f"{meas_n}(class) / {meas_n}(total) * 100", ds, sid))
    order = {"share_of_population_all_ages": 0, "population_aged_15plus": 1, "share_of_population_aged_15plus": 2,
             "census_2021_population": 3, "census_2021_share_of_population": 4}
    cls_order = {"total": 0, "cities": 1, "towns_and_suburbs": 2, "rural_areas": 3}
    rows.sort(key=lambda r: (order[r["measure"]], GEO_ORDER[r["geo"]], int(r["year"]), cls_order[r["degurba_class"]]))
    return rows


def _dg(r, measure, cls, value, unit, vtype, formula, ds, sid):
    return {"geo": r["geo"], "geo_name": GEO_NAMES[r["geo"]], "year": r["period"], "measure": measure,
            "degurba_class": cls, "value": value, "unit": unit, "eurostat_flag": r.get("eurostat_flag", ""),
            "value_type": vtype, "formula": formula, "dataset_code": ds, "source_id": sid}


def rank_desc(values, key):
    """1-based rank of `key` in dict values (highest = 1, ties share the best rank); None if key missing."""
    if values.get(key) is None:
        return None
    return 1 + sum(1 for v in values.values() if v is not None and v > values[key])


def build_summary(annual):
    series = {}
    meta = {}
    for r in annual:
        if r["value_type"] != "reported":
            continue
        k = (r["indicator"], r["sex"])
        series.setdefault(k, {}).setdefault(r["geo"], {})[int(r["year"])] = float(r["value"])
        meta[k] = (r["unit"], r["dataset_code"], r["source_id"])
    out = []
    for (ind, sex), by_geo in sorted(series.items()):
        latest_vals = {g: by_geo[g][max(by_geo[g])] if g in by_geo else None for g in COUNTRIES}
        latest_years = {g: max(by_geo[g]) for g in by_geo}
        for geo in COUNTRIES + ["EU27_2020"]:
            d = by_geo.get(geo)
            if not d:
                continue
            y0, y1 = min(d), max(d)
            v0, v1 = d[y0], d[y1]
            is_level = ind in ("population_1_jan", "life_expectancy_at_birth", "median_age_1_jan",
                               "old_age_dependency_65_per_15_64", "total_fertility_rate")
            same_year = len({latest_years.get(g) for g in COUNTRIES}) == 1
            rank = rank_desc(latest_vals, "PL") if (geo == "PL" and same_year and ind not in COUNT_INDICATORS) else None
            unit, ds, sid = meta[(ind, sex)]
            out.append({"indicator": ind, "sex": sex, "geo": geo, "geo_name": GEO_NAMES[geo], "first_year": y0,
                        "first_value": fmt(v0, 3), "latest_year": y1, "latest_value": fmt(v1, 3),
                        "change_abs": fmt(v1 - v0, 3),
                        "change_pct": fmt((v1 - v0) / v0 * 100, 2) if is_level and v0 else "",
                        "poland_rank_latest_of_7": rank if rank is not None else "", "unit": unit,
                        "value_type": "derived",
                        "formula": "change_abs = latest - first; change_pct = (latest - first) / first * 100 (levels only); "
                                   "rank = position of Poland among PL, CZ, SK, HU, DE, RO, LT in the latest year (1 = highest)",
                        "dataset_code": ds, "source_id": sid})
    return out


def write(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def main():
    raw = load_raw()
    annual = build_annual(raw)
    write(OUT / "europe_annual.csv", ANNUAL_COLS, annual)
    write(OUT / "europe_degurba.csv", DEGURBA_COLS, build_degurba(raw))
    write(OUT / "europe_summary.csv", SUMMARY_COLS, build_summary(annual))
    print("annual", len(annual), "rows")


if __name__ == "__main__":
    main()
