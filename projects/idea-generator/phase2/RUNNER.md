# What a scheduled run does (Phase 2)

The `idea-generator` scheduled task fires every hour. Nobody watches the run, so never ask questions in chat: write them under **Blocked / questions** in `phase2/PROGRESS.md`. This project does **not** use GitHub issues or PRs: all state lives in `phase2/PROGRESS.md` on the branch `research/idea-generator`. Phase 1 is finished; never change its tasks.

`LOCK` means `~/.config/automated/worker-lock.sh`. It is shared with the issue worker, so the two never run more than the allowed number of slots between them.

## 1. Gates (keep this part cheap)
1. `LOCK acquire`. If it prints `BUSY`, end the run. Otherwise note the slot number `N` from `OK: slot N`.
2. `LOCK claim idea-generator`. Exit 1 (`CLAIMED`) means another idea-generator run is live: `LOCK release` and end.
3. Budget: call `mcp__ccd_session_mgmt__get_usage` (load it with ToolSearch if deferred), save the JSON to `/tmp/idea-usage-N.json`, then run
   `AGENT_SLOT=N /Users/user/Projects/automated/agent/budget.py < /tmp/idea-usage-N.json`.
   `WAIT` → `LOCK release` and end the run immediately.

## 2. Working copy
Work only in `/Users/user/Projects/automated-work/idea-generator` (a git worktree on `research/idea-generator`). Never touch or switch the branch of `/Users/user/Projects/automated`.
- If the folder is missing: `git -C /Users/user/Projects/automated worktree add /Users/user/Projects/automated-work/idea-generator research/idea-generator` (fetch first; the branch lives on origin).
- Then `git pull --ff-only`. If that fails, stop and write what happened under Blocked.

## 3. Pick the task
Read `projects/idea-generator/phase2/PROGRESS.md`. Take the first `[~]` task. Otherwise take the first `[ ]` task whose `needs` are all `[x]`. If there is none: every task is `[x]` → add a final line to the Run log and end. Otherwise the remaining ones are blocked → end.

Mark it `[~]`, add an indented `Resume: starting` line under it, commit `idea-generator: phase2 start T<NN>`, push.

## 4. Do the work
Start **one subagent** (Agent tool) with `model: "fable"` and `effort: "medium"` for every task (the owner chose this; don't change it). Give it:
- the working copy path, and the instruction never to touch `/Users/user/Projects/automated`;
- the full text of `phase2/BRIEF.md` and of the task file;
- the task's current **Resume** line and the relevant files already on the branch;
- these rules: commit and push after every small unit; before each commit update the task's Resume line in `phase2/PROGRESS.md`; work for at most about one hour of effort, then stop at a clean point; never mark the task `[x]` or edit other tasks' lines; finish by reporting either `DONE` (the task's "Done when" is met and the link check passes) or `PARTIAL` plus where it stopped.

When the subagent returns:
- **DONE:** check the "Done when" list yourself (files exist, link check passes). Then mark the task `[x]`, remove its Resume line, and add a Run log line.
- **PARTIAL:** make sure its Resume line is specific. Add a Run log line.
- A question it can't decide (spending money, missing access): mark `[!]`, write the question under Blocked, and move on.

Commit `idea-generator: phase2 T<NN> <done|progress>` and push.

## 5. Continue or stop
Re-run the budget gate (step 1.3). On `RUN`, go back to step 3, for at most 3 subagent rounds per run. Then:
1. `LOCK unclaim idea-generator`, then `LOCK release`.
2. If a task was finished or blocked in this run, send one short push notification (`PushNotification`, load with ToolSearch; skip if unavailable), e.g. `Idea generator P2: T03 done, next T04` or `Idea generator P2 blocked on T05: <question>`.

## Never
Push to `main`, force-push, create GitHub issues or PRs, edit files outside `projects/idea-generator/`, or rewrite the history of the branch.
