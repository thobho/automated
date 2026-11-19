#!/usr/bin/env python3
"""Weekly retro digest: what the AI reviewer and the runners sent back to builders in the last N days.

The digest feeds agent/pirx/retro-run.sh, where a model turns findings that repeat into rules in the
project's CLAUDE.md (and, rarely, agent/worker-prompt.md), so builders stop making the same mistake.
No model here: it only reads GitHub.

Sources, per project (from the PR's files or the issue's project label):
  - "Must change" points of AI reviews that requested changes,
  - "Back to the builder" reasons (red CI, clash with main),
  - builder failure notes (comments starting with ❌).

Usage:
  agent/retro.py [--days 7]          the digest as Markdown on stdout; exit 1 when fewer than 2 findings
  agent/retro.py --json [--days 7]
"""
import datetime as dt
import json
import re
import subprocess
import sys

PROJECT_PATH = re.compile(r"^projects/([a-z0-9-]+)/")
POINT = re.compile(r"^\s*\d+\.\s+(.*)$")


def gh_json(*args):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out) if out.strip() else []


def review_points(body):
    """The numbered points under "Must change:" of one AI review comment that requested changes."""
    if "changes requested" not in body or "**Must change:**" not in body:
        return []
    section = body.split("**Must change:**", 1)[1]
    section = re.split(r"\n\*\*[A-Z][^*]*:\*\*", section, maxsplit=1)[0]
    return [re.sub(r"\s+", " ", m.group(1)).strip()[:400] for line in section.splitlines() if (m := POINT.match(line))]


def other_findings(body):
    """Back-to-builder reasons and failure notes in one comment."""
    out = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("❌") or s.startswith("↩️ Back to the builder") or s.startswith("🔁 CI is red"):
            out.append(re.sub(r"<!--.*?-->", "", s).strip()[:300])
    return out


def project_of(paths, labels=()):
    names = {m.group(1) for p in paths if (m := PROJECT_PATH.match(p))}
    names |= {l.split(":", 1)[1] for l in labels if l.startswith("project:")}
    return names.pop() if len(names) == 1 else "automation"


def collect(days):
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%d")
    found = {}
    prs = gh_json("pr", "list", "--state", "all", "--limit", "100", "--search", f"updated:>={since}",
                  "--json", "number,title,headRefName,files,comments")
    for pr in prs:
        if not re.match(r"^agent(-setup)?/", pr["headRefName"]):
            continue
        proj = project_of([f["path"] for f in pr.get("files") or []])
        for c in pr.get("comments") or []:
            if (c.get("createdAt") or "")[:10] < since:
                continue
            for p in review_points(c.get("body") or ""):
                found.setdefault(proj, []).append(f"PR #{pr['number']} ({pr['title'][:60]}): {p}")
    issues = gh_json("issue", "list", "--state", "all", "--limit", "100", "--search", f"updated:>={since}",
                     "--json", "number,title,labels,comments")
    for i in issues:
        proj = project_of([], [l["name"] for l in i.get("labels") or []])
        for c in i.get("comments") or []:
            if (c.get("createdAt") or "")[:10] < since:
                continue
            for f in other_findings(c.get("body") or ""):
                found.setdefault(proj, []).append(f"#{i['number']} ({i['title'][:60]}): {f}")
    return found


def render(found, days):
    out = [f"# Retro digest: findings of the last {days} days", ""]
    for proj in sorted(found):
        out += [f"## {proj} ({len(found[proj])})", ""] + [f"- {f}" for f in found[proj]] + [""]
    return "\n".join(out)


def main():
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
    found = collect(days)
    total = sum(len(v) for v in found.values())
    if "--json" in sys.argv:
        print(json.dumps(found, ensure_ascii=False, indent=2))
    else:
        print(render(found, days))
    sys.exit(0 if total >= 2 else 1)


if __name__ == "__main__":
    main()
