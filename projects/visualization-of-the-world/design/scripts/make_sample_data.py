#!/usr/bin/env python3
"""Write sample/sample-data.json: ILLUSTRATIVE numbers for the style guide only.

These are made-up smooth curves so the charts have something to draw. They are not
GUS data and must never be quoted. The real datasets live in research/ and the site.
"""
import json
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample", "sample-data.json")

VOIVODESHIPS = [
    # code, name, tile column, tile row, base share of village population (made up)
    ("ZP", "Zachodniopomorskie", 0, 0, 31), ("PM", "Pomorskie", 1, 0, 34), ("WN", "Warmińsko-Mazurskie", 2, 0, 41),
    ("PD", "Podlaskie", 3, 0, 39), ("LB", "Lubuskie", 0, 1, 35), ("WP", "Wielkopolskie", 1, 1, 44),
    ("KP", "Kujawsko-Pomorskie", 2, 1, 39), ("MZ", "Mazowieckie", 3, 1, 34), ("DS", "Dolnośląskie", 0, 2, 30),
    ("OP", "Opolskie", 1, 2, 47), ("LD", "Łódzkie", 2, 2, 36), ("SK", "Świętokrzyskie", 3, 2, 54),
    ("LU", "Lubelskie", 4, 2, 53), ("SL", "Śląskie", 1, 3, 23), ("MA", "Małopolskie", 2, 3, 51), ("PK", "Podkarpackie", 3, 3, 58),
]


def main():
    years = list(range(2000, 2025))
    t = [(y - 2000) / 24 for y in years]
    series = {
        "big-cities": [round(31.5 - 2.2 * x + 0.4 * math.sin(6 * x), 1) for x in t],
        "small-cities": [round(30.2 - 1.6 * x + 0.3 * math.cos(5 * x), 1) for x in t],
        "villages": [round(38.3 + 3.8 * x - 0.5 * math.sin(4 * x), 1) for x in t],
    }
    regions = []
    for i, (code, name, col, row, base) in enumerate(VOIVODESHIPS):
        values = [round(base + (3.5 if base < 40 else 1.5) * x + 0.6 * math.sin(i + 5 * x), 1) for x in t]
        if code == "OP":
            values = [None if y < 2006 else v for y, v in zip(years, values)]  # demo of missing values
        change = round((values[-1] - values[-11]) / values[-11] * 100 * 1.5 - 3.5, 1)
        regions.append({"code": code, "name": name, "col": col, "row": row, "values": values, "change": change})
    data = {
        "illustrative": True,
        "note": "Made-up numbers for the design-system style guide. Not real data - do not quote.",
        "years": years,
        "placeShare": {"unit": "% ludności", "series": series},
        "regions": regions,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
