# visualization-of-the-world

Phase 1: data research for a later visualization of the world. Independent project: do not import code from other projects. Research only - no web pages, dashboards or styled charts until a task says so (exception: the design system in `design/`, issue #14).

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
