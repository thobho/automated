# Design system

The look of the visualization site: tokens, components and a style guide. Open `style-guide.html` through `python3 -m http.server` in this folder (it fetches `tokens.json` and sample data, so `file://` will not work).

| File | What it is |
|---|---|
| `tokens.json` | Source of truth: colours (3 directions x light/dark), data palettes, type, space, radius, shadow, motion, layout, contrast rules and accepted exceptions |
| `tokens.css` | CSS variables generated from `tokens.json` by `scripts/build_tokens.py`. Never edit by hand |
| `components.css` / `components.js` | Reusable components (no build step, no dependencies) |
| `style-guide.html` (+ `.css`, `.js`) | Every token and component on one page |
| `fonts/` | Self-hosted woff2 (latin + latin-ext) and their OFL licences |
| `sample/sample-data.json` | **Made-up** numbers for the demo charts. Never quote them |
| `scripts/check_contrast.py` | WCAG AA + colour-blind + ramp checks on `tokens.json`; exit 1 on failure |
| `scripts/verify_page.cjs` | Headless Chromium check of the style guide (errors, 375 px overflow, fonts, interactions, failure path) |

Checks: `python3 scripts/check_contrast.py`, `python3 scripts/build_tokens.py --check`, `python3 -m unittest discover -s tests`. CI runs them plus the browser check (`.github/workflows/visualization-of-the-world-design.yml`).

## How to switch the look
Classes on `<html>`: none = Bałtyk, light, or dark when the OS asks. `theme-light` / `theme-dark` force a theme. `dir-beton` / `dir-noc` switch to an alternative direction (both themes work there too). Components only ever use `var(--color-...)`, so nothing else changes.

## Rules for agents and humans
**Colour**
- Use semantic tokens (`--color-text-secondary`), never raw hex and never `--neutral-*` in components.
- Text: `text-primary` for content, `text-secondary` for subtitles and labels, `text-muted` only for help text and placeholders. All pass 4.5:1 on every background.
- Accent = interaction only (links, selected, primary button, focus, slider). Never a data colour, never decoration. One primary button per view.
- Status (`success/warning/danger/info`) only for messages, always icon + words.
- Page is `bg-page`; anything holding a chart sits on `bg-surface` (a card with `border-subtle`); `bg-sunken` for table headers, footers and empty states.

**Data colour** (shared by all directions so a chart means the same everywhere)
- Identity: categorical slots in fixed order (`--data-cat-1..8`). A 9th series goes to "Inne" or small multiples. Colour follows the entity, never its rank; filtering must not repaint survivors.
- Place type is fixed: big cities `--data-place-big-cities` (blue), small cities `--data-place-small-cities` (orange), villages `--data-place-villages` (aqua). These are slots 1-3, the only three that pass the colour-blind check on all pairs, so they can meet anywhere (maps, scatter).
- Magnitude: one hue, light to dark (`--data-seq-blue-*`). Maps: `--data-map-1..7` (flips in dark mode). Missing = hatched `map-nodata`, never a ramp colour and never 0.
- Change: `--data-div-1..7`, red = decrease, blue = increase, grey midpoint = no change.
- Light-mode aqua, yellow and magenta are below 3:1 on white: any chart using them must have direct labels or a table view (listed as exceptions in `tokens.json`).
- Text in charts uses text tokens, never the series colour.

**Typography**: display face for h1-h3, chart titles and big figures; text face for everything else. `.num` (tables get it automatically) for tabular figures wherever numbers align. Body text max `--measure` (38 rem). No italics for emphasis in headlines, no all-caps labels, no monospace.

**Space and shape**: 4 px base. Inside a component `--space-1..4`, between components `--space-4..6`, between sections `--space-7..9`. Radius: controls `md` (6 px), cards `lg` (10 px), data marks 4 px on the value end only; no pill shapes. Shadows only on floating things (tooltip `md`, menu `lg`).

**Motion**: `--dur-fast` for hover/state, `--dur-base` for panels, `--dur-slow` for chart transitions, `--dur-story` for story steps. All become 0 ms under `prefers-reduced-motion`; never animate without a token.

**Layout**: phone first, 4/8/12 columns at 0/600/960 px, max width 75 rem. Templates (shown in the style guide): landing, scroll-story chapter (sticky chart under the chapter nav), explorer (filters in one row above everything they change), map view (map first, details in a sheet or side panel).

**Charts**: title states the finding, subtitle the measure, unit and years. One value axis only. Hairline gridlines on the value axis, no vertical gridlines on time. Direct labels for up to 4 series plus a legend. Annotations as dashed 1 px rule + short text. Tooltip on hover and keyboard focus, table view for every chart. **Every chart, map and table that shows data ends with the `.chart-source` footer: "Źródło:" + publisher and table as a link + access date.** No source, no chart. The site will draw charts with ECharts (see `research/viz-libraries`); its theme must reproduce these rules.

**States and access**: every data view has loading (skeleton), empty (what is missing + reset) and error (what happened + retry) states. Targets at least 44 x 44 px, 2 px focus ring on `:focus-visible`, never colour alone, skip link first.

## Decisions and rejected alternatives
- **Chosen: Bałtyk.** White `#ffffff` / blue-black `#0d1418` page, sea-teal accent `#0a6c74` / `#4fc1c8`, Schibsted Grotesk (headings, built for a news publisher) + Public Sans (text, neutral, wide language support, tabular figures). It is the calmest of the three and leaves all colour to the data, which matters on a site that is mostly charts.
- **Rejected for now: Beton** (`#e4e8eb` concrete page, brick `#b03a1e`, IBM Plex Sans). Strong identity, but the grey page lowers chart contrast and the brick accent sits close to the red data arm. Kept as `dir-beton`.
- **Rejected for now: Noc** (`#e7edf6` / navy `#0a1628`, raspberry `#a8235a`, Atkinson Hyperlegible Next). Very legible, best dark mode, but the tinted page and pink accent feel louder than "calm"; Atkinson's slashed zero is distinctive in big figures. Kept as `dir-noc`.
- Avoided on purpose: cream/off-white pages, purple gradients, pill buttons, italic accent words, numbered section labels, monospace labels.
- Data palette taken from the dataviz skill's validated reference (8 hues, fixed order), re-checked against our own surfaces. The red ramp was generated at the same OKLCH lightness as the blue ramp so the diverging arms are symmetric.
- Polish UI copy in components, English in the guide's explanations. Tile map instead of real boundaries (no geometry in scope).
- Fonts are variable woff2 from Fontsource 5.3.0 (see `sources.md`), latin + latin-ext only: 256 KB for all four families; a page only downloads the faces its direction uses.
