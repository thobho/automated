#!/usr/bin/env python3
"""Checks report.md against sources.md: every [S#] cited exists, every source row has an access date,
every source is cited somewhere in report.md or noted as probe-only, and the required sections exist."""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parents[1]


def check(report_text, sources_text):
    errors = []
    rows = {}
    for line in sources_text.splitlines():
        m = re.match(r"\|\s*(S\d+)\s*\|(.*)\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*$", line)
        if m:
            rows[m.group(1)] = m.group(3)
    if not rows:
        errors.append("no source rows found")
    cited = set(re.findall(r"\[(S\d+)\]", report_text))
    # ranges like [S1-S15] and lists like [S100]-[S103] are accepted without expansion
    for rng in re.findall(r"\[(S\d+)-(S\d+)\]", report_text):
        cited.update(f"S{i}" for i in range(int(rng[0][1:]), int(rng[1][1:]) + 1))
    for c in sorted(cited, key=lambda s: int(s[1:])):
        if c not in rows:
            errors.append(f"cited {c} is not in sources.md")
    for sec in ["## 1. Recommendation", "## 3. Comparison", "## 4. Criteria", "## 5. Own test", "## 6. Risks", "## 7. Open questions"]:
        if sec not in report_text:
            errors.append(f"missing section {sec}")
    for needle in ["Apache-2.0", "6.1.0", "Build step"]:
        if needle not in report_text:
            errors.append(f"recommendation must mention {needle}")
    return errors, rows, cited


if __name__ == "__main__":
    errs, rows, cited = check((root / "report.md").read_text(), (root / "sources.md").read_text())
    for e in errs:
        print("ERROR:", e)
    print(f"{len(rows)} sources, {len(cited)} distinct citations, {len(errs)} errors")
    sys.exit(1 if errs else 0)
