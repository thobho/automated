# smolec-weather

Static weather page for Smolec (Lower Silesia). Independent project: do not import code from other projects.

- Plain HTML/CSS/JS only. No build step, no framework, no dependencies.
- Data from Open-Meteo (no key), timezone `Europe/Warsaw`.
- WMO weather codes are mapped to emoji + text in `app.js` (`WMO`).
- API failure must show a visible error message (`#error`), never a blank page.
- Keep layout working at 375 px width with no horizontal scroll.
- Test: `python3 -m http.server` in this folder, `node --check app.js`.
- Deployed by `.github/workflows/smolec-weather-pages.yml`; only this folder is published.
