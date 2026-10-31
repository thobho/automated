# Sources for the demo site

Accessed 2026-10-29. HTTP status of each page was checked with `curl -L` (200). The pages are rendered by JavaScript, so a `#anchor` in a URL was **not** verified to exist; the page itself was.

| Fact | Source |
|---|---|
| Library choice: Apache ECharts 6.1.0, Apache-2.0, released 2026-05-19, UMD build needs no build step | `../research/viz-libraries/report.md` section 1 (npm registry https://registry.npmjs.org/echarts, accessed 2026-10-28) |
| ECharts option reference (series, geo, visualMap, dataZoom, brush, tooltip, timeline, toolbox) | https://echarts.apache.org/en/option.html |
| ECharts API (registerMap, getDataURL, resize, connect, renderToSVGString) | https://echarts.apache.org/en/api.html |
| Server-side (SSR) SVG rendering used for SVG export | https://echarts.apache.org/handbook/en/how-to/cross-platform/server/ |
| Dynamic data and animation | https://echarts.apache.org/handbook/en/how-to/data/dynamic-data/ , https://echarts.apache.org/handbook/en/how-to/animation/transition/ |
| Dataset concept (CSV is not read by the library) | https://echarts.apache.org/handbook/en/concepts/dataset |
| Accessibility (aria) | https://echarts.apache.org/handbook/en/best-practices/aria/ |
| Importing / UMD use | https://echarts.apache.org/handbook/en/basics/import |
| topojson-client 3.1.0 (ISC), vendored copy of the jsDelivr build | https://github.com/topojson/topojson-client ; file origin in `../research/viz-libraries/test-charts/vendor/README.md` |
| Boundaries (voivodeships, powiats), city points and names, TERYT codes | `../research/poland-geography/` (sources.csv S1 PRG/GUGiK https://www.geoportal.gov.pl/pl/dane/panstwowy-rejestr-granic-prg/ ; S4 GeoNames CC BY https://www.geonames.org). Simplified copies in `data/geo/` |
| Design system (tokens, components, fonts: SIL OFL) | `../design/` ; copies in `vendor/design/` |
| TERYT convention used by the generator: powiat codes 61 and above are cities with powiat rights | Not verified against a primary source in this task; it only decides which synthetic powiats get a low village share and has no effect on any real number |

**The demo pages (`index.html`, `charts.html`, `interaction.html`, `maps.html`, `formats.html`, `polish.html`, `matrix.html`) show synthetic numbers** (`scripts/make_demo_data.py`, seed 15). None of those is a statistic.

**`real.html` shows real numbers only.** Its data is `data/real/*.csv`, copied verbatim from `../research/poland-demography-housing/data/processed/`; each chart footer names the source ids (S1, S15, S29-S32, S41-S44) registered in [`../research/poland-demography-housing/sources.csv`](../research/poland-demography-housing/sources.csv) (GUS BDL and Eurostat, accessed 2026-10-29). Housing splits for 2000-2008 are proxies and are labelled as such.
