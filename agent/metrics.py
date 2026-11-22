#!/usr/bin/env python3
"""Last-7-days metrics for the health page: how well the agents work, not only whether they run.

  - Merged agent PRs: how many, first-pass approval rate (no "changes" round; a review skipped for red CI
    counts as a round, since it also sent the work back), median review rounds,
    median hours from PR opened to merged, returns to the builder (review changes, red CI).
  - Runs from the logs on pirx (`$AUTOMATED_RUNTIME/logs/<kind>-<n>-<time>.jsonl`): per kind and per build
    model: count, errors, median minutes, API-equivalent cost (what the same tokens would cost on the API;
    the plan itself is flat-rate, so this shows where the effort goes).
  - Red main: the newest finished CI run on main per project.

Computed at most once an hour (cached in state/metrics.json), because the health page refreshes often.

  agent/metrics.py           print the Markdown section (recomputed)
"""
import glob
import json
import os
import re
import statistics
import subprocess
import time
from datetime import datetime, timedelta, timezone

REPO = os.environ.get("AUTOMATED_GH_REPO", "thobho/automated")
RUNTIME = os.path.expanduser(os.environ.get("AUTOMATED_RUNTIME", "~/runtime/automated"))
CACHE = os.path.join(RUNTIME, "state", "metrics.json")
DAYS = 7
CHANGES = "<!-- automated:review-changes -->"
LOG_NAME = re.compile(r"^(claude|review|planner|conflict|retro|heal)-(?:(\d+)-)?")
BRANCH_ISSUE = re.compile(r"^agent/(\d+)-")


def gh_json(*args):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out) if out.strip() else []


def parse_run(lines):
    """The final `result` event of one stream-json run log: cost, minutes, error, main model."""
    res = None
    for line in lines:
        if '"type":"result"' not in line and '"type": "result"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") == "result":
            res = d
    if not res:
        return None
    usage = res.get("modelUsage") or {}
    model = max(usage, key=lambda m: usage[m].get("costUSD", 0), default="")
    short = next((k for k in ("opus", "sonnet", "haiku") if k in model), model or "?")
    return {"cost": float(res.get("total_cost_usd") or 0), "minutes": (res.get("duration_ms") or 0) / 60000,
            "error": bool(res.get("is_error")) or res.get("subtype") not in (None, "success"), "model": short}


def summarize_runs(runs):
    """runs: [(kind, parsed)] -> {kind: {...}}, plus "build:<model>" rows for Claude builds."""
    groups = {}
    for kind, r in runs:
        keys = [kind] + ([f"build:{r['model']}"] if kind == "claude" else [])
        for k in keys:
            groups.setdefault(k, []).append(r)
    out = {}
    for k, rs in groups.items():
        out[k] = {"runs": len(rs), "errors": sum(r["error"] for r in rs),
                  "median_min": round(statistics.median(r["minutes"] for r in rs), 1),
                  "cost": round(sum(r["cost"] for r in rs), 2)}
    return out


def summarize_prs(prs):
    """prs: merged agent PRs with createdAt, mergedAt, comments -> rates and medians."""
    if not prs:
        return {"merged": 0}
    rounds = [sum(CHANGES in (c.get("body") or "") for c in p.get("comments") or []) for p in prs]
    hours = [(datetime.fromisoformat(p["mergedAt"].replace("Z", "+00:00"))
              - datetime.fromisoformat(p["createdAt"].replace("Z", "+00:00"))).total_seconds() / 3600 for p in prs]
    return {"merged": len(prs), "first_pass": round(100 * sum(r == 0 for r in rounds) / len(prs)),
            "median_rounds": statistics.median(rounds), "median_hours": round(statistics.median(hours), 1),
            "returns": sum(rounds)}


def cost_per_task(prs, by_number):
    """Cost of each merged task: every build run of its issue plus the reviews and conflict fixes of its PR,
    grouped by the model of the last build (an escalated task counts under Opus). by_number maps
    (kind, number) -> [parsed runs]. Returns {model: {tasks, first_pass, per_task, escalated}}."""
    groups = {}
    for pr in prs:
        m = BRANCH_ISSUE.match(pr.get("headRefName", ""))
        builds = by_number.get(("claude", m.group(1)), []) if m else []
        if not builds:
            continue
        model = builds[-1]["model"]
        cost = sum(r["cost"] for r in builds)
        cost += sum(r["cost"] for k in ("review", "conflict") for r in by_number.get((k, str(pr["number"])), []))
        rounds = sum(CHANGES in (c.get("body") or "") for c in pr.get("comments") or [])
        g = groups.setdefault(model, {"tasks": 0, "first": 0, "cost": 0.0, "escalated": 0})
        g["tasks"] += 1
        g["first"] += rounds == 0
        g["cost"] += cost
        g["escalated"] += len({r["model"] for r in builds}) > 1
    return {m: {"tasks": g["tasks"], "first_pass": round(100 * g["first"] / g["tasks"]),
                "per_task": round(g["cost"] / g["tasks"], 2), "escalated": g["escalated"]} for m, g in groups.items()}


