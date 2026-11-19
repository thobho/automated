#!/usr/bin/env python3
"""Last-7-days metrics for the health page: how well the agents work, not only whether they run.

  - Merged agent PRs: how many, first-pass approval rate (no "changes" round), median review rounds,
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
LOG_NAME = re.compile(r"^(claude|review|planner|conflict|retro|heal)-")


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


def collect(now):
    since = datetime.fromtimestamp(now, timezone.utc) - timedelta(days=DAYS)
    runs = []
    for path in glob.glob(os.path.join(RUNTIME, "logs", "*.jsonl")):
        m = LOG_NAME.match(os.path.basename(path))
        if not m or os.path.getmtime(path) < since.timestamp():
            continue
        try:
            with open(path, errors="replace") as f:
                r = parse_run(f)
        except OSError:
            continue
        if r:
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
    return {"ts": now, "runs": summarize_runs(runs), "prs": summarize_prs(prs), "main": red}


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
    main = data.get("main", {})
    red = [k for k, v in main.items() if v == "failure"]
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
