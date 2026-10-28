#!/usr/bin/env python3
"""Fail (exit 1) if any data file has an empty or unknown source_id.

Checks every CSV under data/ (except data/raw/cache) that has a `source_id`
column: each non-empty cell, split on ';', must be an id in sources.csv.
Also fails if a CSV under data/processed has no `source_id` column, if
sources.csv has duplicate ids, or if a report cites an unknown [S..] key.
Standard library only.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_COLUMNS = ["id", "title", "publisher", "url", "indicator_or_table_code",
                   "accessed", "type", "notes"]


def load_sources(path):
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != SOURCES_COLUMNS:
            raise ValueError(f"{path}: columns must be {SOURCES_COLUMNS}, got {rd.fieldnames}")
        rows = list(rd)
    ids = [r["id"] for r in rows]
    dup = {i for i in ids if ids.count(i) > 1}
    errors = [f"{path}: duplicate source id {i}" for i in sorted(dup)]
    for r in rows:
        if r["type"] not in ("primary", "secondary"):
            errors.append(f"{path}: {r['id']}: type must be primary or secondary")
        if not r["url"].startswith("http"):
            errors.append(f"{path}: {r['id']}: url missing")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["accessed"]):
            errors.append(f"{path}: {r['id']}: accessed must be YYYY-MM-DD")
    return set(ids), errors


def check_csv(path, known):
    errors = []
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if "source_id" not in (rd.fieldnames or []):
            if "processed" in path.parts:
                errors.append(f"{path}: no source_id column")
            return errors
        for n, row in enumerate(rd, start=2):
            val = (row["source_id"] or "").strip()
            if not val:
                errors.append(f"{path}:{n}: empty source_id")
                continue
            for sid in val.split(";"):
                if sid.strip() not in known:
                    errors.append(f"{path}:{n}: unknown source_id {sid!r}")
    return errors


def check_reports(root, known):
    errors = []
    for md in sorted((root / "reports").glob("*.md")):
        for key in set(re.findall(r"\[(S\d+)\]", md.read_text(encoding="utf-8"))):
            if key not in known:
                errors.append(f"{md}: cites unknown source {key}")
    return errors


def main(root=ROOT):
    root = Path(root)
    known, errors = load_sources(root / "sources.csv")
    for path in sorted((root / "data").rglob("*.csv")):
        if "cache" in path.parts:
            continue
        errors += check_csv(path, known)
    errors += check_reports(root, known)
    for e in errors:
        print("ERROR", e)
    if errors:
        print(f"FAILED: {len(errors)} problem(s)")
        return 1
    print(f"OK: all data files use known source_ids ({len(known)} sources)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ROOT))
