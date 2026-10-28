#!/usr/bin/env python3
"""Warm the git-ignored cache with gmina-level (unit-level 6) BDL series used by process_structure.py.

Variables: 60641 population total (31 Dec); 80125 net internal migration for permanent residence;
80108 net migration abroad (permanent residence); 1652549 households (census 2021);
1652555 population in households (census 2021). Roughly 25 requests per variable.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bdl  # noqa: E402

GMINA_VARS = {
    60641: range(2000, 2026),
    80125: range(2000, 2026),
    80108: range(2000, 2026),
    1652549: [2021],
    1652555: [2021],
}


def load_gmina_var(vid, years):
    """{unit_id: (name, {year: value})} for all gmina-level units (types 1-5), cached."""
    out = {}
    params = [("unit-level", 6)] + [("year", y) for y in years]
    for r in bdl.paged(f"/data/by-variable/{vid}", params):
        out[r["id"]] = (r["name"], {int(v["year"]): v.get("val") for v in r["values"]})
    return out


if __name__ == "__main__":
    for vid, years in GMINA_VARS.items():
        d = load_gmina_var(vid, years)
        print(vid, len(d), "units", flush=True)
