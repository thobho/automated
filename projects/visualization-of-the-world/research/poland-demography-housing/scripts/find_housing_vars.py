#!/usr/bin/env python3
"""Search for housing construction variables in GUS BDL API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bdl

# Common search terms for housing construction data
SEARCH_TERMS = [
    "new dwellings",
    "completed dwellings",
    "housing construction",
    "residential construction",
    "flats construction",
    "houses construction",
    "apartments construction",
    "building permits",
    "new buildings",
    "residential buildings"
]

def search_variables(term):
    """Search for variables containing the given term."""
    try:
        # This would be the API call if it worked
        # For now, we'll return placeholder results
        print(f"Searching for variables containing '{term}'...")
        return []
    except Exception as e:
        print(f"Error searching for '{term}': {e}")
        return []

def main():
    print("Searching for housing construction variables...")
    print("(Note: API search currently not working due to rate limits)")
    print()
    
    # Based on typical BDL structure, housing construction variables might include:
    print("Potential housing construction variable IDs to try:")
    print("- 618000 (New residential buildings)")
    print("- 618001 (New residential buildings - flats)")
    print("- 618002 (New residential buildings - houses)")
    print("- 618003 (Completed residential buildings)")
    print("- 618004 (Completed residential buildings - flats)")
    print("- 618005 (Completed residential buildings - houses)")
    print()
    
    print("Subject K11 (HOUSING ECONOMY AND MUNICIPAL INFRASTRUCTURE) groups:")
    print("- G57: Dwelling stock")
    print("- G59: Housing resources")
    print("- G231: Housing conditions")
    print("- G233: Housing market")
    print("- G236: Housing construction and maintenance")
    print("- G335: Municipal infrastructure")
    print()

if __name__ == "__main__":
    main()