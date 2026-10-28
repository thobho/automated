#!/usr/bin/env python3
"""Rebuild the Poland geography data from the original open sources.

    python3 scripts/build_geo.py            # everything (downloads are cached)
    python3 scripts/build_geo.py --skip-bdl # boundaries + cities from cache only

Stages
  1. download originals into data/raw/cache/ (git-ignored):
       S1  PRG administrative units (GUGiK)   - 377 MB zip, shapefiles in ETRS89 lat/lon
       S4  GeoNames PL dump                   - city coordinates
       S2/S3 GUS BDL API                      - unit list (join check) and population
  2. simplify boundaries with mapshaper (pinned, via npx), keeping shared borders
     topologically consistent, write GeoJSON + TopoJSON to data/
  3. build the cities point layer and the BDL join report

Python 3 standard library only; the only external tool is mapshaper (npm, pinned).
"""
import argparse
import csv
import json
import math
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "cache"
DATA = ROOT / "data"

MAPSHAPER = "mapshaper@0.6.109"
PRG_URL = "https://opendata.geoportal.gov.pl/prg/granice/00_jednostki_administracyjne.zip"
GEONAMES_URL = "https://download.geonames.org/export/dump/PL.zip"
BDL = "https://bdl.stat.gov.pl/api/v1"
POP_VARIABLE = "60641"  # BDL: population by place of residence, total, as of 31 Dec
POP_YEAR = 2025
BIG_CITY_MIN = 100_000
THROTTLE_S = 1.0

# simplification (percent of removed-vertices kept by Visvalingam, weighted) per level
SIMPLIFY = {"powiats": "2%", "gminas": "1%"}
COORD_PRECISION = 0.0001  # degrees, about 11 m
TOPO_QUANT = 10000


# ----------------------------------------------------------------- pure helpers
def bdl_to_teryt(unit_id):
    """12-char BDL unit id -> TERYT code (2 voivodeship, 4 powiat, 7 gmina; '' for the country).

    Layout (checked against the unit list): id[2:4] voivodeship, id[7:9] powiat,
    id[9:11] gmina, id[11] gmina type (1 urban, 2 rural, 3 urban-rural,
    4 urban part, 5 rural part of a type 3 gmina).
    """
    if len(unit_id) != 12 or not unit_id.isdigit():
        raise ValueError("bad BDL unit id: %r" % unit_id)
    voiv, powiat, gmina, kind = unit_id[2:4], unit_id[7:9], unit_id[9:11], unit_id[11]
    if unit_id[2:] == "0" * 10:
        return ""
    if powiat == "00":
        return voiv
    if gmina == "00":
        return voiv + powiat
    return voiv + powiat + gmina + kind


