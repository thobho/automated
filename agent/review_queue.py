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

Merge safety (two builds run in parallel, so a PR can be green alone and still break `main`): an approved
PR is merged only when its head already contains the current `main`. Otherwise review-run.sh asks GitHub
to merge `main` into the branch ("update branch") and leaves `<!-- automated:approved:<sha> -->`. The new
head is then not reviewed again by a model: when its only new commit is that update (its first parent is
the approved sha) and CI on it is green, agent/pirx/merge-ready.sh merges it; red CI there means the PR
clashes with work merged meanwhile and it goes back to the builder. At most MAX_UPDATES updates, then it
merges as soon as CI is green. While a project's CI is red on `main`, its PRs are held (not merged) and the
healer opens one `priority:high` fix task.

Usage:
  agent/review_queue.py              list open agent PRs and their review state
  agent/review_queue.py --next-json [--no-opus]  the next PR to review as JSON; exit 1 if none. With --no-opus
                     (no Opus headroom) Opus-only PRs are skipped and listed in "waiting", others get the fallback
  agent/review_queue.py --next-conflict-json  the next conflicting PR to resolve as JSON; exit 1 if none
  agent/review_queue.py --merge-ready-json    approved PRs updated with main whose CI finished (JSON list)
  agent/review_queue.py --policy <files.json>   diff-policy flags for a PR's file list (one per line)
  agent/review_queue.py --enforce <verdict.json> <flags.txt>   rewrite the verdict file per enforce()
"""
import json
import os
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
APPROVED = re.compile(r"<!-- automated:approved:([0-9a-f]{7,40}) -->")
MAX_UPDATES = 3
UPDATED = "<!-- automated:updated -->"
MERGE_RED = "<!-- automated:merge-red:{sha} -->"
GITHUB_COMMITTER = "noreply@github.com"
# Approvals that merge-ready.sh acts on are local records written by review-run.sh (and merge-ready.sh
# for update commits), not PR comments: builders can post comments, but not write this directory.
APPROVALS_DIR = os.path.join(os.path.expanduser(os.environ.get("AUTOMATED_RUNTIME", "~/runtime/automated")),
                             "state", "approved")
RED_MAIN_LABEL = "red-main"
PROJECT_PATH = re.compile(r"^projects/([a-z0-9-]+)/")
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
  | agent/review-prompt\.md
  | agent/pirx/[^/]*\.sh
  | agent/pirx/[^/]*settings\.json | agent/pirx/opencode\.json | agent/pirx/root/.*
  | agent/pirx/systemd/.* | agent/pirx/owner/.*
  | scripts/(owner-apply|sudo-request|worker-lock)\.sh
)$""", re.VERBOSE)
# Why each group is guarded: the budget and merge code decide what is spent and merged; every
# agent/pirx/*.sh either picks the model and --settings of a Claude run (claude-run, conflict-run,
# planner-run, review-run), holds the slot lock and memory gate (common), or calls the root helper
# (heal); systemd units are copied live by the healer; review-prompt.md is the merge standard;
# owner/* runs in the owner's account; root/* is the agent's only root access.


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


# Diff policy: changes that can hide a failure instead of fixing it. They are not forbidden (a skip for a
# missing binary can be right), but the reviewer must judge each one explicitly; review-run.sh turns an
# approval that ignores a flag into "changes" (see enforce()).
TEST_PATH = re.compile(r"(^|/)(tests?/|test_[^/]*\.py$|[^/]*_test\.py$|[^/]*\.(spec|test)\.[jt]sx?$|conftest\.py$)")
SKIP_ADDED = re.compile(r"^\+(?!\+\+).*?(pytest\.mark\.(?:skipif|skip|xfail)|pytest\.(?:skip|xfail|importorskip)\("
                        r"|unittest\.skip\w*|@skip\w*|\b(?:it|test|describe)\.(?:skip|only)\(|\.only\(|--deselect"
                        r"|pragma: no cover|collect_ignore\w*|pytest_collection_modifyitems|pytest_ignore_collect)", re.M)
