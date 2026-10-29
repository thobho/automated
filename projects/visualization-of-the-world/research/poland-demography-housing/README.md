# Poland: demography and housing (research)

Phase 1 research for `visualization-of-the-world`. Research only: CSV data, scripts, short reports. No charts or pages.
Period: **2000 to 2025** (2025 = latest year published by GUS BDL on 2026-10-28; values are as of 31 December).

## Layout
- `sources.csv` - registry of every source (`S1`...). Every data file has a `source_id` column; reports cite `[S..]`.
- `data/raw/` - small committed extracts of API responses (`bdl_national.csv`, `bdl_gminas.csv`, `bdl_gmina_sums.csv`, `worldbank_poland.csv`). The full API cache lives in `data/raw/cache/` (git-ignored, refetchable).
- `data/processed/` - `population_by_class.csv`, `urbanization_and_big_cities.csv`, `big_city_list.csv` (task 01); `age_sex_pyramid.csv`, `age_structure_indicators.csv`, `vital_rates.csv`, `migration_national.csv`, `ukraine_inflow.csv`, `migration_by_place_class.csv`, `households.csv`, `suburban_belt_gminas.csv`, `suburban_belt_summary.csv`, `small_towns_change.csv` (task 02); `europe_annual.csv`, `europe_degurba.csv`, `europe_summary.csv` (task 03).
- `scripts/` - `fetch_bdl.py`, `fetch_worldbank.py`, `process_population.py`, `check_sources.py`, `bdl.py` (cached throttled client). Python 3 stdlib only.
- `reports/01-population.md`, `reports/02-structure.md` - short reports.
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

## Task 02 - demographic structure, vital rates, migration, households
Report: `reports/02-structure.md`. Rebuild: `python3 scripts/fetch_bdl_structure.py && python3 scripts/fetch_eurostat.py && python3 scripts/fetch_bdl_gminas.py && python3 scripts/process_structure.py && python3 scripts/check_sources.py`. The gmina-level fetch is about 85 requests (two variables, 42 pages each) and takes roughly 15 minutes; it only warms the git-ignored cache. Net migration abroad and 2021 households at gmina level (about 42 requests each) were not fetched; add their ids to `scripts/fetch_bdl_gminas.py` to extend the files.

| file | content | level |
|---|---|---|
| `age_sex_pyramid.csv` | population by 5-year age group and sex, 2000/2010/2020/2025 [S8] | national |
| `age_structure_indicators.csv` | median age, dependency ratios, share 65+ (GUS definitions [S9][S11]; Eurostat convention [S19]); urban/rural dependency from 2012 [S10] | national; urban/rural where BDL has it |
| `vital_rates.csv` | births, deaths, natural increase, infant deaths [S12], total fertility rate [S13][S21], life expectancy [S14] | national + urban/rural (TFR national only) |
| `migration_national.csv` | registered permanent-residence migration [S15], Eurostat immigration/emigration [S22], net migration plus adjustment [S20] | national |
| `ukraine_inflow.csv` | Ukrainian citizens with EU temporary protection in Poland, monthly stock [S23]; kept apart from every other migration series | national |
| `migration_by_place_class.csv` | net internal permanent-residence migration, summed over gminas by place class, per 1000 residents [S15][S1] | big cities / small cities / villages |
| `households.csv` | households and average size: censuses 2002/2011/2021 [S16][S17][S18], EU-LFS annual estimate 2006+ [S24] | national |
| `suburban_belt_gminas.csv`, `suburban_belt_summary.csv` | every gmina within 25 km of the 8 largest cities and its growth 2000-2025 [S1][S26] | gmina |
| `small_towns_change.csv` | all towns below 100,000 inhabitants in 2025 with 2000-2025 change [S1] | town |

Decisions and conventions:
- **Level of detail follows the source.** Pyramids, median age, dependency ratios and fertility have no place-class split in BDL (the lowest published level is the voivodeship for fertility and national for age-by-sex), so they are national, with urban/rural where BDL publishes it (births, deaths, life expectancy, median age from 2016, broad age groups from 2012). Nothing is estimated for the missing levels.
- **Place-class migration** sums gmina-level units: big cities = the fixed 34-city list; small cities = other urban gminas plus the urban parts (type 4) of urban-rural gminas; villages = rural gminas plus rural parts (type 5). BDL does carry migration for type 4/5 units (columns `gmina_units_with_migration` vs `gmina_units_with_population` match); whole urban-rural gminas (type 3) are skipped to avoid double counting. The three class nets sum to zero in every year (tested).
- **Suburban belt:** gminas (types 1-3, not themselves among the 34 big cities) whose centroid lies within 25 km of one of the 8 largest cities by 2025 population, each assigned to the nearest of the 8. The centroid comes from the simplified polygons of the geography task (S26) and the 25 km radius is a judgement call. Series of a gmina that changed type (rural to urban-rural) are joined by the 6-digit TERYT because its territory did not change; gminas created or re-coded after 2000 have no 2000 value and are listed with no change (`note` column).
- **Small towns** are urban gminas and the urban parts of urban-rural gminas with fewer than 100,000 inhabitants in 2025. Ranking of losses ignores towns below 2,000 inhabitants in 2000 and towns without a 2000 value (new town rights).
- **Ukrainian inflow is not in the GUS permanent-residence series** (refugees mostly hold temporary protection), so it is shown only as the Eurostat stock in `ukraine_inflow.csv`. It does not feed any other file.

## Task 03 - Poland in Europe (Eurostat)
Report: `reports/03-europe.md`. Rebuild: `python3 scripts/fetch_eurostat_europe.py && python3 scripts/process_europe.py && python3 scripts/check_sources.py` (about 12 API calls, no key; raw extract `data/raw/eurostat_europe.csv`, 3.7k rows, the API cache is git-ignored).

| file | content |
|---|---|
| `europe_annual.csv` | PL, CZ, SK, HU, DE, RO, LT and EU-27: population 1 Jan, total change, natural change, net migration plus adjustment (level and per 1000) [S29], TFR [S30], median age and old-age dependency 65+/15-64 [S31], life expectancy at birth (total/men/women) [S32], plus derived population index (1 Jan 2000 = 100). Column `eurostat_flag` keeps Eurostat's b/e/p flags |
| `europe_degurba.csv` | cities / towns and suburbs / rural areas (Eurostat DEGURBA): EU-SILC share of persons [S33], EU-LFS population 15+ and derived shares [S34], 2021 census counts and derived shares [S35] |
| `europe_summary.csv` | first and latest value per indicator and country, change, and Poland's rank among the 7 countries (derived) |

Decisions and conventions:
- Every row has `dataset_code` (Eurostat code) and `source_id`. Missing years stay missing (EU-27 starts 2001/2002 for some indicators).
- **DEGURBA is not the GUS urban/rural split** and is never mixed with the place classes above; definitions are compared in the report (section 3).
- The three DEGURBA sources (two surveys, one census) are kept as separate `measure` values and not combined.
- UN WPP and OECD were not used: Eurostat covers all indicators and all eight areas, see the report.
- "Net migration" is Eurostat's residual (net migration plus statistical adjustment), not registered moves; Poland 2020 (-762,735) is mostly an adjustment and flagged b.
