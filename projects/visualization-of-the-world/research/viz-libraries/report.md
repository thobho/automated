# Choosing the JavaScript visualization library (issue #12)

Research date: 2026-10-28. Every fact carries a source key `[S#]` listed with URL and access date in [sources.md](sources.md). "Not found" / "not researched" is written where I did not verify something. Scores are my judgements; the evidence behind each is in this report.

## 1. Recommendation

**Use Apache ECharts 6.1.0 (Apache-2.0) as the one library for charts and the Poland choropleth.** [S1][S35]

| Item | Value |
|---|---|
| Library | Apache ECharts, npm `echarts`, version **6.1.0**, released 2026-05-19 [S1] |
| Licence | **Apache-2.0**, free for commercial use, no branding requirement [S1][S35] |
| Build step | **None needed.** The UMD file `dist/echarts.min.js` (1,122 KB raw, 368 KB gzip) loads with a plain `<script>`; it is vendored in `test-charts/vendor/echarts-6.1.0.min.js` and the three test pages run from `python3 -m http.server` [S48] |
| Maps | The `map` series and `geo` component take GeoJSON through `echarts.registerMap` [S75]; no second map library is needed for a choropleth with bubbles and drill-down on top. Add **MapLibre GL JS 6.16.0 (BSD-3-Clause)** only if the owner wants a real basemap (streets, satellite, vector tiles) or very large point layers; it is ESM-only in v6, which still works without a build step through `<script type="module">` [S13][S66] |
| Runner-up | **D3 7.9.0 (ISC) + Observable Plot 0.6.17 (ISC)**, no build step, 489 KB raw / 161 KB gzip together [S2][S3][S49][S50]. Choose it if the design system needs pixel-level custom marks and the owner accepts writing legends, toggles and animation by hand |

Why ECharts: it scored highest of the libraries that are free for commercial use and can draw both charts and maps (86/100, see section 4); it was the only one of the three tested libraries that needed no workaround for GeoJSON polygons and that gave timeline playback, tooltips, legend toggling and zoom/pan out of the box (section 5); it has docs written for LLMs [S73] and a third-party MCP server [S80]; and it rendered 2,479 gminas in about 250-415 ms (section 5.3).

## 2. Method

1. Candidates: the ten named in the issue (ECharts, D3 with Observable Plot, Vega / Vega-Lite, Plotly.js, Highcharts, Chart.js, amCharts, deck.gl, MapLibre GL JS, Leaflet, OpenLayers). I added no others: nothing in the evidence pointed at a missing candidate, and `chartjs-chart-geo` is covered under Chart.js [S17].
2. Facts (version, date, licence, stars, issues, downloads) come from the npm registry, npm downloads API and GitHub API on 2026-10-28; bundle sizes are measured by me on the exact files in the sources (`wc -c`, `gzip -9`) [S1-S65]. GitHub "open issues" counts include pull requests.
3. **Gate before scoring:** free for commercial use on a public website without mandatory branding and without paid licence. Highcharts fails (public websites need a paid SaaS licence; the CDN is for evaluation) [S67][S69]. amCharts fails (free only while its logo stays visible; removing it needs a commercial licence) [S70][S71]. Both are scored for information but are not recommended. I did not obtain or use trial licences.
4. **Map-only libraries** (deck.gl, MapLibre, Leaflet, OpenLayers) cannot draw the line and bar tests, so they cannot be the single library. They are compared on maps and may be the "second library".
5. The top 3 for own tests were chosen from the pre-test matrix among libraries that pass the gate and can draw charts and maps: **ECharts, Vega-Lite (with Vega), D3 + Plot**. Plotly.js (72) was fourth; its 1.5 MB gzip bundle was the deciding disadvantage [S54].
6. Own test: the same three charts per library (section 5), served over HTTP, loaded in headless Chromium by scripts in `test-charts/scripts/`, screenshots at 375 px and desktop.

## 3. Comparison of 13 libraries and packages (11 scored options)

### 3.1 Facts (npm, GitHub, measured bundle)

