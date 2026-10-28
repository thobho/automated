#!/usr/bin/env python3
"""Build the demographic-structure CSVs in data/processed/ from data/raw/bdl_structure_national.csv,
data/raw/eurostat_poland.csv and the cached gmina-level BDL series (fetch_bdl_gminas.py).
Standard library only. See README section "02 - structure" for method and caveats.

Outputs: age_sex_pyramid.csv, age_structure_indicators.csv, vital_rates.csv, migration_national.csv,
ukraine_inflow.csv, migration_by_place_class.csv, households.csv, suburban_belt_gminas.csv,
suburban_belt_summary.csv, small_towns_change.csv
"""
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
GEO = ROOT.parent / "poland-geography" / "data" / "gminas.geojson"
YEARS = list(range(2000, 2026))
BELT_RADIUS_KM = 25.0
N_CORES = 8
SMALL_TOWN_MIN_POP_2000 = 2000  # ignore tiny towns when ranking percentage losses


# ---------- generic helpers ----------
def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def num(s):
    if s in ("", None):
        return None
    f = float(s)
    return int(f) if f == int(f) and "." not in str(s) else f


def read_bdl_national(path=RAW / "bdl_structure_national.csv"):
    """{(variable_id): {"subject":..., "n1","n2","n3", "vals": {year: number or None}}}"""
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = out.setdefault(int(r["variable_id"]), {"subject": r["subject_id"], "n1": r["n1"], "n2": r["n2"],
                                                       "n3": r["n3"], "vals": {}})
            v["vals"][int(r["year"])] = num(r["value"])
    return out


def read_eurostat(path=RAW / "eurostat_poland.csv"):
    out = defaultdict(dict)
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["series"]][r["period"]] = (num(r["value"]), r["eurostat_flag"])
    return out


def row(**kw):
    return kw


def haversine_km(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(a))


def ring_centroid(ring):
    """Area-weighted centroid (lon, lat) of a closed ring; falls back to vertex mean for degenerate rings."""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        cr = x0 * y1 - x1 * y0
        a += cr
        cx += (x0 + x1) * cr
        cy += (y0 + y1) * cr
    if abs(a) < 1e-12:
        return sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)
    return cx / (3 * a), cy / (3 * a)


def geometry_centroid(geom):
    """Centroid of a Polygon/MultiPolygon: area-weighted over outer rings."""
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    tot = sx = sy = 0.0
    for poly in polys:
        ring = poly[0]
        area = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:]))) / 2
        cx, cy = ring_centroid(ring)
        tot += area
        sx += cx * area
        sy += cy * area
    return (sx / tot, sy / tot) if tot else ring_centroid(polys[0][0])


def unit_teryt(unit_id):
    """BDL 12-digit unit id -> 7-digit TERYT (voivodeship 2 + powiat 2 + gmina 2 + type 1)."""
    return unit_id[2:4] + unit_id[-5:]


def pct_change(a, b):
    return None if a in (None, 0) or b is None else 100.0 * (b - a) / a


def fmt(x, nd=2):
    return "" if x is None else f"{x:.{nd}f}"


# ---------- themes from national series ----------
def build_pyramid(bdl):
    rows = []
    for vid, v in bdl.items():
        if v["subject"] != "P2137" or v["n1"] in ("total", "0-14") or v["n2"] not in ("males", "females"):
            continue
        for y, val in sorted(v["vals"].items()):
            if val is None:
                continue
            rows.append(row(year=y, age_group=v["n1"].replace(" and more", "+"), sex="male" if v["n2"] == "males" else "female",
                            population=val, level="national", value_type="reported", formula="", source_id="S8"))
    order = {g: i for i, g in enumerate(["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49",
                                         "50-54", "55-59", "60-64", "65-69", "70+", "70-74", "75-79", "80-84", "85+"])}
    rows.sort(key=lambda r: (r["year"], order[r["age_group"]], r["sex"]))
    return rows


