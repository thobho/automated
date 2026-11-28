#!/usr/bin/env python3
"""Decide whether the OpenCode worker may spend OpenRouter money right now.

The OpenCode worker has a daily budget (OPENROUTER_DAILY_USD, default 0.50), owner decision 2026-11-28:
cheap models take every routine task they can, and the day's money is there to be used.
  1. Hard limit: the key's own limit (set by the owner on openrouter.ai) must have at least
     OPENROUTER_MIN_TASK_USD (0.05) left.
  2. Daily cap: the key's usage today (`usage_daily`, UTC day, OpenRouter's reset) must stay below
     OPENROUTER_DAILY_USD with at least OPENROUTER_MIN_TASK_USD left.
  3. Monthly safety cap: usage this month below OPENROUTER_MONTHLY_USD (default 15.5 = 31 x 0.50, so
     it only stops a runaway, it does not pace).
  4. A task may spend at most OPENROUTER_TASK_USD (0.50); `task_budget_usd` in the output is the
     smaller of that and what is left under the caps above.

Input: the JSON from `GET https://openrouter.ai/api/v1/key` on stdin (the caller
fetches it, so this script never touches the key).

Output: one JSON line with "decision" ("RUN" or "WAIT"), the reason and the
numbers. Exit code 0 for RUN, 3 for WAIT, 2 for bad input.
"""
import json
import os
import sys
from datetime import datetime, timezone


def env(name, default):
    return float(os.environ.get(name, default))


DAILY_USD = env("OPENROUTER_DAILY_USD", 0.5)
MONTHLY_USD = env("OPENROUTER_MONTHLY_USD", 15.5)
TASK_USD = env("OPENROUTER_TASK_USD", 0.5)
MIN_TASK_USD = env("OPENROUTER_MIN_TASK_USD", 0.05)


def decide(key, now):
    data = key.get("data", key)
    if "usage_monthly" not in data:
        return {"decision": "WAIT", "reason": "no usage_monthly in the key info"}
    if "usage_daily" not in data:
        return {"decision": "WAIT", "reason": "no usage_daily in the key info"}
    used_month = float(data["usage_monthly"])
    used_today = float(data["usage_daily"])
    limit_remaining = data.get("limit_remaining")

    left = min(DAILY_USD - used_today, MONTHLY_USD - used_month)
    if limit_remaining is not None:
        left = min(left, float(limit_remaining))

    result = {
        "usage_daily_usd": round(used_today, 4),
        "daily_budget_usd": DAILY_USD,
        "usage_monthly_usd": round(used_month, 4),
        "monthly_budget_usd": MONTHLY_USD,
        "limit_remaining_usd": None if limit_remaining is None else round(float(limit_remaining), 4),
        "task_budget_usd": round(max(min(TASK_USD, left), 0.0), 2),
        "key_has_limit": data.get("limit") is not None,
        "day": now.strftime("%Y-%m-%d"),
    }
    if limit_remaining is not None and float(limit_remaining) < MIN_TASK_USD:
        result.update(decision="WAIT", reason=f"key limit nearly used (${float(limit_remaining):.2f} left)")
    elif used_month >= MONTHLY_USD:
        result.update(decision="WAIT", reason=f"monthly safety cap reached (${used_month:.2f} of ${MONTHLY_USD:.2f})")
    elif DAILY_USD - used_today < MIN_TASK_USD:
        result.update(decision="WAIT", reason=f"daily budget used (${used_today:.2f} of ${DAILY_USD:.2f} today, resets 00:00 UTC)")
    elif left < MIN_TASK_USD:
        result.update(decision="WAIT", reason=f"only ${left:.2f} left under the caps")
    else:
        result.update(decision="RUN", reason=f"${left:.2f} available now (${used_today:.2f} of ${DAILY_USD:.2f} used today)")
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