| Library | npm latest | Released | Licence | Stars | Open issues+PRs | Last push | Weekly npm downloads | Bundle raw / gzip (KB) | Sources |
|---|---|---|---|---|---|---|---|---|---|
| Apache ECharts | 6.1.0 | 2026-05-19 | Apache-2.0 | 67,622 | 1,488 | 2026-10-13 | 7,305,478 | 1122 / 368 | [S1],[S18],[S35],[S48] |
| D3 | 7.9.0 | 2024-03-12 | ISC | 113,818 | 22 | 2026-10-21 | 25,016,419 | 280 / 92 | [S2],[S19],[S36],[S49] |
| Observable Plot | 0.6.17 | 2025-02-14 | ISC | 5,415 | 350 | 2026-09-01 | 1,005,477 | 209 / 69 | [S3],[S20],[S37],[S50] |
| Vega | 6.4.0 | 2026-08-14 | BSD-3-Clause | 12,027 | 483 | 2026-10-20 | 1,502,715 | 521 / 180 | [S4],[S21],[S38],[S51] |
| Vega-Lite | 6.5.0 | 2026-10-08 | BSD-3-Clause | 5,534 | 822 | 2026-10-28 | 1,441,966 | 258 / 82 | [S5],[S22],[S39],[S52] |
| Plotly.js | 4.1.2 | 2026-10-05 | MIT | 18,369 | 805 | 2026-10-27 | 754,703 | 4834 / 1476 | [S7],[S24],[S40],[S54] |
| Highcharts | 13.1.1 | 2026-09-20 | Commercial (npm field is a licence URL) | 12,498 | 750 | 2026-10-28 | 2,808,832 | 280 / 102 | [S9],[S26],[S41],[S55] |
| Chart.js | 4.6.1 | 2026-10-22 | MIT | 67,767 | 631 | 2026-10-23 | 13,904,303 | 210 / 71 | [S10],[S27],[S42],[S57] |
| amCharts 5 | 5.21.5 | 2026-10-26 | Custom linkware (npm: SEE LICENSE IN LICENSE) | 449 | 22 | 2026-10-26 | 382,986 | not measured | [S11],[S28],[S43],[S58] |
| deck.gl | 9.4.0 | 2026-09-05 | MIT | 14,713 | 610 | 2026-10-28 | 231,561 | 2073 / 575 | [S12],[S29],[S44],[S60] |
| MapLibre GL JS | 6.16.0 | 2026-10-25 | BSD-3-Clause | 11,966 | 297 | 2026-10-28 | 7,266,811 | 1627 / 442 | [S13],[S30],[S45],[S61],[S62] |
| Leaflet | 1.9.4 | 2023-05-18 | BSD-2-Clause | 45,788 | 433 | 2026-10-28 | 9,101,965 | 148 / 42 | [S14],[S31],[S46],[S63] |
| OpenLayers | 10.11.0 | 2026-10-04 | BSD-2-Clause | 12,639 | 879 | 2026-10-26 | 922,215 | 1071 / 298 | [S15],[S32],[S47],[S64] |

Reading notes: Highcharts bundle is the core only; the map module adds 86 KB raw / 30 KB gzip [S56]. amCharts 5 ships as many modules behind a loader; size not measured [S58][S59]. MapLibre 6.16.0 is main bundle plus worker (1,108 + 519 KB raw) [S61][S62]. Vega-Lite needs Vega and usually vega-embed: 839 KB raw / 282 KB gzip together [S51][S52][S53]. Releases in the 12 months before 2026-10-28 (stable x.y.z only, from the npm registry [S1-S15]): echarts 1, d3 0, plot 0, vega 4, vega-lite 3, plotly.js 12, highcharts 10, chart.js 1, amcharts5 33, deck.gl 22, maplibre-gl 38, leaflet 0, ol 7. Leaflet's last stable release is 1.9.4 from 2023-05-18; 2.0 is alpha only [S14][S90].

### 3.2 Features and agent evidence

