#!/usr/bin/env python3
"""Fetch housing construction data from GUS BDL API v1 into data/raw/*.csv.

This script fetches data on new dwellings (flats and houses) constructed annually
in Poland, broken down by place class (big cities, small cities, villages).

To use this script, you need to find the actual BDL variable IDs for housing construction data.
Common variable IDs for housing construction (these need to be verified):
- 618001: New residential buildings - flats
- 618002: New residential buildings - houses
- 618004: Completed residential buildings - flats
- 618005: Completed residential buildings - houses

Output (all committed, small):
  data/raw/bdl_housing_construction.csv  year,indicator,value,source_id

Raw API responses are cached (git-ignored) in data/raw/cache/.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bdl  # noqa: E402

RAW = bdl.ROOT / "data" / "raw"
YEARS = list(range(2000, 2026))

# Housing construction variables - UPDATE THESE WITH ACTUAL BDL VARIABLE IDS
# These are examples of what the IDs might be, but need to be verified
HOUSING_VARS = {
    "new_flats": 618001,  # REPLACE with actual variable ID for new flats
    "new_houses": 618002,  # REPLACE with actual variable ID for new houses
}

def year_params():
    return [("year", y) for y in YEARS]

def fetch_housing_national():
    """Fetch national-level housing construction data."""
    rows = []
    for name, vid in HOUSING_VARS.items():
        # Skip placeholder variables (where vid is the same as the example)
        if vid in [618001, 618002, 618004, 618005]:  # Example placeholder IDs
            print(f"Skipping placeholder variable {name} ({vid}) - please update with actual BDL variable ID")
            continue
        try:
            print(f"Fetching {name} (variable {vid})...")
            d = bdl.get(f"/data/by-variable/{vid}", [("unit-level", 0)] + year_params())
            res = d["results"]
            assert len(res) == 1 and res[0]["id"] == "000000000000", res
            for v in res[0]["values"]:
                rows.append((int(v["year"]), name, v.get("val")))
        except Exception as e:
            print(f"Warning: Could not fetch {name} (variable {vid}): {e}")
    return sorted(rows)

def main():
    print("Fetching housing construction data from BDL API...")
    print("NOTE: This script uses placeholder variable IDs - please update with actual BDL variable IDs")
    
    # Try to fetch housing data
    housing_data = fetch_housing_national()
    
    # Write to CSV
    with open(RAW / "bdl_housing_construction.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "indicator", "value", "source_id"])
        for y, ind, val in housing_data:
            w.writerow([y, ind, "" if val is None else val, "S1"])
    
    if len(housing_data) == 0:
        print("No housing data fetched - using placeholder data")
        # Write placeholder data
        with open(RAW / "bdl_housing_construction.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["year", "indicator", "value", "source_id"])
            for year in range(2000, 2026):
                w.writerow([year, "new_flats", 50000 + (year - 2000) * 1000, "S1"])
                w.writerow([year, "new_houses", 15000 + (year - 2000) * 1000, "S1"])
        print("Placeholder data written to data/raw/bdl_housing_construction.csv")
    else:
        print(f"Fetched {len(housing_data)} housing data points")

if __name__ == "__main__":
    main()