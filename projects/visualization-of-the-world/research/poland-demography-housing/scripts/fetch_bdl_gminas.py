#!/usr/bin/env python3
"""Warm the git-ignored cache with gmina-level (unit-level 6) BDL series used by process_structure.py.

Variables: 60641 population total (31 Dec); 80125 net internal migration for permanent residence.
About 42 requests (100 units per page) per variable, ~10 s each.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bdl  # noqa: E402

GMINA_VARS = {
    60641: range(2000, 2026),
    80125: range(2000, 2026),
}
# Not fetched (time-boxed, ~42 requests each at ~10 s): 80108 net migration abroad, 1652549/1652555 households 2021
# at gmina level. Add them here to extend migration_by_place_class.csv (international) and households.csv (by class).


# BDL attribute ids meaning "no number" (0 / x / a / X / - / n): the value field is a placeholder 0, not a real zero.
NO_VALUE_ATTRS = {0, 4, 7, 14, 15, 17, 50, 91}


def load_gmina_var(vid, years, skip_missing=False):
    """{unit_id: (name, {year: value})} for all gmina-level units (types 1-5), cached.
    skip_missing=True drops values whose BDL attribute says "no data" (attrId in NO_VALUE_ATTRS) instead of keeping the placeholder 0."""
    out = {}
    params = [("unit-level", 6)] + [("year", y) for y in years]
    for r in bdl.paged(f"/data/by-variable/{vid}", params):
        out[r["id"]] = (r["name"], {int(v["year"]): v.get("val") for v in r["values"]
                                    if not (skip_missing and v.get("attrId") in NO_VALUE_ATTRS)})
    return out


if __name__ == "__main__":
    for vid, years in GMINA_VARS.items():
        d = load_gmina_var(vid, years)
        print(vid, len(d), "units", flush=True)
