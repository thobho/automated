# poland-geography

Open boundaries (voivodeships, powiats, gminas) and city points for Poland, keyed by TERYT code so they join with GUS Bank Danych Lokalnych (BDL) data. Findings: [report.md](report.md). Sources and licences: [sources.csv](sources.csv).

## Files (`data/`)

| File | Content | Features |
|---|---|---|
| `voivodeships.geojson` / `.topojson` | voivodeships | 16 |
| `powiats.geojson` / `.topojson` | powiats incl. cities with powiat rights | 380 |
| `gminas.geojson` / `.topojson` | gminas (type 1, 2, 3) | 2479 |
| `cities.geojson` / `cities.csv` | one point per city | 1020 (34 with `big_city` = true) |
| `bdl_join_report.json` | match against the BDL unit list | - |
| `reference/big_city_list_demography_2025.csv` | the 34-city list of the demography series (test fixture) | 34 |

Every feature has `teryt` (2, 4 or 7 digits), `name` and `source_id` (key into `sources.csv`). Cities also carry `bdl_unit_id`, voivodeship and powiat (code and name), `population` (BDL var. 60641, 31 Dec 2025, `source_id` S3), `population_year`, `big_city` (population >= 100000) and `coord_source_id` (S4 = GeoNames, S1 = polygon point).

## Coordinates and simplification

- CRS: the PRG shapefiles are in geographic ETRS89 (GRS80, lon/lat); the output is treated as WGS84 lon/lat (GeoJSON RFC 7946 order: lon, lat). No reprojection step.
- Simplification with mapshaper 0.6.109: Visvalingam, weighted, `keep-shapes` (no feature vanishes), shared borders stay shared (topology-aware).
  - powiats: 2% of removable vertices kept; gminas: 1%.
  - voivodeships are the dissolve of the simplified powiats, so voivodeship and powiat borders coincide exactly. Gmina borders come from their own simplification and can differ slightly from powiat borders (not measured); do not overlay gmina fills over a powiat outline expecting pixel-exact agreement.
  - GeoJSON coordinates rounded to 0.0001 degrees (about 11 m); TopoJSON quantised to 10000 steps.
- Areas (`area_km2`) are the official PRG areas, not computed from the simplified shapes.

## Rebuild

```
python3 scripts/build_geo.py            # downloads (377 MB PRG zip, cached), runs mapshaper via npx, calls BDL
python3 scripts/build_geo.py --skip-bdl # boundaries only
python3 -m unittest discover -s tests
```

Needs Python 3 (standard library only), Node/npx (downloads mapshaper@0.6.109) and network. Downloads and BDL responses are cached in `data/raw/cache/` (git-ignored); BDL calls are throttled and honour Retry-After (87 requests in a full run). A first full run took about 7 minutes.

## City status changes

A "city" here is a BDL/TERYT gmina of type 1 (urban gmina) or type 4 (town inside an urban-rural gmina) that has a current polygon of type 1 or 3 and a 2025 population. When a village receives town status, its gmina changes type (usually 2 to 3) and a new type 4 unit appears, so its 7-digit TERYT code changes; BDL keeps the old unit too (170 such pairs, see the join check). For series over time join on the first 6 digits (gmina) plus name, not on the 7-digit code. The big-city flag is population >= 100000 in 2025 and reproduces the fixed 34-city list exactly (code and population); it is a snapshot, not a history. Some BDL names carry suffixes (`X - miasto`, `Wałbrzych od 2013`, `M.st.Warszawa od 2002`); the cities file strips them to the plain city name.

## Preview

`preview.html` is a throwaway page (plain canvas, no libraries, no styling). Serve this folder and open it:

```
cd research/poland-geography && python3 -m http.server 8137   # then http://localhost:8137/preview.html
```

Screenshots in `docs/verification/`.
