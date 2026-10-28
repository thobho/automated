#!/usr/bin/env python3
"""Order the agent queue and say which task is ready to work on.

Ordering rules:
  1. `agent:doing` issues come first: an earlier run was interrupted.
  2. `agent:todo` issues are ready only when every issue they depend on is
     closed (its PR was merged). Dependencies are lines in the issue body like
     "Depends on #12" or "Depends on: #12, #14".
  3. Ready todos: `priority:high` first, `priority:low` last, then by
     issue number (oldest first).

Parallel runs:
  - An issue claimed by a live worker run (`worker-lock.sh claimed`) is
    running and never picked again.
  - A `Uses: gus-bdl, playwright` line names shared resources. An issue is not
    ready while a running issue uses one of the same resources.

Usage:
  agent/pick_task.py          print the queue in order, with what each one waits on
  agent/pick_task.py --next   print the number of the next issue to work on
                              (a `doing` one, else the first ready todo); exit 1 if none
  agent/pick_task.py --json   the ordered queue as JSON

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
LOCK_SCRIPT = os.environ.get("AUTOMATED_LOCK_SCRIPT",
                             os.path.expanduser("~/.config/automated/worker-lock.sh"))


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


def claimed_issues():
    try:
        out = subprocess.run(["bash", LOCK_SCRIPT, "claimed"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return set()
    if out.returncode != 0:
        return set()
    return {int(n) for n in out.stdout.split() if n.isdigit()}


def build_queue(issues, is_closed, claimed):
    """issues: open GitHub issues (dicts with number, title, body, labels). Returns them ordered."""
    busy = {r for i in issues if i["number"] in claimed for r in resources(i["body"])}

    queue = []
    for issue in issues:
        labels = {l["name"] for l in issue["labels"]}
        state = next((l.split(":", 1)[1] for l in labels
                      if l in ("agent:doing", "agent:todo", "agent:blocked", "agent:review")), None)
        if not state:
            continue
        running = issue["number"] in claimed
        deps = dependencies(issue["body"])
        waiting_on = [n for n in deps if n != issue["number"] and not is_closed(n)]
        uses = sorted(resources(issue["body"]))
        resource_busy = [] if running else [r for r in uses if r in busy]
        priority = 0 if "priority:high" in labels else 2 if "priority:low" in labels else 1
        queue.append({
            "number": issue["number"],
            "title": issue["title"],
            "state": state,
            "running": running,
            "ready": not running and not resource_busy
                     and (state == "doing" or (state == "todo" and not waiting_on)),
            "waiting_on": waiting_on,
            "uses": uses,
            "resource_busy": resource_busy,
            "priority": ["high", "normal", "low"][priority],
            "model": next((l.split(":", 1)[1] for l in labels if l.startswith("model:")), "sonnet"),
            "project": next((l.split(":", 1)[1] for l in labels if l.startswith("project:")), None),
            "_sort": (["doing", "todo", "blocked", "review"].index(state),
                      0 if state != "todo" or not waiting_on else 1, priority, issue["number"]),
        })
    queue.sort(key=lambda t: t["_sort"])
    for t in queue:
        del t["_sort"]
    return queue


def status_text(t):
    if t["running"]:
        return "running"
    if t["state"] == "todo" and t["waiting_on"]:
        return f"waits on {', '.join('#%d' % n for n in t['waiting_on'])}"
    if t["resource_busy"] and t["state"] in ("todo", "doing"):
        return f"waits on {', '.join(t['resource_busy'])}"
    return "ready" if t["state"] == "todo" else t["state"]


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

    if "--json" in sys.argv:
        print(json.dumps(queue, indent=2))
    elif "--next" in sys.argv:
        ready = [t for t in queue if t["ready"]]
        if not ready:
            sys.exit(1)
        print(ready[0]["number"])
    else:
        if not queue:
            print("Queue empty.")
        for t in queue:
            extra = f"  [{t['priority']}]" if t["priority"] != "normal" else ""
            print(f"#{t['number']:<4} {status_text(t):<16} {t['model']:<6} {t['title']}{extra}")


if __name__ == "__main__":
    main()