CI_CONFIG = re.compile(r"(^|/)(\.github/workflows/[^/]+|pytest\.ini|tox\.ini|\.coveragerc|setup\.cfg|ruff\.toml|\.ruff\.toml)$")
PYPROJECT_TEST_KEYS = re.compile(r"^[+-](?!\+\+|--).*\b(addopts|testpaths|omit|fail_under|--cov|deselect|filterwarnings"
                                 r"|extend-ignore|per-file-ignores|exclude)\b", re.M)


PACKAGE_TEST_SCRIPT = re.compile(r'^[+-](?!\+\+|--)\s*"test[\w:-]*"\s*:', re.M)


def diff_policy(files):
    """Flags for the reviewer. `files`: entries of GET /repos/{repo}/pulls/{n}/files (filename, status, patch)."""
    flags = []
    for f in files:
        path, status, patch = f.get("filename", ""), f.get("status", ""), f.get("patch") or ""
        is_test = bool(TEST_PATH.search(path))
        watched = is_test or CI_CONFIG.search(path) or path.endswith(("pyproject.toml", "package.json"))
        if watched and status not in ("removed", "added") and "patch" not in f:
            flags.append(f"patch not available, check manually: {path}")  # GitHub omits very large diffs
        if path.endswith("package.json") and PACKAGE_TEST_SCRIPT.search(patch):
            flags.append(f"test script changed: {path}")
        if is_test and status == "removed":
            flags.append(f"test file deleted: {path}")
        elif is_test and f.get("deletions", 0) >= 20 and f.get("deletions", 0) > 2 * f.get("additions", 0):
            flags.append(f"tests shrunk: {path} (-{f.get('deletions')} +{f.get('additions')})")
        markers = sorted({m.group(1) for m in SKIP_ADDED.finditer(patch)})
        if markers:
            flags.append(f"{path}: adds {', '.join('`' + m + '`' for m in markers)}")
        if CI_CONFIG.search(path) and status != "added":
            flags.append(f"CI or test config changed: {path}")
        if path.endswith("pyproject.toml") and PYPROJECT_TEST_KEYS.search(patch):
            flags.append(f"test/lint/coverage settings changed: {path}")
    return flags


def criteria_count(issue_body):
    """How many acceptance criteria an issue lists: bullets under its "Acceptance criteria" heading."""
    m = re.search(r"acceptance criteria\**:?\s*\n(.*?)(?:\n\s*\n\*\*|\n#|\Z)", issue_body or "", re.I | re.S)
    return sum(1 for l in (m.group(1) if m else "").splitlines() if re.match(r"\s*[-*]\s+\S", l))


def enforce(verdict, flags, min_criteria=0):
    """An approval must show evidence for every acceptance criterion (at least as many as the issue lists) and
    judge every diff-policy flag; otherwise it becomes "changes" with the missing items as points. Entries of the
    wrong type count as missing. Returns the (possibly) new verdict."""
    if not isinstance(verdict, dict) or verdict.get("verdict") not in ("approve", "changes", "blocked"):
        return {"verdict": "changes", "summary": "The review verdict could not be processed.",
                "points": [{"file": "", "issue": "malformed review verdict", "fix": "review again"}]}
    if verdict.get("verdict") != "approve":
        return verdict
    missing = []
    criteria = verdict.get("criteria") if isinstance(verdict.get("criteria"), list) else []
    if not criteria:
        missing.append(("", "no acceptance criteria listed with evidence", "list every criterion of the issue under `criteria`"))
    elif len(criteria) < min_criteria:
        missing.append(("", f"{len(criteria)} criteria listed, the issue has {min_criteria}", "list and check every criterion"))
    for c in criteria:
        if not isinstance(c, dict) or c.get("met") is not True or not str(c.get("evidence", "")).strip():
            name = c.get("criterion", "?") if isinstance(c, dict) else str(c)[:80]
            missing.append(("", f"criterion not shown as met: {name}",
                            "meet it, or show the test, command output or file:line that proves it"))
    policy = verdict.get("policy") if isinstance(verdict.get("policy"), list) else []
    judged = {str(p.get("flag", "")).strip(): p for p in policy if isinstance(p, dict)}
    for flag in flags:
        p = judged.get(flag)
        if p is None:
            missing.append(("", f"diff-policy flag not judged: {flag}", "justify it or remove it"))
        elif p.get("ok") is not True or not str(p.get("why", "")).strip():
            missing.append(("", f"diff-policy flag not acceptable: {flag}", p.get("why") or "remove it or justify it"))
    if not missing:
        return verdict
    out = dict(verdict)
    out["verdict"] = "changes"
    out["points"] = list(verdict.get("points") or []) + [{"file": f, "issue": i, "fix": x} for f, i, x in missing]
    out["summary"] = (verdict.get("summary", "") + " (Approval turned into changes by the runner: "
                      f"{len(missing)} acceptance or diff-policy item(s) without evidence.)").strip()
    return out


