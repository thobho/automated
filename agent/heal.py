#!/usr/bin/env python3
"""Decisions for the healer on pirx (agent/pirx/heal.sh). Pure functions, so they can be tested.

  heal.py track <state.json> [fingerprint ...]   update consecutive counts of the problems seen in this
                                                 run; prints JSON {"new": [...], "diagnose": [...]}
  heal.py mark <state.json> <fingerprint>        record that a diagnosis run started for it
  heal.py stuck <issues.json> <claims,comma,sep> issues in agent:doing with no live run for over an hour
  heal.py money <key name> < key-info.json        an alert line if an OpenRouter key is close to its limit

A problem is diagnosed by a model when it is still there after REPEAT_RUNS healer runs in a row
(the fixed fixes did not help), at most once per DIAGNOSE_EVERY_H hours for the same problem.
"""
import json
import sys
import time
from datetime import datetime

REPEAT_RUNS = 3          # 3 runs, 30 minutes apart: the problem survived an hour of fixes
DIAGNOSE_EVERY_H = 6
STUCK_AFTER_S = 3600
MONEY_MIN_USD = 2.0      # alert when a key has less than this left (or 10% of its limit, if larger)


def track(state, seen, now):
    """Update counts in `state` for this run's problems. Returns (new, diagnose)."""
    counts = state.setdefault("counts", {})
    last = state.setdefault("diagnosed", {})
    for fp in list(counts):
        if fp not in seen:
            del counts[fp]          # fixed: the next occurrence starts from 1 again
    new, diagnose = [], []
    for fp in seen:
        counts[fp] = counts.get(fp, 0) + 1
        if counts[fp] == 1:
            new.append(fp)
        if counts[fp] >= REPEAT_RUNS and now - last.get(fp, 0) > DIAGNOSE_EVERY_H * 3600:
            diagnose.append(fp)
    return new, diagnose


def stuck(issues, claims, now):
    """Issue numbers in agent:doing that no live run claims and that nobody touched for an hour."""
    out = []
    for i in issues:
        if "pull_request" in i or "agent:doing" not in {l["name"] for l in i.get("labels", [])}:
            continue
        if str(i["number"]) in claims:
            continue
        updated = datetime.fromisoformat(i["updated_at"].replace("Z", "+00:00")).timestamp()
        if now - updated > STUCK_AFTER_S:
            out.append(i["number"])
    return out


def money(name, info):
    """Alert text when the key's own limit is nearly used up; None when fine or unknown."""
    data = info.get("data", info)
    limit, left = data.get("limit"), data.get("limit_remaining")
    if limit is None or left is None:
        return None
    if left < max(MONEY_MIN_USD, 0.1 * limit):
        return f"OpenRouter key '{name}' has ${left:.2f} left of its ${limit:.0f} limit"
    return None


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    now = time.time()
    if cmd == "track":
        state = load(argv[2], {})
        new, diagnose = track(state, argv[3:], now)
        with open(argv[2], "w") as f:
            json.dump(state, f)
        print(json.dumps({"new": new, "diagnose": diagnose}))
    elif cmd == "mark":
        state = load(argv[2], {})
        state.setdefault("diagnosed", {})[argv[3]] = now
        with open(argv[2], "w") as f:
            json.dump(state, f)
    elif cmd == "stuck":
        claims = {c for c in argv[3].split(",") if c} if len(argv) > 3 else set()
        print("\n".join(str(n) for n in stuck(load(argv[2], []), claims, now)))
    elif cmd == "money":
        alert = money(argv[2], json.load(sys.stdin))
        if alert:
            print(alert)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
