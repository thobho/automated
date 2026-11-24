#!/usr/bin/env python3
"""Keep the agent queue filled: decide when the planner may open the next batch of issues.

The owner writes the product plan once, as `projects/<project>/ROADMAP.md`. The planner never invents
product scope: it only turns stories that are in the roadmap and not yet in any issue into issues.

Roadmap format (lenient):
    ## M1 First product features          <- a milestone heading: "M<number> <title>"
    - US-1.1: Artist registration         <- a story: id, colon, title
    - US-1.2: Public artist page (depends: US-1.1)

A story counts as planned when any issue (open or closed) has a line `Story: US-1.1` (several ids
may share a line: "Story: US-1.1, US-1.2"). The `Story:` line is what the planner puts in every
issue it writes, so planning twice never duplicates.

The planner runs only when ALL of these hold (see `decide`):
  - the roadmap exists and has unplanned stories (no roadmap -> one `owner:todo` issue asks for it);
  - the ready backlog is small (todo + doing below MIN_BACKLOG, default 2);
  - the previous planner run was more than COOLDOWN_H ago (default 6 h);
  - every dependency of a story is already planned (so `Depends on #n` can be written);
  - at most MAX_NEW stories per run (default 4), from the earliest milestone that still has any.

Usage:
  agent/planner.py --json            the decision as JSON: {"action", "reason", "project", "milestone", "stories": [...]}
  agent/planner.py                   the same, one line
Exit code is 0 only when the action is PLAN, so shell code can `if planner.py --json > f; then`.
State (last plan time) lives in $AUTOMATED_RUNTIME/state/planner.json; `--mark-planned` updates it.
  agent/planner.py --format-stories <decision.json> [--ids]   the prompt's story lines (or the ids) for planner-run.sh
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

MIN_BACKLOG = int(os.environ.get("PLANNER_MIN_BACKLOG", 2))
COOLDOWN_H = float(os.environ.get("PLANNER_COOLDOWN_H", 6))
MAX_NEW = int(os.environ.get("PLANNER_MAX_NEW", 4))
RUNTIME = os.environ.get("AUTOMATED_RUNTIME", os.path.expanduser("~/runtime/automated"))
STATE_FILE = os.path.join(RUNTIME, "state", "planner.json")

MILESTONE = re.compile(r"^#{1,6}\s*(M\d+)\b[\s:.\-–—]*(.*)$")
STORY = re.compile(r"^\s*[-*]\s*\**\s*(US-[\w.]+)\**\s*[:\-–—]\s*(.+?)\s*$")
DEPENDS_ON_LINE = re.compile(r"depends\s+on", re.IGNORECASE)  # issue bodies: "Depends on: #12, #13"
ISSUE_REF = re.compile(r"#(\d+)")
DEPENDS = re.compile(r"\(\s*depends?\s*(?:on)?\s*:?\s*([^)]*)\)\s*$", re.IGNORECASE)
STORY_LINE = re.compile(r"^\s*\**story\s*:\**\s*(.+)$", re.IGNORECASE | re.MULTILINE)
STORY_ID = re.compile(r"US-[\w.]+", re.IGNORECASE)


def parse_roadmap(text):
    """Stories in file order: {"id", "title", "milestone", "milestone_title", "depends"}."""
    stories, milestone, mtitle = [], None, ""
    for line in (text or "").splitlines():
        m = MILESTONE.match(line)
        if m:
            milestone, mtitle = m.group(1).upper(), m.group(2).strip()
            continue
        s = STORY.match(line)
        if not s or milestone is None:
            continue
        title = s.group(2)
        depends = []
        d = DEPENDS.search(title)
        if d:
            depends = [x.upper() for x in STORY_ID.findall(d.group(1))]
            title = title[:d.start()].strip()
        stories.append({"id": s.group(1).upper(), "title": title, "milestone": milestone,
                        "milestone_title": mtitle, "depends": depends})
    return stories


def planned_ids(issues):
    """Story ids named on `Story:` lines of any issue body, open or closed."""
    found = set()
    for issue in issues:
        for line in STORY_LINE.findall(issue.get("body") or ""):
            found |= {x.upper() for x in STORY_ID.findall(line)}
    return found


def open_dependencies(issue, open_numbers):
    """Issue numbers on the body's `Depends on` lines that are still open."""
    deps = []
    for line in (issue.get("body") or "").splitlines():
        if DEPENDS_ON_LINE.search(line):
            deps += [int(n) for n in ISSUE_REF.findall(line)]
    return [n for n in deps if n != issue.get("number") and n in open_numbers]


