#!/usr/bin/env python3
"""Read the Claude plan limits on pirx, without the Mac.

Headless Claude Code runs (`claude -p --output-format stream-json --verbose`) emit `rate_limit_event`
lines with the plan's 5-hour and weekly utilization and reset times. This script:
  1. uses the newest such event from the run logs if it is recent enough (no extra cost), else
  2. makes one tiny probe call (`claude -p` on Haiku, one turn, no tools) and reads its event,
and prints the result in the shape of the desktop app's `get_usage` tool, so agent/budget.py works
unchanged:  {"plan": {"status": "ok", "windows": [{"label": "5-hour limit", ...}, {"label": "Weekly · all models", ...}]}}

  agent/usage_probe.py                 print usage JSON (exit 0), or {"plan": {"status": "unavailable"}} (exit 3)
Env: AUTOMATED_RUNTIME (logs in $AUTOMATED_RUNTIME/logs), USAGE_MAX_AGE_MIN (default 15).
"""
import glob
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

RUNTIME = os.path.expanduser(os.environ.get("AUTOMATED_RUNTIME", "~/runtime/automated"))
MAX_AGE = float(os.environ.get("USAGE_MAX_AGE_MIN", 15)) * 60


def iso(ts):
    return datetime.fromtimestamp(float(ts), timezone.utc).isoformat().replace("+00:00", "Z")


def to_usage(info):
    """rate_limit_info -> get_usage-shaped plan, or None if the windows are missing."""
    w = info.get("unifiedWindows") or {}
    five, week = w.get("five_hour"), w.get("seven_day")
    if not five or not week or five.get("utilization") is None or week.get("utilization") is None:
        return None
    return {"plan": {"status": "ok", "source": "claude rate_limit_event", "windows": [
        {"label": "5-hour limit", "percentUsed": round(float(five["utilization"]) * 100, 1), "resetsAt": iso(five["resetsAt"])},
        {"label": "Weekly · all models", "percentUsed": round(float(week["utilization"]) * 100, 1), "resetsAt": iso(week["resetsAt"])},
    ]}}


def last_event(lines):
    found = None
    for line in lines:
        if '"rate_limit_event"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") == "rate_limit_event" and to_usage(d.get("rate_limit_info") or {}):
            found = d["rate_limit_info"]
    return found


def from_logs(now):
    files = sorted(glob.glob(os.path.join(RUNTIME, "logs", "*.jsonl")), key=os.path.getmtime, reverse=True)
    for f in files[:5]:
        if now - os.path.getmtime(f) > MAX_AGE:
            break
        with open(f, errors="replace") as fh:
            info = last_event(fh)
        if info:
            return to_usage(info)
    return None


def probe():
    cmd = ["claude", "-p", "Reply with exactly: OK", "--model", "haiku", "--max-turns", "1",
           "--output-format", "stream-json", "--verbose", "--tools", ""]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=180).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    with open(os.path.join(RUNTIME, "logs", "usage-probe.jsonl"), "w") as f:
        f.write(out)
    info = last_event(out.splitlines())
    return to_usage(info) if info else None


def main():
    usage = from_logs(time.time()) or probe()
    if not usage:
        print(json.dumps({"plan": {"status": "unavailable"}}))
        sys.exit(3)
    print(json.dumps(usage))


if __name__ == "__main__":
    main()
