# Scheduled task: automated-dispatcher

The Claude work itself runs on pirx (see `agent/pirx/README.md`). Only the Mac's desktop app can read the plan limits, so this hourly Mac task reads them and hands them to pirx in one SSH call. It must stay tiny: it is the only Claude cost of a run that ends up waiting.

Create it in the Claude desktop app (Code tab → Scheduled tasks), or ask Claude to create it.
- **Schedule:** every hour, at minute 7 (cron `7 * * * *`, local time)
- **Model:** the cheapest available (Haiku)
- **Prompt:**

```
You are the dispatcher for the agent runs of the repo thobho/automated. Nobody is watching: never ask questions. Do exactly this and nothing else:
1. Call the get_usage tool (mcp__ccd_session_mgmt__get_usage; load it with ToolSearch if it is deferred).
2. Write its JSON output, unchanged, to /tmp/automated-usage.json.
3. Run: ssh -o BatchMode=yes -o ConnectTimeout=15 agent@192.168.68.62 'bash ~/Projects/automated-work/runner/agent/pirx/start-claude-run.sh' < /tmp/automated-usage.json
4. Reply with the one line it printed (or the SSH error) and end the run.
Do not read files, do not investigate errors, do not retry more than once.
```

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
