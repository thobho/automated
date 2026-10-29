#!/usr/bin/env python3
"""Generate the SYNTHETIC demo data used by the demo site. Deterministic (seeded), standard library only.

Every number written here is made up. Only boundaries, TERYT codes and city names are real (they come
from research/poland-geography). Run from anywhere: python3 site/scripts/make_demo_data.py
"""
import csv, json, random, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
GEO = os.path.join(DATA, "geo")
YEARS = list(range(2000, 2026))
NOTE = "DEMO DATA, NOT REAL. Synthetic numbers made up for the demo site; only boundaries and place names are real."


def region_series(rng, v0, vtrend, bigshare):
    """Shares (%) of population in big cities / small cities / villages per year; each year sums to 100."""
    out = {"big_cities": [], "small_cities": [], "villages": []}
    v = v0
    for i, _ in enumerate(YEARS):
        v = v + vtrend + rng.uniform(-0.12, 0.12)
        villages = round(min(80, max(10, v)), 1)
        rest = 100 - villages
        big = round(rest * (bigshare - 0.004 * i + rng.uniform(-0.004, 0.004)), 1)
        out["big_cities"].append(big)
        out["villages"].append(villages)
        out["small_cities"].append(round(100 - villages - big, 1))
    return out


def main():
    rng = random.Random(15)
    voiv = json.load(open(os.path.join(GEO, "voivodeships.geojson"), encoding="utf-8"))["features"]
    regions = []
    for f in voiv:
        p = f["properties"]
        regions.append({
            "teryt": p["teryt"], "name": p["name"], "weight_index": round(rng.uniform(1.0, 5.5), 2),
            "shares": region_series(rng, rng.uniform(28, 62), rng.uniform(-0.15, 0.25), rng.uniform(0.35, 0.65)),
        })
    # deliberate gap so the "no data" state of the map can be demonstrated (clearly flagged in the file)
    gap = regions[7]["teryt"]  # opolskie, only in the map data, never in the series
    meta = {"demo": True, "note": NOTE, "generator": "site/scripts/make_demo_data.py (seed 15)",
            "unit": "% of population (synthetic)", "no_data_teryt": gap}
    json.dump({"meta": meta, "years": YEARS, "regions": regions}, open(os.path.join(DATA, "demo.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(DATA, "demo-regions.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["teryt", "name", "year", "big_cities", "small_cities", "villages", "demo_flag"])
        for r in regions:
            for i, y in enumerate(YEARS):
                w.writerow([r["teryt"], r["name"], y] + [r["shares"][k][i] for k in ("big_cities", "small_cities", "villages")] + ["DEMO DATA, NOT REAL"])
    # powiats: parent 2025 village share +- noise
    parent = {r["teryt"]: r["shares"]["villages"][-1] for r in regions}
    powiats = json.load(open(os.path.join(GEO, "powiats.topojson"), encoding="utf-8"))
    geoms = powiats["objects"]["powiats"]["geometries"]
    with open(os.path.join(DATA, "demo-powiats.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["teryt", "name", "voivodeship_teryt", "villages", "demo_flag"])
        for g in geoms:
            p = g["properties"]
            v = round(min(90, max(5, parent[p["voivodeship_teryt"]] + rng.gauss(0, 9))), 1)
            if int(p["teryt"][2:]) >= 61:  # TERYT: powiat numbers 61+ are cities with powiat rights, urban: low village share
                v = round(rng.uniform(0, 6), 1)
            w.writerow([p["teryt"], p["name"], p["voivodeship_teryt"], v, "DEMO DATA, NOT REAL"])
    # cities: synthetic size index and growth; big_city flag is the only real attribute used
    cities = json.load(open(os.path.join(GEO, "cities.geojson"), encoding="utf-8"))["features"]
    with open(os.path.join(DATA, "demo-cities.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["teryt", "name", "voivodeship_teryt", "place_type", "size_index", "growth_pct", "demo_flag"])
        for f in cities:
            p = f["properties"]
            big = p["big_city"]
            size = rng.uniform(100, 800) if big else min(99, rng.lognormvariate(2.6, 0.9))
            growth = rng.gauss(-2 if big else -4, 6)
            w.writerow([p["teryt"], p["name"], p["voivodeship_teryt"], "big_cities" if big else "small_cities",
                        round(size, 1), round(growth, 1), "DEMO DATA, NOT REAL"])


if __name__ == "__main__":
    main()
