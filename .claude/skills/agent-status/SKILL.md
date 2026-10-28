---
name: agent-status
description: Show the autonomous worker's plan limits, reset times, budget decision and task queue. Use when the user asks about agent status, progress, limits, resets or the queue.
---

# Agent status

1. Call `mcp__ccd_session_mgmt__get_usage` (load it with ToolSearch if deferred), save the JSON to `/tmp/agent-usage.json`, run `agent/budget.py < /tmp/agent-usage.json`.
2. Run `scripts/queue.sh`.
3. For each `agent:doing` issue, read its latest comments (`gh issue view <n> --comments`) to see checklist progress.
4. Reply briefly: a table of 5-hour and weekly usage with reset times in the user's local time, whether the worker would run now and why, then the queue by state with progress for the in-flight tasks and links to open PRs.
5. If the user asks, refresh the pinned dashboard: `agent/budget.py < /tmp/agent-usage.json | scripts/update-status.sh "Manual refresh"`.
