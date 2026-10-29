# Sources (design system)

All accessed **2026-10-29**. Font facts come from the npm registry (`npm view`) and from the `metadata.json` and `LICENSE` files inside each downloaded package. Upstream repository links are the ones printed in those licence files; I did not open the upstream repositories themselves.

## Fonts

All four: npm package version **5.3.0**, published to npm 2026-07-19, licence **OFL-1.1** (SIL Open Font License 1.1; full text in `fonts/OFL-*.txt`). Fontsource packages Google Fonts files (`metadata.json` field `source`: https://github.com/google/fonts). Files copied: `*-latin-wght-normal.woff2` and `*-latin-ext-wght-normal.woff2` (variable weight axis, normal style only), unchanged.

| Key | Family | Upstream font version (Fontsource metadata) | Download (npm tarball) | Upstream project | Files (bytes) | SHA-256 (latin / latin-ext) |
|---|---|---|---|---|---|---|
| F1 | Public Sans | v21, modified 2025-09-16 | https://registry.npmjs.org/@fontsource-variable/public-sans/-/public-sans-5.3.0.tgz | https://github.com/uswds/public-sans | 26,832 + 18,472 | `5ed4d31c…6de90d68` / `3a00a32f…4e79586a` |
| F2 | Schibsted Grotesk | v7, modified 2025-09-05 | https://registry.npmjs.org/@fontsource-variable/schibsted-grotesk/-/schibsted-grotesk-5.3.0.tgz | https://github.com/schibsted/schibsted-grotesk | 46,752 + 20,924 | `4c8b93f4…d8a75e05` / `ee9eeb23…abdb2936` |
| F3 | IBM Plex Sans | v23, modified 2025-09-08 | https://registry.npmjs.org/@fontsource-variable/ibm-plex-sans/-/ibm-plex-sans-5.3.0.tgz | not stated in the licence file (copyright IBM Corp.) | 45,712 + 30,964 | `e2291e84…4a859470` / `d160e209…75aa2f81` |
| F4 | Atkinson Hyperlegible Next | v7, modified 2025-09-05 | https://registry.npmjs.org/@fontsource-variable/atkinson-hyperlegible-next/-/atkinson-hyperlegible-next-5.3.0.tgz | https://github.com/googlefonts/atkinson-hyperlegible-next | 33,996 + 19,092 | `18b2a1a3…e0e1bbaf` / `7dae0c6c…f4dd93f3` |

- Fontsource package pages: https://www.npmjs.com/package/@fontsource-variable/public-sans (and the same pattern for the other three).
- `unicode-range` values in `tokens.css` are copied from each package's `wght.css`. "ó" is in the latin file; "ą ć ę ł ń ś ź ż" are in latin-ext.
- Polish glyph coverage and tabular figures were **verified in Chromium**, not taken from documentation: `scripts/verify_page.cjs` checks `document.fonts.check()` with `ąćęłńóśźżĄĆĘŁŃÓŚŹŻ` for all four families and measures that tabular `1111111` and `8808080` have equal width (`docs/verification/results.json`).

## Colour and accessibility methods

| Key | What | URL |
|---|---|---|
| C1 | WCAG 2.2 contrast ratio and relative luminance (SC 1.4.3 text 4.5:1, SC 1.4.11 non-text 3:1) | https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio |
| C2 | WCAG 2.2 SC 2.5.8 target size (minimum); we use 44 px as in SC 2.5.5 | https://www.w3.org/TR/WCAG22/#target-size-minimum |
| C3 | OKLab / OKLCH colour space (Ottosson) | https://bottosson.github.io/posts/oklab/ |
| C4 | Machado, Oliveira & Fernandes (2009), CVD simulation matrices (severity 1.0) | https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html |
| C5 | Categorical, sequential (blue), status palettes, thresholds (CVD dE >= 8, normal >= 15, L band, chroma floor) | Claude Code `dataviz` skill, `references/palette.md` and `scripts/validate_palette.js` (bundled skill, no public URL). Our Python port reproduces its numbers (unit test `test_delta_e_matches_dataviz_validator`) |

## Chart library

The site's chart library (ECharts 6.1.0) was chosen in `../research/viz-libraries/report.md`; see its `sources.md`.
