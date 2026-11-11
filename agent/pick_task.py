#!/usr/bin/env python3
"""Order the agent queue and say which task is ready to work on, and for whom.

Ordering rules:
  1. `agent:doing` issues come first: an earlier run was interrupted.
  2. `agent:todo` issues are ready only when every issue they depend on is
     closed (its PR was merged). Dependencies are lines in the issue body like
     "Depends on #12" or "Depends on: #12, #14".
  3. Ready todos: `priority:high` first, `priority:low` last; then the earliest
     GitHub milestone (M1 before M2, no milestone last); then the task that
     unblocks the most other open issues; then the oldest issue number.

Executors (who builds a task):
  - `model:pirx` -> OpenCode on pirx (OpenRouter budget).
  - `model:haiku|sonnet|opus` (default sonnet) -> a Claude run (plan budget).
  - Security tasks (`area:security`) never go to OpenCode: a `model:pirx` there
    is treated as `sonnet`.
  - Spillover: with `--spillover`, a Claude run may take OpenCode tasks when no
    Claude task is ready; it builds them with sonnet.

Review limit: while a project has MAX_OPEN_REVIEWS (default 5,
AGENT_MAX_OPEN_REVIEWS) issues in `agent:review`, its todo issues wait, so work
does not pile up ahead of the owner's reviews. Interrupted `doing` issues still run.

Parallel runs:
  - An issue claimed by a live worker run (`worker-lock.sh claimed`) is
    running and never picked again.
  - A `Uses: gus-bdl, playwright` line names shared resources. An issue is not
    ready while a running issue uses one of the same resources.

Usage:
  agent/pick_task.py                          the queue in order, with what each one waits on
  agent/pick_task.py --next [--executor E] [--spillover]
                                              the number of the next issue to work on; exit 1 if none
  agent/pick_task.py --next-json [...]        the same as JSON: {"number", "executor", "model", "title", "project"}
  agent/pick_task.py --json                   the ordered queue as JSON
E is `claude` or `opencode`; without --executor any executor matches.

The lock script is $AUTOMATED_LOCK_SCRIPT, default ~/.config/automated/worker-lock.sh;
when it is missing or fails, nothing counts as claimed.
"""
import json
import os
import re
import subprocess
import sys

DEPENDS = re.compile(r"depends\s+on", re.IGNORECASE)
ISSUE_REF = re.compile(r"#(\d+)")
USES = re.compile(r"^\s*uses\s*:(.*)$", re.IGNORECASE | re.MULTILINE)
MODEL_LINE = re.compile(r"^\s*\**model\s*:\s*\**\s*`?(\w+)`?", re.IGNORECASE | re.MULTILINE)
LOCK_SCRIPT = os.environ.get("AUTOMATED_LOCK_SCRIPT",
                             os.path.expanduser("~/.config/automated/worker-lock.sh"))
MAX_OPEN_REVIEWS = int(os.environ.get("AGENT_MAX_OPEN_REVIEWS", 5))
MODELS = ("pirx", "haiku", "sonnet", "opus")


