# Poland: demography and housing, 2000-2025 (final report)

Merges the five earlier reports (`01-population.md` to `05-housing-vs-population.md`). Every number carries a source key `[S..]` that resolves in `../sources.csv` (full references: `bibliography.md`; ready-to-paste captions per data file: `citation-sheet.md`). Values computed in this project are marked "derived" with a key `D..` that points to the formula table in section 9. Numbers were re-checked against the processed CSVs in `data/processed/` (`tests/test_final_report.py` does this on every run); where an earlier report disagreed with its CSV, the CSV wins (section 8).

**Latest year: 2025** for all GUS Bank Danych Lokalnych (BDL) series, 31 December or calendar year [S1][S41]. Exceptions are listed in section 1.

## Executive summary

**Population and urbanization**
- Poland's population fell from 38.25 million (2000) to 37.33 million (2025), -2.41% (derived, D3) [S1]. The urban share fell from 61.85% to 59.34% [S1].
- By place class only **villages grew**: 14.59 million (38.15% of the total) to 15.18 million (40.66%). **Small cities and towns** shrank from 13.05 to 12.07 million; the **34 big cities** (at least 100,000 inhabitants in 2025, fixed list) from 10.61 to 10.08 million (derived, D1) [S1]. Cities at or above 100,000 in the given year fell from 41 to 34 [S1].
- Villages gain people from internal migration every year (+2.4 per 1000 residents in 2025); small cities lose (-2.6); big cities lose since 2020 (-0.4 in 2025) (derived, D4) [S15][S1]. Eight big-city belts of gminas within 25 km grew from 2.14 to 3.01 million (+41%, derived, D3) while 649 of 777 small towns lost population [S1][S26].

**Demographic structure**
- The population is ageing fast: share aged 65+ 12.4% to 21.1%, share aged 0-14 19.1% to 14.2% (derived, D5) [S8]. Median age 35.1 (1 Jan 2000) to 43.4 (1 Jan 2025) [S19].
- Births fell from 378 thousand to 238 thousand; deaths were 406 thousand in 2025; natural increase was -167 thousand [S12]. Total fertility rate was 1.37 (2000, Eurostat) and 1.07 in 2025 (GUS) [S21][S13].

**Europe**
- Against six peers and the EU-27, Poland's old-age dependency rose most (+14.9 points to 32.7) and the population index (2000 = 100) is 94.95 against 105.49 for the EU-27 on 1 January 2026 (derived, D8) [S31][S29]. Poland's fertility (1.14 in 2024) is sixth of seven [S30].
- The Eurostat degree-of-urbanisation (DEGURBA) is not the GUS urban/rural split: the 2021 census gives Poland 34.67% in rural areas against 24.48% for the EU-27 (derived, D9) [S35]; GUS counts 40.32% rural the same year [S1].

**Housing**
- Completed dwellings rose from 87.8 thousand (2000) to a record 238.5 thousand (2022), then 208.3 thousand in 2025 [S41]. The dwelling stock grew from 11.84 to 16.16 million, +36.4% (derived, D3) while the population fell [S44][S1].
- New dwellings per 1000 residents in 2025: big cities 8.07, villages 4.90, small cities 4.36 (derived, D4) [S41][S1]. **Big cities build flats** (84.9% of completions in 2025), **villages build houses** (89.3%), small cities are mixed (38.7% houses, 60.1% flats) [S43].
- Construction does not follow population: 2009 to 2025 the big cities completed 117.4 dwellings per 1000 residents of 2009 while losing 2.9% of residents; villages 73.0 while gaining 2.0%; small cities 59.5 while losing 6.4% (derived, D6) [S43][S1].

**Biggest caveats** (section 9): census rebasing breaks in 2002, 2010, 2020 and 2021 [S1]; Eurostat and GUS levels differ by about 1.0 million people [S29][S1]; direct house/flat data exist only from 2009 [S43]; no place-class split for fertility, age pyramid or construction starts [S8][S46]. The earlier comparison report (task 05) contains numbers that do not match its CSV and is superseded by section 7 (section 8).

## 1. Scope, place classes, latest years

