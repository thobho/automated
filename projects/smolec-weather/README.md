# smolec-weather

A tiny static web page showing the current weather and a 7-day forecast for Smolec, Lower Silesia, Poland (51.08 N, 16.88 E).

- Plain HTML/CSS/JS, no build step, no framework, no API key.
- Data: [Open-Meteo](https://open-meteo.com/), fetched in the browser. Times in Europe/Warsaw.
- Published to GitHub Pages by `.github/workflows/smolec-weather-pages.yml` on push to `main`.

## Run locally

```sh
cd projects/smolec-weather
python3 -m http.server 8000
# open http://localhost:8000
```

## Files
- `index.html` - markup
- `style.css` - responsive styles (works at 375 px)
- `app.js` - fetch, WMO code mapping, rendering, error message
