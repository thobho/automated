# Demo site (issue #15)

Proof-of-concept showing what the chosen charting library can do, in the project design system, on the real Poland boundaries. **Every number is synthetic ("DEMO DATA, NOT REAL")**; only boundaries, TERYT codes and city names are real.

Library: **Apache ECharts 6.1.0** (pinned, vendored as `vendor/lib/echarts-6.1.0.min.js`), plus topojson-client 3.1.0. Library choice and evidence: `../research/viz-libraries/report.md`. Facts and docs links: [sources.md](sources.md).

## Run
```
cd projects/visualization-of-the-world/site
python3 -m http.server 8000      # open http://localhost:8000/
```
No build step, no CDN. `file://` does not work (the pages fetch data).

## Pages
`index.html` overview, `charts.html` (13 chart types), `interaction.html` (playback, filter, brush, linked views, zoom, morph), `maps.html` (choropleth, powiat drill-down, city bubbles, zoom to region), `formats.html` (CSV, JSON, GeoJSON, TopoJSON in; PNG, SVG, CSV out), `polish.html` (responsive, theme, loading/empty/error, Source footer), `matrix.html` (capabilities table from `data/capabilities.json`).

## Folder structure
```
site/
  *.html                 one page each; same skeleton, scripts at the bottom
  css/site.css           layer on top of the design system (tokens only, no raw colours)
  js/shell.js            top bar, nav, theme switch, DEMO banner, footer (injected on every page)
  js/votw-core.js        pure logic (CSV, index, rank, bins, bbox); unit-tested, runs in node too
  js/votw-charts.js      Votw.figure(): card, states, legend, table view, exports, Source footer; token->ECharts helpers
  js/specs-*.js          chart specs per page; js/page-*.js mount them
  data/                  demo.json, demo-*.csv (synthetic), geo/ (simplified boundaries, cities), capabilities.json
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
   { id: "my-chart", title: "States the finding", subtitle: "Measure, unit, years (synthetic)",
     source: { label: "Publisher, table", url: "https://...", meta: "access date etc." },   // required
     load: () => Votw.data.regions(),                 // async, may throw -> error state with Try again
     csv: (d) => ({ header: [...], rows: [...] }),    // feeds table view and CSV export
     build: (d, ctx) => Votw.base({ xAxis: Votw.catAxis([...]), yAxis: Votw.valueAxis(), series: [...] }),
     height: 340 }                                    // number or (width) => number
   ```
2. Mount it: `Votw.figure(document.getElementById("figures"), spec)`. Return `"empty"` from `build` to show the empty state.
3. Colours only through tokens: `Votw.placeColor("villages")`, `Votw.catColors()`, `Votw.mapRamp()`, `Votw.cssVar("--color-...")`. Never write a hex value. Charts redraw on theme change automatically because `build` is called again.
4. Missing `source` makes `Votw.figure` throw; `node scripts/check_footers.cjs <url>` fails if any card lacks the footer.
5. Add the capability to `data/capabilities.json` if it is new.

For real data later replace `Votw.DEMO_SOURCE` with the real source (publisher, table code, access date) and remove the DEMO tag in `votw-charts.js`.

## Checks
```
python3 -m unittest discover -s tests                 # generator determinism, flags, matrix completeness
node --test tests/core.test.js                        # core logic
python3 -m http.server 8000 &                         # then, with playwright installed (NODE_PATH) and optional CHROMIUM_PATH:
node scripts/check_footers.cjs http://localhost:8000
node scripts/verify_site.cjs http://localhost:8000 docs/verification
python3 scripts/make_demo_data.py                     # regenerate the synthetic data (deterministic)
```
`verify_site.cjs` checks 7 pages at 375, 768 and 1280 px (console errors, failed requests, horizontal scroll, Source footer, DEMO tag), then tooltip, table view, CSV/SVG/PNG export, dark theme, play, filter, brush, zoom, shape morph, map drill-down, zoom to region, touch taps and the blocked-data failure path with recovery. Results: `docs/verification/results.json`.

## Notes
- Language: page text is English; the design system's "Źródło:" footer label is shown as "Source:" here (issue text). `vendor/design/components.js` still has some Polish aria labels (play button, menu); they are part of the design system copy.
- Library problems and workarounds are listed in the PR and summarised in `data/capabilities.json` notes.
