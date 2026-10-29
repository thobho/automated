# Housing vs Population Analysis: Poland 2000-2025

Analysis of housing construction in relation to population changes across place classes in Poland from 2000 to 2025.

## Key Findings

### New Dwellings per 1,000 Inhabitants

In 2025, the rate of new housing construction per 1,000 residents varied significantly by place class:
- **Big cities**: 6.8 flats and 4.8 houses per 1,000 inhabitants
- **Small cities**: 5.3 flats and 3.4 houses per 1,000 inhabitants  
- **Villages**: 4.8 flats and 3.4 houses per 1,000 inhabitants

Throughout the period, big cities consistently had the highest rate of housing construction per capita for flats, while small cities led in house construction rates. Villages generally had the lowest rates, though they experienced significant growth in the 2010s.

### Five-Year Construction Trends

Over 5-year periods, the relationship between population change and housing construction showed interesting patterns:
- In most periods, housing construction increased even when population declined in some areas
- Villages showed the most volatile relationship between population and housing changes
- Big cities maintained relatively stable construction rates despite population fluctuations
- The ratio of new dwellings to population change varied significantly by period and place class

### Housing Type Distribution

The share of houses vs flats in new construction (using direct data from 2009-2025):
- Flats consistently made up approximately 50-56% of new construction
- Houses accounted for 44-50% of new construction
- This distribution shows more balance than previously assumed, with a slight shift toward flats in recent years

### Indexed Dynamics (2000 = 100)

By 2025, compared to 2000 baseline levels:
- **Population changes**:
  - Big cities: 95.0% (slight decline)
  - Small cities: 92.5% (modest decline)  
  - Villages: 104.0% (modest growth)
- **Housing construction changes** (using proxy data for 2000-2008, direct for 2009-2025):
  - Flats: 157.8% (significant growth)
  - Houses: 266.7% (strong growth)

## Data Limitations

While this analysis uses real BDL data, several important limitations remain:
1. **Proxy vs Direct Data**: 2000-2008 values use proxy columns due to lack of direct data, while 2009-2025 use direct measurements. This affects comparability over the full period.
2. **Data Gaps**: Some combinations of place class and year have missing values due to data availability in source datasets.
3. **Methodological Changes**: GUS changed definitions around 2018, potentially affecting comparability (see task 04 methodology notes).

## Methodology Notes

All calculations follow the project's established methodology:
- Place classes are defined as:
  - Big cities: Cities with ≥100,000 inhabitants in 2025 (fixed list of 34 cities)
  - Small cities: All other urban areas
  - Villages: Rural areas
- All metrics are calculated per 1,000 inhabitants or as percentages
- Five-year windows are used to smooth annual volatility
- Source attribution distinguishes between direct data (S43) and proxy data (S41, S42)

## Source References

[S1] GUS (Statistics Poland) - Population by place of residence
[S41] GUS (Statistics Poland) - Dwellings completed: total and by form of construction (variable 748601, 748604)
[S42] GUS (Statistics Poland) - Dwellings completed by forms of construction (variable 430)
[S43] GUS (Statistics Poland) - Dwellings completed by building type (variables 748247, 748250)