def build_age_indicators(bdl, eu):
    rows = []

    def add(year, indicator, area, value, unit, sid, vtype="reported", formula="", note=""):
        if value is None:
            return
        rows.append(row(year=year, indicator=indicator, area=area, value=value, unit=unit, value_type=vtype,
                        formula=formula, note=note, source_id=sid))
    for y, val in bdl[746289]["vals"].items():
        add(y, "median_age", "national", val, "years", "S11", note="31 Dec")
    for vid, area in ((746283, "urban"), (746286, "rural")):
        for y, val in bdl[vid]["vals"].items():
            add(y, "median_age", area, val, "years", "S11", note="31 Dec")
    for p, (val, flag) in sorted(eu["median_age"].items()):
        add(int(p), "median_age", "national", val, "years", "S19", note="1 Jan of year; Eurostat flag " + (flag or "none"))
    for y, val in bdl[634067]["vals"].items():
        add(y, "old_age_dependency_65plus_per_100_working_age", "national", val, "persons per 100", "S9", note="GUS working age: women 15-59, men 15-64")
    for y, val in bdl[60563]["vals"].items():
        add(y, "total_dependency_per_100_working_age", "national", val, "persons per 100", "S9", note="GUS working age: women 15-59, men 15-64")
    for y, val in bdl[634989]["vals"].items():
        add(y, "share_aged_65plus", "national", val, "percent", "S9")
    for p, (val, flag) in sorted(eu["old_age_dependency_65_per_15_64"].items()):
        add(int(p), "old_age_dependency_65plus_per_100_aged_15_64", "national", val, "persons per 100", "S19", note="1 Jan; Eurostat flag " + (flag or "none"))
    for p, (val, flag) in sorted(eu["total_dependency_per_15_64"].items()):
        add(int(p), "total_dependency_0_14_and_65plus_per_100_aged_15_64", "national", val, "persons per 100", "S19", note="1 Jan; Eurostat flag " + (flag or "none"))
    # urban/rural dependency ratios from BDL P3361 (2012+)
    ids = {"urban": {"pre": 399973, "work": 399974, "post": 399975}, "rural": {"pre": 399967, "work": 399968, "post": 399969}}
    for area, m in ids.items():
        for y in sorted(bdl[m["work"]]["vals"]):
            pre, work, post = (bdl[m[k]]["vals"].get(y) for k in ("pre", "work", "post"))
            if None in (pre, work, post) or not work:
                continue
            add(y, "total_dependency_per_100_working_age", area, round(100 * (pre + post) / work, 1), "persons per 100", "S10", "derived",
                f"(pre-working + post-working) / working age x 100; inputs BDL {m['pre']},{m['work']},{m['post']}")
            add(y, "old_age_dependency_post_working_per_100_working_age", area, round(100 * post / work, 1), "persons per 100", "S10", "derived",
                f"post-working / working age x 100; inputs BDL {m['work']},{m['post']}; post-working = women 60+, men 65+, not 65+")
    rows.sort(key=lambda r: (r["indicator"], r["area"], r["source_id"], r["year"]))
    return rows


def build_vital(bdl, eu):
    rows = []

    def add(year, indicator, area, sex, value, unit, sid, vtype="reported", formula=""):
        if value is None:
            return
        rows.append(row(year=year, indicator=indicator, area=area, sex=sex, value=value, unit=unit, value_type=vtype,
                        formula=formula, source_id=sid))
    m = {1616435: ("live_births", "national"), 1616436: ("live_births", "urban"), 1616437: ("live_births", "rural"),
         1616441: ("deaths", "national"), 1616442: ("deaths", "urban"), 1616443: ("deaths", "rural"),
         1616453: ("natural_increase", "national"), 1616454: ("natural_increase", "urban"), 1616455: ("natural_increase", "rural"),
         1616447: ("infant_deaths", "national"), 1616448: ("infant_deaths", "urban"), 1616449: ("infant_deaths", "rural")}
    for vid, (ind, area) in m.items():
        for y, val in bdl[vid]["vals"].items():
            add(y, ind, area, "total", val, "persons", "S12")
    per1000 = {1616438: ("live_births_per_1000", "national"), 1616439: ("live_births_per_1000", "urban"), 1616440: ("live_births_per_1000", "rural"),
               1616444: ("deaths_per_1000", "national"), 1616445: ("deaths_per_1000", "urban"), 1616446: ("deaths_per_1000", "rural"),
               1616456: ("natural_increase_per_1000", "national"), 1616457: ("natural_increase_per_1000", "urban"), 1616458: ("natural_increase_per_1000", "rural"),
               1616450: ("infant_deaths_per_1000_live_births", "national"), 1616451: ("infant_deaths_per_1000_live_births", "urban"),
               1616452: ("infant_deaths_per_1000_live_births", "rural")}
    for vid, (ind, area) in per1000.items():
        for y, val in bdl[vid]["vals"].items():
            add(y, ind, area, "total", val, "per 1000" if "infant" not in ind else "per 1000 live births", "S12")
    for y, val in bdl[59049]["vals"].items():
        add(y, "total_fertility_rate", "national", "female", val, "children per woman", "S13")
    for y, val in bdl[59048]["vals"].items():
        add(y, "gross_reproduction_rate", "national", "female", val, "daughters per woman", "S13")
    for p, (val, flag) in sorted(eu["total_fertility_rate"].items()):
        add(int(p), "total_fertility_rate", "national", "female", val, "children per woman", "S21")
    le = {101554: ("national", "male"), 101555: ("national", "female"), 101551: ("urban", "male"), 101552: ("urban", "female"),
          101548: ("rural", "male"), 101549: ("rural", "female")}
    for vid, (area, sex) in le.items():
        for y, val in bdl[vid]["vals"].items():
            add(y, "life_expectancy_at_birth", area, sex, val, "years", "S14")
    rows.sort(key=lambda r: (r["indicator"], r["area"], r["sex"], r["source_id"], r["year"]))
    return rows