def backlog_size(issues, project=None):
    """Open issues the dispatcher can pick up soon: agent:doing, or agent:todo whose dependencies are closed.

    A todo that waits on an open issue is not backlog: counting it let a chain T29 -> T30 -> T31 keep the
    backlog "full" while nothing was ready, and the plan sat idle (36 idle hours in 2026-11-15..21).
    Closed issues are ignored (merged tasks can keep a stale agent:todo label), and with `project`
    only that project's issues count, so another project's queue does not stop the planner."""
    open_numbers = {i.get("number") for i in issues if str(i.get("state", "OPEN")).upper() == "OPEN"}
    n = 0
    for issue in issues:
        if str(issue.get("state", "OPEN")).upper() != "OPEN":
            continue
        labels = {l["name"] for l in issue.get("labels", [])}
        if "agent:done" in labels or not labels & {"agent:todo", "agent:doing"}:
            continue
        if project and f"project:{project}" not in labels:
            continue
        if "agent:doing" not in labels and open_dependencies(issue, open_numbers):
            continue
        n += 1
    return n


def milestone_number(name):
    return int(re.sub(r"\D", "", name) or 0)


def decide(stories, planned, backlog, last_plan_ts, now, *, min_backlog=None, cooldown_h=None, max_new=None):
    """Return {"action": PLAN|SKIP|NEED_ROADMAP, "reason", "stories"}; pure, so it can be tested."""
    min_backlog = MIN_BACKLOG if min_backlog is None else min_backlog
    cooldown_h = COOLDOWN_H if cooldown_h is None else cooldown_h
    max_new = MAX_NEW if max_new is None else max_new
    if not stories:
        return {"action": "NEED_ROADMAP", "reason": "no stories in the roadmap", "stories": []}
    todo = [s for s in stories if s["id"] not in planned]
    if not todo:
        return {"action": "SKIP", "reason": "every roadmap story is already planned", "stories": []}
    if backlog >= min_backlog:
        return {"action": "SKIP", "reason": f"backlog is {backlog} (planner runs below {min_backlog})", "stories": []}
    if last_plan_ts and now - last_plan_ts < cooldown_h * 3600:
        wait = cooldown_h - (now - last_plan_ts) / 3600
        return {"action": "SKIP", "reason": f"last plan was recent (cooldown, {wait:.1f} h left)", "stories": []}
    first = min(milestone_number(s["milestone"]) for s in todo)
    group = [s for s in todo if milestone_number(s["milestone"]) == first]
    known = set(planned)
    chosen = []
    for s in group:  # file order; a story needs its dependencies planned or chosen earlier in this batch
        if all(d in known for d in s["depends"]):
            chosen.append(s)
            known.add(s["id"])
        if len(chosen) >= max_new:
            break
    if not chosen:
        return {"action": "SKIP", "reason": "the next stories wait on dependencies that are not in the roadmap",
                "stories": []}
    return {"action": "PLAN", "reason": f"{len(chosen)} unplanned stories, backlog {backlog}", "stories": chosen}


def format_stories(decision):
    """The "Stories to plan" lines for the planner prompt, one per story, in planning order."""
    lines = []
    for s in decision.get("stories", []):
        dep = ", ".join(s.get("depends") or []) or "none"
        lines.append(f"- {s['id']}: {s['title']} (depends on stories: {dep})")
    return "\n".join(lines)


def gh_json(args):
    out = subprocess.run(["gh"] + args, check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def load_roadmaps(root):
    """{project: stories} for every projects/<project>/ROADMAP.md under root."""
    result = {}
    for path in sorted(glob.glob(os.path.join(root, "projects", "*", "ROADMAP.md"))):
        project = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as f:
            result[project] = parse_roadmap(f.read())
    return result


def read_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)


def main():
    root = os.environ.get("AUTOMATED_RUNNER_DIR", os.path.expanduser("~/Projects/automated-work/runner"))
    state = read_state()
    if "--format-stories" in sys.argv:  # --format-stories <decision.json>: prompt lines, or "ids" with --ids
        with open(sys.argv[sys.argv.index("--format-stories") + 1], encoding="utf-8") as f:
            decision = json.load(f)
        if "--ids" in sys.argv:
            print(" ".join(s["id"] for s in decision.get("stories", [])))
        else:
            print(format_stories(decision))
        return
    if "--mark-planned" in sys.argv:
        state["last_plan_ts"] = time.time()
        write_state(state)
        return
    issues = gh_json(["issue", "list", "--state", "all", "--limit", "500", "--json", "number,state,body,labels"])
    roadmaps = load_roadmaps(root)
    planned = planned_ids(issues)
    result = None
    for project, stories in roadmaps.items():
        d = decide(stories, planned, backlog_size(issues, project), state.get("last_plan_ts"), time.time())
        d["project"] = project
        d["milestone"] = d["stories"][0]["milestone"] if d["stories"] else None
        d["milestone_title"] = d["stories"][0]["milestone_title"] if d["stories"] else None
        if d["action"] == "PLAN":
            result = d
            break
        result = result or d
    if result is None:
        result = {"action": "NEED_ROADMAP", "reason": "no projects/<project>/ROADMAP.md found",
                  "project": None, "milestone": None, "stories": []}
    if "--json" in sys.argv:
        print(json.dumps(result))
    else:
        print(f"{result['action']}: {result['reason']}")
    sys.exit(0 if result["action"] == "PLAN" else 1)


if __name__ == "__main__":
    main()