| Library | Rendering and formats (as far as researched) | Maps | Agent-friendliness evidence |
|---|---|---|---|
| ECharts | Canvas or SVG renderer, SVG string for server-side rendering [S75][S76]; PNG via `getDataURL` [S76]; option docs list timeline, dataZoom, brush, aria, geo, `connect` for linked charts [S74][S75][S78]; `universalTransition` for animated morphs [S77] | `map` series + `geo` component, `registerMap(name, geoJSON)`; region join by `properties.name` or `nameProperty` [S75] | `llms.txt` with markdown docs [S73]; third-party MCP server `mcp-echarts` (MIT, 270 stars) [S80]; no LLM benchmark covering ECharts found [S100] |
| D3 + Plot | SVG output (own test); GeoJSON used directly; TopoJSON via `topojson-client` [S16] | `Plot.geo` with projections, `tip`, fill from feature properties [S96] | No `llms.txt` at d3js.org (404) [S99]; Plot docs site returned HTTP 429, so its `llms.txt` could not be checked [S97][S98]; no benchmark found [S100] |
| Vega-Lite + Vega | TSV data in the official example [S91]; own test loaded JSON, GeoJSON and TopoJSON; SVG and canvas renderers (own test) | `geoshape` + `lookup` join [S91][S94]; own test: TopoJSON worked, GeoJSON drew a solid fill | Declarative JSON suits generation; evidence: a 1,981-spec Vega-Lite dataset and the VisEval and VegaChat papers (found in search, not read in full) [S101][S102][S103]; no `llms.txt` [S99] |
| Plotly.js | Not researched beyond maps and animation | `choropleth` trace has `geojson` and `featureidkey` [S84] | `llms.txt` exists but is marketing/Dash content [S82]; a UPC study reports 76.8% success with Plotly, the best of three libraries, for GPT-4o (from a search summary; PDF not parsed) [S100] |
| Highcharts | Not researched (gate failed) | Maps product with a map collection [S69] | `llms.txt` 404 [S99] |
| Chart.js | Canvas only [S86]; tree-shaking supported [S86] | No built-in maps; plugin `chartjs-chart-geo` 4.3.6, MIT [S17] | `llms.txt` 404 [S99] |
| amCharts 5 | Canvas default, SVG option [S71] | Choropleth, bubble, drill-down, separate geodata package [S71] | `llms.txt` and 418 KB `llms-full.txt`, agent notes inside the npm package from 5.21.0 [S71][S72] |
| deck.gl | Not researched | Map layers (map only) | `llms.txt` [S89] |
| MapLibre GL JS | Not researched | Fill layer from GeoJSON, feature-state hover, clustering [S87]; basemap tiles not required by those examples but not confirmed | `llms.txt` [S88] |
| Leaflet | Not researched | Not researched in this task | `llms.txt` 404 [S99] |
| OpenLayers | Not researched | Not researched in this task | `llms.txt` 404 [S99] |

Benchmark evidence overall is thin: the only multi-library result I found is the UPC study (3 libraries, GPT-4o 64.7% average) [S100]; benchmarks I found concentrate on Vega-Lite, matplotlib and Plotly; nothing covers ECharts, D3 or Chart.js head to head. Our own test (section 5) is therefore the main evidence.

## 4. Criteria, weights and scoring

Weights sum to 100 and reflect the site goal "beautiful, dynamic, Poland-focused, built by an agent, static hosting":

| Criterion | Weight | Why |
|---|---|---|
| Maps (choropleth, points, drill-down, ~2,500 shapes) | 20 | Every series task is geographic; voivodeship to powiat to gmina is the core interaction |
| Visual polish and styling | 15 | The site's value is how it looks; must fit a custom design system |
| Dynamic features (animation, timeline, tooltips, zoom, brushing, linked views) | 15 | "Dynamic" is in the brief; time series 2000-2025 need playback |
| Agent-friendliness | 10 | The site is built and maintained by an agent; wrong first attempts cost tokens |
| Input/output formats | 8 | CSV/JSON/GeoJSON/TopoJSON in, SVG/PNG/data out |
| Licence | 8 | Must be free for commercial use; failing the gate is disqualifying, the weight only separates the rest |
| Docs and community | 7 | Fewer dead ends |
| Maintenance health | 7 | Release cadence, activity |
| Bundle size and no-build | 5 | Static hosting, phone users; deliberately low because a 300 KB gzip file is acceptable |
| Accessibility, touch, mobile | 5 | Needed, but all candidates are similar and evidence is thin |