ZERO_2015 = {80122, 80124, 1365224, 1365229, 1365234, 80108}  # BDL reports 0 for 2015 although 2014 and 2016 are in the tens of thousands


def build_migration_national(bdl, eu):
    rows = []

    def add(year, indicator, value, unit, sid, note=""):
        rows.append(row(year=year, indicator=indicator, area="national", value="" if value is None else value, unit=unit,
                        note=note, source_id=sid))
    # National net internal migration (80125) is 0 in every year by construction (every move is counted once as a
    # departure and once as an arrival), so it is not output; class-level internal flows are in migration_by_place_class.csv.
    m = {1365224: "permanent_registrations_total", 80121: "permanent_registrations_internal", 80122: "permanent_registrations_from_abroad",
         1365229: "permanent_deregistrations_total", 80123: "permanent_deregistrations_internal", 80124: "permanent_deregistrations_to_abroad",
         80108: "net_international_migration"}
    for vid, ind in m.items():
        for y, val in bdl[vid]["vals"].items():
            if y == 2015 and vid in ZERO_2015:
                add(y, ind, None, "persons", "S15", "MISSING: BDL reports 0 for 2015 (implausible; 2014 and 2016 are far from 0); not used")
            else:
                add(y, ind, val, "persons", "S15", "registered changes of permanent residence only")
    for p, (val, flag) in sorted(eu["immigration_all_citizenships"].items()):
        add(int(p), "eurostat_immigration_all_citizenships", val, "persons", "S22", "level break 2008/2009; flag " + (flag or "none"))
    for p, (val, flag) in sorted(eu["emigration_all_citizenships"].items()):
        add(int(p), "eurostat_emigration_all_citizenships", val, "persons", "S22", "level break 2008/2009; flag " + (flag or "none"))
    for p, (val, flag) in sorted(eu["net_migration_plus_adjustment"].items()):
        add(int(p), "eurostat_net_migration_plus_statistical_adjustment", val, "persons", "S20", "residual: population change minus natural change; flag " + (flag or "none"))
    rows.sort(key=lambda r: (r["indicator"], r["source_id"], r["year"]))
    return rows


def build_ukraine(eu):
    rows = []
    for p, (val, flag) in sorted(eu["temporary_protection_ukrainian_citizens_end_of_month"].items()):
        rows.append(row(period=p, indicator="temporary_protection_beneficiaries_ukrainian_citizens", area="national", value=val,
                        unit="persons (stock at end of month)", note="separate from the GUS series; Eurostat flag " + (flag or "none"), source_id="S23"))
    return rows


# ---------- gmina-level themes ----------
def gmina_class(unit_id, big_ids):
    """Place class of a gmina-level BDL unit (type digit = last char)."""
    t = unit_id[-1]
    if unit_id in big_ids:
        return "big_cities"
    return {"1": "small_cities", "4": "small_cities", "2": "villages", "5": "villages", "3": "urban_rural_gminas_whole"}.get(t)


def class_sums(series_by_unit, big_ids, years, use_parts):
    """Sum a gmina series by place class. use_parts: sum urban/rural parts (types 4,5) instead of whole urban-rural gminas (3)."""
    sums = defaultdict(lambda: defaultdict(int))
    counts = defaultdict(lambda: defaultdict(int))
    for uid, (name, vals) in series_by_unit.items():
        t = uid[-1]
        if use_parts and t == "3":
            continue
        if not use_parts and t in "45":
            continue
        cls = gmina_class(uid, big_ids)
        if cls is None:
            continue
        for y in years:
            v = vals.get(y)
            if v is not None:
                sums[cls][y] += v
                counts[cls][y] += 1
    return sums, counts


