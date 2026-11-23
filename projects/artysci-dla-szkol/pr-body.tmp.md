## Summary
Public artist page and preview: alt texts (stored `Material.alt_text` + Polish fallback service, no AI), skip link, landmarks, expander button with aria, keyboard-operable gallery dialog, 3:1 focus outline in all themes, reduced motion with a stylesheet scan test, Playwright + axe + keyboard suite. README checklist for new sections, D116.

## Verification
- `uv run pytest -q --tb=short apps/profiles apps/artists` → **870 passed**; ruff check/format clean; `makemigrations --check` clean; coverage of `accessibility.py` and `materials.py` ≥ 96%.
- Real app (`make web`, Postgres container) + `make e2e`: **22 passed**. Axe per theme (critical/serious): burgundy_light 0, cream_green 0, navy_gold 0, coral_dark 0 (0 violations of any impact). Screenshots in `e2e-screenshots/a11y-*.png`.
- Criteria: alt on every img (stored/fallback; decorative empty) ✅ unit + e2e · Tab: skip link first, then every control in order with outline ≥2px and ≥3:1 ✅ e2e · gallery Esc / focus loop / focus return ✅ e2e · Enter/Space toggles aria-expanded ✅ e2e · reduced motion: scroll-behavior auto, 0 animations + CSS scan test ✅ · axe ✅ · one h1, no skipped levels, lang=pl ✅ · no inline script/style ✅.
- web-design-guidelines check of changed templates/CSS: labels/aria present, no `outline:none` except the programmatic skip target, `loading=lazy` on gallery.
- Note: the local dev server returned 500 ("too many clients" on the container Postgres) after many runs; restarting the server fixed it. Environment issue, not code.

## Decisions I made
- "Pokaż pozostałe" is a button instead of `<details>` (as the issue demands); without JS it stays hidden and offers are visible.
- Gallery = links to files, opened by `static/profiles/page.js` in a native `<dialog>` with a Tab loop added (Chromium lets Tab leave a modal dialog).
- Alt field is on the materials page next to each ready photo; max 200 chars.
- SECURITY.md has no accessibility row, so unchanged. FAQ stays a plain `<dl>` (no interactive items).
- Updated existing tests that looked for `<details>`.

## Action for you
none — review and merge. (Migration `artists.0009_photo_alt_text` adds one blank-default column.)

Closes #171

🤖 Generated with [Claude Code](https://claude.com/claude-code)
