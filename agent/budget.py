#!/usr/bin/env python3
"""Decide whether an agent run may spend Claude plan tokens right now.

The goal is an even burn: the plan is used steadily through the week, so the
owner always has headroom for small things in Claude Code.

Gates (all must pass):
  1. 5-hour pace: used% must stay below a line that rises evenly across the
     window from FIVE_HOUR_BUFFER (default 15) to FIVE_HOUR_CAP (default 70)
     at its reset.
  2. Weekly even line: used% must stay below
        WEEKLY_BASE + WEEKLY_SLOPE x share of the week elapsed
     (defaults 5 + 90 x elapsed). In the last WEEKLY_FINAL_HOURS (12) of the
     week the line opens up to WEEKLY_CAP (98), so nothing is wasted.
     headroom = line - used.
  3. Opus (AGENT_MODEL=opus): only with headroom >= OPUS_HEADROOM (5).
  4. Parallel runs (AGENT_SLOT >= 2): only with headroom >= PARALLEL_HEADROOM
     (10) and the 5-hour window below PARALLEL_CAP (50).

The output also says whether spillover is allowed (headroom >= SPILLOVER_HEADROOM,
default 10): then a Claude run may take simple tasks meant for OpenCode when no
Claude task is ready.

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


def env(name, default):
    return float(os.environ.get(name, default))


FIVE_HOUR_CAP = env("AGENT_FIVE_HOUR_CAP", 70)
FIVE_HOUR_BUFFER = env("AGENT_FIVE_HOUR_BUFFER", 15)
WEEKLY_BASE = env("AGENT_WEEKLY_BASE", 5)
WEEKLY_SLOPE = env("AGENT_WEEKLY_SLOPE", 90)
WEEKLY_CAP = env("AGENT_WEEKLY_CAP", 98)
WEEKLY_FINAL_HOURS = env("AGENT_WEEKLY_FINAL_HOURS", 12)
OPUS_HEADROOM = env("AGENT_OPUS_HEADROOM", 5)
PARALLEL_HEADROOM = env("AGENT_PARALLEL_HEADROOM", 10)
PARALLEL_CAP = env("AGENT_PARALLEL_CAP", 50)
SPILLOVER_HEADROOM = env("AGENT_SPILLOVER_HEADROOM", 10)
SLOT = int(os.environ.get("AGENT_SLOT", 1))
MODEL = os.environ.get("AGENT_MODEL", "sonnet").lower()

WEEK = timedelta(days=7)


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def find_window(windows, *needles):
    for w in windows:
        label = w.get("label", "").lower()
        if all(n in label for n in needles):
            return w
    return None


def five_hour_allowance(resets_at, now):
    """Allowed used% now: rises evenly from the buffer at the window start to the cap at the reset."""
    if not resets_at:  # no window open yet: the next use starts one
        return min(FIVE_HOUR_BUFFER, FIVE_HOUR_CAP), 0.0
    length = timedelta(hours=5)
    elapsed = min(max((now - (parse_time(resets_at) - length)) / length, 0.0), 1.0)
    return min(FIVE_HOUR_CAP * elapsed + FIVE_HOUR_BUFFER, FIVE_HOUR_CAP), elapsed


def weekly_line(resets_at, now):
    """Allowed used% now on the even weekly line; opens to the cap in the final hours."""
    if not resets_at:
        return min(WEEKLY_BASE, WEEKLY_CAP), 0.0
    reset = parse_time(resets_at)
    elapsed = min(max((now - (reset - WEEK)) / WEEK, 0.0), 1.0)
    if reset - now <= timedelta(hours=WEEKLY_FINAL_HOURS):
        return WEEKLY_CAP, elapsed
    return min(WEEKLY_BASE + WEEKLY_SLOPE * elapsed, WEEKLY_CAP), elapsed


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
    five_allowed, five_elapsed = five_hour_allowance(five.get("resetsAt"), now)
    line, elapsed = weekly_line(weekly.get("resetsAt"), now)
    headroom = line - weekly_used

    result = {
        "model": MODEL,
        "slot": SLOT,
        "five_hour_used": five_used,
        "five_hour_allowed_now": round(five_allowed, 1),
        "five_hour_cap": FIVE_HOUR_CAP,
        "five_hour_resets_at": five.get("resetsAt"),
        "five_hour_elapsed_pct": round(five_elapsed * 100, 1),
        "weekly_used": weekly_used,
        "weekly_allowed_now": round(line, 1),
        "weekly_cap": WEEKLY_CAP,
        "weekly_headroom": round(headroom, 1),
        "weekly_resets_at": weekly.get("resetsAt"),
        "week_elapsed_pct": round(elapsed * 100, 1),
        "opus_ok": headroom >= OPUS_HEADROOM,
        "spillover_ok": headroom >= SPILLOVER_HEADROOM,
    }
    if five_used >= FIVE_HOUR_CAP:
        result.update(decision="WAIT", reason=f"5-hour window at {five_used:.0f}% (cap {FIVE_HOUR_CAP:.0f}%)")
    elif five_used >= five_allowed:
        result.update(decision="WAIT", reason=f"5-hour window at {five_used:.0f}%, ahead of pace ({five_allowed:.0f}% allowed so far)")
    elif headroom <= 0:
        result.update(decision="WAIT", reason=f"weekly at {weekly_used:.0f}%, ahead of the even line ({line:.0f}% allowed now)")
    elif SLOT > 1 and (headroom < PARALLEL_HEADROOM or five_used >= PARALLEL_CAP):
        result.update(decision="WAIT", reason=f"slot {SLOT}: needs {PARALLEL_HEADROOM:.0f} points of weekly headroom (has {headroom:.0f}) and the 5-hour window below {PARALLEL_CAP:.0f}% (at {five_used:.0f}%)")
    elif MODEL == "opus" and headroom < OPUS_HEADROOM:
        result.update(decision="WAIT", reason=f"opus needs {OPUS_HEADROOM:.0f} points of weekly headroom (has {headroom:.0f})")
    else:
        result.update(decision="RUN", reason=f"within 5-hour pace and {headroom:.0f} points under the weekly line")
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