def gh_api(path):
    out = subprocess.run(["gh", "api", path], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def dependencies(body):
    deps = []
    for line in (body or "").splitlines():
        if DEPENDS.search(line):
            deps += [int(n) for n in ISSUE_REF.findall(line)]
    return deps


def resources(body):
    """Shared resources from `Uses:` lines, lowercased: "Uses: GUS-BDL, playwright" -> {"gus-bdl", "playwright"}."""
    found = set()
    for line in USES.findall(body or ""):
        line = re.sub(r"<!--.*?-->", "", line)
        found |= {r.strip("`").lower() for r in re.split(r"[,\s]+", line) if r.strip("`")}
    return found


def model_of(labels, body):
    """The model label, else a `Model:` line in the body, else sonnet; security work never goes to pirx."""
    model = next((l.split(":", 1)[1] for l in labels if l.startswith("model:")), None)
    if model not in MODELS:
        line = MODEL_LINE.search(body or "")
        model = line.group(1).lower() if line and line.group(1).lower() in MODELS else "sonnet"
    if model == "pirx" and "area:security" in labels:
        model = "sonnet"
    return model


def milestone_key(issue):
    """Sort key for the GitHub milestone: M1 < M2 < M10 < other titles < no milestone."""
    title = ((issue.get("milestone") or {}).get("title") or "").strip()
    if not title:
        return (2, 0, "")
    m = re.match(r"\D*(\d+)", title)
    return (0, int(m.group(1)), title) if m else (1, 0, title.lower())


def claimed_issues():
    try:
        out = subprocess.run(["bash", LOCK_SCRIPT, "claimed"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return set()
    if out.returncode != 0:
        return set()
    return {int(n) for n in out.stdout.split() if n.isdigit()}


def build_queue(issues, is_closed, claimed):
    """issues: open GitHub issues (dicts with number, title, body, labels, optional milestone). Returns them ordered."""
    busy = {r for i in issues if i["number"] in claimed for r in resources(i["body"])}
    open_numbers = {i["number"] for i in issues}
    unblocks = {}
    for i in issues:
        for d in set(dependencies(i["body"])):
            if d != i["number"] and d in open_numbers:
                unblocks[d] = unblocks.get(d, 0) + 1
    reviews = {}
    for i in issues:
        labels = {l["name"] for l in i["labels"]}
        if "agent:review" in labels:
            project = next((l.split(":", 1)[1] for l in labels if l.startswith("project:")), None)
            reviews[project] = reviews.get(project, 0) + 1

    queue = []
    for issue in issues:
        labels = {l["name"] for l in issue["labels"]}
        state = next((l.split(":", 1)[1] for l in labels
                      if l in ("agent:doing", "agent:todo", "agent:blocked", "agent:review")), None)
        if not state:
            continue
        project = next((l.split(":", 1)[1] for l in labels if l.startswith("project:")), None)
        running = issue["number"] in claimed
        deps = dependencies(issue["body"])
        waiting_on = [n for n in deps if n != issue["number"] and not is_closed(n)]
        uses = sorted(resources(issue["body"]))
        resource_busy = [] if running else [r for r in uses if r in busy]
        review_limit = state == "todo" and reviews.get(project, 0) >= MAX_OPEN_REVIEWS
        priority = 0 if "priority:high" in labels else 2 if "priority:low" in labels else 1
        model = model_of(labels, issue["body"])
        queue.append({
            "number": issue["number"],
            "title": issue["title"],
            "state": state,
            "running": running,
            "ready": not running and not resource_busy and not review_limit
                     and (state == "doing" or (state == "todo" and not waiting_on)),
            "waiting_on": waiting_on,
            "uses": uses,
            "resource_busy": resource_busy,
            "review_limit": review_limit,
            "priority": ["high", "normal", "low"][priority],
            "model": model,
            "executor": "opencode" if model == "pirx" else "claude",
            "milestone": (issue.get("milestone") or {}).get("title"),
            "unblocks": unblocks.get(issue["number"], 0),
            "project": project,
            "_sort": (["doing", "todo", "blocked", "review"].index(state),
                      0 if state != "todo" or not waiting_on else 1, priority,
                      milestone_key(issue), -unblocks.get(issue["number"], 0), issue["number"]),
        })
    queue.sort(key=lambda t: t["_sort"])
    for t in queue:
        del t["_sort"]
    return queue


def next_task(queue, executor=None, spillover=False):
    """The first ready task for this executor, as {"number", "executor", "model", ...}; None if none.

    A Claude run with spillover takes an OpenCode task only when no Claude task is ready,
    and builds it with sonnet."""
    ready = [t for t in queue if t["ready"]]
    own = [t for t in ready if executor in (None, t["executor"])]
    if own:
        t = own[0]
        return {k: t[k] for k in ("number", "title", "project", "executor", "model")}
    if executor == "claude" and spillover:
        spilled = [t for t in ready if t["executor"] == "opencode"]
        if spilled:
            t = spilled[0]
            return {"number": t["number"], "title": t["title"], "project": t["project"],
                    "executor": "claude", "model": "sonnet", "spillover": True}
    return None


def status_text(t):
    if t["running"]:
        return "running"
    if t["state"] == "todo" and t["waiting_on"]:
        return f"waits on {', '.join('#%d' % n for n in t['waiting_on'])}"
    if t["resource_busy"] and t["state"] in ("todo", "doing"):
        return f"waits on {', '.join(t['resource_busy'])}"
    if t.get("review_limit"):
        return "waits on reviews"
    return "ready" if t["state"] == "todo" else t["state"]


def arg_value(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def main():
    issues = [i for i in gh_api("repos/{owner}/{repo}/issues?state=open&per_page=100")
              if "pull_request" not in i]
    open_numbers = {i["number"] for i in issues}
    state_cache = {}

    def is_closed(n):
        if n in open_numbers:
            return False
        if n not in state_cache:
            try:
                state_cache[n] = gh_api(f"repos/{{owner}}/{{repo}}/issues/{n}")["state"] == "closed"
            except subprocess.CalledProcessError:
                state_cache[n] = False  # unknown issue: wait rather than guess
        return state_cache[n]

    queue = build_queue(issues, is_closed, claimed_issues())
    executor = arg_value("--executor")
    if executor not in (None, "claude", "opencode"):
        sys.exit(f"unknown executor: {executor}")

    if "--json" in sys.argv:
        print(json.dumps(queue, indent=2))
    elif "--next" in sys.argv or "--next-json" in sys.argv:
        task = next_task(queue, executor, "--spillover" in sys.argv)
        if not task:
            sys.exit(1)
        print(json.dumps(task) if "--next-json" in sys.argv else task["number"])
    else:
        if not queue:
            print("Queue empty.")
        for t in queue:
            extra = f"  [{t['priority']}]" if t["priority"] != "normal" else ""
            ms = f" {t['milestone']}" if t["milestone"] else ""
            print(f"#{t['number']:<4} {status_text(t):<16} {t['model']:<6}{ms} {t['title']}{extra}")


if __name__ == "__main__":
    main()