Score 0-5 per criterion, total = sum(score x weight) / 5. Matrix (also produced by `python3 scripts/scoring.py`, weights tested in `tests/`):

| Library | Visual polish and styling (15) | Dynamic features (15) | Maps (choropleth, points, drill-down, 2.5k shapes) (20) | Input/output formats (8) | Docs and community (7) | Agent-friendliness (10) | Licence (8) | Maintenance health (7) | Bundle size and no-build (5) | Accessibility, touch, mobile (5) | Total /100 | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MapLibre GL JS | 5 | 4 | 5 | 4 | 4 | 3 | 5 | 5 | 3 | 4 | 87 | map only |
| amCharts 5 | 5 | 5 | 5 | 4 | 4 | 4 | 2 | 5 | 3 | 3 | 86 | FAILS gate: free tier forces the amCharts logo |
| Apache ECharts | 4 | 5 | 4 | 4 | 4 | 5 | 5 | 4 | 3 | 4 | 86 |  |
| Vega-Lite (+Vega) | 3 | 4 | 4 | 5 | 4 | 4 | 5 | 5 | 3 | 3 | 80 |  |
| OpenLayers | 3 | 3 | 5 | 5 | 4 | 3 | 5 | 5 | 2 | 3 | 78 | map only |
| Highcharts | 5 | 4 | 4 | 4 | 5 | 3 | 0 | 5 | 4 | 4 | 77 | FAILS gate: paid licence for public websites |
| deck.gl | 4 | 4 | 4 | 4 | 4 | 3 | 5 | 5 | 1 | 2 | 76 | map only |
| D3 + Observable Plot | 4 | 3 | 4 | 5 | 4 | 3 | 5 | 3 | 4 | 3 | 76 |  |
| Leaflet | 3 | 3 | 4 | 4 | 5 | 4 | 5 | 2 | 5 | 4 | 75 | map only |
| Plotly.js | 3 | 4 | 3 | 3 | 5 | 4 | 5 | 5 | 1 | 3 | 72 |  |
| Chart.js | 3 | 3 | 1 | 3 | 4 | 4 | 5 | 4 | 5 | 2 | 61 |  |

Highest scores per group: ECharts leads among libraries that can draw charts and maps and pass the gate. MapLibre's 87 is for maps only. Where I gave a score without researching a sub-criterion in this task (Plotly formats, deck.gl, Leaflet, OpenLayers details), the score is a judgement from general reputation and the facts in section 3.1, and is the least reliable part of the matrix; it does not affect the top 3 choice because those libraries cannot be the single library or rank below the three tested.

## 5. Own test: three charts, top three libraries

Pages: `test-charts/<library>/{line,bar-animation,choropleth}.html`. Shared synthetic data `shared/demo-data.json` (generated by `shared/make_demo_data.py`, every label says DEMO) and the PRG voivodeship boundaries from PR #19 (`shared/voivodeships.geojson/.topojson`, simplified, PRG/GUGiK) [S104]. Libraries are vendored in `test-charts/vendor/` at pinned versions. Honesty note: I worked from the official docs and example files for API details (ECharts API markdown, Plot's geo.md, Vega-Lite example specs) [S75][S91][S92][S93][S96], but I also have prior knowledge of these libraries, so the attempt counts are a floor for a cold agent. Observable's docs site rate-limited me (HTTP 429), so Plot docs were read from the GitHub markdown source [S96][S97].

### 5.1 Attempts log

An attempt = one full write/run/inspect cycle. "Correct" = the chart renders, the requested interactions work and a screenshot looks right.

