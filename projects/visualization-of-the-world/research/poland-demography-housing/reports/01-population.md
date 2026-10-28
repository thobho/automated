# 01 - Population by place class, Poland 2000-2025

Latest year available: **2025** (31 December, GUS BDL [S1]). Class definitions and method: see `../README.md`. All class figures below are derived in `data/processed/population_by_class.csv` from GUS BDL data [S1]; big cities = the 34 cities with at least 100,000 inhabitants in 2025 (fixed list).

## Trend
- **Total population** fell from 38.25 million in 2000 to 37.33 million in 2025 [S1]. Over the same years the World Bank/UN series shows 38.26 million falling to 36.44 million [S3]; the two differ in method, and GUS is used throughout.
- **Urbanization rate** (urban share of the population) fell from 61.85% in 2000 to 59.34% in 2025 [S1]. The World Bank series shows 61.75% for 2000 and 60.09% for 2025 [S4]; it is not a GUS definition and the 2025 values diverge, so it is a cross-check only.
- **Villages** grew from 14.59 million (38.15% of the total) in 2000 to 15.18 million (40.66%) in 2025 [S1], the only class that grew. Most of the growth came in two steps: 2009 to 2010 (+224 thousand, see data breaks) and a steady rise to 2019 (15.35 million) [S1]. Villages then declined slightly, to 15.18 million in 2025 [S1].
- **Small cities and towns** shrank from 13.05 million (34.10%) in 2000 to 12.07 million (32.33%) in 2025 [S1], a loss of about 0.98 million.
- **Big cities (fixed list of 34)** shrank from 10.61 million (27.75%) in 2000 to 10.08 million (27.01%) in 2025 [S1]. Their share has been broadly flat since about 2010 (26.87% in 2010, 27.01% in 2025) [S1]; the 2020 uptick (26.78% to 27.05%) coincides with GUS recalculating its series on the 2021 census [S1].
- **Number of cities with at least 100,000 inhabitants in the given year** fell from 41 in 2000 to 34 in 2025 [S1] (derived: count of urban gminas at or above the threshold). The 7 cities that dropped out are Chorzów, Kalisz, Legnica, Wałbrzych, Grudziądz, Włocławek and Słupsk (all below 100,000 in 2025) [S1]; no city entered the class (derived by comparing 2000 and 2025 gmina values).

## Reading the numbers
- Direction of change is consistent with the literature on suburbanisation: migration flows from large cities into surrounding municipalities [S6][S7]. Our data cannot separate suburban villages from remote ones, so this is context, not a finding of this dataset.
- Treat year-on-year changes at 2002, 2010 and 2020 with caution (census rebasing and methodology changes); see "known data breaks" in the README.
