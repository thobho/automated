# automated

Projects built continuously by a Claude Code worker, fed from this repo's GitHub issues.

## Add a task
- **Phone:** GitHub app → this repo → Issues → New → **Agent task**. The template adds `agent:todo` for you.

**Order and dependencies:** write `Depends on: #12, #14` in the issue body and the agent won't start it until those issues are closed (PR merged). Among ready tasks: `priority:high` first, `priority:low` last; then the earliest GitHub milestone (M1 before M2); then the task that unblocks the most other issues; then oldest first. `scripts/queue.sh` shows the order and what each task waits on.

**Model per task:** add a `model:pirx`, `model:haiku`, `model:sonnet` or `model:opus` label (or edit the `Model:` line in the template). Default is Sonnet.
- `model:pirx` goes to **OpenCode on pirx** (OpenRouter, 10 USD a month); use it for simple, well-specified work: templates, fixtures, extra tests, docs, simple views.
- The other models are built by a **Claude run** on your plan. Opus is for security, AI and architecture work and hard bugs.
- `area:security` tasks never go to OpenCode, even with `model:pirx`.
- **Review limit:** while a project has 5 PRs waiting for your review (`agent:review`), its new tasks wait (`AGENT_MAX_OPEN_REVIEWS`).

## Track it
- **Pinned issue "🤖 Agent status"**: limits, reset times, whether the worker may run, and the queue. Updated on every worker run.
- **Labels on each issue:** `agent:todo` → `agent:doing` → `agent:review` (PR open) → close it by merging. `agent:blocked` = the agent asked you something in the comments; answer there.
- **Plan checklist** in each task's comments shows step-by-step progress.
- **Each PR** has a **Verification** section (real API calls, headless-browser screenshots), **Decisions I made** and **Action for you**. Failures are posted as `❌` comments on the issue; a push notification goes out when a PR opens, a task blocks or something fails.
- **API keys** for tasks go in `~/.config/automated/secrets.env` (never committed).

## How the worker spends your limits
A desktop-app scheduled task (`automated-worker-2`, prompt in `agent/scheduled-task.md`) checks in every hour and runs `agent/worker-prompt.md`. Before each task it runs `agent/budget.py`, which spreads usage evenly:
- **5-hour window:** usage must stay under a line rising evenly from **15%** at the window start to **70%** at its reset, so a window isn't burned in its first hour and you keep room for your own work.
- **Weekly (even burn):** usage must stay under the line **5% + 90% × share of the week elapsed** (50% at mid-week). In the last 12 hours before the reset the line opens to **98%**, so nothing is wasted. The gap between the line and usage is the *headroom*.
- **Opus** runs only with at least **5** points of headroom; a **second parallel run** needs **10** points and the 5-hour window below **50%**.
- **Spillover:** with 10 points of headroom and no Claude task ready, a Claude run may build an OpenCode task (with Sonnet).

The OpenCode worker has its own gate, `agent/openrouter_budget.py`: it spends the monthly 10 USD evenly (usage below 10 USD × share of the month elapsed + 0.5 USD, no pace gate in the last 2 days), at most 0.75 USD per task, and stops when the key's own limit is nearly used. Set that limit (10 USD, monthly reset) on the key at openrouter.ai.

Checking hourly is what makes the pacing work: a run that finds usage ahead of the line stops after the cheap gate. Tune with the `AGENT_*` variables at the top of `agent/budget.py` and the `OPENROUTER_*` ones in `agent/openrouter_budget.py`.

## Parallel runs
Up to two worker runs build at the same time, each on its own task.
- **Slots:** `~/.config/automated/worker-lock.sh` (a copy of `scripts/worker-lock.sh`, outside the repo) hands each run a slot. When every slot is taken, the new run skips. The count comes from `~/.config/automated/state/slots.conf` (default 1).
- **Claims:** a run claims its issue, so no other run picks it. Slots and claims free themselves when the run's process dies.
- **Shared resources:** add a `Uses: gus-bdl` line (comma-separated names) to issues that hit the same API, data or tool. The picker won't start one while another issue using the same thing is running.
- **Own folder per task:** `scripts/task-worktree.sh <issue> <slug>` gives each task a git worktree in `../automated-work/issue-<n>`. The shared checkout stays on `main`.
- **Usage:** a second run starts only with 10 points of weekly headroom and the 5-hour window below 50% (`AGENT_PARALLEL_HEADROOM`, `AGENT_PARALLEL_CAP`). The 70% 5-hour cap applies to both.
- **Other scheduled runners** can share the slots and the budget gate without using issues. `idea-generator` (branch `research/idea-generator`, prompt in `agent/scheduled-task.md`) takes a slot and claims `idea-generator`, and tracks its work in files instead of issues.

Tests: `scripts/test-worker-lock.sh`, `python3 agent/test_pick_task.py`, `python3 agent/test_budget.py` and `python3 agent/test_openrouter_budget.py`.

## Layout
`projects/<name>/` holds independent projects, each with its own README, CLAUDE.md and dependencies. `agent/` and `scripts/` hold the worker tooling.

## Live site
`projects/visualization-of-the-world/site/` (real GUS/Eurostat showcase plus the synthetic demo pages) is deployed to GitHub Pages by `.github/workflows/deploy-pages.yml` on pushes to `main`. Data sources, the proxy/direct distinction and the deploy steps are in [projects/visualization-of-the-world/site/README.md](projects/visualization-of-the-world/site/README.md).
