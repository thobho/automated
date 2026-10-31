# Visualization-of-the-world site

Two provenances, one component library:

- **`real.html` — real showcase.** Statistics Poland (GUS) Bank Danych Lokalnych and Eurostat numbers from `../research/poland-demography-housing/data/processed/`, copied verbatim into `data/real/`. Every chart is marked **REAL DATA**, carries the source ids in its footer and exports a `source_id` column.
- **Demo pages (`index.html`, `charts.html`, ...)** — the same components on synthetic numbers, marked **DEMO DATA, NOT REAL**. Only boundaries and place names are real there.

Library: **Apache ECharts 6.1.0** (pinned, vendored as `vendor/lib/echarts-6.1.0.min.js`), plus topojson-client 3.1.0. Library choice and evidence: `../research/viz-libraries/report.md`. Facts and docs links: [sources.md](sources.md).

## Run
```
cd projects/visualization-of-the-world/site
python3 -m http.server 8000      # open http://localhost:8000/real.html
```
No build step, no CDN. `file://` does not work (the pages fetch data).

## Pages
`real.html` (real GUS/Eurostat data: KPI cards, indexed dynamics, housing vs population, houses/flats, Poland vs neighbours, 34 big cities on the map), `index.html` overview, `charts.html` (13 chart types), `interaction.html` (playback, filter, brush, linked views, zoom, morph), `maps.html` (choropleth, powiat drill-down, city bubbles, zoom to region), `formats.html` (CSV, JSON, GeoJSON, TopoJSON in; PNG, SVG, CSV out), `polish.html` (responsive, theme, loading/empty/error, Source footer), `matrix.html` (capabilities table from `data/capabilities.json`).

## Real data (`data/real/`)

The eight files are byte-identical copies of `../research/poland-demography-housing/data/processed/` (a `node --test` check enforces this). Do not edit them here; re-copy after a research update. `source_id` values point at `../research/poland-demography-housing/sources.csv` (accessed 2026-10-29).

| File | What it holds | Years | Source ids (research registry) |
|---|---|---|---|
| `population_by_class.csv` | Population (31 Dec) by place class: big cities (34 gminas), small cities, villages | 2000-2025 | S1 (GUS BDL var 60641, 60617, 60633) |
| `housing_completions_by_class.csv` | Dwellings completed by class, type and basis (`total`, `house`/`flat` direct, `house_proxy_*`/`flat_proxy_*` proxy, `other`) | 2000-2025 | S41 (BDL 748601), S42 (BDL 430, proxy), S43 (BDL 748247, direct) |
| `housing_vs_population.csv` | Flats/houses per 1000 residents, indices and shares by class; row-level `source_id` and basis notes | 2000-2025 | S41;S42;S43;S1 |
| `housing_stock_by_class.csv` | Dwelling stock, floor area, dwellings per 1000 residents, persons per dwelling | 2000-2025 | S44;S1 (BDL 60811, 60813, 60641) |
| `migration_by_place_class.csv` | Net internal migration (permanent residence) by class, absolute and per 1000 | 2000-2025 | S15;S1 (BDL 80125) |
| `europe_summary.csv` | First/latest values, change and Poland rank for 9 indicators; PL, CZ, SK, HU, DE, RO, LT, EU-27 | 2000-2025 | S29 (demo_gind), S30 (demo_find), S31 (demo_pjanind), S32 (demo_mlexpec) |
| `europe_annual.csv` | Annual Eurostat series behind the summary (population 1 Jan and index 2000=100, life expectancy, median age, fertility, ...) | 2000-2025 | S29-S32 |
| `big_city_list.csv` | The 34 big cities with TERYT unit id and 2025 population | 2025 | S1; city points: poland-geography (GUGiK PRG + GeoNames) |

Loader: `Votw.data.realPopulation()`, `realCompletions()`, `realHousingVsPop()`, `realStock()`, `realMigration()`, `realEurope()` (+ `realEuropeSummary()`), `realBigCities()` in `js/votw-charts.js`; they fetch `data/real/<name>.csv` and parse it with `VotwCore.parseCsv`.

### Proxy vs direct
GUS publishes two different series for the houses/flats split:

- **Direct (2009-2025):** var 748247, houses = single-family, flats = multi-family, plus var 748601 for the total. Used by the houses/flats chart (direct only).
- **Proxy (2000-2008):** individual construction (var 430, mostly houses but also private dwellings for sale or rent) against the total (var 748601). Used only in the housing-vs-population chart, under a hatched band labelled "proxy basis 2000-2008".

A chart never draws proxy and direct years as one unmarked line; 2000-2008 and 2009-2025 are always visually separated (hatch + label, or the chart starts in 2009).

