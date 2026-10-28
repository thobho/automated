#!/usr/bin/env python3
"""Order the agent queue and say which task is ready to work on.

Ordering rules:
  1. `agent:doing` issues come first: an earlier run was interrupted.
  2. `agent:todo` issues are ready only when every issue they depend on is
     closed (its PR was merged). Dependencies are lines in the issue body like
     "Depends on #12" or "Depends on: #12, #14".
  3. Ready todos: `priority:high` first, `priority:low` last, then by
     issue number (oldest first).

Usage:
  agent/pick_task.py          print the queue in order, with what each one waits on
  agent/pick_task.py --next   print the number of the next issue to work on
                              (a `doing` one, else the first ready todo); exit 1 if none
  agent/pick_task.py --json   the ordered queue as JSON
"""
import json
import re
import subprocess
import sys

DEPENDS = re.compile(r"depends\s+on", re.IGNORECASE)
ISSUE_REF = re.compile(r"#(\d+)")


def gh_api(path):
    out = subprocess.run(["gh", "api", path], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def dependencies(body):
    deps = []
    for line in (body or "").splitlines():
        if DEPENDS.search(line):
            deps += [int(n) for n in ISSUE_REF.findall(line)]
    return deps


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

    queue = []
    for issue in issues:
        labels = {l["name"] for l in issue["labels"]}
        state = next((l.split(":", 1)[1] for l in labels
                      if l in ("agent:doing", "agent:todo", "agent:blocked", "agent:review")), None)
        if not state:
            continue
        deps = dependencies(issue["body"])
        waiting_on = [n for n in deps if n != issue["number"] and not is_closed(n)]
        priority = 0 if "priority:high" in labels else 2 if "priority:low" in labels else 1
        queue.append({
            "number": issue["number"],
            "title": issue["title"],
            "state": state,
            "ready": state == "doing" or (state == "todo" and not waiting_on),
            "waiting_on": waiting_on,
            "priority": ["high", "normal", "low"][priority],
            "model": next((l.split(":", 1)[1] for l in labels if l.startswith("model:")), "sonnet"),
            "project": next((l.split(":", 1)[1] for l in labels if l.startswith("project:")), None),
            "_sort": (["doing", "todo", "blocked", "review"].index(state),
                      0 if state != "todo" or not waiting_on else 1, priority, issue["number"]),
        })
    queue.sort(key=lambda t: t["_sort"])
    for t in queue:
        del t["_sort"]

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
            if t["state"] == "todo":
                status = f"waits on {', '.join('#%d' % n for n in t['waiting_on'])}" if t["waiting_on"] else "ready"
            else:
                status = t["state"]
            extra = f"  [{t['priority']}]" if t["priority"] != "normal" else ""
            print(f"#{t['number']:<4} {status:<16} {t['model']:<6} {t['title']}{extra}")


if __name__ == "__main__":
    main()
