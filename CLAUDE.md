# automated

Home for projects that an autonomous Claude Code worker builds from a GitHub issue queue.

## Layout
- `projects/<name>/` — one folder per project. Projects are **completely independent**: own README, own CLAUDE.md, own dependencies, own tests. Never import, share or reference code across project folders.
- `agent/` — the worker: `budget.py` (may we spend tokens now?) and `worker-prompt.md` (what a scheduled run does).
- `scripts/` — `queue.sh`, `update-status.sh`, `setup-labels.sh`.

## Task queue = GitHub issues
Every task is an issue with `agent:todo` and exactly one `project:<name>` label. State moves through labels:
`agent:todo` → `agent:doing` → `agent:review` (PR open) → `agent:done` (PR merged), or `agent:blocked` when the agent needs an answer.
`priority:high` tasks are picked first; otherwise oldest first. The pinned `agent:status` issue is the dashboard (limits, resets, queue).

## Rules for any agent working here
- Work only inside `projects/<name>/` for the issue's project label. A new project name means creating that folder with a README and CLAUDE.md.
- Never push to `main`. Branch `agent/<issue>-<slug>`, open a PR with `Closes #<issue>`.
- Unclear task → comment with specific questions, label `agent:blocked`, move on. Do not guess.
- Keep each PR small enough to review on a phone.
