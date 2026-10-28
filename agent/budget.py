#!/usr/bin/env python3
"""Decide whether the autonomous worker may spend tokens right now.

Two gates, both must pass:
  1. 5-hour window: used% must stay below FIVE_HOUR_CAP (default 80).
  2. Weekly pace: used% must stay below a line that rises evenly from the
     start of the week to WEEKLY_CAP (default 80) at the reset, plus a small
     PACE_BUFFER so the first hours of a week aren't blocked.

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


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def find_window(windows, *needles):
    for w in windows:
        label = w.get("label", "").lower()
        if all(n in label for n in needles):
            return w
    return None


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
    weekly_reset = parse_time(weekly["resetsAt"])
    week_start = weekly_reset - timedelta(days=7)
    elapsed = min(max((now - week_start) / timedelta(days=7), 0.0), 1.0)
    weekly_allowed = min(WEEKLY_CAP * elapsed + PACE_BUFFER, WEEKLY_CAP)

    result = {
        "five_hour_used": five_used,
        "five_hour_cap": FIVE_HOUR_CAP,
        "five_hour_resets_at": five["resetsAt"],
        "weekly_used": weekly_used,
        "weekly_allowed_now": round(weekly_allowed, 1),
        "weekly_cap": WEEKLY_CAP,
        "weekly_resets_at": weekly["resetsAt"],
        "week_elapsed_pct": round(elapsed * 100, 1),
    }
    if five_used >= FIVE_HOUR_CAP:
        result.update(decision="WAIT", reason=f"5-hour window at {five_used:.0f}% (cap {FIVE_HOUR_CAP:.0f}%)")
    elif weekly_used >= weekly_allowed:
        result.update(decision="WAIT", reason=f"weekly at {weekly_used:.0f}%, ahead of pace ({weekly_allowed:.0f}% allowed so far)")
    else:
        result.update(decision="RUN", reason="within 5-hour cap and weekly pace")
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
