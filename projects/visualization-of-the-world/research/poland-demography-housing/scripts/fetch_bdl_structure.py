#!/usr/bin/env python3
"""Fetch national-level (unit 000000000000) BDL series for the structure report into data/raw/bdl_structure_national.csv.

Columns: subject_id,variable_id,n1,n2,n3,year,value. One request returns up to 20 variables (by-unit endpoint).
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bdl  # noqa: E402

RAW = bdl.ROOT / "data" / "raw"
NATIONAL = "000000000000"
ALL = list(range(2000, 2026))
PYRAMID_YEARS = [2000, 2010, 2020, 2025]
# subject -> (years, variable filter: None = all variables of the subject, or a set of ids)
PLAN = {
    "P2137": (PYRAMID_YEARS, None),          # population by sex and 5-year age group
    "P2426": (ALL, None),                    # demographic dependency ratios, ageing ratio
    "P3361": (ALL, None),                    # pre-/working/post-working age population, urban/rural
    "P3814": (ALL, None),                    # median age by sex
    "P3813": (ALL, None),                    # median age by sex, urban/rural
    "P1873": (ALL, {59, 60, 61, 65, 66, 67, 62}),   # live births, deaths, infant deaths
    "P3992": (ALL, None),                    # births, deaths, natural increase, urban/rural
    "P3428": (ALL, None),                    # per 1000 population
    "P2346": (ALL, None),                    # fertility (total fertility rate) and gross reproduction
    "P2730": (ALL, {101554, 101551, 101548, 101555, 101552, 101549}),  # life expectancy at birth
    "P1350": (ALL, {1365224, 80121, 80122, 1365229, 80123, 80124, 1365234, 80125, 80108}),
    "P4287": ([2021], None),                 # households by size, census 2021
    "P2115": ([2002], None),                 # households by type, census 2002
    "P2871": ([2002], None),                 # households by size, census 2002
    "P3420": ([2011], None),                 # households by size, census 2011 (numerical data)
}


def variables(subject):
    return list(bdl.paged("/variables", {"subject-id": subject}))


def main():
    rows = []
    for subject, (years, keep) in PLAN.items():
        vs = [v for v in variables(subject) if keep is None or v["id"] in keep]
        if subject == "P3420":
            vs = [v for v in vs if v.get("n2") == "numerical data"]
        for i in range(0, len(vs), 20):
            chunk = vs[i:i + 20]
            params = [("var-id", v["id"]) for v in chunk] + [("year", y) for y in years]
            # by-unit responses are paged: follow every page or variables are silently dropped
            by_id = {r["id"]: r for r in bdl.paged(f"/data/by-unit/{NATIONAL}", params)}
            for v in chunk:
                for val in by_id.get(v["id"], {}).get("values", []):
                    rows.append((subject, v["id"], v.get("n1") or "", v.get("n2") or "", v.get("n3") or "",
                                 int(val["year"]), "" if val.get("val") is None else val["val"]))
        print(subject, len(vs), "variables", flush=True)
    rows.sort(key=lambda r: (r[0], r[1], r[5]))
    with open(RAW / "bdl_structure_national.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["subject_id", "variable_id", "n1", "n2", "n3", "year", "value"])
        w.writerows(rows)
    print("rows", len(rows))


if __name__ == "__main__":
    main()
