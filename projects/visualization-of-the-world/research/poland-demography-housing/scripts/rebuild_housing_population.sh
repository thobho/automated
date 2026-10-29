#!/bin/bash
# Rebuild housing vs population analysis
# Usage: ./scripts/rebuild_housing_population.sh

set -e

cd "$(dirname "$0")/../"

echo "Rebuilding housing vs population analysis..."

echo "Step 1: Fetching housing construction data (using placeholder data)..."
python3 scripts/fetch_bdl_housing.py

echo "Step 2: Processing housing vs population data..."
python3 scripts/process_housing_population.py

echo "Step 3: Validating sources..."
python3 scripts/check_sources.py

echo "Done! Results:"
echo "- Raw housing data: data/raw/bdl_housing_construction.csv"
echo "- Processed metrics: data/processed/housing_vs_population.csv"
echo "- Report: reports/05-housing-vs-population.md"