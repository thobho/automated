# automated

Projects built continuously by a Claude Code worker, fed from this repo's GitHub issues.

## Add a task
- **Phone:** GitHub app → this repo → Issues → New → **Agent task**. The template adds `agent:todo` for you.

**Order and dependencies:** write `Depends on: #12, #14` in the issue body and the agent won't start it until those issues are closed (PR merged). Among ready tasks: `priority:high` first, `priority:low` last, otherwise oldest first. `scripts/queue.sh` shows the order and what each task waits on.

**Model per task:** add a `model:haiku`, `model:sonnet` or `model:opus` label (or edit the `Model:` line in the template). Default is Sonnet. The worker hands the building to a subagent on that model.

## Track it
- **Pinned issue "🤖 Agent status"**: limits, reset times, whether the worker may run, and the queue. Updated on every worker run.
- **Labels on each issue:** `agent:todo` → `agent:doing` → `agent:review` (PR open) → close it by merging. `agent:blocked` = the agent asked you something in the comments; answer there.
- **Plan checklist** in each task's comments shows step-by-step progress.
- **Each PR** has a **Verification** section (real API calls, headless-browser screenshots), **Decisions I made** and **Action for you**. Failures are posted as `❌` comments on the issue; a push notification goes out when a PR opens, a task blocks or something fails.
- **API keys** for tasks go in `~/.config/automated/secrets.env` (never committed).

## How the worker spends your limits
A desktop-app scheduled task runs `agent/worker-prompt.md` every hour. Before each task it runs `agent/budget.py`:
- 5-hour window must be under **80%**.
- Weekly usage must stay under a line rising evenly to **80%** across the week (+5% buffer), so it never burns the week in a day.

That leaves at least 20% for your own work. Tune with `AGENT_FIVE_HOUR_CAP`, `AGENT_WEEKLY_CAP`, `AGENT_PACE_BUFFER`.

## Parallel runs
Up to two worker runs build at the same time, each on its own task.
- **Slots:** `~/.config/automated/worker-lock.sh` (a copy of `scripts/worker-lock.sh`, outside the repo) hands each run a slot. When every slot is taken, the new run skips. The count comes from `~/.config/automated/state/slots.conf` (default 1).
- **Claims:** a run claims its issue, so no other run picks it. Slots and claims free themselves when the run's process dies.
- **Shared resources:** add a `Uses: gus-bdl` line (comma-separated names) to issues that hit the same API, data or tool. The picker won't start one while another issue using the same thing is running.
- **Own folder per task:** `scripts/task-worktree.sh <issue> <slug>` gives each task a git worktree in `../automated-work/issue-<n>`. The shared checkout stays on `main`.
- **Usage:** a second run starts only while the 5-hour window is below 60% (`AGENT_PARALLEL_CAP`). The 80% caps apply to both.

Tests: `scripts/test-worker-lock.sh` and `python3 agent/test_pick_task.py`.

## Layout
`projects/<name>/` holds independent projects, each with its own README, CLAUDE.md and dependencies. `agent/` and `scripts/` hold the worker tooling.
