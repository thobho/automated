# R3 DACH & Benelux (T07): patterns and coverage

Germany, Netherlands, Switzerland, Austria, Belgium, Luxembourg (scanned in that order). All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R3-dach-benelux.csv](../../../catalogue/R3-dach-benelux.csv).

Draft: updated after each country.

## Files

| File | Content |
|---|---|
| [germany.md](germany.md) | law, tax/DATEV, health admin, property, trades, benefits, education, horizontal; charts (DE-001…016) |
| [netherlands.md](netherlands.md) | GP scribe, audit, tenders, legal, accounting (NL-001…005) |
| [switzerland.md](switzerland.md) | legal search, fiduciary AI via association, hospital documentation and coding, study app, invoicing (CH-001…006) |

## Choices recorded
- IDs `R3-<ISO>-NNN`, numbered per country (DE-001…). Products already in R0/R1/R2 are not re-added (listed below).
- `works_in_polish` is `unknown` unless a source shows the product in Poland (Libra: yes, launched by Wolters Kluwer in PL).
- Non-LLM products are catalogued only where the pattern matters for Poland (Elterngeld Buddy), and `llm_role` says so.

## Coverage

| Country | Status | New rows | R0–R2 overlaps | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| Germany | done | 16 | 10 (R0) | 37 | 20 pages + 6 feeds | 21 | |
| Netherlands | done | 5 | 0 | 11 | 7 pages + 6 feeds | 9 | thin applied-AI pipeline |
| Switzerland | done | 6 | 0 | 12 | 6 pages + 6 feeds | 6 | 1 row on excerpt (TreuhandGPT) |
