#!/usr/bin/env python3
"""Decide whether the OpenCode worker may spend OpenRouter money right now.

The OpenCode worker has a monthly budget (OPENROUTER_MONTHLY_USD, default 10)
that it spends evenly through the month:
  1. Hard limit: the key's own limit (set by the owner on openrouter.ai, with a
     monthly reset) must have at least OPENROUTER_MIN_TASK_USD (0.25) left.
  2. Pace: usage this month must stay below
        OPENROUTER_MONTHLY_USD x share of the month elapsed + OPENROUTER_PACE_BUFFER_USD (0.5).
     In the last OPENROUTER_FREE_DAYS (2) days of the month the pace gate is off,
     so the rest of the budget is used before the reset.
  3. A task may spend at most OPENROUTER_TASK_USD (0.75); `task_budget_usd` in the
     output is the smaller of that and what is left under both gates.

Input: the JSON from `GET https://openrouter.ai/api/v1/key` on stdin (the caller
fetches it, so this script never touches the key). Months are in UTC, like
OpenRouter's monthly reset.

Output: one JSON line with "decision" ("RUN" or "WAIT"), the reason and the
numbers. Exit code 0 for RUN, 3 for WAIT, 2 for bad input.
"""
import calendar
import json
import os
import sys
from datetime import datetime, timezone


def env(name, default):
    return float(os.environ.get(name, default))


MONTHLY_USD = env("OPENROUTER_MONTHLY_USD", 10)
PACE_BUFFER_USD = env("OPENROUTER_PACE_BUFFER_USD", 0.5)
TASK_USD = env("OPENROUTER_TASK_USD", 0.75)
MIN_TASK_USD = env("OPENROUTER_MIN_TASK_USD", 0.25)
FREE_DAYS = env("OPENROUTER_FREE_DAYS", 2)


def month_elapsed(now):
    days = calendar.monthrange(now.year, now.month)[1]
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    seconds = (now - start).total_seconds()
    return seconds / (days * 86400), days - seconds / 86400


def decide(key, now):
    data = key.get("data", key)
    if "usage_monthly" not in data:
        return {"decision": "WAIT", "reason": "no usage_monthly in the key info"}
    used = float(data["usage_monthly"])
    limit_remaining = data.get("limit_remaining")
    elapsed, days_left = month_elapsed(now)

    final_days = days_left <= FREE_DAYS
    pace_allowed = MONTHLY_USD if final_days else min(MONTHLY_USD * elapsed + PACE_BUFFER_USD, MONTHLY_USD)
    left = pace_allowed - used
    if limit_remaining is not None:
        left = min(left, float(limit_remaining))

    result = {
        "usage_monthly_usd": round(used, 4),
        "monthly_budget_usd": MONTHLY_USD,
        "allowed_now_usd": round(pace_allowed, 2),
        "limit_remaining_usd": None if limit_remaining is None else round(float(limit_remaining), 4),
        "month_elapsed_pct": round(elapsed * 100, 1),
        "pace_gate": not final_days,
        "task_budget_usd": round(max(min(TASK_USD, left), 0.0), 2),
        "key_has_limit": data.get("limit") is not None,
    }
    if limit_remaining is not None and float(limit_remaining) < MIN_TASK_USD:
        result.update(decision="WAIT", reason=f"key limit nearly used (${float(limit_remaining):.2f} left)")
    elif used >= MONTHLY_USD:
        result.update(decision="WAIT", reason=f"monthly budget used (${used:.2f} of ${MONTHLY_USD:.2f})")
    elif left < MIN_TASK_USD:
        result.update(decision="WAIT", reason=f"ahead of the monthly pace (${used:.2f} used, ${pace_allowed:.2f} allowed so far)")
    else:
        result.update(decision="RUN", reason=f"${left:.2f} available now (${used:.2f} of ${MONTHLY_USD:.2f} used this month)")
    return result


def main():
    try:
        key = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"decision": "WAIT", "reason": f"bad input: {e}"}))
        sys.exit(2)
    result = decide(key, datetime.now(timezone.utc))
    print(json.dumps(result))
    sys.exit(0 if result["decision"] == "RUN" else 3)


if __name__ == "__main__":
    main()