def norm_name(s):
    """Fold a place name for matching: case, diacritics (incl. l-stroke), punctuation."""
    s = s.replace("ł", "l").replace("Ł", "L")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def ring_contains(ring, x, y):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def polygons_of(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPolygon":
        return geom["coordinates"]
    raise ValueError(geom["type"])


def point_in_geometry(geom, x, y):
    """Point-in-(Multi)Polygon with holes."""
    for poly in polygons_of(geom):
        if ring_contains(poly[0], x, y) and not any(ring_contains(h, x, y) for h in poly[1:]):
            return True
    return False


def ring_area_centroid(ring):
    a = cx = cy = 0.0
    for i in range(len(ring) - 1):
        x0, y0, x1, y1 = ring[i][0], ring[i][1], ring[i + 1][0], ring[i + 1][1]
        cr = x0 * y1 - x1 * y0
        a += cr
        cx += (x0 + x1) * cr
        cy += (y0 + y1) * cr
    if a == 0:
        return 0.0, ring[0][0], ring[0][1]
    return a / 2, cx / (3 * a), cy / (3 * a)


def representative_point(geom):
    """A point guaranteed inside the geometry: centroid of the largest polygon if it
    is inside, otherwise the middle of the widest horizontal interior interval."""
    best = max(polygons_of(geom), key=lambda p: abs(ring_area_centroid(p[0])[0]))
    _, cx, cy = ring_area_centroid(best[0])
    if point_in_geometry({"type": "Polygon", "coordinates": best}, cx, cy):
        return cx, cy
    ys = [p[1] for p in best[0]]
    y = (min(ys) + max(ys)) / 2
    xs = []
    for ring in best:
        for i in range(len(ring) - 1):
            (x0, y0), (x1, y1) = ring[i][:2], ring[i + 1][:2]
            if (y0 > y) != (y1 > y):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    xs.sort()
    spans = [(xs[i + 1] - xs[i], (xs[i] + xs[i + 1]) / 2) for i in range(0, len(xs) - 1, 2)]
    return max(spans)[1], y


def city_name(bdl_name):
    """BDL names the town of an urban-rural gmina 'X - miasto'; the city name is 'X'."""
    if bdl_name.startswith("M.st.Warszawa"):  # BDL: 'M.st.Warszawa od 2002'
        return "Warszawa"
    bdl_name = re.sub(r"\s+od\s+\d{4}$", "", bdl_name)  # BDL: 'Walbrzych od 2013'
    return re.sub(r"\s+-\s+(miasto|obszar wiejski)$", "", bdl_name)


def is_city_kind(kind):
    """BDL/TERYT gmina types that are a city: 1 (urban gmina), 4 (town of an urban-rural gmina)."""
    return str(kind) in ("1", "4")


def pick_geonames(cands):
    """Best GeoNames candidate: administrative-seat feature codes first, then population."""
    return max(cands, key=lambda c: (c["fcode"].startswith("PPLA"), c["population"]))


def explain_unmatched_bdl(codes, geo_codes):
    """Why BDL lists units that no current polygon has. BDL keeps historical units, so a gmina
    that changed type (e.g. rural 2 -> urban-rural 3 after getting town status) appears twice."""
    geo6 = {g[:6] for g in geo_codes if len(g) == 7}
    out = {"type_changed_current_gmina_exists": 0, "no_current_gmina_with_this_code": 0,
           "not_a_gmina_code": 0}
    for c in codes:
        if len(c) != 7:
            out["not_a_gmina_code"] += 1
        elif c[:6] in geo6:
            out["type_changed_current_gmina_exists"] += 1
        else:
            out["no_current_gmina_with_this_code"] += 1
    return out


def match_stats(a, b):
    a, b = set(a), set(b)
    return {"a": len(a), "b": len(b), "both": len(a & b), "only_a": sorted(a - b), "only_b": sorted(b - a)}


# ------------------------------------------------------------------ network bits
def log(*a):
    print(*a, flush=True)


def download(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    log("downloading", url)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "poland-geography-build/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    tmp.rename(dest)
    return dest


def bdl_get(path, params):
    """Cached, throttled BDL GET. Honours Retry-After on HTTP 429."""
    import hashlib

    q = urllib.parse.urlencode(list(params) + [("format", "json")])
    url = "%s%s?%s" % (BDL, path, q)
    cp = RAW / "bdl" / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".json")
    if cp.exists():
        return json.loads(cp.read_text())
    for _ in range(30):
        time.sleep(THROTTLE_S)
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            cp.parent.mkdir(parents=True, exist_ok=True)
            cp.write_text(json.dumps(data))
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(str(e.headers.get("Retry-After", "60")).split()[0]) + 2
                log("BDL 429, sleeping %d s (Retry-After)" % wait)
                time.sleep(min(wait, 3600))
                continue
            raise
    raise RuntimeError("BDL kept refusing: " + url)


def bdl_paged(path, params):
    page = 0
    while True:
        d = bdl_get(path, list(params) + [("page-size", 100), ("page", page)])
        yield from d.get("results", [])
        if not d.get("links", {}).get("next"):
            return
        page += 1


# --------------------------------------------------------------------- stage 2
def mapshaper(*args):
    cmd = ["npx", "--yes", MAPSHAPER] + [str(a) for a in args]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("mapshaper failed: %s\n%s" % (" ".join(cmd), r.stderr))
    return r.stdout


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def extract_prg():
    zp = download(PRG_URL, RAW / "prg" / "00_jednostki_administracyjne.zip")
    out = RAW / "prg" / "shp"
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zp) as z:
        for name in z.namelist():
            if re.match(r"A0[123]_.*\.(shp|shx|dbf|prj|cpg)$", name) and not (out / name).exists():
                z.extract(name, out)
    return out


