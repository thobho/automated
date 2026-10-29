# Verification log - task 11 (final report, bibliography, citation sheet)

Run on 2026-10-29 in the issue working copy.

## 1. check_sources.py on the real repo files
`python3 scripts/check_sources.py` ->
```
OK: all data files use known source_ids (49 sources)
```
It now also checks the final report (numbers without a key, unknown keys, undefined D keys) and unused sources.
Before the report existed it failed with "S5: unused"; the report now cites S5 (and S2).

## 2. Unit tests
`python3 -m unittest discover -s tests` ->
```
Ran 110 tests in 0.457s
OK
```
`tests/test_final_report.py` recomputes headline numbers from data/processed and asserts they are in the report.
During the build it caught wrong or differently rounded numbers copied from earlier reports (for example +362 thousand
is +363 thousand, Poznan -8.3% is -8.2%, small-city flats 60.2% is 60.1%, the "2-8%" proxy gap is 2.5-7.4%); all fixed in the report.

## 3. Headline numbers against live APIs (curl)
- GUS BDL /data/by-variable/60641?unit-level=0&year=2025 -> POLSKA 2025 = 37332510 (report: 37,332,510).
- Eurostat demo_gind?geo=PL&indic_de=JAN&time=2026 -> 36332765 (report: 36,332,765).
- GUS BDL /data/by-variable/748601?unit-level=0&year=2022 -> 238490 (report: record 238.5 thousand in 2022).

## 4. Bibliography URLs (curl -L, HTTP status)
S1 200, S5 200, S6 200, S29 200, S36 200, S38 200, S43 200.

## 5. Not verified
- The remaining URLs of the 49 sources were not requested; they are the URLs recorded by the earlier tasks.
- Why Eurostat and GUS population differ by about 1.0 million, and the cause of the 2010 population jump, are unverified (stated in the report).
