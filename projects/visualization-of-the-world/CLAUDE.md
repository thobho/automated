# visualization-of-the-world

Phase 1: data research for a later visualization of the world. Independent project: do not import code from other projects. Research only - no web pages, dashboards or styled charts until a task says so (exceptions: the design system in `design/`, issue #14, and the demo site in `site/`, issue #15; see `site/README.md`).

## Rules
- **Every number needs a source.** Each topic has `sources.csv` (`id,title,publisher,url,indicator_or_table_code,accessed,type,notes`; type = primary or secondary). Every data file has a `source_id` column; report text cites with keys like `[S3]`.
- **Primary sources first** (GUS BDL, Rocznik Demograficzny, censuses, Eurostat, UN WPP, OECD, World Bank). Articles/analyses are `secondary`: use them for interpretation, never as the origin of a number when a primary source exists.
- **No invention.** Never fill gaps or estimate silently. Missing values are empty and flagged; derived values are marked `derived` with formula and input source ids.
- **Layout:** research files go under `research/<topic>/` (`README.md`, `sources.csv`, `data/raw`, `data/processed`, `scripts/`, `reports/`).
- **Scripts:** Python 3 standard library only. Raw downloads are cached by scripts, throttled (BDL anonymous limit is 100 requests / 15 min).
- **Checks:** `python3 research/<topic>/scripts/check_sources.py` must pass; tests: `python3 -m unittest discover -s research/<topic>/tests`.
- Keep PRs small enough to review on a phone: data in CSV, short README sections.

## Design system (`design/`)
- `design/tokens.json` is the source of truth; regenerate `tokens.css` with `python3 design/scripts/build_tokens.py`, never edit it by hand.
- Components and charts use only `var(--...)` tokens: no raw hex, no external font or script CDNs (fonts are self-hosted woff2 with OFL licences).
- Follow the colour, chart and "Źródło:" footer rules in `design/README.md`; every chart, map and table showing data cites its source.
- Checks: `python3 design/scripts/check_contrast.py`, `python3 design/scripts/build_tokens.py --check`, `python3 -m unittest discover -s design/tests`, browser check `node design/scripts/verify_page.cjs` (see the CI workflow `visualization-of-the-world-design.yml`).
- `design/sample/sample-data.json` is made up; never use it as data.

## Demo site (`site/`)
- Self-contained: served from `site/` with `python3 -m http.server`; copies of design files and geodata live in `site/vendor/` and `site/data/`. ECharts 6.1.0 is pinned and vendored.
- All numbers on the site are synthetic and labelled "DEMO DATA, NOT REAL". Never put real statistics in `site/data/demo*`.
- Every chart goes through `Votw.figure()` (Source footer mandatory). Checks: `node --test site/tests/core.test.js`, `python3 -m unittest discover -s site/tests`, `node site/scripts/check_footers.cjs <url>`, `node site/scripts/verify_site.cjs <url> <out>`.

## Visualization Playbook

### Rules for Creating Visualizations

1. **Use templates first**: Always start with a template from `site/templates/` rather than creating from scratch
2. **Pinned versions only**: Never use CDNs; always use vendored libraries with pinned versions
3. **Tokens only**: Use only CSS variables from the design system (`var(--...)`); never hardcode colors or measurements
4. **Every number sourced**: All data must have a proper source with URL and access date
5. **Demo data labeled**: Any synthetic data must be clearly marked as "DEMO DATA, NOT REAL"

### Common Pitfalls and Fixes

Based on issues encountered in the demo site (#15) and library evaluation (#12):

1. **Empty charts not handled properly**
   - *Problem*: Charts showing no data don't provide user feedback
   - *Fix*: Always implement `emptyMsg` property in spec and use appropriate empty state UI components

2. **Missing Source footers**
   - *Problem*: Charts without proper source attribution fail accessibility and credibility standards
   - *Fix*: Ensure every `spec.source` object includes `label`, `url`, and `meta` properties

3. **Poor mobile responsiveness**
   - *Problem*: Charts don't adapt well to small screens
   - *Fix*: Use responsive `height` functions and adjust axis labeling for mobile

4. **Inaccessible color contrast**
   - *Problem*: Text and chart elements don't meet AA contrast requirements
   - *Fix*: Use the design system tokens which are pre-checked for contrast

5. **Missing alt/aria attributes**
   - *Problem*: Charts aren't accessible to screen readers
   - *Fix*: Always include proper `aria-label` attributes on chart containers

6. **Console errors breaking user experience**
   - *Problem*: JavaScript errors prevent charts from rendering
   - *Fix*: Implement proper error handling with try/catch and error state UI

7. **Horizontal scroll on mobile**
   - *Problem*: Pages aren't fully responsive at 375px width
   - *Fix*: Test thoroughly at 375px and adjust container widths and padding

### Prompt Snippets for Agents

When requesting visualizations, use these standardized prompts:

1. "Create a line chart showing trends over time using the line chart template"

2. "Build a bar chart comparing categories with proper source attribution"

3. "Make a choropleth map of regional data using the map template"

4. "Develop a chart with timeline controls using the timeline slider template"

5. "Implement a visualization with place-type filtering using the toggle template"

### Templates Reference

Templates are available in `site/templates/`:
- `chart-template.html` - Basic chart structure
- `line-chart-template.html` - Line chart with time series
- `bar-chart-template.html` - Bar chart for comparisons
- `stacked-chart-template.html` - Stacked area/bar charts
- `map-choropleth-template.html` - Geographic choropleth maps
- `map-bubbles-template.html` - Point data bubble maps
- `timeline-slider-template.html` - Charts with time playback controls
- `place-toggle-template.html` - Charts with place type filters
- `source-footer-template.html` - Proper source footer implementation

### Playbook Validation

See `PLAYBOOK-TEST-RESULTS.md` for test results demonstrating that:
- The playbook works correctly for creating valid charts
- The verification script detects both valid and invalid implementations
- All templates follow project standards and pass checks