def build_boundaries():
    shp = extract_prg()
    tmp = RAW / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    gj = ["format=geojson", "precision=%s" % COORD_PRECISION]

    # voivodeship names/areas from the official layer (attributes only)
    mapshaper(shp / "A01_Granice_wojewodztw.shp", "-filter-fields", "JPT_KOD_JE,JPT_NAZWA_,JPT_POWIER",
              "-o", tmp / "voiv_attr.csv", "format=csv")
    voiv_attr = {r["JPT_KOD_JE"]: r for r in read_csv(tmp / "voiv_attr.csv")}

    # powiats simplified; voivodeships = dissolve of the simplified powiats (borders match exactly)
    simp = ["-simplify", "visvalingam", "weighted", SIMPLIFY["powiats"], "keep-shapes"]
    mapshaper(shp / "A02_Granice_powiatow.shp", "-filter-fields", "JPT_KOD_JE,JPT_NAZWA_,JPT_POWIER",
              "-rename-fields", "teryt=JPT_KOD_JE,name=JPT_NAZWA_,area_ha=JPT_POWIER",
              *simp, "-each", "voiv=teryt.substr(0,2)",
              "-o", tmp / "powiats.json", *gj)
    mapshaper(tmp / "powiats.json", "-dissolve", "voiv", "-o", tmp / "voivs.json", *gj)
    mapshaper(shp / "A03_Granice_gmin.shp", "-filter-fields", "JPT_KOD_JE,JPT_NAZWA_,JPT_POWIER",
              "-rename-fields", "teryt=JPT_KOD_JE,name=JPT_NAZWA_,area_ha=JPT_POWIER",
              "-simplify", "visvalingam", "weighted", SIMPLIFY["gminas"], "keep-shapes",
              "-o", tmp / "gminas.json", *gj)

    voivs = json.loads((tmp / "voivs.json").read_text())
    for f in voivs["features"]:
        t = f["properties"].pop("voiv")
        a = voiv_attr[t]
        f["properties"] = {"teryt": t, "name": a["JPT_NAZWA_"].replace("województwo ", ""),
                           "area_km2": round(float(a["JPT_POWIER"]) / 100, 1), "source_id": "S1"}
    voivs["features"].sort(key=lambda f: f["properties"]["teryt"])

    powiats = json.loads((tmp / "powiats.json").read_text())
    for f in powiats["features"]:
        p = f["properties"]
        f["properties"] = {"teryt": p["teryt"], "name": p["name"], "voivodeship_teryt": p["teryt"][:2],
                           "area_km2": round(float(p["area_ha"]) / 100, 1), "source_id": "S1"}
    powiats["features"].sort(key=lambda f: f["properties"]["teryt"])

    gminas = json.loads((tmp / "gminas.json").read_text())
    for f in gminas["features"]:
        p = f["properties"]
        f["properties"] = {"teryt": p["teryt"], "name": p["name"], "type": int(p["teryt"][6]),
                           "powiat_teryt": p["teryt"][:4], "voivodeship_teryt": p["teryt"][:2],
                           "area_km2": round(float(p["area_ha"]) / 100, 1), "source_id": "S1"}
    gminas["features"].sort(key=lambda f: f["properties"]["teryt"])

    layers = {"voivodeships": voivs, "powiats": powiats, "gminas": gminas}
    for name, fc in layers.items():
        write_json(DATA / (name + ".geojson"), fc)
        mapshaper(DATA / (name + ".geojson"), "-o", DATA / (name + ".topojson"), "format=topojson",
                  "quantization=%d" % TOPO_QUANT)
        log("%-13s %4d features  geojson %7d B  topojson %7d B" % (
            name, len(fc["features"]), (DATA / (name + ".geojson")).stat().st_size,
            (DATA / (name + ".topojson")).stat().st_size))
    return layers


# --------------------------------------------------------------------- stage 3
def load_bdl_units():
    units = {}
    for lvl in (2, 5, 6):
        for u in bdl_paged("/units", [("level", lvl)]):
            units[u["id"]] = dict(u, teryt=bdl_to_teryt(u["id"]))
    return units


def load_bdl_population():
    pop = {}
    for r in bdl_paged("/data/by-variable/" + POP_VARIABLE, [("unit-level", 6), ("year", POP_YEAR)]):
        v = [x for x in r.get("values", []) if int(x["year"]) == POP_YEAR and x.get("val") is not None]
        if v:
            pop[r["id"]] = int(round(float(v[0]["val"])))
    return pop


def join_report(layers, units):
    rep = {}
    for lvl, key, ndig in ((2, "voivodeships", 2), (5, "powiats", 4), (6, "gminas", 7)):
        ours = [f["properties"]["teryt"] for f in layers[key]["features"]]
        theirs = [u["teryt"] for u in units.values()
                  if u["level"] == lvl and (lvl != 6 or u["kind"] in ("1", "2", "3"))]
        s = match_stats(ours, theirs)
        s["rate_geo_in_bdl"] = round(100 * s["both"] / s["a"], 2)
        s["rate_bdl_in_geo"] = round(100 * s["both"] / s["b"], 2)
        rep[key] = {"geometry_units": s["a"], "bdl_units": s["b"], "matched": s["both"],
                    "percent_geometry_found_in_bdl": s["rate_geo_in_bdl"],
                    "percent_bdl_found_in_geometry": s["rate_bdl_in_geo"],
                    "only_in_geometry": s["only_a"], "only_in_bdl": s["only_b"]}
        if key == "gminas":
            rep[key]["only_in_bdl_explained"] = explain_unmatched_bdl(s["only_b"], ours)
    return rep