- **Place classes** (GUS urban/rural legal status, one fixed definition for all years): `big_cities` = the 34 cities with at least 100,000 inhabitants in 2025 [S1]; `small_cities` = all other urban areas; `villages` = rural areas [S1][S40]. The unit is the gmina; the town part of an urban-rural gmina counts as urban and the rest as rural [S5][S38][S39]. Levels are never mixed silently: where a source has no class split, the national level is stated.
- **Latest year by source:** GUS BDL population, vital rates, housing completions, stock, permits: 2025 [S1][S12][S41][S44][S45]. Construction starts: 2019 only [S46]. Eurostat population 1 January: 2026; population change, natural change, net migration: 2025; median age and old-age dependency: 1 January 2025; fertility and life expectancy: 2024 [S29][S31][S30][S32]. Degree of urbanisation: surveys 2025, census 2021 [S33][S35]. Ukrainian temporary-protection stock: September 2026, the latest month [S23].
- **Definitions that differ:** the GUS urban population is people in localities with town status [S40]; Eurostat's DEGURBA classes whole gminas by grid-cell density (section 5) [S36][S37].

## 2. Urbanization and population by place class

| class | 2000 | 2025 | change | share 2000 | share 2025 | source |
|---|---|---|---|---|---|---|
| big cities (34, fixed list) | 10,614,664 | 10,084,486 | -4.99% | 27.75% | 27.01% | [S1] D1 D2 D3 |
| small cities and towns | 13,045,026 | 12,067,918 | -7.49% | 34.10% | 32.33% | [S1] D1 D2 D3 |
| villages | 14,594,265 | 15,180,106 | +4.01% | 38.15% | 40.66% | [S1] D1 D2 D3 |
| Poland | 38,253,955 | 37,332,510 | -2.41% | 100% | 100% | [S1] D3 |

- Urban population 23.66 million to 22.15 million; urbanization rate 61.85% to 59.34% (derived, D3) [S1]. Villages peaked at 15.35 million in 2019 and then declined to 15.18 million [S1].
- The big-city share has been flat since 2010 (26.87% in 2010, 27.01% in 2025) [S1]. The 2020 uptick (26.78% to 27.05%) coincides with GUS recalculating its series on the 2021 census [S1].
- Seven cities dropped below 100,000 between 2000 and 2025 (Chorzów, Kalisz, Legnica, Wałbrzych, Grudziądz, Włocławek, Słupsk); no city entered (derived by comparing gmina values, D10) [S1]. They are in `small_cities` for all years, which understates big-city population relative to the then-current definition [S1].
- Cross-check, not used for any value: the World Bank/UN series gives 36.44 million people, 21.89 million urban and 60.09% urban for 2025 [S3][S2][S4] against 37.33 million, 22.15 million and 59.34% in GUS [S1].
- Breaks: the national total jumps +363 thousand (+0.95%) from 2009 to 2010 and the rural population +224 thousand, when GUS changed its population concept; it falls 294 thousand (-0.77%) from 2019 to 2020 with the recalculation on the 2021 census (derived, D3) [S1]. The cause of the 2010 jump was not confirmed in a GUS methodological note.

## 3. Demographic structure, vital rates, migration, households

**Age and sex (national only; BDL has no pyramid by urban/rural or place class)** [S8]
- Aged 0-14: 19.1% (2000) to 14.2% (2025); aged 65+: 12.4% to 21.1% (derived, D5) [S8]; GUS publishes 21.1% for 2025 [S9]. The 0-4 cohort shrank from 1.98 million to 1.40 million; women aged 70+ grew from 2.02 to 3.34 million [S8].
- Median age: 35.1 on 1 January 2000 to 43.4 on 1 January 2025 (Eurostat) [S19]; GUS gives 43.8 at 31 December 2025, urban 44.8 and rural 42.3 [S11].
- Old-age dependency (65+ per 100 aged 15-64): 17.8 (2000) to 32.7 (2025) [S19]; on the GUS definition (women 15-59, men 15-64 as working age) 18.6 in 2003 and 32.6 in 2025 [S9]. Total dependency 71.8 in 2025 (GUS); in towns 74.2 and in the countryside 68.4 [S9][S10].