## Folder structure
```
site/
  *.html                 one page each; same skeleton, scripts at the bottom (real.html sets body[data-provenance="real"])
  css/site.css           layer on top of the design system (tokens only, no raw colours)
  js/shell.js            top bar, nav, theme switch, provenance banner and footer (demo or real, from body[data-provenance])
  js/votw-core.js        pure logic (CSV, index, rank, bins, bbox, real-data pivots); unit-tested, runs in node too
  js/votw-charts.js      Votw.figure(): card, states, legend, table view, exports, Source footer; token->ECharts helpers
  js/specs-*.js          chart specs per page; js/page-*.js mount them (specs-real.js = real.html)
  data/                  demo.json, demo-*.csv (synthetic), real/ (verbatim GUS/Eurostat CSVs), geo/ (simplified boundaries, cities), capabilities.json
  vendor/lib/            echarts 6.1.0, topojson-client 3.1.0 (unmodified, minified)
  vendor/design/         copies of ../design tokens.css, components.css/js and the two used font families
  scripts/               make_demo_data.py, verify_site.cjs (browser checks), check_footers.cjs
  tests/                 core.test.js (node), test_demo_data.py
  docs/verification/     screenshots and results.json from verify_site.cjs
```
`vendor/design/` is a copy: after changing `../design/`, re-copy `tokens.css`, `components.css`, `components.js` (and fonts if the font set changed). Only the Baltyk direction's fonts are copied; the other directions are not used here.

## How to add a chart
1. Add a spec to a `js/specs-*.js` file (or a new one, loaded before its `page-*.js`):
   ```js
   { id: "my-chart", title: "States the finding", subtitle: "Measure, unit, years",
     source: { label: "Publisher, table (S41)", url: "https://...", meta: "access date etc.", ids: "S41" }, // required
     real: true,                                     // real GUS/Eurostat data: REAL DATA badge, source_id CSV column
     load: () => Votw.data.realCompletions(),        // async, may throw -> error state with Try again
     csv: (d) => ({ header: [...], rows: [...], sourceId: (row) => "S41" }), // feeds table view and CSV export
     build: (d, ctx) => Votw.base({ xAxis: Votw.catAxis([...]), yAxis: Votw.valueAxis(), series: [...] }),
     height: 340 }                                    // number or (width) => number
   ```
   Demo specs keep the default provenance (`DEMO DATA, NOT REAL`). Real specs must carry `real: true`, source ids in `source.label` and per-row ids in `csv.sourceId` (a function, an array or a constant); `source.ids` is the fallback.
2. Mount it: `Votw.figure(document.getElementById("figures"), spec)`. Return `"empty"` from `build` to show the empty state.
3. Colours only through tokens: `Votw.placeColor("villages")`, `Votw.catColors()`, `Votw.mapRamp()`, `Votw.cssVar("--color-...")`. Never write a hex value. Charts redraw on theme change automatically because `build` is called again.
4. Missing `source` makes `Votw.figure` throw; `node scripts/check_footers.cjs <url>` fails if any card lacks the footer.
5. Never mix proxy (2000-2008) and direct (2009-2025) housing bases in one unlabelled series: use `VotwCore.basisRanges()` plus a hatched band, or start at 2009.
6. Add the capability to `data/capabilities.json` if it is new.

## Deploy
The site is published by `.github/workflows/deploy-pages.yml` on every push to `main` that touches `projects/visualization-of-the-world/site/**` (or by `workflow_dispatch`). No build step: the workflow uploads `site/` with `actions/upload-pages-artifact` and deploys it with `actions/deploy-pages`.

1. Repository **Settings → Pages → Build and deployment → Source: GitHub Actions** (once).
2. Push to `main` (or run the workflow manually). The site is served at `https://<owner>.github.io/automated/` (the repo-name subpath).
3. All asset paths are relative (`vendor/...`, `css/...`, `js/...`, `data/...`), so the subpath works without a base path. GitHub Pages serves `index.html` at the root of `site/`; the real showcase is at `real.html`.
4. GitHub Pages hosts one site per repository. If `smolec-weather-pages.yml` is also enabled, the most recent deployment wins; enable only the workflow for the folder you want live.

## Templates

Reusable chart templates are available in `templates/`:
- Basic structure templates for different chart types
- Pre-built components for common interactions (timeline, filters)
- Proper source footer implementations
- Accessible color schemes and layouts

Always start with a template rather than building from scratch.

## Checks
```
python3 -m unittest discover -s tests                 # generator determinism, flags, matrix completeness
node --test tests/core.test.js                        # core logic + real-data shaping + verbatim data copies
python3 -m http.server 8000 &                         # then, with playwright installed (NODE_PATH) and optional CHROMIUM_PATH:
node scripts/check_footers.cjs http://localhost:8000
node scripts/verify_site.cjs http://localhost:8000 docs/verification
python3 scripts/make_demo_data.py                     # regenerate the synthetic data (deterministic)
```
`verify_site.cjs` checks 8 pages (the seven demo pages and `real.html`) at 375, 768 and 1280 px (console errors, failed requests, horizontal scroll, Source footer, provenance tag), then tooltip, table view, CSV/SVG/PNG export, dark theme, play, filter, brush, zoom, shape morph, map drill-down, zoom to region, touch taps, the blocked-data failure path with recovery, and on `real.html`: the REAL DATA banner, no DEMO wording, the three KPI cards with manual Source footers, the `source_id` CSV column and real-data aria labels. Results: `docs/verification/results.json`.

## Notes
- Language: page text is English; the design system's "Źródło:" footer label is shown as "Source:" here (issue text). `vendor/design/components.js` still has some Polish aria labels (play button, menu); they are part of the design system copy.
- The real showcase adds no value that the research series does not publish: the map shows cities only (no per-voivodeship indicator), and no synthetic number is used anywhere on `real.html`.
- Library problems and workarounds are listed in the PR and summarised in `data/capabilities.json` notes.

