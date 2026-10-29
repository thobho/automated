#!/usr/bin/env python3
"""Process housing construction and population data to create the housing vs population comparison.

Creates the core comparison metrics:
- New dwellings per 1,000 inhabitants, houses and flats separately (2000-2025)
- New dwellings per additional resident (5-year windows)
- Share of houses vs flats in new construction per class over time
- Indexed dynamics (2000 = 100) of population, houses and flats per class
"""

import csv
from collections import defaultdict
from pathlib import Path

PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"

def read_population_by_class():
    """Read population data by class."""
    data = defaultdict(dict)
    with open(PROCESSED / "population_by_class.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["year"])
            class_name = row["class"]
            population = int(float(row["population"])) if row["population"] else 0
            data[year][class_name] = population
    return data

def read_housing_completions_by_class():
    """Read housing completions data by class."""
    data = defaultdict(lambda: defaultdict(dict))
    with open(PROCESSED / "housing_completions_by_class.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["year"])
            class_name = row["class"]
            dwelling_type = row["type"]
            basis = row["basis"]
            
            # Convert dwellings to integer, handling empty values
            dwellings = int(float(row["dwellings"])) if row["dwellings"] else 0
            
            # Store data by year, class, type and basis
            data[year][class_name][f"{dwelling_type}_{basis}"] = dwellings
            
    return data

def get_direct_housing_data_for_year(housing_data, year, class_name):
    """Get direct housing data for a specific year and class."""
    if year not in housing_data or class_name not in housing_data[year]:
        return None, None
    
    year_data = housing_data[year][class_name]
    
    # Look for direct data first (2009-2025)
    house_direct = year_data.get("house_direct", 0)
    flat_direct = year_data.get("flat_direct", 0)
    
    # If no direct data, use proxy data (2000-2008)
    if house_direct == 0 and flat_direct == 0:
        # Use appropriate proxy based on year
        if year <= 2008:
            # Use individual proxy for 2000-2008
            house_direct = year_data.get("house_proxy_individual_proxy", 0)
            flat_direct = year_data.get("flat_proxy_non_individual_proxy", 0)
        elif year >= 2005:
            # Use own-use proxy for 2005-2008
            house_direct = year_data.get("house_proxy_own_use_proxy", 0)
            flat_direct = year_data.get("flat_proxy_not_own_use_proxy", 0)
    
    return house_direct, flat_direct

def calculate_dwellings_per_1000(population_data, housing_data):
    """Calculate new dwellings per 1,000 inhabitants."""
    results = []
    
    for year in range(2000, 2026):
        if year not in population_data:
            continue
            
        for class_name in ["big_cities", "small_cities", "villages"]:
            if class_name not in population_data[year]:
                continue
                
            population = population_data[year][class_name]
            if population == 0:
                continue
                
            # Get housing data for the year and class
            if year not in housing_data or class_name not in housing_data[year]:
                continue
                
            year_data = housing_data[year][class_name]
            
            # Determine which data to use based on year
            if year >= 2009:
                # Use direct data for 2009-2025
                house_value = year_data.get("house_direct", 0)
                flat_value = year_data.get("flat_direct", 0)
                house_source = "S43"  # Direct house data source
                flat_source = "S43"   # Direct flat data source
            else:
                # Use proxy data for 2000-2008
                if year <= 2004:
                    # Use individual proxy
                    house_value = year_data.get("house_proxy_individual_proxy", 0)
                    flat_value = year_data.get("flat_proxy_non_individual_proxy", 0)
                    house_source = "S42"  # Individual proxy source
                    flat_source = "S41;S42"  # Non-individual proxy uses both sources
                else:
                    # Use own-use proxy for 2005-2008
                    house_value = year_data.get("house_proxy_own_use_proxy", 0)
                    flat_value = year_data.get("flat_proxy_not_own_use_proxy", 0)
                    house_source = "S41"  # Own-use proxy source
                    flat_source = "S41"    # Not-own-use proxy source
            
            # Calculate for flats per 1000 inhabitants
            if flat_value > 0:
                flats_per_1000 = (flat_value / population) * 1000
                results.append({
                    "year": year,
                    "class": class_name,
                    "measure": "flats_per_1000",
                    "value": round(flats_per_1000, 2),
                    "source_id": flat_source,
                    "notes": "proxy_individual" if year <= 2008 and year >= 2009 else ("proxy_own_use" if year >= 2005 and year <= 2008 else "")
                })
            
            # Calculate for houses per 1000 inhabitants
            if house_value > 0:
                houses_per_1000 = (house_value / population) * 1000
                results.append({
                    "year": year,
                    "class": class_name,
                    "measure": "houses_per_1000",
                    "value": round(houses_per_1000, 2),
                    "source_id": house_source,
                    "notes": "proxy_individual" if year <= 2008 and year >= 2009 else ("proxy_own_use" if year >= 2005 and year <= 2008 else "")
                })
                
    return results

def calculate_five_year_changes(population_data, housing_data):
    """Calculate new dwellings per additional resident over 5-year windows."""
    results = []
    
    for year in range(2005, 2026):
        prev_year = year - 5
        
        if prev_year not in population_data or year not in population_data:
            continue
            
        for class_name in ["big_cities", "small_cities", "villages"]:
            if (class_name not in population_data[prev_year] or 
                class_name not in population_data[year]):
                continue
                
            # Population change
            pop_prev = population_data[prev_year][class_name]
            pop_current = population_data[year][class_name]
            pop_change = pop_current - pop_prev
            
            # Get housing data for both years
            if (prev_year not in housing_data or class_name not in housing_data[prev_year] or
                year not in housing_data or class_name not in housing_data[year]):
                continue
                
            prev_data = housing_data[prev_year][class_name]
            current_data = housing_data[year][class_name]
            
            # Determine which data to use based on year range
            if prev_year >= 2009 and year >= 2009:
                # Use direct data for both years
                flats_prev = prev_data.get("flat_direct", 0)
                flats_current = current_data.get("flat_direct", 0)
                houses_prev = prev_data.get("house_direct", 0)
                houses_current = current_data.get("house_direct", 0)
                source_id = "S43"  # Direct data source
            elif prev_year <= 2008 and year <= 2008:
                # Use proxy data for both years (individual proxy)
                flats_prev = prev_data.get("flat_proxy_non_individual_proxy", 0)
                flats_current = current_data.get("flat_proxy_non_individual_proxy", 0)
                houses_prev = prev_data.get("house_proxy_individual_proxy", 0)
                houses_current = current_data.get("house_proxy_individual_proxy", 0)
                source_id = "S41;S42"  # Proxy sources
            elif prev_year <= 2008 and year >= 2009:
                # Mixed: proxy to direct transition
                # For simplicity, we'll use direct data for both years in this case
                flats_prev = prev_data.get("flat_direct", 0) if "flat_direct" in prev_data else 0
                flats_current = current_data.get("flat_direct", 0)
                houses_prev = prev_data.get("house_direct", 0) if "house_direct" in prev_data else 0
                houses_current = current_data.get("house_direct", 0)
                source_id = "S43"  # Direct data source
            else:
                # Other combinations, use direct data
                flats_prev = prev_data.get("flat_direct", 0)
                flats_current = current_data.get("flat_direct", 0)
                houses_prev = prev_data.get("house_direct", 0)
                houses_current = current_data.get("house_direct", 0)
                source_id = "S43"  # Direct data source
            
            # Housing construction change
            flats_change = flats_current - flats_prev
            houses_change = houses_current - houses_prev
            
            # Calculate ratios (avoid division by zero)
            if pop_change != 0:
                flats_per_pop_change = flats_change / abs(pop_change) if pop_change != 0 else 0
                houses_per_pop_change = houses_change / abs(pop_change) if pop_change != 0 else 0
                
                results.append({
                    "period_start": prev_year,
                    "period_end": year,
                    "class": class_name,
                    "measure": "flats_per_pop_change",
                    "value": round(flats_per_pop_change, 2),
                    "pop_change": pop_change,
                    "housing_change": flats_change,
                    "source_id": source_id,
                    "notes": ""
                })
                
                results.append({
                    "period_start": prev_year,
                    "period_end": year,
                    "class": class_name,
                    "measure": "houses_per_pop_change",
                    "value": round(houses_per_pop_change, 2),
                    "pop_change": pop_change,
                    "housing_change": houses_change,
                    "source_id": source_id,
                    "notes": ""
                })
                
    return results

def calculate_housing_shares(housing_data):
    """Calculate share of houses vs flats in new construction over time."""
    results = []
    
    for year in range(2000, 2026):
        if year not in housing_data:
            continue
            
        # Calculate total for all classes combined
        total_houses = 0
        total_flats = 0
        
        for class_name in ["big_cities", "small_cities", "villages"]:
            if class_name not in housing_data[year]:
                continue
                
            year_data = housing_data[year][class_name]
            
            # Use direct data only for share calculation (2009-2025)
            if year >= 2009:
                house_value = year_data.get("house_direct", 0)
                flat_value = year_data.get("flat_direct", 0)
                total_houses += house_value
                total_flats += flat_value
            # For 2000-2008, we could use proxy data, but the requirement is to use direct data only for shares
            # So we'll skip these years for share calculation
            
        # Only calculate shares for years with direct data (2009-2025)
        if year >= 2009 and (total_houses + total_flats) > 0:
            total = total_houses + total_flats
            flats_share = (total_flats / total) * 100
            houses_share = (total_houses / total) * 100
            
            results.append({
                "year": year,
                "class": "total",
                "measure": "flats_share_percent",
                "value": round(flats_share, 2),
                "source_id": "S43",  # Direct data source
                "notes": ""
            })
            
            results.append({
                "year": year,
                "class": "total",
                "measure": "houses_share_percent",
                "value": round(houses_share, 2),
                "source_id": "S43",  # Direct data source
                "notes": ""
            })
        
    return results

def calculate_indexed_dynamics(population_data, housing_data):
    """Calculate indexed dynamics (2000 = 100) of population, houses and flats per class."""
    results = []
    
    # Base values for 2000
    base_population = {}
    base_housing = {"flats": {}, "houses": {}}
    
    # Initialize base values for each class
    for class_name in ["big_cities", "small_cities", "villages"]:
        base_population[class_name] = 0
        base_housing["flats"][class_name] = 0
        base_housing["houses"][class_name] = 0
    
    # Get base values for 2000
    if 2000 in population_data:
        for class_name in ["big_cities", "small_cities", "villages"]:
            if class_name in population_data[2000]:
                base_population[class_name] = population_data[2000][class_name]
    
    if 2000 in housing_data:
        for class_name in ["big_cities", "small_cities", "villages"]:
            if class_name in housing_data[2000]:
                year_2000_data = housing_data[2000][class_name]
                # For 2000, we use proxy data since direct data starts in 2009
                base_housing["flats"][class_name] = year_2000_data.get("flat_proxy_non_individual_proxy", 0)
                base_housing["houses"][class_name] = year_2000_data.get("house_proxy_individual_proxy", 0)
    
    # Calculate indexes for all years
    for year in range(2000, 2026):
        # Population index
        if year in population_data:
            for class_name in ["big_cities", "small_cities", "villages"]:
                if class_name in population_data[year] and class_name in base_population:
                    if base_population[class_name] > 0:
                        pop_index = (population_data[year][class_name] / base_population[class_name]) * 100
                        results.append({
                            "year": year,
                            "class": class_name,
                            "measure": "population_index",
                            "value": round(pop_index, 2),
                            "source_id": "S1",
                            "notes": ""
                        })
        
        # Housing indexes - calculate separately for each class
        if year in housing_data:
            for class_name in ["big_cities", "small_cities", "villages"]:
                if class_name in housing_data[year]:
                    year_data = housing_data[year][class_name]
                    
                    # Determine which data to use based on year
                    if year >= 2009:
                        # Use direct data for 2009-2025
                        flats_value = year_data.get("flat_direct", 0)
                        houses_value = year_data.get("house_direct", 0)
                        flats_source = "S43"
                        houses_source = "S43"
                    else:
                        # Use proxy data for 2000-2008
                        flats_value = year_data.get("flat_proxy_non_individual_proxy", 0)
                        houses_value = year_data.get("house_proxy_individual_proxy", 0)
                        flats_source = "S41;S42"
                        houses_source = "S42"
                    
                    # Calculate flats index
                    if base_housing["flats"][class_name] > 0:
                        flats_index = (flats_value / base_housing["flats"][class_name]) * 100
                        results.append({
                            "year": year,
                            "class": class_name,
                            "measure": "flats_index",
                            "value": round(flats_index, 2),
                            "source_id": flats_source,
                            "notes": "proxy_individual" if year <= 2008 else ""
                        })
                    
                    # Calculate houses index
                    if base_housing["houses"][class_name] > 0:
                        houses_index = (houses_value / base_housing["houses"][class_name]) * 100
                        results.append({
                            "year": year,
                            "class": class_name,
                            "measure": "houses_index",
                            "value": round(houses_index, 2),
                            "source_id": houses_source,
                            "notes": "proxy_individual" if year <= 2008 else ""
                        })
                        
                    # Also calculate total indexes (across all classes)
                    if year == 2000:
                        # Set base values for total indexes
                        base_housing["flats"]["total"] = 0
                        base_housing["houses"]["total"] = 0
                        for c in ["big_cities", "small_cities", "villages"]:
                            if c in housing_data[2000] and c in base_housing["flats"]:
                                base_housing["flats"]["total"] += base_housing["flats"][c]
                                base_housing["houses"]["total"] += base_housing["houses"][c]
                    
                    # Total indexes (sum across all classes)
                    if "total" in base_housing["flats"] and base_housing["flats"]["total"] > 0:
                        total_flats = 0
                        total_houses = 0
                        
                        for c in ["big_cities", "small_cities", "villages"]:
                            if c in housing_data[year]:
                                c_data = housing_data[year][c]
                                if year >= 2009:
                                    total_flats += c_data.get("flat_direct", 0)
                                    total_houses += c_data.get("house_direct", 0)
                                else:
                                    total_flats += c_data.get("flat_proxy_non_individual_proxy", 0)
                                    total_houses += c_data.get("house_proxy_individual_proxy", 0)
                        
                        total_flats_index = (total_flats / base_housing["flats"]["total"]) * 100
                        total_houses_index = (total_houses / base_housing["houses"]["total"]) * 100
                        
                        results.append({
                            "year": year,
                            "class": "total",
                            "measure": "flats_index",
                            "value": round(total_flats_index, 2),
                            "source_id": flats_source if year >= 2009 else "S41;S42",
                            "notes": "proxy_individual" if year <= 2008 else ""
                        })
                        
                        results.append({
                            "year": year,
                            "class": "total",
                            "measure": "houses_index",
                            "value": round(total_houses_index, 2),
                            "source_id": houses_source if year >= 2009 else "S42",
                            "notes": "proxy_individual" if year <= 2008 else ""
                        })
    
    return results

def main():
    # Read data
    population_data = read_population_by_class()
    housing_data = read_housing_completions_by_class()
    
    # Calculate metrics
    dwellings_per_1000 = calculate_dwellings_per_1000(population_data, housing_data)
    five_year_changes = calculate_five_year_changes(population_data, housing_data)
    housing_shares = calculate_housing_shares(housing_data)
    indexed_dynamics = calculate_indexed_dynamics(population_data, housing_data)
    
    # Write results to CSV files
    output_file = PROCESSED / "housing_vs_population.csv"
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["year", "class", "measure", "value", "source_id", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write dwellings per 1000 inhabitants
        for row in dwellings_per_1000:
            writer.writerow(row)
            
        # Write five-year changes
        for row in five_year_changes:
            writer.writerow({
                "year": f"{row['period_start']}-{row['period_end']}",
                "class": row["class"],
                "measure": row["measure"],
                "value": row["value"],
                "source_id": row["source_id"],
                "notes": f"pop_change={row['pop_change']}, housing_change={row['housing_change']}" + (f", {row['notes']}" if row['notes'] else "")
            })
            
        # Write housing shares
        for row in housing_shares:
            writer.writerow(row)
            
        # Write indexed dynamics
        for row in indexed_dynamics:
            writer.writerow(row)
    
    print(f"Processed housing vs population data and saved to {output_file}")
    print(f"Generated {len(dwellings_per_1000) + len(five_year_changes) + len(housing_shares) + len(indexed_dynamics)} data points")

if __name__ == "__main__":
    main()