**Births, deaths, fertility, life expectancy**
- Births: 378 thousand (2000), 413 thousand (2010), 402 thousand (2017), 238 thousand (2025). Deaths: 368 thousand (2000), 520 thousand (2021, COVID-19), 406 thousand (2025) [S12].
- Natural increase: +10 thousand (2000), +35 thousand (2008 peak), -188 thousand (2021), -167 thousand (2025). Per 1000 residents in 2025: towns -5.0, villages -3.7 [S12].
- Total fertility rate: 1.37 (2000) and 1.31 (2001) from Eurostat, 1.25 (2002), 1.38 (2010), 1.45 (2017) and 1.07 (2025) from GUS [S21][S13]. BDL gives fertility only nationally.
- Life expectancy at birth rose for men from 69.7 (2000) to 75.4 (2025) and for women from 78.0 to 82.5; 2021 fell to 71.8 and 79.7 [S14].

**Migration**
- Internal permanent-residence migration, net, per 1000 residents (derived, D4) [S15][S1]: villages +0.29 (2000), +3.24 (2007), +3.49 (2022), +2.38 (2025); small cities -0.50, -2.31, -3.36 and -2.63; big cities +0.21, -1.73, -1.18 and -0.43. The three nets sum to zero each year [S15]. An origin-destination matrix (city to village) is not published by BDL in aggregate. Literature agrees on the direction (core city to surrounding municipalities) [S6][S7][S28].
- International, GUS (registered change of permanent residence): net -19.7 thousand (2000) to +10.9 thousand (2025) [S15]. Eurostat's net migration plus statistical adjustment was +33.2 thousand in 2024 and +2.8 thousand in 2025 [S20]. These are different concepts and are never combined (section 8).
- Ukrainian citizens under temporary protection, a stock and not a flow, kept apart from all other series: 0.68 million (March 2022), peak 1.37 million (September 2022), 0.97 million (December 2025), 0.86 million (September 2026) [S23]. The literature describes the 2022 wave as the largest since World War II [S27].

**Households**
- Census: 13.34 million households, 2.84 persons (2002); 13.57 million, 2.82 (2011); 12.52 million, 2.99 (2021) [S16][S17][S18]. EU Labour Force Survey average: 3.0 persons (2006) to 2.3 (2025), rounded to one decimal [S24]. The census trio contradicts the survey trend (section 8). No household data by place class.

## 4. Suburban belts and small towns

- **Belt method:** gminas whose centre lies within 25 km of one of the 8 largest cities, excluding the 34 big cities themselves, each assigned to the nearest [S1][S26]. The 25 km radius and the use of simplified polygon centroids are judgement calls.
- 132 belt gminas with 2000 and 2025 values grew from 2.14 to 3.01 million, +41% (derived, D3) [S1].
- Core versus belt population change 2000 to 2025 (derived, D3) [S1]: Warsaw +11.6% vs belt +47.5%; Kraków +7.6% vs +32.3%; Wrocław +5.0% vs +102.1%; Poznań -8.2% vs +79.3%; Gdańsk +5.7% vs +55.0%; Szczecin -7.9% vs +29.0%; Łódź -19.9% vs +6.6%; Lublin -9.0% vs +11.5%.
- Fastest-growing gminas: Dobra (Szczecińska) from 8.6 to 31.6 thousand (+266%), then Dopiewo (+249%), Rokietnica (+229%), Komorniki (+221%) [S1]. Of the 132 belt gminas 20 lost population [S1].
- **Small towns** (urban gminas and town parts below 100,000 inhabitants in 2025, with at least 2,000 inhabitants in 2000): of 777 towns 649 lost and 127 gained; together 12.78 to 11.59 million, -9.4% (derived, D3) [S1]. Largest relative loss: Hel -39.7% [S1].

## 5. Poland in Europe

Comparison set: Poland, Czechia, Slovakia, Hungary, Germany, Romania, Lithuania and the EU-27, all from Eurostat [S29][S30][S31][S32]. Rank = Poland's position among the seven countries (derived, D11). Flags b (break), e (estimate), p (provisional) are kept in the data; the latest values are largely provisional [S29].

