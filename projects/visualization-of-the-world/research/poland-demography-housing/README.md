# Poland: demography and housing (research)

Phase 1 research for `visualization-of-the-world`. Research only: CSV data, scripts, short reports. No charts or pages.
Period: **2000 to 2025** (2025 = latest year published by GUS BDL on 2026-10-28; values are as of 31 December).

## Layout
- `sources.csv` - registry of every source (`S1`...). Every data file has a `source_id` column; reports cite `[S..]`.
- `data/raw/` - small committed extracts of API responses (`bdl_national.csv`, `bdl_gminas.csv`, `bdl_gmina_sums.csv`, `worldbank_poland.csv`). The full API cache lives in `data/raw/cache/` (git-ignored, refetchable).
- `data/processed/` - `population_by_class.csv`, `urbanization_and_big_cities.csv`, `big_city_list.csv`.
- `scripts/` - `fetch_bdl.py`, `fetch_worldbank.py`, `process_population.py`, `check_sources.py`, `bdl.py` (cached throttled client). Python 3 stdlib only.
- `reports/01-population.md` - short trend report.
- `tests/` - `python3 -m unittest discover -s tests`.

Reproduce: `python3 scripts/fetch_bdl.py && python3 scripts/fetch_worldbank.py && python3 scripts/process_population.py && python3 scripts/check_sources.py`.
The BDL anonymous limit is 100 requests / 15 min and 1000 / 12 h; a full fetch needs about 30 requests and waits automatically when the limit is hit.

## Place classes (fixed for the whole series)
| class | definition |
|---|---|
| `big_cities` | cities with at least 100,000 inhabitants in **2025**. One fixed list of 34 cities (`data/processed/big_city_list.csv`) used for every year, so the class is comparable over time. |
| `small_cities` | all other cities and towns (all urban areas not in the big-city list). |
| `villages` | rural areas. |

Everything is on GUS's own urban/rural classification (miasto = urban, wies = rural). This is an administrative definition (legal town status), not a density-based one.

## Method
- National **total**, **urban** and **rural** population come directly from BDL variables 60641 / 60617 / 60633 (subject P1336, place of residence, 31 December) [S1].
- `villages` = BDL rural total (reported).
- `big_cities` = sum of the 34 cities' populations (BDL gmina-level total, variable 60641). Each of these cities is an *urban gmina* (BDL unit-id last digit `1`) and therefore entirely urban. Derived value.
- `small_cities` = BDL urban total - `big_cities`. Derived value. The three classes sum to the national total exactly by construction (the independent check is that the sum of all gmina values equals the national total in every year, see `data/raw/bdl_gmina_sums.csv` and the tests).
- `share_of_total_pct` = class / national total x 100 (2 decimals; shares sum to 100 +- 0.02 from rounding).
- `urbanization_rate_pct` = urban / total x 100.
- `big_cities_ge100k_in_year_count` = number of urban gminas with at least 100,000 inhabitants **in that year** (cities enter or leave the class); `big_cities_fixed_list_count` is the constant 34. Only gminas that ever reached 50,000 inhabitants are stored in `bdl_gminas.csv`, which is enough for the 100,000 threshold.

### Urban-rural gminas
BDL has three gmina kinds that matter here: urban (id ends `1`), rural (`2`), urban-rural (`3`); the urban and rural *parts* of urban-rural gminas are separate units (`4`, `5`). The national urban and rural totals from BDL already allocate the town part of an urban-rural gmina to urban and the rest to rural, so `small_cities` includes the towns that are seats of urban-rural gminas and `villages` includes their rural parts. No big city is part of an urban-rural gmina (the largest such gmina in 2025, Piaseczno, has 98,414 inhabitants in total, town and villages together, so even its town is below the threshold). Type `4`/`5` units are excluded when summing gminas to avoid double counting. The class split is therefore at the town level, not at the whole-gmina level.

## Known data breaks and caveats
- **2002 and 2011 censuses:** GUS rebased the population after the 2002 and 2011 censuses; **2021 census:** series from 2020 were recalculated on the 2021 census (BDL variable description). Year-on-year changes at these points mix real change and rebasing.
- **2009 to 2010:** the national total jumps by +362 thousand (+0.95%) and the rural population by +224 thousand in one year [S1]. BDL's variable description says that from 2010 the population balance is compiled with a single concept (previously two: de facto and de jure). The jump is a statistical break, not real growth; its exact cause was not confirmed in a GUS methodological note here.
- **2019 to 2020:** the national total falls by 294 thousand (-0.77%) [S1], which includes the recalculation on the 2021 census (see above).
- **Status changes:** the urban/rural split is as of 31 December of each year on the then-current legal status. New town rights, towns losing rights, and boundary changes (annexations of villages to cities) move people between `villages` and the city classes. These changes were **not** individually traced or corrected; the series are not restated to a constant territory. Whether BDL restates earlier years for status changes was not verified.
- **Warsaw:** until 2001 BDL carries Warsaw as one unit plus 11 district units; the districts are dropped, the whole-city unit is used. Units `Wałbrzych to 2002`, `since 2003 to 2012`, `since 2013` are joined into one series; Wałbrzych is not a big city in 2025 (97,546).
- **Fixed list vs. true classification in earlier years:** in 2000 there were 41 cities at or above 100,000; 7 of them fell below by 2025 and are in `small_cities` for all years. This is deliberate (comparability), but it understates the "big city" population relative to the then-current definition.
- **World Bank/UN series** (S2-S4) differ from GUS in method and are used only as a sanity check (2025 total: 36.4 million vs. 37.3 million GUS). They are not used for any class value.
- The `value_type` column marks values `reported` (taken as is from BDL) or `derived` (formula in the `formula` column).
- 2025 values are the latest published (possibly preliminary) at the access date; this was not verified against a revision.
