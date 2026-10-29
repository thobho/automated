#!/usr/bin/env python3
"""Fail (exit 1) if any data file has an empty or unknown source_id.

Checks every CSV under data/ (except data/raw/cache) that has a `source_id`
column: each non-empty cell, split on ';', must be an id in sources.csv.
Also fails if a CSV under data/processed has no `source_id` column, if
sources.csv has duplicate ids, or if a report cites an unknown [S..] key.

Final-report rules (reports/final-report.md, checked when the file exists):
every line that contains a number carries an [S..] key, every "derived"
line carries a [D..] key that is defined in a table row `| D.. |`.

Unused sources: a source is "used" if it is cited as [S..] in any report
under reports/ (bibliography.md and citation-sheet.md are generated from
sources.csv and do not count) or appears in a source_id column of a data
file. A source that is used nowhere fails the check: cite it or remove it.
Standard library only.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATED_REPORTS = {"bibliography.md", "citation-sheet.md"}
FINAL_REPORT = "final-report.md"
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


def read_sources(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def source_ids_in_csv(path):
    """Set of ids in the source_id column of a CSV (empty if no such column)."""
    out = set()
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if "source_id" not in (rd.fieldnames or []):
            return out
        for row in rd:
            out |= {x.strip() for x in (row["source_id"] or "").split(";") if x.strip()}
    return out


def data_files(root):
    return [p for p in sorted((Path(root) / "data").rglob("*.csv")) if "cache" not in p.parts]


def source_usage(root):
    """{source id: {'reports': set of report names, 'data': set of data file names}}."""
    root = Path(root)
    usage = {}
    for md in sorted((root / "reports").glob("*.md")):
        if md.name in GENERATED_REPORTS:
            continue
        for key in set(re.findall(r"\[(S\d+)\]", md.read_text(encoding="utf-8"))):
            usage.setdefault(key, {"reports": set(), "data": set()})["reports"].add(md.name)
    for path in data_files(root):
        for sid in source_ids_in_csv(path):
            usage.setdefault(sid, {"reports": set(), "data": set()})["data"].add(path.name)
    return usage


def check_unused(root, known):
    usage = source_usage(root)
    return [f"{sid}: unused (not cited in any report, not in any data file source_id); "
            f"cite it where relevant or remove it from sources.csv"
            for sid in sorted(known, key=lambda s: int(s[1:]))
            if sid not in usage]


_KEY = re.compile(r"\[S\d+\]")
_DKEY = re.compile(r"\bD\d+\b")


def line_needs_key(line):
    """True if the line (outside headings/fences) contains a number once years,
    ids, codes (letters mixed with digits), code spans and section references
    are removed."""
    t = re.sub(r"`[^`]*`", " ", line)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"\[[SD]\d+\]", " ", t)
    t = t.replace("EU-27", " ")
    t = re.sub(r"\b(?:19|20)\d\d\b", " ", t)
    t = re.sub(r"\b(?:[Ss]ection|[Tt]ask|[Rr]eport|[Ii]ssue|#)\s*\d+(?:\.\d+)?\b", " ", t)
    t = re.sub(r"\bper 1000\b|\bx 100\b|\bx 1000\b", " ", t)  # unit wording, not data
    t = re.sub(r"\b\w*[A-Za-z_]\w*\d\w*\b", " ", t)  # S19, P3824, km2, ilc_lvho01
    return bool(re.search(r"\d", t))


def check_final_report(path, known):
    errors = []
    text = Path(path).read_text(encoding="utf-8")
    defined = set(re.findall(r"^\|\s*(D\d+)\s*\|", text, flags=re.M))
    fence = False
    lines = text.splitlines()
    for n, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            fence = not fence
            continue
        s = line.strip()
        if fence or not s or s.startswith("#") or s.startswith("<!--") or re.fullmatch(r"[|:\- ]+", s):
            continue
        keys = _KEY.findall(line)
        for k in keys:
            if k[1:-1] not in known:
                errors.append(f"{path}:{n}: unknown source key {k}")
        is_def = bool(re.match(r"\|\s*D\d+\s*\|", s))
        nxt = lines[n].strip() if n < len(lines) else ""
        if is_def or (s.startswith("|") and re.fullmatch(r"[|:\- ]+", nxt)):
            continue  # formula rows and table header rows hold wording, not data
        for d in _DKEY.findall(line):
            if d not in defined:
                errors.append(f"{path}:{n}: derived key {d} is not defined in the D table")
        if keys and re.search(r"\bderived\b", line, flags=re.I) and not _DKEY.search(line):
            errors.append(f"{path}:{n}: 'derived' without a D key (formula and inputs)")
        if not keys and line_needs_key(line):
            errors.append(f"{path}:{n}: number without an [S..] key: {s[:80]}")
    return errors


def main(root=ROOT):
    root = Path(root)
    known, errors = load_sources(root / "sources.csv")
    for path in sorted((root / "data").rglob("*.csv")):
        if "cache" in path.parts:
            continue
        errors += check_csv(path, known)
    errors += check_reports(root, known)
    errors += check_unused(root, known)
    final = root / "reports" / FINAL_REPORT
    if final.exists():
        errors += check_final_report(final, known)
    for e in errors:
        print("ERROR", e)
    if errors:
        print(f"FAILED: {len(errors)} problem(s)")
        return 1
    print(f"OK: all data files use known source_ids ({len(known)} sources)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ROOT))