| indicator | Poland | EU-27 | rank among seven | source |
|---|---|---|---|---|
| Population index, 1 Jan 2026 (1 Jan 2000 = 100) | 94.95 | 105.49 | fourth of four countries that lost population | [S29] D8 |
| Total fertility rate 2024 | 1.14 (1.37 in 2000) | 1.34 | sixth | [S30] D11 |
| Median age 1 Jan 2025 | 43.4 (35.1 in 2000) | 44.9 | sixth | [S31] D11 |
| Old-age dependency 2025 | 32.7 (17.8 in 2000) | 34.5 | second | [S31] D11 |
| Life expectancy at birth 2024 | 78.5 (73.8 in 2000) | 81.5 | third | [S32] D11 |
| Net migration plus adjustment 2025, per 1000 | 0.1 | 4.6 | sixth | [S29] D11 |

- **Ageing speed is the outlier:** old-age dependency rose by 14.9 points (+83.7%), the largest of the seven; next CZ +12.6, RO +12.3, DE +12.0, SK +12.1, LT +11.3, HU +10.2 and EU-27 +11.1 (2001 to 2025) (derived, D10) [S31].
- **Fertility fell while most peers rose:** 1.37 to 1.14 for Poland (-0.23); CZ 1.15 to 1.36, SK 1.30 to 1.46, HU 1.32 to 1.41, RO 1.31 to 1.39; only Lithuania fell more (1.39 to 1.11) [S30].
- **Population:** Poland 38.26 million (1 January 2000) to 36.33 million (1 January 2026), -5.05%; EU-27 +5.49% (derived, D3) [S29]. Natural change was +10,321 in 2000 and -167,483 in 2025 [S29].
- **Net migration is a residual,** not a count of moves. Poland's 2020 value (-762,735 against a total change of -884,781) is mostly a statistical adjustment (flag b) and must be excluded from trends [S29].
- **Degree of urbanisation (DEGURBA):** 2021 census, Poland: cities 12,453,650 (33.64%), towns and suburbs 11,731,735 (31.69%), rural areas 12,834,067 (34.67%) (derived shares, D9) [S35]. EU-27 shares 39.12% / 36.40% / 24.48% (derived, D9) [S35]. Poland's rural share is 10.2 points above the EU-27 (derived, D10) [S35].
- **Survey dynamics** (EU-SILC, Poland, 2012 to 2025, after a break in 2011/2012): cities 33.9% to 34.3%, towns and suburbs 24.5% to 30.3%, rural 41.6% to 35.4% (derived, D10) [S33]. The direction (cities stable, towns and suburbs growing, rural shrinking) agrees with the labour-force survey (rural 40.3% to 35.9% for ages 15+) [S34]; the size is uncertain because the classification was updated [S33].
- Definitions: DEGURBA cities = at least 50% of a gmina's population in contiguous cells of at least 1,500 inhabitants per km2 and 50,000 inhabitants; towns and suburbs = clusters of at least 300 per km2 and 5,000 inhabitants; rural = the rest [S36][S37].
- UN WPP and OECD were not used: Eurostat covers every indicator for all eight areas, and mixing in modelled series would not add comparability [S29]. A big-city/small-city/village comparison across countries is not possible; DEGURBA is the best available level [S35].

## 6. Housing construction

**Completions (national, then by class)**
- National completions: 87.8 thousand (2000), 162.7 thousand (2003 spike), 160.0 thousand (2009), 135.8 thousand (2010), 178.3 thousand (2017), record 238.5 thousand (2022), 208.3 thousand (2025) [S41][S42].
- By class (thousand dwellings, derived, D1 sums of gmina values) [S41]: big cities 40.7 (2000), 64.4 (2009), 78.2 (2017), 85.6 (2022), 81.3 (2025); small cities 29.4, 46.9, 40.0, 62.5, 52.6; villages 17.7, 48.7, 60.1, 90.4, 74.4. Class sums equal the BDL national value in all 243 variable-year checks [S41][S43][S44][S45].
- Share of completions 2025: big cities 39%, villages 36%, small cities 25% (derived, D12); in 2000: 46%, 20% and 34% [S41].

**Houses and flats, direct data 2009 to 2025** (new single-family buildings = houses; new multi-family buildings = flats) [S43]
- Nationally 2025: 97.9 thousand houses and 107.8 thousand flats; houses peaked at 119.5 thousand in 2022 [S43].
- Houses outnumbered flats in 2010 to 2015 and in 2022 [S43].
- Floor area: average of all completed dwellings fell in every class, 2025 in big cities 62 m2 (76 in 2000), small cities 78 (87), villages 120 (125) (derived, D13) [S41]. Houses averaged 126, 121 and 128 m2 and flats 52, 50 and 50 m2 in big cities, small cities and villages (derived, D13) [S43].

