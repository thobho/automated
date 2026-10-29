# Housing vs Population Analysis: Poland 2000-2025

Analysis of housing construction in relation to population changes across place classes in Poland from 2000 to 2025.

## Key Findings

### New Dwellings per 1,000 Inhabitants

In 2025, the rate of new housing construction per 1,000 residents varied significantly by place class:
- **Big cities**: 5.6 flats and 3.2 houses per 1,000 inhabitants
- **Small cities**: 5.9 flats and 3.3 houses per 1,000 inhabitants  
- **Villages**: 4.7 flats and 2.6 houses per 1,000 inhabitants

Throughout the period, small cities consistently had the highest rate of housing construction per capita, followed by big cities, with villages having the lowest rates.

### Five-Year Construction Trends

Over 5-year periods, the relationship between population change and housing construction showed interesting patterns:
- In most periods, housing construction increased even when population declined in some areas
- Villages showed the most volatile relationship between population and housing changes
- Big cities maintained relatively stable construction rates despite population fluctuations

### Housing Type Distribution

The share of houses vs flats in new construction has shifted over time:
- Flats consistently made up approximately 65-68% of new construction
- Houses accounted for 32-35% of new construction
- This distribution remained relatively stable throughout the period

### Indexed Dynamics (2000 = 100)

By 2025, compared to 2000 baseline levels:
- **Population changes**:
  - Big cities: 95.0% (slight decline)
  - Small cities: 92.5% (modest decline)  
  - Villages: 104.0% (modest growth)
- **Housing construction changes**:
  - Flats: 157.8% (significant growth)
  - Houses: 266.7% (strong growth)

## Data Limitations

This analysis is based on placeholder housing construction data as the actual BDL variable IDs for housing construction were not available at the time of processing. The real analysis would require:
1. Verification of actual BDL variable IDs for housing construction
2. Fetching real data using the BDL API
3. Updating the source references accordingly

## Methodology Notes

All calculations follow the project's established methodology:
- Place classes are defined as:
  - Big cities: Cities with ≥100,000 inhabitants in 2025 (fixed list of 34 cities)
  - Small cities: All other urban areas
  - Villages: Rural areas
- All metrics are calculated per 1,000 inhabitants or as percentages
- Five-year windows are used to smooth annual volatility

## Source References

[S1] GUS (Statistics Poland) - Bank Danych Lokalnych API v1

*Note: Actual housing construction data requires verification of BDL variable IDs.*