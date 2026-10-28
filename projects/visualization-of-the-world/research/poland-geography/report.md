# Poland geography data: what exists, licences, sizes, recommendation

Access date for every source: 2026-10-28. Keys like [S1] refer to [sources.csv](sources.csv).

## 1. What is available per level

| Level | Available? | Source | Result |
|---|---|---|---|
| Voivodeships (16) | yes | PRG, GUGiK [S1] | built: `voivodeships.*` |
| Powiats (380) | yes | PRG [S1] | built: `powiats.*` |
| Gminas (2479) | yes, no fallback needed | PRG [S1] | built: `gminas.*` (optional layer, see sizes) |
| Cities as points | no official point layer was used | BDL population [S3] + GeoNames coordinates [S4] | built: `cities.*`, 1020 cities |

Boundaries: the State Register of Borders (PRG) is the official, referential database of the three-tier division into gminas, powiats and voivodeships with TERYT code and name per unit [S1]. The geoportal page states the data are free of charge and for any use [S1]. Download: one 377 MB zip with shapefiles for voivodeships (A01), powiats (A02), gminas (A03) plus cadastral units (A05) and precincts (A06), which are not used. The build script extracts only A01 to A03.

Cities: no official city coordinate file was found among the sources checked (not searched further), so points come from GeoNames [S4], whose `admin3` field equals the 6-digit TERYT gmina code, joined by name and gmina code (1020 of 1020 matched; every point lies inside its gmina polygon). Population comes only from BDL [S3]. A GeoNames dependency is the one weak point: it is secondary, volunteer-curated data under an attribution licence. Fallback in the script when no match exists: a point guaranteed inside the gmina polygon (`coord_source_id` = S1); this was needed 0 times.

Not used: Natural Earth (licence text not retrievable on the access date, and it is a small-scale world dataset; no powiat level expected) [S11]; OpenStreetMap-derived boundaries (ODbL share-alike [S6], and PRG is the official source). GUS publishes unit codes via BDL and TERYT [S2, S10]; its geometry for units is not offered as a separate download in what was checked.

## 2. Licences and attribution

| Data | Licence | Attribution to show |
|---|---|---|
| Boundaries [S1] | free of charge, any use | none required; suggested "Source: PRG, GUGiK" |
| Population, unit codes [S2, S3] | licence text not found on the BDL API page | suggested "Source: GUS, BDL" |
| City coordinates [S4] | CC BY (version not stated) | "GeoNames, https://www.geonames.org" - required |

The attribution for the cities layer (GeoNames) must appear on any page that shows city points.

## 3. File sizes

Raw sizes by `stat`; gzip -9 as an estimate of what a compressing server sends (python `http.server` does not compress).

| File | Raw | gzip -9 |
|---|---|---|
| voivodeships.topojson | 50,760 B | 14,785 B |
| voivodeships.geojson | 177,481 B | 56,540 B |
| powiats.topojson | 273,813 B | 70,613 B |
| powiats.geojson | 884,113 B | 228,000 B |
| gminas.topojson | 892,880 B | 200,110 B |
| gminas.geojson | 1,741,616 B | 364,119 B |
| cities.geojson | 388,834 B | 35,034 B |
| cities.csv | 116,607 B | 29,850 B |

Simplification: powiats 2%, gminas 1% of removable vertices (Visvalingam weighted), coordinates 0.0001 degree. Voivodeships inherit the powiat simplification. Looking at the screenshots (`docs/verification/`), outlines are recognisable at 375 px width and at 1000 px with all gminas drawn; fine coastal and river detail is smoothed. Tighter simplification (4%) was measured and would give powiats 1.6 MB GeoJSON / 409 KB TopoJSON and gminas 4.3 MB / 1.25 MB, which was judged too big for phones.

## 4. Join with GUS BDL

BDL unit ids are 12 characters; the TERYT code is composed from characters 3-4 (voivodeship), 8-9 (powiat), 10-11 (gmina) and 12 (type). The units endpoint was fetched for levels 2, 5 and 6 (4596 units) [S2]. Full detail: `data/bdl_join_report.json`.

| Level | Our units | BDL units | Matched | Our units found in BDL | BDL units found in ours |
|---|---|---|---|---|---|
| Voivodeship | 16 | 16 | 16 | 100% | 100% |
| Powiat | 380 | 382 | 380 | 100% | 99.48% |
| Gmina (type 1-3) | 2479 | 2705 | 2479 | 100% | 91.65% |

Every polygon joins to BDL. The extra BDL units are historical or pseudo units: powiat 0263 "Powiat m. Wałbrzych do 2002" and 1431 "Powiat warszawski"; for gminas, 226 units: 170 are a former type of a gmina that exists today under another type digit (e.g. rural 2 became urban-rural 3 when the village got town status; Pieszyce 0202031 vs current 0202033), 52 have no current gmina with that code (e.g. "Wałbrzych od 2003 do 2012", "Miejska strefa usług publicznych"), 4 are not gmina codes. Practical rule: join on the polygon codes (current state) and ignore BDL units without a polygon; historical series for status-changed gminas need a 6-digit key.

Cities: 302 of type 1 and 718 of type 4 = 1020 cities with a 2025 population. This count was not cross-checked against an external official count of towns (none was looked up). The 34 cities with `big_city` = true match the demography series list [S12] in both unit id and population (tested).

## 5. Basemap options for later

| Option | Licence / terms | Attribution | Notes |
|---|---|---|---|
| No basemap | - | the data attributions above | smallest, fully offline, recommended for the demo |
| Outline only (these voivodeship/powiat borders) | PRG, free for any use [S1] | as above | gives a map without any tile service |
| OSM raster tiles (tile.openstreetmap.org) | OSM data ODbL [S6]; tile server policy: heavy use may be blocked, best-effort availability [S7] | © OpenStreetMap contributors | not suited for a public page with real traffic |
| OpenFreeMap vector tiles | public instance free, no key, no request limits per its site [S8] | OpenFreeMap © OpenMapTiles Data from OpenStreetMap | external service: page stops being fully static/offline; not tested here |

Other providers (Protomaps, MapTiler, etc.) were not evaluated.

## 6. Limits

- Boundaries follow the PRG as published (zip dated 2026-10-23; PRG updates yearly as of 1 January [S1]); they are administrative, not coastlines, and no check of how they treat water areas was made.
- Simplification means areas and lengths must not be measured from the shapes; use the `area_km2` property (official).
- Gmina borders are simplified separately from powiat borders (see README).
- City points are GeoNames locations, not official centroids; 1020 matched by name within the same TERYT gmina.
- BDL licence text was not found; the GeoNames licence version is not stated on its page.
- BDL anonymous quota: the full build used 87 requests, cached afterwards.
- Warsaw is one city unit; cities of urban-rural gminas have a type 4 code.

## 7. Recommendation for the page

- Default view: `voivodeships.topojson` + `powiats.topojson` (together about 325 KB raw, about 85 KB gzipped). TopoJSON is 3 to 4 times smaller than GeoJSON; decode client-side with a small pinned library, or keep the GeoJSON files if no library is wanted (3x larger).
- Gminas: load `gminas.topojson` (893 KB raw, 200 KB gzipped) lazily only when the user zooms in or switches to gmina data; skip it for the first version if the series is not gmina level.
- Cities: `cities.geojson` (35 KB gzipped) for points, filter `big_city` for the 34 large cities; show the GeoNames attribution.
- Join data on `teryt`: BDL id to TERYT with the rule in section 4 (function `bdl_to_teryt` in `scripts/build_geo.py`).
- Basemap: none, or the plain outline; keep OSM-based tiles out of the first version.
