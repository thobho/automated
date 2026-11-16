# Dispatcher: runs on pirx (no Mac task)

Since 2026-11-16 the hourly dispatcher is the systemd timer `automated-dispatch` on pirx (`agent/pirx/dispatch.sh`). It reads the Claude plan limits from pirx's own Claude Code (`agent/usage_probe.py`), so the agent runtime never depends on the Mac. The former Mac scheduled task `automated-dispatcher` is paused; delete it from the app once the pirx timer has run for a few days.

# Scheduled task: idea-generator

Research runs from files on the branch `research/idea-generator` (see `projects/idea-generator/RUNNER.md` there); it does not use issues.
- **Schedule:** every hour, at minute 37 (cron `37 * * * *`), so it starts apart from the worker
- **Prompt:**

```
You are the unattended runner for the idea-generator research in the repo thobho/automated. Nobody is watching this run: never ask questions in chat.

All work happens in the git worktree /Users/user/Projects/automated-work/idea-generator on branch research/idea-generator. If that folder is missing, create it: `git -C /Users/user/Projects/automated fetch origin research/idea-generator` and then `git -C /Users/user/Projects/automated worktree add /Users/user/Projects/automated-work/idea-generator research/idea-generator`. Never switch branches in /Users/user/Projects/automated itself.

Read and follow exactly: /Users/user/Projects/automated-work/idea-generator/projects/idea-generator/RUNNER.md

Key points (RUNNER.md has the details):
- Gates come first and must stay cheap: take a slot with ~/.config/automated/worker-lock.sh acquire, claim "idea-generator", then run the budget gate (/Users/user/Projects/automated/agent/budget.py, which paces usage evenly over the 5-hour window and the week). WAIT or BUSY → release and end immediately.
- State lives in projects/idea-generator/PROGRESS.md (markers [ ] [~] [x] [!]). Continue the [~] task, otherwise start the first ready [ ] task. One subagent per round, with the task's model.
- Commit and push small pieces often, and keep the task's Resume line in PROGRESS.md current, so a run stopped by the budget loses nothing.
- Never create GitHub issues or PRs for this project, never push to main, never force-push, and only edit files in projects/idea-generator/.
```