**Proxies for 2000 to 2008** (no direct split exists) [S42][S41]
- Individual construction (BDL "private") is a house proxy for 2000 to 2017; the narrower own-use series [S41] for 2005 to 2025. Proxies are labelled in the data and never spliced with the direct series. In 2009 to 2017 individual construction is 2.5% to 7.4% above the direct house count and own use 5.0% to 15.8% below it (derived, D10) [S42][S43][S41].

**Stock, permits, starts**
- Dwelling stock (31 December) grew from 11.84 million (2000) to 16.16 million (2025) [S44]. Per 1000 residents: big cities 356 to 550, small cities 320 to 450, villages 267 to 341; persons per dwelling 2.81 to 1.82, 3.12 to 2.22, 3.75 to 2.93 (derived, D4) [S44][S1]. Census 2021 counted 15.23 million dwellings (13.44 million inhabited) against 15.36 million in the BDL stock [S48][S44].
- Permits: 178.8 thousand (2009), record 341.2 thousand (2021), 266.4 thousand (2025) [S45]. Classes exist only for 2018 to 2025; 2025: big cities 90.3 thousand (6.4 thousand houses, 81.6 thousand multi-family), small cities 67.9 thousand, villages 108.2 thousand (derived, D1) [S45].
- Starts exist at powiat level only, so only big cities against the rest of Poland, and only to 2019: 40.0 thousand (2005) to 95.3 thousand (2019), 40% of the national total in 2019 [S46]. Small cities and villages cannot be separated and are not estimated.

## 7. Housing against population: big cities, small cities, villages

Built only from `housing_completions_by_class.csv`, `population_by_class.csv` and `housing_stock_by_class.csv`, direct data 2009 to 2025 (derived: D4, D6; classes as in section 1). It replaces the numbers of task 05 (section 8).

**Table A - new dwellings per 1000 residents, 2025, and stock**

| class | residents 2025 | new houses per 1000 | new flats per 1000 | all new per 1000 | houses share | flats share | stock per 1000 | source |
|---|---|---|---|---|---|---|---|---|
| big cities | 10,084,486 | 1.10 | 6.84 | 8.07 | 13.6% | 84.9% | 550 | [S43][S41][S44][S1] D4 |
| small cities | 12,067,918 | 1.69 | 2.62 | 4.36 | 38.7% | 60.1% | 450 | [S43][S41][S44][S1] D4 |
| villages | 15,180,106 | 4.38 | 0.47 | 4.90 | 89.3% | 9.6% | 341 | [S43][S41][S44][S1] D4 |

The remainder to 100% is dwellings in non-residential buildings, extensions and conversions [S43].

**Table B - cumulative 2009 to 2025 against population change**

| class | residents 2009 | residents 2025 | change | houses completed | flats completed | all completed | completed per 1000 residents of 2009 | source |
|---|---|---|---|---|---|---|---|---|
| big cities | 10,388,753 | 10,084,486 | -2.93% | 162,848 | 1,036,931 | 1,219,585 | 117.4 | [S43][S41][S1] D3 D6 |
| small cities | 12,889,434 | 12,067,918 | -6.37% | 321,117 | 420,428 | 766,759 | 59.5 | [S43][S41][S1] D3 D6 |
| villages | 14,889,142 | 15,180,106 | +1.95% | 977,605 | 86,907 | 1,087,182 | 73.0 | [S43][S41][S1] D3 D6 |

- **Findings.** (1) Construction is not driven by population change: big cities built most per resident while shrinking, villages built 73.0 per 1000 while growing, small cities least while shrinking fastest [S43][S1]. (2) The mix is stable: of the dwellings completed 2009 to 2025, 85.0% in big cities were flats and 89.9% in villages were houses; small cities 54.8% flats and 41.9% houses (derived, D6) [S43]. (3) Big cities and small cities thus add to housing stock per resident, not to population, as persons per dwelling fell from 2.81 to 1.82 and from 3.12 to 2.22 [S44][S1].
- All new dwellings per 1000 residents, 2000 to 2025: big cities 3.83 to 8.07; small cities 2.25 to 4.36; villages 1.21 to 4.90 (derived, D4) [S41][S1]. Peaks: big cities 9.48 (2020), small cities 5.08 and villages 5.92 (both 2022) [S41].
- Limits: this is correlation of aggregates over classes with a fixed 2025 big-city list; it does not say where the buyers come from, and class membership moves with town rights [S1]. Starts and 2000 to 2008 house/flat data are not available by class (section 6).

