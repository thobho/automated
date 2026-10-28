#!/usr/bin/env python3
"""Fetch World Bank cross-check series for Poland (no key needed) -> data/raw/worldbank_poland.csv."""
import csv
import json
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "worldbank_poland.csv"
IND = {"SP.POP.TOTL": "S3", "SP.URB.TOTL": "S2", "SP.URB.TOTL.IN.ZS": "S4"}


def main():
    rows = []
    for code, sid in IND.items():
        url = f"https://api.worldbank.org/v2/country/POL/indicator/{code}?format=json&date=2000:2025&per_page=100"
        with urllib.request.urlopen(url, timeout=60) as r:
            meta, data = json.loads(r.read())
        for d in data:
            rows.append((int(d["date"]), code, "" if d["value"] is None else d["value"], sid))
    rows.sort()
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "indicator", "value", "source_id"])
        w.writerows(rows)
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