def load_geonames():
    zp = download(GEONAMES_URL, RAW / "geonames" / "PL.zip")
    out = []
    with zipfile.ZipFile(zp) as z, z.open("PL.txt") as f:
        for line in f.read().decode("utf-8").splitlines():
            c = line.split("\t")
            if c[6] != "P":
                continue
            names = {norm_name(c[1]), norm_name(c[2])} | {norm_name(a) for a in c[3].split(",") if a}
            out.append({"id": c[0], "names": names, "admin3": c[12], "lat": float(c[4]), "lon": float(c[5]),
                        "fcode": c[7], "population": int(c[14] or 0)})
    by_name = {}
    for g in out:
        for n in g["names"]:
            by_name.setdefault(n, []).append(g)
    return by_name


def build_cities(layers, units, pop, geonames):
    gm = {f["properties"]["teryt"][:6]: f for f in layers["gminas"]["features"]}
    voiv_name = {f["properties"]["teryt"]: f["properties"]["name"] for f in layers["voivodeships"]["features"]}
    pow_name = {f["properties"]["teryt"]: f["properties"]["name"] for f in layers["powiats"]["features"]}
    pow_feats = {}
    for f in layers["gminas"]["features"]:
        pow_feats.setdefault(f["properties"]["powiat_teryt"], []).append(f)
    feats, csv_rows = [], []
    for uid, u in sorted(units.items(), key=lambda kv: kv[1]["teryt"]):
        if u["level"] != 6 or not is_city_kind(u["kind"]) or uid not in pop:
            continue
        t = u["teryt"]
        home = gm.get(t[:6])
        # only current gminas: a type-1 city needs a type-1 polygon, a type-4 town a type-3 polygon
        if home is None or home["properties"]["type"] != (1 if t[6] == "1" else 3):
            continue
        name = city_name(u["name"])
        cands = geonames.get(norm_name(name), [])
        # tier 1: same TERYT gmina code in GeoNames (admin3); tier 2: inside the gmina polygon
        inside = [c for c in cands if c["admin3"] == t[:6]] or [
            c for c in cands if point_in_geometry(home["geometry"], c["lon"], c["lat"])]
        chosen = pick_geonames(inside) if inside else None
        if chosen is None:  # near a simplified border: accept a same-name place in the same powiat
            near = [c for c in cands if any(point_in_geometry(g["geometry"], c["lon"], c["lat"])
                                            for g in pow_feats[t[:4]])]
            chosen = pick_geonames(near) if near else None
        if chosen:
            lon, lat, src = chosen["lon"], chosen["lat"], "S4"
        else:
            lon, lat = representative_point(home["geometry"])
            src = "S1"
        p = pop[uid]
        props = {"teryt": t, "bdl_unit_id": uid, "name": name, "voivodeship_teryt": t[:2],
                 "voivodeship": voiv_name[t[:2]], "powiat_teryt": t[:4], "powiat": pow_name[t[:4]],
                 "gmina_type": int(t[6]), "population": p, "population_year": POP_YEAR,
                 "big_city": p >= BIG_CITY_MIN, "coord_source_id": src, "source_id": "S3"}
        feats.append({"type": "Feature", "properties": props,
                      "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]}})
        csv_rows.append(dict(props, lon=round(lon, 5), lat=round(lat, 5)))
    return {"type": "FeatureCollection", "features": feats}, csv_rows


def write_cities(fc, rows):
    write_json(DATA / "cities.geojson", fc)
    cols = list(rows[0].keys())
    with open(DATA / "cities.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-bdl", action="store_true", help="do not call the BDL API (boundaries only)")
    args = ap.parse_args()
    layers = build_boundaries()
    if args.skip_bdl:
        return 0
    units = load_bdl_units()
    log("BDL units fetched:", len(units))
    rep = join_report(layers, units)
    write_json(DATA / "bdl_join_report.json", rep)
    for k, v in rep.items():
        log("join %-13s geometry %4d  BDL %4d  matched %4d" % (k, v["geometry_units"], v["bdl_units"], v["matched"]))
    pop = load_bdl_population()
    fc, rows = build_cities(layers, units, pop, load_geonames())
    write_cities(fc, rows)
    log("cities:", len(rows), "big:", sum(1 for r in rows if r["big_city"]),
        "from geonames:", sum(1 for r in rows if r["coord_source_id"] == "S4"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