## 8. Contradictions between sources and the choice made

| # | topic | what the sources say | choice and reason | source |
|---|---|---|---|---|
| C1 | population level | GUS 37,332,510 at 31 December 2025; Eurostat 36,332,765 on 1 January 2026, about 1.0 million lower, same date in practice (derived, D10) | GUS for everything by place class (only source with urban/rural and gmina level); Eurostat only in the cross-country comparison; never mixed. The reason (concept, long-term absentees, revision timing) was not verified | [S1][S29] |
| C2 | population in the 2021 census year | BDL 31 December 2021: 37,907,704; Eurostat's census table: 37,019,452 | GUS time series for classes; census counts only for DEGURBA shares of the same table. Different reference dates and concepts; reason not verified | [S1][S35] |
| C3 | World Bank against GUS | 2025: 36.44 million and 60.09% urban against 37.33 million and 59.34% | GUS; World Bank/UN used only as a check | [S3][S4][S1] |
| C4 | median age | Eurostat 43.4 at 1 January 2025; GUS 43.8 at 31 December 2025 | Eurostat for the 2000 to 2025 series (GUS starts 2016/2018) and the Europe table; GUS for urban/rural; reference dates differ | [S19][S11] |
| C5 | old-age dependency | Eurostat 32.7 (15-64 base); GUS 32.6 (women 15-59, men 15-64) | Eurostat in the Europe comparison; GUS where urban/rural exists; definitions are never mixed in one series | [S19][S9] |
| C6 | fertility rate | Eurostat higher by 0.03 to 0.04 where both exist: 2010 1.41 against 1.38, 2017 1.48 against 1.45, 2024 1.14 against 1.10 (derived, D10) | GUS for 2002 to 2025 (latest 2025: 1.07), Eurostat for 2000 and 2001 and for countries; the 2000/2001 values are not strictly continuous with 2002 onward | [S21][S13] |
| C7 | life expectancy and natural change | GUS and Eurostat agree: 2024 men 74.93 and 74.8, women 82.26 and 82.2; natural change 2025 both -167,483 | GUS nationally with urban/rural, Eurostat for peers; no conflict | [S14][S32][S12][S29] |
| C8 | migration | GUS registered permanent-residence net +10.9 thousand (2025); Eurostat residual +2.8 thousand (2025); Eurostat immigration 300 thousand and emigration 206 thousand (2024) | three concepts, not comparable (Eurostat flow series has a level break between 2008 and 2009); each shown separately | [S15][S20][S22] |
| C9 | households | census 2021: 2.99 persons; EU-LFS 2021: 2.5; census 2011 2.82 against 2021 2.99 contradicts the falling trend | all kept and labelled; no trend drawn from the three census points; no GUS method note found | [S18][S24][S17] |
| C10 | urban against rural definition | GUS rural 40.32% in 2021; DEGURBA rural 34.67% (census); GUS rural share rose 39.44% (2012) to 40.66% (2025) while DEGURBA surveys fell by about 6 points | GUS legal status for Poland; DEGURBA only for the European comparison; never combined | [S1][S35][S33] |
| C11 | housing stock | BDL stock 15.36 million at 31 December 2021; census 15.23 million; stock jumps in 2002, 2020, 2021 are rebasing, not construction | BDL for the series, census as a check (0.9% apart) | [S44][S48][S41] |
| C12 | house/flat measure | direct house count against proxies (individual 2.5% to 7.4% above, own use 5.0% to 15.8% below) | direct 2009 to 2025 for all comparisons; proxies only for 2000 to 2008, labelled | [S43][S42][S41] |
| C13 | 2018 definition change | a trade article says GUS changed its method in 2018; no GUS note found; own-use series moves 67.7 to 66.2 thousand (2017 to 2018) | no adjustment, because no visible national break | [S49][S41] |
| C14 | task 05 against its own CSV | task 05 text: 2025 big cities 4.8 houses per 1000, villages 4.8 flats; CSV and task 04: 1.10 houses and 0.47 flats. The text index values (houses 266.7%, flats 157.8%) do not match the CSV (275.37, 206.3) | the CSV and section 7 are authoritative; the task 05 indexes splice a proxy base (2000) with direct data (2009 on), which breaks the no-splice rule, so they are not used | [S43] |