| Library | Chart | Attempts | What went wrong | Console errors | Fix |
|---|---|---|---|---|---|
| ECharts 6.1.0 | 1 Line, 3 series, tooltip, legend toggle | 1 | nothing | none | - |
| ECharts | 2 Stacked bar + year animation | 2 | Attempt 1: my fixed `yAxis.max: 100` clipped bars (stack sums reach 174); year title overlapped the legend when it wrapped at 375 px. Found only by looking at the screenshot | none | `max: 180`, title and grid moved down |
| ECharts | 3 Choropleth, 16 voivodeships | 1 | nothing; `properties.name` joins data to regions [S75]; no ring-winding fix needed | none | - |
| D3 7.9.0 + Plot 0.6.17 | 1 Line | 1 | nothing; legend toggle is custom checkboxes that re-render Plot (I found no built-in legend toggle in the docs I read: not exhaustive) | none | - |
| D3 + Plot | 2 Stacked bar + animation | 1 | works, but Plot has no animation API in what I used: I wrote a play button, slider and a 500 ms tween that re-renders the SVG each frame (about 20 lines) | none | - |
| D3 + Plot | 3 Choropleth | 2 | Attempt 1: the whole plot area was one solid colour, no error. GeoJSON outer rings follow RFC 7946 (counter-clockwise) while d3-geo expects clockwise, so each polygon is read as "everything except Poland" | none (silent) | reverse rings when `d3.geoArea(f) > 2*Math.PI`. The 2,479-gmina TopoJSON page needed no fix when loaded through `topojson-client` |
| Vega-Lite 6.5.0 + Vega 6.4.0 + vega-embed 7.3.0 | 1 Line | 2 | Attempt 1: chart correct but page overflowed 8 px horizontally at 375 px (`width: "container"` measured the padded parent) | none | removed padding on the container |
| Vega-Lite | 2 Stacked bar + animation | 4 | Attempts 1-3: blank chart, no error, no axes visible; the SVG content was translated 7,248 px off screen. Cause: the compiled spec stacks across all years and applies the animation filter afterwards (`data_0_curr`), so bars were thousands of units tall. 1: stack in the encoding; 2: dropped `aggregate`; 3: explicit `stack` transform grouped by `group` only; all still blank | none (silent) | Attempt 4: explicit `stack` transform grouped by `group` **and** `year`, y/y2 from its output. Built-in `time` channel + `timer` selection then animates [S92]. Note there is no year label in the chart by default |
| Vega-Lite | 3 Choropleth | 2 | Attempt 1: `format: {type: "json", property: "features"}` on the GeoJSON gave a solid-colour rectangle, no error (same winding cause as Plot). | none (silent) | Attempt 2: load `voivodeships.topojson` with `format: {type: "topojson", feature: "voivodeships"}`; correct. Also, a failed data load is only logged by Vega and leaves a blank chart, so I wrapped the loader to show an error message |

Totals (attempts across the 3 charts): ECharts 4, D3 + Plot 4, Vega-Lite 8. Three of the five failures were silent (no console error, just a wrong picture), so any agent workflow must screenshot, not only read the console.

### 5.2 Results per interaction (headless Chromium, 375 px, `scripts/check_interactions.cjs`)

| Check | ECharts | D3 + Plot | Vega-Lite |
|---|---|---|---|
| Tooltip on line chart | yes, shared tooltip lists all 3 series | yes, nearest point only | yes, nearest point (point marks) |
| Legend toggle | built in (click legend; series state false confirmed) | custom checkbox code | built in (`bind: "legend"` selection) |
| Stacked bar animates without input | yes, built-in timeline with play/pause and slider | yes, custom tween | yes, built-in `timer` + `time` channel |
| Choropleth tooltip and hover highlight | yes, plus roam (zoom/pan) | yes, tooltip only | yes, tooltip only |
| Console errors/warnings, final pages | 0 | 0 | 0 |
| Horizontal overflow at 375 px, final pages | 0 px | 0 px | 0 px |
| Failure path (data files blocked) | message shown | message shown | message shown (needed loader wrapper for the choropleth) |

Evidence files: [check-pages.json](../../docs/verification/viz-libraries/check-pages.json), [interactions.json](../../docs/verification/viz-libraries/interactions.json); screenshots in `test-charts/<library>/screenshots/` (`*-375.png` mobile, `*-desktop.jpg`, `*-tooltip-375.png`, `line-legend-toggled-375.png`).