MERGE = {  # same city split over several BDL unit ids (see process_population.py)
    "071412831001": "071412865011",
    "030210363011": "030210365011",
    "030210321091": "030210365011",
}


def merged_series(raw):
    """Apply MERGE and drop pre-2002 Warsaw districts. raw: {unit_id: (name, {year: value})}."""
    out = {}
    for uid, (name, vals) in raw.items():
        if name.endswith(" to 2001") and not name.startswith("Capital city"):
            continue
        key = MERGE.get(uid, uid)
        if key in out:
            merged = dict(out[key][1])
            for y, v in vals.items():
                if v is not None:
                    merged.setdefault(y, v)
            out[key] = (out[key][0] if key == uid or key not in MERGE.values() else name, merged)
        else:
            out[key] = (name, dict(vals))
    return out


def whole_gminas(pop):
    """Merge whole-gmina series (types 1-3) by 6-digit TERYT, so a gmina that changed type (rural -> urban-rural after
    a village got town rights) keeps one continuous series: its territory is unchanged. Returns
    {teryt6: {"name", "uid", "vals"}}; uid is the unit that carries the latest value."""
    out = {}
    for u, (name, vals) in sorted(pop.items()):
        if u[-1] not in "123":
            continue
        k = unit_teryt(u)[:6]
        e = out.setdefault(k, {"name": name, "uid": u, "vals": {}})
        for y, v in vals.items():
            if v is not None:
                e["vals"][y] = v
        if vals.get(2025) is not None:
            e["uid"], e["name"] = u, name
    return out


def select_belt(whole, exclude6, city_pts, centroids, radius=BELT_RADIUS_KM):
    """Whole gminas (not in `exclude6`, the big cities) whose centroid lies within `radius` km of a core city point.
    centroids: {teryt6: (lon, lat)}. Returns [(teryt6, core_unit_id, distance_km)], each gmina assigned to its nearest core."""
    out = []
    for k, (lon, lat) in centroids.items():
        if k not in whole or k in exclude6:
            continue
        d, core = min((haversine_km(lon, lat, *pt), c) for c, pt in city_pts.items())
        if d <= radius:
            out.append((k, core, d))
    return out


