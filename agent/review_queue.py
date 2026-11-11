#!/usr/bin/env python3
"""Which agent PR the AI reviewer should look at next, with which model, and whether it may be merged.

A PR needs a review when:
  - its branch is `agent/...` (task PRs) or `agent-setup/...` (automation PRs),
  - its CI has finished (green or red; a PR without checks counts as finished),
  - there is no review comment yet for its current head commit
    (`<!-- automated:review:<sha> -->`, written by agent/pirx/review-run.sh).

Model: security work (`area:security` on the linked issue) is always reviewed by Opus, never a fallback.
Other PRs prefer Opus and fall back to Sonnet when the plan budget has no Opus headroom; a PR built
by Opus is reviewed by Sonnet. The reviewer is always a separate run from the builder.

Protected PRs (they change the automation itself: `agent/`, `scripts/`, `.github/` except a project's
`<project>-ci.yml` workflow, or files in the repo root) are reviewed but never merged automatically:
the owner merges them with one tap after an approving review.

Usage:
  agent/review_queue.py              list open agent PRs and their review state
  agent/review_queue.py --next-json  the next PR to review as JSON; exit 1 if none
"""
import json
import re
import subprocess
import sys

AGENT_BRANCH = re.compile(r"^agent(-setup)?/")
CLOSES = re.compile(r"\b(?:closes|fixes|resolves)\s+#(\d+)", re.IGNORECASE)
PROJECT_CI = re.compile(r"^\.github/workflows/[a-z0-9-]+-ci\.ya?ml$")
REVIEW_MARK = "<!-- automated:review:{sha} -->"
CHANGES_MARK = "<!-- automated:review-changes -->"


def gh_json(*args):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out) if out.strip() else []


def ci_state(pr):
    checks = pr.get("statusCheckRollup") or []
    if not checks:
        return "none"
    states = {(c.get("conclusion") or c.get("state") or c.get("status") or "").upper() for c in checks}
    if states & {"PENDING", "IN_PROGRESS", "QUEUED", "EXPECTED", "WAITING", ""}:
        return "running"
    if states & {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}:
        return "red"
    return "green"


def protected(paths):
    """Paths that change the automation itself (or the repo root) need the owner's merge."""
    hits = []
    for p in paths:
        if "/" not in p or p.startswith(("agent/", "scripts/")):
            hits.append(p)
        elif p.startswith(".github/") and not PROJECT_CI.match(p):
            hits.append(p)
    return hits


def review_model(issue_labels):
    """(preferred, fallback) reviewer models for a PR whose linked issue has these labels."""
    if "area:security" in issue_labels:
        return "opus", None
    if "model:opus" in issue_labels:
        return "sonnet", None
    return "opus", "sonnet"


def assess(pr, issue_labels):
    sha = pr["headRefOid"]
    bodies = [c.get("body") or "" for c in pr.get("comments") or []]
    reviewed = any(REVIEW_MARK.format(sha=sha) in b for b in bodies)
    ci = ci_state(pr)
    m = CLOSES.search(pr.get("body") or "")
    preferred, fallback = review_model(issue_labels)
    paths = [f["path"] for f in pr.get("files") or []]
    return {
        "pr": pr["number"],
        "title": pr["title"],
        "branch": pr["headRefName"],
        "sha": sha,
        "issue": int(m.group(1)) if m else None,
        "ci": ci,
        "reviewed": reviewed,
        "rounds": sum(CHANGES_MARK in b for b in bodies),
        "protected": protected(paths),
        "model": preferred,
        "fallback": fallback,
        "needs_review": not reviewed and ci != "running" and not pr.get("isDraft"),
    }


def queue(prs, labels_of):
    out = []
    for pr in sorted(prs, key=lambda p: p["number"]):
        if not AGENT_BRANCH.match(pr["headRefName"]):
            continue
        a = assess(pr, labels_of(pr))
        out.append(a)
    return out


def main():
    prs = gh_json("pr", "list", "--state", "open", "--limit", "50", "--json",
                  "number,title,body,headRefName,headRefOid,isDraft,statusCheckRollup,comments,files")
    cache = {}

    def labels_of(pr):
        m = CLOSES.search(pr.get("body") or "")
        if not m:
            return set()
        n = int(m.group(1))
        if n not in cache:
            try:
                cache[n] = {l["name"] for l in gh_json("issue", "view", str(n), "--json", "labels")["labels"]}
            except subprocess.CalledProcessError:
                cache[n] = set()
        return cache[n]

    q = queue(prs, labels_of)
    if "--next-json" in sys.argv:
        todo = [t for t in q if t["needs_review"]]
        if not todo:
            sys.exit(1)
        print(json.dumps(todo[0]))
        return
    for t in q:
        state = "needs review" if t["needs_review"] else ("reviewed" if t["reviewed"] else f"CI {t['ci']}")
        prot = " [owner merges]" if t["protected"] else ""
        print(f"PR #{t['pr']:<4} {state:<13} CI {t['ci']:<7} {t['model']}/{t['fallback'] or '-'} {t['title']}{prot}")


if __name__ == "__main__":
    main()
