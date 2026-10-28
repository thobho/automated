# automated

Projects built continuously by a Claude Code worker, fed from this repo's GitHub issues.

## Add a task
- **Phone:** GitHub app → this repo → Issues → New → **Agent task**. The template adds `agent:todo` for you.
- **Claude Code session in this folder:** `/new-task build a CLI that ...`
- **Terminal:** `scripts/new-task.sh -p my-project -t "Do the thing" -b "Details" [--high]`

## Track it
- **Pinned issue "🤖 Agent status"**: limits, reset times, whether the worker may run, and the queue. Updated on every worker run.
- **Labels on each issue:** `agent:todo` → `agent:doing` → `agent:review` (PR open) → close it by merging. `agent:blocked` = the agent asked you something in the comments; answer there.
- **Plan checklist** in each task's comments shows step-by-step progress.
- **Claude Code session:** `/agent-status`.

## How the worker spends your limits
A desktop-app scheduled task runs `agent/worker-prompt.md` every hour. Before each task it runs `agent/budget.py`:
- 5-hour window must be under **80%**.
- Weekly usage must stay under a line rising evenly to **80%** across the week (+5% buffer), so it never burns the week in a day.

That leaves at least 20% for your own work. Tune with `AGENT_FIVE_HOUR_CAP`, `AGENT_WEEKLY_CAP`, `AGENT_PACE_BUFFER`.

## Layout
`projects/<name>/` holds independent projects, each with its own README, CLAUDE.md and dependencies. `agent/` and `scripts/` hold the worker tooling.
