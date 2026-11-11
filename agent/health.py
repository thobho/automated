#!/usr/bin/env python3
"""Health page of the automation: one pinned GitHub issue ("🩺 Automation health", label agent:status)
that answers two questions at a glance:
  1. Is the automation alive and working?  (heartbeat of every component, last decisions)
  2. Do I have blockers or errors?          (blocked tasks, failed runs, red CI, failed units, owner tasks)

Runs on pirx as the `agent` user: after every runner event (status_update in agent/pirx/common.sh) and every
30 minutes from the `automated-health` timer, so a component that stops shows up as late even when
nothing else happens. If the page itself stops updating, its "Updated" time goes stale, and the 08:00
WhatsApp message says so (agent/pirx/report-send.sh checks the issue's update time).

  agent/health.py           render and write the issue
  agent/health.py --print   render only
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

REPO = os.environ.get("AUTOMATED_GH_REPO", "thobho/automated")
TZ = ZoneInfo(os.environ.get("AGENT_TZ", "Europe/Warsaw"))
RUNTIME = os.path.expanduser(os.environ.get("AUTOMATED_RUNTIME", "~/runtime/automated"))
STATE = os.path.join(RUNTIME, "state")
TITLE = "🩺 Automation health"
ERROR_WORDS = re.compile(r"fail|error|without a verdict|without a PR|rejected|timed out|stopped at the task budget", re.I)

# component -> (what it is, how often it should run, a hint when it is late)
COMPONENTS = {
    "dispatcher": ("Mac dispatcher → pirx (Claude runs)", timedelta(hours=2),
                   "the Mac is asleep or the Claude app is closed; Claude runs pause, OpenCode continues"),
    "opencode": ("OpenCode worker (pirx timer)", timedelta(hours=2), "check `systemctl --user status automated-opencode` as agent"),
    "health": ("This page (pirx timer)", timedelta(hours=1), "check `systemctl --user status automated-health` as agent"),
    "report": ("Daily report (07:45)", timedelta(hours=26), "check `systemctl --user status automated-report` as agent"),
    "claude-run": ("Last Claude build run", None, None),
    "review": ("Last AI review", None, None),
}


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def gh_json(*args):
    out = gh(*args)
    return json.loads(out) if out.strip() else []


def load(name):
    try:
        with open(os.path.join(STATE, name)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def ago(seconds):
    if seconds is None:
        return "never"
    m = int(seconds // 60)
    if m < 60:
        return f"{m} min ago"
    h = m // 60
    return f"{h} h {m % 60} min ago" if h < 48 else f"{h // 24} days ago"


def local(ts):
    return datetime.fromtimestamp(ts, TZ).strftime("%a %H:%M")


def heartbeats(now):
    rows, problems, late_keys = [], [], set()
    for key, (label, every, hint) in COMPONENTS.items():
        try:
            ts = float(open(os.path.join(STATE, f"beat-{key}")).read().strip())
        except (OSError, ValueError):
            ts = None
        age = None if ts is None else now - ts
        if every is None:
            mark = "·"
        elif ts is None:
            mark = "⚪ not yet"
        elif age <= every.total_seconds():
            mark = "✅"
        else:
            mark = "⚠️ late"
            late_keys.add(key)
            problems.append(f"{label}: last ran {ago(age)}. Likely cause: {hint}.")
        when = "never" if ts is None else f"{local(ts)} ({ago(age)})"
        rows.append(f"| {label} | {mark} | {when} |")
    return rows, problems, late_keys


def failed_units():
    try:
        out = subprocess.run(["systemctl", "--user", "list-units", "--failed", "--no-legend", "automated-*"],
                             capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [l.split()[0].lstrip("●").strip() for l in out.splitlines() if l.strip()]


def recent_events(now, hours=24):
    since = datetime.fromtimestamp(now - hours * 3600, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    events = []
    try:
        with open(os.path.join(STATE, "events.log")) as f:
            for line in f:
                ts, _, note = line.rstrip("\n").partition("|")
                if ts >= since:
                    events.append((ts, note))
    except OSError:
        pass
    return events


def render(now):
    beat_rows, late, late_keys = heartbeats(now)
    events = recent_events(now)
    errors = [(ts, n) for ts, n in events if ERROR_WORDS.search(n)]
    units = failed_units()

    issues = [i for i in gh_json("api", f"repos/{REPO}/issues?state=open&per_page=100") if "pull_request" not in i]
    def has(i, label):
        return any(l["name"] == label for l in i["labels"])
    blocked = [i for i in issues if has(i, "agent:blocked")]
    owner = [i for i in issues if has(i, "owner:todo")]
    states = {s: sum(has(i, f"agent:{s}") for i in issues) for s in ("todo", "doing", "review", "blocked")}
    prs = gh_json("pr", "list", "-R", REPO, "--state", "open", "--json", "number,title,url,headRefName,statusCheckRollup")
    red = [p for p in prs if p["headRefName"].startswith("agent") and any(
        (c.get("conclusion") or "").upper() in ("FAILURE", "ERROR", "TIMED_OUT", "CANCELLED") for c in p.get("statusCheckRollup") or [])]

    claude, opencode = load("claude-budget.json"), load("openrouter-budget.json")
    last_decisions = []
    if claude.get("decision"):
        last_decisions.append(f"Claude: **{claude['decision']}**: {claude.get('reason', '')}")
    if opencode.get("decision"):
        last_decisions.append(f"OpenCode: **{opencode['decision']}**: {opencode.get('reason', '')}")

    problems = late + [f"Failed systemd unit: `{u}`" for u in units]
    problems += [f"#{i['number']} {i['title']}: blocked, needs your answer" for i in blocked]
    problems += [f"PR #{p['number']} {p['title']}: CI is red" for p in red]
    problems += [f"{datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(TZ):%a %H:%M} {n}" for ts, n in errors[-8:]]

    if "opencode" in late_keys or units:
        verdict = "🔴 **Not working on pirx**: its timers are not running (see below)."
    elif "dispatcher" in late_keys:
        verdict = "🟡 **Claude runs paused**: the Mac dispatcher has not checked in (Mac asleep or Claude app closed)."
    elif problems:
        verdict = f"🟡 **Needs attention**: {len(problems)} item(s) below."
    else:
        verdict = "🟢 **Running normally**: every component checked in on time and nothing is blocked."

    def lst(items, empty):
        return "\n".join(f"- {x}" for x in items) if items else empty

    report = gh_json("api", f"repos/{REPO}/issues?labels=agent:report&state=open&per_page=1")
    report_link = f"[📋 Daily reports]({report[0]['html_url']})" if report else "📋 Daily reports: none yet"
    return f"""## {TITLE}
{verdict}

