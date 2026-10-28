# Verification (2026-10-28)

Real API calls (GUS BDL API v1, anonymous):

- `GET https://bdl.stat.gov.pl/api/v1/data/by-variable/60641?unit-level=0&year=2025&format=json`
  -> `{"variableId":60641,"results":[{"id":"000000000000","name":"POLSKA","values":[{"year":"2025","val":37332510,"attrId":1}]}]}`
- `GET .../data/by-variable/60641?unit-level=6&year=2000..2025&page-size=100&page=N` (25 pages): per-gmina `results[].id/name/values[].year/val`; the code reads exactly these fields.
- Variables listing for subject P1336 confirmed ids 60641 (total), 60617 (urban areas), 60633 (rural areas), "place of residence", "as of 31 December", total sexes.
- World Bank API v2 `country/POL/indicator/{SP.POP.TOTL,SP.URB.TOTL,SP.URB.TOTL.IN.ZS}` returned 26 yearly values each.
- Anonymous quota was hit (HTTP 429, `Retry-After` ~6100 s, "1000 per 12 h"); the client honours `Retry-After` and resumed after the wait.

Checks passed:
- national urban + rural = total in all 26 years; sum of gmina types 1-3 = national total for 2002-2025 exactly, and for 2000-2001 after dropping the Warsaw district units (double count).
- `python3 scripts/check_sources.py` -> `OK: all data files use known source_ids (7 sources)`, exit 0.
- Same script on a copy with one `S99` and one empty `source_id` -> two ERROR lines, exit 1.
- `python3 -m unittest discover -s tests` -> 12 tests OK.
