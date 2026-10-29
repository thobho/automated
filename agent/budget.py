#!/usr/bin/env python3
"""Decide whether the autonomous worker may spend tokens right now.

Two gates, both must pass:
  1. 5-hour pace: used% must stay below a line that rises evenly across the
     window to FIVE_HOUR_CAP (default 80) at its reset, plus FIVE_HOUR_BUFFER
     (default 20) so a fresh window can start work at once.
  2. Weekly pace: used% must stay below a line that rises evenly from the
     start of the week to WEEKLY_CAP (default 80) at the reset, plus a small
     PACE_BUFFER so the first hours of a week aren't blocked.
  3. Parallel runs: a run in worker slot 2 or higher (AGENT_SLOT) starts only
     while the 5-hour window is below PARALLEL_CAP (default 60).

Input: the plan usage as JSON on stdin, in the shape the Claude desktop
`get_usage` tool returns (`{"plan": {"windows": [...]}}`), or just the
`plan` object itself.

Output: one JSON line with "decision" ("RUN" or "WAIT"), the reason, and the
numbers behind it. Exit code 0 for RUN, 3 for WAIT, 2 for bad input.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

FIVE_HOUR_CAP = float(os.environ.get("AGENT_FIVE_HOUR_CAP", 80))
WEEKLY_CAP = float(os.environ.get("AGENT_WEEKLY_CAP", 80))
PACE_BUFFER = float(os.environ.get("AGENT_PACE_BUFFER", 5))
FIVE_HOUR_BUFFER = float(os.environ.get("AGENT_FIVE_HOUR_BUFFER", 20))
PARALLEL_CAP = float(os.environ.get("AGENT_PARALLEL_CAP", 60))
SLOT = int(os.environ.get("AGENT_SLOT", 1))


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def find_window(windows, *needles):
    for w in windows:
        label = w.get("label", "").lower()
        if all(n in label for n in needles):
            return w
    return None


def paced_allowance(cap, buffer, resets_at, length, now):
    """Allowed used% now: rises evenly from `buffer` at the window start to `cap` at the reset."""
    if not resets_at:  # no window open yet: the next use starts one
        return min(buffer, cap), 0.0
    elapsed = (now - (parse_time(resets_at) - length)) / length
    elapsed = min(max(elapsed, 0.0), 1.0)
    return min(cap * elapsed + buffer, cap), elapsed


def decide(plan, now):
    if plan.get("status") not in (None, "ok"):
        return {"decision": "WAIT", "reason": f"plan limits unavailable ({plan.get('status')})"}

    windows = plan.get("windows", [])
    five = find_window(windows, "5-hour")
    weekly = find_window(windows, "weekly", "all")
    if not five or not weekly:
        return {"decision": "WAIT", "reason": "could not find 5-hour and weekly windows"}

    five_used = float(five["percentUsed"])
    weekly_used = float(weekly["percentUsed"])
    five_allowed, five_elapsed = paced_allowance(
        FIVE_HOUR_CAP, FIVE_HOUR_BUFFER, five.get("resetsAt"), timedelta(hours=5), now)
    weekly_allowed, elapsed = paced_allowance(
        WEEKLY_CAP, PACE_BUFFER, weekly.get("resetsAt"), timedelta(days=7), now)

    result = {
        "five_hour_used": five_used,
        "five_hour_allowed_now": round(five_allowed, 1),
        "five_hour_cap": FIVE_HOUR_CAP,
        "five_hour_resets_at": five.get("resetsAt"),
        "five_hour_elapsed_pct": round(five_elapsed * 100, 1),
        "weekly_used": weekly_used,
        "weekly_allowed_now": round(weekly_allowed, 1),
        "weekly_cap": WEEKLY_CAP,
        "weekly_resets_at": weekly.get("resetsAt"),
        "week_elapsed_pct": round(elapsed * 100, 1),
    }
    if five_used >= FIVE_HOUR_CAP:
        result.update(decision="WAIT", reason=f"5-hour window at {five_used:.0f}% (cap {FIVE_HOUR_CAP:.0f}%)")
    elif five_used >= five_allowed:
        result.update(decision="WAIT", reason=f"5-hour window at {five_used:.0f}%, ahead of pace ({five_allowed:.0f}% allowed so far)")
    elif SLOT > 1 and five_used >= PARALLEL_CAP:
        result.update(decision="WAIT", reason=f"slot {SLOT}: 5-hour window at {five_used:.0f}% (parallel cap {PARALLEL_CAP:.0f}%)")
    elif weekly_used >= weekly_allowed:
        result.update(decision="WAIT", reason=f"weekly at {weekly_used:.0f}%, ahead of pace ({weekly_allowed:.0f}% allowed so far)")
    else:
        result.update(decision="RUN", reason="within 5-hour pace and weekly pace")
    return result


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"decision": "WAIT", "reason": f"bad input: {e}"}))
        sys.exit(2)
    plan = data.get("plan", data)
    result = decide(plan, datetime.now(timezone.utc))
    print(json.dumps(result))
    sys.exit(0 if result["decision"] == "RUN" else 3)


if __name__ == "__main__":
    main()
