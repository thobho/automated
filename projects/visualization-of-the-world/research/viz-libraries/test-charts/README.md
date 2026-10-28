# Test charts (issue #12)

Three charts per library (line + legend toggle, stacked bar + year animation, voivodeship choropleth) for ECharts, D3 + Plot and Vega-Lite, plus a 2,479-gmina performance page. Findings: [../report.md](../report.md).

```
cd projects/visualization-of-the-world/research/viz-libraries/test-charts
python3 -m http.server 8712        # then open http://localhost:8712/echarts/line.html etc.
```

- `shared/demo-data.json`: SYNTHETIC data (generator: `shared/make_demo_data.py`). Not real statistics.
- `shared/voivodeships.geojson|topojson`, `shared/gminas.topojson`: simplified PRG/GUGiK boundaries copied from PR #19 (branch `agent/13-poland-geography`); the geography task owns the originals.
- `vendor/`: pinned minified libraries, see its README.
- `scripts/`: Playwright checks (`npm i playwright`, then `node scripts/check_pages.cjs http://localhost:8712 out.json`; also `check_interactions.cjs`, `check_failure.cjs`, `check_perf.cjs`). Set `CHROMIUM_PATH` to use an existing Chromium.
- `<library>/screenshots/`: 375 px PNGs and desktop JPEGs produced by those scripts.