def read_big(path=OUT / "big_city_list.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return [(r["unit_id"], r["city"], int(r["population_latest_year"])) for r in csv.DictReader(f)]


def read_city_points(path=ROOT.parent / "poland-geography" / "data" / "cities.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return {r["bdl_unit_id"]: (float(r["lon"]), float(r["lat"])) for r in csv.DictReader(f) if r["lon"]}


def read_centroids(path=GEO):
    d = json.load(open(path, encoding="utf-8"))
    return {f["properties"]["teryt"][:6]: geometry_centroid(f["geometry"]) for f in d["features"]}


SNAP = [2000, 2010, 2020, 2025]


def snap_cols(vals):
    return {f"pop_{y}": ("" if vals.get(y) is None else vals[y]) for y in SNAP}


def belt_rows(pop, big, city_pts, centroids, n_cores=N_CORES, radius=BELT_RADIUS_KM):
    cores = big[:n_cores]  # big_city_list.csv is sorted by population, largest first
    core_name = {c[0]: c[1] for c in cores}
    whole = whole_gminas(pop)
    exclude6 = {unit_teryt(c[0])[:6] for c in big}
    belt = select_belt(whole, exclude6, {c: city_pts[c] for c in core_name}, centroids, radius)
    rows = []
    for k, core, d in belt:
        g = whole[k]
        vals = g["vals"]
        p0, p10, p25 = vals.get(2000), vals.get(2010), vals.get(2025)
        r = {"core_city": core_name[core], "teryt": unit_teryt(g["uid"]), "bdl_unit_id": g["uid"], "gmina": g["name"],
             "gmina_type": {"1": "urban", "2": "rural", "3": "urban-rural"}[g["uid"][-1]], "distance_to_core_km": fmt(d, 1)}
        r.update(snap_cols(vals))
        r["change_2000_2025_abs"] = "" if p0 is None or p25 is None else p25 - p0
        r["change_2000_2025_pct"] = fmt(pct_change(p0, p25))
        r["change_2010_2025_pct"] = fmt(pct_change(p10, p25))
        r["note"] = "" if p0 is not None and p25 is not None else "missing 2000 or 2025 value (unit created or re-coded after 2000); no change computed"
        r["value_type"] = "population reported; changes derived"
        r["formula"] = "change_pct = (pop_end - pop_start) / pop_start x 100; series merged across type changes by 6-digit TERYT"
        r["source_id"] = "S1;S26"
        rows.append(r)
    rows.sort(key=lambda r: (-float(r["change_2000_2025_pct"]) if r["change_2000_2025_pct"] else 1e9))
    rank = 0
    for r in rows:
        if r["change_2000_2025_pct"]:
            rank += 1
            r["rank_growth_2000_2025"] = rank
        else:
            r["rank_growth_2000_2025"] = ""
    return rows


def belt_summary(rows, pop, big, n_cores=N_CORES):
    out = []
    for uid, city, _ in big[:n_cores]:
        vals = pop[uid][1]
        mine = [r for r in rows if r["core_city"] == city and r["change_2000_2025_pct"]]
        b0 = sum(r["pop_2000"] for r in mine)
        b25 = sum(r["pop_2025"] for r in mine)
        c0, c25 = vals.get(2000), vals.get(2025)
        out.append({"core_city": city, "core_pop_2000": c0, "core_pop_2025": c25,
                    "core_change_pct": fmt(pct_change(c0, c25)),
                    "belt_gminas_with_data": len(mine), "belt_pop_2000": b0, "belt_pop_2025": b25,
                    "belt_change_pct": fmt(pct_change(b0, b25)),
                    "belt_gminas_growing_over_20pct": sum(1 for r in mine if float(r["change_2000_2025_pct"]) > 20),
                    "belt_gminas_shrinking": sum(1 for r in mine if float(r["change_2000_2025_pct"]) < 0),
                    "radius_km": BELT_RADIUS_KM, "value_type": "derived",
                    "formula": "sums over belt gminas with both 2000 and 2025 values; belt = gmina centroid within radius of the core city point",
                    "source_id": "S1;S26"})
    return out


def small_town_rows(pop, big):
    big_all = {c[0] for c in big}
    rows = []
    for uid, (name, vals) in pop.items():
        if uid[-1] not in "14" or uid in big_all:
            continue
        p25 = vals.get(2025)
        if p25 is None:
            continue  # town no longer exists / not in 2025 list
        if p25 >= 100_000:
            continue
        p0 = vals.get(2000)
        r = {"bdl_unit_id": uid, "teryt": unit_teryt(uid), "town": name.replace(" - urban area", ""),
             "unit_type": "urban gmina" if uid[-1] == "1" else "town part of urban-rural gmina"}
        r.update(snap_cols(vals))
        r["change_2000_2025_abs"] = "" if p0 is None else p25 - p0
        r["change_2000_2025_pct"] = fmt(pct_change(p0, p25))
        r["note"] = "" if p0 is not None else "no 2000 value in BDL (new unit or new town rights); excluded from ranking"
        r["value_type"] = "population reported; changes derived"
        r["formula"] = "change_pct = (pop_2025 - pop_2000) / pop_2000 x 100"
        r["source_id"] = "S1"
        rows.append(r)
    rank_pool = [r for r in rows if r["change_2000_2025_pct"] and int(r["pop_2000"]) >= SMALL_TOWN_MIN_POP_2000]
    rank_pool.sort(key=lambda r: float(r["change_2000_2025_pct"]))
    for i, r in enumerate(rank_pool, 1):
        r["rank_loss_pct"] = i
    for r in rows:
        r.setdefault("rank_loss_pct", "")
    rows.sort(key=lambda r: (r["rank_loss_pct"] == "", r["rank_loss_pct"] or 0))
    return rows


def households_rows(bdl, eu, hh_by_class):
    rows = []

    def add(**kw):
        rows.append(kw)
    # census 2002
    sizes02 = [(194837, 194838, "1"), (194835, 194836, "2"), (194833, 194834, "3"), (194831, 194832, "4"), (194829, 194830, "5+")]
    hh02 = bdl[9199]["vals"][2002]
    pop02 = sum(bdl[p]["vals"][2002] for _, p, _ in sizes02)
    add(year=2002, area="national", kind="census", households=hh02, population_in_households=pop02,
        avg_persons_per_household=round(pop02 / hh02, 2), **{f"hh_{lab}_person": bdl[h]["vals"][2002] for h, _, lab in sizes02},
        value_type="households reported; population and average derived",
        formula="population_in_households = sum of BDL 194830/194832/194834/194836/194838; average = population / households", source_id="S16")
    sizes11 = [(450472, "1"), (450474, "2"), (450475, "3"), (450476, "4"), (450477, "5+")]
    add(year=2011, area="national", kind="census", households=bdl[450473]["vals"][2011],
        population_in_households=bdl[450478]["vals"][2011], avg_persons_per_household=bdl[450479]["vals"][2011],
        **{f"hh_{lab}_person": bdl[h]["vals"][2011] for h, lab in sizes11},
        value_type="reported", formula="", source_id="S17")
    sizes21 = [(1652550, "1"), (1652551, "2"), (1652552, "3"), (1652553, "4"), (1652554, "5+")]
    add(year=2021, area="national", kind="census", households=bdl[1652549]["vals"][2021],
        population_in_households=bdl[1652555]["vals"][2021], avg_persons_per_household=bdl[1652556]["vals"][2021],
        **{f"hh_{lab}_person": bdl[h]["vals"][2021] for h, lab in sizes21},
        value_type="reported", formula="", source_id="S18")
    for cls, (h, p) in hh_by_class.items():
        add(year=2021, area=cls, kind="census (sum of gminas)", households=h, population_in_households=p,
            avg_persons_per_household=round(p / h, 2), value_type="derived",
            formula="sum of gmina values by place class (BDL 1652549 and 1652555); average = population / households", source_id="S18")
    for per, (val, flag) in sorted(eu["persons_per_private_household_eu_lfs"].items()):
        add(year=int(per), area="national", kind="annual estimate (EU-LFS survey)", households="", population_in_households="",
            avg_persons_per_household=val, value_type="reported", formula="", source_id="S24")
    keys = ["year", "area", "kind", "households", "population_in_households", "avg_persons_per_household",
            "hh_1_person", "hh_2_person", "hh_3_person", "hh_4_person", "hh_5+_person", "value_type", "formula", "source_id"]
    return [{k: r.get(k, "") for k in keys} for r in rows]


def migration_class_rows(net_int, pop, big_ids):
    """Net internal migration (permanent-residence registrations) summed by place class, with per-1000 rates."""
    rows = []
    sp, cp = class_sums(pop, big_ids, YEARS, True)
    si, ci = class_sums(net_int, big_ids, YEARS, True)
    for cls in ("big_cities", "small_cities", "villages"):
        for y in YEARS:
            p, i = sp[cls].get(y), si[cls].get(y)
            if p is None:
                continue
            rows.append({"year": y, "class": cls, "population": p, "net_internal_migration": "" if i is None else i,
                         "net_internal_per_1000": fmt(1000 * i / p) if i is not None else "",
                         "gmina_units_with_migration": ci[cls][y], "gmina_units_with_population": cp[cls][y],
                         "value_type": "derived",
                         "formula": "sum over gmina-level BDL units of the class (var 80125, urban parts type 4 and rural parts type 5 where BDL has them); per 1000 = net / population (60641) x 1000",
                         "source_id": "S15;S1"})
    return rows


def main():
    import fetch_bdl_gminas as fg
    bdl = read_bdl_national()
    eu = read_eurostat()
    write(OUT / "age_sex_pyramid.csv", build_pyramid(bdl))
    write(OUT / "age_structure_indicators.csv", build_age_indicators(bdl, eu))
    write(OUT / "vital_rates.csv", build_vital(bdl, eu))
    write(OUT / "migration_national.csv", build_migration_national(bdl, eu))
    write(OUT / "ukraine_inflow.csv", build_ukraine(eu))
    big = read_big()
    big_ids = {c[0] for c in big}
    pop = merged_series(fg.load_gmina_var(60641, YEARS))
    brows = belt_rows(pop, big, read_city_points(), read_centroids())
    write(OUT / "suburban_belt_gminas.csv", brows)
    write(OUT / "suburban_belt_summary.csv", belt_summary(brows, pop, big))
    write(OUT / "small_towns_change.csv", small_town_rows(pop, big))
    net_int = merged_series(fg.load_gmina_var(80125, YEARS))
    write(OUT / "migration_by_place_class.csv", migration_class_rows(net_int, pop, big_ids))
    write(OUT / "households.csv", households_rows(bdl, eu, {}))
    print("done")


if __name__ == "__main__":
    main()