def collect(now):
    since = datetime.fromtimestamp(now, timezone.utc) - timedelta(days=DAYS)
    runs, by_number = [], {}
    for path in sorted(glob.glob(os.path.join(RUNTIME, "logs", "*.jsonl"))):  # names sort by run time
        m = LOG_NAME.match(os.path.basename(path))
        if not m:
            continue
        try:
            with open(path, errors="replace") as f:
                r = parse_run(f)
        except OSError:
            continue
        if not r:
            continue
        if m.group(2):  # all kept logs (30 days) count toward a task merged in the window
            by_number.setdefault((m.group(1), m.group(2)), []).append(r)
        if os.path.getmtime(path) >= since.timestamp():
            runs.append((m.group(1), r))
    prs = gh_json("pr", "list", "-R", REPO, "--state", "merged", "--limit", "100",
                  "--search", f"merged:>={since:%Y-%m-%d}", "--json", "number,headRefName,createdAt,mergedAt,comments")
    prs = [p for p in prs if p["headRefName"].startswith("agent/")]
    red = {}
    for wf in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".github", "workflows", "*-ci.yml")):
        name = os.path.basename(wf)
        try:
            last = gh_json("run", "list", "-R", REPO, "--branch", "main", "--workflow", name, "--status", "completed",
                           "--limit", "1", "--json", "conclusion")
        except subprocess.CalledProcessError:
            continue
        if last:
            red[name[:-len("-ci.yml")]] = last[0]["conclusion"]
    return {"ts": now, "runs": summarize_runs(runs), "prs": summarize_prs(prs), "main": red,
            "per_task": cost_per_task(prs, by_number)}


def cached(now, max_age=3600):
    try:
        with open(CACHE) as f:
            data = json.load(f)
        if now - data.get("ts", 0) < max_age:
            return data
    except (OSError, ValueError):
        pass
    data = collect(now)
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w") as f:
            json.dump(data, f)
    except OSError:
        pass
    return data


def render(data):
    p, runs = data.get("prs", {}), data.get("runs", {})
    lines = [f"### 3. How well is it working? (last {DAYS} days)"]
    if p.get("merged"):
        lines.append(f"- **{p['merged']}** task PRs merged · **{p['first_pass']}%** approved on the first review · "
                     f"median {p['median_rounds']:g} review round(s) · median **{p['median_hours']} h** from PR to merge · "
                     f"{p['returns']} return(s) to the builder")
    else:
        lines.append("- No task PR merged in the last 7 days.")
    per = data.get("per_task") or {}
    if per:
        lines += ["", "| Builder model | merged tasks | approved on first review | cost per merged task | escalated |",
                  "|---|---|---|---|---|"]
        for model in sorted(per, key=lambda k: -per[k]["tasks"]):
            g = per[model]
            lines.append(f"| {model} | {g['tasks']} | {g['first_pass']}% | ${g['per_task']:.2f} | {g['escalated']} |")
        lines.append("")
    main = data.get("main", {})
    red = [k for k, v in main.items() if v not in ("success", "skipped")]  # timed_out, cancelled, ... are not green
    lines.append("- Main: " + (", ".join(f"🔴 **{k} CI red**" for k in red) if red
                               else "✅ CI green on main for every project" if main else "no CI runs on main found"))
    if runs:
        lines += ["", "| Runs | count | errors | median min | API-equivalent cost |", "|---|---|---|---|---|"]
        order = ["claude"] + sorted(k for k in runs if k.startswith("build:")) + \
                [k for k in ("review", "conflict", "planner", "retro", "heal") if k in runs]
        names = {"claude": "Builds (Claude)", "review": "Reviews", "conflict": "Conflict fixes", "planner": "Planner",
                 "retro": "Retro", "heal": "Healer diagnosis"}
        for k in order:
            if k not in runs:
                continue
            r = runs[k]
            label = f"↳ builds on {k.split(':', 1)[1]}" if k.startswith("build:") else names.get(k, k)
            lines.append(f"| {label} | {r['runs']} | {r['errors']} | {r['median_min']} | ${r['cost']:.2f} |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(render(collect(time.time())))