### 5.3 Performance with about 2,500 shapes

All 2,479 gminas as a choropleth (`test-charts/perf/`, 3 runs each, headless Chromium on this Mac, time from parsed data to first render; not a rigorous benchmark) [S104]:

| Library | Runs (ms) | DOM nodes |
|---|---|---|
| ECharts (canvas) | 247, 415, 259 | canvas |
| D3 + Plot (SVG) | 249, 175, 264 | 2,481 |
| Vega-Lite (SVG) | 465, 449, 438 | 2,486 |
| Vega-Lite (canvas) | 375, 365, 390 | canvas |

All three are fine at this size. Raw timings are in [perf-2479-gminas.json](../../docs/verification/viz-libraries/perf-2479-gminas.json). ECharts needed `nameProperty: "teryt"` because gmina names are not unique; that worked first time.

### 5.4 What the tests say

- ECharts needed the least code for the interactions the brief asks for (timeline, legend, tooltip, zoom). Its look is polished by default but ECharts-recognisable; custom themes exist (not tested here).
- D3 + Plot gives the cleanest, most designable SVG and smaller files, but every interaction beyond a tooltip is code we write and maintain.
- Vega-Lite is declarative and compact for choropleth and linked views, but its new animation feature interacted badly with stacking and failed silently; the gotchas cost 8 attempts.

## 6. Risks

1. **ECharts GeoJSON name join:** regions join by `properties.name` unless `nameProperty` is set; non-unique names (gminas) must use the TERYT code [S75]. Mitigation: always set `nameProperty: "teryt"`.
2. **Large bundle:** 368 KB gzip for the full build. Mitigation: later optional custom build (needs a build step) or accept; it is cached and fine on phones for a dashboard.
3. **Few stable releases:** 1 stable ECharts release in 12 months (v6.1.0 on 2026-05-19) and 1,488 open issues+PRs [S1][S35]. Pin the version; vendor the file.
4. **Canvas accessibility:** canvas charts are weaker for screen readers; ECharts has an `aria` option that generates text descriptions [S78] but I did not test it. Provide data tables next to charts.
5. **No real basemap:** a choropleth of administrative areas does not need tiles. If a street basemap is wanted, a second library (MapLibre) and a tile provider (cost, terms) come in.
6. **Winding order:** GeoJSON through d3-geo/Vega (the runner-up path) silently fills the map; prefer TopoJSON there, or rewind.
7. **Evidence gaps:** no LLM benchmark covers ECharts; agent-friendliness is based on `llms.txt`, MCP availability and my test, not on measured pass rates.
8. **Mapshaper-simplified boundaries** (PR #19) are fine for the tests; very high zoom on gminas needs the detail level decision of the geography task.

## 7. Open questions for the owner

1. Does the site need a real basemap (streets, satellite, terrain), or are plain administrative shapes enough? If a basemap, approve adding MapLibre GL JS and choose a tile provider (may involve cost).
2. Is a ~370 KB gzip full ECharts bundle acceptable, or should a later task build a trimmed custom bundle (introduces a build step)?
3. Should the design system target ECharts themes (JSON theme files), or is pixel-level control of D3 + Plot worth the extra code?
4. Accept ECharts' Apache-2.0 notice requirement (NOTICE/licence file must ship with the vendored copy)? I did not verify the exact attribution wording in this task.
5. Are Highcharts or amCharts commercial licences of any interest? Both were excluded by the free-use gate and I did not request trial licences.

## 8. Limits of this research

- Plotly.js, Highcharts, Chart.js, amCharts, deck.gl, MapLibre, Leaflet and OpenLayers were researched from registries, licences, `llms.txt` and a few docs pages only; none of them was built into test pages.
- Drill-down (region to powiat to gmina) was not built; performance of 2,479 shapes was measured, interaction latency was not.
- Touch behaviour was tested only through Chromium at a 375 px viewport with mouse events, not on a physical phone.
- PNG/data export was not exercised in the tests; it is mentioned only where documented [S76].
- Benchmark evidence comes from search results, not full papers [S100]-[S103].