_Updated {datetime.fromtimestamp(now, TZ):%a %d %b %H:%M} (Warsaw). Refreshes every 30 min and after every run; if this time is more than an hour old, pirx itself is down._

### 1. Is it alive?
| Component | State | Last run |
|---|---|---|
{chr(10).join(beat_rows)}

{lst(last_decisions, '_No budget decision recorded yet._')}

### 2. Blockers and errors
{lst(problems, '✅ None.')}

### Your open actions ({len(owner)})
{lst([f"#{i['number']} {i['title']}" for i in owner], '✅ None.')}

### Queue
todo {states['todo']} · doing {states['doing']} · in AI review {states['review']} · blocked {states['blocked']}

### Last events (24 h)
{lst([f"{datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(TZ):%a %H:%M} {n}" for ts, n in events[-10:]], '_No events in the last 24 h._')}

{report_link} · Logs on pirx: `~agent/runtime/automated/logs/`
"""


def main():
    now = time.time()
    body = render(now)
    if "--print" in sys.argv:
        print(body)
        return
    found = gh_json("api", f"repos/{REPO}/issues?labels=agent:status&state=open&per_page=1")
    if found:
        n = found[0]["number"]
        gh("issue", "edit", str(n), "-R", REPO, "--title", TITLE, "--body", body)
    else:
        url = gh("issue", "create", "-R", REPO, "--title", TITLE, "--label", "agent:status", "--body", body).strip()
        n = int(url.rsplit("/", 1)[1])
        subprocess.run(["gh", "issue", "pin", str(n), "-R", REPO], capture_output=True)
    with open(os.path.join(STATE, "beat-health"), "w") as f:
        f.write(str(int(now)))
    print(f"https://github.com/{REPO}/issues/{n}")


if __name__ == "__main__":
    main()