## 9. Methods and limitations

**Method.** Population by class, stock and completions are sums over gmina-level BDL units; the national BDL value is the control total [S1][S41][S44]. Raw API extracts are cached by scripts and the small extracts are committed (`data/raw/`); processing scripts are in `scripts/`, Python standard library only. BDL anonymous limits (100 requests per 15 minutes, 1000 per 12 hours) shaped the fetch scripts [S5]. Values with BDL attribute "no data" are missing, not zero.

**Derived values**

| id | name | formula | inputs |
|---|---|---|---|
| D1 | class population or class sum | big cities = sum of 34 city gmina values; small cities = urban total minus big cities; villages = rural total; housing classes = sum over gmina-level units | S1 S41 S43 S44 S45 |
| D2 | share of total | class / national total x 100 | S1 |
| D3 | change in per cent | (end - start) / start x 100 | as cited in the line |
| D4 | per 1000 residents | value / class population at 31 December x 1000 | S1 S15 S41 S43 S44 |
| D5 | age-group share | group / all ages x 100, fine age groups only (the broad group 70+ is excluded where finer groups exist) | S8 |
| D6 | cumulative completions | sum of annual direct class values 2009 to 2025; per 1000 uses 2009 class population | S43 S1 |
| D8 | population index | value on 1 January of year / value on 1 January 2000 x 100 | S29 |
| D9 | DEGURBA census shares | class count / country total x 100 | S35 |
| D10 | difference or comparison | A minus B, or ratio as stated in the line | as cited in the line |
| D11 | rank | position of Poland among PL, CZ, SK, HU, DE, RO, LT in the latest year, 1 = highest | S29 S30 S31 S32 |
| D12 | share of three classes | class completions / sum of the three classes x 100 | S41 |
| D13 | average floor area | useful floor area / dwellings, summed over the class | S41 S43 |

**Limitations**
- **Breaks:** population rebased at the 2002, 2011 and 2021 censuses; the 2010 concept change; 2020 recalculation [S1]. Year-on-year changes at those points mix real change and rebasing. Stock jumps in 2002, 2020, 2021 [S44].
- **Territory:** the classes follow the legal status in each year; new town rights and annexations move people between villages and cities and were not corrected [S1]. The fixed 2025 list of big cities understates the class in 2000 [S1].
- **Level of detail follows the source:** age pyramid, fertility and dependency are national or urban/rural, never by place class [S8][S9][S13]; starts only for big cities against the rest, to 2019 [S46]; permits by class from 2018 only [S45]; house/flat split from 2009 only [S43].
- **Provisional values:** 2024 to 2026 Eurostat values carry flag p [S29]. The 2025 GUS values were not checked against a later revision [S1].
- **Census household and migration series** are not comparable across concepts (section 8).
- **Known data-file defect, not fixed here:** `housing_vs_population.csv` stores the `total` index rows three times per year and its indexes splice proxy and direct data; this report does not use them [S43].
- **Secondary sources** (articles, a trade press item) are used for interpretation only, never as the origin of a number [S6][S7][S27][S28][S49]. The GUS publication on the demographic situation to 2024 is listed but was not read; no figure comes from it [S25].
- **Source registry decision:** a source counts as used if it is cited in a report or appears in a data file `source_id`. Source S5 (BDL API documentation) was unused anywhere and is now cited in this report, where it defines gmina unit types; S2 was used only by a raw file and is cited in section 2 for the cross-check [S5].

## 10. Reuse

- Cite numbers with their `[S..]` source: copy the caption for the data file from `citation-sheet.md`; full references in `bibliography.md`. Both files are generated by `python3 scripts/build_reference_docs.py` and checked by `scripts/check_sources.py`.
- When reusing a derived value say it is derived and give the formula from the table in section 9.
