#!/usr/bin/env python3
"""Which agent PR the AI reviewer should look at next, with which model, and whether it may be merged.

A PR needs a review when:
  - its branch is `agent/...` (task PRs) or `agent-setup/...` (automation PRs),
  - its CI has finished (green or red; a PR without checks counts as finished),
  - there is no review comment yet for its current head commit, and
  - its linked issue is not back with the builder (`agent:todo`, `agent:doing` or `agent:blocked`),
    (`<!-- automated:review:<sha> -->`, written by agent/pirx/review-run.sh).

Model: security work (`area:security` on the linked issue) is always reviewed by Opus, never a fallback.
Other PRs prefer Opus and fall back to Sonnet when the plan budget has no Opus headroom; a PR built
by Opus is reviewed by Sonnet. The reviewer is always a separate run from the builder.

A PR that conflicts with main is not reviewed: it goes to the conflict resolver first
(agent/pirx/conflict-run.sh), which merges main into the branch and pushes; the new head commit is
then reviewed as usual. A failed attempt leaves `<!-- automated:conflict-failed -->`, a success
`<!-- automated:conflict-resolved -->`; only failures since the last success count. After
MAX_CONFLICT_ATTEMPTS failures in a row the task is blocked. Attempt 1 runs on Sonnet, the next on Opus.

Automation PRs (they change `agent/`, `scripts/`, `.github/` except a project's `<project>-ci.yml`,
or files in the repo root) are reviewed by Opus only, never a fallback, and merged on approval like
any other PR. Guarded PRs, the subset that touches money or permissions (budget gates, settings and
allowlists, the root helper, the merge rules, the dispatcher, setup scripts, workflows, root files),
are reviewed but never merged automatically: the owner merges them with one tap.

Usage:
  agent/review_queue.py              list open agent PRs and their review state
  agent/review_queue.py --next-json  the next PR to review as JSON; exit 1 if none
  agent/review_queue.py --next-conflict-json  the next conflicting PR to resolve as JSON; exit 1 if none
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
CONFLICT_FAILED = "<!-- automated:conflict-failed -->"
CONFLICT_RESOLVED = "<!-- automated:conflict-resolved -->"
MAX_CONFLICT_ATTEMPTS = 2
WITH_BUILDER = {"agent:todo", "agent:doing", "agent:blocked"}


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


GUARDED = re.compile(r"""^(
    agent/(budget|openrouter_budget|review_queue|usage_probe)\.py
  | agent/pirx/(review-run|start-claude-run|dispatch|opencode-worker|heal-diagnose|setup|setup-agent-user)\.sh
  | agent/pirx/[^/]*settings\.json | agent/pirx/opencode\.json | agent/pirx/root/.*
  | scripts/(owner-apply|sudo-request|worker-lock)\.sh
)$""", re.VERBOSE)


MONEY = re.compile(r"^agent/(budget|openrouter_budget)\.py$")


def automation(paths):
    """Paths that change the automation itself (or the repo root)."""
    hits = []
    for p in paths:
        if "/" not in p or p.startswith(("agent/", "scripts/")):
            hits.append(p)
        elif p.startswith(".github/") and not PROJECT_CI.match(p):
            hits.append(p)
    return hits


def protected(paths):
    """Automation paths that touch money or permissions: these PRs need the owner's merge."""
    return [p for p in automation(paths) if "/" not in p or p.startswith(".github/") or GUARDED.match(p)]


def review_model(issue_labels, paths=()):
    """(preferred, fallback) reviewer models for a PR whose linked issue has these labels."""
    if "area:security" in issue_labels or automation(paths):
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
    paths = [f["path"] for f in pr.get("files") or []]
    preferred, fallback = review_model(issue_labels, paths)
    conflicting = pr.get("mergeable") == "CONFLICTING"
    since = max((i for i, b in enumerate(bodies) if CONFLICT_RESOLVED in b), default=-1)
    attempts = sum(CONFLICT_FAILED in b for b in bodies[since + 1:])
    with_builder = bool(issue_labels & WITH_BUILDER)
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
        "automation": automation(paths),
        "money": [p for p in paths if MONEY.match(p)],
        "model": preferred,
        "fallback": fallback,
        "conflicting": conflicting,
        "conflict_attempts": attempts,
        "conflict_model": "sonnet" if attempts == 0 else "opus",
        "needs_resolve": conflicting and not pr.get("isDraft") and not with_builder
                         and attempts < MAX_CONFLICT_ATTEMPTS,
        "needs_review": not reviewed and not conflicting and ci != "running" and not pr.get("isDraft")
                        and not with_builder,
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
                  "number,title,body,headRefName,headRefOid,isDraft,mergeable,statusCheckRollup,comments,files")
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
    if "--next-conflict-json" in sys.argv:
        todo = [t for t in q if t["needs_resolve"]]
        if not todo:
            sys.exit(1)
        print(json.dumps(todo[0]))
        return
    if "--next-json" in sys.argv:
        todo = [t for t in q if t["needs_review"]]
        if not todo:
            sys.exit(1)
        print(json.dumps(todo[0]))
        return
    for t in q:
        state = ("conflict" if t["conflicting"] else "needs review" if t["needs_review"]
                 else "reviewed" if t["reviewed"] else f"CI {t['ci']}")
        prot = " [owner merges]" if t["protected"] else ""
        print(f"PR #{t['pr']:<4} {state:<13} CI {t['ci']:<7} {t['model']}/{t['fallback'] or '-'} {t['title']}{prot}")


if __name__ == "__main__":
    main()