def project_of(paths):
    """The single project a PR changes (projects/<name>/...), or None."""
    names = {m.group(1) for p in paths if (m := PROJECT_PATH.match(p))}
    return names.pop() if len(names) == 1 else None


def review_model(issue_labels, paths=()):
    """(preferred, fallback) reviewer models for a PR whose linked issue has these labels."""
    if "area:security" in issue_labels or automation(paths):
        return "opus", None
    if "model:opus" in issue_labels:
        return "sonnet", None
    return "opus", "sonnet"


def next_review(todo, opus_ok=True):
    """The PR to review now, or None, plus the Opus-only PRs passed over. Without Opus headroom an Opus-only
    review (security, automation, Sonnet-built) waits, but it no longer blocks the PRs behind it."""
    if opus_ok:
        return (todo[0] if todo else None), []
    waiting = [t["pr"] for t in todo if t["model"] == "opus" and not t["fallback"]]
    for t in todo:
        if t["model"] != "opus":
            return t, waiting
        if t["fallback"]:
            return dict(t, model=t["fallback"]), waiting
    return None, waiting


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
    # Approved commits: the local records when given (production), else the comment markers (tests, listing).
    approved = list(pr["approvedShas"]) if "approvedShas" in pr else [m.group(1) for b in bodies for m in APPROVED.finditer(b)]
    head = pr.get("headCommit") or {}
    parents = head.get("parents") or []
    # The head is GitHub's own merge of main into an approved commit ("update branch": committed and signed by
    # GitHub): no new code to review, only CI to wait for. A merge made by anyone else (a builder, the conflict
    # resolver) may carry hand edits, so it is reviewed again.
    update_of_approved = (len(parents) == 2 and any(parents[0].startswith(a) for a in approved)
                          and head.get("committer") == GITHUB_COMMITTER and head.get("verified") is True)
    head_approved = any(sha.startswith(a) for a in approved)
    prot = protected(paths)
    # CI must have really run on the head: right after an update GitHub can show no checks yet ("none").
    ci_ready = ci == "green" or (ci == "none" and not pr.get("projectHasCI", True))
    red_handled = MERGE_RED.format(sha=sha) in " ".join(bodies)
    return {
        "pr": pr["number"],
        "title": pr["title"],
        "branch": pr["headRefName"],
        "sha": sha,
        "issue": int(m.group(1)) if m else None,
        "ci": ci,
        "reviewed": reviewed,
        "rounds": sum(CHANGES_MARK in b for b in bodies),
        "protected": prot,
        "automation": automation(paths),
        "money": [p for p in paths if MONEY.match(p)],
        "model": preferred,
        "fallback": fallback,
        "conflicting": conflicting,
        "project": project_of(paths),
        "updates": sum(UPDATED in b for b in bodies),
        "max_updates": MAX_UPDATES,
        "red_main_fix": RED_MAIN_LABEL in issue_labels,
        "update_of_approved": update_of_approved,
        "needs_merge": (head_approved or update_of_approved) and not prot and not conflicting and not pr.get("isDraft")
                       and not with_builder and (ci_ready or (ci == "red" and not red_handled)),
        "conflict_attempts": attempts,
        "conflict_model": "sonnet" if attempts == 0 else "opus",
        "needs_resolve": conflicting and not pr.get("isDraft") and not with_builder
                         and attempts < MAX_CONFLICT_ATTEMPTS,
        "needs_review": not reviewed and not conflicting and ci != "running" and not pr.get("isDraft")
                        and not with_builder and not update_of_approved,
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
    if "--policy" in sys.argv:
        for flag in diff_policy(json.load(open(sys.argv[sys.argv.index("--policy") + 1]))):
            print(flag)
        return
    if "--enforce" in sys.argv:  # never crashes: anything unreadable becomes "changes"
        i = sys.argv.index("--enforce")
        path, flags_path = sys.argv[i + 1], sys.argv[i + 2]
        min_criteria = int(sys.argv[i + 3]) if len(sys.argv) > i + 3 and sys.argv[i + 3].isdigit() else 0
        try:
            flags = [l.rstrip("\n") for l in open(flags_path) if l.strip()]
            v = enforce(json.load(open(path)), flags, min_criteria)
        except Exception as e:
            v = {"verdict": "changes", "summary": f"The review verdict could not be processed ({type(e).__name__}).",
                 "points": [{"file": "", "issue": "malformed review verdict", "fix": "review again"}]}
        json.dump(v, open(path, "w"))
        print(v["verdict"])
        return
    if "--criteria-count" in sys.argv:
        print(criteria_count(sys.stdin.read()))
        return
    prs = gh_json("pr", "list", "--state", "open", "--limit", "50", "--json",
                  "number,title,body,headRefName,headRefOid,isDraft,mergeable,statusCheckRollup,comments,files")
    cache = {}
    records = os.listdir(APPROVALS_DIR) if os.path.isdir(APPROVALS_DIR) else []
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for pr in prs:
        pr["approvedShas"] = [r.split("-", 1)[1] for r in records if r.startswith(f"{pr['number']}-")]
        proj = project_of([f["path"] for f in pr.get("files") or []])
        pr["projectHasCI"] = bool(proj) and os.path.exists(os.path.join(root, ".github", "workflows", f"{proj}-ci.yml"))
        if pr["approvedShas"] and not any(pr["headRefOid"].startswith(s) for s in pr["approvedShas"]):
            try:  # who made the head commit: only GitHub's own update-branch merge skips the review
                pr["headCommit"] = gh_json("api", f"repos/{{owner}}/{{repo}}/commits/{pr['headRefOid']}", "--jq",
                                           "{parents: [.parents[].sha], committer: .commit.committer.email,"
                                           " verified: .commit.verification.verified}")
            except subprocess.CalledProcessError:
                pr["headCommit"] = {}

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
    if "--merge-ready-json" in sys.argv:  # every approved-and-updated PR whose CI has finished
        print(json.dumps([t for t in q if t["needs_merge"]]))
        return
    if "--next-json" in sys.argv:
        t, waiting = next_review([t for t in q if t["needs_review"]], "--no-opus" not in sys.argv)
        print(json.dumps(dict(t or {"pr": None}, waiting=" ".join(map(str, waiting)))))
        sys.exit(0 if t else 1)
    for t in q:
        state = ("conflict" if t["conflicting"] else "needs review" if t["needs_review"]
                 else "reviewed" if t["reviewed"] else f"CI {t['ci']}")
        prot = " [owner merges]" if t["protected"] else ""
        print(f"PR #{t['pr']:<4} {state:<13} CI {t['ci']:<7} {t['model']}/{t['fallback'] or '-'} {t['title']}{prot}")


if __name__ == "__main__":
    main()
